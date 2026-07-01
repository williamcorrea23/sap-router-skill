import { describe, it, expect } from "vitest";
import { MUTATING_TOOL_NAMES, AUDIT_WRAPPED_TOOLS, SELF_AUDITED_TOOLS } from "../src/tools/mutating-tools.js";
import { TOOL_CATEGORIES } from "../src/tools/tool-registry.js";

describe("MUTATING_TOOL_NAMES", () => {
  it("covers every tool in the WRITE, CREATE and DELETE categories (except pretty_print)", () => {
    const expected = [
      ...TOOL_CATEGORIES.WRITE,
      ...TOOL_CATEGORIES.CREATE,
      ...TOOL_CATEGORIES.DELETE,
    ].filter((t) => t !== "pretty_print");
    for (const tool of expected) {
      expect(MUTATING_TOOL_NAMES.has(tool), `${tool} missing from MUTATING_TOOL_NAMES`).toBe(true);
    }
  });

  it("includes the mutating tools outside those categories", () => {
    for (const tool of ["execute_abap_snippet", "abapgit_pull", "create_transport", "create_test_include", "SAPWrite"]) {
      expect(MUTATING_TOOL_NAMES.has(tool), `${tool} missing from MUTATING_TOOL_NAMES`).toBe(true);
    }
  });

  it("contains no unknown tool names (catches typos)", () => {
    const known = new Set([
      ...Object.values(TOOL_CATEGORIES).flat(),
      "create_test_include", // TEST category
    ]);
    for (const tool of MUTATING_TOOL_NAMES) {
      expect(known.has(tool), `${tool} is not a registered tool`).toBe(true);
    }
  });

  it("wrapped and self-audited sets do not overlap (no double audit lines)", () => {
    const wrapped = new Set(AUDIT_WRAPPED_TOOLS.map(([name]) => name));
    for (const tool of SELF_AUDITED_TOOLS) {
      expect(wrapped.has(tool), `${tool} would be audited twice`).toBe(false);
    }
  });
});
