"""Shared ``add`` / ``batch`` behavior for the card commands.

Reads the items, generates them with a concurrency cap and a per-minute
limit, reports one result per item, and sets the exit code: 0 when every
item was saved, 1 when any failed or Anki couldn't be reached, 2 for usage
errors. stdout carries only the result (the summary, or with ``--json`` one
JSON document); progress and anything printed while generating go to stderr.
"""

import asyncio
import json
import sys
from collections.abc import Awaitable, Callable, Coroutine, Iterable, Sequence
from contextlib import AbstractAsyncContextManager, redirect_stdout
from dataclasses import dataclass
from typing import Protocol, TextIO

import click
from asynciolimiter import StrictLimiter

MAX_CONCURRENCY = 10


class NoteMaker(Protocol):
    """A card collection: generates one item's card(s) and saves them."""

    def generate_and_add_note(self, text: str, /) -> Awaitable[int | list[int]]: ...


type CollectionScope = Callable[[], AbstractAsyncContextManager[NoteMaker]]
"""Opens Anki and the collection; called once per command run."""


@dataclass(frozen=True, slots=True)
class Item:
    """One input to make cards from."""

    text: str


@dataclass(frozen=True, slots=True)
class ItemResult:
    """What happened to one item: the saved note ids, or why it failed."""

    item: Item
    note_ids: tuple[int, ...] = ()
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None


def json_option(cmd):
    """Add ``--json`` to an ``add`` or ``batch`` command."""
    return click.option(
        "--json",
        "as_json",
        is_flag=True,
        help=(
            "Print one JSON document with each item's result (note ids or "
            "error) to stdout; progress and logs go to stderr."
        ),
    )(cmd)


def batch_options(*, rpm_default: int, rpm_note: str = ""):
    """Add ``--file``, ``--rpm`` and ``--json`` to a ``batch`` command.

    :param rpm_default: the kind's default items per minute.
    :param rpm_note: appended to ``--rpm``'s help, e.g. why the default is low.
    """
    rpm_help = (
        "Max items started per minute; 0 for no limit. Each card makes "
        "several AI requests, so stay below your provider's limit."
    )

    def decorate(cmd):
        cmd = json_option(cmd)
        cmd = click.option(
            "--rpm",
            default=rpm_default,
            show_default=True,
            type=click.IntRange(min=0),
            help=f"{rpm_help} {rpm_note}".strip(),
        )(cmd)
        return click.option(
            "--file",
            "-f",
            type=click.File("r", encoding="utf-8"),
            help="Read more items from a file, one per line; - reads stdin.",
        )(cmd)

    return decorate


def read_items(args: Sequence[str], file: TextIO | None, *, noun: str) -> list[Item]:
    """Items from the arguments, then the file's non-blank lines.

    :param noun: the kind's plural, for the error message ("words").
    :raises click.UsageError: there are no items.
    """
    texts = [arg.strip() for arg in args]
    if file is not None:
        texts += file.read().splitlines()
    items = [Item(text.strip()) for text in texts if text.strip()]
    if not items:
        raise click.UsageError(
            f"No {noun} given: pass them as arguments or with --file."
        )
    return items


def add_one(scope: CollectionScope, text: str, *, kind: str, as_json: bool) -> None:
    """Make one item's card(s) and print the saved note ids.

    :param kind: the command group ("word"), named in the JSON document.
    :raises click.ClickException: Anki is unreachable, or (without
        ``as_json``) the item failed.
    """
    [result] = _make_all_quietly(scope, [Item(text)], rpm=0)
    if as_json:
        _print_json(kind, [result])
    elif result.ok:
        click.echo(f"✓ Added: {text} ({_notes(result.note_ids)})")
    else:
        raise click.ClickException(f"{text}: {result.error}")
    if not result.ok:
        click.get_current_context().exit(1)


def add_many(
    scope: CollectionScope,
    items: list[Item],
    *,
    kind: str,
    noun: str,
    rpm: int,
    as_json: bool,
) -> None:
    """Make every item's cards and report each result; exit 1 if any failed."""
    click.echo(
        f"Processing {len(items)} {noun} "
        f"(concurrency={MAX_CONCURRENCY}, rpm={rpm or 'no limit'}) ...",
        err=True,
    )
    results = _make_all_quietly(scope, items, rpm=rpm)
    if as_json:
        _print_json(kind, results)
    else:
        _print_summary(results)
    if not all(result.ok for result in results):
        click.get_current_context().exit(1)


def run[T](coro: Coroutine[object, object, T]) -> T:
    """Run a command's coroutine; turn unexpected errors into a one-line error.

    :raises click.ClickException: the coroutine raised anything but a click
        error (Anki unreachable, a bad setting).
    """
    try:
        return asyncio.run(coro)
    except click.ClickException:
        raise
    except Exception as e:
        raise click.ClickException(_describe(e)) from e


def _make_all_quietly(
    scope: CollectionScope, items: Iterable[Item], *, rpm: int
) -> list[ItemResult]:
    """Generate the items with stdout sent to stderr.

    Providers' libraries print to stdout (litellm does on some errors), which
    would corrupt the result an agent parses.
    """
    try:
        with redirect_stdout(sys.stderr):
            return run(_make_all(scope, items, rpm=rpm))
    finally:
        sys.stderr.flush()


async def _make_all(
    scope: CollectionScope, items: Iterable[Item], *, rpm: int
) -> list[ItemResult]:
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    limiter = StrictLimiter(rpm / 60) if rpm > 0 else None

    async with scope() as collection:

        async def make(item: Item) -> ItemResult:
            async with semaphore:
                if limiter is not None:
                    await limiter.wait()
                try:
                    saved = await collection.generate_and_add_note(item.text)
                except Exception as e:  # one item's failure is reported, not fatal
                    return ItemResult(item, error=_describe(e))
                ids = saved if isinstance(saved, list) else [saved]
                return ItemResult(item, note_ids=tuple(ids))

        async with asyncio.TaskGroup() as group:
            tasks = [group.create_task(make(item)) for item in items]
    return [task.result() for task in tasks]


def _print_json(kind: str, results: Sequence[ItemResult]) -> None:
    succeeded = sum(result.ok for result in results)
    document = {
        "kind": kind,
        "total": len(results),
        "succeeded": succeeded,
        "failed": len(results) - succeeded,
        "results": [_result_json(result) for result in results],
    }
    click.echo(json.dumps(document, ensure_ascii=False))


def _result_json(result: ItemResult) -> dict[str, object]:
    if result.ok:
        return {"input": result.item.text, "ok": True, "note_ids": [*result.note_ids]}
    return {"input": result.item.text, "ok": False, "error": result.error}


def _print_summary(results: list[ItemResult]) -> None:
    saved = [result for result in results if result.ok]
    failed = [result for result in results if not result.ok]
    click.echo(f"\n✅ {len(saved)}/{len(results)} saved")
    for result in saved:
        click.echo(f"   • {result.item.text} ({_notes(result.note_ids)})")
    if failed:
        click.echo(f"\n❌ {len(failed)} failed")
        for result in failed:
            click.echo(f"   • {result.item.text}: {result.error}")


def _notes(note_ids: Sequence[int]) -> str:
    label = "note" if len(note_ids) == 1 else "notes"
    return f"{label} {', '.join(map(str, note_ids))}"


def _describe(error: Exception) -> str:
    return str(error) or type(error).__name__
