"""The --profile/--image-profile CLI flags reach the typed collection options."""

from click.testing import CliRunner

from ankinote.settings import ProviderProfile, Settings, save_settings


def test_word_add_profile_reaches_options(capture_options):
    from ankinote.cli import word

    captured = capture_options(word)
    result = CliRunner().invoke(
        word.word,
        ["add", "heat", "--profile", "mine", "--image-profile", "images"],
    )

    assert result.exit_code == 0, result.output
    assert captured["options"].profile == "mine"
    assert captured["options"].image_profile == "images"


def test_stem_add_profile_reaches_options(capture_options):
    from ankinote.cli import stem

    captured = capture_options(stem)
    result = CliRunner().invoke(
        stem.stem,
        ["add", "What is a derivative?", "--profile", "mine"],
    )

    assert result.exit_code == 0, result.output
    assert captured["options"].profile == "mine"


def test_word_add_unknown_profile_lists_available_profiles():
    from ankinote.cli import word

    save_settings(
        Settings(
            text_providers={"OpenAI": ProviderProfile(vendor="OpenAI", model="gpt-4o")}
        )
    )

    result = CliRunner().invoke(word.word, ["add", "heat", "--profile", "bogus"])

    assert result.exit_code == 2
    assert "bogus" in result.output
    assert "OpenAI" in result.output


def test_stem_add_unknown_image_profile_lists_available_profiles():
    from ankinote.cli import stem

    save_settings(
        Settings(
            image_providers={
                "OpenAI": ProviderProfile(vendor="OpenAI", model="gpt-image-1.5")
            }
        )
    )

    result = CliRunner().invoke(
        stem.stem, ["add", "What is a derivative?", "--image-profile", "bogus"]
    )

    assert result.exit_code == 2
    assert "bogus" in result.output
    assert "OpenAI" in result.output
