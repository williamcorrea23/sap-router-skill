/**
 * Workspace list with headline counts — every number computed by SQL.
 * Company-scoped (Change Order 03): the caller's company's workspaces plus
 * the globally readable example workspaces.
 */
import { NextRequest } from "next/server";
import { requireUser } from "../../../lib/auth/server";
import { query } from "../../../lib/db/client";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const auth = await requireUser(req);
  if (auth instanceof Response) return auth;
  // Both lists depend only on the company — fetch them in parallel.
  const [rows, pendingJobs] = await Promise.all([
    query(
      `select w.name, w.source, w.kind, w.simulated_usage, w.seeded_at, w.source_branch,
            (w.kind = 'example') as is_example,
            (select count(*) from objects o where o.workspace_id = w.id) as objects,
            (select count(*) from objects o where o.workspace_id = w.id and o.parse_status = 'failed') as parse_failed,
            (select count(*) from call_edges e where e.workspace_id = w.id) as call_edges,
            (select count(*) from table_accesses t where t.workspace_id = w.id) as table_accesses,
            (select count(*) from usage_stats u where u.workspace_id = w.id) as usage_rows,
            (select count(*) from objects o where o.workspace_id = w.id and o.summary is not null) as summaries,
            (select count(*) from findings f where f.workspace_id = w.id and f.tier = 1 and not f.suppressed) as tier1_findings,
            (select count(*) from findings f where f.workspace_id = w.id and f.tier = 2 and not f.suppressed) as tier2_findings,
            (select count(*) from findings f where f.workspace_id = w.id and f.tier = 3 and not f.suppressed) as tier3_findings,
            (select jsonb_object_agg(g.grade, g.n)
             from (select og.grade, count(*) as n from object_risk_grades og
                   where og.workspace_id = w.id and og.grade is not null
                   group by og.grade) g) as grades,
            case when exists (select 1 from usage_stats u where u.workspace_id = w.id) then
              (select count(*) from usage_stats u
               where u.workspace_id = w.id and u.call_count_24m = 0
                 and not exists (select 1 from call_edges e
                                 where e.workspace_id = w.id and e.callee_id = u.object_id
                                   and e.caller_id <> u.object_id))
            end as retirement_candidates,
            (select to_jsonb(j) from (
               select ij.id, ij.status, ij.error, ij.files_parsed, ij.files_total,
                      ij.summaries_done, ij.summaries_planned, ij.created_at
               from ingestion_jobs ij
               where ij.company_id = $1
                 and (ij.workspace_id = w.id or ij.workspace_name = w.name)
               order by ij.created_at desc limit 1) j) as last_job,
            -- an in-flight report run, so a card can show progress in place
            -- instead of sending the user to the report tab to see it
            (select to_jsonb(r) from (
               select rr.id, rr.stage, rr.objects_done, rr.analyze_total
               from report_runs rr
               where rr.workspace_id = w.id and rr.finished_at is null
                 and rr.stage in ('queued', 'analyzing', 'validating', 'rendering')
               order by rr.started_at desc limit 1) r) as active_report_run
     from workspaces w
     where w.kind = 'example' or w.company_id = $1
     order by w.seeded_at desc nulls last, w.name`,
      [auth.companyId]
    ),
    // Ingestions that have no workspace row (yet): a fresh source being cloned/
    // parsed, or a failed attempt — the Connections page shows them as pending
    // sources with their pipeline status.
    query(
      `select distinct on (workspace_name)
            id, git_url, workspace_name, status, error, files_parsed, files_total,
            summaries_done, summaries_planned, created_at
     from ingestion_jobs
     where company_id = $1
       and status in ('queued','cloning','parsing','graph','summarizing','failed')
       and not exists (select 1 from workspaces w where w.name = ingestion_jobs.workspace_name)
     order by workspace_name, created_at desc`,
      [auth.companyId]
    ),
  ]);

  return Response.json({ workspaces: rows, pending_jobs: pendingJobs });
}

/**
 * B3 — delete a user-ingested workspace and all its rows (cascade).
 * DELETE /api/workspaces?name=<name>. Admin-only; example workspaces can
 * never be deleted.
 */
export async function DELETE(req: NextRequest) {
  const auth = await requireUser(req);
  if (auth instanceof Response) return auth;
  if (auth.role !== "admin") {
    return Response.json({ error: "only company admins can delete systems" }, { status: 403 });
  }
  const name = req.nextUrl.searchParams.get("name");
  if (!name) return Response.json({ error: "name required" }, { status: 400 });
  const rows = await query<{ id: string }>(
    `delete from workspaces where name = $1 and company_id = $2 and kind = 'ingested' returning id`,
    [name, auth.companyId]
  );
  if (rows.length === 0) {
    return Response.json({ error: "system not found (or not deletable)" }, { status: 404 });
  }
  await query(`delete from ingestion_jobs where workspace_id = $1 or (workspace_name = $2 and company_id = $3)`, [
    rows[0].id,
    name,
    auth.companyId,
  ]);
  return Response.json({ deleted: name });
}
