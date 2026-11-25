import { describe, expect, it } from "vitest";

import { parseLine } from "./brackets";

describe("parseLine", () => {
  it("takes a line without brackets as it is", () => {
    expect(parseLine("word", "  bank ")).toEqual({ ok: true, item: { text: "bank" } });
    expect(parseLine("phrase", "pick up")).toEqual({ ok: true, item: { text: "pick up" } });
  });

  it("makes the bracketed word the item and the line its context", () => {
    expect(parseLine("word", "We sat on the [bank] of the river.")).toEqual({
      ok: true,
      item: { text: "bank", context: "We sat on the bank of the river." },
    });
  });

  it("keeps the form the sentence uses", () => {
    expect(parseLine("word", "She [ran] home.")).toEqual({
      ok: true,
      item: { text: "ran", context: "She ran home." },
    });
  });

  it("joins the marked parts of a split phrase in order", () => {
    expect(parseLine("phrase", "I'll [pick] you [up] at six.")).toEqual({
      ok: true,
      item: { text: "pick … up", context: "I'll pick you up at six." },
    });
  });

  it("joins the parts of a split word too (German separable verbs)", () => {
    expect(parseLine("word", "Ich [rufe] dich morgen [an].")).toEqual({
      ok: true,
      item: { text: "rufe … an", context: "Ich rufe dich morgen an." },
    });
  });

  it("works without spaces between words", () => {
    expect(parseLine("word", "昨日[食べた]ケーキ")).toEqual({
      ok: true,
      item: { text: "食べた", context: "昨日食べたケーキ" },
    });
  });

  it("takes full-width brackets from CJK input methods", () => {
    expect(parseLine("word", "我们坐在河【岸】边。")).toEqual({
      ok: true,
      item: { text: "岸", context: "我们坐在河岸边。" },
    });
    expect(parseLine("word", "昨日［食べた］ケーキ")).toEqual({
      ok: true,
      item: { text: "食べた", context: "昨日食べたケーキ" },
    });
  });

  it("trims spaces inside the brackets", () => {
    expect(parseLine("word", "the [ bank ] of the river")).toEqual({
      ok: true,
      item: { text: "bank", context: "the  bank  of the river" },
    });
  });

  it("has no context when the whole line is bracketed", () => {
    expect(parseLine("word", "[bank]")).toEqual({ ok: true, item: { text: "bank" } });
  });

  it.each([
    ["the [bank of the river", "unclosed"],
    ["the bank] of the river", "unopened"],
    ["the [[bank]] of the river", "nested"],
    ["the [ ] of the river", "empty"],
  ])("refuses %s (%s)", (line, error) => {
    expect(parseLine("word", line)).toEqual({ ok: false, error });
    expect(parseLine("phrase", line)).toEqual({ ok: false, error });
  });

  it("leaves brackets alone for sentences and STEM", () => {
    const line = "We sat on the [bank] of the river.";
    expect(parseLine("sentence", line)).toEqual({ ok: true, item: { text: line } });
    expect(parseLine("stem", "Solve [x + 1] = 3")).toEqual({
      ok: true,
      item: { text: "Solve [x + 1] = 3" },
    });
  });
});
