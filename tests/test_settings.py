"""Tests for settings.json loading, saving and defaults."""

import json
import os
from pathlib import Path

import httpx
import pytest

from ankinote.settings import (
    CUSTOM_VENDOR,
    IMAGE_PROVIDERS,
    ProviderProfile,
    Settings,
    apply_env,
    default_collection_path,
    fetch_image_model_ids,
    fetch_model_ids,
    get_image_provider_models,
    image_provider_for,
    load_settings,
    save_settings,
    unique_name,
)


async def test_fetch_model_ids_openai_shape(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["auth"] = request.headers.get("authorization")
        return httpx.Response(200, json={"data": [{"id": "gpt-4o"}, {"id": "o3"}]})

    _patch_client(monkeypatch, handler)
    ids = await fetch_model_ids(
        litellm_provider="openai",
        api_base="https://api.openai.com/v1",
        api_key="sk-x",
    )
    assert ids == ["gpt-4o", "o3"]
    assert seen["url"] == "https://api.openai.com/v1/models"
    assert seen["auth"] == "Bearer sk-x"


async def test_fetch_model_ids_gemini_shape_adds_prefix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert "key" not in request.url.params
        assert request.headers["x-goog-api-key"] == "k"
        return httpx.Response(
            200,
            json={
                "models": [
                    {
                        "name": "models/gemini-2.5-pro",
                        "supportedGenerationMethods": ["generateContent"],
                    },
                    {
                        "name": "models/embedding-001",
                        "supportedGenerationMethods": ["embedContent"],
                    },
                ]
            },
        )

    _patch_client(monkeypatch, handler)
    ids = await fetch_model_ids(
        litellm_provider="gemini",
        api_base="https://generativelanguage.googleapis.com/v1beta",
        api_key="k",
        model_prefix="gemini/",
    )
    assert ids == ["gemini/gemini-2.5-pro"]


async def test_fetch_model_ids_raises_on_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_client(monkeypatch, lambda _: httpx.Response(401, json={"error": "nope"}))
    with pytest.raises(httpx.HTTPStatusError):
        await fetch_model_ids(
            litellm_provider="openai",
            api_base="https://api.openai.com/v1",
            api_key="bad",
        )


def _patch_client(monkeypatch: pytest.MonkeyPatch, handler) -> None:
    real_init = httpx.AsyncClient.__init__

    def patched_init(self: httpx.AsyncClient, *args: object, **kwargs: object) -> None:
        kwargs["transport"] = httpx.MockTransport(handler)
        real_init(self, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(httpx.AsyncClient, "__init__", patched_init)


@pytest.mark.parametrize(
    ("model", "expected"),
    [
        ("gemini/gemini-3.1-flash-lite-image", "Gemini"),
        ("gpt-image-1", "OpenAI"),
        ("dall-e-3", "OpenAI"),
        ("fal_ai/fal-ai/flux/schnell", "Fal"),
        ("fal-ai/z-image/turbo", "Fal"),
        ("no-such-provider/whatever", "Gemini"),
    ],
)
def test_image_provider_for(model: str, expected: str) -> None:
    assert image_provider_for(model) == expected


def test_get_image_provider_models_returns_non_empty_for_each_provider() -> None:
    for provider in IMAGE_PROVIDERS:
        info = IMAGE_PROVIDERS[provider]
        models = get_image_provider_models(provider)
        assert models, provider
        prefix = info["model_prefix"]
        if prefix:
            assert all(m.startswith(prefix) for m in models)
        # fal_ai's canonical model ids are themselves slash-separated paths
        # (e.g. "fal-ai/flux/schnell"), so the "no nested slash" invariant
        # that holds for the other providers doesn't apply to it.
        if info["litellm_provider"] != "fal_ai":
            assert all("/" not in m.removeprefix(prefix or "") for m in models)


def test_fal_image_models_are_discovered_from_litellm_catalog() -> None:
    """The curated ``models`` fallback is a single entry — anything beyond
    that must come from litellm's catalog, proving discovery actually runs
    for fal_ai instead of silently falling back."""
    models = get_image_provider_models("Fal")
    assert len(models) > 1
    assert "fal_ai/fal-ai/flux-pro/v1.1" in models


async def test_fetch_image_model_ids_uses_fal_platform_api_and_pagination(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        assert request.headers["Authorization"] == "Key fal-key"
        assert request.url.params["category"] == "text-to-image"
        assert request.url.params["status"] == "active"
        if request.url.params.get("cursor") == "next-page":
            return httpx.Response(
                200,
                json={
                    "models": [{"endpoint_id": "fal-ai/z-image/turbo"}],
                    "next_cursor": None,
                    "has_more": False,
                },
            )
        return httpx.Response(
            200,
            json={
                "models": [
                    {"endpoint_id": "fal-ai/flux/dev"},
                    {"endpoint_id": "fal-ai/flux/dev"},
                    {"endpoint_id": None},
                ],
                "next_cursor": "next-page",
                "has_more": True,
            },
        )

    _patch_client(monkeypatch, handler)
    ids = await fetch_image_model_ids(
        litellm_provider="fal_ai",
        api_base="https://api.fal.ai/v1",
        api_key="fal-key",
        model_prefix="fal_ai/",
    )
    assert ids == ["fal-ai/flux/dev", "fal-ai/z-image/turbo"]
    assert [str(request.url) for request in requests] == [
        "https://api.fal.ai/v1/models?category=text-to-image&status=active&limit=100",
        "https://api.fal.ai/v1/models?category=text-to-image&status=active&limit=100&cursor=next-page",
    ]


async def test_fetch_fal_models_allows_an_empty_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert "Authorization" not in request.headers
        return httpx.Response(200, json={"models": [], "next_cursor": None})

    _patch_client(monkeypatch, handler)
    ids = await fetch_image_model_ids(
        litellm_provider="fal_ai",
        api_base="https://api.fal.ai/v1",
        api_key="",
    )
    assert ids == []


def test_openai_image_models_include_gpt_image_1() -> None:
    assert "gpt-image-1" in get_image_provider_models("OpenAI")


def test_unique_name_dedupes_against_taken_set() -> None:
    assert unique_name("OpenAI", set()) == "OpenAI"
    assert unique_name("OpenAI", {"OpenAI"}) == "OpenAI (2)"
    assert unique_name("OpenAI", {"OpenAI", "OpenAI (2)"}) == "OpenAI (3)"


def test_apply_env_syncs_tts_key_into_envs(monkeypatch: pytest.MonkeyPatch) -> None:
    """The TTS service reads ``envs.GOOGLE_TTS_KEY``, bound once at import, so
    ``apply_env`` must update it and not just ``os.environ``."""
    monkeypatch.setattr("ankinote.config.envs.GOOGLE_TTS_KEY", "")
    monkeypatch.delenv("GOOGLE_TTS_KEY", raising=False)

    apply_env(Settings(api_keys={"GOOGLE_TTS_KEY": "imported-key"}))

    from ankinote.config import envs

    assert envs.GOOGLE_TTS_KEY == "imported-key"
    assert os.environ["GOOGLE_TTS_KEY"] == "imported-key"


def test_apply_env_syncs_anki_backend_into_envs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("ankinote.config.envs.ANKI_BACKEND", "connect")
    monkeypatch.setattr("ankinote.config.envs.ANKI_COLLECTION_PATH", "")
    monkeypatch.delenv("ANKI_BACKEND", raising=False)
    monkeypatch.delenv("ANKI_COLLECTION_PATH", raising=False)

    apply_env(
        Settings(
            anki_backend="collection", anki_collection_path="/data/collection.anki2"
        )
    )

    from ankinote.config import envs

    assert envs.ANKI_BACKEND == "collection"
    assert envs.ANKI_COLLECTION_PATH == "/data/collection.anki2"
    assert os.environ["ANKI_BACKEND"] == "collection"
    assert os.environ["ANKI_COLLECTION_PATH"] == "/data/collection.anki2"


def test_apply_env_leaves_anki_backend_untouched_when_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("ankinote.config.envs.ANKI_BACKEND", "collection")
    apply_env(Settings())

    from ankinote.config import envs

    assert envs.ANKI_BACKEND == "collection"


def test_default_collection_path_is_under_home_local_share() -> None:
    path = default_collection_path()
    assert path.endswith(("ankinote/collection.anki2", "ankinote\\collection.anki2"))


def test_settings_round_trip_preserves_anki_backend_fields(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    save_settings(
        Settings(anki_backend="collection", anki_collection_path="/data/x.anki2")
    )
    loaded = load_settings()
    assert loaded.anki_backend == "collection"
    assert loaded.anki_collection_path == "/data/x.anki2"


def test_load_settings_seeds_anki_backend_from_env_when_file_absent(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    monkeypatch.setattr("ankinote.config.envs.ANKI_BACKEND", "collection")
    monkeypatch.setattr(
        "ankinote.config.envs.ANKI_COLLECTION_PATH", "/env/collection.anki2"
    )
    settings = load_settings()
    assert settings.anki_backend == "collection"
    assert settings.anki_collection_path == "/env/collection.anki2"


def test_load_settings_prefers_saved_anki_backend_over_env(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    monkeypatch.setattr("ankinote.config.envs.ANKI_BACKEND", "collection")
    save_settings(Settings(anki_backend="connect", anki_collection_path=""))
    settings = load_settings()
    assert settings.anki_backend == "connect"


def test_settings_round_trip_preserves_profiles(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    original = Settings(
        text_providers={
            "OpenAI (work)": ProviderProfile(
                vendor="OpenAI",
                model="gpt-4o",
                base_url="https://api.openai.com/v1",
                api_key="sk-work",
            ),
            "OpenAI (personal)": ProviderProfile(
                vendor="OpenAI",
                model="gpt-4o-mini",
                base_url="https://api.openai.com/v1",
                api_key="sk-personal",
            ),
        },
        active_text_provider="OpenAI (work)",
        image_providers={
            "My xAI account": ProviderProfile(
                vendor=CUSTOM_VENDOR,
                model="xai/grok-2-image",
                base_url="https://api.x.ai/v1",
                api_key="sk-x",
            ),
        },
        active_image_provider="My xAI account",
    )
    save_settings(original)
    loaded = load_settings()
    assert loaded.active_text_provider == "OpenAI (work)"
    assert set(loaded.text_providers) == {"OpenAI (work)", "OpenAI (personal)"}
    assert loaded.text_providers["OpenAI (personal)"].api_key == "sk-personal"
    assert loaded.active_image_provider == "My xAI account"
    assert loaded.image_providers["My xAI account"].model == "xai/grok-2-image"


def test_save_settings_writes_only_the_current_shape(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    save_settings(Settings())
    data = json.loads((tmp_path / "ankinote" / "settings.json").read_text())
    assert "text_providers" in data
    assert "active_text_provider" in data
    assert "image_providers" in data
    assert "active_image_provider" in data
    for legacy_key in (
        "provider",
        "text_model",
        "image_provider",
        "image_model",
        "custom_base_url",
        "custom_providers",
    ):
        assert legacy_key not in data


def test_load_settings_migrates_legacy_builtin_provider(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    config_dir = tmp_path / "ankinote"
    config_dir.mkdir()
    (config_dir / "settings.json").write_text(
        json.dumps(
            {
                "provider": "OpenAI",
                "text_model": "gpt-4.1",
                "image_model": "gpt-image-1",
                "api_keys": {"OPENAI_API_KEY": "sk-legacy"},
            }
        ),
        encoding="utf-8",
    )
    settings = load_settings()
    assert settings.active_text_provider == "OpenAI"
    profile = settings.text_providers["OpenAI"]
    assert profile.vendor == "OpenAI"
    assert profile.model == "gpt-4.1"
    assert profile.api_key == "sk-legacy"
    assert settings.active_image_provider == "OpenAI"
    assert settings.image_providers["OpenAI"].model == "gpt-image-1"


def test_load_settings_migrates_legacy_custom_providers_with_name_collision(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    config_dir = tmp_path / "ankinote"
    config_dir.mkdir()
    # The active provider is itself a legacy custom sentinel, AND a
    # custom_providers entry happens to share the synthesized name "Custom".
    (config_dir / "settings.json").write_text(
        json.dumps(
            {
                "provider": "Custom (OpenAI-compatible)",
                "text_model": "qwen-max",
                "custom_base_url": "http://localhost:8000/v1",
                "api_keys": {"CUSTOM_API_KEY": "sk-active"},
                "custom_providers": {
                    "Custom": {
                        "base_url": "http://other-host/v1",
                        "model": "other-model",
                        "api_key": "sk-other",
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    settings = load_settings()
    # Two distinct profiles — no data loss despite both wanting the name
    # "Custom"; the synthesized active profile claims it first.
    assert len(settings.text_providers) == 2
    assert settings.active_text_provider == "Custom"
    active = settings.text_providers["Custom"]
    assert active.vendor == CUSTOM_VENDOR
    assert active.model == "qwen-max"
    assert active.api_key == "sk-active"
    other_name = next(n for n in settings.text_providers if n != "Custom")
    other = settings.text_providers[other_name]
    assert other.api_key == "sk-other"
    assert other.model == "other-model"


def test_load_settings_migrates_legacy_custom_provider_as_active(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    config_dir = tmp_path / "ankinote"
    config_dir.mkdir()
    (config_dir / "settings.json").write_text(
        json.dumps(
            {
                "provider": "Local vLLM",
                "custom_providers": {
                    "Local vLLM": {
                        "base_url": "http://localhost:8000/v1",
                        "model": "Qwen/Qwen2.5-7B",
                        "api_key": "k",
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    settings = load_settings()
    assert settings.active_text_provider == "Local vLLM"
    assert len(settings.text_providers) == 1
    profile = settings.text_providers["Local vLLM"]
    assert profile.vendor == CUSTOM_VENDOR
    assert profile.model == "Qwen/Qwen2.5-7B"
    assert profile.base_url == "http://localhost:8000/v1"


@pytest.mark.skipif(os.name == "nt", reason="POSIX file modes")
def test_saved_settings_are_private_to_the_user(tmp_path, monkeypatch) -> None:
    # settings.json holds API keys; other local users must not read it.
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    path = tmp_path / "ankinote" / "settings.json"
    path.parent.mkdir()
    path.write_text("{}")
    path.chmod(0o644)

    save_settings(Settings(api_keys={"OPENAI_API_KEY": "sk-secret"}))

    assert path.stat().st_mode & 0o777 == 0o600
    assert json.loads(path.read_text())["api_keys"] == {"OPENAI_API_KEY": "sk-secret"}
    assert [p.name for p in path.parent.iterdir()] == ["settings.json"]


def _write_settings(tmp_path, monkeypatch, data: object) -> Path:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    path = tmp_path / "ankinote" / "settings.json"
    path.parent.mkdir()
    path.write_text(data if isinstance(data, str) else json.dumps(data))
    return path


_CURRENT = {
    "text_providers": {
        "Work": {
            "vendor": "OpenAI",
            "model": "gpt-4o",
            "base_url": "https://api.openai.com/v1",
            "api_key": "sk-work",
        }
    },
    "active_text_provider": "Work",
    "api_keys": {"GOOGLE_TTS_KEY": "g-key"},
    "defaults": {"native_language": "German", "target_language": "Japanese"},
}


@pytest.mark.parametrize(
    "extra",
    [
        {"future_top_level": {"x": 1}},
        {"defaults": {**_CURRENT["defaults"], "future_default": True}},
        {
            "text_providers": {
                "Work": {**_CURRENT["text_providers"]["Work"], "future": "x"}
            }
        },
    ],
    ids=["top-level", "defaults", "profile"],
)
def test_an_unknown_key_keeps_the_rest_of_the_settings(
    tmp_path, monkeypatch, extra: dict
) -> None:
    # A newer release may add keys; an older one sharing the file must not
    # throw the whole file away because of them.
    _write_settings(tmp_path, monkeypatch, {**_CURRENT, **extra})

    settings = load_settings()

    assert settings.active_text_provider == "Work"
    assert settings.text_providers["Work"].api_key == "sk-work"
    assert settings.api_keys == {"GOOGLE_TTS_KEY": "g-key"}
    assert settings.defaults.native_language == "German"
    assert settings.defaults.target_language == "Japanese"


def test_a_wrong_type_falls_back_for_that_field_only(tmp_path, monkeypatch) -> None:
    _write_settings(
        tmp_path,
        monkeypatch,
        {
            **_CURRENT,
            "image_size": "big",
            "ui_language": 3,
            "api_keys": {"GOOGLE_TTS_KEY": "g-key", "BAD": 1},
            "defaults": {"native_language": "German", "generate_image": "no"},
            "text_providers": {
                "Work": {**_CURRENT["text_providers"]["Work"], "model": 4},
                "Broken": "not a profile",
            },
            "image_providers": [],
        },
    )

    settings = load_settings()

    assert settings.image_size == 512
    assert settings.ui_language == "en"
    assert settings.api_keys == {"GOOGLE_TTS_KEY": "g-key"}
    assert settings.defaults.native_language == "German"
    assert settings.defaults.generate_image is True
    assert set(settings.text_providers) == {"Work"}
    assert settings.text_providers["Work"].model == ""
    assert settings.text_providers["Work"].api_key == "sk-work"
    assert settings.image_providers  # the defaults


def test_save_keeps_keys_a_newer_release_wrote(tmp_path, monkeypatch) -> None:
    # Downgrade, save, upgrade again: the newer settings must still be there.
    path = _write_settings(
        tmp_path,
        monkeypatch,
        {
            **_CURRENT,
            "future_top_level": {"x": 1},
            "defaults": {**_CURRENT["defaults"], "future_default": True},
            "text_providers": {
                "Work": {**_CURRENT["text_providers"]["Work"], "future": "x"}
            },
        },
    )

    settings = load_settings()
    settings.defaults.native_language = "French"
    settings.text_providers["Home"] = ProviderProfile(vendor="OpenAI")
    save_settings(settings)

    data = json.loads(path.read_text())
    assert data["future_top_level"] == {"x": 1}
    assert data["defaults"]["future_default"] is True
    assert data["defaults"]["native_language"] == "French"
    assert data["text_providers"]["Work"]["future"] == "x"
    assert data["text_providers"]["Home"]["vendor"] == "OpenAI"


def test_save_drops_a_removed_profile_and_legacy_keys(tmp_path, monkeypatch) -> None:
    path = _write_settings(tmp_path, monkeypatch, {"provider": "OpenAI"})

    settings = load_settings()
    save_settings(settings)
    settings.text_providers = {"Other": ProviderProfile(vendor="OpenAI")}
    settings.active_text_provider = "Other"
    save_settings(settings)

    data = json.loads(path.read_text())
    assert "provider" not in data
    assert set(data["text_providers"]) == {"Other"}


@pytest.mark.parametrize("content", ["{not json", "[1, 2]", "null"])
def test_an_unreadable_file_is_set_aside_not_overwritten(
    tmp_path, monkeypatch, content: str
) -> None:
    path = _write_settings(tmp_path, monkeypatch, content)

    settings = load_settings()
    save_settings(settings)

    assert settings.active_text_provider == Settings().active_text_provider
    broken = list(path.parent.glob("settings.json.broken-*"))
    assert len(broken) == 1
    assert broken[0].read_text() == content
    assert json.loads(path.read_text())["text_providers"]
