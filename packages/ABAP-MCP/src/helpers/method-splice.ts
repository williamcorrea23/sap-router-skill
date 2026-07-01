/**
 * ABAP MCP Server — Method-Level Source Surgery
 *
 * ADT classes are stored as one monolithic source (definition + implementation
 * in a single `/source/main`). There is no per-method ADT object, so to support
 * method-level read/edit we parse `METHOD <name>. … ENDMETHOD.` blocks out of
 * the full class source ourselves. The win is on the *generation* side: the LLM
 * reads/rewrites a single method instead of re-emitting an 800-line class, which
 * is the dominant token cost in iterative coding. The reassembled full source is
 * still handed to the normal write workflow, so locking/syntax/activation are
 * unchanged.
 *
 * Parsing is regex-based and statement-anchored (mirroring the style already in
 * context.ts). It deliberately matches only the implementation form
 * `METHOD name.` (a block) and never the declaration forms `METHODS` /
 * `CLASS-METHODS` (the `\b` after `METHOD` excludes the trailing `S`). Methods do
 * not nest in ABAP, so the first `ENDMETHOD.` after a `METHOD.` closes it.
 *
 * Known limitation: a literal string or comment containing `METHOD foo.` on its
 * own line could in theory be mis-detected. In practice method bodies do not
 * start a line with that exact shape; callers get a clear "method not found"
 * rather than a silent corruption when a name does not resolve.
 */

export interface MethodBlock {
  /** Method name exactly as written in the source (may include `~` for intf). */
  name: string;
  /** Index of the first character of the `METHOD` keyword. */
  start: number;
  /** Index just past the closing `ENDMETHOD.`. */
  end: number;
  /** Leading whitespace of the `METHOD` line, reused when rebuilding. */
  indent: string;
  /** Full matched block text (METHOD … ENDMETHOD.). */
  block: string;
  /** Body between the `METHOD name.` header line and `ENDMETHOD.`. */
  body: string;
}

// METHOD <name>. ... ENDMETHOD.  — name allows word chars, ~ (intf impl), / (ns).
const METHOD_RE = /^([ \t]*)METHOD\s+([\w~/]+)\s*\.[ \t]*\r?\n([\s\S]*?)^[ \t]*ENDMETHOD\s*\./gim;

/** Parse all implementation method blocks out of a class source. */
export function parseMethods(source: string): MethodBlock[] {
  const blocks: MethodBlock[] = [];
  METHOD_RE.lastIndex = 0;
  let m: RegExpExecArray | null;
  while ((m = METHOD_RE.exec(source)) !== null) {
    const [full, indent, name, body] = m;
    blocks.push({
      name,
      start: m.index,
      end: m.index + full.length,
      indent: indent ?? "",
      block: full,
      body: body ?? "",
    });
  }
  return blocks;
}

/** Compare two ABAP method identifiers case-insensitively. */
function sameName(a: string, b: string): boolean {
  return a.toLowerCase() === b.toLowerCase();
}

/** Find a single method block by name (case-insensitive). */
export function findMethod(source: string, methodName: string): MethodBlock | undefined {
  return parseMethods(source).find((b) => sameName(b.name, methodName));
}

/** List the names of all implemented methods (for error messages / discovery). */
export function listMethodNames(source: string): string[] {
  return parseMethods(source).map((b) => b.name);
}

export class MethodNotFoundError extends Error {
  constructor(methodName: string, available: string[]) {
    super(
      `Method '${methodName}' not found in source. ` +
      (available.length > 0
        ? `Available methods: ${available.join(", ")}`
        : "No METHOD…ENDMETHOD implementation blocks were found — is this a class implementation source?"),
    );
    this.name = "MethodNotFoundError";
  }
}

/**
 * Replace the body of one method, returning the full reassembled source.
 *
 * `newBody` is the statements *between* `METHOD name.` and `ENDMETHOD.` (no
 * `METHOD`/`ENDMETHOD` keywords). If the caller does include those keywords we
 * tolerate it by stripping a leading `METHOD ….` / trailing `ENDMETHOD.` so the
 * result never double-wraps. The original `METHOD name.` header and its
 * indentation are preserved exactly.
 */
export function replaceMethodBody(source: string, methodName: string, newBody: string): string {
  const block = findMethod(source, methodName);
  if (!block) throw new MethodNotFoundError(methodName, listMethodNames(source));

  let body = newBody.replace(/\r\n/g, "\n");
  // Tolerate callers that pasted the whole method back in.
  body = body.replace(/^\s*METHOD\s+[\w~/]+\s*\.[ \t]*\n?/i, "");
  body = body.replace(/\n?[ \t]*ENDMETHOD\s*\.\s*$/i, "");
  // Trim a single leading/trailing blank line for tidy output.
  body = body.replace(/^\n+/, "").replace(/\n+$/, "");

  const header = source.slice(block.start, block.start + block.block.indexOf("\n") + 1);
  const rebuilt = `${header}${body}\n${block.indent}ENDMETHOD.`;
  return source.slice(0, block.start) + rebuilt + source.slice(block.end);
}

/** Extract just one method's full block text (for read_abap_method). */
export function extractMethod(source: string, methodName: string): MethodBlock {
  const block = findMethod(source, methodName);
  if (!block) throw new MethodNotFoundError(methodName, listMethodNames(source));
  return block;
}
