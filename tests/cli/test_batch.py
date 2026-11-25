"""Shared behavior of the card commands' ``add`` and ``batch``."""

import importlib

import pytest
from click.testing import CliRunner

KINDS = ["word", "phrase", "sentence", "stem"]


def _group(kind: str):
    module = importlib.import_module(f"ankinote.cli.{kind}")
    return module, getattr(module, kind)


@pytest.mark.parametrize("kind", KINDS)
def test_batch_exits_1_and_names_the_failed_item(kind, capture_options):
    module, group = _group(kind)
    captured = capture_options(module, fail={"xyzzy"})

    result = CliRunner().invoke(group, ["batch", "apple", "xyzzy", "pear"])

    assert result.exit_code == 1, result.output
    assert sorted(captured["items"]) == ["apple", "pear", "xyzzy"]
    assert "2/3" in result.output
    assert "xyzzy: boom: xyzzy" in result.output


@pytest.mark.parametrize("kind", KINDS)
def test_batch_exits_0_when_every_item_is_saved(kind, capture_options):
    module, group = _group(kind)
    capture_options(module)

    result = CliRunner().invoke(group, ["batch", "apple", "pear"])

    assert result.exit_code == 0, result.output


@pytest.mark.parametrize("kind", KINDS)
def test_batch_file_reads_one_item_per_line(kind, capture_options, tmp_path):
    module, group = _group(kind)
    captured = capture_options(module)
    items = tmp_path / "items.txt"
    items.write_text("apple\n  ice cream \n\n", encoding="utf-8")

    result = CliRunner().invoke(group, ["batch", "pear", "-f", str(items)])

    assert result.exit_code == 0, result.output
    assert sorted(captured["items"]) == ["apple", "ice cream", "pear"]


@pytest.mark.parametrize("kind", KINDS)
def test_batch_without_items_is_a_usage_error(kind, capture_options):
    module, group = _group(kind)
    capture_options(module)

    result = CliRunner().invoke(group, ["batch"])

    assert result.exit_code == 2, result.output


@pytest.mark.parametrize("kind", KINDS)
def test_batch_rpm_0_means_no_limit(kind, capture_options):
    module, group = _group(kind)
    captured = capture_options(module)

    result = CliRunner().invoke(group, ["batch", "apple", "pear", "--rpm", "0"])

    assert result.exit_code == 0, result.output
    assert len(captured["items"]) == 2


@pytest.mark.parametrize("kind", KINDS)
def test_add_prints_the_saved_note_ids(kind, capture_options):
    module, group = _group(kind)
    capture_options(module, note_ids=[1712, 1713])

    result = CliRunner().invoke(group, ["add", "apple"])

    assert result.exit_code == 0, result.output
    assert "1712" in result.output
    assert "1713" in result.output


@pytest.mark.parametrize("kind", KINDS)
def test_add_failure_is_a_one_line_error(kind, capture_options):
    module, group = _group(kind)
    capture_options(module, fail={"xyzzy"})

    result = CliRunner().invoke(group, ["add", "xyzzy"])

    assert result.exit_code == 1, result.output
    # A handled click error, not an exception escaping with a traceback.
    assert isinstance(result.exception, SystemExit)
    assert "Error: xyzzy: boom: xyzzy" in result.output


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("command", [["init"], ["add", "apple"], ["batch", "apple"]])
def test_unreachable_anki_is_a_one_line_error(kind, command, unreachable_anki):
    module, group = _group(kind)
    unreachable_anki(module)

    result = CliRunner().invoke(group, command)

    assert result.exit_code == 1, result.output
    assert isinstance(result.exception, SystemExit)
    assert "Error: Anki is not running" in result.output
