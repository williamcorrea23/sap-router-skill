/**
 * Run snapshot + executive summary (report restructure).
 *
 * Every finished report run freezes its numbers as a `snapshot` jsonb on
 * report_runs — grade distribution, usage coverage, category counts, tier
 * counts, retirement candidates — all computed by SQL. The executive summary
 * is 3–4 sentences of generated prose whose numbers are injected from that
 * snapshot: the traced LLM call is only allowed to phrase them. A
 * deterministic guard rejects any output that introduces a number not on the
 * allow-list (or drops a required one) and falls back to a template built
 * from the same SQL numbers — the prose can never contradict the data.
 */
import Anthropic from "@anthropic-ai/sdk";
import { query } from "../db/client";

export const EXEC_SUMMARY_MODEL = "claude-haiku-4-5-20251001";

export interface RunSnapshot {
  total_objects: number;
  parse_ok: number;
  tiers: { "1": number; "2": number; "3": number };
  affected_objects: number;
  /** counts keyed by grade letter; absent letters mean 0 */
  grades: Record<string, number>;
  usage: { rows: number; coverage_pct: number; simulated: boolean };
  categories: { category: string | null; n: number }[];
  /** null when the workspace has no usage data at all */
  retirement_candidates: number | null;
}

export interface TopRiskArea {
  rule_id: string;
  title: string;
  severity: string;
  n: number;
}

/**
 * Freeze the run's numbers. Caller contract: the run's `finished_at` must
 * already be set — the object_risk_grades view grades from the latest
 * *finished* run, so grading only sees this run once it is finished.
 * (The migration 009 backfill computes the same shape in pure SQL.)
 */
export async function computeSnapshot(wsId: string, runId: string): Promise<RunSnapshot> {
  const [counts] = await query<{
    total: string; parse_ok: string; tier1: string; tier2: string; tier3: string;
    affected: string; usage_rows: string; retirement: string;
  }>(
    `select
       (select count(*) from objects where workspace_id = $1) as total,
       (select count(*) from objects where workspace_id = $1 and parse_status = 'ok') as parse_ok,
       (select count(*) from findings where run_id = $2 and tier = 1 and not suppressed) as tier1,
       (select count(*) from findings where run_id = $2 and tier = 2 and not suppressed) as tier2,
       (select count(*) from findings where run_id = $2 and tier = 3 and not suppressed) as tier3,
       (select count(distinct object_id) from findings where run_id = $2 and tier in (1, 2) and not suppressed) as affected,
       (select count(*) from usage_stats where workspace_id = $1) as usage_rows,
       (select count(*) from usage_stats u
        where u.workspace_id = $1 and u.call_count_24m = 0
          and not exists (select 1 from call_edges e
                          where e.workspace_id = $1 and e.callee_id = u.object_id
                            and e.caller_id <> u.object_id)) as retirement`,
    [wsId, runId]
  );

  const gradeRows = await query<{ grade: string; n: string }>(
    `select grade, count(*) as n from object_risk_grades
     where workspace_id = $1 and grade is not null group by grade`,
    [wsId]
  );
  const grades: Record<string, number> = {};
  for (const g of gradeRows) grades[g.grade] = Number(g.n);

  const categories = await query<{ category: string | null; n: string }>(
    `select category, count(*) as n from objects where workspace_id = $1
     group by category order by count(*) desc, category`,
    [wsId]
  );

  const [ws] = await query<{ simulated_usage: boolean }>(
    `select simulated_usage from workspaces where id = $1`,
    [wsId]
  );

  const total = Number(counts.total);
  const usageRows = Number(counts.usage_rows);
  return {
    total_objects: total,
    parse_ok: Number(counts.parse_ok),
    tiers: { "1": Number(counts.tier1), "2": Number(counts.tier2), "3": Number(counts.tier3) },
    affected_objects: Number(counts.affected),
    grades,
    usage: {
      rows: usageRows,
      coverage_pct: total > 0 ? Math.round((100 * usageRows) / total) : 0,
      simulated: ws?.simulated_usage ?? false,
    },
    categories: categories.map((c) => ({ category: c.category, n: Number(c.n) })),
    retirement_candidates: usageRows > 0 ? Number(counts.retirement) : null,
  };
}

/** Top Tier-1 rules by finding count — the "top risk areas" of the prose. */
export async function topRiskAreas(runId: string, limit = 3): Promise<TopRiskArea[]> {
  return query<TopRiskArea & { n: number }>(
    `select r.id as rule_id, r.title, r.severity, count(*)::int as n
     from findings f join incompatibility_rules r on r.id = f.rule_id
     where f.run_id = $1 and f.tier = 1 and not f.suppressed
     group by r.id, r.title, r.severity
     order by count(*) desc, r.id
     limit $2`,
    [runId, limit]
  );
}

/** % of the migration scope removable by retiring the candidates (rounded). */
export function retirementScopePct(snapshot: RunSnapshot): number | null {
  if (snapshot.retirement_candidates === null || snapshot.total_objects === 0) return null;
  return Math.round((100 * snapshot.retirement_candidates) / snapshot.total_objects);
}

/**
 * Every number the summary is allowed to contain (as strings). Includes the
 * tier labels (1, 2, 3) and the 24-month retirement window; "S/4HANA" is
 * stripped before extraction, so its 4 never counts.
 */
export function allowedSummaryNumbers(snapshot: RunSnapshot, objectsAnalyzed: number, top: TopRiskArea[]): Set<string> {
  const scopePct = retirementScopePct(snapshot);
  const values: (number | null)[] = [
    1, 2, 3, 24,
    snapshot.total_objects,
    snapshot.parse_ok,
    objectsAnalyzed,
    snapshot.tiers["1"],
    snapshot.tiers["2"],
    snapshot.tiers["3"],
    snapshot.affected_objects,
    snapshot.retirement_candidates,
    scopePct,
    snapshot.usage.coverage_pct,
    ...Object.values(snapshot.grades),
    ...top.map((t) => t.n),
  ];
  return new Set(values.filter((v): v is number => v !== null).map(String));
}

/** Extract every number of a summary text (S/4HANA's digit excluded). */
export function extractSummaryNumbers(text: string): string[] {
  const cleaned = text.replace(/S\/4\s?HANA/gi, "").replace(/S\/4/g, "");
  return cleaned.match(/\d+(?:\.\d+)?/g) ?? [];
}

/**
 * The guard that makes the prose safe: every number in the text must be on
 * the allow-list, and the load-bearing numbers must actually appear.
 */
export function summaryPassesNumericGuard(
  text: string,
  snapshot: RunSnapshot,
  objectsAnalyzed: number,
  top: TopRiskArea[]
): boolean {
  const allowed = allowedSummaryNumbers(snapshot, objectsAnalyzed, top);
  const present = extractSummaryNumbers(text);
  if (!present.every((n) => allowed.has(n))) return false;
  const required = [String(objectsAnalyzed), String(snapshot.tiers["1"]), String(snapshot.tiers["2"])];
  if (snapshot.retirement_candidates !== null) required.push(String(snapshot.retirement_candidates));
  return required.every((n) => present.includes(n));
}

function sentenceCount(text: string): number {
  return (text.match(/[.!?](\s|$)/g) ?? []).length;
}

/** Deterministic 3–4 sentence summary from the same SQL numbers (fallback +
 *  skip-LLM path + pre-restructure runs without a stored summary). */
export function buildFallbackSummary(
  snapshot: RunSnapshot,
  objectsAnalyzed: number,
  top: TopRiskArea[]
): string {
  const t1 = snapshot.tiers["1"];
  const t2 = snapshot.tiers["2"];
  const scopePct = retirementScopePct(snapshot);
  const sim = snapshot.usage.simulated ? " (simulated)" : "";

  const s1 = `This report run analyzed ${objectsAnalyzed} objects in the system.`;
  const s2 =
    t1 + t2 > 0
      ? `It found ${t1} Tier-1 (machine-verified) and ${t2} Tier-2 (evidence-linked) S/4HANA incompatibilities across ${snapshot.affected_objects} objects.`
      : `It found ${t1} Tier-1 (machine-verified) and ${t2} Tier-2 (evidence-linked) S/4HANA incompatibilities.`;
  const s3 =
    snapshot.retirement_candidates === null
      ? "No usage data is available for this system, so retirement analysis was not possible."
      : snapshot.retirement_candidates === 0
        ? `Usage data${sim} is present, but no objects met the retirement criteria.`
        : `${snapshot.retirement_candidates} objects are retirement candidates${sim} — zero executions in 24 months and no inbound references — which would remove ${scopePct}% of the migration scope.`;
  const s4 = top.length
    ? `The largest risk area is "${top[0].title}" with ${top[0].n} machine-verified findings.`
    : null;

  return [s1, s2, s3, s4].filter(Boolean).join(" ");
}

/**
 * Generate the executive summary for a finished run: one traced LLM call for
 * the prose, numbers injected from the snapshot, deterministic guard +
 * fallback. Never throws — a failed or guard-rejected LLM call degrades to
 * the template, never to a missing or wrong summary.
 */
export async function generateExecutiveSummary(opts: {
  wsId: string;
  runId: string;
  snapshot: RunSnapshot;
  objectsAnalyzed: number;
  skipLlm?: boolean;
  log?: (s: string) => void;
}): Promise<string> {
  const { wsId, runId, snapshot, objectsAnalyzed } = opts;
  const log = opts.log ?? (() => {});
  const top = await topRiskAreas(runId);
  const fallback = buildFallbackSummary(snapshot, objectsAnalyzed, top);
  if (opts.skipLlm) return fallback;

  const scopePct = retirementScopePct(snapshot);
  const facts = {
    objects_analyzed: objectsAnalyzed,
    tier1_findings_machine_verified: snapshot.tiers["1"],
    tier2_findings_evidence_linked: snapshot.tiers["2"],
    affected_objects: snapshot.affected_objects,
    retirement_candidates: snapshot.retirement_candidates,
    retirement_scope_pct_saved: scopePct,
    usage_data: snapshot.usage.rows === 0 ? "none" : snapshot.usage.simulated ? "simulated" : "real",
    top_risk_areas: top.map((t) => ({ title: t.title, severity: t.severity, findings: t.n })),
  };

  const prompt = `Write the executive summary for an SAP S/4HANA migration readiness report as exactly 3 or 4 plain sentences (no headings, no bullets, no markdown).

It must state: how many objects were analyzed; the Tier-1 and Tier-2 finding counts (Tier 1 = machine-verified, Tier 2 = evidence-linked); the retirement candidates and the percentage of migration scope their retirement would save (if retirement_candidates is null, say instead that no usage data was available for retirement analysis; if usage_data is "simulated", mention the usage data is simulated); and the top risk area(s).

HARD RULE: use ONLY the numbers given below, written exactly as given (no rewording like "a dozen", no derived numbers, no percentages you compute yourself). Do not invent any fact that is not in the data.

Data (JSON):
${JSON.stringify(facts, null, 2)}`;

  const started = Date.now();
  try {
    const client = new Anthropic();
    const res = await client.messages.create({
      model: EXEC_SUMMARY_MODEL,
      max_tokens: 400,
      messages: [{ role: "user", content: prompt }],
    });
    const text = res.content
      .filter((b) => b.type === "text")
      .map((b) => (b as { text: string }).text)
      .join("")
      .trim();
    await query(
      `insert into traces (workspace_id, kind, model, input, output, input_tokens, output_tokens, duration_ms)
       values ($1, 'exec_summary', $2, $3, $4, $5, $6, $7)`,
      [
        wsId,
        EXEC_SUMMARY_MODEL,
        JSON.stringify({ run_id: runId, facts }),
        JSON.stringify({ text: text.slice(0, 4000) }),
        res.usage.input_tokens,
        res.usage.output_tokens,
        Date.now() - started,
      ]
    );

    const sentences = sentenceCount(text);
    if (sentences < 3 || sentences > 5) {
      log(`exec summary: sentence count ${sentences} outside 3–5 — using deterministic fallback`);
      return fallback;
    }
    if (!summaryPassesNumericGuard(text, snapshot, objectsAnalyzed, top)) {
      log("exec summary: numeric guard rejected the LLM prose — using deterministic fallback");
      return fallback;
    }
    return text;
  } catch (e) {
    log(`exec summary: LLM call failed (${(e as Error).message}) — using deterministic fallback`);
    return fallback;
  }
}
