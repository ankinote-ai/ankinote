# Troubleshooting

- **Collection "in use by another process" / "locked"**: built-in Anki is open
  in `ankinote-web` or Anki desktop. Ask the user before stopping it, or have
  them add the cards in the web app instead.
- **"AnkiConnect not available"**: Anki desktop isn't running or lacks the
  AnkiConnect add-on. If the user meant to use built-in Anki, they should pick
  it in the web app's Settings → Anki.
- **No provider / "API key not found"**: `ankinote profiles list` shows no
  usable text profile. Ask the user to finish the web app's setup wizard (or
  run bare `ankinote`). A provider key in the environment (`GEMINI_API_KEY`,
  `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `DEEPSEEK_API_KEY`, …) also works.
- **Unknown profile**: the error lists the configured names; pick one of those.
- **Missing note type or deck**: run `ankinote <kind> init`.
- **No audio on cards**: speech isn't configured; the card is still saved. Point
  the user to the web app's Settings → Models.
- **"Anki writes are blocked"**: built-in Anki hasn't finished its first sync,
  or AnkiWeb needs a full sync. A full sync means choosing whether to upload
  or download, and the wrong choice loses cards, so ask the user. Don't pick
  one for them.
- **AnkiWeb sync fails**: check `ankinote anki status`; if logged out, ask the
  user to sign in (web app or `ankinote anki login`).
