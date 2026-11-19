/**
 * State for "Connect Anki": Anki Desktop through AnkiConnect (preselected
 * unless a choice was made) or built-in Anki synced with AnkiWeb, for an
 * always-on server. Once connected and writable, the note types and decks
 * are set up automatically. Shared by the wizard and Settings → Anki.
 */
import {
  api,
  ApiError,
  type AnkiBackend,
  type AnkiStatus,
  type DesktopProbe,
  type Direction,
  type NoteTypeItem,
} from "./api";

export type Action = "" | "load" | "connect" | "login" | "logout" | "sync" | "full" | "types";

/** Where an error happened decides where the step shows it. */
export type Failure = { scope: "connect" | "login" | "sync" | "types"; code: string; detail: string };

const POLL_MS = 1000;
/** How often to look again for Anki Desktop while it isn't answering. */
const DETECT_MS = 3000;

export class AnkiSetup {
  status = $state<AnkiStatus | null>(null);
  loadError = $state(false);
  choice = $state<AnkiBackend>("connect");
  /** Whether Anki Desktop answers; null until the first look. */
  desktop = $state<DesktopProbe | null>(null);

  email = $state("");
  password = $state("");
  direction = $state<Direction | "">("");

  action = $state<Action>("load");
  failure = $state<Failure | null>(null);
  noteTypes = $state<NoteTypeItem[] | null>(null);
  /**
   * Setting up the note types added fields, which Anki can only send to
   * AnkiWeb as a full upload; downloading instead would undo the setup.
   */
  upgraded = $state(false);

  private disposed = false;
  private polling = false;
  private detectTimer: ReturnType<typeof setTimeout> | undefined;

  readonly sync = $derived(this.status?.sync ?? null);
  /**
   * The selected backend was chosen and is the one in use (and, built-in,
   * it's open). Nothing is set up in Anki before the user chooses.
   */
  readonly live = $derived(
    this.status !== null &&
      this.status.chosen &&
      this.status.backend === this.choice &&
      (this.choice === "connect" || this.status.open),
  );
  /** Syncing with AnkiWeb, or a full upload/download, is running. */
  readonly syncing = $derived(
    !!this.status?.busy || this.sync?.state === "syncing" || this.sync?.state === "initializing",
  );
  readonly desktopFound = $derived(this.desktop?.version != null);
  readonly loggedIn = $derived(
    this.live && this.choice === "collection" && !!this.status?.account &&
      this.sync?.state !== "not_logged_in" && this.sync?.error !== "credentials",
  );
  readonly ready = $derived(
    this.live &&
      this.action === "" &&
      (this.choice === "connect" || !!this.status?.writable) &&
      this.noteTypes !== null &&
      this.noteTypes.every((n) => n.state === "synced"),
  );

  async load() {
    try {
      this.status = await api.anki();
    } catch {
      this.loadError = true;
      return;
    } finally {
      this.action = "";
    }
    this.choice = this.status.builtin_available ? this.status.choice : "connect";
    void this.detect();
    if (!this.live) return;
    if (this.syncing) void this.poll();
    else if (this.choice === "collection" ? this.status.writable : true) await this.listNoteTypes();
  }

  select(choice: AnkiBackend) {
    if (choice === this.choice || this.action) return;
    this.choice = choice;
    this.failure = null;
    this.noteTypes = null;
    if (choice === "connect" && !this.desktopFound && this.detectTimer === undefined) {
      void this.detect();
    }
    // Back on the backend in use: show its note types again.
    if (this.live && !this.syncing && (choice === "connect" || this.status?.writable)) {
      void this.listNoteTypes();
    }
  }

  dispose() {
    this.disposed = true;
    clearTimeout(this.detectTimer);
  }

  /**
   * Look for Anki Desktop, and keep looking every few seconds while it's
   * selected but not answering, so installing the add-on and restarting
   * Anki shows up without a click.
   */
  async detect() {
    clearTimeout(this.detectTimer);
    this.detectTimer = undefined;
    try {
      this.desktop = await api.ankiDesktop();
    } catch {
      // Server hiccup: keep the last answer.
    }
    if (this.disposed || this.desktopFound) return;
    this.detectTimer = setTimeout(() => {
      if (this.choice === "connect" && !this.live) void this.detect();
      else this.detectTimer = undefined;
    }, DETECT_MS);
  }

  private async run(action: Action, scope: Failure["scope"], work: () => Promise<void>) {
    if (this.action) return;
    this.action = action;
    this.failure = null;
    try {
      await work();
    } catch (error) {
      this.failure =
        error instanceof ApiError
          ? { scope, code: error.code, detail: error.detail }
          : { scope, code: "server", detail: "" };
    } finally {
      this.action = "";
    }
  }

  /** Open the built-in collection unless it already is. */
  private async ensureBuiltin() {
    if (this.status?.backend === "collection" && this.status.open) return;
    this.noteTypes = null;
    this.status = await api.setAnkiBackend("collection");
  }

  /** Built-in with a deployment-set account: opening it logs in and syncs. */
  async connectBuiltin() {
    await this.run("connect", "connect", async () => {
      await this.ensureBuiltin();
      if (this.status?.sync?.error === "credentials") this.status = await api.ankiSync();
    });
    await this.afterSync();
  }

  async login() {
    if (!this.email.trim() || !this.password) {
      this.failure = { scope: "login", code: "fields", detail: "" };
      return;
    }
    await this.run("login", "login", async () => {
      await this.ensureBuiltin();
      try {
        this.status = await api.ankiLogin(this.email.trim(), this.password);
      } finally {
        // Sent once; never kept, whether it worked or not.
        this.password = "";
      }
    });
    await this.afterSync();
  }

  async logout() {
    await this.run("logout", "sync", async () => {
      this.status = await api.ankiLogout();
      this.noteTypes = null;
    });
  }

  async retrySync() {
    await this.run("sync", "sync", async () => {
      this.status = await api.ankiSync();
    });
    await this.afterSync();
  }

  async fullSync(direction: Direction) {
    await this.run("full", "sync", async () => {
      this.status = await api.ankiFullSync(direction);
    });
    this.direction = "";
    if (!this.sync?.full_sync_required) this.upgraded = false;
    await this.afterSync();
  }

  async connectDesktop() {
    await this.run("connect", "connect", async () => {
      this.noteTypes = null;
      this.status = await api.setAnkiBackend("connect");
    });
    if (this.failure) {
      // The choice was saved even though Anki didn't answer.
      this.status = await api.anki().catch(() => this.status);
      void this.detect();
      return;
    }
    if (!this.desktopFound) void this.detect();
    await this.prepare();
  }

  /** After any sync-changing call: wait it out, then set up note types. */
  private async afterSync() {
    if (this.syncing) await this.poll();
    if (this.live && this.status?.writable && this.sync?.state !== "not_logged_in") {
      await this.prepare();
    }
  }

  private async poll() {
    if (this.polling) return;
    this.polling = true;
    try {
      while (!this.disposed && this.syncing) {
        await new Promise((resolve) => setTimeout(resolve, POLL_MS));
        try {
          this.status = await api.anki();
        } catch {
          // Server hiccup: keep the last status and try again.
        }
      }
    } finally {
      this.polling = false;
    }
  }

  private async listNoteTypes() {
    await this.run("types", "types", async () => {
      this.noteTypes = await api.noteTypes();
    });
    if (this.noteTypes?.some((n) => n.state !== "synced")) await this.prepare();
  }

  async prepare() {
    const blocked = !!this.sync?.full_sync_required;
    await this.run("types", "types", async () => {
      this.noteTypes = await api.prepareNoteTypes();
    });
    if (this.choice !== "collection" || !this.live) return;
    // Saving the note types ran a sync, which a field change turns into a
    // full-sync choice; the step has to show that, not the old status.
    this.status = await api.anki().catch(() => this.status);
    if (this.syncing) await this.poll();
    if (!blocked && this.sync?.full_sync_required) this.upgraded = true;
  }
}
