/**
 * Change Order 01 unit tests: A1 claim-evidence check, A2 suppression
 * evaluation, A3 finding dedupe. Pure functions — no DB, no LLM.
 */
import { describe, expect, it } from "vitest";
import { checkClaim } from "../lib/report/claims";
import { evaluateSuppression, type SuppressionRule } from "../lib/report/suppress";
import { dedupeFindings, type DraftFinding } from "../lib/report/dedupe";

describe("A1 — checkClaim", () => {
  it("accepts a table claim whose token appears in the evidence", () => {
    const c = checkClaim("SELECT on MKPF — material documents", "SELECT SINGLE * FROM mkpf INTO ls_mkpf.");
    expect(c.supported).toBe(true);
  });

  it("rejects a table claim absent from the evidence", () => {
    const c = checkClaim("Direct read of VBUK status table", "SELECT * FROM vbak INTO TABLE lt_vbak.");
    expect(c.supported).toBe(false);
    expect(c.missing).toContain("VBUK");
  });

  it("accepts successor-table titles when the offending table is present", () => {
    const c = checkClaim(
      "KONV replaced by PRCD_ELEMENTS in S/4HANA",
      "SELECT kbetr FROM konv INTO lv_kbetr WHERE knumv = lv_knumv."
    );
    expect(c.supported).toBe(true);
  });

  it("accepts a length claim whose number appears in the evidence", () => {
    const c = checkClaim(
      "Hard-coded 18-character material number length",
      "TYPES ty_matnr_legacy TYPE c LENGTH 18."
    );
    expect(c.supported).toBe(true);
  });

  it("rejects a length claim citing a line without that length", () => {
    const c = checkClaim(
      "Amount field length 15 assumption",
      "DATA lv_amount TYPE p DECIMALS 2."
    );
    expect(c.supported).toBe(false);
    expect(c.missing).toContain("15");
  });

  it("does not extract tokens from generic vocabulary (S/4HANA, CHAR, SELECT)", () => {
    const c = checkClaim("SELECT with CHAR field breaks in S/4HANA", "WRITE lv_x.");
    expect(c.claimed).toEqual([]);
    expect(c.supported).toBe(true);
  });

  it("checks substrings case-insensitively (MATNR inside ty_matnr_legacy)", () => {
    const c = checkClaim("MATNR truncation", "lv_work = lv_matnr_legacy+0(18).");
    expect(c.supported).toBe(true);
  });
});

describe("A2 — evaluateSuppression", () => {
  const rules: SuppressionRule[] = [
    {
      id: "werks-field-length",
      kind: "regex",
      pattern:
        "(\\bwerks\\b|\\bplant\\b[^.]*\\bfield\\b)[^.]*\\b(length|char|size|width)\\b|\\b(length|char|size|width)\\b[^.]*\\bwerks\\b",
      category: null,
      reason: "WERKS is CHAR 4 in ECC and S/4HANA alike.",
    },
    {
      id: "non-matnr-field-length",
      kind: "category",
      pattern: null,
      category: "non-matnr-field-length",
      reason: "Length claims only actionable for MATNR unless tied to a seeded rule.",
    },
  ];

  it("suppresses WERKS field-length observations", () => {
    const hit = evaluateSuppression(rules, {
      title: "WERKS field length assumption",
      detail: "The code assumes plant WERKS is CHAR 4.",
      ruleId: null,
    });
    expect(hit?.ruleId).toBe("werks-field-length");
  });

  it("suppresses non-MATNR length claims not tied to a rule", () => {
    const hit = evaluateSuppression(rules, {
      title: "Amount field length extension",
      detail: "Amount fields are extended in S/4HANA; this declaration may truncate.",
      ruleId: null,
    });
    expect(hit?.ruleId).toBe("non-matnr-field-length");
  });

  it("keeps MATNR length findings (the hold-out class)", () => {
    const hit = evaluateSuppression(rules, {
      title: "Hard-coded 18-char material number length",
      detail: "TYPES ty_matnr_legacy TYPE c LENGTH 18 truncates 40-char MATNR values.",
      ruleId: null,
    });
    expect(hit).toBeNull();
  });

  it("keeps length claims tied to a seeded rule", () => {
    const hit = evaluateSuppression(rules, {
      title: "Condition amount length changed",
      detail: "KBETR length changes with PRCD_ELEMENTS.",
      ruleId: "konv-prcd-elements",
    });
    expect(hit).toBeNull();
  });

  it("keeps ordinary findings untouched", () => {
    const hit = evaluateSuppression(rules, {
      title: "SELECT on VBUK — status tables eliminated",
      detail: "VBUK no longer filled for new documents.",
      ruleId: "vbuk-vbup-status-tables",
    });
    expect(hit).toBeNull();
  });
});

describe("A3 — dedupeFindings", () => {
  const base: DraftFinding = {
    objectId: "obj-1",
    ruleId: "mkpf-mseg-matdoc",
    tier: 1,
    title: "SELECT on MKPF — Material documents",
    detail: "detail",
    file: "zprog.abap",
    line: 42,
    evidence: "SELECT ... FROM mkpf JOIN mseg ...",
    validator: "mkpf-mseg-matdoc",
    validatorPassed: true,
    op: "select",
    token: "MKPF",
    ruleTitle: "Material documents: MKPF/MSEG replaced by MATDOC",
    ruleDescription: "MKPF and MSEG are replaced by MATDOC.",
  };

  it("merges same object + line + rule family into one finding listing all tables", () => {
    const out = dedupeFindings([base, { ...base, token: "MSEG" }]);
    expect(out).toHaveLength(1);
    expect(out[0].title).toContain("MKPF, MSEG");
    expect(out[0].tier).toBe(1);
    expect(out[0].validatorPassed).toBe(true);
  });

  it("a merged line is only Tier 1 when every member was confirmed", () => {
    const out = dedupeFindings([base, { ...base, token: "MSEG", tier: 2, validatorPassed: false }]);
    expect(out).toHaveLength(1);
    expect(out[0].tier).toBe(2);
  });

  it("does not merge different rules on the same line", () => {
    const other = { ...base, ruleId: "fi-index-aggregate-acdoca", validator: "fi-index-aggregate-acdoca", token: "BSIS" };
    expect(dedupeFindings([base, other])).toHaveLength(2);
  });

  it("does not merge the same rule on different lines", () => {
    expect(dedupeFindings([base, { ...base, line: 99 }])).toHaveLength(2);
  });

  it("drops same-line LLM rewordings instead of appending them to the detail", () => {
    const llm: DraftFinding = {
      ...base,
      ruleId: null,
      validator: null,
      validatorPassed: null,
      op: undefined,
      token: undefined,
      tier: 2,
      title: "Legacy MATNR length",
    };
    const out = dedupeFindings([llm, { ...llm, title: "18-char material number" }]);
    expect(out).toHaveLength(1);
    expect(out[0].title).toBe("Legacy MATNR length"); // first occurrence wins
    expect(out[0].detail).toBe("detail");
    expect(out[0].detail).not.toContain("Also reported for this line");
  });
});
