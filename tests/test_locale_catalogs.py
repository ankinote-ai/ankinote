"""Every interface language carries the same keys and placeholders as English."""

import json
import re
from pathlib import Path

import pytest

LOCALES = Path(__file__).parents[1] / "frontend" / "src" / "lib" / "locales"
PLACEHOLDER = re.compile(r"\{(\w+)\}")


def _load(name: str) -> dict[str, str]:
    return json.loads((LOCALES / f"{name}.json").read_text(encoding="utf-8"))


EN = _load("en")
OTHERS = sorted(p.stem for p in LOCALES.glob("*.json") if p.stem != "en")


def test_every_interface_language_is_present() -> None:
    assert OTHERS == ["de", "es", "fr", "ja", "ko", "zh-CN", "zh-Hant"]


@pytest.mark.parametrize("name", OTHERS)
def test_catalog_matches_english(name: str) -> None:
    catalog = _load(name)
    assert set(catalog) == set(EN)
    for key, text in EN.items():
        assert set(PLACEHOLDER.findall(catalog[key])) == set(
            PLACEHOLDER.findall(text)
        ), key
