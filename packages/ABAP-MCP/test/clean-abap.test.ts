import { describe, it, expect } from "vitest";
import {
  parseMarkdownSections,
  isNavigationSection,
  searchCleanAbapSections,
  CLEAN_ABAP_RULES,
} from "../src/helpers/clean-abap.js";

describe("parseMarkdownSections", () => {
  it("captures intro text before the first heading", () => {
    const sections = parseMarkdownSections("badge line\nsome intro\n\n## First\nbody");
    expect(sections[0].heading).toBe("(Intro)");
    expect(sections[0].content).toContain("some intro");
  });

  it("builds breadcrumb headings for nested h3/h4 under their h2", () => {
    const md = [
      "## Methods",
      "intro to methods",
      "### Calls",
      "intro to calls",
      "#### Prefer functional to procedural calls",
      "the rule body",
    ].join("\n");
    const sections = parseMarkdownSections(md);
    const headings = sections.map((s) => s.heading);
    expect(headings).toContain("Methods");
    expect(headings).toContain("Methods › Calls");
    expect(headings).toContain("Methods › Calls › Prefer functional to procedural calls");
  });

  it("resets the h3 breadcrumb when a new h2 starts", () => {
    const md = ["## A", "### A1", "x", "## B", "#### B-deep", "y"].join("\n");
    const headings = parseMarkdownSections(md).map((s) => s.heading);
    // B-deep must NOT inherit A1 from the previous category
    expect(headings).toContain("B › B-deep");
    expect(headings).not.toContain("A › A1 › B-deep");
  });

  it("does not emit sections that have no body content", () => {
    const sections = parseMarkdownSections("## Empty\n## Filled\nbody");
    expect(sections.find((s) => s.heading === "Empty")).toBeUndefined();
    expect(sections.find((s) => s.heading === "Filled")?.content).toBe("body");
  });
});

describe("isNavigationSection", () => {
  it("flags the table of contents and intro (case/space insensitive)", () => {
    expect(isNavigationSection("Content")).toBe(true);
    expect(isNavigationSection("  content  ")).toBe(true);
    expect(isNavigationSection("(Intro)")).toBe(true);
  });

  it("does not flag real rule headings", () => {
    expect(isNavigationSection("Methods › Calls")).toBe(false);
    expect(isNavigationSection("Names")).toBe(false);
  });
});

describe("searchCleanAbapSections", () => {
  const sections = [
    { heading: "Content", content: "link to naming link to methods link to tables" },
    { heading: "Names", content: "use descriptive naming for variables" },
    { heading: "Tables", content: "prefer INTO TABLE over SELECT loops" },
  ];

  it("excludes the navigation/ToC section even when it matches every term", () => {
    const results = searchCleanAbapSections(sections, "naming");
    expect(results.map((r) => r.heading)).not.toContain("Content");
    expect(results[0].heading).toBe("Names");
  });

  it("returns nothing when no real section matches", () => {
    expect(searchCleanAbapSections(sections, "nonexistentterm")).toHaveLength(0);
  });

  it("respects the maxResults limit", () => {
    expect(searchCleanAbapSections(sections, "naming tables", 1)).toHaveLength(1);
  });
});

describe("CLEAN_ABAP_RULES regexes", () => {
  const ruleById = (id: string) => {
    const rule = CLEAN_ABAP_RULES.find((r) => r.id === id);
    if (!rule) throw new Error(`rule ${id} not found`);
    return rule;
  };

  it("flags Hungarian notation in DATA declarations", () => {
    expect(ruleById("HUNGARIAN_NOTATION").pattern.test("  DATA lv_count TYPE i.")).toBe(true);
    expect(ruleById("HUNGARIAN_NOTATION").pattern.test("  DATA customer TYPE i.")).toBe(false);
  });

  it("flags obsolete MOVE ... TO but not modern assignment", () => {
    expect(ruleById("MOVE_STATEMENT").pattern.test("MOVE a TO b.")).toBe(true);
    expect(ruleById("MOVE_STATEMENT").pattern.test("b = a.")).toBe(false);
  });

  it("flags CONCATENATE statements", () => {
    expect(ruleById("CONCATENATE_STATEMENT").pattern.test("CONCATENATE a b INTO c.")).toBe(true);
  });

  it("flags SELECT ... ENDSELECT loops across lines", () => {
    const src = "SELECT * FROM t INTO wa.\n  WRITE wa.\nENDSELECT.";
    expect(ruleById("SELECT_ENDSELECT").pattern.test(src)).toBe(true);
  });

  it("flags CALL METHOD but not a functional call", () => {
    expect(ruleById("CALL_METHOD").pattern.test("CALL METHOD obj->do( ).")).toBe(true);
    expect(ruleById("CALL_METHOD").pattern.test("obj->do( ).")).toBe(false);
  });
});
