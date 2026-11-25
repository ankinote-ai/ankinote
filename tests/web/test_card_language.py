"""Card labels and template names follow the native language in settings."""

from typing import Any

import httpx

from ankinote.services.anki_factory import get_shared_runtime
from tests.conftest import set_native_language
from tests.web.anki_fakes import builtin, login


async def _snapshot() -> dict:
    runtime = get_shared_runtime()
    assert runtime is not None

    def read(col: Any) -> dict:
        model = col.models.by_name("AINote Word V2")
        return {
            "names": [t["name"] for t in model["tmpls"]],
            "front": model["tmpls"][0]["qfmt"],
            "cards": col.card_count(),
            "scm": col.db.scalar("select scm from col"),
        }

    return await runtime.submit(read)


async def _add_word_note() -> None:
    runtime = get_shared_runtime()
    assert runtime is not None

    def add(col: Any) -> None:
        note = col.new_note(col.models.by_name("AINote Word V2"))
        note["lemma"] = "moon"
        note["core_meaning"] = "月亮"
        col.add_note(note, col.decks.id("AINote::Words"))

    await runtime.submit_write(add)


async def test_new_native_language_renames_templates_and_keeps_cards(
    api: httpx.AsyncClient, ankiweb: dict[str, Any]
) -> None:
    await builtin(api)
    await login(api)
    assert (await api.post("/api/anki/note-types/word")).status_code == 200
    await _add_word_note()
    before = await _snapshot()
    assert before["names"] == ["辨识", "回想", "拼写"]  # settings default: Chinese
    assert "辨识" in before["front"]

    response = await api.patch(
        "/api/settings",
        json={"native_language": "English", "target_language": "French"},
    )
    assert response.status_code == 200, response.text

    after = await _snapshot()
    assert after["names"] == ["Recognition", "Recall", "Spelling"]
    assert "Recognition" in after["front"]
    assert after["cards"] == before["cards"] == 3  # same cards, review history kept
    assert after["scm"] == before["scm"]  # a rename needs no full AnkiWeb sync

    status = {i["key"]: i for i in (await api.get("/api/anki/note-types")).json()}
    assert status["word"]["state"] == "synced"
    assert status["phrase"]["state"] == "missing"  # never created by a rename


async def test_status_shows_renames_until_the_type_is_updated(
    api: httpx.AsyncClient, ankiweb: dict[str, Any]
) -> None:
    await builtin(api)
    await login(api)
    await api.post("/api/anki/note-types/word")
    await _add_word_note()
    set_native_language("German")  # e.g. changed in the TUI, Anki untouched

    word = next(
        i for i in (await api.get("/api/anki/note-types")).json() if i["key"] == "word"
    )
    assert word["state"] == "update"
    assert word["renamed_templates"] == ["Erkennen", "Abrufen", "Schreibweise"]
    assert word["missing_templates"] == []

    result = (await api.post("/api/anki/note-types/word")).json()
    assert result["state"] == "synced"
    after = await _snapshot()
    assert after["names"] == ["Erkennen", "Abrufen", "Schreibweise"]
    assert after["cards"] == 3
