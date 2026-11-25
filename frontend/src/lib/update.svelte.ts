import { api, type UpdateStatus } from "./api";
import { showMarker } from "./update";

const SEEN_KEY = "ankinote.updateSeen";

function loadSeen(): string | null {
  try {
    return localStorage.getItem(SEEN_KEY);
  } catch {
    return null;
  }
}

/** The server's update check, asked once per page load and shared. */
class Update {
  status = $state<UpdateStatus | null>(null);
  #seen = $state<string | null>(loadSeen());

  marked = $derived(showMarker(this.status, this.#seen));

  constructor() {
    // No answer (an older server, offline) just means no marker.
    api.update().then(
      (s) => (this.status = s),
      () => {},
    );
  }

  /** About has shown the new version: drop the top bar's marker for it. */
  markSeen() {
    const latest = this.status?.available ? this.status.latest : null;
    if (!latest || latest === this.#seen) return;
    this.#seen = latest;
    try {
      localStorage.setItem(SEEN_KEY, latest);
    } catch {
      // Storage blocked: the marker comes back on the next load.
    }
  }
}

export const update = new Update();
