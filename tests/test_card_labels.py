"""Card labels and template names come in every native language."""

import re
from importlib.resources import files

import pytest

from ankinote import card_labels
from ankinote.consts import NATIVE_LANGUAGES, Language

_TEMPLATES = [
    path
    for package in ("word", "phrase", "sentence", "stem")
    for path in files(f"ankinote.collections.{package}")
    .joinpath("card_templates")
    .glob("**/*.html")
]


def test_every_native_language_has_every_label() -> None:
    english = set(card_labels.catalogs()[Language.ENGLISH])
    for language in NATIVE_LANGUAGES:
        texts = card_labels.catalogs()[language]
        assert set(texts) == english, language
        assert all(text.strip() for text in texts.values()), language


@pytest.mark.parametrize("language", NATIVE_LANGUAGES)
def test_templates_have_no_label_left_unfilled(language: Language) -> None:
    assert _TEMPLATES
    for path in _TEMPLATES:
        raw = path.read_text(encoding="utf-8")
        for key in re.findall(r"\[\[t:([^\]]+)\]\]", raw):
            assert key in card_labels.catalogs()[Language.ENGLISH], (path, key)
        assert "[[" not in card_labels.localize(raw, language), path


def test_each_template_name_belongs_to_one_slot() -> None:
    """Otherwise a rename could pick another slot's template."""
    slots = ["recognition", "recall", "spelling", "production", "card"]
    seen: dict[str, str] = {}
    for slot in slots:
        for language in NATIVE_LANGUAGES:
            name = card_labels.template_name(slot, language)
            assert seen.setdefault(name, slot) == slot, name
            assert card_labels.known_names(name) == card_labels.known_names(
                card_labels.template_name(slot, Language.ENGLISH)
            )


def test_english_keeps_the_names_cards_had_before() -> None:
    english = Language.ENGLISH
    assert [
        card_labels.template_name(s, english)
        for s in ("recognition", "recall", "spelling", "production", "card")
    ] == ["Recognition", "Recall", "Spelling", "Production", "Card 1"]


def test_cards_follow_the_native_language_in_settings() -> None:
    from tests.conftest import set_native_language

    assert card_labels.card_language() == Language.CHINESE_S  # settings default
    set_native_language("Japanese")
    assert card_labels.card_language() == Language.JAPANESE
    assert card_labels.template_name("recall") == "想起"
    set_native_language("not a language")
    assert card_labels.card_language() == Language.ENGLISH
