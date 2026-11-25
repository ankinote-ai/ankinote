"""Notice a newer release on PyPI and say how to upgrade.

The server asks PyPI at startup and once a day after that, since a
home-server container can run for months. It only reports: upgrading
means replacing the running process (or container), which the app can't
do to itself. ``ANKINOTE_UPDATE_CHECK=0`` switches the check off.
"""

import asyncio
import importlib.metadata
import os
import sys
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

import httpx
from fastapi import APIRouter, Request
from loguru import logger
from packaging.version import InvalidVersion, Version
from pydantic import BaseModel

from ankinote import __version__
from ankinote.utils.httpcli import get_session

PACKAGE = "ankinote-ai"
PYPI_URL = f"https://pypi.org/pypi/{PACKAGE}/json"
RELEASES_URL = "https://github.com/ankinote-ai/ankinote/releases"
CHECK_ENV = "ANKINOTE_UPDATE_CHECK"
INSTALL_ENV = "ANKINOTE_INSTALL"
CHECK_INTERVAL = 24 * 60 * 60.0
_OFF = {"0", "false", "no", "off"}


class InstallMethod(StrEnum):
    """How this copy of AnkiNote was installed, which decides the upgrade."""

    DOCKER = "docker"
    UV_TOOL = "uv_tool"
    UVX = "uvx"
    PIP = "pip"
    UNKNOWN = "unknown"


NOTES_LABEL = "upgradenotes"
"""A project URL labelled "Upgrade notes" (any case or punctuation) in the
latest release's metadata replaces the link to its GitHub release page.

Every install reads the newest release's ``project_urls``, so a release can
send installs that shipped long before it to a page written for the upgrade.
"""


UPGRADE_COMMANDS: dict[InstallMethod, str] = {
    InstallMethod.DOCKER: "docker compose pull && docker compose up -d",
    InstallMethod.UV_TOOL: f"uv tool upgrade {PACKAGE}",
    InstallMethod.UVX: f"uvx --from {PACKAGE}@latest ankinote-web",
    InstallMethod.PIP: f"pip install -U {PACKAGE}",
}


def detect_install(
    *, environ: Mapping[str, str], prefix: Path, installer: str | None
) -> InstallMethod:
    """Tell the install path from what each one leaves behind.

    :param environ: The process environment; the Docker image sets
        ``ANKINOTE_INSTALL=docker``.
    :param prefix: ``sys.prefix``: uv keeps a ``uv-receipt.toml`` in a
        ``uv tool install`` environment, and runs uvx from its cache's
        ``archive-v0`` bucket.
    :param installer: The distribution's ``INSTALLER`` record (``pip``, ``uv``).
    """
    if environ.get(INSTALL_ENV, "").strip().lower() == InstallMethod.DOCKER:
        return InstallMethod.DOCKER
    if (prefix / "uv-receipt.toml").is_file():
        return InstallMethod.UV_TOOL
    if prefix.parent.name == "archive-v0":
        return InstallMethod.UVX
    if installer == "pip":
        return InstallMethod.PIP
    return InstallMethod.UNKNOWN


def current_install() -> InstallMethod:
    """The install path of the running process."""
    try:
        installer = importlib.metadata.distribution(PACKAGE).read_text("INSTALLER")
    except importlib.metadata.PackageNotFoundError:
        installer = None
    return detect_install(
        environ=os.environ,
        prefix=Path(sys.prefix),
        installer=installer.strip() if installer else None,
    )


def update_check_enabled(environ: Mapping[str, str]) -> bool:
    """Whether to ask PyPI; on unless ``ANKINOTE_UPDATE_CHECK`` says off."""
    return environ.get(CHECK_ENV, "").strip().lower() not in _OFF


def is_newer(latest: str, current: str) -> bool:
    """Whether ``latest`` is a final release after ``current``."""
    try:
        new = Version(latest)
        return not new.is_prerelease and new > Version(current)
    except InvalidVersion:
        return False


def is_major(latest: str, current: str) -> bool:
    """Whether ``latest`` raises the major version, which may break things."""
    try:
        return Version(latest).major > Version(current).major
    except InvalidVersion:
        return False


@dataclass(frozen=True)
class Release:
    """The latest release, as PyPI describes it."""

    version: str
    notes_url: str | None = None


def _label_key(label: str) -> str:
    return "".join(c for c in label.casefold() if c.isalnum())


def upgrade_notes_url(project_urls: object) -> str | None:
    """The "Upgrade notes" link among a release's project URLs, if any.

    Only ``https`` links count, since the page renders it as a link.
    """
    if not isinstance(project_urls, dict):
        return None
    for label, url in project_urls.items():
        if (
            isinstance(label, str)
            and _label_key(label) == NOTES_LABEL
            and isinstance(url, str)
            and url.startswith("https://")
        ):
            return url
    return None


async def fetch_latest_from_pypi(client: httpx.AsyncClient) -> Release:
    """The latest release PyPI lists.

    :raises httpx.HTTPError: When PyPI can't be reached or answers with an error.
    :raises ValueError: When the answer isn't the JSON API's shape.
    """
    response = await client.get(PYPI_URL, timeout=10.0)
    response.raise_for_status()
    data = response.json()
    info = data.get("info") if isinstance(data, dict) else None
    version = info.get("version") if isinstance(info, dict) else None
    if isinstance(info, dict) and isinstance(version, str):
        return Release(version, upgrade_notes_url(info.get("project_urls")))
    raise ValueError("PyPI's answer has no info.version")


async def _fetch_with_shared_session() -> Release:
    return await fetch_latest_from_pypi(get_session())


class UpgradeCommand(BaseModel):
    install: InstallMethod
    command: str


class UpdateStatus(BaseModel):
    enabled: bool
    current: str
    latest: str | None
    available: bool
    major: bool
    install: InstallMethod
    commands: list[UpgradeCommand]
    notes_url: str | None


@dataclass
class UpdateChecker:
    """Remembers the latest release PyPI reported.

    :param fetch: Returns the latest release; any error it raises is logged
        and otherwise ignored.
    """

    fetch: Callable[[], Awaitable[Release]] = _fetch_with_shared_session
    current: str = __version__
    enabled: bool = field(default_factory=lambda: update_check_enabled(os.environ))
    install: InstallMethod = field(default_factory=current_install)
    latest: Release | None = None

    async def check(self) -> None:
        """Ask once; a failure keeps the previous answer and stays silent."""
        try:
            self.latest = await self.fetch()
        except (httpx.HTTPError, ValueError) as error:
            logger.debug(f"Update check failed: {error!r}")

    async def run(self, interval: float = CHECK_INTERVAL) -> None:
        """Check now and every ``interval`` seconds until cancelled."""
        while True:
            await self.check()
            await asyncio.sleep(interval)

    def status(self) -> UpdateStatus:
        latest = self.latest.version if self.latest else None
        available = (
            self.enabled and latest is not None and is_newer(latest, self.current)
        )
        notes_url = None
        if available and self.latest:
            notes_url = self.latest.notes_url or f"{RELEASES_URL}/tag/v{latest}"
        if self.install is InstallMethod.UNKNOWN:
            installs = list(UPGRADE_COMMANDS)
        else:
            installs = [self.install]
        return UpdateStatus(
            enabled=self.enabled,
            current=self.current,
            latest=latest,
            available=available,
            major=available and latest is not None and is_major(latest, self.current),
            install=self.install,
            commands=[
                UpgradeCommand(install=i, command=UPGRADE_COMMANDS[i]) for i in installs
            ],
            notes_url=notes_url,
        )


router = APIRouter(prefix="/api")


@router.get("/update")
async def update(request: Request) -> UpdateStatus:
    checker: UpdateChecker = request.app.state.updates
    return checker.status()
