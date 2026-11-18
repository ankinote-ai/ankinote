"""Keep web pages the user visits from driving their AnkiNote.

AnkiNote has no login, so without this any page open in the user's browser
could reach it on localhost:

- DNS rebinding: the attacker's domain re-resolves to 127.0.0.1, which makes
  the page same-origin with AnkiNote. The Host header still names that domain,
  so only IP literals, ``localhost`` and the names in ``ANKINOTE_ALLOWED_HOSTS``
  are served.
- Cross-site writes: a page can POST without a CORS preflight. Browsers send
  ``Origin`` with every such request, so a write from another origin is
  refused. Clients that send no ``Origin`` (the CLI, curl) pass. A reverse
  proxy may forward to the backend's IP, so an ``Origin`` naming one of the
  ``ANKINOTE_ALLOWED_HOSTS`` names also passes: the user vouched for it.
"""

import ipaddress
import os
from urllib.parse import urlsplit

from starlette.datastructures import Headers
from starlette.responses import PlainTextResponse
from starlette.types import ASGIApp, Receive, Scope, Send

ALLOWED_HOSTS_ENV = "ANKINOTE_ALLOWED_HOSTS"

_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


def _host_name(host: str) -> str:
    """``name[:port]`` → the lowercased name, without IPv6 brackets."""
    host = host.strip().lower()
    if host.startswith("["):
        return host[1:].partition("]")[0]
    return host.partition(":")[0]


def _is_ip(name: str) -> bool:
    try:
        ipaddress.ip_address(name)
    except ValueError:
        return False
    return True


def configured_host_names() -> frozenset[str]:
    """The comma-separated names in ``ANKINOTE_ALLOWED_HOSTS``."""
    extra = os.environ.get(ALLOWED_HOSTS_ENV, "").split(",")
    return frozenset(_host_name(h) for h in extra if h.strip())


class LocalAccessGuard:
    """ASGI middleware enforcing the Host and Origin rules above."""

    def __init__(self, app: ASGIApp, configured_hosts: frozenset[str]) -> None:
        self.app = app
        self.configured_hosts = configured_hosts
        self.allowed_hosts = configured_hosts | {"localhost"}

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = Headers(scope=scope)
        host = headers.get("host", "")
        name = _host_name(host)
        if host and not (name in self.allowed_hosts or _is_ip(name)):
            response = PlainTextResponse(
                f"AnkiNote does not answer to the host name {name!r}. If you "
                f"reach it by this name, add the name to {ALLOWED_HOSTS_ENV}.\n",
                status_code=400,
            )
            await response(scope, receive, send)
            return
        origin = headers.get("origin")
        if (
            scope["method"] not in _SAFE_METHODS
            and origin is not None
            and not self._trusted_origin(origin, host)
        ):
            response = PlainTextResponse(
                "Cross-origin request refused.\n", status_code=403
            )
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)

    def _trusted_origin(self, origin: str, host: str) -> bool:
        parts = urlsplit(origin)
        if parts.netloc.lower() == host.lower():
            return True
        return parts.hostname is not None and parts.hostname in self.configured_hosts
