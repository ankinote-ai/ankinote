"""The sentence an item came from (context) reaches the word and phrase prompts.

Without context, what is sent to the model is the language prompt and the
rules for reporting problems with the input, nothing more.
"""

from collections.abc import Sequence
from importlib.resources import files

import pytest

from ankinote.collections.phrase.collection import PhraseCollection
from ankinote.collections.phrase.generator import PhraseGenerator
from ankinote.collections.word.collection import WordCollection
from ankinote.collections.word.generator import WordGenerator
from ankinote.consts import Language
from ankinote.services.ai import TextMessage

WORD_JSON = """[{
  "lemma": "bank", "part_of_speech": "noun", "difficulty": "A2",
  "core_meaning": {"target_text": "the side of a river", "native_text": "河岸"},
  "examples": [{"sentence": "We sat on the bank of the river.",
                "translation": "我们坐在河岸上。", "highlights": ["bank"]}]
}]"""

PHRASE_JSON = """{
  "phrase": "pick up", "difficulty": "A2",
  "core_meaning": {"target_text": "to collect someone", "native_text": "接（某人）"},
  "examples": [{"sentence": "I'll pick you up at six.",
                "translation": "我六点来接你。", "highlights": ["pick", "up"]}],
  "production_hint": "开车去接人"
}"""

BANK = "We sat on the bank of the river."
PICK_UP = "I'll pick you up at six."


class FakeTextService:
    def __init__(self, response: str) -> None:
        self._response = response
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
        return self._response


def _prompt(package: str, name: str) -> str:
    return (
        files(f"ankinote.collections.{package}.prompts")
        .joinpath(name)
        .read_text(encoding="utf-8")
    )


async def _word(
    context: str | None = None, target: Language = Language.ENGLISH
) -> tuple[str, str]:
    service = FakeTextService(WORD_JSON)
    generator = WordGenerator(
        tts_service=None, text_service=service, image_service=None, text_model="m"
    )
    kwargs = {} if context is None else {"context": context}
    await generator.generate_word_data("bank", target, Language.CHINESE_S, **kwargs)
    system, user = service.messages
    return str(system["content"]), str(user["content"])


async def _phrase(
    context: str | None = None, target: Language = Language.ENGLISH
) -> tuple[str, str]:
    service = FakeTextService(PHRASE_JSON)
    generator = PhraseGenerator(tts_service=None, text_service=service, text_model="m")
    kwargs = {} if context is None else {"context": context}
    await generator.generate_phrase_data(
        "pick up", target, Language.CHINESE_S, **kwargs
    )
    system, user = service.messages
    return str(system["content"]), str(user["content"])


@pytest.mark.parametrize(
    ("target", "prompt_file"),
    [(Language.ENGLISH, "latin_alphabet.md"), (Language.CHINESE_S, "chinese.md")],
)
async def test_word_prompt_without_context_is_unchanged(target, prompt_file):
    system, user = await _word(target=target)

    assert system == _prompt("word", prompt_file) + "\n\n" + _prompt(
        "word", "input_issues.md"
    )
    assert user == (
        "Word: bank\n"
        f"Target language: {target.value}\n"
        "Native language: Chinese(Simplified)\n"
        "Goal: Create concise Anki cards optimized for recognition, recall, and spelling."
    )


@pytest.mark.parametrize(
    ("target", "prompt_file"),
    [(Language.ENGLISH, "latin_alphabet.md"), (Language.JAPANESE, "japanese.md")],
)
async def test_phrase_prompt_without_context_is_unchanged(target, prompt_file):
    system, user = await _phrase(target=target)

    assert system == _prompt("phrase", prompt_file) + "\n\n" + _prompt(
        "phrase", "input_issues.md"
    )
    assert user == (
        "Phrase: pick up\n"
        f"Target language: {target.value}\n"
        "Native language: Chinese(Simplified)"
    )


async def test_blank_context_counts_as_none():
    assert await _word("  ") == await _word()
    assert await _phrase("") == await _phrase()


@pytest.mark.parametrize("target", [Language.ENGLISH, Language.CHINESE_S])
async def test_word_context_adds_the_sentence_and_the_one_sense_rules(target):
    plain_system, plain_user = await _word(target=target)

    system, user = await _word(f"  {BANK}\n", target=target)

    assert system == plain_system + "\n\n" + _prompt("word", "context.md")
    assert user == plain_user + f"\nContext: {BANK}"


@pytest.mark.parametrize("target", [Language.ENGLISH, Language.KOREAN])
async def test_phrase_context_adds_the_sentence_and_the_one_sense_rules(target):
    plain_system, plain_user = await _phrase(target=target)

    system, user = await _phrase(PICK_UP, target=target)

    assert system == plain_system + "\n\n" + _prompt("phrase", "context.md")
    assert user == plain_user + f"\nContext: {PICK_UP}"


@pytest.mark.parametrize("package", ["word", "phrase"])
def test_context_rules_cover_one_sense_and_the_verbatim_example(package):
    rules = _prompt(package, "context.md")

    assert "Context:" in rules
    assert "exactly" in rules  # the sentence is copied, not rephrased
    assert "never about another" in rules  # the card stays on the queried item


async def test_word_collection_passes_context_to_the_prompt():
    service = FakeTextService(WORD_JSON)
    collection = WordCollection(
        None,
        native_language=Language.CHINESE_S,
        target_language=Language.ENGLISH,
        text_model="m",
        text_service=service,
        image_service=None,
    )

    [card] = await collection.generate_cards("bank", context=BANK)

    assert card.model.lemma == "bank"
    assert str(service.messages[1]["content"]).endswith(f"\nContext: {BANK}")


async def test_phrase_collection_passes_context_to_the_prompt():
    service = FakeTextService(PHRASE_JSON)
    collection = PhraseCollection(
        None,
        native_language=Language.CHINESE_S,
        target_language=Language.ENGLISH,
        text_model="m",
        text_service=service,
    )

    [card] = await collection.generate_cards("pick up", context=PICK_UP)

    assert card.model.phrase == "pick up"
    assert str(service.messages[1]["content"]).endswith(f"\nContext: {PICK_UP}")
