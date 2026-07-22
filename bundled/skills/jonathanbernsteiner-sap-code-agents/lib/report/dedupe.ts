/**
 * A3 — finding dedupe. Findings on the same object + same evidence line +
 * same rule family are merged into one finding listing all affected
 * tables/tokens (one JOIN line touching MKPF and MSEG → one finding, two
 * tables). LLM findings (no rule) form their own family per line.
 *
 * CO-08 — root-cause merge (mergeRootCauses). Tier-2 LLM findings on the
 * same object whose demonstrated claim tokens overlap are one underlying
 * cause stated in different words (the classic case: four separate findings
 * all citing the hard-coded 18-char MATNR length). They merge into a single
 * finding whose primary citation is the earliest location; the remaining
 * citations move to extraEvidence. Deterministic: tokens come from
 * claims.supportedTokens, grouping is transitive (union-find), ordering is
 * by file/line.
 */
import { supportedTokens } from "./claims";

export interface ExtraEvidence {
  file: string | null;
  line: number | null;
  evidence: string | null;
}

export interface DraftFinding {
  objectId: string;
  ruleId: string | null;
  tier: 1 | 2 | 3;
  title: string;
  detail: string;
  file: string | null;
  line: number | null;
  evidence: string | null;
  validator: string | null;
  validatorPassed: boolean | null;
  /** CO-08 root-cause merge: further citations of the same underlying cause */
  extraEvidence?: ExtraEvidence[];
  /** deterministic table_access drafts: what this hit is about, for merging */
  op?: string;
  token?: string;
  ruleTitle?: string;
  ruleDescription?: string;
  suppressed?: boolean;
  suppressionReason?: string | null;
}

export function dedupeFindings(drafts: DraftFinding[]): DraftFinding[] {
  const groups = new Map<string, DraftFinding[]>();
  for (const d of drafts) {
    const key = `${d.objectId}|${d.file ?? ""}|${d.line ?? ""}|${d.ruleId ?? "llm"}`;
    const list = groups.get(key) ?? [];
    list.push(d);
    groups.set(key, list);
  }

  const out: DraftFinding[] = [];
  for (const group of groups.values()) {
    if (group.length === 1) {
      out.push(group[0]);
      continue;
    }
    const first = group[0];
    if (first.ruleId !== null && first.op !== undefined) {
      // deterministic table_access family: one line, several tables/ops
      const ops = [...new Set(group.map((g) => g.op!.toUpperCase()))];
      const tokens = [...new Set(group.map((g) => g.token!))];
      // the merged line is only Tier 1 if every member was validator-confirmed
      const confirmed = group.every((g) => g.validatorPassed === true);
      const what = `${ops.join("/")} on ${tokens.join(", ")}`;
      out.push({
        ...first,
        tier: confirmed ? 1 : 2,
        validatorPassed: confirmed,
        title: `${what} — ${first.ruleTitle ?? first.title}`,
        detail: confirmed
          ? `Machine-verified: deterministic validator '${first.ruleId}' confirmed this ${what} at the cited line. ${first.ruleDescription ?? ""}`.trim()
          : `Parser recorded this ${what}, but the deterministic validator could not confirm the exact cited line — needs expert review. ${first.ruleDescription ?? ""}`.trim(),
        token: tokens.join(", "),
      });
    } else {
      // same-line LLM (or scan-rule) findings are restatements of one claim
      // (both already passed the claim-evidence check against the same line):
      // keep the first, drop the rewordings — never append them to the detail
      out.push(first);
    }
  }
  return out;
}

/**
 * CO-08 — merge Tier-2 LLM findings that state the same root cause.
 * Runs after the claim-evidence check (so every member's claim is already
 * supported by its own citation) and before suppression.
 */
export function mergeRootCauses(findings: DraftFinding[]): DraftFinding[] {
  const out: DraftFinding[] = [];
  const perObject = new Map<string, { f: DraftFinding; tokens: string[] }[]>();
  for (const f of findings) {
    if (f.tier !== 2 || f.ruleId !== null) {
      out.push(f);
      continue;
    }
    // tokenless titles (no specific identifier/length claimed) still join the
    // pool — the adjacency edge below can merge them with their code block
    const tokens = supportedTokens(f.title, f.evidence) ?? [];
    const list = perObject.get(f.objectId) ?? [];
    list.push({ f, tokens });
    perObject.set(f.objectId, list);
  }

  for (const members of perObject.values()) {
    // transitive grouping: one cause = shared demonstrated token, OR citations
    // of the same code block (same file, lines within ±3)
    const parent = members.map((_, i) => i);
    const find = (i: number): number => (parent[i] === i ? i : (parent[i] = find(parent[i])));
    for (let i = 0; i < members.length; i++) {
      for (let j = i + 1; j < members.length; j++) {
        const a = members[i];
        const b = members[j];
        const sharedToken = a.tokens.some((t) => b.tokens.includes(t));
        const adjacent =
          a.f.file !== null &&
          a.f.file === b.f.file &&
          a.f.line !== null &&
          b.f.line !== null &&
          Math.abs(a.f.line - b.f.line) <= 3;
        if (sharedToken || adjacent) parent[find(i)] = find(j);
      }
    }
    const groups = new Map<number, DraftFinding[]>();
    for (let i = 0; i < members.length; i++) {
      const root = find(i);
      groups.set(root, [...(groups.get(root) ?? []), members[i].f]);
    }
    for (const group of groups.values()) {
      const sorted = [...group].sort(
        (a, b) => (a.file ?? "").localeCompare(b.file ?? "") || (a.line ?? 0) - (b.line ?? 0)
      );
      const primary = { ...sorted[0] };
      if (sorted.length > 1) {
        primary.extraEvidence = sorted
          .slice(1)
          .map((g) => ({ file: g.file, line: g.line, evidence: g.evidence }));
        primary.detail += `\n\nThis issue appears at ${sorted.length} locations in this object; all citations are listed below.`;
      }
      out.push(primary);
    }
  }
  return out;
}
