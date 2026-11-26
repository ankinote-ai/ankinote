"""CLI commands for word cards."""

from contextlib import asynccontextmanager
from typing import TextIO

import click

from ankinote.cli.batch import (
    InputFormat,
    add_many,
    add_one,
    as_typed_option,
    batch_options,
    context_option,
    json_option,
    read_items,
    run,
)
from ankinote.cli.factory import (
    WordCollectionOptions,
    anki_client_scope,
    build_word_collection,
    language_options,
    model_options,
    resolve_languages,
    resolve_thinking,
)
from ankinote.services.ai import DISABLE_REASONING


def collection_options(cmd):
    cmd = model_options(thinking_default="off for word cards", images=True)(cmd)
    return language_options(cmd)


def build_options(
    native: str | None,
    target: str | None,
    llm: str | None,
    image_model: str | None,
    image_size: int | None,
    profile: str | None = None,
    image_profile: str | None = None,
    thinking: str | None = None,
) -> WordCollectionOptions:
    """Convert CLI parameters to typed collection options."""
    native_language, target_language = resolve_languages(native, target)
    return WordCollectionOptions(
        native_language=native_language,
        target_language=target_language,
        llm_model=llm,
        image_model=image_model,
        image_size=image_size,
        reasoning_effort=resolve_thinking(thinking, unset=DISABLE_REASONING),
        profile=profile,
        image_profile=image_profile,
    )


def _scope(options: WordCollectionOptions):
    @asynccontextmanager
    async def scope():
        async with (
            anki_client_scope() as client,
            build_word_collection(client, options) as collection,
        ):
            yield collection

    return scope


# -- word group ---------------------------------------------------------------


@click.group("word")
def word():
    """Word card commands"""


@word.command("init")
@collection_options
def init(
    native, target, llm, profile, thinking, image_model, image_size, image_profile
):
    """Create or update the note type and deck in Anki.

    Updates an existing note type to this version's fields, templates and
    styling, which can make AnkiWeb ask for a full sync; `add` and `batch`
    only create what is missing.
    """
    options = build_options(
        native, target, llm, image_model, image_size, profile, image_profile, thinking
    )

    async def _run():
        async with _scope(options)() as collection:
            await collection.ensure_in_anki()

    run(_run())
    click.echo("✓ Ready (word collection)")


@word.command("add")
@click.argument("word")
@context_option
@as_typed_option
@json_option
@collection_options
def add(
    word,
    context,
    as_typed,
    as_json,
    native,
    target,
    llm,
    profile,
    thinking,
    image_model,
    image_size,
    image_profile,
):
    """Generate and push a single word card (one note per part of speech).

    \b
    With --context, one note for the sense the word has in that sentence:
      ankinote word add bank --context "We sat on the bank of the river."
    """
    options = build_options(
        native, target, llm, image_model, image_size, profile, image_profile, thinking
    )
    add_one(
        _scope(options),
        word,
        kind="word",
        as_json=as_json,
        context=context,
        as_typed=as_typed,
    )


@word.command("batch")
@click.argument("words", nargs=-1, metavar="[WORD ...]")
@batch_options(
    rpm_default=8,
    rpm_note="Word cards default lower: each also makes a picture and audio.",
    context=True,
)
@collection_options
def batch(
    words: tuple[str, ...],
    file: TextIO | None,
    rpm: int,
    as_json: bool,
    input_format: InputFormat,
    native,
    target,
    llm,
    profile,
    thinking,
    image_model,
    image_size,
    image_profile,
):
    """Generate and push multiple word cards.

    \b
    Words can be passed as arguments, read from a file (one per line),
    or both at the same time.

    \b
    Examples:
      ankinote word batch apple banana cat
      ankinote word batch --file words.txt
      cat words.txt | ankinote word batch --file - --json
      ankinote word batch --rpm 30 apple --file more.txt
      ankinote word batch --format jsonl --file words.jsonl --json

    \b
    With --format jsonl, each line can carry the sentence the word came from,
    and the card covers only the sense used there:
      {"text": "bank", "context": "We sat on the bank of the river."}
    """
    items = read_items(words, file, noun="words", input_format=input_format)
    options = build_options(
        native, target, llm, image_model, image_size, profile, image_profile, thinking
    )
    add_many(
        _scope(options), items, kind="word", noun="words", rpm=rpm, as_json=as_json
    )
