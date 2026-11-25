"""Shared fixtures for CLI tests."""

from collections.abc import Callable, Iterable
from contextlib import asynccontextmanager

import pytest


@pytest.fixture
def capture_options(monkeypatch):
    """Patch a CLI module's collection builder to record what it gets.

    Call it with the CLI module; it returns a dict whose ``"options"`` key holds
    the typed collection options after the command runs, and whose ``"items"``
    key lists the inputs the collection was asked to generate, in order;
    ``"note_kwargs"`` holds the keyword arguments of the last call.
    Inputs listed in ``fail`` raise ``RuntimeError("boom: <input>")``; the
    others are saved as note ``1``, or ``note_ids`` when a list is given.
    """

    def capture(
        module, *, fail: Iterable[str] = (), note_ids: list[int] | None = None
    ) -> dict[str, object]:
        failing = set(fail)
        items: list[str] = []
        captured: dict[str, object] = {"items": items}

        @asynccontextmanager
        async def fake_client_scope():
            yield object()

        class _FakeCollection:
            deck_name = "deck"

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return None

            async def generate_and_add_note(self, text, *args, **kwargs):
                items.append(text)
                captured["note_kwargs"] = kwargs
                if text in failing:
                    raise RuntimeError(f"boom: {text}")
                return 1 if note_ids is None else note_ids

        def fake_builder(client, options):
            captured["options"] = options
            return _FakeCollection()

        monkeypatch.setattr(module, "anki_client_scope", fake_client_scope)
        monkeypatch.setattr(module, _builder_name(module), fake_builder)
        return captured

    return capture


@pytest.fixture
def unreachable_anki(monkeypatch) -> Callable[[object], None]:
    """Make a CLI module's Anki connection fail before any card is made."""

    def patch(module) -> None:
        @asynccontextmanager
        async def failing_client_scope():
            raise ConnectionError("Anki is not running")
            yield  # pragma: no cover

        monkeypatch.setattr(module, "anki_client_scope", failing_client_scope)

    return patch


def _builder_name(module) -> str:
    return next(
        name
        for name in vars(module)
        if name.startswith("build_") and name.endswith("_collection")
    )
