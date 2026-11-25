"""CLI commands for phrase cards."""

from contextlib import asynccontextmanager
from typing import TextIO

import click

from ankinote.cli.batch import (
    InputFormat,
    add_many,
    add_one,
    batch_options,
    context_option,
    json_option,
    read_items,
    run,
)
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
    """Create or update the phrase note type and deck in Anki.

    Updates an existing note type to this version's fields, templates and
    styling, which can make AnkiWeb ask for a full sync; `add` and `batch`
    only create what is missing.
    """

    async def _run():
        options = build_options(native, target, llm, profile, thinking)
        async with _scope(options)() as collection:
            await collection.ensure_in_anki()

    run(_run())
    click.echo("✓ Ready (phrase collection)")


@phrase.command("add")
@click.argument("phrase")
@context_option
@json_option
@collection_options
def add(phrase, context, as_json, native, target, llm, profile, thinking):
    """Generate and push a single phrase card.

    \b
    With --context, the card covers the sense used in that sentence:
      ankinote phrase add "pick up" --context "I'll pick you up at six."
    """
    add_one(
        _scope(build_options(native, target, llm, profile, thinking)),
        phrase,
        kind="phrase",
        as_json=as_json,
        context=context,
    )


@phrase.command("batch")
@click.argument("phrases", nargs=-1, metavar="[PHRASE ...]")
@batch_options(rpm_default=60, context=True)
@collection_options
def batch(
    phrases: tuple[str, ...],
    file: TextIO | None,
    rpm: int,
    as_json: bool,
    input_format: InputFormat,
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
      cat phrases.txt | ankinote phrase batch --file - --json
      ankinote phrase batch "call off" --file more.txt
      ankinote phrase batch --format jsonl --file phrases.jsonl --json

    \b
    With --format jsonl, each line can carry the sentence the phrase came
    from, and the card covers only the sense used there:
      {"text": "pick up", "context": "I'll pick you up at six."}
    """
    items = read_items(phrases, file, noun="phrases", input_format=input_format)
    options = build_options(native, target, llm, profile, thinking)
    add_many(
        _scope(options), items, kind="phrase", noun="phrases", rpm=rpm, as_json=as_json
    )
