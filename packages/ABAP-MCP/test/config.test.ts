import { describe, it, expect } from "vitest";
import { parseBoolean } from "../src/config.js";

describe("parseBoolean", () => {
  it("returns the fallback for an unset value", () => {
    expect(parseBoolean(undefined)).toBe(false);
    expect(parseBoolean(undefined, true)).toBe(true);
  });

  it("returns the fallback for an empty/whitespace value", () => {
    expect(parseBoolean("", true)).toBe(true);
    expect(parseBoolean("   ", true)).toBe(true);
    expect(parseBoolean("")).toBe(false);
  });

  it("accepts truthy spellings regardless of case/whitespace", () => {
    for (const v of ["true", "TRUE", " True ", "1", "yes", "YES", "on", "ON"]) {
      expect(parseBoolean(v), `expected ${JSON.stringify(v)} to be true`).toBe(true);
    }
  });

  it("treats anything else as false", () => {
    for (const v of ["false", "FALSE", "0", "no", "off", "enabled", "y"]) {
      expect(parseBoolean(v), `expected ${JSON.stringify(v)} to be false`).toBe(false);
    }
  });
});
