"""The sentence an item came from: ``add --context`` and ``batch --format jsonl``."""

import importlib
import json

import pytest
from click.testing import CliRunner

CONTEXT_KINDS = ["word", "phrase"]
BANK = "We sat on the bank of the river."


def _group(kind: str):
    module = importlib.import_module(f"ankinote.cli.{kind}")
    return module, getattr(module, kind)


def _jsonl(*records: object) -> str:
    return "".join(json.dumps(record) + "\n" for record in records)


@pytest.mark.parametrize("kind", CONTEXT_KINDS)
def test_add_context_reaches_the_collection(kind, capture_options):
    module, group = _group(kind)
    captured = capture_options(module)

    result = CliRunner().invoke(group, ["add", "bank", "--context", BANK])

    assert result.exit_code == 0, result.output
    assert captured["note_kwargs"] == {"context": BANK}


@pytest.mark.parametrize("kind", CONTEXT_KINDS)
def test_add_without_context_calls_the_collection_as_before(kind, capture_options):
    module, group = _group(kind)
    captured = capture_options(module)

    result = CliRunner().invoke(group, ["add", "bank"])

    assert result.exit_code == 0, result.output
    assert captured["note_kwargs"] == {}


@pytest.mark.parametrize("kind", CONTEXT_KINDS)
def test_add_json_echoes_the_context(kind, capture_options):
    module, group = _group(kind)
    capture_options(module, note_ids=[7])

    result = CliRunner().invoke(group, ["add", "bank", "--context", BANK, "--json"])

    assert result.exit_code == 0, result.stderr
    [item] = json.loads(result.stdout)["results"]
    assert item == {
        "input": "bank",
        "context": BANK,
        "ok": True,
        "note_ids": [7],
        "issues": [],
    }


@pytest.mark.parametrize("kind", CONTEXT_KINDS)
def test_batch_jsonl_reads_items_with_optional_context(kind, capture_options):
    module, group = _group(kind)
    captured = capture_options(module, note_ids=[1])
    stdin = _jsonl({"text": "bank", "context": BANK}, {"text": "ice cream"}) + "\n"

    result = CliRunner().invoke(
        group,
        ["batch", "pear", "--format", "jsonl", "--file", "-", "--json"],
        input=stdin,
    )

    assert result.exit_code == 0, result.stderr
    assert captured["kwargs_by_item"] == {
        "pear": {},
        "bank": {"context": BANK},
        "ice cream": {},
    }
    results = json.loads(result.stdout)["results"]
    assert [r.get("context") for r in results] == [None, BANK, None]
    assert "context" not in results[0]


@pytest.mark.parametrize("kind", CONTEXT_KINDS)
@pytest.mark.parametrize(
    ("line", "problem"),
    [
        ("bank", "line 2: not JSON"),
        ('["bank"]', "line 2: expected an object"),
        ('{"context": "x"}', 'line 2: "text" must be a non-empty string'),
        ('{"text": "bank", "context": 3}', 'line 2: "context" must be a string'),
        ('{"text": "bank", "sentence": "x"}', 'line 2: unknown key "sentence"'),
    ],
)
def test_batch_jsonl_bad_line_is_a_usage_error(kind, line, problem, capture_options):
    module, group = _group(kind)
    captured = capture_options(module)
    stdin = _jsonl({"text": "pear"}) + line + "\n"

    result = CliRunner().invoke(
        group, ["batch", "--format", "jsonl", "--file", "-"], input=stdin
    )

    assert result.exit_code == 2
    assert problem in result.stderr
    assert captured["items"] == []


@pytest.mark.parametrize("kind", CONTEXT_KINDS)
def test_batch_lines_format_keeps_json_text_as_an_item(kind, capture_options):
    module, group = _group(kind)
    captured = capture_options(module)

    result = CliRunner().invoke(
        group, ["batch", "--file", "-"], input='{"text": "bank"}\n'
    )

    assert result.exit_code == 0, result.output
    assert captured["items"] == ['{"text": "bank"}']


@pytest.mark.parametrize("kind", ["sentence", "stem"])
@pytest.mark.parametrize(
    "args", [["add", "x", "--context", BANK], ["batch", "--format", "jsonl", "x"]]
)
def test_sentence_and_stem_take_no_context(kind, args, capture_options):
    module, group = _group(kind)
    capture_options(module)

    result = CliRunner().invoke(group, args)

    assert result.exit_code == 2
    assert "No such option" in result.output


@pytest.mark.parametrize("kind", CONTEXT_KINDS)
def test_add_as_typed_reaches_the_collection(kind, capture_options):
    """The way back when the model corrected a spelling that was meant."""
    module, group = _group(kind)
    captured = capture_options(module)

    result = CliRunner().invoke(group, ["add", "recieve", "--as-typed"])

    assert result.exit_code == 0, result.output
    assert captured["note_kwargs"] == {"as_typed": True}


@pytest.mark.parametrize("kind", ["sentence", "stem"])
def test_as_typed_is_only_for_words_and_phrases(kind):
    _, group = _group(kind)

    result = CliRunner().invoke(group, ["add", "recieve", "--as-typed"])

    assert result.exit_code == 2
