# CLI as an Agent's Tool: Plan

Work breakdown for the roadmap's
[CLI as an agent's tool](../roadmap.md#the-cli-as-an-agents-tool), scoped
2026-11-25. Each step ships on its own and fits one session; do them in
order. Mark a step done here (with its commit) when it lands.

Goal: an agent can hand `ankinote` a list of items, read back exactly which
cards were saved and which failed, and retry or report without parsing prose.

## Where things stand

The four card commands (`src/ankinote/cli/{word,phrase,sentence,stem}.py`)
each copy the same options and batch loop, and have drifted apart:

- `batch` exits 0 even when items fail; `add` fails with a Python traceback;
  `stem batch` with no input prints an error and exits 0.
- `word batch --file` splits on whitespace ("ice cream" becomes two words);
  the others read one item per line, as the README says for words too.
- `stem batch` runs items one at a time, prints with rich instead of click,
  has no `-f` for `--file`, and its summary leaves out why items failed.
- `word`, `phrase`, `sentence` `add` don't print the saved note id; `stem` does.
- Stale text: docstring examples say `anki …` instead of `ankinote …`;
  `sentence --help` still says "(V2 - production cards)".
- Default `--rpm` differs per kind (word 8, phrase/sentence 60, stem 10). This
  is deliberate in spirit (a word card makes several requests: text, image,
  audio), but nowhere says so.

Tests: `tests/cli/`, with the `capture_options` fixture in
`tests/cli/conftest.py` faking the collection; extend that fake to return
note ids or raise per item.

## Decisions

Proposed 2026-11-25; confirm with the user at the start of the step that
needs them.

- **One item per line everywhere, including `word batch --file`**
  (confirmed 2026-11-25, done in step 1). Breaks word files written as
  space-separated words on one line; the README and CLI guide already
  describe one word per line.
- **JSON output shape** (step 3): one JSON document on stdout, logs stay on
  stderr:

  ```json
  {"kind": "word", "total": 3, "succeeded": 2, "failed": 1,
   "results": [
     {"input": "apple", "ok": true, "note_ids": [1712, 1713]},
     {"input": "xyzzy", "ok": false, "error": "…"}]}
  ```

  `note_ids` is always a list (a word can make one note per part of speech).
  `add` prints the same shape with one result.
- **Exit codes**: 0 all saved, 1 any item failed, 2 usage error (click's).
- **Context input format** (step 5): `add --context "…"`; for `batch`,
  `--format jsonl` with lines `{"text": "…", "context": "…"}`, default
  `lines`. JSONL is easy for an agent to write and needs no escaping rules;
  tabs are awkward to type in a shell. Confirmed 2026-11-25.
- **What context does to a card** (step 5, confirmed 2026-11-25): `word` and
  `phrase` take it; `sentence` (already a sentence) and `stem` (has
  `--image`) don't. With context the card covers only the part of speech and
  the one sense used there (word: one record, one sense; phrase: no
  supporting meanings), the context sentence is the first example (only the
  sentence holding the item if the context is longer, wording unchanged),
  and the picture shows that sense. Without context, what is sent to the
  model is byte-for-byte what it is today: the rules live in a separate
  prompt addendum, and the note types don't change.
- **Web input** (step 6, confirmed 2026-11-25): no new control. A line on the
  Generate page with `[ ]` around the item is the context sentence: `We sat
  on the [bank] of the river.` Several marked parts are one item, joined in
  order with ` … ` (`I'll [pick] you [up] at six.` → `pick … up`), for words
  too, so a German separable verb works (`Ich [rufe] dich [an].` →
  `rufe … an`, card `anrufen`); the model gives the dictionary form. Changed
  from "word takes exactly one" at the start of step 6. Lines without
  brackets behave as before; sentence and STEM ignore brackets.

## Step 1: Shared batch runner; word, phrase, sentence on it (M), done

Done 2026-11-25. `cli/batch.py` (`read_items`, `add_one`, `add_many`, `run`,
`batch_options`) and `model_options` in `cli/factory.py`; tests in
`tests/cli/test_batch.py`. Each kind module keeps resolving
`anki_client_scope` and its `build_*_collection` from its own globals (via
`_scope`), which the `capture_options` fixture relies on. `--rpm 0` now means
no limit. Progress and summary still print to stdout; step 3 moves them.

1. Tests first, red against today's code: `word batch` exits non-zero when an
   item fails; `word batch --file` keeps "ice cream" as one item; `add`
   failing exits 1 with a one-line error, not a traceback.
2. New module (e.g. `cli/batch.py`):
   - read items from arguments plus `--file` (one per line, blank lines
     skipped), returning item objects (text, later context) rather than
     bare strings so step 5 only adds a parser;
   - run them with the shared concurrency cap and `--rpm` limiter;
   - collect one result per item (note ids or error message);
   - print the human summary and set the exit code.
3. Move the shared options (`--llm`, `--profile`, `--thinking`, image
   options) into one place; per-kind differences stay as parameters (default
   `--rpm`, `--thinking` default text, whether image options apply).
4. Port `word`, `phrase`, `sentence` `add`/`batch` onto it. `add` prints the
   note id(s). Fix the stale docstrings.
5. Explain in `--rpm`'s help that it limits items started per minute, and why
   word's default is lower.

Done when: the new tests pass, the existing `tests/cli/` suite passes, and
`ankinote word|phrase|sentence batch --help` reads consistently.

## Step 2: STEM on the shared runner (S), done

Done 2026-11-25. `stem` is in `KINDS` for every shared test;
`tests/cli/test_stem_cli.py` covers `--image` and the help. `stem add
--image` wraps the collection in `_WithReferenceImage` inside `stem._scope`,
so `batch.py` is unchanged. `stem batch` now runs up to `MAX_CONCURRENCY`
topics at once (was one at a time); `--rpm` still defaults to 10.

1. Tests first: `stem batch` with no input exits 2; a failed item exits 1
   and its reason shows in the summary.
2. Port `stem add`/`batch`: concurrency and limiter from the runner (keep a
   low default, STEM cards think at `high` and draw an image), click output
   instead of rich, `-f` for `--file`. `stem add --image` and `--type` stay.
   Replace stem's own `collection_options` with `model_options(images=True)`
   plus `--type`; `stem add --image` needs `add_one` to pass the reference
   image through (or its own call into `run`).
3. Add `"stem"` to `KINDS` in `tests/cli/test_batch.py` where the topics fit.

Done when: STEM behaves like the other kinds apart from its own options.

## Step 3: `--json` and stdin (S), done

Done 2026-11-25. `json_option` in `cli/batch.py`; `--file` is a
`click.File`, so `-` reads stdin and a missing file is a usage error. stdout
carries only the result: the "Processing …" line goes to stderr, and
generation runs under `redirect_stdout(sys.stderr)` because litellm prints
to stdout on some errors. When Anki can't be reached the run fails before
any item: exit 1, the error on stderr, stdout empty (no JSON document); the
skill in step 4 should say so.

1. Tests first: `--json` output parses and matches the shape above for all
   succeeded, some failed, and `add`; `--file -` reads stdin; nothing but
   the JSON document goes to stdout under `--json` (progress lines and
   loguru output stay on stderr).
2. Add `--json` to every `add` and `batch`; accept `-` for `--file`.

Done when: an agent can run
`printf 'apple\nice cream\n' | ankinote word batch --file - --json` and get
one parseable result per line.

## Step 4: Docs and the agent skill (S), done

Done 2026-11-25. Decided with the user: the skill ships in the wheel at
`src/ankinote/skills/ankinote-cli/` (`.agents/skills/ankinote-cli` is a
symlink to it), and `ankinote skill install [--dir …]` copies it into
`~/.claude/skills` and `~/.agents/skills` (`cli/skill.py`, tests in
`tests/cli/test_skill_cli.py`). The skill tells agents to retry only failed
inputs, since language cards allow duplicates.

- `SKILL.md`: prefer `--json`, read `results`,
  retry or report failed items, exit codes, stdin.
- `docs/cli-usage.md` and the README's terminal section: one item per line
  for every kind, `--json`, `--file -`.
- Roadmap: tick items 2–4 of "The CLI as an agent's tool".
- Where the skill lives (decide with the user): a skill in this repo only
  reaches agents working in this repo, but the goal is that any agent on the
  machine (other projects, `uvx` installs) can drive `ankinote`. Options:
  install it user-wide (`~/.claude/skills/`, `~/.agents/skills/`) by symlink
  or copy, document that in the README, or ship it in the wheel with a
  command that installs it (e.g. `ankinote skill install`).

## Step 5: Context with each item (M), done

Done 2026-11-25. The rules are `collections/{word,phrase}/prompts/context.md`,
added by `collections/common.py:with_context`; `context` is a keyword-only
argument from the generators up to `generate_and_add_note`. CLI: `Item.context`,
`context_option`, `batch_options(context=True)` adds `--format`. Tests in
`tests/collections/test_context_prompts.py` and `tests/cli/test_context_cli.py`.
Checked live with `gemini-3.5-flash-lite` ("bank" river vs. aircraft,
"ran" → run, "make out", "pick up"): one record, one sense, the sentence
verbatim as the first example. Two prompt fixes came out of it: the card must
stay on the queried item (an unrelated context once produced a card for
another word), and `supporting_meanings` must be `[]`. A context without
the item still ends up as an example; that is left to the roadmap's "flag
problem input" item.

The highest-value roadmap item, and the only one that changes generation.
Scope and card behavior are under [Decisions](#decisions).

1. Tests first: the prompt sent for a word with context contains the
   context; without context the prompt is unchanged (existing wire and
   prompt tests stay green).
2. Thread an optional `context` from `generate_word_data` /
   `generate_phrase_data` (`collections/*/generator.py`) through the
   collections' `generate_cards` / `generate_and_add_note` to the CLI, and
   extend the prompts in `collections/{word,phrase}/prompts/`: focus the card
   on the sense used there, and use the sentence as one of the examples.
3. CLI: `add --context`, `batch --format jsonl`. Results echo the context.
   Update the `ankinote-cli` skill.
4. Check a few real cards against a live key (polysemous words such as
   "bank", "run") before calling it done: call the generators only, no
   media, nothing saved to Anki.

## Step 6: Context on the web app's Generate page (M), done

Done 2026-11-25. Parser: `frontend/src/lib/brackets.ts`, tested with Vitest
(`make web-test`, new with this step) in `brackets.test.ts`; full-width
`［］` and `【】` count, since CJK input methods type them. A line whose
brackets don't pair up stays in the box with a note; the others are queued.
API: `context` on `POST /api/cards/{kind}` (words and phrases; 422
`context_not_supported` otherwise, `context_too_long` past 1000
characters); the row keeps it, so Regenerate sends it again. Prompts: parts
joined with ` … ` are one item, and a split word's highlights are its parts
as written. Checked live with `gemini-3.5-flash-lite`: German `rufe … an` →
anrufen, `fängt … an` → anfangen, 食べた → 食べる, 먹었어요 → 먹다,
`dímelo` → decir, `levée` → se lever, `pick … up` → pick up, each with the
sentence verbatim as the first example. README: "How People Use It" in all
six languages.

1. Tests first: the bracket parser (one item for word, joined parts for
   phrase, no brackets → today's line, several brackets on a word line → an
   error on that line); the generate API passes `context` through.
2. API: an optional `context` per item; regenerate keeps it.
3. Generate page: parse brackets for word and phrase; the queue row shows
   the item with the sentence on a muted second line; placeholder and line
   hint explain the brackets. Follow the design language; check desktop and
   phone widths.
4. README (all six languages): a short "how people use it" section after the
   showcase, workflow first, with this one: paste the sentence you met the
   word in and mark it. Benefits: the card covers that one sense, so a
   polysemous word or phrasal verb stays uncluttered, and the sentence you
   actually read stays on the card as its first example, which helps it
   stick. Present it through the web app; the CLI stays low-key.

## Later: the "photograph a wrong answer" workflow in the README, done

Added 2026-11-25 to "How People Use It" in all six READMEs: a photo of the
problem on the Generate page (STEM, Problem type), the worked solution and
how to find the method, checked in the preview before saving.

## After this plan

- [Flag problem input on language cards](../roadmap.md#flag-problem-input-on-language-cards):
  its CLI part adds a `warnings` list to each JSON result from step 3.
- "Review later" (roadmap item 5) needs web app work and stays a later idea.
