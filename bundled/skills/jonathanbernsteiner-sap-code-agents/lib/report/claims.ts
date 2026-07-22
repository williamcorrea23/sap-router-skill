/**
 * A1 — mechanical claim-evidence alignment for Tier-2 findings.
 *
 * A Tier-2 finding whose title claims a specific pattern (a table, a
 * transaction, a function module, a field length) must show that pattern in
 * its cited evidence snippet. If the referenced tokens do not appear there
 * (case-insensitive), the finding is downgraded to Tier 3. Deterministic,
 * no LLM involvement.
 */

/** Generic words that look like SAP identifiers but claim nothing specific. */
const IDENTIFIER_STOPLIST = new Set([
  "SAP", "ABAP", "HANA", "S4HANA", "ECC", "ERP", "API", "BAPI", "CDS", "SQL",
  "RFC", "GUI", "ALV", "DDIC", "IDOC", "BADI", "BDC", "OSS", "LLM",
  "CHAR", "NUMC", "CURR", "QUAN", "DEC", "INT", "STRING", "TYPE", "TYPES",
  "LENGTH", "FIELD", "TABLE", "TABLES", "VIEW", "SELECT", "INSERT", "UPDATE",
  "DELETE", "MODIFY", "JOIN", "CALL", "FUNCTION", "TRANSACTION", "MODULE",
  "REPORT", "NOTE", "AND", "NOT", "THE", "FOR", "WITH",
]);

export interface ClaimCheck {
  /** identifiers/lengths the title claims */
  claimed: string[];
  /** true when the evidence snippet supports the claim (or nothing specific is claimed) */
  supported: boolean;
  /** claimed tokens that were not found in the evidence */
  missing: string[];
}

/** All-caps SAP-style identifiers claimed in a finding title. */
function claimedIdentifiers(title: string): string[] {
  const ids = title.match(/\b[A-Z][A-Z0-9_]{2,}\b/g) ?? [];
  return [...new Set(ids.filter((t) => !IDENTIFIER_STOPLIST.has(t)))];
}

/** Numbers that are part of an explicit length claim ("18 chars", "LENGTH 40"). */
function claimedLengths(title: string): string[] {
  const out = new Set<string>();
  const patterns = [
    /\b(?:length|len)\s*(\d{1,4})\b/gi,
    /\b(\d{1,4})[\s-]*(?:char(?:acter)?s?|digits?|bytes?)\b/gi,
    /\bchar\s*(\d{1,4})\b/gi,
  ];
  for (const re of patterns) {
    for (const m of title.matchAll(re)) out.add(m[1]);
  }
  return [...out];
}

/**
 * Check a Tier-2 claim against its evidence snippet. The rule: if the title
 * claims identifiers, at least one must appear in the evidence; if it claims
 * field lengths, at least one claimed length must appear. (Titles routinely
 * also name the S/4HANA successor — e.g. "KONV replaced by PRCD_ELEMENTS" —
 * so requiring every identifier would reject valid findings.)
 */
/**
 * CO-08 — the tokens a Tier-2 finding actually demonstrates: identifiers and
 * lengths claimed in the title that are present in the cited evidence. Used
 * as the deterministic root-cause signature for merging findings that state
 * the same underlying problem in different words (e.g. every variant of the
 * hard-coded 18-char MATNR issue reduces to the token "18"). Returns null
 * when nothing specific is demonstrated.
 */
export function supportedTokens(title: string, evidence: string | null): string[] | null {
  if (!evidence) return null;
  const haystack = evidence.toLowerCase();
  const present = [
    ...claimedIdentifiers(title).filter((t) => haystack.includes(t.toLowerCase())),
    ...claimedLengths(title).filter((n) => new RegExp(`\\b${n}\\b`).test(evidence)),
  ];
  return present.length > 0 ? [...new Set(present)].sort() : null;
}

export function checkClaim(title: string, evidence: string | null): ClaimCheck {
  const identifiers = claimedIdentifiers(title);
  const lengths = claimedLengths(title);
  const claimed = [...identifiers, ...lengths];
  if (claimed.length === 0 || !evidence) {
    return { claimed, supported: true, missing: [] };
  }
  const haystack = evidence.toLowerCase();
  const idPresent = identifiers.filter((t) => haystack.includes(t.toLowerCase()));
  const lenPresent = lengths.filter((n) => new RegExp(`\\b${n}\\b`).test(evidence));
  const supported =
    (identifiers.length === 0 || idPresent.length > 0) &&
    (lengths.length === 0 || lenPresent.length > 0);
  const missing = [
    ...identifiers.filter((t) => !idPresent.includes(t)),
    ...lengths.filter((n) => !lenPresent.includes(n)),
  ];
  return { claimed, supported, missing };
}
