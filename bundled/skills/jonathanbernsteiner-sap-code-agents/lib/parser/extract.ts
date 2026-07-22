/**
 * abaplint-based extraction shared by the parse proof (Phase 1) and the
 * workspace seeder (Phase 2).
 *
 * Everything here is deterministic: objects, call references and table
 * accesses come straight out of the abaplint syntax tree, with the source
 * line recorded as evidence. No LLM involvement.
 */
import {
  ABAPObject,
  Expressions,
  MemoryFile,
  Registry,
  Statements,
  Unknown,
} from "@abaplint/core";

export interface ParseInput {
  /** repo-relative path, e.g. src/zcl_foo.clas.abap */
  path: string;
  contents: string;
}

export interface ParseErrorInfo {
  file: string;
  line: number;
  snippet: string;
}

export interface CallRef {
  /**
   * function  = CALL FUNCTION 'NAME'
   * perform   = PERFORM name
   * class     = static/instance reference to a class name
   * interface = reference to an interface/type name (resolved later against
   *             known workspace objects; unresolvable ones are dropped from
   *             the edge list, never guessed)
   */
  kind: "function" | "perform" | "class" | "interface";
  target: string;
  file: string;
  line: number;
  /**
   * true when the target is defined inside the same compilation unit (a FORM
   * in the same program, a local class, a function module of the same group).
   * ABAP resolves locally first, so such a call is never an external
   * dependency — even if an identically named object exists elsewhere.
   */
  internal: boolean;
}

export interface TableAccess {
  op: "select" | "insert" | "update" | "modify" | "delete";
  table: string;
  /** true when the table name is dynamic, e.g. SELECT ... FROM (lv_tab) */
  dynamic: boolean;
  file: string;
  line: number;
  /** verbatim source line — the evidence for this access */
  evidence: string;
}

export interface ExtractedObject {
  name: string;
  type: string;
  files: string[];
  parseStatus: "ok" | "failed";
  parseErrors: ParseErrorInfo[];
  /** concatenated source of all files belonging to the object */
  source: string;
  calls: CallRef[];
  tableAccesses: TableAccess[];
}

export interface ExtractResult {
  objects: ExtractedObject[];
  /** input files that abaplint did not attach to any object */
  unattachedFiles: { path: string; reason: string }[];
  totals: {
    inputFiles: number;
    attachedFiles: number;
    objects: number;
    objectsOk: number;
    objectsFailed: number;
  };
}

const TABLE_OP_MAP: [unknown, TableAccess["op"]][] = [
  [Statements.Select, "select"],
  [Statements.SelectLoop, "select"],
  [Statements.InsertDatabase, "insert"],
  [Statements.UpdateDatabase, "update"],
  [Statements.ModifyDatabase, "modify"],
  [Statements.DeleteDatabase, "delete"],
];

/** Parse a set of ABAP files and extract objects, calls and table accesses. */
export function extractWorkspace(inputs: ParseInput[]): ExtractResult {
  const reg = new Registry();
  for (const input of inputs) {
    reg.addFile(new MemoryFile(input.path, input.contents));
  }
  reg.parse();

  const sourceByPath = new Map(inputs.map((i) => [i.path, i.contents]));
  const attached = new Set<string>();
  const objects: ExtractedObject[] = [];

  for (const obj of reg.getObjects()) {
    if (!(obj instanceof ABAPObject)) {
      // non-ABAP artifacts (e.g. TABL definitions from .tabl.xml) — keep them
      // as objects so table accesses / where-used can resolve against them
      const files: string[] = [];
      let source = "";
      for (const f of obj.getFiles()) {
        attached.add(f.getFilename());
        files.push(f.getFilename());
        source += (source ? "\n\n" : "") + (sourceByPath.get(f.getFilename()) ?? f.getRaw());
      }
      objects.push({
        name: obj.getName(),
        type: obj.getType(),
        files,
        parseStatus: "ok",
        parseErrors: [],
        source,
        calls: [],
        tableAccesses: [],
      });
      continue;
    }

    const extracted: ExtractedObject = {
      name: obj.getName(),
      type: obj.getType(),
      files: [],
      parseStatus: "ok",
      parseErrors: [],
      source: "",
      calls: [],
      tableAccesses: [],
    };
    // names DEFINED in this compilation unit: FORMs, function modules of the
    // group, local classes/interfaces — collected alongside the calls, then
    // used to mark same-unit calls as internal (local resolution wins)
    const definedNames = new Set<string>();

    for (const file of obj.getABAPFiles()) {
      const path = file.getFilename();
      attached.add(path);
      extracted.files.push(path);
      const raw = sourceByPath.get(path) ?? file.getRaw();
      const lines = raw.split("\n");
      extracted.source += (extracted.source ? "\n\n" : "") + `* ===== ${path} =====\n` + raw;

      for (const statement of file.getStatements()) {
        const stmt = statement.get();
        const row = statement.getFirstToken().getStart().getRow();

        if (stmt instanceof Unknown) {
          extracted.parseStatus = "failed";
          if (extracted.parseErrors.length < 5) {
            extracted.parseErrors.push({
              file: path,
              line: row,
              snippet: statement.concatTokens().slice(0, 120),
            });
          }
          continue;
        }

        // ---- table accesses ----
        for (const [cls, op] of TABLE_OP_MAP) {
          if (stmt instanceof (cls as never)) {
            for (const expr of statement.findAllExpressions(Expressions.DatabaseTable)) {
              const tokens = expr.concatTokens();
              const dynamic = tokens.includes("(");
              extracted.tableAccesses.push({
                op,
                table: dynamic ? tokens : tokens.toUpperCase(),
                dynamic,
                file: path,
                line: expr.getFirstToken().getStart().getRow(),
                evidence: (lines[expr.getFirstToken().getStart().getRow() - 1] ?? "").trim(),
              });
            }
          }
        }

        // ---- definitions (for internal-call classification) ----
        if (stmt instanceof Statements.Form) {
          const nameExpr = statement.findFirstExpression(Expressions.FormName);
          if (nameExpr) definedNames.add(nameExpr.concatTokens().toUpperCase());
        }
        if (stmt instanceof Statements.FunctionModule) {
          const nameExpr = statement.findFirstExpression(Expressions.Field);
          if (nameExpr) definedNames.add(nameExpr.concatTokens().toUpperCase());
        }
        if (stmt instanceof Statements.ClassDefinition || stmt instanceof Statements.ClassImplementation) {
          const nameExpr = statement.findFirstExpression(Expressions.ClassName);
          if (nameExpr) definedNames.add(nameExpr.concatTokens().toUpperCase());
        }
        if (stmt instanceof Statements.Interface) {
          const nameExpr = statement.findFirstExpression(Expressions.InterfaceName);
          if (nameExpr) definedNames.add(nameExpr.concatTokens().toUpperCase());
        }

        // ---- calls ----
        if (stmt instanceof Statements.CallFunction) {
          const nameExpr = statement.findFirstExpression(Expressions.FunctionName);
          if (nameExpr) {
            const tokens = nameExpr.concatTokens();
            const quoted = tokens.match(/^'(.*)'$/);
            extracted.calls.push({
              internal: false,
              kind: "function",
              // dynamic function names stay verbatim (marked unresolved later)
              target: quoted ? quoted[1].toUpperCase() : tokens,
              file: path,
              line: row,
            });
          }
        }
        if (stmt instanceof Statements.Perform) {
          const nameExpr = statement.findFirstExpression(Expressions.FormName);
          if (nameExpr) {
            extracted.calls.push({
              internal: false,
              kind: "perform",
              target: nameExpr.concatTokens().toUpperCase(),
              file: path,
              line: row,
            });
          }
        }
        for (const expr of statement.findAllExpressions(Expressions.ClassName)) {
          extracted.calls.push({
            internal: false,
            kind: "class",
            target: expr.concatTokens().toUpperCase(),
            file: path,
            line: expr.getFirstToken().getStart().getRow(),
          });
        }
        // TypeNames inside NEW ...( ) are instantiations — class references
        const newObjectTypes = new Set<string>();
        for (const newExpr of statement.findAllExpressions(Expressions.NewObject)) {
          const typeExpr = newExpr.findFirstExpression(Expressions.TypeName);
          if (typeExpr) {
            const pos = typeExpr.getFirstToken().getStart();
            newObjectTypes.add(`${pos.getRow()}:${pos.getCol()}`);
            extracted.calls.push({
              internal: false,
              kind: "class",
              target: typeExpr.concatTokens().toUpperCase(),
              file: path,
              line: pos.getRow(),
            });
          }
        }
        for (const expr of statement.findAllExpressions(Expressions.TypeName)) {
          const pos = expr.getFirstToken().getStart();
          if (newObjectTypes.has(`${pos.getRow()}:${pos.getCol()}`)) continue;
          extracted.calls.push({
            internal: false,
            kind: "interface",
            target: expr.concatTokens().toUpperCase(),
            file: path,
            line: pos.getRow(),
          });
        }
      }
    }

    // definitions can appear after the calls that use them (FORM below
    // START-OF-SELECTION), so internal-ness is decided after the full pass
    for (const call of extracted.calls) {
      call.internal = definedNames.has(call.target);
    }
    // self-references are noise, not edges
    extracted.calls = extracted.calls.filter((c) => c.target !== extracted.name);
    objects.push(extracted);
  }

  const unattachedFiles = inputs
    .filter((i) => !attached.has(i.path))
    .map((i) => ({
      path: i.path,
      reason: "abaplint did not map this file to an object (unsupported filename pattern)",
    }));

  const objectsOk = objects.filter((o) => o.parseStatus === "ok").length;
  return {
    objects,
    unattachedFiles,
    totals: {
      inputFiles: inputs.length,
      attachedFiles: attached.size,
      objects: objects.length,
      objectsOk,
      objectsFailed: objects.length - objectsOk,
    },
  };
}
