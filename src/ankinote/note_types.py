"""The note types and decks ankinote manages in Anki.

Used by the web API (wizard "Connect Anki", the Note types workspace) and
the CLI's ``init`` commands. Each spec mirrors what its collection's
``ensure_in_anki()`` writes, so a status computed here matches what setting
it up will actually do.
"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Literal

from ankinote.card_labels import card_language
from ankinote.card_theme import CardTheme, current_theme
from ankinote.collections.common import store_card_fonts, template_upserts
from ankinote.collections.phrase import PhraseCollection
from ankinote.collections.phrase.models import PhraseNoteType
from ankinote.collections.phrase.templates import load_card_style as _phrase_style
from ankinote.collections.sentence import SentenceCollection
from ankinote.collections.sentence.models import SentenceNoteType
from ankinote.collections.sentence.templates import load_card_style as _sentence_style
from ankinote.collections.stem import StemCollection
from ankinote.collections.stem.collection import stem_card_templates
from ankinote.collections.stem.models import NOTE_FIELDS, CardType, note_type_name
from ankinote.collections.stem.templates import load_card_style as _stem_style
from ankinote.collections.word import WordCollection
from ankinote.collections.word.models import WordNoteType
from ankinote.collections.word.templates import load_card_style as _word_style
from ankinote.consts import Language
from ankinote.services.ai import LiteLLMTextService
from ankinote.services.anki import AnkiCollectionClient

State = Literal["synced", "update", "missing"]


@dataclass(frozen=True, slots=True)
class NoteTypeSpec:
    """Static description of one note type ankinote can create/update."""

    key: str
    notetype_name: str  # Anki model name
    deck_name: str  # Anki deck path
    fields: tuple[str, ...]
    card_templates: tuple[dict[str, str], ...]  # as Anki stores them
    css: str
    sync: Callable[[AnkiCollectionClient], Awaitable[None]]

    @property
    def templates(self) -> tuple[str, ...]:
        """The card template names, in the card language."""
        return tuple(template["Name"] for template in self.card_templates)

    @property
    def css_size_kb(self) -> str:
        """Human-readable size of the note type styling."""
        return f"{len(self.css.encode()) / 1024:.1f} KB"


@dataclass(frozen=True, slots=True)
class TypeStatus:
    """Live status of one note type as seen in Anki."""

    spec: NoteTypeSpec
    exists: bool
    deck_exists: bool
    missing_fields: list[str]
    missing_templates: list[str]
    # Templates Anki has under another language's name.
    renamed_templates: list[str]
    css_differs: bool

    @property
    def state(self) -> State:
        if not self.exists:
            return "missing"
        if (
            self.missing_fields
            or self.missing_templates
            or self.renamed_templates
            or self.css_differs
        ):
            return "update"
        return "synced"


def _field_names(note_type) -> tuple[str, ...]:
    return tuple(field.name for field in note_type.__dataclass_fields__.values())


def build_specs(
    theme: CardTheme | None = None, language: Language | None = None
) -> list[NoteTypeSpec]:
    """The fixed set of note types managed by ankinote, in display order.

    Their styling uses ``theme``, or the card theme saved in settings; their
    card templates are in ``language``, or the card language in settings.
    """
    theme = theme or current_theme()
    language = language or card_language()

    def sync_word(notetype_name: str, deck_name: str):
        async def _sync(client: AnkiCollectionClient) -> None:
            collection = WordCollection(
                client,
                native_language=Language.CHINESE_S,
                target_language=Language.ENGLISH,
                notetype_name=notetype_name,
                deck_name=deck_name,
                text_model="",
                text_service=LiteLLMTextService(),
                image_service=None,
            )
            await collection.ensure_in_anki()

        return _sync

    def sync_language(clazz, notetype_name: str, deck_name: str):
        async def _sync(client: AnkiCollectionClient) -> None:
            collection = clazz(
                client,
                native_language=Language.CHINESE_S,
                target_language=Language.ENGLISH,
                notetype_name=notetype_name,
                deck_name=deck_name,
                text_model="",
                text_service=LiteLLMTextService(),
            )
            await collection.ensure_in_anki()

        return _sync

    def sync_stem(card_type: CardType):
        async def _sync(client: AnkiCollectionClient) -> None:
            collection = StemCollection(
                client,
                card_type=card_type,
                text_model="",
                text_service=LiteLLMTextService(),
            )
            await collection.ensure_in_anki()

        return _sync

    return [
        NoteTypeSpec(
            key="word",
            notetype_name="AINote Word V2",
            deck_name="AINote::Words",
            fields=_field_names(WordNoteType),
            card_templates=tuple(WordCollection.card_templates(language)),
            css=_word_style(theme),
            sync=sync_word("AINote Word V2", "AINote::Words"),
        ),
        NoteTypeSpec(
            key="phrase",
            notetype_name="AINote Phrase V2",
            deck_name="AINote::Phrases",
            fields=_field_names(PhraseNoteType),
            card_templates=tuple(PhraseCollection.card_templates(language)),
            css=_phrase_style(theme),
            sync=sync_language(PhraseCollection, "AINote Phrase V2", "AINote::Phrases"),
        ),
        NoteTypeSpec(
            key="sentence",
            notetype_name="AINote Sentence V2",
            deck_name="AINote::Sentences",
            fields=_field_names(SentenceNoteType),
            card_templates=tuple(SentenceCollection.card_templates(language)),
            css=_sentence_style(theme),
            sync=sync_language(
                SentenceCollection, "AINote Sentence V2", "AINote::Sentences"
            ),
        ),
        *[
            NoteTypeSpec(
                key=f"stem_{kind}",
                notetype_name=note_type_name(kind),
                deck_name="AINote::STEM",
                fields=NOTE_FIELDS[kind],
                card_templates=tuple(stem_card_templates(kind, language)),
                css=_stem_style(theme),
                sync=sync_stem(kind),
            )
            for kind in CardType
        ],
    ]


async def load_status(client: AnkiCollectionClient, spec: NoteTypeSpec) -> TypeStatus:
    """Compute one note type's live status from Anki."""
    model = await client.models.get(spec.notetype_name)
    deck_exists = await client.decks.exists(spec.deck_name)
    if model is None:
        return TypeStatus(
            spec=spec,
            exists=False,
            deck_exists=deck_exists,
            missing_fields=[],
            missing_templates=[],
            renamed_templates=[],
            css_differs=False,
        )

    existing_fields = {f.name for f in model.fields}
    existing_templates = {t.name for t in model.templates}
    upserts = template_upserts(list(spec.card_templates))
    matches = {u.name: u.match(existing_templates) for u in upserts}
    return TypeStatus(
        spec=spec,
        exists=True,
        deck_exists=deck_exists,
        missing_fields=[f for f in spec.fields if f not in existing_fields],
        missing_templates=[name for name, found in matches.items() if found is None],
        renamed_templates=[
            name for name, found in matches.items() if found not in (None, name)
        ],
        css_differs=model.css != spec.css,
    )


async def restyle(client: AnkiCollectionClient, specs: list[NoteTypeSpec]) -> list[str]:
    """Give the note types that exist their spec's styling, and nothing else.

    Unlike setting a type up, this never adds fields or card templates (new
    templates would create cards), and types that don't exist stay absent.
    Returns the keys of the types restyled.
    """
    existing = [s for s in specs if await client.models.exists(s.notetype_name)]
    if existing:
        await store_card_fonts(client)
    for spec in existing:
        await client.models.update_styling(spec.notetype_name, spec.css)
    return [spec.key for spec in existing]


async def relabel(client: AnkiCollectionClient, specs: list[NoteTypeSpec]) -> list[str]:
    """Put the existing card templates into the specs' language, and nothing else.

    Renames each template Anki has (under any language's name) and rewrites
    its labels. Like :func:`restyle`, it never adds fields or templates, and
    types that don't exist stay absent. Returns the keys of the types updated.
    """
    updated = []
    for spec in specs:
        model = await client.models.get(spec.notetype_name)
        if model is None:
            continue
        existing = {t.name for t in model.templates}
        upserts = [
            u
            for u in template_upserts(list(spec.card_templates))
            if u.match(existing) is not None
        ]
        if upserts:
            await client.models.update_templates(spec.notetype_name, upserts)
            updated.append(spec.key)
    return updated
