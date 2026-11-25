"""FastAPI app serving the JSON API and the built frontend.

The frontend lives in ``frontend/`` and builds into ``DIST_DIR``. In
development, run the Vite dev server instead; it proxies ``/api`` here.
"""

import asyncio
import contextlib
import os
import platform
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path, PurePath

from fastapi import APIRouter, FastAPI
from fastapi.responses import FileResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles

from ankinote import __version__
from ankinote.services.anki_factory import stop_anki_backend
from ankinote.utils.httpcli import close_session, init_session
from ankinote.web import (
    anki_api,
    card_theme_api,
    cards_api,
    note_types_api,
    settings_api,
    update_api,
)
from ankinote.web.guard import LocalAccessGuard, configured_host_names
from ankinote.web.update_api import UpdateChecker

DIST_DIR = Path(__file__).parent / "dist"
API_DOCS_ENV = "ANKINOTE_API_DOCS"

# Types ``mimetypes`` doesn't know on every supported Python.
_MEDIA_TYPES = {".webmanifest": "application/manifest+json"}

_NOT_BUILT = (
    "The web frontend has not been built.\n"
    "From a source checkout, run `make web-build`, or use `make web-dev` "
    "while developing.\n"
)


def is_root_file_name(dist_dir: PurePath, path: str) -> bool:
    """Whether the URL ``path`` names one file directly inside ``dist_dir``.

    Checked with ``dist_dir``'s own path rules, so on Windows a drive letter,
    UNC prefix or backslash in the URL can't point outside it.
    """
    if not path or path.startswith("."):
        return False
    candidate = dist_dir / path
    return candidate.name == path and candidate.parent == dist_dir


def _api() -> APIRouter:
    router = APIRouter(prefix="/api")

    @router.get("/health")
    async def health() -> dict[str, str]:
        return {
            "status": "ok",
            "version": __version__,
            "python": platform.python_version(),
            "platform": platform.platform(),
        }

    @router.api_route(
        "/{path:path}",
        methods=["GET", "POST", "PUT", "DELETE"],
        include_in_schema=False,
    )
    async def unknown(path: str) -> Response:
        # Keep unknown API paths out of the SPA fallback below.
        return Response(
            content='{"detail":"Not Found"}',
            status_code=404,
            media_type="application/json",
        )

    return router


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    # One shared HTTP session (AnkiConnect) and one Anki backend per process.
    init_session()
    await anki_api.start_backend()
    checker: UpdateChecker = app.state.updates
    # In the background: startup never waits for PyPI.
    check = asyncio.create_task(checker.run()) if checker.enabled else None
    try:
        yield
    finally:
        if check is not None:
            check.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await check
        await stop_anki_backend()
        await close_session()


def create_app(
    dist_dir: Path = DIST_DIR, updates: UpdateChecker | None = None
) -> FastAPI:
    # The interactive docs list every unauthenticated endpoint, so they are
    # opt-in for development.
    docs = os.environ.get(API_DOCS_ENV, "").lower() in {"1", "true", "yes"}
    app = FastAPI(
        title="ankinote",
        version=__version__,
        docs_url="/api/docs" if docs else None,
        redoc_url=None,
        openapi_url="/api/openapi.json" if docs else None,
        lifespan=_lifespan,
    )
    app.state.updates = updates or UpdateChecker()
    app.add_middleware(LocalAccessGuard, configured_hosts=configured_host_names())
    app.include_router(settings_api.router)
    app.include_router(anki_api.router)
    app.include_router(cards_api.router)
    app.include_router(note_types_api.router)
    app.include_router(card_theme_api.router)
    app.include_router(update_api.router)
    app.include_router(_api())

    index = dist_dir / "index.html"
    if (dist_dir / "assets").is_dir():
        # Vite fingerprints everything under assets/, so it may be cached.
        app.mount("/assets", StaticFiles(directory=dist_dir / "assets"))

    @app.get("/{path:path}", include_in_schema=False)
    async def spa(path: str) -> Response:
        if not index.is_file():
            return PlainTextResponse(_NOT_BUILT, status_code=503)
        # frontend/public/ (icons, manifest) lands next to index.html.
        public = dist_dir / path
        if is_root_file_name(dist_dir, path) and public.is_file():
            return FileResponse(public, media_type=_MEDIA_TYPES.get(public.suffix))
        # Client-side routes all load the same page; never cache it so a new
        # build's asset names are picked up.
        return FileResponse(index, headers={"Cache-Control": "no-cache"})

    return app
