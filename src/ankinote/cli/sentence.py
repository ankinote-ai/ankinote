"""CLI commands for sentence (production) cards."""

from contextlib import asynccontextmanager
from typing import TextIO

import click

from ankinote.cli.batch import (
    add_many,
    add_one,
    batch_options,
    json_option,
    read_items,
    run,
)
from ankinote.cli.factory import (
    LanguageCollectionOptions,
    anki_client_scope,
    build_sentence_collection,
    language_options,
    model_options,
    resolve_languages,
    resolve_thinking,
)
from ankinote.services.ai import DISABLE_REASONING


def collection_options(cmd):
    cmd = model_options(thinking_default="off for sentence cards", images=False)(cmd)
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
            build_sentence_collection(client, options) as collection,
        ):
            yield collection

    return scope


# -- sentence group -----------------------------------------------------------


@click.group("sentence")
def sentence():
    """Sentence card commands (production cards: recall the target sentence)."""


@sentence.command("init")
@collection_options
def init(native, target, llm, profile, thinking):
    """Create sentence note type and deck in Anki."""

    async def _run():
        async with _scope(build_options(native, target, llm, profile, thinking))():
            pass

    run(_run())
    click.echo("✓ Ready (sentence collection)")


@sentence.command("add")
@click.argument("sentence")
@json_option
@collection_options
def add(sentence, as_json, native, target, llm, profile, thinking):
    """Generate and push a single sentence production card.

    The *sentence* argument should be in the target language. Its
    native-language translation will appear on the card front; the target
    sentence, notes, and phrase breakdown appear on the back.
    """
    add_one(
        _scope(build_options(native, target, llm, profile, thinking)),
        sentence,
        kind="sentence",
        as_json=as_json,
    )


@sentence.command("batch")
@click.argument("sentences", nargs=-1, metavar="[SENTENCE ...]")
@batch_options(rpm_default=60)
@collection_options
def batch(
    sentences: tuple[str, ...],
    file: TextIO | None,
    rpm: int,
    as_json: bool,
    native,
    target,
    llm,
    profile,
    thinking,
):
    """Generate and push multiple sentence production cards.

    \b
    Sentences should be provided in the target language. They can be passed as
    arguments, read from a file (one per line), or both at the same time.

    \b
    Examples:
      ankinote sentence add "I overslept this morning."
      ankinote sentence batch --file sentences.txt
      cat sentences.txt | ankinote sentence batch --file - --json
      ankinote sentence batch "I overslept this morning." --file more.txt
    """
    items = read_items(sentences, file, noun="sentences")
    options = build_options(native, target, llm, profile, thinking)
    add_many(
        _scope(options),
        items,
        kind="sentence",
        noun="sentences",
        rpm=rpm,
        as_json=as_json,
    )
