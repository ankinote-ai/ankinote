"""--native/--target default to the languages saved in settings."""

import pytest
from click.testing import CliRunner

from ankinote.consts import Language
from ankinote.settings import DefaultsConfig, Settings, save_settings

COMMANDS = [
    ("word", ["add", "neko"]),
    ("phrase", ["add", "neko ni koban"]),
    ("sentence", ["add", "neko ga suki desu"]),
]


def _save_languages(native: str, target: str) -> None:
    defaults = DefaultsConfig(native_language=native, target_language=target)
    save_settings(Settings(defaults=defaults))


def _invoke(name: str, args: list[str]):
    from ankinote.cli import phrase, sentence, word

    module = {"word": word, "phrase": phrase, "sentence": sentence}[name]
    return module, getattr(module, name)


@pytest.mark.parametrize(("name", "args"), COMMANDS)
def test_languages_default_to_settings(capture_options, name, args):
    _save_languages("English", "Japanese")
    module, group = _invoke(name, args)
    captured = capture_options(module)

    result = CliRunner().invoke(group, args)

    assert result.exit_code == 0, result.output
    assert captured["options"].native_language == Language.ENGLISH
    assert captured["options"].target_language == Language.JAPANESE


@pytest.mark.parametrize(("name", "args"), COMMANDS)
def test_flags_override_settings(capture_options, name, args):
    _save_languages("English", "Japanese")
    module, group = _invoke(name, args)
    captured = capture_options(module)

    result = CliRunner().invoke(group, [*args, "--native", "German"])

    assert result.exit_code == 0, result.output
    assert captured["options"].native_language == Language.GERMAN
    assert captured["options"].target_language == Language.JAPANESE


def test_without_settings_file_keeps_old_defaults(capture_options):
    from ankinote.cli import word

    captured = capture_options(word)

    result = CliRunner().invoke(word.word, ["add", "heat"])

    assert result.exit_code == 0, result.output
    assert captured["options"].native_language == Language.CHINESE_S
    assert captured["options"].target_language == Language.ENGLISH
