import platform
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath

import pytest
from fastapi.testclient import TestClient

from ankinote import __version__
from ankinote.web.app import create_app, is_root_file_name


@pytest.fixture
def dist(tmp_path: Path) -> Path:
    (tmp_path / "assets").mkdir()
    (tmp_path / "index.html").write_text("<!doctype html><div id=app></div>")
    (tmp_path / "assets" / "app.js").write_text("console.log(1)")
    return tmp_path


def test_health_reports_version(dist: Path) -> None:
    client = TestClient(create_app(dist), base_url="http://localhost")

    response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == __version__
    assert body["python"] == platform.python_version()
    assert body["platform"] == platform.platform()


def test_unknown_api_path_is_json_404_not_the_spa(dist: Path) -> None:
    client = TestClient(create_app(dist), base_url="http://localhost")

    response = client.get("/api/nope")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")


@pytest.mark.parametrize("path", ["/", "/wizard", "/generate/word"])
def test_client_routes_serve_index(dist: Path, path: str) -> None:
    client = TestClient(create_app(dist), base_url="http://localhost")

    response = client.get(path)

    assert response.status_code == 200
    assert "<div id=app>" in response.text
    assert response.headers["cache-control"] == "no-cache"


def test_built_assets_are_served(dist: Path) -> None:
    client = TestClient(create_app(dist), base_url="http://localhost")

    response = client.get("/assets/app.js")

    assert response.status_code == 200
    assert response.text == "console.log(1)"


@pytest.mark.parametrize(
    ("name", "content_type"),
    [
        ("favicon.svg", "image/svg+xml"),
        ("manifest.webmanifest", "application/manifest+json"),
    ],
)
def test_public_files_at_the_root_are_served(
    dist: Path, name: str, content_type: str
) -> None:
    # Vite copies frontend/public/ to the top of dist/, next to index.html.
    (dist / name).write_text("x")
    client = TestClient(create_app(dist), base_url="http://localhost")

    response = client.get(f"/{name}")

    assert response.status_code == 200
    assert response.text == "x"
    assert response.headers["content-type"].startswith(content_type)


@pytest.mark.parametrize("path", ["/index.html/", "/assets", "/../pyproject.toml"])
def test_only_plain_files_at_the_root_are_public(dist: Path, path: str) -> None:
    client = TestClient(create_app(dist), base_url="http://localhost")

    response = client.get(path)

    assert "<div id=app>" in response.text


def test_missing_asset_is_404_not_index(dist: Path) -> None:
    client = TestClient(create_app(dist), base_url="http://localhost")

    assert client.get("/assets/missing.js").status_code == 404


def test_api_docs_are_off_by_default(dist: Path) -> None:
    client = TestClient(create_app(dist), base_url="http://localhost")

    assert client.get("/api/docs").status_code == 404
    assert "openapi" not in client.get("/openapi.json").text
    assert client.get("/api/openapi.json").status_code == 404


def test_api_docs_can_be_turned_on(dist: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANKINOTE_API_DOCS", "1")
    client = TestClient(create_app(dist), base_url="http://localhost")

    assert client.get("/api/docs").status_code == 200
    assert "/api/openapi.json" in client.get("/api/docs").text
    assert client.get("/api/openapi.json").json()["info"]["title"] == "ankinote"


def test_missing_build_explains_how_to_build(tmp_path: Path) -> None:
    client = TestClient(create_app(tmp_path / "absent"), base_url="http://localhost")

    response = client.get("/")

    assert response.status_code == 503
    assert "make web-build" in response.text


@pytest.mark.parametrize(
    "path",
    [
        "C:\\Users\\me\\AppData\\Roaming\\ankinote\\settings.json",
        "C:settings.json",
        "assets\\..\\..\\settings.json",
        "\\\\server\\share\\settings.json",
    ],
)
def test_root_file_check_rejects_windows_escapes(path: str) -> None:
    # A Windows path in the URL must not reach files outside dist/.
    assert not is_root_file_name(PureWindowsPath("C:/app/dist"), path)


@pytest.mark.parametrize(
    "dist_dir", [PurePosixPath("/app/dist"), PureWindowsPath("C:/app/dist")]
)
def test_root_file_check_accepts_plain_names(dist_dir: PurePath) -> None:
    assert is_root_file_name(dist_dir, "favicon.svg")


@pytest.mark.parametrize(
    "host", ["localhost:8080", "127.0.0.1:8080", "[::1]:8000", "100.64.0.5:8080"]
)
def test_loopback_and_ip_hosts_are_allowed(dist: Path, host: str) -> None:
    client = TestClient(create_app(dist), base_url="http://localhost")

    response = client.get("/api/health", headers={"Host": host})

    assert response.status_code == 200


def test_unknown_host_names_are_refused(dist: Path) -> None:
    # DNS rebinding: the attacker's domain now resolves to 127.0.0.1.
    client = TestClient(create_app(dist), base_url="http://localhost")

    response = client.get("/api/health", headers={"Host": "evil.example:8080"})

    assert response.status_code == 400
    assert "ANKINOTE_ALLOWED_HOSTS" in response.text


def test_allowed_hosts_setting_adds_names(
    dist: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ANKINOTE_ALLOWED_HOSTS", "ankinote.example.com, Box.local")
    client = TestClient(create_app(dist), base_url="http://localhost")

    for host in ("ankinote.example.com", "box.local:8080"):
        assert client.get("/api/health", headers={"Host": host}).status_code == 200


@pytest.mark.parametrize(
    "origin", ["https://evil.example", "http://localhost:3000", "null"]
)
def test_cross_origin_writes_are_refused(dist: Path, origin: str) -> None:
    # A page elsewhere can send a "simple" POST without a CORS preflight.
    client = TestClient(create_app(dist), base_url="http://localhost:8080")

    response = client.post(
        "/api/anki/full-sync",
        content=b'{"direction":"upload"}',
        headers={"Origin": origin},
    )

    assert response.status_code == 403


def test_same_origin_and_non_browser_writes_pass(dist: Path) -> None:
    client = TestClient(create_app(dist), base_url="http://localhost:8080")

    same_origin = client.post("/api/nope", headers={"Origin": "http://localhost:8080"})
    no_origin = client.post("/api/nope")

    assert same_origin.status_code == 404
    assert no_origin.status_code == 404


def test_cross_origin_reads_are_not_blocked(dist: Path) -> None:
    # Reads are guarded by the browser's same-origin policy, not by us.
    client = TestClient(create_app(dist), base_url="http://localhost:8080")

    response = client.get("/api/health", headers={"Origin": "https://evil.example"})

    assert response.status_code == 200
