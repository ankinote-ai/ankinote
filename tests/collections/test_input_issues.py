"""Problems the model sees in the input reach the caller instead of vanishing.

Language cards mirror the input: a line with several sentences becomes one
long card, a typo stays on the card. The model now reports such problems
next to the card (``input_issues``); they are never stored on the note.
"""

import json
from collections.abc import Sequence

import pytest

from ankinote.collections.common import InputIssue, input_issues
from ankinote.collections.phrase.collection import PhraseCollection
from ankinote.collections.sentence.collection import SentenceCollection
from ankinote.collections.word.collection import WordCollection
from ankinote.consts import Language
from ankinote.services.ai import TextMessage

TWO_SENTENCES = "I overslept. The bus was late."
TWO_SENTENCES_ANSWER = {
    "target_sentence": TWO_SENTENCES,
    "native_sentence": "我睡过头了。公交车晚点了。",
    "notes": [],
    "phrases": [],
    "input_issues": [
        {
            "kind": "several",
            "note": "这一行有两个句子。",
            "parts": ["I overslept.", "The bus was late."],
        }
    ],
}

RECIEVE_ANSWER = [
    {
        "lemma": "recieve",
        "part_of_speech": "verb",
        "difficulty": "A2",
        "core_meaning": {"target_text": "to get something", "native_text": "收到"},
        "examples": [
            {"sentence": "I recieved a letter.", "translation": "我收到一封信。"}
        ],
        "input_issues": [
            {"kind": "typo", "note": "拼写可能有误。", "correction": "receive"}
        ],
    }
]


class FakeTextService:
    def __init__(self, answer: object) -> None:
        self._answer = json.dumps(answer)
        self.messages: Sequence[TextMessage] = ()

    async def generate_text(
        self,
        *,
        model: str,
        messages: Sequence[TextMessage],
        temperature: float | None = None,
        reasoning_effort: str | None = None,
    ) -> str:
        self.messages = messages
        return self._answer


def _languages() -> dict[str, Language]:
    return {
        "native_language": Language.CHINESE_S,
        "target_language": Language.ENGLISH,
    }


@pytest.mark.asyncio
async def test_a_line_with_two_sentences_is_flagged_not_silently_kept():
    service = FakeTextService(TWO_SENTENCES_ANSWER)
    collection = SentenceCollection(
        None, text_model="m", text_service=service, tts_service=None, **_languages()
    )

    cards = await collection.generate_cards(TWO_SENTENCES)

    assert input_issues(TWO_SENTENCES, cards) == [
        InputIssue(
            kind="several",
            note="这一行有两个句子。",
            parts=["I overslept.", "The bus was late."],
        )
    ]
    system = str(service.messages[0]["content"])
    assert "input_issues" in system


@pytest.mark.asyncio
async def test_a_kept_typo_is_flagged_with_its_correction():
    service = FakeTextService(RECIEVE_ANSWER)
    collection = WordCollection(
        None,
        text_model="m",
        text_service=service,
        image_service=None,
        tts_service=None,
        **_languages(),
    )

    cards = await collection.generate_cards("recieve")

    [issue] = input_issues("recieve", cards)
    assert (issue.kind, issue.correction) == ("typo", "receive")
    assert "input_issues" in str(service.messages[0]["content"])


@pytest.mark.asyncio
async def test_phrase_prompt_asks_for_problems_too():
    answer = {
        "phrase": "pick up",
        "difficulty": "A2",
        "core_meaning": {"target_text": "collect", "native_text": "接"},
        "examples": [{"sentence": "Pick me up.", "translation": "来接我。"}],
        "production_hint": "接人",
    }
    service = FakeTextService(answer)
    collection = PhraseCollection(
        None, text_model="m", text_service=service, tts_service=None, **_languages()
    )

    cards = await collection.generate_cards("pick up")

    assert input_issues("pick up", cards) == []
    assert "input_issues" in str(service.messages[0]["content"])


@pytest.mark.asyncio
async def test_a_malformed_problem_never_costs_the_card():
    answer = {
        **TWO_SENTENCES_ANSWER,
        "input_issues": [
            {"kind": "made_up"},
            "not an object",
            {"kind": "fragment", "note": "句子不完整。"},
        ],
    }
    collection = SentenceCollection(
        None,
        text_model="m",
        text_service=FakeTextService(answer),
        tts_service=None,
        **_languages(),
    )

    cards = await collection.generate_cards(TWO_SENTENCES)

    assert [i.kind for i in input_issues(TWO_SENTENCES, cards)] == ["fragment"]


@pytest.mark.asyncio
async def test_problems_are_not_stored_on_the_note():
    collection = SentenceCollection(
        None,
        text_model="m",
        text_service=FakeTextService(TWO_SENTENCES_ANSWER),
        tts_service=None,
        **_languages(),
    )

    [card] = await collection.generate_cards(TWO_SENTENCES)

    fields = collection.note_fields(card)
    assert not any("overslept." in v and "bus" not in v for v in fields.values())
    assert "这一行有两个句子" not in json.dumps(fields, ensure_ascii=False)


def test_input_issues_drops_repeats_and_problems_that_say_nothing():
    """A word's notes each carry the same problems; a "typo" whose correction
    is the input, or "several" with one part, contradicts itself."""
    typo = InputIssue(kind="typo", note="", correction="receive")
    other_language = InputIssue(kind="wrong_language", correction=" ")

    class Card:
        def __init__(self, *issues: InputIssue) -> None:
            self.model = type("M", (), {"input_issues": list(issues)})()

    cards = [
        Card(typo, InputIssue(kind="typo", correction=" recieve ")),
        Card(typo, InputIssue(kind="several", parts=["only one", " "])),
        Card(other_language),
    ]

    assert input_issues("recieve", cards) == [
        typo,
        InputIssue(kind="wrong_language", correction=None),
    ]


# -- Words and phrases: a typo is corrected on the card, and said so -----------

RECEIVE_ANSWER = [
    {
        **RECIEVE_ANSWER[0],
        "lemma": "receive",
        "examples": [
            {"sentence": "I received a letter.", "translation": "我收到一封信。"}
        ],
        "input_issues": [
            {"kind": "corrected", "note": "拼写可能有误。", "correction": "receive"}
        ],
    }
]


def _word_collection(service: FakeTextService) -> WordCollection:
    return WordCollection(
        None,
        text_model="m",
        text_service=service,
        image_service=None,
        tts_service=None,
        **_languages(),
    )


@pytest.mark.parametrize("package", ["word", "phrase"])
def test_word_and_phrase_prompts_correct_a_typo_on_the_card(package):
    from importlib.resources import files

    rules = (
        files(f"ankinote.collections.{package}.prompts")
        .joinpath("input_issues.md")
        .read_text(encoding="utf-8")
    )

    assert '"corrected"' in rules
    assert '"typo"' not in rules  # never a card made from the misspelling


def test_sentence_prompt_keeps_a_typo_on_the_card():
    from importlib.resources import files

    rules = (
        files("ankinote.collections.sentence.prompts")
        .joinpath("input_issues.md")
        .read_text(encoding="utf-8")
    )

    assert '"typo"' in rules
    assert '"corrected"' not in rules


@pytest.mark.asyncio
async def test_a_misspelled_word_makes_the_card_for_the_correction():
    collection = _word_collection(FakeTextService(RECEIVE_ANSWER))

    cards = await collection.generate_cards("recieve")

    assert [card.model.lemma for card in cards] == ["receive"]
    [issue] = input_issues("recieve", cards)
    assert (issue.kind, issue.correction) == ("corrected", "receive")


@pytest.mark.asyncio
async def test_as_typed_tells_the_model_not_to_correct():
    plain, typed = FakeTextService(RECIEVE_ANSWER), FakeTextService(RECIEVE_ANSWER)

    await _word_collection(plain).generate_cards("recieve")
    await _word_collection(typed).generate_cards("recieve", as_typed=True)

    assert plain.messages[0] == typed.messages[0]
    plain_user = str(plain.messages[1]["content"])
    typed_user = str(typed.messages[1]["content"])
    assert typed_user.startswith(plain_user + "\n")
    assert "as typed" in typed_user.removeprefix(plain_user)


@pytest.mark.asyncio
async def test_phrase_as_typed_tells_the_model_not_to_correct():
    answer = {
        "phrase": "pick up",
        "difficulty": "A2",
        "core_meaning": {"target_text": "collect", "native_text": "接"},
        "examples": [{"sentence": "Pick me up.", "translation": "来接我。"}],
    }
    service = FakeTextService(answer)
    collection = PhraseCollection(
        None, text_model="m", text_service=service, tts_service=None, **_languages()
    )

    await collection.generate_cards("pick up", as_typed=True)

    assert "as typed" in str(service.messages[1]["content"])


def test_a_correction_that_is_the_input_says_nothing():
    class Card:
        model = type(
            "M",
            (),
            {"input_issues": [InputIssue(kind="corrected", correction="receive")]},
        )()

    assert input_issues("receive", [Card()]) == []
