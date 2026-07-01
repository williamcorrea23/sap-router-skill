import { describe, it, expect } from "vitest";
import { truncateContent, normalizeUrlForMatch, pickBestResult } from "../src/helpers/web.js";

describe("truncateContent", () => {
  it("returns short content unchanged", () => {
    expect(truncateContent("hello", 100)).toBe("hello");
  });

  it("returns content of exactly maxLen unchanged", () => {
    const s = "x".repeat(50);
    expect(truncateContent(s, 50)).toBe(s);
  });

  it("truncates long content and appends the marker", () => {
    const s = "a".repeat(200);
    const out = truncateContent(s, 50);
    expect(out.startsWith("a".repeat(50))).toBe(true);
    expect(out).toContain("Inhalt gekürzt: 200 → 50 Zeichen");
  });
});

describe("normalizeUrlForMatch", () => {
  it("ignores protocol differences", () => {
    expect(normalizeUrlForMatch("http://help.sap.com/docs/x"))
      .toBe(normalizeUrlForMatch("https://help.sap.com/docs/x"));
  });

  it("ignores www prefix, trailing slash, query and fragment", () => {
    expect(normalizeUrlForMatch("https://www.example.com/page/?locale=en#top"))
      .toBe(normalizeUrlForMatch("https://example.com/page"));
  });

  it("is case-insensitive on the host but not the path", () => {
    expect(normalizeUrlForMatch("https://EXAMPLE.com/Page"))
      .toBe("example.com/Page");
  });

  it("falls back to trimmed lowercase for unparseable input", () => {
    expect(normalizeUrlForMatch(" not-a-url/ ")).toBe("not-a-url");
  });
});

describe("pickBestResult", () => {
  const results = [
    { url: "https://example.com/other", title: "other" },
    { url: "http://www.example.com/page/", title: "wanted" },
  ];

  it("prefers the normalized exact match over the first result", () => {
    expect(pickBestResult("https://example.com/page?x=1", results)?.title).toBe("wanted");
  });

  it("falls back to the first result when nothing matches", () => {
    expect(pickBestResult("https://example.com/missing", results)?.title).toBe("other");
  });

  it("returns undefined for empty or missing results", () => {
    expect(pickBestResult("https://example.com", [])).toBeUndefined();
    expect(pickBestResult("https://example.com", undefined)).toBeUndefined();
  });
});
