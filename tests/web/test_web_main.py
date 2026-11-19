"""``ankinote-web``: what it says at startup about who can reach it."""

import pytest
from click.testing import CliRunner

from ankinote.web import main as web_main


@pytest.mark.parametrize("host", ["127.0.0.1", "localhost", "::1", "127.0.0.2"])
def test_loopback_is_quiet(host: str) -> None:
    assert web_main.exposure_warning(host) is None


@pytest.mark.parametrize("host", ["0.0.0.0", "::", "192.168.1.20", "nas.local"])
def test_other_interfaces_warn_there_is_no_login(host: str) -> None:
    warning = web_main.exposure_warning(host)
    assert warning is not None
    assert "no login" in warning
    assert "deploy/README.md" in warning


def test_warning_is_logged_before_serving(monkeypatch: pytest.MonkeyPatch) -> None:
    logged: list[str] = []
    monkeypatch.setattr(web_main.logger, "warning", logged.append)
    monkeypatch.setattr(web_main.uvicorn, "run", lambda *args, **kwargs: None)
    result = CliRunner().invoke(web_main.main, ["--host", "0.0.0.0"])
    assert result.exit_code == 0, result.output
    assert logged == [web_main.exposure_warning("0.0.0.0")]
