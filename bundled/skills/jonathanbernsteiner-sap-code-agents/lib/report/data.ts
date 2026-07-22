/**
 * Shared report data assembly (A4/A6) — one query layer for the on-screen
 * report API and the MD/CSV exports, so surfaces cannot diverge.
 *
 * Systemic guarantees enforced here:
 *  - suppressed findings never appear (debug view requests them explicitly)
 *  - SAP Note numbers render only for rules with source_status = 'verified'
 *  - headline numbers are SQL over the findings table; Tier 3 never counted
 *  - the executive summary and run snapshot are the FROZEN per-run values
 *    stored by the report job; for runs predating the restructure they are
 *    recomputed with the same SQL / deterministic template
 *
 * Section order (report restructure): metadata & run snapshot (one merged
 * table) → executive summary → object inventory & disposition (includes the
 * retirement columns) → Tier 1 grouped by rule → Tier 2 grouped by object
 * → Tier 3. The findings ordering below matches: Tier 1 sorts by rule first,
 * Tier 2/3 by object.
 */
import { query } from "../db/client";
import { NOT_AVAILABLE } from "../empty-values";
import {
  buildFallbackSummary,
  computeSnapshot,
  topRiskAreas,
  type RunSnapshot,
} from "./summary";

export interface ReportFindingRow {
  object_name: string;
  object_type: string;
  /** the object's category (abap | enhancement | custom_table | interface) */
  category: string | null;
  rule_id: string | null;
  tier: number;
  title: string;
  detail: string;
  evidence_file: string | null;
  evidence_line: number | null;
  evidence: string | null;
  validator: string | null;
  validator_passed: boolean | null;
  suppression_reason: string | null;
  sap_note: string | null;
  simplification_item: string | null;
  source_url: string | null;
  replacement: string | null;
  /** seeded rule reference data — lets Tier 1 render per-rule groups that
   *  state title/explanation/replacement once */
  rule_title: string | null;
  rule_description: string | null;
  /** CO-07 source layer (verified rules only): severity, effort band, and the
   *  verbatim Simplification List excerpt with its page-anchored public URL */
  rule_severity: string | null;
  remediation_effort: string | null;
  effort_rationale: string | null;
  verified_release: string | null;
  source_excerpt: string | null;
  excerpt_source_url: string | null;
  /** CO-05: the finding's object's process areas (derived, may be empty) */
  process_areas: string[] | null;
  /** CO-08: further citations of the same root cause (merged findings) */
  extra_evidence: { file: string | null; line: number | null; evidence: string | null }[] | null;
}

export interface RetirementRow {
  name: string;
  object_type: string;
  call_count_24m: string;
  last_executed: string | null;
  simulated: boolean;
}

/** CO-09 — one row per object: the consultant's working table. */
export interface InventoryRow {
  name: string;
  object_type: string;
  category: string | null;
  process_areas: string[] | null;
  grade: string | null;
  disposition: string | null;
  is_retirement_candidate: boolean;
  tier1_n: number;
  tier2_n: number;
  call_count_24m: string | null;
  last_executed: string | null;
  usage_simulated: boolean | null;
  inbound_refs: number;
}

export const DISPOSITION_ORDER = ["retire", "redesign", "adapt", "review", "keep"] as const;

export const DISPOSITION_LABELS: Record<string, string> = {
  retire: "Retire",
  redesign: "Redesign",
  adapt: "Adapt",
  review: "Expert review",
  keep: "Keep",
};

/**
 * CO-09 — deterministic closing recommendation, built purely from the
 * disposition counts and the findings-in-retirement numbers. Rendered as its
 * own line after the executive summary; never merged into the guarded prose.
 */
export function buildRecommendedActions(
  inventory: InventoryRow[],
  netOfRetirement: { tier1: number; tier2: number } | null
): string | null {
  const counts = new Map<string, number>();
  for (const row of inventory) {
    if (row.disposition) counts.set(row.disposition, (counts.get(row.disposition) ?? 0) + 1);
  }
  return recommendedActionsFromCounts(counts, netOfRetirement);
}

/**
 * The template itself, over raw disposition counts — so the overview can
 * render the identical sentence from a SQL aggregate without assembling a
 * full inventory. One implementation, no drift between surfaces.
 */
export function recommendedActionsFromCounts(
  counts: Map<string, number>,
  netOfRetirement: { tier1: number; tier2: number } | null
): string | null {
  if (counts.size === 0) return null;
  const parts: string[] = [];
  for (const d of DISPOSITION_ORDER) {
    const n = counts.get(d) ?? 0;
    if (n === 0) continue;
    let part = `${DISPOSITION_LABELS[d].toLowerCase()} ${n} object${n === 1 ? "" : "s"}`;
    if (d === "retire" && netOfRetirement && netOfRetirement.tier1 + netOfRetirement.tier2 > 0) {
      part += ` (removing ${netOfRetirement.tier1} Tier-1 and ${netOfRetirement.tier2} Tier-2 findings from scope)`;
    }
    parts.push(part);
  }
  return `Recommended next steps: ${parts.join("; ")}; re-run the report after cleanup.`;
}

export interface ReportData {
  workspace: string;
  source: string;
  /** branch recorded at ingestion (null for fixtures / older ingestions) */
  source_branch: string | null;
  kind: string;
  simulated_usage: boolean;
  has_usage_data: boolean;
  run: { id: string; finished_at: string; objects_analyzed: number | null } | null;
  /** generated prose (numbers injected from the snapshot, guard-checked);
   *  null only when there is no finished run */
  executive_summary: string | null;
  /** the run's frozen numbers; null only when there is no finished run */
  snapshot: RunSnapshot | null;
  /** CO-04: Migration Risk Grade distribution of the run (from the snapshot;
   *  null until a report run exists — objects are then ungraded) */
  grades: { A: number; B: number; C: number; D: number } | null;
  headline: {
    tier1: number;
    tier2: number;
    tier3: number;
    affected_objects: number;
    total_objects: number;
    parse_ok: number;
    parse_rate: string; // "99.83%"
  };
  findings: ReportFindingRow[];
  retirement: RetirementRow[];
  /** CO-09 — one row per object with grade, findings, usage, disposition */
  inventory: InventoryRow[];
  /** CO-09 — Tier-1/2 findings sitting in retire-disposition objects: the
   *  scope that disappears by deleting instead of fixing */
  findings_in_retirement: { tier1: number; tier2: number } | null;
  /** CO-09 — deterministic closing recommendation (null before the first run) */
  recommended_actions: string | null;
  /** only present when requested (debug view) */
  suppressed?: ReportFindingRow[];
}

export async function getReportData(
  workspaceName: string,
  opts: { includeSuppressed?: boolean } = {}
): Promise<ReportData | null> {
  const [ws] = await query<{
    id: string;
    source: string;
    source_branch: string | null;
    kind: string;
    simulated_usage: boolean;
  }>(`select id, source, source_branch, kind, simulated_usage from workspaces where name = $1`, [
    workspaceName,
  ]);
  if (!ws) return null;

  const findingColumns = `
     select o.name as object_name, o.object_type, o.category, f.rule_id, f.tier, f.title, f.detail,
            f.evidence_file, f.evidence_line, f.evidence, f.validator, f.validator_passed,
            f.suppression_reason, f.extra_evidence,
            case when r.source_status = 'verified' then r.sap_note else null end as sap_note,
            case when r.source_status = 'verified' then r.simplification_item else null end as simplification_item,
            case when r.source_status = 'verified' then r.source_url else null end as source_url,
            r.replacement,
            r.title as rule_title,
            r.description as rule_description,
            r.severity as rule_severity,
            r.remediation_effort,
            r.effort_rationale,
            r.verified_release,
            case when r.source_status = 'verified' then r.source_excerpt else null end as source_excerpt,
            case when r.source_status = 'verified' then r.excerpt_source_url else null end as excerpt_source_url,
            (select array_agg(pa.process_area order by pa.process_area)
             from object_process_areas pa where pa.object_id = o.id) as process_areas
     from findings f
     join objects o on o.id = f.object_id
     left join incompatibility_rules r on r.id = f.rule_id`;

  // Every section below depends only on ws.id — one parallel batch instead of
  // six-plus sequential round-trips (this feeds the report page AND all three
  // exports). Row content and ordering are unchanged.
  const [runRows, headlineRows, findings, retirement, inventory, netRows, suppressedRows] =
    await Promise.all([
      query<{
        id: string;
        finished_at: string;
        objects_analyzed: number | null;
        executive_summary: string | null;
        snapshot: RunSnapshot | null;
      }>(
        `select id, finished_at, objects_analyzed, executive_summary, snapshot from report_runs
         where workspace_id = $1 and finished_at is not null
         order by finished_at desc limit 1`,
        [ws.id]
      ),
      query<{
        tier1: string; tier2: string; tier3: string; affected: string;
        total: string; parse_ok: string; usage_rows: string;
      }>(
        `select
           (select count(*) from findings where workspace_id = $1 and tier = 1 and not suppressed) as tier1,
           (select count(*) from findings where workspace_id = $1 and tier = 2 and not suppressed) as tier2,
           (select count(*) from findings where workspace_id = $1 and tier = 3 and not suppressed) as tier3,
           (select count(distinct object_id) from findings where workspace_id = $1 and tier in (1,2) and not suppressed) as affected,
           (select count(*) from objects where workspace_id = $1) as total,
           (select count(*) from objects where workspace_id = $1 and parse_status = 'ok') as parse_ok,
           (select count(*) from usage_stats where workspace_id = $1) as usage_rows`,
        [ws.id]
      ),
      // Tier 1 renders grouped by rule, Tier 2/3 grouped by object — the row
      // order IS the display/export order.
      query<ReportFindingRow>(
        `${findingColumns}
         where f.workspace_id = $1 and not f.suppressed
         order by f.tier,
                  case when f.tier = 1 then f.rule_id end nulls last,
                  o.name, f.evidence_line nulls last`,
        [ws.id]
      ),
      query<RetirementRow>(
        `select o.name, o.object_type, u.call_count_24m, u.last_executed, u.simulated
         from usage_stats u join objects o on o.id = u.object_id
         where u.workspace_id = $1 and u.call_count_24m = 0
           and not exists (select 1 from call_edges e
                           where e.workspace_id = $1 and e.callee_id = o.id and e.caller_id <> o.id)
         order by o.name`,
        [ws.id]
      ),
      // CO-09 — object inventory with disposition (pure SQL over the views)
      query<InventoryRow>(
        `select o.name, o.object_type, o.category,
                (select array_agg(pa.process_area order by pa.process_area)
                 from object_process_areas pa where pa.object_id = o.id) as process_areas,
                d.grade, d.disposition, coalesce(d.is_retirement_candidate, false) as is_retirement_candidate,
                (select count(*) from findings f where f.object_id = o.id and f.tier = 1 and not f.suppressed)::int as tier1_n,
                (select count(*) from findings f where f.object_id = o.id and f.tier = 2 and not f.suppressed)::int as tier2_n,
                u.call_count_24m, u.last_executed, u.simulated as usage_simulated,
                (select count(*) from call_edges e
                 where e.workspace_id = $1 and e.callee_id = o.id and e.caller_id <> o.id)::int as inbound_refs
         from objects o
         left join object_dispositions d on d.object_id = o.id
         left join usage_stats u on u.object_id = o.id
         where o.workspace_id = $1
         order by case d.disposition
                    when 'retire' then 0 when 'redesign' then 1 when 'adapt' then 2
                    when 'review' then 3 when 'keep' then 4 else 5 end,
                  o.name`,
        [ws.id]
      ),
      query<{ tier1: string; tier2: string }>(
        `select
           count(*) filter (where f.tier = 1)::int as tier1,
           count(*) filter (where f.tier = 2)::int as tier2
         from findings f
         join object_dispositions d on d.object_id = f.object_id
         where f.workspace_id = $1 and not f.suppressed and d.disposition = 'retire'`,
        [ws.id]
      ),
      opts.includeSuppressed
        ? query<ReportFindingRow>(
            `${findingColumns}
             where f.workspace_id = $1 and f.suppressed
             order by o.name, f.evidence_line`,
            [ws.id]
          )
        : Promise.resolve(null),
    ]);
  const [run] = runRows;
  const [headline] = headlineRows;
  const [net] = netRows;

  // Frozen per-run values; for pre-restructure runs without them, recompute
  // with the same SQL / deterministic template (findings only exist for the
  // latest run, so the recomputation states exactly what that run found).
  let snapshot: RunSnapshot | null = null;
  let executiveSummary: string | null = null;
  if (run) {
    snapshot = run.snapshot ?? (await computeSnapshot(ws.id, run.id));
    const analyzed = run.objects_analyzed ?? snapshot.total_objects;
    executiveSummary =
      run.executive_summary ?? buildFallbackSummary(snapshot, analyzed, await topRiskAreas(run.id));
  }

  const grades: ReportData["grades"] = snapshot
    ? {
        A: snapshot.grades.A ?? 0,
        B: snapshot.grades.B ?? 0,
        C: snapshot.grades.C ?? 0,
        D: snapshot.grades.D ?? 0,
      }
    : null;

  const total = Number(headline.total);
  const parseOk = Number(headline.parse_ok);
  const data: ReportData = {
    workspace: workspaceName,
    source: ws.source,
    source_branch: ws.source_branch,
    kind: ws.kind,
    simulated_usage: ws.simulated_usage,
    has_usage_data: Number(headline.usage_rows) > 0,
    run: run ? { id: run.id, finished_at: run.finished_at, objects_analyzed: run.objects_analyzed } : null,
    executive_summary: executiveSummary,
    snapshot,
    grades,
    headline: {
      tier1: Number(headline.tier1),
      tier2: Number(headline.tier2),
      tier3: Number(headline.tier3),
      affected_objects: Number(headline.affected),
      total_objects: total,
      parse_ok: parseOk,
      parse_rate: total > 0 ? `${((100 * parseOk) / total).toFixed(2)}%` : NOT_AVAILABLE,
    },
    findings,
    retirement,
    inventory,
    findings_in_retirement: run ? { tier1: Number(net.tier1), tier2: Number(net.tier2) } : null,
    recommended_actions: run ? buildRecommendedActions(inventory, { tier1: Number(net.tier1), tier2: Number(net.tier2) }) : null,
  };

  if (suppressedRows) data.suppressed = suppressedRows;
  return data;
}

/** CO-04 — one shared rendering of the run's grade distribution. */
export function gradeDistributionLine(data: ReportData): string {
  if (!data.grades) return "not graded — no report run yet";
  return (["A", "B", "C", "D"] as const).map((g) => `${g}: ${data.grades![g]}`).join(" · ");
}

/**
 * A4 — the retirement section always states the actual condition explicitly.
 */
export function retirementStatement(data: ReportData): string | null {
  if (!data.has_usage_data) {
    return (
      "No usage data is available for this system, so no object can be shown as unused. " +
      "Retirement analysis requires execution statistics from the SAP system itself " +
      "(ST03N / SCMON / UPL); a source repository carries none. Dispositions below are derived " +
      "from findings alone."
    );
  }
  if (data.retirement.length === 0) {
    return "Usage data present; no objects met the retirement criteria.";
  }
  return null; // candidates exist → render the table
}
