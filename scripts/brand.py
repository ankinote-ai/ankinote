"""Generate the AnkiNote mark, icons and social preview from palettes.json.

The mark has no colour of its own: lines use the palette's ``fg`` and the
answer tile its ``accent``. Fixed assets (favicon, app icons, README) use the
default palette. Run ``make brand`` after changing the mark or the default
palette; it needs ``rsvg-convert`` (librsvg) for the PNGs and Playwright's
Chromium for the social preview, which uses the bundled Source Sans 3.
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEMES = ROOT / "src" / "ankinote" / "themes"
PUBLIC = ROOT / "frontend" / "public"
DOCS = ROOT / "docs" / "brand"

# The mark on a 32-unit grid: the card's front (outlined, with a word on it)
# and its back (filled), side by side like two tiled panes.
FRONT = '<rect x="3.25" y="5.25" width="10.5" height="21.5" rx="2.75" fill="none" stroke="{fg}" stroke-width="2.5"/>'
WORD = '<rect x="6" y="10" width="5" height="2.5" rx="1.25" fill="{fg}"/>'
BACK = '<rect x="18" y="4" width="12" height="24" rx="3.5" fill="{accent}"/>'


def _palette() -> dict[str, dict[str, str]]:
    tokens = json.loads((THEMES / "palettes.json").read_text("utf-8"))
    return tokens["palettes"][tokens["default"]]


def mark(fg: str, accent: str) -> str:
    return (FRONT + WORD + BACK).format(fg=fg, accent=accent)


def _svg(body: str, size: int = 32, title: str = "AnkiNote") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
        f'role="img"><title>{title}</title>{body}</svg>\n'
    )


def adaptive_mark(palette: dict[str, dict[str, str]]) -> str:
    """Transparent mark that follows the viewer's light/dark preference."""
    light, dark = palette["light"], palette["dark"]
    style = (
        f"<style>.f{{stroke:{light['fg']}}}.w{{fill:{light['fg']}}}"
        f".b{{fill:{light['accent']}}}"
        "@media (prefers-color-scheme: dark){"
        f".f{{stroke:{dark['fg']}}}.w{{fill:{dark['fg']}}}.b{{fill:{dark['accent']}}}}}"
        "</style>"
    )
    body = (
        FRONT.replace('stroke="{fg}"', 'class="f"')
        + WORD.replace('fill="{fg}"', 'class="w"')
        + BACK.replace('fill="{accent}"', 'class="b"')
    )
    return _svg(style + body)


def icon(colors: dict[str, str], *, scale: float, radius: float) -> str:
    """The mark centred on a ``tile`` square; ``radius`` 0 for full bleed."""
    offset = 16 * (1 - scale)
    body = (
        f'<rect width="32" height="32" rx="{radius}" fill="{colors["tile"]}"/>'
        f'<g transform="translate({offset} {offset}) scale({scale})">'
        f"{mark(colors['fg'], colors['accent'])}</g>"
    )
    return _svg(body)


SOCIAL = """<!doctype html><meta charset="utf-8"><style>
@font-face{{font-family:Sans;font-weight:400;src:url("{fonts}/source-sans-3-latin-400-normal.woff2")}}
@font-face{{font-family:Sans;font-weight:600;src:url("{fonts}/source-sans-3-latin-600-normal.woff2")}}
html,body{{margin:0}}
body{{width:1280px;height:640px;box-sizing:border-box;padding:40px;background:{outer};font-family:Sans}}
.tile{{height:100%;box-sizing:border-box;border:3px solid {border};border-radius:16px;background:{tile};
display:flex;align-items:center;gap:56px;padding:0 96px}}
h1{{margin:0;font-size:104px;font-weight:600;letter-spacing:-0.02em;color:{fg};line-height:1}}
p{{margin:24px 0 0;font-size:34px;line-height:1.35;color:{muted};max-width:640px}}
</style><div class="tile"><svg width="220" height="220" viewBox="0 0 32 32">{mark}</svg>
<div><h1>AnkiNote</h1><p>Turn any word, sentence, or STEM problem into a ready-to-review Anki card.</p></div></div>
"""


def _png(svg: str, out: Path, size: int) -> None:
    subprocess.run(
        ["rsvg-convert", "-w", str(size), "-h", str(size), "-o", str(out)],
        input=svg.encode(),
        check=True,
    )


def _social(colors: dict[str, str], out: Path) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("skip social preview: run with `uv run --with playwright`")
        return
    html = SOCIAL.format(
        fonts=(THEMES / "fonts").as_uri(),
        mark=mark(colors["fg"], colors["accent"]),
        **colors,
    )
    with tempfile.TemporaryDirectory() as tmp:
        page_file = Path(tmp) / "social.html"
        page_file.write_text(html, "utf-8")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1280, "height": 640})
            page.goto(page_file.as_uri())
            page.evaluate("document.fonts.ready")
            page.screenshot(path=str(out))
            browser.close()


def main() -> None:
    if not shutil.which("rsvg-convert"):
        sys.exit("rsvg-convert not found: install librsvg (librsvg2-bin)")
    palette = _palette()
    dark, light = palette["dark"], palette["light"]
    DOCS.mkdir(parents=True, exist_ok=True)

    adaptive = adaptive_mark(palette)
    (PUBLIC / "favicon.svg").write_text(adaptive)

    (DOCS / "mark-light.svg").write_text(_svg(mark(light["fg"], light["accent"])))
    (DOCS / "mark-dark.svg").write_text(_svg(mark(dark["fg"], dark["accent"])))
    rounded = icon(dark, scale=0.62, radius=7)
    (DOCS / "icon.svg").write_text(rounded)
    _png(rounded, DOCS / "icon-1024.png", 1024)

    _png(rounded, PUBLIC / "icon-192.png", 192)
    _png(rounded, PUBLIC / "icon-512.png", 512)
    # Maskable and Apple icons are cropped by the OS: full bleed, smaller mark.
    _png(icon(dark, scale=0.5, radius=0), PUBLIC / "icon-maskable-512.png", 512)
    _png(icon(dark, scale=0.6, radius=0), PUBLIC / "apple-touch-icon.png", 180)

    manifest = {
        "name": "AnkiNote",
        "short_name": "AnkiNote",
        "start_url": "/",
        "display": "standalone",
        "background_color": dark["outer"],
        "theme_color": dark["outer"],
        "icons": [
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"},
            {
                "src": "/icon-maskable-512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "maskable",
            },
        ],
    }
    (PUBLIC / "manifest.webmanifest").write_text(json.dumps(manifest, indent=2) + "\n")

    _social(dark, DOCS / "social-preview.png")


if __name__ == "__main__":
    main()
