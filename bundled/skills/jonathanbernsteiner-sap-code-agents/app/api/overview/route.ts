/**
 * System Overview (Change Order 04): GET /api/overview?workspace=<name>
 * Every number is computed by SQL — grades come from the object_risk_grades
 * view, findings/severity counts from the findings table joined to the seeded
 * rule severities, process areas (Change Order 05) from object_process_areas.
 */
import { NextRequest } from "next/server";
import { requireUser, resolveWorkspaceForCompany } from "../../../lib/auth/server";
import { query } from "../../../lib/db/client";
import { NOT_AVAILABLE } from "../../../lib/empty-values";
import { recommendedActionsFromCounts } from "../../../lib/report/data";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const auth = await requireUser(req);
  if (auth instanceof Response) return auth;
  const workspace = req.nextUrl.searchParams.get("workspace");
  if (!workspace) return Response.json({ error: "workspace required" }, { status: 400 });
  const ws = await resolveWorkspaceForCompany(workspace, auth.companyId);
  if (!ws) return Response.json({ error: "workspace not found" }, { status: 404 });

  // All aggregates depend only on ws.id — run them in parallel instead
  // of paying that many sequential round-trips on this hot landing view.
  const [
    headerRows, categories, runRows, gradeRows, severity, retirementRows, processAreas,
    dispositionRows, netRows,
  ] =
    await Promise.all([
      query<{
        objects: string; edges: string; accesses: string; parse_ok: string; usage_rows: string;
        affected_objects: string;
      }>(
        `select
           (select count(*) from objects where workspace_id = $1) as objects,
           (select count(*) from call_edges where workspace_id = $1) as edges,
           (select count(*) from table_accesses where workspace_id = $1) as accesses,
           (select count(*) from objects where workspace_id = $1 and parse_status = 'ok') as parse_ok,
           (select count(*) from usage_stats where workspace_id = $1) as usage_rows,
           (select count(distinct object_id) from findings
             where workspace_id = $1 and tier in (1,2) and not suppressed) as affected_objects`,
        [ws.id]
      ),
      query<{ category: string | null; n: string }>(
        `select category, count(*) as n from objects where workspace_id = $1
         group by category order by count(*) desc, category`,
        [ws.id]
      ),
      query<{ id: string; finished_at: string }>(
        `select id, finished_at from report_runs
         where workspace_id = $1 and finished_at is not null
         order by finished_at desc limit 1`,
        [ws.id]
      ),
      query<{ grade: string | null; n: string }>(
        `select grade, count(*) as n from object_risk_grades
         where workspace_id = $1 group by grade`,
        [ws.id]
      ),
      // Tier-1/Tier-2 counts by rule severity from the latest run's persisted
      // findings. Tier-2 findings without a rule (LLM, evidence-linked) have no
      // seeded severity and are reported as 'unrated'.
      query<{ tier: number; severity: string; n: string }>(
        `select f.tier, coalesce(r.severity, 'unrated') as severity, count(*) as n
         from findings f left join incompatibility_rules r on r.id = f.rule_id
         where f.workspace_id = $1 and not f.suppressed and f.tier in (1, 2)
         group by f.tier, coalesce(r.severity, 'unrated')
         order by f.tier, severity`,
        [ws.id]
      ),
      // identical criteria to the report's retirement list (lib/report/data.ts)
      query<{ n: string }>(
        `select count(*) as n
         from usage_stats u
         where u.workspace_id = $1 and u.call_count_24m = 0
           and not exists (select 1 from call_edges e
                           where e.workspace_id = $1 and e.callee_id = u.object_id and e.caller_id <> u.object_id)`,
        [ws.id]
      ),
      query<{ process_area: string; n: string }>(
        `select process_area, count(distinct object_id) as n
         from object_process_areas where workspace_id = $1
         group by process_area order by count(distinct object_id) desc, process_area`,
        [ws.id]
      ).catch(() => []), // view arrives with Change Order 05
      // CO-09 dispositions — the overview closes with the same deterministic
      // recommendation sentence the report states, built from these counts
      query<{ disposition: string | null; n: string }>(
        `select disposition, count(*) as n from object_dispositions
         where workspace_id = $1 and disposition is not null
         group by disposition`,
        [ws.id]
      ).catch(() => []),
      query<{ tier1: string; tier2: string }>(
        `select
           count(*) filter (where f.tier = 1)::int as tier1,
           count(*) filter (where f.tier = 2)::int as tier2
         from findings f
         join object_dispositions d on d.object_id = f.object_id
         where f.workspace_id = $1 and not f.suppressed and d.disposition = 'retire'`,
        [ws.id]
      ).catch(() => []),
    ]);
  const [header] = headerRows;
  const [run] = runRows;
  const [retirement] = retirementRows;
  const [net] = netRows;
  const grades: Record<string, number> = { A: 0, B: 0, C: 0, D: 0, Ungraded: 0 };
  for (const r of gradeRows) grades[r.grade ?? "Ungraded"] = Number(r.n);

  const total = Number(header.objects);
  const parseOk = Number(header.parse_ok);
  const usageRows = Number(header.usage_rows);
  return Response.json({
    workspace: ws.name,
    kind: ws.kind,
    simulated_usage: ws.simulated_usage,
    header: {
      objects: total,
      edges: Number(header.edges),
      table_accesses: Number(header.accesses),
      parse_ok: parseOk,
      parse_rate: total > 0 ? `${((100 * parseOk) / total).toFixed(2)}%` : NOT_AVAILABLE,
      categories: categories.map((c) => ({ category: c.category, n: Number(c.n) })),
    },
    run: run ?? null,
    grades,
    usage: {
      rows: usageRows,
      coverage_pct: total > 0 ? Math.round((100 * usageRows) / total) : 0,
    },
    findings_by_severity: severity.map((s) => ({ tier: s.tier, severity: s.severity, n: Number(s.n) })),
    affected_objects: Number(header.affected_objects),
    retirement_candidates: usageRows > 0 ? Number(retirement.n) : null,
    // CO-09 dispositions, so the overview can show findings → grades → actions
    dispositions: Object.fromEntries(dispositionRows.map((d) => [d.disposition as string, Number(d.n)])),
    recommended_actions: run
      ? recommendedActionsFromCounts(
          new Map(dispositionRows.map((d) => [d.disposition as string, Number(d.n)])),
          net ? { tier1: Number(net.tier1), tier2: Number(net.tier2) } : null
        )
      : null,
    process_areas: processAreas.map((p) => ({ process_area: p.process_area, n: Number(p.n) })),
  });
}
