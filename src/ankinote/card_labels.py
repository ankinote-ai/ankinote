"""The words ankinote writes into Anki, in the user's native language.

Two kinds, both from ``card_labels.json``:

- Labels printed on the cards (section titles, badges). Card templates
  mark them as ``[[t:key]]``; :func:`localize` fills them in.
- Card template names (``template.<slot>``), which Anki shows in its browser
  and statistics. A template keeps its slot when the language changes, so
  :func:`known_names` lists every name a slot has had, to find and rename it.

The language is the native language saved in settings, never a per-run CLI
option: the note types are shared, so they follow one setting.
"""

import json
import re
from functools import cache
from importlib.resources import files

from ankinote.consts import Language

_PLACEHOLDER = re.compile(r"\[\[t:([a-z_.]+)\]\]")
_TEMPLATE_PREFIX = "template."


@cache
def catalogs() -> dict[Language, dict[str, str]]:
    """Language -> label key -> text."""
    raw = json.loads(
        files("ankinote").joinpath("card_labels.json").read_text(encoding="utf-8")
    )
    return {Language(lang): labels for lang, labels in raw.items()}


def card_language() -> Language:
    """The native language in settings, or English if it has no labels."""
    from ankinote.settings import load_settings

    try:
        language = Language(load_settings().defaults.native_language)
    except ValueError:
        return Language.ENGLISH
    return language if language in catalogs() else Language.ENGLISH


def label(key: str, language: Language | None = None) -> str:
    """One label's text; English when the language lacks it."""
    language = language or card_language()
    texts = catalogs().get(language, {})
    return texts.get(key) or catalogs()[Language.ENGLISH][key]


def localize(template: str, language: Language | None = None) -> str:
    """Fill in a card template's ``[[t:key]]`` labels."""
    language = language or card_language()
    return _PLACEHOLDER.sub(lambda m: label(m.group(1), language), template)


def template_name(slot: str, language: Language | None = None) -> str:
    """The name of a card template slot (``recognition``, ``card``, …)."""
    return label(_TEMPLATE_PREFIX + slot, language)


def known_names(name: str) -> tuple[str, ...]:
    """Every name, in any language, of the slot that ``name`` belongs to.

    ``(name,)`` when it is no slot's name.
    """
    for slot in _slots():
        names = _slot_names(slot)
        if name in names:
            return names
    return (name,)


@cache
def _slots() -> tuple[str, ...]:
    english = catalogs()[Language.ENGLISH]
    return tuple(
        key.removeprefix(_TEMPLATE_PREFIX)
        for key in english
        if key.startswith(_TEMPLATE_PREFIX)
    )


@cache
def _slot_names(slot: str) -> tuple[str, ...]:
    key = _TEMPLATE_PREFIX + slot
    return tuple(dict.fromkeys(texts[key] for texts in catalogs().values()))
