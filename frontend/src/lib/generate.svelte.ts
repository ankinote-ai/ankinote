/**
 * The Generate workspace's session: every line of input becomes a queue
 * row that generates in the background (a few at a time), and the preview
 * follows the selected row. Nothing reaches Anki until a row is saved. A
 * word or phrase line may be the sentence it was met in, with the item
 * marked by brackets (`brackets.ts`).
 *
 * A ready or saved note can have its fields edited first (`Editing`);
 * applying an edit replaces the note's preview, and a saved row goes back
 * to ready until it's saved again. A STEM note's editor previews the edit
 * live, and a STEM note can be rewritten by the model from an instruction.
 * Edits and rewrites can be undone.
 *
 * The model may report problems with a line (a likely typo, several
 * sentences on one line): the row is flagged and offers to correct or split
 * the line, or to keep the notes as made. "Save all" leaves flagged rows.
 * A misspelled word or phrase is made as the correction instead; the row
 * says so and can be made again as typed, but isn't held back.
 *
 * The session lives at module level, so switching workspaces keeps it; a
 * reload starts a new one (drafts are in the server's memory anyway).
 */
import { parseLine, type BracketError } from "./brackets";
import type { Picture } from "./picture";
import { randomId } from "./randomId";
import {
  api,
  ApiError,
  type CardSide,
  type DraftNote,
  type FormField,
  type FormRow,
  type FormValues,
  type InputIssue,
  type Kind,
  type MathError,
  type SavedNote,
  type StemType,
  THINKING,
  type Thinking,
} from "./api";

/** Providers rate-limit; two at a time keeps a batch moving without 429s. */
const CONCURRENCY = 2;
const STORAGE_KEY = "ankinote.generate";

export type RowState = "queued" | "generating" | "ready" | "saving" | "saved" | "failed";
export type Failure = {
  code: string;
  detail: string;
  during: "generate" | "save" | "edit" | "rewrite" | "undo";
};

/** Wait this long after the last keystroke before previewing an edit. */
const LIVE_DELAY_MS = 300;

/** The editor's working copy: a lines field is one text, one item per line. */
export type EditValues = Record<string, string | FormRow[]>;

function editValues(form: FormField[]): EditValues {
  return Object.fromEntries(
    form.map((f) => [f.key, f.type === "lines" ? f.value.join("\n") : $state.snapshot(f.value)]),
  );
}

function formValues(form: FormField[], values: EditValues): FormValues {
  return Object.fromEntries(
    form.map((f) => {
      const value = values[f.key]!;
      return [f.key, f.type === "lines" ? (value as string).split("\n") : $state.snapshot(value)];
    }),
  );
}

/** One note's fields being edited, until applied or cancelled. */
export class Editing {
  values = $state<EditValues>({});
  applying = $state(false);
  failure = $state<Failure | null>(null);
  /** STEM: the cards as the edit stands (null until it differs). */
  live = $state<CardSide[] | null>(null);
  /** STEM: why the edit as it stands can't be previewed (a blank field…). */
  liveFailure = $state<Failure | null>(null);
  readonly #original: string;
  #asked = 0;
  #timer: ReturnType<typeof setTimeout> | null = null;

  constructor(readonly note: DraftNote) {
    this.values = editValues(note.form);
    this.#original = JSON.stringify(this.payload());
  }

  /** Whether the editor shows the card beside the form as you type. */
  get isLive(): boolean {
    return this.note.kind === "stem";
  }

  /** Preview the edit as it stands, once typing pauses. */
  schedule() {
    if (!this.isLive) return;
    if (this.#timer) clearTimeout(this.#timer);
    this.#timer = setTimeout(() => void this.#preview(), LIVE_DELAY_MS);
  }

  stop() {
    if (this.#timer) clearTimeout(this.#timer);
    this.#asked += 1;
  }

  async #preview() {
    const asked = ++this.#asked;
    if (!this.changed) {
      this.live = null;
      this.liveFailure = null;
      return;
    }
    try {
      const { cards } = await api.previewDraft(this.note.id, this.payload());
      if (asked !== this.#asked) return;
      this.live = cards;
      this.liveFailure = null;
    } catch (error) {
      // Keep showing the last edit that could be previewed.
      if (asked === this.#asked) this.liveFailure = describe(error, "edit");
    }
  }

  payload(): FormValues {
    return formValues(this.note.form, this.values);
  }

  get changed(): boolean {
    return JSON.stringify(this.payload()) !== this.#original;
  }
}

export class Row {
  readonly id = randomId();
  state = $state<RowState>("queued");
  /** One note per part of speech for a word. */
  notes = $state<DraftNote[]>([]);
  /** Which of `notes` the preview shows. */
  pick = $state(0);
  startedAt = $state(0);
  /** What the generation under way was asked for besides the text. */
  asked = $state({ image: false, audio: false });
  failure = $state<Failure | null>(null);
  saved = $state<SavedNote | null>(null);
  /** Set while the selected note's fields are being edited. */
  editing = $state<Editing | null>(null);
  /** Set while the model rewrites the note; when it started. */
  rewriting = $state(0);
  /** The rewrite under way only fixes the formulas the preview couldn't show. */
  fixing = $state(false);
  undoing = $state(false);
  /** A rewrite or undo that didn't happen; the note is as it was. */
  changeFailure = $state<Failure | null>(null);
  /** What the model saw wrong with the line; the notes follow it as typed. */
  issues = $state<InputIssue[]>([]);
  /** The user chose to keep the notes despite `issues` (or saved them). */
  issuesKept = $state(false);

  /** STEM: the type asked for; undefined lets the model choose. */
  readonly cardType?: StemType;
  /** STEM: how hard the model thinks; undefined is the server's default. */
  readonly thinking?: Thinking;
  /** STEM: a picture of the question, read by the model. */
  readonly picture?: Picture;
  /** Words and phrases: the sentence the item was met in; regenerating keeps it. */
  readonly context?: string;
  /** Words and phrases: made from the spelling given, never a correction. */
  readonly asTyped: boolean;

  constructor(
    readonly kind: Kind,
    readonly text: string,
    extra: {
      cardType?: StemType;
      thinking?: Thinking;
      picture?: Picture;
      context?: string;
      asTyped?: boolean;
    } = {},
  ) {
    this.cardType = extra.cardType;
    this.thinking = extra.thinking;
    this.picture = extra.picture;
    this.context = extra.context;
    this.asTyped = extra.asTyped ?? false;
  }

  get note(): DraftNote | null {
    return this.notes[this.pick] ?? null;
  }

  /** Has a preview that can be saved (again). */
  get saveable(): boolean {
    return this.notes.length > 0 && (this.state === "ready" || this.state === "saved");
  }

  /** Ready, with problems the user hasn't seen off yet (a correction included). */
  get noticed(): boolean {
    return this.state === "ready" && this.issues.length > 0 && !this.issuesKept;
  }

  /** Noticed for problems the notes still have: "Save all" waits for a decision. */
  get flagged(): boolean {
    return this.noticed && this.issues.some((issue) => issue.kind !== "corrected");
  }

  get busy(): boolean {
    return (
      this.state === "queued" ||
      this.state === "generating" ||
      this.state === "saving" ||
      !!this.rewriting ||
      this.undoing ||
      !!this.editing?.applying
    );
  }
}

type Stored = {
  kind: Kind;
  image: boolean;
  audio: boolean;
  stemType: StemType | "auto";
  thinking: Thinking | "auto";
};

function stored(): Partial<Stored> {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "{}") as Partial<Stored>;
  } catch {
    return {};
  }
}

class Session {
  rows = $state<Row[]>([]);
  selectedId = $state<string | null>(null);
  kind = $state<Kind>(stored().kind ?? "word");
  image = $state(stored().image ?? true);
  audio = $state(stored().audio ?? true);
  /** STEM: the type new rows ask for; "auto" lets the model choose. */
  // Procedure isn't offered as a chip; a choice saved before that falls back to Auto.
  stemType = $state<StemType | "auto">(
    stored().stemType === "procedure" ? "auto" : (stored().stemType ?? "auto"),
  );
  /** STEM: how hard the model thinks; "auto" leaves it to the server (medium). */
  thinking = $state<Thinking | "auto">(
    THINKING.includes(stored().thinking as Thinking) ? (stored().thinking as Thinking) : "auto",
  );
  /** False when no image model is set up: the switch is off and disabled. */
  imageAvailable = $state(true);
  /** Whether the main model can read a picture; "unknown" may be tried. */
  vision = $state<"yes" | "no" | "unknown">("unknown");
  /** Ticks every second while something generates, for elapsed times. */
  now = $state(Date.now());

  #timer: ReturnType<typeof setInterval> | null = null;
  #saving: Promise<unknown> = Promise.resolve();
  #settingsLoaded = false;

  readonly selected = $derived(this.rows.find((r) => r.id === this.selectedId) ?? null);
  /** Ready rows "Save all" would save: not those flagged for a look first. */
  readonly readyCount = $derived(this.rows.filter((r) => r.state === "ready" && !r.flagged).length);

  constructor() {
    $effect.root(() => {
      $effect(() => {
        const value: Stored = {
          kind: this.kind,
          image: this.image,
          audio: this.audio,
          stemType: this.stemType,
          thinking: this.thinking,
        };
        try {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(value));
        } catch {
          // Not persisted.
        }
      });
    });
  }

  /**
   * Learn which media can be made; the switches follow it. Runs each time the
   * page opens, since Settings may have added or removed the image model.
   */
  async load() {
    try {
      const settings = await api.settings();
      this.imageAvailable = settings.models.image !== null;
      this.vision = settings.models.text?.vision || "unknown";
      if (!this.#settingsLoaded && stored().image === undefined) {
        this.image = settings.defaults.generate_image;
      }
      this.#settingsLoaded = true;
    } catch {
      // Keep the switches as they are; a failed request shows on the row.
    }
  }

  /**
   * Queue one row per non-empty line. Returns how many were added, and the
   * lines whose brackets couldn't be read, with the first such problem.
   */
  add(input: string): { added: number; kept: string[]; error: BracketError | null } {
    const seen = new Set<string>();
    const lines = input
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line && !seen.has(line) && (seen.add(line), true));
    const kept: string[] = [];
    let error: BracketError | null = null;
    const rows: Row[] = [];
    for (const line of lines) {
      const parsed = parseLine(this.kind, line);
      if (parsed.ok) {
        rows.push(new Row(this.kind, parsed.item.text, { context: parsed.item.context }));
      } else {
        kept.push(line);
        error ??= parsed.error;
      }
    }
    if (!rows.length) return { added: 0, kept, error };
    this.rows.push(...rows);
    // Follow the new input unless the user is looking at a finished card.
    if (!this.selected || !this.selected.saveable) this.selectedId = rows[0]!.id;
    this.#pump();
    return { added: rows.length, kept, error };
  }

  /** Queue one STEM card: the whole text is one question, with its picture if any. */
  addStem(input: string, picture?: Picture): boolean {
    const text = input.trim();
    if (!text && !picture) return false;
    const type = this.stemType !== "auto" ? this.stemType : undefined;
    const thinking = this.thinking !== "auto" ? this.thinking : undefined;
    const row = new Row("stem", text, { cardType: type, thinking, picture });
    this.rows.push(row);
    // Follow the new input unless the user is looking at a finished card.
    if (!this.selected || !this.selected.saveable) this.selectedId = row.id;
    this.#pump();
    return true;
  }

  select(row: Row) {
    this.selectedId = row.id;
  }

  /** Move the selection up (-1) or down (+1) the queue. */
  step(delta: number) {
    if (!this.rows.length) return;
    const index = this.rows.findIndex((r) => r.id === this.selectedId);
    const next = index < 0 ? 0 : Math.min(Math.max(index + delta, 0), this.rows.length - 1);
    this.selectedId = this.rows[next]!.id;
  }

  regenerate(row: Row) {
    if (row.busy) return;
    row.editing?.stop();
    row.editing = null;
    row.state = "queued";
    row.failure = null;
    row.changeFailure = null;
    this.#pump();
  }

  /** Keep the notes as made, despite the problems the model saw in the line. */
  keepAsIs(row: Row) {
    row.issuesKept = true;
  }

  /**
   * Make `row`'s line again as `texts` (a corrected line, or one row per part
   * of a split line), in its place. The unsaved notes are dropped. `asTyped`
   * keeps a spelling the model corrected.
   */
  replaceLine(row: Row, texts: string[], asTyped = false) {
    const lines = texts.map((text) => text.trim()).filter(Boolean);
    if (row.busy || row.state === "saved" || !lines.length) return;
    row.editing?.stop();
    const rows = lines.map((text) => new Row(row.kind, text, { context: row.context, asTyped }));
    this.rows.splice(this.rows.indexOf(row), 1, ...rows);
    if (this.selectedId === row.id) this.selectedId = rows[0]!.id;
    this.#pump();
  }

  /** Remove a row that isn't working; its draft stays on the server until evicted. */
  remove(row: Row) {
    if (row.busy) return;
    const index = this.rows.indexOf(row);
    this.rows.splice(index, 1);
    if (this.selectedId === row.id) {
      this.selectedId = (this.rows[index] ?? this.rows[index - 1])?.id ?? null;
    }
  }

  /** Start editing the note the preview shows. */
  edit(row: Row) {
    const note = row.note;
    if (!note || !row.saveable || row.editing || row.busy) return;
    row.changeFailure = null;
    row.editing = new Editing(note);
  }

  cancelEdit(row: Row) {
    if (row.editing?.applying) return;
    row.editing?.stop();
    row.editing = null;
  }

  /** Send the edit; on success the note's preview is replaced. False if it failed. */
  async applyEdit(row: Row): Promise<boolean> {
    const editing = row.editing;
    if (!editing || editing.applying) return false;
    if (!editing.changed) {
      editing.stop();
      row.editing = null;
      return true;
    }
    editing.stop();
    editing.applying = true;
    editing.failure = null;
    try {
      this.#replace(row, await api.editDraft(editing.note.id, editing.payload()));
      if (row.editing === editing) row.editing = null;
      return true;
    } catch (error) {
      editing.failure = describe(error, "edit");
      return false;
    } finally {
      editing.applying = false;
    }
  }

  /** A changed note takes the old one's place; Anki has the old one until saved again. */
  #replace(row: Row, updated: DraftNote) {
    const index = row.notes.findIndex((n) => n.id === updated.id);
    if (index >= 0) row.notes[index] = updated;
    if (row.state === "saved") {
      row.state = "ready";
      row.saved = null;
    }
    row.failure = null;
    row.changeFailure = null;
  }

  /** STEM: have the model rewrite the selected note. False if it didn't. */
  async rewrite(row: Row, instruction: string, cardType?: StemType): Promise<boolean> {
    return this.#remake(row, false, (id) => api.rewriteDraft(id, instruction.trim(), cardType));
  }

  /** STEM: have the model fix just the formulas the preview reported. */
  async fixLatex(row: Row, errors: MathError[]): Promise<boolean> {
    if (!errors.length) return false;
    return this.#remake(row, true, (id) => api.fixLatex(id, errors));
  }

  async #remake(row: Row, fixing: boolean, call: (id: string) => Promise<DraftNote>): Promise<boolean> {
    const note = row.note;
    if (!note || note.kind !== "stem" || !row.saveable || row.busy || row.editing) return false;
    row.rewriting = Date.now();
    row.fixing = fixing;
    row.changeFailure = null;
    this.#tick();
    try {
      this.#replace(row, await call(note.id));
      return true;
    } catch (error) {
      row.changeFailure = describe(error, "rewrite");
      return false;
    } finally {
      row.rewriting = 0;
      row.fixing = false;
      this.#tick();
    }
  }

  /** Put back the note as it was before its last edit or rewrite. */
  async undo(row: Row) {
    const note = row.note;
    if (!note?.can_undo || !row.saveable || row.busy || row.editing) return;
    row.undoing = true;
    row.changeFailure = null;
    try {
      this.#replace(row, await api.undoDraft(note.id));
    } catch (error) {
      row.changeFailure = describe(error, "undo");
    } finally {
      row.undoing = false;
    }
  }

  /** Save every note of `row` (applying an open edit first); saves run one at a time. */
  async save(row: Row): Promise<void> {
    if (row.rewriting || row.undoing) return;
    if (row.editing && !(await this.applyEdit(row))) return;
    if (!row.saveable) return;
    row.issuesKept = true;
    row.state = "saving";
    row.failure = null;
    const run = this.#saving.then(async () => {
      try {
        let last: SavedNote | null = null;
        for (const note of row.notes) {
          last = await api.saveDraft(note.id);
          note.note_id = last.note_id;
        }
        row.saved = last;
        row.state = "saved";
      } catch (error) {
        row.failure = describe(error, "save");
        row.state = "ready";
      }
    });
    this.#saving = run;
    return run;
  }

  saveAllReady() {
    for (const row of this.rows) if (row.state === "ready" && !row.flagged) void this.save(row);
  }

  #pump() {
    let running = this.rows.filter((r) => r.state === "generating").length;
    for (const row of this.rows) {
      if (running >= CONCURRENCY) break;
      if (row.state !== "queued") continue;
      running += 1;
      void this.#generate(row);
    }
    this.#tick();
  }

  async #generate(row: Row) {
    row.state = "generating";
    row.startedAt = Date.now();
    row.saved = null;
    const pictures = row.kind === "word" || row.kind === "stem";
    const options = {
      image: pictures && this.image && this.imageAvailable,
      audio: this.audio,
      card_type: row.cardType,
      thinking: row.thinking,
      reference_image: row.picture && { data: row.picture.data, mime: row.picture.mime },
      context: row.context,
      as_typed: row.asTyped || undefined,
    };
    row.asked = { image: options.image, audio: options.audio };
    try {
      const made = await api.generate(row.kind, row.text, options);
      row.notes = made.notes;
      row.issues = made.issues ?? [];
      row.issuesKept = false;
      row.pick = 0;
      row.state = "ready";
    } catch (error) {
      row.failure = describe(error, "generate");
      row.state = "failed";
    }
    this.#pump();
  }

  #tick() {
    const active = this.rows.some((r) => r.state === "generating" || r.rewriting);
    if (active && !this.#timer) {
      this.now = Date.now();
      this.#timer = setInterval(() => (this.now = Date.now()), 1000);
    } else if (!active && this.#timer) {
      clearInterval(this.#timer);
      this.#timer = null;
    }
  }
}

function describe(error: unknown, during: Failure["during"]): Failure {
  if (error instanceof ApiError) return { code: error.code, detail: error.detail, during };
  return { code: "server", detail: "", during };
}

export const session = new Session();
