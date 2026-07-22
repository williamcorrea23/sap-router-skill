/**
 * The short finding statement of a Tier-1 finding — what was found at the
 * cited line ("SELECT on BSID", "transaction MB01"), without the rule title
 * the generator appends ("<statement> — <rule title>"). Rendered as the
 * Finding column of the affected-locations tables so two findings on one
 * object (BSID line 29 vs BSAD line 37) read as two rows, not a duplicate.
 * Dependency-free on purpose: shared by the MD/PDF renderers and the client
 * report page.
 */
export function findingStatement(f: { title: string; rule_title: string | null }): string {
  const suffix = f.rule_title ? ` — ${f.rule_title}` : null;
  if (suffix && f.title.endsWith(suffix)) return f.title.slice(0, -suffix.length);
  return f.title;
}
