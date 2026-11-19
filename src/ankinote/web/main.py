"""``ankinote-web``: run the 1.0 web app."""

import ipaddress

import click
import uvicorn
from loguru import logger

from ankinote.web.app import create_app


def exposure_warning(host: str) -> str | None:
    """What to say when ``host`` lets other machines in; None on loopback.

    AnkiNote is single-user and has no login, so listening beyond this
    machine is only safe on a private network or behind a proxy that asks
    for one. In Docker the container listens on all interfaces and the
    published port decides who gets in, which the wording covers.
    """
    if host == "localhost":
        return None
    try:
        if ipaddress.ip_address(host).is_loopback:
            return None
    except ValueError:
        pass
    return (
        f"Listening on {host}: AnkiNote has no login, so anyone who can reach "
        "this port can use your AI keys and add cards to your Anki. Keep it on "
        "a private network (home LAN, Tailscale) or behind a reverse proxy "
        "that asks for a login; see deploy/README.md."
    )


@click.command()
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8000, show_default=True, type=int)
def main(host: str, port: int) -> None:
    """Serve the ankinote web app."""
    if warning := exposure_warning(host):
        logger.warning(warning)
    uvicorn.run(create_app(), host=host, port=port)
