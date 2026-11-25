/**
 * A line on the Generate page, read for a word or phrase met in a sentence:
 * `We sat on the [bank] of the river.` makes a card for "bank" in the sense
 * that sentence uses. Several marked parts are one item, joined in order with
 * " … " (`I'll [pick] you [up] at six.` → "pick … up"; German `Ich [rufe]
 * dich [an].` → "rufe … an"); the model gives the dictionary form.
 *
 * Full-width brackets count too, since CJK input methods type `【` or `［`
 * for `[`. Sentences and STEM questions are taken as they are.
 */
import type { Kind } from "./api";

export type Item = {
  text: string;
  /** The sentence the item was met in, brackets removed. */
  context?: string;
};

export type BracketError = "unclosed" | "unopened" | "nested" | "empty";

export type Parsed = { ok: true; item: Item } | { ok: false; error: BracketError };

const OPEN = new Set(["[", "［", "【"]);
const CLOSE = new Set(["]", "］", "】"]);

export const JOINER = " … ";

/** Whether lines of this kind may mark an item in its sentence. */
export function takesContext(kind: Kind): boolean {
  return kind === "word" || kind === "phrase";
}

export function parseLine(kind: Kind, line: string): Parsed {
  const text = line.trim();
  if (!takesContext(kind)) return { ok: true, item: { text } };

  const parts: string[] = [];
  let context = "";
  let part: string | null = null;
  for (const char of text) {
    if (OPEN.has(char)) {
      if (part !== null) return { ok: false, error: "nested" };
      part = "";
    } else if (CLOSE.has(char)) {
      if (part === null) return { ok: false, error: "unopened" };
      if (!part.trim()) return { ok: false, error: "empty" };
      parts.push(part.trim());
      part = null;
    } else {
      context += char;
      if (part !== null) part += char;
    }
  }
  if (part !== null) return { ok: false, error: "unclosed" };
  if (!parts.length) return { ok: true, item: { text } };

  const item = parts.join(JOINER);
  context = context.trim();
  return { ok: true, item: context === item ? { text: item } : { text: item, context } };
}
