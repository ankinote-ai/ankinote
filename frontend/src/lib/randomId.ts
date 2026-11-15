/**
 * A random 128-bit id as 32 hex digits. Unlike `crypto.randomUUID`, which
 * only exists in secure contexts, this works when the app is opened over
 * plain HTTP on a LAN or Tailscale address, not just localhost.
 */
export function randomId(): string {
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
}
