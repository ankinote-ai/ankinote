"""What the thinking setting puts on the wire, through LiteLLM's real request mapping.

The unit tests in ``test_ai.py`` mock ``acompletion`` and only see the
arguments we hand LiteLLM. LiteLLM then maps (or silently drops) them per
model, and that mapping is where thinking control broke for the recommended
Gemini and OpenAI models. These tests run the real ``acompletion`` against a
local server and assert on the request body a provider would receive.
"""

from __future__ import annotations

import json
import threading
from collections.abc import Iterator
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import pytest

from ankinote.model_presets import PRESETS
from ankinote.services.ai import DISABLE_REASONING, LiteLLMTextService

_OPENAI_REPLY = {
    "id": "chatcmpl-test",
    "object": "chat.completion",
    "created": 0,
    "model": "test",
    "choices": [
        {
            "index": 0,
            "message": {"role": "assistant", "content": "ok"},
            "finish_reason": "stop",
        }
    ],
    "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
}
_GEMINI_REPLY = {
    "candidates": [
        {
            "content": {"role": "model", "parts": [{"text": "ok"}]},
            "finishReason": "STOP",
            "index": 0,
        }
    ],
    "usageMetadata": {
        "promptTokenCount": 1,
        "candidatesTokenCount": 1,
        "totalTokenCount": 2,
    },
}
_ANTHROPIC_REPLY = {
    "id": "msg_test",
    "type": "message",
    "role": "assistant",
    "model": "test",
    "content": [{"type": "text", "text": "ok"}],
    "stop_reason": "end_turn",
    "usage": {"input_tokens": 1, "output_tokens": 1},
}


@dataclass
class _Recorder:
    url: str
    bodies: list[dict[str, Any]] = field(default_factory=list)

    @property
    def body(self) -> dict[str, Any]:
        assert len(self.bodies) == 1, self.bodies
        return self.bodies[0]


@pytest.fixture
def provider_server() -> Iterator[_Recorder]:
    """A local stand-in for the OpenAI, Gemini and Anthropic chat endpoints."""
    recorder = _Recorder(url="")

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            length = int(self.headers.get("Content-Length", "0"))
            recorder.bodies.append(json.loads(self.rfile.read(length)))
            if "generateContent" in self.path:
                reply = _GEMINI_REPLY
            elif self.path.endswith("/messages"):
                reply = _ANTHROPIC_REPLY
            else:
                reply = _OPENAI_REPLY
            payload = json.dumps(reply).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, format: str, *args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    recorder.url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        yield recorder
    finally:
        server.shutdown()
        server.server_close()


async def _send(
    server: _Recorder,
    model: str,
    reasoning_effort: str | None,
    *,
    force_openai_route: bool = False,
) -> dict[str, Any]:
    service = LiteLLMTextService(
        api_base=server.url,
        api_key="test-key",
        force_openai_route=force_openai_route,
    )
    await service.generate_text(
        model=model,
        messages=[{"role": "user", "content": "hello"}],
        temperature=0.3,
        reasoning_effort=reasoning_effort,
    )
    return server.body


GEMINI_TEXT = PRESETS["gemini"].models["text"]
OPENAI_TEXT = PRESETS["openai"].models["text"]
ANTHROPIC_TEXT = PRESETS["anthropic"].models["text"]
DEEPSEEK_TEXT = PRESETS["deepseek"].models["text"]


@pytest.mark.asyncio
async def test_openai_preset_turns_thinking_off(provider_server: _Recorder) -> None:
    body = await _send(provider_server, OPENAI_TEXT, DISABLE_REASONING)

    assert body["reasoning_effort"] == "none"
    # Sampling temperature is accepted while reasoning is off.
    assert body["temperature"] == 0.3


@pytest.mark.asyncio
async def test_openai_preset_forwards_a_thinking_level(
    provider_server: _Recorder,
) -> None:
    body = await _send(provider_server, OPENAI_TEXT, "high")

    assert body["reasoning_effort"] == "high"
    # OpenAI rejects a non-default temperature while reasoning is on.
    assert "temperature" not in body


@pytest.mark.asyncio
async def test_gemini_preset_turns_thinking_down_to_its_floor(
    provider_server: _Recorder,
) -> None:
    body = await _send(provider_server, GEMINI_TEXT, DISABLE_REASONING)

    # Gemini 3 models cannot switch thinking off; "minimal" is the lowest level.
    thinking = body["generationConfig"]["thinkingConfig"]
    assert thinking["thinkingLevel"] == "minimal"
    assert thinking["includeThoughts"] is False


@pytest.mark.asyncio
async def test_gemini_preset_forwards_a_thinking_level(
    provider_server: _Recorder,
) -> None:
    body = await _send(provider_server, GEMINI_TEXT, "medium")

    assert body["generationConfig"]["thinkingConfig"]["thinkingLevel"] == "medium"


@pytest.mark.asyncio
async def test_gemini_3_keeps_its_default_temperature(
    provider_server: _Recorder,
) -> None:
    body = await _send(provider_server, GEMINI_TEXT, DISABLE_REASONING)

    # Google advises leaving Gemini 3 at its default temperature of 1.0;
    # lower values can make it loop or degrade.
    assert body["generationConfig"].get("temperature", 1.0) == 1.0


@pytest.mark.asyncio
async def test_older_gemini_keeps_the_requested_temperature(
    provider_server: _Recorder,
) -> None:
    body = await _send(provider_server, "gemini/gemini-2.5-flash", DISABLE_REASONING)

    assert body["generationConfig"]["temperature"] == 0.3


@pytest.mark.asyncio
async def test_anthropic_preset_turns_thinking_off(
    provider_server: _Recorder,
) -> None:
    body = await _send(provider_server, ANTHROPIC_TEXT, DISABLE_REASONING)

    assert "thinking" not in body
    assert "output_config" not in body


@pytest.mark.asyncio
async def test_deepseek_preset_turns_thinking_off(provider_server: _Recorder) -> None:
    body = await _send(
        provider_server, DEEPSEEK_TEXT, DISABLE_REASONING, force_openai_route=True
    )

    assert body["thinking"] == {"type": "disabled"}
    assert "reasoning_effort" not in body


@pytest.mark.asyncio
async def test_custom_endpoint_gets_no_thinking_field_when_off(
    provider_server: _Recorder,
) -> None:
    # A local or third-party OpenAI-compatible server may reject an unknown
    # reasoning_effort value, so "off" leaves it at the server's default.
    body = await _send(
        provider_server, "Qwen/Qwen3-8B", DISABLE_REASONING, force_openai_route=True
    )

    assert "reasoning_effort" not in body
    assert "thinking" not in body
