"""Capture the README screenshots and demo GIF from a running AnkiNote web app.

Run against an isolated server (see ../SKILL.md), with the UI in English:

    uv run --with playwright python capture.py --base http://127.0.0.1:8931 --out OUT [targets...]

Targets (default: all, in this order): wizard themes word stem gif.
`wizard` saves and tests the Gemini key from GEMINI_KEY_FILE, which the
other targets need; `word`, `stem` and `gif` each spend one real generation.
Files land in OUT under their docs/img names; review them before copying.
"""

import argparse
import asyncio
import json
import os
import subprocess
import time
from pathlib import Path

from playwright.async_api import Page, async_playwright

WORD = "kaleidoscope"
STEM = (
    "A ball is launched at 20 m/s at an angle of 30° above the horizontal. "
    "Ignoring air resistance (g = 10 m/s²), find the time of flight and the horizontal range."
)
DONE_JS = "() => document.body.innerText.includes('Save to Anki') && !/Generating/.test(document.body.innerText)"
GEN_TIMEOUT = 180_000
GIF_FILTER = (
    "fps=12,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];"
    "[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle"
)


async def page(
    browser, base, path, *, width=1280, height=800, scale=2, scheme="light"
) -> Page:
    pg = await browser.new_page(
        viewport={"width": width, "height": height},
        device_scale_factor=scale,
        color_scheme=scheme,
    )
    await pg.goto(base + path)
    await pg.wait_for_timeout(1500)
    return pg


async def shot_around(pg: Page, locator, out: Path, pad=16):
    await pg.mouse.move(0, 0)
    bb = await locator.bounding_box()
    assert bb, f"nothing to capture for {out.name}"
    await pg.screenshot(
        path=str(out),
        clip={
            "x": bb["x"] - pad,
            "y": bb["y"] - pad,
            "width": bb["width"] + 2 * pad,
            "height": bb["height"] + 2 * pad,
        },
    )


async def wizard(browser, base, out):
    # 1000px tall so each step fits; step 1 is shot before the test, whose
    # results would push the provider picker out of view.
    key = Path(os.environ["GEMINI_KEY_FILE"]).read_text().strip()
    pg = await page(browser, base, "/wizard", height=1000)
    await pg.get_by_label("Gemini API key").fill(key)
    await pg.locator("body").click(position={"x": 5, "y": 700})
    await pg.mouse.move(0, 0)
    await pg.wait_for_timeout(300)
    await pg.screenshot(path=str(out / "wizard-api.png"))
    await pg.get_by_role("button", name="Test connection").click()
    await pg.wait_for_function(
        "() => [...document.querySelectorAll('button')].some(b => b.textContent.trim()==='Next' && !b.disabled)",
        timeout=60_000,
    )
    await pg.get_by_role("button", name="Next").click()
    await pg.wait_for_timeout(1500)
    await pg.mouse.move(0, 0)
    await pg.screenshot(path=str(out / "wizard-anki-account.png"))
    await pg.close()


async def themes(browser, base, out):
    for scheme in ("light", "dark"):
        pg = await page(browser, base, "/settings/appearance", scheme=scheme)
        palette = pg.locator(
            "fieldset", has=pg.locator("legend", has_text="Palette")
        ).first
        await shot_around(pg, palette, out / f"themes-{scheme}.png")
        await pg.close()


async def showcase(browser, base, out, kind):
    # Tall viewport so the whole back of the card renders without scrolling.
    pg = await page(browser, base, "/", height=3200)
    await pg.get_by_role(
        "radio", name="STEM" if kind == "stem" else "Word", exact=True
    ).first.click()
    if kind == "stem":
        await pg.wait_for_timeout(500)
        await pg.get_by_role("radio", name="Problem", exact=True).click()
    await pg.locator("textarea:visible").first.fill(STEM if kind == "stem" else WORD)
    await pg.locator("button.primary[type=submit]:visible").first.click()
    await pg.wait_for_function(DONE_JS, timeout=GEN_TIMEOUT)
    await pg.wait_for_timeout(3000)
    await pg.get_by_role("radio", name="Back", exact=True).click()
    await pg.wait_for_timeout(3000)
    await shot_around(
        pg,
        pg.locator(".preview").first,
        out / f"showcase-{'stem' if kind == 'stem' else 'word'}.png",
    )
    await pg.close()


async def gif(browser, base, out):
    frames = out / "gif-frames"
    frames.mkdir(parents=True, exist_ok=True)
    log, phase, state = [], ["idle"], {"stop": False}
    pg = await page(browser, base, "/", scale=1)
    await pg.mouse.move(1270, 790)

    async def grab():
        i = 0
        while not state["stop"]:
            t = time.monotonic()
            try:
                await pg.screenshot(path=str(frames / f"{i:05d}.png"))
            except Exception:
                await asyncio.sleep(0.05)
                continue
            log.append({"i": i, "t": t, "phase": phase[0]})
            i += 1
            await asyncio.sleep(0.04)

    task = asyncio.create_task(grab())
    await asyncio.sleep(1.2)
    phase[0] = "type"
    box = pg.locator("textarea:visible").first
    await box.click()
    await asyncio.sleep(0.4)
    await box.type(WORD, delay=120)
    await asyncio.sleep(0.8)
    await pg.keyboard.press("Control+Enter")
    phase[0] = "wait"
    await pg.wait_for_function(DONE_JS, timeout=GEN_TIMEOUT)
    phase[0] = "front"
    await asyncio.sleep(2.0)
    await pg.get_by_role("radio", name="Back", exact=True).click()
    phase[0] = "back"
    await asyncio.sleep(1.5)
    await pg.mouse.move(680, 450)
    phase[0] = "scroll"
    for _ in range(45):
        await pg.mouse.wheel(0, 40)
        await asyncio.sleep(0.07)
    await asyncio.sleep(1.5)
    for _ in range(15):
        await pg.mouse.wheel(0, -160)
        await asyncio.sleep(0.05)
    await asyncio.sleep(0.5)
    phase[0] = "end"
    await pg.get_by_role("radio", name="Front", exact=True).click()
    await asyncio.sleep(2.0)
    state["stop"] = True
    await task
    await pg.close()

    # Real timing, except the generation wait, squeezed to ~2.5 s.
    wait = [x for x in log if x["phase"] == "wait"]
    squeeze = 2.5 / max(wait[-1]["t"] - wait[0]["t"], 0.1)
    lines = []
    for a, b in zip(log, log[1:] + [None]):
        d = (b["t"] - a["t"]) if b else 1.5
        lines.append(
            f"file '{a['i']:05d}.png'\nduration {d * (squeeze if a['phase'] == 'wait' else 1):.4f}\n"
        )
    lines.append(f"file '{log[-1]['i']:05d}.png'\n")
    (frames / "concat.txt").write_text("".join(lines))
    await asyncio.to_thread(
        subprocess.run,
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(frames / "concat.txt"),
            "-vf",
            GIF_FILTER,
            "-loop",
            "0",
            str(out / "demo-hero.gif"),
        ],
        check=True,
    )
    (frames / "log.json").write_text(json.dumps(log))


TARGETS = {
    "wizard": wizard,
    "themes": themes,
    "word": lambda b, base, out: showcase(b, base, out, "word"),
    "stem": lambda b, base, out: showcase(b, base, out, "stem"),
    "gif": gif,
}


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8931")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument(
        "targets", nargs="*", help=f"any of {', '.join(TARGETS)} (default: all)"
    )
    args = ap.parse_args()
    args.targets = args.targets or list(TARGETS)
    if unknown := set(args.targets) - set(TARGETS):
        ap.error(f"unknown targets: {', '.join(sorted(unknown))}")
    args.out.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for name in args.targets:
            print(f"capturing {name}…", flush=True)
            await TARGETS[name](browser, args.base, args.out)
        await browser.close()


asyncio.run(main())
