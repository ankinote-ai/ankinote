"""Whether the card model can read a picture, from litellm's catalog."""

import pytest

from ankinote import model_routes
from ankinote.model_presets import CUSTOM_VENDOR, PRESETS
from ankinote.model_routes import vision_support
from ankinote.settings import ProviderProfile

CATALOG = {
    "gpt-vision": {"supports_vision": True},
    "plain-chat": {"mode": "chat"},
    "deepseek/deepseek-vision": {"supports_vision": True},
    "deepseek/deepseek-plain": {"mode": "chat"},
}


@pytest.fixture(autouse=True)
def catalog(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(model_routes, "model_cost", CATALOG)


def _custom(model: str) -> ProviderProfile:
    return ProviderProfile(
        vendor=CUSTOM_VENDOR, model=model, base_url="https://llm.example/v1"
    )


def _preset(preset: str, model: str) -> ProviderProfile:
    return ProviderProfile(
        vendor=PRESETS[preset].vendor,
        model=model,
        base_url=PRESETS[preset].base_url,
        preset=preset,
    )


def test_a_catalog_model_with_vision_is_yes() -> None:
    assert vision_support(_preset("openai", "gpt-vision")) == "yes"


def test_a_preset_model_the_catalog_says_is_text_only_is_no() -> None:
    assert vision_support(_preset("openai", "plain-chat")) == "no"


def test_a_model_the_catalog_does_not_know_is_unknown() -> None:
    assert vision_support(_preset("openai", "brand-new")) == "unknown"


def test_deepseek_is_looked_up_under_its_own_name() -> None:
    # The preset reaches DeepSeek through the OpenAI-compatible route, but the
    # catalog lists its models as "deepseek/<id>".
    assert vision_support(_preset("deepseek", "deepseek-vision")) == "yes"
    assert vision_support(_preset("deepseek", "deepseek-plain")) == "no"


def test_a_custom_endpoint_is_never_ruled_out() -> None:
    # Any model can sit behind any id on an endpoint of the user's own.
    assert vision_support(_custom("gpt-vision")) == "yes"
    assert vision_support(_custom("plain-chat")) == "unknown"
    assert vision_support(_custom("my-local-llava")) == "unknown"


def test_no_preset_recommends_a_text_model_that_cannot_read_pictures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from litellm import model_cost

    monkeypatch.setattr(model_routes, "model_cost", model_cost)
    for preset in PRESETS.values():
        if "text" in preset.models:
            profile = _preset(preset.id, preset.models["text"])
            assert vision_support(profile) != "no", preset.id
