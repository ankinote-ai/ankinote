import { describe, expect, it } from "vitest";

import type { UpdateStatus } from "./api";
import { showMarker } from "./update";

const status = (over: Partial<UpdateStatus> = {}): UpdateStatus => ({
  enabled: true,
  current: "1.2.3",
  latest: "1.3.0",
  available: true,
  major: false,
  install: "uvx",
  commands: [{ install: "uvx", command: "uvx --from ankinote-ai@latest ankinote-web" }],
  notes_url: "https://github.com/ankinote-ai/ankinote/releases/tag/v1.3.0",
  ...over,
});

describe("showMarker", () => {
  it("marks a new version that hasn't been seen", () => {
    expect(showMarker(status(), null)).toBe(true);
  });

  it("stays away once About has shown that version", () => {
    expect(showMarker(status(), "1.3.0")).toBe(false);
  });

  it("comes back for the next version", () => {
    expect(showMarker(status({ latest: "1.4.0" }), "1.3.0")).toBe(true);
  });

  it("shows nothing when up to date, switched off or not checked yet", () => {
    expect(showMarker(status({ available: false }), null)).toBe(false);
    expect(showMarker(status({ enabled: false, available: false, latest: null }), null)).toBe(false);
    expect(showMarker(null, null)).toBe(false);
  });
});
