"""Shared ``add`` / ``batch`` behavior for the card commands.

Reads the items, generates them with a concurrency cap and a per-minute
limit, prints one line per item, and sets the exit code: 0 when every item
was saved, 1 when any failed or Anki couldn't be reached, 2 for usage errors.
"""

import asyncio
from collections.abc import Awaitable, Callable, Coroutine, Iterable, Sequence
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

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


def batch_options(*, rpm_default: int, rpm_note: str = ""):
    """Add ``--file`` and ``--rpm`` to a ``batch`` command.

    :param rpm_default: the kind's default items per minute.
    :param rpm_note: appended to ``--rpm``'s help, e.g. why the default is low.
    """
    rpm_help = (
        "Max items started per minute; 0 for no limit. Each card makes "
        "several AI requests, so stay below your provider's limit."
    )

    def decorate(cmd):
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
            type=click.Path(exists=True, dir_okay=False, path_type=Path),
            help="Read more items from a file, one per line.",
        )(cmd)

    return decorate


def read_items(args: Sequence[str], file: Path | None, *, noun: str) -> list[Item]:
    """Items from the arguments, then the file's non-blank lines.

    :param noun: the kind's plural, for the error message ("words").
    :raises click.UsageError: there are no items.
    """
    texts = [arg.strip() for arg in args]
    if file is not None:
        texts += file.read_text(encoding="utf-8").splitlines()
    items = [Item(text.strip()) for text in texts if text.strip()]
    if not items:
        raise click.UsageError(
            f"No {noun} given: pass them as arguments or with --file."
        )
    return items


def add_one(scope: CollectionScope, text: str) -> None:
    """Make one item's card(s) and print the saved note ids.

    :raises click.ClickException: the item failed or Anki is unreachable.
    """
    [result] = run(_make_all(scope, [Item(text)], rpm=0))
    if not result.ok:
        raise click.ClickException(f"{text}: {result.error}")
    click.echo(f"✓ Added: {text} ({_notes(result.note_ids)})")


def add_many(scope: CollectionScope, items: list[Item], *, noun: str, rpm: int) -> None:
    """Make every item's cards and print a summary; exit 1 if any failed."""
    click.echo(
        f"Processing {len(items)} {noun} "
        f"(concurrency={MAX_CONCURRENCY}, rpm={rpm or 'no limit'}) ..."
    )
    results = run(_make_all(scope, items, rpm=rpm))
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
