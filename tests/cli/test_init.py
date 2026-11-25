"""`init` is the CLI's one way to update an existing note type."""

import importlib

import pytest
from click.testing import CliRunner

KINDS = ["word", "phrase", "sentence", "stem"]


@pytest.mark.parametrize("kind", KINDS)
def test_init_creates_or_updates_the_note_type(kind, capture_options):
    module = importlib.import_module(f"ankinote.cli.{kind}")
    captured = capture_options(module)

    result = CliRunner().invoke(getattr(module, kind), ["init"])

    assert result.exit_code == 0, result.output
    assert captured.get("ensured") is True


@pytest.mark.parametrize("kind", KINDS)
def test_add_does_not_update_the_note_type(kind, capture_options):
    module = importlib.import_module(f"ankinote.cli.{kind}")
    captured = capture_options(module)

    result = CliRunner().invoke(getattr(module, kind), ["add", "x"])

    assert result.exit_code == 0, result.output
    assert "ensured" not in captured
