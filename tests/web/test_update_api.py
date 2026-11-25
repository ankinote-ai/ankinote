"""The web app's update check: PyPI's latest release and how to upgrade."""

import asyncio
import os
from collections.abc import AsyncIterator
from pathlib import Path

import httpx
import pytest

from ankinote import __version__
from ankinote.web.app import create_app
from ankinote.web.update_api import (
    UPGRADE_COMMANDS,
    InstallMethod,
    UpdateChecker,
    detect_install,
    fetch_latest_from_pypi,
    is_newer,
    update_check_enabled,
)


class FakePyPI:
    """Answers like PyPI's JSON API; counts the calls."""

    def __init__(self, latest: str = "9.0.0", *, down: bool = False) -> None:
        self.latest = latest
        self.down = down
        self.calls = 0

    async def __call__(self) -> str:
        self.calls += 1
        if self.down:
            raise httpx.ConnectError("offline")
        return self.latest


def _env_dir(tmp_path: Path, *parts: str, files: tuple[str, ...] = ()) -> Path:
    prefix = tmp_path.joinpath(*parts)
    prefix.mkdir(parents=True)
    for name in files:
        (prefix / name).write_text("")
    return prefix


# Install paths


def test_docker_is_told_by_the_image_env(tmp_path: Path) -> None:
    prefix = _env_dir(tmp_path, "usr", "local")

    method = detect_install(
        environ={"ANKINOTE_INSTALL": "docker"}, prefix=prefix, installer="pip"
    )

    assert method is InstallMethod.DOCKER


def test_uv_tool_install_has_a_receipt(tmp_path: Path) -> None:
    prefix = _env_dir(
        tmp_path, "uv", "tools", "ankinote-ai", files=("uv-receipt.toml",)
    )

    assert (
        detect_install(environ={}, prefix=prefix, installer="uv")
        is InstallMethod.UV_TOOL
    )


def test_uvx_runs_from_the_uv_cache(tmp_path: Path) -> None:
    prefix = _env_dir(tmp_path, "cache", "uv", "archive-v0", "1MVJTV47ZmOmN8y3")

    assert (
        detect_install(environ={}, prefix=prefix, installer="uv") is InstallMethod.UVX
    )


def test_pip_install_is_told_by_its_installer(tmp_path: Path) -> None:
    prefix = _env_dir(tmp_path, "venv")

    assert (
        detect_install(environ={}, prefix=prefix, installer="pip") is InstallMethod.PIP
    )


def test_anything_else_is_unknown(tmp_path: Path) -> None:
    # A source checkout under `uv run`, for one.
    prefix = _env_dir(tmp_path, "checkout", ".venv")

    assert (
        detect_install(environ={}, prefix=prefix, installer="uv")
        is InstallMethod.UNKNOWN
    )


def test_every_known_install_path_has_a_command() -> None:
    known = set(InstallMethod) - {InstallMethod.UNKNOWN}

    assert set(UPGRADE_COMMANDS) == known
    assert (
        UPGRADE_COMMANDS[InstallMethod.UVX]
        == "uvx --from ankinote-ai@latest ankinote-web"
    )


# Switch and version comparison


@pytest.mark.parametrize(
    ("value", "enabled"),
    [
        (None, True),
        ("1", True),
        ("", True),
        ("0", False),
        ("false", False),
        ("off", False),
    ],
)
def test_check_is_on_unless_switched_off(value: str | None, enabled: bool) -> None:
    environ = {} if value is None else {"ANKINOTE_UPDATE_CHECK": value}

    assert update_check_enabled(environ) is enabled


@pytest.mark.parametrize(
    ("latest", "current", "newer"),
    [
        ("1.3.0", "1.2.3", True),
        ("1.10.0", "1.9.0", True),
        ("1.2.3", "1.2.3", False),
        ("1.2.2", "1.2.3", False),
        ("1.3.0rc1", "1.2.3", False),
        ("not a version", "1.2.3", False),
    ],
)
def test_only_a_newer_final_release_counts(
    latest: str, current: str, newer: bool
) -> None:
    assert is_newer(latest, current) is newer


# PyPI


async def test_reads_the_latest_version_from_pypi() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "https://pypi.org/pypi/ankinote-ai/json"
        return httpx.Response(200, json={"info": {"version": "1.4.0"}, "releases": {}})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        assert await fetch_latest_from_pypi(client) == "1.4.0"


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(503, text="busy"),
        httpx.Response(200, text="<html>"),
        httpx.Response(200, json={"info": {}}),
        httpx.Response(200, json={"info": {"version": 7}}),
    ],
)
async def test_a_bad_pypi_answer_is_an_error(response: httpx.Response) -> None:
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda _: response)
    ) as client:
        with pytest.raises((httpx.HTTPError, ValueError)):
            await fetch_latest_from_pypi(client)


# The checker


async def test_a_failed_check_stays_silent_and_keeps_the_last_answer() -> None:
    pypi = FakePyPI("1.9.0")
    checker = UpdateChecker(
        fetch=pypi, current="1.2.3", enabled=True, install=InstallMethod.PIP
    )
    await checker.check()

    pypi.down = True
    await checker.check()

    assert checker.latest == "1.9.0"
    assert checker.status().available


async def test_checks_again_while_running() -> None:
    pypi = FakePyPI()
    checker = UpdateChecker(fetch=pypi, enabled=True, install=InstallMethod.PIP)

    task = asyncio.create_task(checker.run(interval=0.01))
    async with asyncio.timeout(2):
        while pypi.calls < 3:
            await asyncio.sleep(0.005)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


# The API


@pytest.fixture
def no_dist(tmp_path: Path) -> Path:
    return tmp_path / "no-dist"


async def _client(app) -> AsyncIterator[httpx.AsyncClient]:
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://localhost"
        ) as client,
    ):
        yield client


async def _update(app, pypi: FakePyPI) -> dict:
    async for client in _client(app):
        async with asyncio.timeout(2):
            while pypi.calls == 0:
                await asyncio.sleep(0.005)
        response = await client.get("/api/update")
        assert response.status_code == 200
        return response.json()
    raise AssertionError("no client")


async def test_startup_checks_and_reports_a_new_version(no_dist: Path) -> None:
    pypi = FakePyPI("9.0.0")
    checker = UpdateChecker(
        fetch=pypi, current="1.2.3", enabled=True, install=InstallMethod.UVX
    )

    body = await _update(create_app(no_dist, updates=checker), pypi)

    assert body == {
        "enabled": True,
        "current": "1.2.3",
        "latest": "9.0.0",
        "available": True,
        "install": "uvx",
        "commands": [
            {"install": "uvx", "command": "uvx --from ankinote-ai@latest ankinote-web"}
        ],
        "notes_url": "https://github.com/ankinote-ai/ankinote/releases/tag/v9.0.0",
    }


async def test_unknown_install_lists_every_command(no_dist: Path) -> None:
    pypi = FakePyPI("9.0.0")
    checker = UpdateChecker(
        fetch=pypi, current="1.2.3", enabled=True, install=InstallMethod.UNKNOWN
    )

    body = await _update(create_app(no_dist, updates=checker), pypi)

    assert [c["install"] for c in body["commands"]] == [
        "docker",
        "uv_tool",
        "uvx",
        "pip",
    ]


async def test_up_to_date_is_not_an_update(no_dist: Path) -> None:
    pypi = FakePyPI(__version__)
    checker = UpdateChecker(fetch=pypi, enabled=True, install=InstallMethod.PIP)

    body = await _update(create_app(no_dist, updates=checker), pypi)

    assert body["latest"] == __version__
    assert body["available"] is False
    assert body["notes_url"] is None


async def test_switched_off_never_contacts_pypi(
    no_dist: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ANKINOTE_UPDATE_CHECK", "0")
    pypi = FakePyPI()
    app = create_app(
        no_dist, updates=UpdateChecker(fetch=pypi, install=InstallMethod.PIP)
    )

    async for client in _client(app):
        await asyncio.sleep(0.05)
        body = (await client.get("/api/update")).json()

    assert pypi.calls == 0
    assert body["enabled"] is False
    assert body["available"] is False


def test_the_suite_never_checks_pypi() -> None:
    # tests/conftest.py switches the check off, so no test reaches the network.
    assert update_check_enabled(os.environ) is False
