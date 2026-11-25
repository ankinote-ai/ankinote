# Roadmap

Product directions, grouped by status. Nothing here is a commitment to a date,
framework, or API. Last reorganized 2026-11-25.

- **Next**: nothing scheduled; the [CLI agent-tool plan](plans/cli-agent-tool.md)
  finished 2026-11-25.
- **Small follow-ups**: [unscheduled, independent of each other](#small-follow-ups).
- **Waiting for demand**: [built only once users ask](#waiting-for-demand).
- **Later ideas**: [CLI as an agent's tool](#the-cli-as-an-agents-tool),
  [2.0 custom card types](#20-candidate-custom-card-types-with-ai-assisted-authoring),
  [deployable web service](#future-major-version-deployable-web-service).
- **Dropped or out of scope**: [what isn't planned](#dropped-or-out-of-scope).
- **Shipped**: [history and settled decisions](#shipped).

## Product principles

Positioning: a free, open, bring-your-own-key card maker for self-hosters and
heavy Anki users, not a general-purpose toolkit. The fixed prompts and note
types are the product (in-app editing of them was
[dropped](#dropped-or-out-of-scope); fully custom types are a
[2.0 question](#20-candidate-custom-card-types-with-ai-assisted-authoring)).

- **Show the result before the install**: sample cards, GIF, translated READMEs.
- **One key is enough**: a single Gemini or OpenAI key covers text, image,
  and audio; a text-only key still produces cards, without media.
- **One recommended path per place** (revised 2026-11-19; until then the
  built-in `collection` backend was the single recommendation):
  - *On the computer the user studies on* (the `uvx` install, the CLI an
    agent runs): AnkiConnect into Anki Desktop. Most Anki users have
    Desktop; writing into it avoids a second collection, the first full
    download (slow for large collections), and the full-sync conflicts two
    collections on one AnkiWeb account can cause. The wizard preselects it.
  - *On an always-on home server or NAS* ("add a word from the phone
    browser while the computer is off"): built-in `collection` with
    AnkiWeb sync, via the headless Docker stack.
  - *Not the public internet.* AnkiNote is single-user without a login; the
    local-access guard stops other web pages from driving it, nothing more.
    Use a home network, Tailscale, or a reverse proxy that asks for a login
    (`ankinote-web` warns at startup when it listens beyond loopback).
- **The web app leads; the CLI supports** (2026-11-25): READMEs, docs and
  launch copy present the web app first and keep the CLI and its agent
  skill short and near the end.
- **Curated over configurable**: a few good themes and language pairs
  rather than open-ended editors.
- **Never break existing cards**: note type names and fields stay or get a
  migration (field changes force a full AnkiWeb sync).

## Next

Nothing scheduled. Last: the [upgrade check](#upgrades-notice-a-new-version-upgrade-easily)
and the fixes from its [compatibility review](plans/upgrade-compatibility.md),
released in 1.3.0 (2026-11-25).

Before that: [The CLI as an agent's tool](#the-cli-as-an-agents-tool),
items 1–4, plus the CLI's inconsistencies, ran as a step-by-step
[plan](plans/cli-agent-tool.md) that finished 2026-11-25, including context
sentences in the CLI and on the Generate page. Grammar cards and scene cards
were next before that and are now [waiting for demand](#waiting-for-demand).

## Small follow-ups

Unscheduled; each can ship on its own.

### Flag problem input on language cards

Agreed 2026-11-25. Today the prompts mirror the input exactly: a line with
several sentences becomes one long card, a cut-off sentence is translated as
it stands, and a typo stays on the card (on a production card the learner
then memorizes it). Nothing tells the user.

- Keep "one line, one card". The model also returns the problems it sees
  (several sentences, a fragment, a likely typo with its correction, the
  wrong language); they are not stored, so the note types don't change.
- Neither fix silently nor mirror silently. The web app shows them on the
  row with actions (split into lines, use the correction, keep as is); the
  CLI reports them, ideally in the `--json` results of
  [the agent's tool](#the-cli-as-an-agents-tool).
- Never split automatically: a short exchange ("How are you? — Fine.") is
  one item on purpose.
- Start with tests that reproduce the kept typo and the unflagged
  several-sentence line.
- Also flag a context sentence that doesn't contain the item (CLI
  `--context`; the web app's brackets rule it out). Checked 2026-11-25: told
  to ignore such a context, the model still used it as the first example.

### Fix with AI inside the live editor

Today "Fix with AI" sits under the preview's formula errors and works on the
applied card. In the STEM live editor the same error list only says "fix them
in the form, or apply the edit and use Fix with AI", which is two steps.

Proposed 2026-11-25 (UI not yet confirmed):

- Show the same button in the live editor's error list, with the same label.
  It is a targeted, no-input action triggered by detected errors, so the
  label names what changes (the formulas), not a generic "edit further";
  open-ended requests stay in the "Rewrite with AI" box.
- It sends the current, unapplied form plus the errors, and writes the fixed
  fields back into the form rather than applying them, marking the fields
  that changed. The editor's contract stays "nothing changes until Apply";
  Cancel still discards everything.
- Backend: the fix-latex route needs to accept form contents, not only a
  draft id.

### STEM in the web app

- Thinking level on the Generate page: in 0.x, not yet in the web app.

### Rendering polish

- Let detailed explanations/derivations expand on demand. Verify `<details>`
  on Anki desktop and AnkiDroid before shipping; keep a visible fallback where
  unsupported.
- Shared MathJax macro configuration for common notation.
- Optional `common_mistakes` callout where appropriate, added to the relevant
  type's schema and template rather than a new card type.

### Thinking control

How it works today is under [Shipped](#thinking-control-shipped). Open items:

- Measure what "off" saves on the presets (latency, tokens per card) with real
  keys; the wire tests only prove the request is right.
- Disabling thinking made the model less consistent about the output contract
  (`word` occasionally returns a bare record instead of a JSON array; now
  tolerated in `generate_word_data`). Watch for similar contract slips in the
  other language generators and tighten prompts or parsing as needed.

### Launch

- Promotion channels and their status are tracked outside the repo.

## Waiting for demand

Designed or discussed; built only once users ask.

- **Grammar cards** (raised and deferred 2026-11-25). No user has asked;
  sentence cards already explain grammar in context; LLMs are least reliable
  on exactly these fields (contrasts, common mistakes), and learners can't
  catch the errors; the cost is M–L. If built:
  - English as the target first (beta, hidden for other targets), since
    English grammar is where models are most reliable and Chinese speakers
    learning English are the likely audience. Fields stay language-neutral
    so other targets can follow without a note type change.
  - A language card type next to Word/Phrase/Sentence, not a fifth STEM
    type (STEM Concept has no language pair, audio or ruby), with
    fill-in-the-blank on its examples.
  - Input: the pattern as a textbook writes it (`〜ばかりだ`, `ser vs
    estar`), optionally with the sentence it was met in as context. The
    front is the model's normalized pattern, so spellings of one pattern
    land on one card. One point per card: too broad a topic returns
    narrower points to pick from; "A vs B" is one card about A with B under
    the contrast. Native-language "how do I say…" queries are left out.
- **Scene cards with image occlusion** (raised and deferred 2026-11-25): a
  labeled scene (a kitchen with each object named in the target language),
  the labels hidden by Anki's own Image Occlusion masks. Deferred because it
  saves the user little over making the same note in Anki. Findings if
  built:
  - Write Anki's stock `Image Occlusion` notes; no new note type. The
    `Occlusion` field holds `{{cN::image-occlusion:rect:left=…:top=…:width=…:height=…:oi=1}}`
    with 0–1 coordinates, one `cN` per card. Rendering depends only on the
    field, so AnkiConnect's `addNote` should work as well as the direct
    backend's `add_image_occlusion_note` (unverified against Desktop;
    collections from before 23.10 may lack the type).
  - AnkiNote draws the labels itself, never the image model (it misspells,
    above all CJK, and its text positions are unknown). Flow: text model
    lists the objects for a topic → image model draws them without text →
    vision model locates the listed objects → labels with leader lines
    composited onto the image, masks placed on the known label boxes.
  - No per-word audio (`Back Extra` is shared by the note's cards); CJK
    labels need a bundled font. Generated scenes first; a user's own photo
    reuses the flow with harder detection.

- **A built-in password** for the web app. Until then, a reverse proxy that
  asks for a login (see the principles above). Accounts belong to the
  [deployable web service](#future-major-version-deployable-web-service).
- **Per-field rewrite / simplify buttons** on STEM cards: only if users keep
  wanting to change one field rather than the whole card.
- **Extra instructions per card type** (2026-11-25): one text box per type
  (Word, Phrase, Sentence, STEM), appended to the built-in prompt as the
  user's preferences ("examples from business settings", "explanations in two
  sentences"). The built-in prompt and its output contract stay code-owned;
  reset is clearing the box. An advanced option on the Note types page only,
  kept out of the Generate workflow; the CLI uses it too. A "try it" button
  may compare a sample card before and after.
- **Keep template edits made in Anki** (2026-11-25): today every run rewrites
  the card templates. Possible approach: a version marker comment in each
  default template plus the hashes of all past defaults, so templates still
  equal to a past default update as now and edited ones are left alone (with
  "a newer default exists" and a reset on the Note types page). The preview
  would then have to read the templates from Anki.

## The CLI as an agent's tool

Idea, 2026-11-18. The workflow: a user photographs a page they're reading with
new words underlined and asks an AI agent (Claude Code, Codex, …) to make
cards. The agent reads the picture, extracts the underlined words, and calls
`ankinote word batch …`. This works today and is how the README presents the
CLI; batch generation for people who want to review each card is the web
app's job (one item per line on the Generate page).

What would make the CLI a better agent tool, in rough order of value
(items 1–4 shipped 2026-11-25 by the [plan](plans/cli-agent-tool.md)):

1. ✅ **Context with each item.** Pass the sentence the word was underlined in,
   so the card explains the sense used there and can use that sentence as an
   example (the agent has it from the photo anyway). CLI: `add --context`,
   `batch --format jsonl`; the Generate page takes the sentence with the item
   in brackets.
2. ✅ **Machine-readable results.** `--json` on `add`/`batch`: one result per
   item (saved note id, or the error), and a non-zero exit when any item
   failed, so the agent can retry or report exactly what didn't make it.
3. ✅ **Input from stdin** (`--file -`) and one-item-per-line files, so phrases
   and sentences batch as cleanly as words.
4. ✅ **A ready-made agent skill**: when to call which command, the
   language flags, and to ask before making more than a few dozen cards.
   Ships in the wheel; `ankinote skill install` copies it into
   `~/.claude/skills` and `~/.agents/skills`.
5. **Review later.** Optionally send CLI-made cards to the web app's queue
   instead of straight to Anki, for users who want the agent to collect and
   themselves to approve.

## 2.0 candidate: custom card types with AI-assisted authoring

Idea raised 2026-11-14; not scheduled.

Users define their own card types — fields, templates, style — plus the
instructions used to generate them, and AI helps write and tune them. This
widens the audience from language and STEM learners to any domain (medicine,
law, programming, certifications) and to heavy Anki users who already have
their own note types.

It reverses the position that the fixed prompts and note types are the
product. Taking it on means repositioning 2.0 from "good cards out of the
box" to "a card generation platform", decided deliberately. (Editing only
the built-in types' templates, styling and prompts was considered as a first
step and dropped 2026-11-25; see [Dropped](#dropped-or-out-of-scope).)

### Card type spec

A declarative, shareable file per card type:

```yaml
name: Drug Card
input: "drug name"              # what the user types
fields:
  - name: Drug
    source: input
  - name: Class
    source: generated
    description: "pharmacological class, one short phrase"
  - name: SideEffects
    source: generated
    kind: list                  # rendered as <ul> by the template
    description: "the 3–5 most common side effects"
  - name: Audio
    source: tts(Drug)
  - name: Picture
    source: image(Drug)
prompt: "For pharmacy students…"  # overall instructions
templates: [...]                # front/back in Anki template syntax
css: ...                        # or references to theme tokens only
```

- The JSON schema for structured output is derived from `fields`; the prompt
  is a fixed system part + field descriptions + the user's instructions +
  examples.
- Media fields (`tts`, `image`) reuse the existing `MediaGap` degradation.
- Fields hold content only; presentation belongs to the template. Built-in
  collections today bake HTML into fields at generation time (`meaning-row`,
  `*-chip`, ruby conversion), which a user-defined type can't rely on.
- Test of the design: re-express the built-in kinds as specs. What can't
  be expressed (ruby text, highlighted example sentences, several records per
  query) shows which field `kind`s are missing. Ideally built-ins end up as
  spec files too.

### AI-assisted authoring: iterate on sample cards, not on the prompt

Users can't judge a prompt but can judge a card at a glance.

1. Start from one of: a one-line description of the goal; an existing Anki
   note type imported from the collection (fields, templates and CSS are
   already readable, and its existing notes are the best few-shot examples);
   a gallery template.
2. AI drafts the spec and immediately generates about three sample cards with
   the real model, shown in the card preview.
3. The user critiques the samples ("side effects too long", "add a
   mnemonic"); AI revises the *spec*, not the cards, regenerates the samples,
   and shows them against the previous version.
4. The sample inputs become a regression set, re-run whenever the spec
   changes.

### Sharing

A spec is one file: export, import, and possibly a community gallery like
AnkiWeb shared decks, which doubles as a promotion channel.

### Risks

- Quality: bad custom types produce bad cards that reflect on the tool; the
  AI-assisted loop is what makes the feature viable, not an extra.
- Changing a type's fields forces a full AnkiWeb sync once it is in use; the
  editor must say so before applying.
- User templates and CSS run in the preview; keep it sandboxed as today.

### Preparation now

- New collection code should keep content and presentation apart where it
  costs little, to ease the move.
- First 2.0 step is not UI: express the built-in types as specs to validate
  the format.

## Future major version: deployable web service

Explore evolving ankinote from a local CLI/web application into a web
service that can be deployed to the public internet. A maybe-later if the
single-user product gains traction (set aside, then back on the table
2026-09-15); no architecture work started, and no commitment to a framework
or authentication provider.

The web version must include user identity and access management as a
foundational concern, rather than an afterthought. Initial planning should
cover:

- user registration, sign-in, sign-out, and secure session management;
- account recovery and verification flows;
- authorization and strict per-user data isolation;
- secure storage and handling of user-provided AI-provider credentials, if
  supported;
- deployment, HTTPS, secrets management, observability, and abuse/rate-limit
  controls;
- how web users create and synchronize cards with Anki, without assuming a
  publicly reachable AnkiConnect instance.

## Dropped or out of scope

- **Comparison card type** (`AINote STEM Comparison`, contrast pairs such as
  L1 vs L2 regularization): dropped 2026-11-25.
- **Editing the built-in card types in the app** (templates, CSS and whole
  prompts, with reset to default): scoped 2026-11-21, dropped 2026-11-25. No
  user had asked for it, and an editor, preview, "newer default" tracking and
  prompt splitting add a lot of product for that. What remains is in
  [Waiting for demand](#waiting-for-demand) (extra instructions, keeping
  template edits made in Anki). The scoping notes are in git history
  (commit 918cbe6).
- **A downloadable sample deck** (`.apkg`, 2026-11-25): the README's
  screenshots and GIF show the cards.
- **Photo input for language cards** (2026-11-25): an agent reading the
  photo and calling the CLI covers it.
- **`gemini-nano-banana-2.1` for images** (2026-11-25): same $0.0336 per 1K
  image as `gemini-3.1-flash-lite-image` and better quality, but it thinks at
  `medium` by default, billed at $7.50 per 1M tokens, and LiteLLM's
  `aimage_generation` sends no thinking setting. Neither model has a 512px
  tier, so we take 1K and resize.
- **Gemini Batch API** (2026-11-25): half price, but jobs are asynchronous
  (up to 24 hours), which does not suit generating while you review. Worth
  revisiting only for large file imports.
- **Cloze cards from a context sentence** (2026-11-25): the marked word in
  its sentence could become a cloze, but a new card needs a new field (a
  migration and a full AnkiWeb sync), and the word note's recall card
  already targets the one sense. Cloze fits grammar cards better, which are
  [waiting for demand](#waiting-for-demand).
- **Stronger grammar notes on sentence cards** (2026-11-25): which grammar
  is worth explaining depends on the learner's level, which AnkiNote doesn't
  know.
- **"Explain" (tutoring)**: makes the app a learning companion rather than a
  card maker.
- **HyperTTS-level provider coverage**, an **Anki add-on rewrite**, and a
  **hosted multi-user service** run by the project (a self-deployable one is
  the [later idea](#future-major-version-deployable-web-service) above).
- **Open-ended editors**: no layout variants for themes, no in-app CSS or
  template editor.

## Shipped

### Upgrades: notice a new version, upgrade easily

Shipped in 1.3.0 (2026-11-25). AnkiNote notices a newer release and shows how
to upgrade; it never upgrades itself.

- **`uvx` stays current by itself.** uvx reuses the environment cached on
  the first run, so `uvx --from ankinote-ai ankinote-web` users never see a
  new release. The READMEs switch to `uvx --from ankinote-ai@latest
  ankinote-web`, which checks PyPI on each launch and still starts offline
  from the cache (checked with uv 0.13.9).
- **The web app's backend checks PyPI**
  (`https://pypi.org/pypi/ankinote-ai/json`, `info.version`) at startup and
  once a day while it runs, since a home-server container can run for
  months. It is the source for every install path (the Docker images are
  built from PyPI releases) and has no rate limit, unlike GitHub's API.
  A failed check stays silent. The browser never contacts PyPI.
- **On by default, with an off switch**: `ANKINOTE_UPDATE_CHECK=0`. The
  check shows pypi.org the server's IP; the README says so.
- **Shown in the top bar and on the About page**: a small "new version"
  marker in the top bar links to About, which shows the new version, its
  release notes link (where "Before you upgrade" notes live) and the
  command. The marker can be dismissed for that version.
- **The command matches the install path**, with all of them listed when
  it can't be told:
  - Docker (`ENV ANKINOTE_INSTALL=docker` in the Dockerfile):
    `docker compose pull && docker compose up -d`.
  - `uv tool install` (`uv-receipt.toml` in `sys.prefix`):
    `uv tool upgrade ankinote-ai`.
  - `uvx` (`sys.prefix` inside the uv cache): the `@latest` command.
  - Otherwise: `pip install -U ankinote-ai`.
- **Not run by the app**: a running process can't replace itself, a
  container would need the Docker socket, and Windows locks running
  executables.
- **No check in the CLI**: agents read its output, `--json` above all.

**Forward-compatibility review: done 2026-11-25; its fixes shipped with
the check in 1.3.0.**
Whatever a release ships keeps running in every install that never
upgrades, so the fixes ship with the check, not after it. Findings, steps
and estimates are in the [plan](plans/upgrade-compatibility.md). In short:

- Blockers: one unknown key makes `settings.json` reset to defaults (keys
  lost on the next save); CLI card commands rewrite existing note types on
  every run (a new field forces a full AnkiWeb sync unasked).
- The check: say "read first" for a major release (no "stay on 1.x");
  take an optional release-notes link from PyPI's `project_urls` rather
  than a separately fetched JSON; the skill moves to `@latest`; the
  Docker command says where to run it.
- **Compatibility rules** for every release from now on: never rename the
  package, entry points, image, `ANKINOTE_INSTALL`, volume paths or env
  vars; note type fields and templates are add-only and applied only on
  an explicit update; `settings.json` is read leniently; `anki` bumps only
  in a minor release; `--json` and jsonl keys are add-only; breaking
  changes only in a major release with "Before you upgrade" notes (or an
  `"Upgrade notes"` project URL, which every older install links to).

### 1.0: shorter path to the first card (2026-11)

Direction agreed 2026-11-12 (work breakdown in [plans/v1.md](plans/v1.md));
released as 1.0.0. The rewrite replaced the NiceGUI UI with a Svelte
single-page app bundled into the wheel, so the `uvx` install needs no Node;
the CLI/TUI stay and share `settings.json` with the web app.

- README fixes and a one-line install (v0.6.5).
- Design language: one token set shared by the web UI and the cards; see
  [Design Language](design/design-language.md).
- API layer and the new frontend (wizard and Generate pages), one-key
  presets, additional TTS providers, graceful degradation without media.
- Languages: Chinese and Korean (beta) as targets, so English, Spanish,
  French, German, Japanese, Chinese, and Korean work in any native/target
  pairing.
- Card themes: a few curated palettes, light and dark chosen independently,
  applied to the UI and the cards together.
- Showcase: GIF, screenshots, READMEs in six languages, Docker deploy
  templates (`deploy/headless`, `deploy/standard`).

### STEM architecture

The unified STEM schema was replaced by four independent generation models,
prompts, field sets, and Anki note types:

- `AINote STEM Concept`: front, brief answer, detailed explanation, image.
- `AINote STEM Formula`: front, formula, meaning, variables, conditions, derivation, image.
- `AINote STEM Procedure`: front, summary, steps, conditions, image.
- `AINote STEM Example`: front, answer, solution steps, explanation, image.

All use `front` as the first field (Anki's default sort field), native Anki
tags, and the shared `AINote::STEM` deck and paper-card visual theme.
Structured variable/step lists render into their own storage fields.
There is no stored `card_type` field and no V2 suffix.

The common STEM entrypoint accepts automatic classification or an explicit type.
Automatic mode classifies first and then loads the selected type's prompt/schema;
explicit selection skips classification. Upserts are scoped by note type as
well as front and deck.

The legacy `AINote STEM` is no longer created or updated. Existing legacy notes
are left alone; there is no automatic migration or deletion.

### STEM in the web app (2026-11-13)

Generate → MathJax preview → live edit → rewrite with an instruction → save;
see the design language's Generate page notes. "Fix with AI" under the
preview's formula errors shipped the same day.

### Thinking control (shipped)

`TextGenerationService.generate_text` takes `reasoning_effort`. The language
generators (`word`, `phrase`, `sentence`) pass `DISABLE_REASONING` (`"none"`).
For a known vendor the service forwards it as `reasoning_effort` and LiteLLM
maps it per model (fixed 2026-11-25; before, only DeepSeek was turned off and
LiteLLM 1.81 silently dropped every level for `gpt-6-luna`):

- OpenAI: `reasoning_effort="none"`.
- Gemini 3: the lowest `thinkingLevel` the model takes (`minimal` for
  `gemini-3.5-flash-lite`, `low` for `gemini-3.8-flash`); Gemini 3 cannot
  switch thinking off.
- Anthropic: no `thinking` block.
- DeepSeek: `extra_body={"thinking": {"type": "disabled"}}`.
- A custom OpenAI-compatible endpoint: nothing, as a local server may reject
  the value.

This depends on LiteLLM's model table knowing the model, so a new preset
model needs a LiteLLM that lists it. `tests/services/test_ai_thinking_wire.py`
checks the request body each preset produces. `stem` keeps thinking on and
sends no `temperature`, which thinking models ignore or reject.

Language cards ask for `temperature=0.3` (steady, dictionary-like output),
except on Gemini 3 and later, which keep their default 1.0 as Google advises
(lower values can make them loop or degrade).

All CLI commands take `--thinking [off|low|medium|high|default]` to override
the per-collection default for a single run. `services.ai.resolve_thinking`
(with `THINKING_CHOICES`) maps the choice to a `reasoning_effort` value; it is
shared by the CLI (`cli/factory` re-exports it).

### Cards in the native language (2026-11-25)

Card template names (Recognition, Recall, …, Card 1) and the labels printed
on the cards (section titles, STEM type badges) follow the native language
in settings, never a per-run CLI option, since the note types are shared.

- Texts live in `src/ankinote/card_labels.json`; templates mark labels as
  `[[t:key]]`. English keeps the names cards had before.
- A template is matched under its name in any language and renamed in
  place, which keeps its cards and review history and needs no full AnkiWeb
  sync (a test checks `scm`).
- Saving a new native language in the web app renames and relabels the
  types Anki has at once; otherwise (TUI, Anki unreachable) the Note types
  page shows the rename as pending, and the next update or CLI run does it.

### Google key setup (2026-11-25)

Default audio stays on Gemini's speech model; Google Cloud Text-to-Speech
stays an option under "Set up each kind of content separately". Checked
against Google's docs on 2026-11-25:

- Since 2026-05-28 new AI Studio keys are restricted to the Gemini API, and
  Google advises against widening a key to other APIs, so Cloud TTS needs a
  second key from the Cloud console.
- Cloud TTS needs billing on its project even within the free monthly
  allowance. Both break "one key is enough".
- Gemini's speech models are on the free tier; their daily limits aren't
  published and show per project in AI Studio.

The wizard's Gemini steps note those free-tier limits (a word card makes
several clips). The Cloud TTS route lists its three steps (billing, enable
the API, a key restricted to it). The connection test now tells a project
without billing (`BILLING_DISABLED`) and a key whose restrictions leave the
API out (`API_KEY_SERVICE_BLOCKED`, e.g. an AI Studio key) apart from a bad
key.

### Interface languages (2026-11-18)

The language menu in the top bar offers every language the cards support:
English, Simplified and Traditional Chinese, Japanese, Korean, French,
Spanish and German.

- Catalogs live in `frontend/src/lib/locales/`, one JSON per language; the
  first visit picks the closest to the browser language (`zh-TW`, `zh-HK` and
  `zh-Hant` get Traditional).
- Each catalog has the same keys and `{placeholders}` as `en.json`
  (`tests/test_locale_catalogs.py` checks it). A missing key still falls back
  to English rather than showing the key.
- Adding a language: a new catalog, one line in `i18n.svelte.ts`, and its
  card-language entries in `languages.ts`.

### Settled earlier

The CLI stays and shares `settings.json` with the web app (2026-09-22); the
Anki backend, collection path, and storage secret no longer need env vars
(2026-09-22).
