import type { UpdateStatus } from "./api";

/** The top bar marks a new version until About has shown it. */
export function showMarker(status: UpdateStatus | null, seen: string | null): boolean {
  return !!status?.available && status.latest !== seen;
}
