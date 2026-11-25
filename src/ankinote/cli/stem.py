"""CLI commands for STEM card generation."""

import mimetypes
from collections.abc import Awaitable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

import click

from ankinote.cli.batch import add_many, add_one, batch_options, read_items, run
from ankinote.cli.factory import (
    StemCollectionOptions,
    anki_client_scope,
    build_stem_collection,
    model_options,
    resolve_thinking,
)
from ankinote.collections.stem import CardType, StemCollection


def collection_options(cmd):
    cmd = click.option(
        "--type",
        "card_type",
        type=click.Choice(["auto", *(str(kind) for kind in CardType)]),
        default="auto",
        show_default=True,
        help="Card type; auto lets the AI choose per topic.",
    )(cmd)
    return model_options(thinking_default="high for STEM cards", images=True)(cmd)


def build_options(
    llm: str | None,
    image_model: str | None,
    image_size: int | None,
    profile: str | None = None,
    image_profile: str | None = None,
    thinking: str | None = None,
    card_type: str = "auto",
) -> StemCollectionOptions:
    """Convert CLI parameters to typed collection options."""
    return StemCollectionOptions(
        llm_model=llm,
        image_model=image_model,
        image_size=image_size,
        reasoning_effort=resolve_thinking(thinking, unset="high"),
        card_type=None if card_type == "auto" else CardType(card_type),
        profile=profile,
        image_profile=image_profile,
    )


@dataclass(frozen=True, slots=True)
class _WithReferenceImage:
    """Makes every card from the topic plus one reference image."""

    collection: StemCollection
    image: bytes
    mime: str

    def generate_and_add_note(self, text: str, /) -> Awaitable[int]:
        return self.collection.generate_and_add_note(
            text, reference_image=self.image, reference_image_mime=self.mime
        )


def _scope(options: StemCollectionOptions, image_path: Path | None = None):
    @asynccontextmanager
    async def scope():
        async with (
            anki_client_scope() as client,
            build_stem_collection(client, options) as collection,
        ):
            if image_path is None:
                yield collection
            else:
                mime = mimetypes.guess_type(image_path.name)[0] or "image/png"
                yield _WithReferenceImage(collection, image_path.read_bytes(), mime)

    return scope


# -- stem group ---------------------------------------------------------------


@click.group("stem")
def stem():
    """STEM knowledge cards (Math, CS, Finance, ML, ...)."""


@stem.command("init")
@collection_options
def init(llm, profile, thinking, image_model, image_size, image_profile, card_type):
    """Create note types and deck in Anki (only --type's note type if given)."""
    options = build_options(
        llm, image_model, image_size, profile, image_profile, thinking, card_type
    )

    async def _run():
        async with _scope(options)() as collection:
            return collection.deck_name

    deck_name = run(_run())
    click.echo(f"✓ Ready (STEM collection: {deck_name})")


@stem.command("add")
@click.argument("topic")
@click.option(
    "--image",
    "image_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help=(
        "Reference image (e.g. a photographed problem) for the AI to solve "
        "from. Requires a vision-capable --llm model."
    ),
)
@collection_options
def add(
    topic,
    image_path: Path | None,
    llm,
    profile,
    thinking,
    image_model,
    image_size,
    image_profile,
    card_type,
):
    """Generate and push a single STEM card.

    TOPIC is any question or concept (e.g. "What is a derivative?",
    "请解释平行线的概念", "State Bayes' theorem").
    """
    options = build_options(
        llm, image_model, image_size, profile, image_profile, thinking, card_type
    )
    add_one(_scope(options, image_path), topic)


@stem.command("batch")
@click.argument("topics", nargs=-1, metavar="[TOPIC ...]")
@batch_options(
    rpm_default=10,
    rpm_note="STEM cards default lower: each thinks at high and may draw a diagram.",
)
@collection_options
def batch(
    topics: tuple[str, ...],
    file: Path | None,
    rpm: int,
    llm,
    profile,
    thinking,
    image_model,
    image_size,
    image_profile,
    card_type,
):
    """Generate and push multiple STEM cards.

    \b
    Topics can be passed as arguments, read from a file (one per line),
    or both at the same time.

    \b
    Examples:
      ankinote stem batch "What is entropy?" "State Bayes' theorem"
      ankinote stem batch --file topics.txt
      ankinote stem batch --file problems.txt --type example
    """
    items = read_items(topics, file, noun="topics")
    options = build_options(
        llm, image_model, image_size, profile, image_profile, thinking, card_type
    )
    add_many(_scope(options), items, noun="topics", rpm=rpm)
