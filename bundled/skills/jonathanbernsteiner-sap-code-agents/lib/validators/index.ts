/**
 * Deterministic validators — one per Tier-1-eligible incompatibility rule
 * (Phase 3).
 *
 * A validator takes raw ABAP source and returns every match with the
 * statement text and line number. Findings are only Tier 1 when the
 * validator, re-run on the cited evidence, confirms the match. No LLM
 * involvement anywhere in this module.
 */
import rulesFile from "../rules/rules.json";

export interface RuleDetection {
  type: "table_access" | "call_transaction" | "function_call";
  tables?: string[];
  ops?: string[];
  transactions?: string[];
  functions?: string[];
}

export interface Rule {
  id: string;
  title: string;
  description: string;
  sap_note: string;
  simplification_item?: string;
  source_url?: string;
  detection: RuleDetection;
  replacement?: string;
  tier1_eligible: boolean;
}

export interface ValidatorMatch {
  ruleId: string;
  line: number;
  /** last line of the matched statement (multi-line statements span a range) */
  endLine: number;
  /** the matched statement, whitespace-normalized — the evidence */
  statement: string;
  /** what matched, e.g. "select on KONV" or "CALL TRANSACTION 'MB01'" */
  detail: string;
}

export const RULES: Rule[] = (rulesFile as { rules: Rule[] }).rules;

/**
 * Split ABAP source into statements with their starting line numbers.
 * Strips full-line (*) and end-of-line (") comments; respects '...' string
 * literals (including '' escapes). Deterministic and side-effect free.
 */
export function splitStatements(source: string): { text: string; line: number; endLine: number }[] {
  const statements: { text: string; line: number; endLine: number }[] = [];
  let current = "";
  let startLine = -1;
  let line = 1;
  let inString = false;
  const lines = source.split("\n");
  for (let li = 0; li < lines.length; li++) {
    line = li + 1;
    const raw = lines[li];
    if (!inString && /^\s*\*/.test(raw)) continue; // full-line comment
    let processed = "";
    for (let i = 0; i < raw.length; i++) {
      const ch = raw[i];
      if (inString) {
        processed += ch;
        if (ch === "'") {
          if (raw[i + 1] === "'") {
            processed += "'";
            i++;
          } else {
            inString = false;
          }
        }
        continue;
      }
      if (ch === "'") {
        inString = true;
        processed += ch;
        continue;
      }
      if (ch === '"') break; // end-of-line comment
      if (ch === ".") {
        const text = (current + " " + processed).replace(/\s+/g, " ").trim();
        if (text) statements.push({ text, line: startLine === -1 ? line : startLine, endLine: line });
        current = "";
        processed = "";
        startLine = -1;
        continue;
      }
      processed += ch;
    }
    if (processed.trim() && startLine === -1) startLine = line;
    current += " " + processed;
    inString = false; // ABAP string literals do not span lines
  }
  const rest = current.replace(/\s+/g, " ").trim();
  if (rest) statements.push({ text: rest, line: startLine === -1 ? line : startLine, endLine: line });
  return statements;
}

function escape(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

const OP_PATTERNS: Record<string, (table: string) => RegExp> = {
  select: (t) => new RegExp(`\\bSELECT\\b.*\\b(?:FROM|JOIN)\\s+${escape(t)}\\b`, "i"),
  insert: (t) => new RegExp(`\\bINSERT\\s+(?:INTO\\s+)?${escape(t)}\\b`, "i"),
  update: (t) => new RegExp(`\\bUPDATE\\s+${escape(t)}\\b`, "i"),
  modify: (t) => new RegExp(`\\bMODIFY\\s+${escape(t)}\\b`, "i"),
  delete: (t) => new RegExp(`\\bDELETE\\s+(?:FROM\\s+)?${escape(t)}\\b`, "i"),
};

/** Run one rule's validator over raw ABAP source. */
export function runValidator(rule: Rule, source: string): ValidatorMatch[] {
  const statements = splitStatements(source);
  const matches: ValidatorMatch[] = [];
  const det = rule.detection;

  for (const stmt of statements) {
    if (det.type === "table_access") {
      for (const table of det.tables ?? []) {
        for (const op of det.ops ?? []) {
          const pattern = OP_PATTERNS[op];
          if (pattern && pattern(table).test(stmt.text)) {
            matches.push({
              ruleId: rule.id,
              line: stmt.line,
              endLine: stmt.endLine,
              statement: stmt.text,
              detail: `${op} on ${table.toUpperCase()}`,
            });
          }
        }
      }
    } else if (det.type === "call_transaction") {
      for (const tcode of det.transactions ?? []) {
        const re = new RegExp(`\\b(?:CALL|LEAVE\\s+TO)\\s+TRANSACTION\\s+'${escape(tcode)}'`, "i");
        if (re.test(stmt.text)) {
          matches.push({
            ruleId: rule.id,
            line: stmt.line,
            endLine: stmt.endLine,
            statement: stmt.text,
            detail: `transaction ${tcode.toUpperCase()}`,
          });
        }
      }
    } else if (det.type === "function_call") {
      for (const fname of det.functions ?? []) {
        const re = new RegExp(`\\bCALL\\s+FUNCTION\\s+'${escape(fname)}'`, "i");
        if (re.test(stmt.text)) {
          matches.push({
            ruleId: rule.id,
            line: stmt.line,
            endLine: stmt.endLine,
            statement: stmt.text,
            detail: `function ${fname.toUpperCase()}`,
          });
        }
      }
    }
  }
  return matches;
}

/** Run every Tier-1-eligible rule's validator over raw ABAP source. */
export function runAllValidators(source: string): ValidatorMatch[] {
  return RULES.filter((r) => r.tier1_eligible).flatMap((r) => runValidator(r, source));
}

/**
 * Re-validate a single cited evidence location: true only when the rule's
 * validator still matches at exactly that line. Used by the report job to
 * confirm Tier-1 findings.
 */
export function validateEvidence(rule: Rule, source: string, line: number): boolean {
  return runValidator(rule, source).some((m) => line >= m.line && line <= m.endLine);
}
