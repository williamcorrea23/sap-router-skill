/**
 * ABAP MCP Server — Dependency Contracts (context compression)
 *
 * A "contract" is the compressed public interface of an object: class/interface
 * name plus public method signatures, interfaces, events and public type/data/
 * constant declarations — but NOT method bodies. For an agent that needs to know
 * *how to call* a dependency, this is the relevant 5–10% of a class source; the
 * implementation bodies are noise. Emitting contracts instead of full source is
 * where the 7–30× context compression of comparable servers comes from.
 *
 * Parsing is regex/statement based (consistent with context.ts and
 * method-splice.ts) — it does not need a full ABAP grammar, just the public
 * declaration surface. Bodies, PROTECTED and PRIVATE sections are dropped.
 */

/** Strip ABAP comments: full-line `*` (column 1) and inline `"` to end-of-line. */
function stripComments(source: string): string {
  return source
    .split(/\r?\n/)
    .map((line) => {
      if (/^\*/.test(line)) return ""; // full-line comment
      // inline comment — naive: a quote not inside a string literal. Good enough
      // for declaration sections, which rarely embed quotes in public signatures.
      const idx = line.indexOf('"');
      return idx >= 0 ? line.slice(0, idx) : line;
    })
    .join("\n");
}

/** Collapse whitespace in a single declaration statement for compact output. */
function compact(stmt: string): string {
  return stmt.replace(/\s+/g, " ").trim();
}

/** Split a section's text into statements on `.` (ignoring chained `,` members). */
function splitStatements(text: string): string[] {
  return text
    .split(/\.(?:\s|$)/)
    .map((s) => s.trim())
    .filter(Boolean);
}

const PUBLIC_KEYWORDS =
  /^(CLASS-METHODS|METHODS|INTERFACES|ALIASES|EVENTS|CLASS-EVENTS|TYPES|CONSTANTS|CLASS-DATA|DATA)\b/i;

export interface Contract {
  kind: "class" | "interface" | "unknown";
  name: string;
  /** Compact one-line declarations from the public surface. */
  members: string[];
}

/**
 * Build a contract from an object's full source. Best-effort: for classes the
 * PUBLIC SECTION is used; for interfaces the whole body; for anything else an
 * empty member list with kind "unknown" is returned so callers can fall back.
 */
export function buildContract(source: string, fallbackName = ""): Contract {
  const clean = stripComments(source);

  // --- Interface ---
  const intf = /INTERFACE\s+([\w/]+)\s*(?:PUBLIC)?\s*\.([\s\S]*?)ENDINTERFACE\s*\./i.exec(clean);
  if (intf) {
    return {
      kind: "interface",
      name: intf[1],
      members: collectMembers(intf[2]),
    };
  }

  // --- Class definition ---
  const clsDef = /CLASS\s+([\w/]+)\s+DEFINITION\b([\s\S]*?)ENDCLASS\s*\./i.exec(clean);
  if (clsDef) {
    const name = clsDef[1];
    const defBody = clsDef[2];
    // Public section runs until PROTECTED/PRIVATE SECTION or end of definition.
    const pub = /PUBLIC\s+SECTION\s*\.([\s\S]*?)(?:PROTECTED\s+SECTION|PRIVATE\s+SECTION|$)/i.exec(defBody);
    const inheritance = /CLASS\s+[\w/]+\s+DEFINITION\b([^.]*)\./i.exec(clean);
    const members = pub ? collectMembers(pub[1]) : [];
    if (inheritance && /INHERITING\s+FROM\s+([\w/]+)/i.test(inheritance[1])) {
      const sup = /INHERITING\s+FROM\s+([\w/]+)/i.exec(inheritance[1])![1];
      members.unshift(`INHERITING FROM ${sup}`);
    }
    return { kind: "class", name, members };
  }

  return { kind: "unknown", name: fallbackName, members: [] };
}

function collectMembers(sectionText: string): string[] {
  const out: string[] = [];
  for (const stmt of splitStatements(sectionText)) {
    if (PUBLIC_KEYWORDS.test(stmt)) out.push(compact(stmt));
  }
  return out;
}

/** Render a contract as a compact text block for tool output. */
export function renderContract(c: Contract): string {
  const head = c.kind === "unknown"
    ? `OBJECT ${c.name || "(unknown)"} — no class/interface contract could be derived`
    : `${c.kind.toUpperCase()} ${c.name}`;
  if (c.members.length === 0) return head;
  const body = c.members.map((m) => `  ${m}.`).join("\n");
  return `${head}\n${body}`;
}
