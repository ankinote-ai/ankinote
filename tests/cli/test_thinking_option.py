"""The --thinking CLI flag reaches the typed collection options."""

import pytest
from click.testing import CliRunner

from ankinote.services.ai import DISABLE_REASONING


@pytest.mark.parametrize(
    "command", [["init"], ["add", "topic"], ["batch", "topic", "--rpm", "0"]]
)
@pytest.mark.parametrize("kind", ["auto", "concept", "formula", "procedure", "example"])
def test_stem_type_selection_reaches_collection(command, kind, capture_options):
    from ankinote.cli import stem

    captured = capture_options(stem)
    result = CliRunner().invoke(stem.stem, [*command, "--type", kind])
    assert result.exit_code == 0, result.output
    assert captured["options"].card_type == (None if kind == "auto" else kind)


def test_stem_add_thinking_off(capture_options):
    from ankinote.cli import stem

    captured = capture_options(stem)
    result = CliRunner().invoke(
        stem.stem, ["add", "What is a derivative?", "--thinking", "off"]
    )

    assert result.exit_code == 0, result.output
    assert captured["options"].reasoning_effort == DISABLE_REASONING


def test_stem_add_thinking_defaults_to_high(capture_options):
    from ankinote.cli import stem

    captured = capture_options(stem)
    result = CliRunner().invoke(stem.stem, ["add", "What is a derivative?"])

    assert result.exit_code == 0, result.output
    assert captured["options"].reasoning_effort == "high"


def test_word_add_thinking_high(capture_options):
    from ankinote.cli import word

    captured = capture_options(word)
    result = CliRunner().invoke(word.word, ["add", "heat", "--thinking", "high"])

    assert result.exit_code == 0, result.output
    assert captured["options"].reasoning_effort == "high"


def test_word_add_thinking_defaults_to_disabled(capture_options):
    from ankinote.cli import word

    captured = capture_options(word)
    result = CliRunner().invoke(word.word, ["add", "heat"])

    assert result.exit_code == 0, result.output
    assert captured["options"].reasoning_effort == DISABLE_REASONING
