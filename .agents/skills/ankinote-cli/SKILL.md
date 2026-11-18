---
name: ankinote-cli
description: Make Anki cards with the ankinote CLI from words, phrases, sentences, or STEM problems the user gives you (typed, in a file, or picked out of a photo or text they're reading). Use when the user asks to add something to Anki or turn material into flashcards.
---

# AnkiNote CLI

`ankinote` turns words, phrases, sentences, and STEM questions into finished
Anki cards (AI-written fields, optional picture and audio) and saves them to
the user's Anki collection. It reads the same settings as the AnkiNote web
app, so once the user has finished the web app's setup wizard, the CLI needs
no configuration.

## Typical workflow

1. Work out the items from what the user gave you: underlined words in a
   photo of a page, a vocabulary list, sentences from an article, a
   photographed math problem.
2. Show the list and confirm it if you had to guess (unclear handwriting,
   ambiguous underlines). Otherwise go ahead.
3. Run one `batch` (or `add`) command per card kind, e.g.
   `ankinote word batch serendipity ephemeral eloquent`.
4. Report what was saved and any items that failed.

CLI cards are saved without a preview. If the user wants to check or edit
each card first, suggest pasting the list into the web app's Generate page
instead.

## Running it

Use whichever works: `ankinote` (installed with `uv tool install ankinote-ai`),
`uvx --from ankinote-ai ankinote`, or `uv run ankinote` inside a checkout of
this repository.

Before the first run in a session, check what is configured:

```bash
ankinote profiles list --json   # provider profiles; never prints API keys
```

If no text profile exists, ask the user to run `ankinote-web` and finish the
setup wizard (or run bare `ankinote` for a terminal menu). Don't invent API
keys or edit `settings.json` by hand.

## Commands

```
ankinote <word|phrase|sentence|stem> add <item>
ankinote <word|phrase|sentence|stem> batch [items...] [--file path] [--rpm N]
ankinote <word|phrase|sentence|stem> init        # create note type + deck if missing
ankinote anki <login|logout|status|sync>         # built-in Anki only
ankinote profiles list [--json]
```

| Kind | Input | Notes |
| --- | --- | --- |
| `word` | one word | picture + audio when configured |
| `phrase` | a phrase or short sentence | |
| `sentence` | a sentence **in the target language** | the card front shows its translation; tests producing the sentence |
| `stem` | a question, concept, or problem | `--image <file>` solves from a photo (needs a vision-capable model); see [references/stem.md](references/stem.md) |

Run `ankinote <kind> <command> --help` for the full, current option list.

Decisions that matter:

- **Languages:** `word`/`phrase`/`sentence` use the native and target
  languages saved in the web app's settings. Pass `--native`/`--target` only
  when the user wants cards for a different pair this time.
- **Provider:** prefer `--profile <name>` (and `--image-profile` for
  `word`/`stem`) with a name from `profiles list`. `--llm` / `--image-model`
  override just the model.
- **Rate:** `--rpm` defaults to 8 for `word`, 10 for `stem`, 60 otherwise.
  Keep the default unless the user's provider allows more.
- **Note types:** the web app's setup already creates them. Run `init` only
  if a command reports a missing note type or deck.

## Built-in Anki vs AnkiConnect

The backend is whatever the user chose in the web app (or `ANKI_BACKEND`).
With built-in Anki, the collection can only be open in one process: if the
CLI reports the collection is in use, the web app (or Anki desktop) has it
open. Ask the user before stopping it. In a Docker deployment, run the CLI
inside the container (`docker exec <container> ankinote …`).
See [references/anki-sync.md](references/anki-sync.md) for sync commands and
[references/troubleshooting.md](references/troubleshooting.md) for errors.
