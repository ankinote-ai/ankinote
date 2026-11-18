"""Shared fixtures for CLI tests."""

from contextlib import asynccontextmanager

import pytest


@pytest.fixture
def capture_options(monkeypatch):
    """Patch a CLI module's collection builder to record the options it gets.

    Call it with the CLI module; it returns a dict whose ``"options"`` key holds
    the typed collection options after the command runs.
    """

    def capture(module) -> dict[str, object]:
        captured: dict[str, object] = {}

        @asynccontextmanager
        async def fake_client_scope():
            yield object()

        class _FakeCollection:
            deck_name = "deck"

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return None

            async def generate_and_add_note(self, *args, **kwargs):
                return 1

        def fake_builder(client, options):
            captured["options"] = options
            return _FakeCollection()

        monkeypatch.setattr(module, "anki_client_scope", fake_client_scope)
        builder_name = next(
            name
            for name in vars(module)
            if name.startswith("build_") and name.endswith("_collection")
        )
        monkeypatch.setattr(module, builder_name, fake_builder)
        return captured

    return capture
