"""CLI commands for phrase cards."""

from contextlib import asynccontextmanager
from pathlib import Path

import click

from ankinote.cli.batch import add_many, add_one, batch_options, read_items, run
from ankinote.cli.factory import (
    LanguageCollectionOptions,
    anki_client_scope,
    build_phrase_collection,
    language_options,
    model_options,
    resolve_languages,
    resolve_thinking,
)
from ankinote.services.ai import DISABLE_REASONING


def collection_options(cmd):
    cmd = model_options(thinking_default="off for phrase cards", images=False)(cmd)
    return language_options(cmd)


def build_options(
    native: str | None,
    target: str | None,
    llm: str | None,
    profile: str | None = None,
    thinking: str | None = None,
) -> LanguageCollectionOptions:
    """Convert CLI parameters to typed collection options."""
    native_language, target_language = resolve_languages(native, target)
    return LanguageCollectionOptions(
        native_language=native_language,
        target_language=target_language,
        llm_model=llm,
        reasoning_effort=resolve_thinking(thinking, unset=DISABLE_REASONING),
        profile=profile,
    )


def _scope(options: LanguageCollectionOptions):
    @asynccontextmanager
    async def scope():
        async with (
            anki_client_scope() as client,
            build_phrase_collection(client, options) as collection,
        ):
            yield collection

    return scope


# -- phrase group -------------------------------------------------------------


@click.group("phrase")
def phrase():
    """Phrase card commands."""


@phrase.command("init")
@collection_options
def init(native, target, llm, profile, thinking):
    """Create phrase note type and deck in Anki."""

    async def _run():
        async with _scope(build_options(native, target, llm, profile, thinking))():
            pass

    run(_run())
    click.echo("✓ Ready (phrase collection)")


@phrase.command("add")
@click.argument("phrase")
@collection_options
def add(phrase, native, target, llm, profile, thinking):
    """Generate and push a single phrase card."""
    add_one(_scope(build_options(native, target, llm, profile, thinking)), phrase)


@phrase.command("batch")
@click.argument("phrases", nargs=-1, metavar="[PHRASE ...]")
@batch_options(rpm_default=60)
@collection_options
def batch(
    phrases: tuple[str, ...],
    file: Path | None,
    rpm: int,
    native,
    target,
    llm,
    profile,
    thinking,
):
    """Generate and push multiple phrase cards.

    \b
    Phrases can be passed as arguments, read from a file (one per line),
    or both at the same time.

    \b
    Examples:
      ankinote phrase batch "focus on" "look after"
      ankinote phrase batch --file phrases.txt
      ankinote phrase batch "call off" --file more.txt
    """
    items = read_items(phrases, file, noun="phrases")
    options = build_options(native, target, llm, profile, thinking)
    add_many(_scope(options), items, noun="phrases", rpm=rpm)
