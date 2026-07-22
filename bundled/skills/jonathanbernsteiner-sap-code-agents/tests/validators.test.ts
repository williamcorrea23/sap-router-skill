import { describe, expect, it } from "vitest";
import { RULES, runValidator, runAllValidators, splitStatements, validateEvidence, type Rule } from "../lib/validators";

function rule(id: string): Rule {
  const r = RULES.find((r) => r.id === id);
  if (!r) throw new Error(`rule ${id} not found`);
  return r;
}

describe("splitStatements", () => {
  it("tracks line numbers across multi-line statements", () => {
    const src = "REPORT zx.\nSELECT *\n  FROM konv\n  INTO TABLE gt.\nWRITE 'done'.";
    const stmts = splitStatements(src);
    expect(stmts).toHaveLength(3);
    expect(stmts[1]).toMatchObject({ line: 2 });
    expect(stmts[1].text).toContain("FROM konv");
  });

  it("strips full-line and end-of-line comments", () => {
    const src = "* SELECT * FROM konv INTO TABLE gt.\nWRITE 'x'. \" SELECT * FROM konv\nWRITE 'y'.";
    const stmts = splitStatements(src);
    expect(stmts.map((s) => s.text).join("|")).not.toContain("konv");
  });

  it("keeps quoted periods and double quotes inside string literals", () => {
    const stmts = splitStatements(`WRITE 'a. \"b'. WRITE 'c'.`);
    expect(stmts).toHaveLength(2);
    expect(stmts[0].text).toBe(`WRITE 'a. "b'`);
  });
});

describe("every Tier-1-eligible rule has a working validator", () => {
  it("all shipped rules are tier1_eligible and covered below", () => {
    expect(RULES.filter((r) => r.tier1_eligible)).toHaveLength(12);
  });
});

// ---- table_access rules: ≥1 positive, ≥1 near-miss negative each ----

describe("konv-prcd-elements", () => {
  const r = rule("konv-prcd-elements");
  it("matches a multi-line SELECT on KONV", () => {
    const m = runValidator(r, "SELECT knumv kposn\n  FROM konv\n  INTO TABLE gt_prices\n  WHERE knumv = lv_knumv.");
    expect(m).toHaveLength(1);
    expect(m[0].detail).toBe("select on KONV");
    expect(m[0].line).toBe(1);
  });
  it("near-miss: prefixed table ZKONV and internal table lt_konv do not match", () => {
    expect(runValidator(r, "SELECT * FROM zkonv INTO TABLE gt.")).toHaveLength(0);
    expect(runValidator(r, "MODIFY lt_konv FROM ls_price. DELETE lt_konv WHERE kbetr = 0.")).toHaveLength(0);
  });
  it("near-miss: commented-out SELECT does not match", () => {
    expect(runValidator(r, "* SELECT * FROM konv INTO TABLE gt.\nWRITE 'x'.")).toHaveLength(0);
  });
});

describe("mkpf-mseg-matdoc", () => {
  const r = rule("mkpf-mseg-matdoc");
  it("matches a JOIN on MSEG and an INSERT into MKPF", () => {
    const join = runValidator(r, "SELECT g~mblnr INTO TABLE gt FROM mkpf AS g INNER JOIN mseg AS i ON g~mblnr = i~mblnr.");
    expect(join.map((m) => m.detail).sort()).toEqual(["select on MKPF", "select on MSEG"]);
    expect(runValidator(r, "INSERT mkpf FROM ls_mkpf.")).toHaveLength(1);
  });
  it("near-miss: SELECT on MATDOC or on view V_MSEG does not match", () => {
    expect(runValidator(r, "SELECT * FROM matdoc INTO TABLE gt.")).toHaveLength(0);
    expect(runValidator(r, "SELECT * FROM v_mseg INTO TABLE gt.")).toHaveLength(0);
  });
});

describe("fi-index-aggregate-acdoca", () => {
  const r = rule("fi-index-aggregate-acdoca");
  it("matches SELECT on BSID and UPDATE on GLT0", () => {
    expect(runValidator(r, "SELECT kunnr belnr INTO TABLE gt_open FROM bsid WHERE bukrs = p_bukrs.")).toHaveLength(1);
    expect(runValidator(r, "UPDATE glt0 SET hslvt = 0 WHERE ryear = '2025'.")).toHaveLength(1);
  });
  it("near-miss: BSEG (still real in S/4) and lt_bsid do not match", () => {
    expect(runValidator(r, "SELECT * FROM bseg INTO TABLE gt WHERE bukrs = p_bukrs.")).toHaveLength(0);
    expect(runValidator(r, "DELETE lt_bsid WHERE dmbtr = 0.")).toHaveLength(0);
  });
});

describe("vbuk-vbup-status-tables", () => {
  const r = rule("vbuk-vbup-status-tables");
  it("matches SELECT SINGLE on VBUK", () => {
    const m = runValidator(r, "SELECT SINGLE gbstk FROM vbuk INTO lv_gbstk WHERE vbeln = lv_vbeln.");
    expect(m).toHaveLength(1);
    expect(m[0].detail).toBe("select on VBUK");
  });
  it("near-miss: VBAK/VBAP (the replacement) do not match", () => {
    expect(runValidator(r, "SELECT SINGLE gbstk FROM vbak INTO lv WHERE vbeln = lv_vbeln.")).toHaveLength(0);
  });
});

describe("sd-rebates-vbox", () => {
  const r = rule("sd-rebates-vbox");
  it("matches DELETE FROM VBOX", () => {
    expect(runValidator(r, "DELETE FROM vbox WHERE vkorg = p_vkorg.")).toHaveLength(1);
  });
  it("near-miss: a variable named lv_vbox does not match", () => {
    expect(runValidator(r, "CLEAR lv_vbox. DELETE lt_vbox WHERE knumh IS INITIAL.")).toHaveLength(0);
  });
});

describe("co-totals-acdoca", () => {
  const r = rule("co-totals-acdoca");
  it("matches SELECT on COEP", () => {
    expect(runValidator(r, "SELECT * FROM coep INTO TABLE gt WHERE kokrs = '1000'.")).toHaveLength(1);
  });
  it("near-miss: V_COEP compatibility view does not match", () => {
    expect(runValidator(r, "SELECT * FROM v_coep INTO TABLE gt.")).toHaveLength(0);
  });
});

describe("asset-accounting-acdoca", () => {
  const r = rule("asset-accounting-acdoca");
  it("matches UPDATE on ANLC", () => {
    expect(runValidator(r, "UPDATE anlc SET kansw = lv_val WHERE anln1 = lv_anln1.")).toHaveLength(1);
  });
  it("near-miss: ANLA (still real) does not match", () => {
    expect(runValidator(r, "SELECT * FROM anla INTO TABLE gt.")).toHaveLength(0);
  });
});

describe("foreign-trade-eikp-eipo", () => {
  const r = rule("foreign-trade-eikp-eipo");
  it("matches SELECT on EIKP", () => {
    expect(runValidator(r, "SELECT * FROM eikp INTO TABLE gt WHERE exnum = lv_exnum.")).toHaveLength(1);
  });
  it("near-miss: EKKO/EKPO purchasing tables do not match", () => {
    expect(runValidator(r, "SELECT * FROM ekpo INTO TABLE gt WHERE ebeln = lv_ebeln.")).toHaveLength(0);
  });
});

// ---- call_transaction rules ----

describe("mb-transactions-migo", () => {
  const r = rule("mb-transactions-migo");
  it("matches CALL TRANSACTION 'MB01' and LEAVE TO TRANSACTION 'MB1C'", () => {
    expect(runValidator(r, "CALL TRANSACTION 'MB01' USING gt_bdc MODE 'N' UPDATE 'S'.")).toHaveLength(1);
    expect(runValidator(r, "LEAVE TO TRANSACTION 'MB1C'.")).toHaveLength(1);
  });
  it("near-miss: MIGO, an unlisted tcode, and a WRITE literal do not match", () => {
    expect(runValidator(r, "CALL TRANSACTION 'MIGO'.")).toHaveLength(0);
    expect(runValidator(r, "CALL TRANSACTION 'MB90'.")).toHaveLength(0);
    expect(runValidator(r, "WRITE 'MB01'.")).toHaveLength(0);
  });
});

describe("customer-vendor-business-partner", () => {
  const r = rule("customer-vendor-business-partner");
  it("matches CALL TRANSACTION 'XD01'", () => {
    expect(runValidator(r, "CALL TRANSACTION 'XD01' USING gt_bdc MODE 'E'.")).toHaveLength(1);
  });
  it("near-miss: transaction BP and tcode XD99 do not match", () => {
    expect(runValidator(r, "CALL TRANSACTION 'BP'. CALL TRANSACTION 'XD99'.")).toHaveLength(0);
  });
});

describe("credit-management-fscm", () => {
  const r = rule("credit-management-fscm");
  it("matches CALL TRANSACTION 'FD32'", () => {
    expect(runValidator(r, "CALL TRANSACTION 'FD32' USING gt_bdc MODE 'N'.")).toHaveLength(1);
  });
  it("near-miss: FD01 (not a credit tcode in this rule) does not match", () => {
    expect(runValidator(r, "CALL TRANSACTION 'FD01'.")).toHaveLength(0);
  });
});

// ---- function_call rule ----

describe("mm-im-classic-goods-movement-fm", () => {
  const r = rule("mm-im-classic-goods-movement-fm");
  it("matches CALL FUNCTION 'MB_CREATE_GOODS_MOVEMENT'", () => {
    expect(runValidator(r, "CALL FUNCTION 'MB_CREATE_GOODS_MOVEMENT' TABLES imseg = lt_imseg.")).toHaveLength(1);
  });
  it("near-miss: the replacement BAPI and a Z-copy do not match", () => {
    expect(runValidator(r, "CALL FUNCTION 'BAPI_GOODSMVT_CREATE' TABLES goodsmvt_item = lt_items.")).toHaveLength(0);
    expect(runValidator(r, "CALL FUNCTION 'ZMB_CREATE_GOODS_MOVEMENT'.")).toHaveLength(0);
  });
});

// ---- evidence re-validation (used by the Phase 5 report job) ----

describe("validateEvidence", () => {
  it("confirms a match only at the cited line", () => {
    const src = "REPORT z.\nSELECT * FROM konv INTO TABLE gt.\nWRITE 'x'.";
    const r = rule("konv-prcd-elements");
    expect(validateEvidence(r, src, 2)).toBe(true);
    expect(validateEvidence(r, src, 3)).toBe(false);
  });
});

describe("runAllValidators", () => {
  it("finds multiple different rules in one source", () => {
    const src = [
      "SELECT * FROM konv INTO TABLE gt.",
      "SELECT * FROM bsid INTO TABLE gt2.",
      "CALL TRANSACTION 'MB01' USING gt_bdc.",
    ].join("\n");
    const ids = new Set(runAllValidators(src).map((m) => m.ruleId));
    expect(ids).toEqual(new Set(["konv-prcd-elements", "fi-index-aggregate-acdoca", "mb-transactions-migo"]));
  });
});
