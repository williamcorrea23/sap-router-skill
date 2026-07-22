/**
 * Dependency edge classification — general-purpose tests with inline ABAP
 * fixtures, deliberately NOT tied to the seeded systems: they pin the
 * contract for ANY future ingested repo.
 *
 * The principle under test: an edge's target is classified at extraction time
 * (internal / workspace / external) and rendered by that class — never
 * guessed at render time from "does an object with this name exist?".
 */
import { describe, expect, it } from "vitest";
import { extractWorkspace, type ExtractedObject } from "../lib/parser/extract";
import { classifyEdgeTarget, type EdgeTargetKind } from "../lib/ingest/pipeline";
import {
  buildObjectDiagram,
  edgesToMermaid,
  isSapStandardName,
  type DiagramEdge,
} from "../lib/diagram";
import { splitStoredSource } from "../scripts/backfill-target-kind";

function extractOne(path: string, contents: string, extra: { path: string; contents: string }[] = []) {
  const result = extractWorkspace([{ path, contents }, ...extra]);
  const obj = result.objects.find((o) => o.files.includes(path));
  expect(obj).toBeDefined();
  return { result, obj: obj as ExtractedObject };
}

/** classify like insertEdges does, resolving against the given workspace names */
function classify(obj: ExtractedObject, workspaceNames: Set<string>) {
  const out = new Map<string, EdgeTargetKind>();
  for (const call of obj.calls) {
    const kind = classifyEdgeTarget(call, workspaceNames.has(call.target) ? "some-id" : null);
    if (call.kind === "interface" && kind === "external") continue; // DDIC noise, dropped
    out.set(`${call.kind}|${call.target}`, kind);
  }
  return out;
}

describe("edge target classification (extraction layer)", () => {
  it("1: PERFORM targets with same-source FORMs are internal, never external", () => {
    const { obj } = extractOne(
      "ztest_report.prog.abap",
      `REPORT ztest_report.
START-OF-SELECTION.
  PERFORM load_data.
  PERFORM write_output.
FORM load_data.
  WRITE 'x'.
ENDFORM.
FORM write_output.
  WRITE 'y'.
ENDFORM.
`
    );
    const kinds = classify(obj, new Set());
    expect(kinds.get("perform|LOAD_DATA")).toBe("internal");
    expect(kinds.get("perform|WRITE_OUTPUT")).toBe("internal");
    expect([...kinds.values()]).not.toContain("external");
  });

  it("ambiguity rule: a same-source FORM wins over an identically named workspace object", () => {
    const { obj } = extractOne(
      "ztest_report.prog.abap",
      `REPORT ztest_report.
START-OF-SELECTION.
  PERFORM zutil_helper.
FORM zutil_helper.
ENDFORM.
`
    );
    // an object named ZUTIL_HELPER exists in the workspace — local still wins
    const kinds = classify(obj, new Set(["ZUTIL_HELPER"]));
    expect(kinds.get("perform|ZUTIL_HELPER")).toBe("internal");
  });

  it("2: a call to a Z-function module ingested in the workspace is 'workspace'", () => {
    const { obj } = extractOne(
      "ztest_caller.prog.abap",
      `REPORT ztest_caller.
START-OF-SELECTION.
  CALL FUNCTION 'Z_GET_STOCK'.
`
    );
    const kinds = classify(obj, new Set(["Z_GET_STOCK"]));
    expect(kinds.get("function|Z_GET_STOCK")).toBe("workspace");
  });

  it("3: a call to a non-ingested BAPI is 'external' and labeled SAP standard", () => {
    const { obj } = extractOne(
      "ztest_bapi.prog.abap",
      `REPORT ztest_bapi.
START-OF-SELECTION.
  CALL FUNCTION 'BAPI_GOODSMVT_CREATE'.
`
    );
    const kinds = classify(obj, new Set());
    expect(kinds.get("function|BAPI_GOODSMVT_CREATE")).toBe("external");
    expect(isSapStandardName("BAPI_GOODSMVT_CREATE", "function")).toBe(true);
    // non-customer-namespace function modules are SAP standard...
    expect(isSapStandardName("GUI_DOWNLOAD", "function")).toBe(true);
    // ...customer-namespace names are not
    expect(isSapStandardName("Z_MISSING_FM", "function")).toBe(false);
  });

  it("5: a local helper class is internal; another ingested class is workspace", () => {
    const { obj } = extractOne(
      "zcl_service.clas.abap",
      `CLASS zcl_service DEFINITION PUBLIC CREATE PUBLIC.
  PUBLIC SECTION.
    METHODS run.
ENDCLASS.
CLASS lcl_helper DEFINITION.
  PUBLIC SECTION.
    METHODS assist.
ENDCLASS.
CLASS lcl_helper IMPLEMENTATION.
  METHOD assist.
  ENDMETHOD.
ENDCLASS.
CLASS zcl_service IMPLEMENTATION.
  METHOD run.
    DATA(lo_helper) = NEW lcl_helper( ).
    lo_helper->assist( ).
    DATA(lo_reader) = NEW zcl_other_reader( ).
  ENDMETHOD.
ENDCLASS.
`
    );
    const kinds = classify(obj, new Set(["ZCL_OTHER_READER"]));
    expect(kinds.get("class|LCL_HELPER")).toBe("internal");
    expect(kinds.get("class|ZCL_OTHER_READER")).toBe("workspace");
  });
});

describe("diagram rendering (per target_kind)", () => {
  const FOCUS = "ZTEST_REPORT";

  it("never emits the '(not in workspace)' label for any edge class", () => {
    const edges: DiagramEdge[] = [
      { from: FOCUS, to: "ZCL_A", kind: "class", targetKind: "workspace" },
      { from: FOCUS, to: "BAPI_X", kind: "function", targetKind: "external" },
      { from: FOCUS, to: "LOAD_DATA", kind: "perform", targetKind: "internal" },
    ];
    expect(edgesToMermaid(edges, FOCUS)).not.toContain("not in workspace");
    expect(buildObjectDiagram(FOCUS, edges).mermaid).not.toContain("not in workspace");
  });

  it("labels external nodes 'SAP standard' or 'external' by name pattern", () => {
    const mermaid = edgesToMermaid(
      [
        { from: FOCUS, to: "BAPI_GOODSMVT_CREATE", kind: "function", targetKind: "external" },
        { from: FOCUS, to: "Z_MISSING_FM", kind: "function", targetKind: "external" },
      ],
      FOCUS
    );
    expect(mermaid).toContain("BAPI_GOODSMVT_CREATE (SAP standard)");
    expect(mermaid).toContain("Z_MISSING_FM (external)");
  });

  it("omits internal routines when real dependencies exist", () => {
    const diagram = buildObjectDiagram(FOCUS, [
      { from: FOCUS, to: "ZCL_A", kind: "class", targetKind: "workspace" },
      { from: FOCUS, to: "LOAD_DATA", kind: "perform", targetKind: "internal" },
    ]);
    expect(diagram.internalOnly).toBe(false);
    expect(diagram.mermaid).toContain("ZCL_A");
    expect(diagram.mermaid).not.toContain("LOAD_DATA");
  });

  it("4: an object with ONLY internal FORMs renders the internal fallback, never an empty box", () => {
    const diagram = buildObjectDiagram(FOCUS, [
      { from: FOCUS, to: "LOAD_ORDERS", kind: "perform", targetKind: "internal" },
      { from: FOCUS, to: "WRITE_MARGINS", kind: "perform", targetKind: "internal" },
    ]);
    expect(diagram.internalOnly).toBe(true);
    expect(diagram.mermaid).toContain("LOAD_ORDERS (internal routine)");
    expect(diagram.mermaid).toContain("WRITE_MARGINS (internal routine)");
    expect(diagram.mermaid).not.toContain("not in workspace");
  });
});

describe("6: mixed object end-to-end (the daily-movement pattern)", () => {
  it("shows exactly the workspace class and table as dependencies; FORMs excluded", () => {
    const { obj } = extractOne(
      "zmix_report.prog.abap",
      `REPORT zmix_report.
DATA gt_log TYPE STANDARD TABLE OF zmy_log_table WITH DEFAULT KEY.
START-OF-SELECTION.
  PERFORM load.
  PERFORM reconcile.
FORM load.
  SELECT * FROM zmy_log_table INTO TABLE gt_log.
ENDFORM.
FORM reconcile.
  DATA lo_reader TYPE REF TO zcl_my_reader.
  CREATE OBJECT lo_reader.
ENDFORM.
`
    );
    const workspaceNames = new Set(["ZCL_MY_READER", "ZMY_LOG_TABLE"]);
    const kinds = classify(obj, workspaceNames);
    const edges: DiagramEdge[] = [...kinds.entries()].map(([key, targetKind]) => {
      const [kind, target] = key.split("|");
      return { from: "ZMIX_REPORT", to: target, kind, targetKind };
    });
    const diagram = buildObjectDiagram("ZMIX_REPORT", edges);
    expect(diagram.internalOnly).toBe(false);
    expect(diagram.mermaid).toContain("ZCL_MY_READER");
    expect(diagram.mermaid).toContain("ZMY_LOG_TABLE");
    expect(diagram.mermaid).not.toContain("LOAD");
    expect(diagram.mermaid).not.toContain("RECONCILE");
    expect(diagram.mermaid).not.toContain("not in workspace");
    // the table access itself stays in table_accesses (its own edge class)
    expect(obj.tableAccesses.map((t) => t.table)).toContain("ZMY_LOG_TABLE");
  });
});

describe("backfill source splitting", () => {
  it("reconstructs the per-file inputs the seeder concatenated", () => {
    const fileA = "REPORT zbf_a.\nSTART-OF-SELECTION.\n  PERFORM go.\nFORM go.\nENDFORM.\n";
    const stored = `* ===== zbf_a.prog.abap =====\n${fileA}`;
    const inputs = splitStoredSource(stored);
    expect(inputs).toHaveLength(1);
    expect(inputs[0].path).toBe("zbf_a.prog.abap");
    // re-extraction over the reconstructed input classifies like the original
    const result = extractWorkspace(inputs);
    const calls = result.objects.flatMap((o) => o.calls);
    expect(calls.find((c) => c.target === "GO")?.internal).toBe(true);
  });
});
