# Upgrade Compatibility: Plan

Work breakdown for the forward-compatibility review of
[Upgrades](../roadmap.md#upgrades-notice-a-new-version-upgrade-easily),
done 2026-11-25. Do the steps in order and mark each one done here (with
its commit) when it lands. A step that fixes a bug starts with a test that
reproduces it.

Why now: the upgrade check (8c530f5, not pushed) makes people upgrade, and
whatever a release ships keeps running in every install that never
upgrades. An old install can only be protected by its own code being
lenient, so the fixes below must ship in the same release as the check.
Don't push or release until step 6 is done.

## Findings

1. **`settings.json` with one unknown key is thrown away.** Reproduced: a
   `future_default` key under `defaults` makes `DefaultsConfig(**…)` raise
   `TypeError`; `load_settings()` catches it and returns `Settings()`, so
   every profile and API key is gone, and the next save (web settings, TUI)
   writes the defaults over the file. Mixed versions are realistic: the
   agent skill runs `uvx --from ankinote-ai ankinote`, which keeps the
   first cached version next to an upgraded web app, and Docker users pin
   tags or downgrade.
2. **CLI card commands rewrite existing note types on every run.** Each
   collection's `__aenter__` calls `_ensure_note_type_exists()`, which on
   an existing type adds missing fields and overwrites templates and CSS.
   A release that adds a field then changes the schema on the next
   `ankinote word add` (AnkiWeb demands a full sync, nobody asked); an
   older CLI next to a newer web app reverts templates, labels and styling,
   and would re-add a template a later release removed (new cards, schema
   change). The web app only creates missing types on save and leaves
   updates to the Note types page.
3. **The agent skill points at a cache-pinned CLI**:
   `src/ankinote/skills/ankinote-cli/SKILL.md` says
   `uvx --from ankinote-ai ankinote`; the READMEs moved to `@latest`.
4. **A major release looks like a patch** in the top bar and on About.
5. **Every link and command is frozen in code.** A separate JSON to fetch
   was considered and rejected: a second host to keep alive forever, and
   `raw.githubusercontent.com` is often unreachable from mainland China.
   The PyPI answer already carries `info.project_urls` from the *latest*
   release's `pyproject.toml`, which a future release can use to redirect
   old installs.
6. **The Docker command doesn't say where to run it**, and does nothing
   when `ANKINOTE_IMAGE` pins a version tag.

Places without a version or migration path, and why each is acceptable
once the steps land:

| Place | Today | After |
|---|---|---|
| `settings.json` | No schema version; the shape is told by keys | Lenient reading (step 1); add a version only for the first non-additive change |
| Note types | No version; status diffs fields, templates, CSS | Fields and templates are add-only (rules below) |
| `<collection>.sync.json` | Strict; an unknown state fails | Fails closed (no sync, no writes): acceptable |
| `--json`, jsonl input | No version field | Add-only keys (rules below) |
| Installed skill copy | Not refreshed by an upgrade | README already says to re-run `ankinote skill install`; release notes repeat it when the skill changes |
| `/api/update` | Ships with its frontend in one wheel | No constraint |

## Steps

Estimates are working time including tests and checks.

### Session 1: the two blockers (Python only, about 2.5–3 h)

1. **Lenient settings** (1.5–2 h), done 2026-11-25.
   `src/ankinote/settings.py`, `tests/test_settings.py`.
   - Tests first: an unknown key in `defaults`, in a profile, and at the
     top level keeps the rest of the settings; a save keeps unknown
     top-level keys; an unparseable file is not overwritten by defaults.
   - `defaults` and profiles take known keys only; wrong types fall back
     per field, not for the whole file.
   - `save_settings` merges into the keys already on disk, so a
     downgrade-then-upgrade round trip keeps newer settings.
   - An unreadable file (bad JSON, wrong top-level type) is moved aside to
     `settings.json.broken-<timestamp>` with a warning before defaults are
     used, so no key is lost.

   *Cut point: commit; safe to stop here.*

2. **CLI leaves existing note types alone** (about 1 h), done 2026-11-25.
   `src/ankinote/collections/{word,phrase,sentence,stem}/collection.py`,
   `src/ankinote/cli/*.py` `init` commands, `tests/collections/`,
   `tests/cli/`.
   - Tests first: entering a collection whose type exists calls neither
     `ensure_fields`, `update_templates` nor `update_styling`; a missing
     type is still created.
   - `__aenter__` creates the type and deck only when missing; `init` calls
     `ensure_in_anki()` explicitly and stays the CLI's way to update.
   - Update `init`'s help, the skill's command list ("create note type +
     deck if missing") and `docs/cli-usage.md`: `init` also updates an
     existing type, which can require a full sync.

   *Cut point: commit; end of session 1.*

### Session 2: the update check and its texts (about 2–2.5 h)

3. **Skill uses `@latest`** (10 min), done 2026-11-25. `SKILL.md` "Running it":
   `uvx --from ankinote-ai@latest ankinote`.
4. **Major releases** (about 1 h), done 2026-11-25.
   `src/ankinote/web/update_api.py`,
   `frontend/src/lib/api.ts`, `frontend/src/routes/About.svelte`,
   8 locale files, `tests/web/test_update_api.py`.
   - `UpdateStatus.major: bool` (latest major above current).
   - About puts the release notes first and says "major release: read
     before upgrading"; the command follows. No "stay on 1.x": every
     upgrade command jumps to the newest release anyway.
5. **Notes link from PyPI's `project_urls`** (about 45 min), done
   2026-11-25. `update_api.py`, tests.
   - Read `info.project_urls` from the same response; a label matching
     "Upgrade notes" (compare case- and punctuation-insensitively) replaces
     the `…/releases/tag/vX.Y.Z` link. Don't set it in `pyproject.toml`
     yet; it exists for a future release to use. Only `https://` links
     count, since the page renders it as a link.
6. **Docker wording** (20 min, together with step 4's locale edits), done
   2026-11-25:
   run it in the folder with `compose.yaml`; if `ANKINOTE_IMAGE` pins a
   version, change the tag first.

   *Cut point: commit; steps 3–6 can also be split after step 3 or 4.*

### Session 3 (or the end of session 2): verify and release (about 1 h)

7. Add a one-line pointer to the compatibility rules in `AGENTS.md`
   (follow the `cc-agent-instructions` skill), done 2026-11-25.
8. Full checks: `make test`, `make lint`, `make check`, `make web-check`,
   `make web-test`, `make web-build`; run the web app against a faked
   PyPI answer to see the chip and About for a minor and a major release,
   done 2026-11-25: all green; the chip, About (Docker hint for a minor,
   notes first for a major) and the phone layout look right.
9. Push, then `make release part=minor` (new behaviour: update check). The
   release notes say to re-run `ankinote skill install`. Done 2026-11-25:
   v1.3.0, notes written by hand.

## Compatibility rules

These bind every release from now on; they are also listed in the roadmap.

- Never rename: the package `ankinote-ai`; the entry points `ankinote` and
  `ankinote-web`; the image `ghcr.io/ankinote-ai/ankinote` and its
  `:latest` tag; `ANKINOTE_INSTALL=docker` in the image; the volume paths
  `/config` and `/data`; existing environment variable names.
- Note types: fields and card templates are add-only (no rename, no
  removal). Only an explicit update (Note types page, `init`) applies them.
- `settings.json`: read leniently, keep unknown keys; a non-additive change
  needs a version key and a migration.
- `anki` is pinned exactly; bump it only in a minor release, with a note
  that the collection may be upgraded and can't be opened by older
  releases afterwards.
- `--json` output and jsonl input: add keys only; exit codes keep their
  meaning.
- Breaking changes only in a major release, whose release notes start with
  "Before you upgrade" (`make release` uses `--generate-notes`, so write
  that section by hand for a major). To point every older install at a
  page instead, set `"Upgrade notes"` under `[project.urls]`.
