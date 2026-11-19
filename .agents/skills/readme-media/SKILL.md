---
name: readme-media
description: Recapture the README screenshots and demo GIF in docs/img from the web UI. Use when the UI changed and the README images are out of date.
---

# README media

`docs/img` holds the README images; all six READMEs reference them by
filename, so replacing the files is enough. [`scripts/capture.py`](scripts/capture.py)
produces every one of them; this file covers what the script can't do.

| File | What it shows |
| --- | --- |
| `demo-hero.gif` | Generate: type a word, Ctrl+Enter, card front, Back, scroll, Front (960×600) |
| `showcase-word.png`, `showcase-stem.png` | The `.preview` block on the Back side, whole card |
| `themes-light.png`, `themes-dark.png` | Settings → Appearance, the Palette fieldset |
| `wizard-api.png`, `wizard-anki-account.png` | Wizard steps 1–2, 1280×1000; step 2 with Anki Desktop found, not yet connected |

## Run an isolated server

Never point the capture at the user's own config or their compose stacks.

1. A real generation needs a Gemini key with billing (for the pictures).
   Ask the user to put it in a file; none lives in `settings.json` or `.env`.
2. `make web-build`, then start the server in the background with
   `XDG_CONFIG_HOME` and `XDG_DATA_HOME` pointing at fresh directories in the
   scratchpad and a port other than 8765 (AnkiConnect's; something on this
   machine already holds it), e.g. `uv run ankinote-web --port 8931`.
   A fresh config opens the wizard in English, which the script's selectors
   assume.
3. `GEMINI_KEY_FILE=<key file> uv run --with playwright python
   .agents/skills/readme-media/scripts/capture.py --out <scratch dir>`.
   Run `wizard` first (it saves and tests the key); pass target names to
   redo only some images.
4. `anki` (step 2) needs AnkiConnect answering at the server's
   `ANKI_CONNECT_URL` (default `localhost:8765`). Unless the user's own Anki
   is there, run `uv run python .agents/skills/readme-media/scripts/fake_desktop.py
   <scratch dir>` in the background first: a throwaway collection behind the
   test suite's AnkiConnect fake. Any saved key gets past step 1, so `anki`
   alone needs no real key.

## Check before copying

Look at every output; the script can't judge content. Redo a target if a
generated card is weak (no picture, odd example) or a layout is cut off.
If a selector times out, the UI changed: read the current labels in
`frontend/src/lib/locales/en.json` (the STEM chip that was "Example" is now
"Problem") and update the script with the fix. When the UI moved enough
that a shot frames the wrong thing, change the script, not just the image.

Copy the files into `docs/img` under the same names. If the content changed
meaningfully, update the alt text in all six READMEs. `README.md` loads the
images from `raw.githubusercontent.com/.../main`, so they appear only after a
push.

## Clean up

Stop the server (and `fake_desktop.py`) by its background task or PID: `pkill -f ankinote-web`
also matches your own shell command, which kills it before the next step
runs, and the user's containers run `ankinote-web` too. Then delete the key
file and the scratch `settings.json` (it now holds the key).
