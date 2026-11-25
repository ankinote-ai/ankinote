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
   photographed math problem. For words and phrases, keep the sentence each
   one appeared in when you have it (see [Context](#context)).
2. Show the list and confirm it if you had to guess (unclear handwriting,
   ambiguous underlines), or if it's more than a few dozen cards: each card
   costs AI requests on the user's key. Otherwise go ahead.
3. Run one `batch` per card kind with `--json`, items on stdin (see
   [Input](#input)).
4. Read the result (see [Results](#results)), retry the failed items once if
   the error looks temporary, then tell the user what was saved and what
   failed and why.

CLI cards are saved without a preview. If the user wants to check or edit
each card first, suggest pasting the list into the web app's Generate page
instead.

## Running it

Use whichever works: `ankinote` (installed with `uv tool install ankinote-ai`),
`uvx --from ankinote-ai@latest ankinote`, or `uv run ankinote` inside a
checkout of the ankinote repository.

Before the first run in a session, check what is configured:

```bash
ankinote profiles list --json   # provider profiles; never prints API keys
```

If no text profile exists, ask the user to run `ankinote-web` and finish the
setup wizard (or run bare `ankinote` for a terminal menu). Don't invent API
keys or edit `settings.json` by hand.

## Commands

```
ankinote <word|phrase|sentence|stem> add <item> [--json]
ankinote <word|phrase|sentence|stem> batch [items...] [--file path|-] [--rpm N] [--json]
ankinote <word|phrase> add <item> --context "<sentence>"
ankinote <word|phrase> batch --format jsonl --file path|-
ankinote <word|phrase|sentence|stem> init        # create or update note type + deck
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
- **Rate:** `--rpm` caps items started per minute: 8 for `word`, 10 for
  `stem`, 60 otherwise. Keep the default unless the user's provider allows
  more; lower it if items fail with rate-limit errors.
- **Note types:** the web app's setup already creates them, and `add`/`batch`
  create a missing one but never change an existing one. Run `init` only when
  the user asks to update them: it rewrites an existing type's templates and
  styling, which can make AnkiWeb ask for a full sync.

## Input

Every kind takes one item per line; blank lines are skipped. `--file -`
reads stdin, which avoids quoting items with spaces or apostrophes:

```bash
ankinote word batch --json --file - <<'EOF'
serendipity
ice cream
EOF
```

Items can also be arguments (quote multi-word ones), and both can be mixed.

## Context

For `word` and `phrase`, pass the sentence the item appeared in whenever you
have it, e.g. the sentence around an underlined word in a photo. The card
then covers only the part of speech and the sense used there (one note, not
one per part of speech), uses that sentence as its first example, and its
picture shows that sense. Without context, a word card lists its most common
senses. Use the sentence as written; don't fix or shorten it.

`--format jsonl` reads one JSON object per line from `--file`; `context` is
optional per line, and arguments stay plain items:

```bash
ankinote word batch --format jsonl --json --file - <<'EOF'
{"text": "bank", "context": "We sat on the bank of the river."}
{"text": "serendipity"}
EOF
ankinote phrase add "pick up" --context "I'll pick you up at six." --json
```

Give the item in its dictionary form or as it appears; the card uses the
dictionary form either way. `sentence` and `stem` take no context.

## Results

With `--json`, stdout holds exactly one JSON document; progress and logs go
to stderr. `add` prints the same shape with one result.

```json
{"kind": "word", "total": 2, "succeeded": 1, "failed": 1,
 "results": [
   {"input": "serendipity", "ok": true, "note_ids": [1712, 1713]},
   {"input": "xyzzy", "ok": false, "error": "…"}]}
```

`note_ids` is a list: a word can make one note per part of speech. Results
of items given with context also echo `"context"`.

| Exit | Meaning | stdout |
| --- | --- | --- |
| 0 | every item saved | the JSON document |
| 1 | some items failed | the JSON document; read each `error` |
| 1 | nothing ran (Anki unreachable, collection in use, bad setting) | empty; the error is on stderr |
| 2 | usage error (no items, unknown option, missing file, a bad jsonl line) | empty; the error is on stderr |

To retry, rerun only the inputs whose `ok` is false. Never rerun the whole
batch: language cards allow duplicates, so items that already succeeded
would be saved twice. Retry once for temporary errors (rate limit, timeout,
provider overloaded); report the rest as they are. For errors that need the
user (no API key, Anki not running), see
[references/troubleshooting.md](references/troubleshooting.md).

## Built-in Anki vs AnkiConnect

The backend is whatever the user chose in the web app (or `ANKI_BACKEND`).
With built-in Anki, the collection can only be open in one process: if the
CLI reports the collection is in use, the web app (or Anki desktop) has it
open. Ask the user before stopping it. In a Docker deployment, run the CLI
inside the container (`docker exec <container> ankinote …`).
See [references/anki-sync.md](references/anki-sync.md) for sync commands.
