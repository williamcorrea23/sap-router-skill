/**
 * A2 — known-false-positive suppression.
 *
 * Rules live in the suppression_rules table (data, not code): 'regex' rules
 * apply their case-insensitive pattern to title + detail; 'category' rules
 * activate one of the coded checks below. Suppressed findings are stored with
 * suppressed = true + the rule's reason and are visible only in the debug
 * view — never in reports.
 */
import { query } from "../db/client";

export interface SuppressionRule {
  id: string;
  kind: "regex" | "category";
  pattern: string | null;
  category: string | null;
  reason: string;
}

export interface SuppressionInput {
  title: string;
  detail: string;
  ruleId: string | null;
}

/**
 * Coded category checks. Each gets the finding and says whether it is a
 * known false positive. New categories are added here; enabling one is an
 * INSERT into suppression_rules.
 */
const CATEGORY_CHECKS: Record<string, (f: SuppressionInput) => boolean> = {
  // Field-length claims are only actionable for MATNR (40-char extension)
  // unless the finding is tied to a seeded incompatibility rule.
  "non-matnr-field-length": (f) => {
    if (f.ruleId !== null) return false;
    const text = `${f.title}\n${f.detail}`;
    const lengthClaim = /\b(?:field\s+)?length\b|\bchar\s*\d|\d+[\s-]*char(?:acter)?s?\b|\btruncat/i.test(text);
    if (!lengthClaim) return false;
    return !/matnr|material\s+number/i.test(text);
  },
};

export async function loadSuppressionRules(): Promise<SuppressionRule[]> {
  return query<SuppressionRule>(
    `select id, kind, pattern, category, reason from suppression_rules order by id`
  );
}

/** Returns the suppression reason, or null when the finding is not suppressed. */
export function evaluateSuppression(
  rules: SuppressionRule[],
  finding: SuppressionInput
): { ruleId: string; reason: string } | null {
  for (const rule of rules) {
    if (rule.kind === "regex" && rule.pattern) {
      if (new RegExp(rule.pattern, "i").test(`${finding.title}\n${finding.detail}`)) {
        return { ruleId: rule.id, reason: rule.reason };
      }
    } else if (rule.kind === "category" && rule.category) {
      const check = CATEGORY_CHECKS[rule.category];
      if (check && check(finding)) return { ruleId: rule.id, reason: rule.reason };
    }
  }
  return null;
}
