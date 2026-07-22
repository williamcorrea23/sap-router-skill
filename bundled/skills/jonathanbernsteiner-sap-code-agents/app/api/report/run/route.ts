/**
 * CO-06 — web-triggered report runs.
 *
 * POST { workspace }: pre-creates the report_runs row (stage 'queued'),
 * returns its id immediately and executes the unchanged runReport() job
 * after the response (same invocation, Fluid Compute). The pipeline UI polls
 * GET ?workspace= for the latest run's stage + counters — all SQL/job
 * counters, never LLM output.
 *
 * Example workspaces are read-only reference data (403) — their reports are
 * refreshed by the operator via `npm run report`, matching the CO-03 policy.
 */
import { NextRequest, after } from "next/server";
import { requireUser, resolveWorkspaceForCompany } from "../../../../lib/auth/server";
import { query } from "../../../../lib/db/client";
import { runReport } from "../../../../lib/report/job";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 300;

const STALL_MINUTES = 10;

export async function POST(req: NextRequest) {
  const auth = await requireUser(req);
  if (auth instanceof Response) return auth;
  let workspace: unknown;
  try {
    ({ workspace } = await req.json());
  } catch {
    return Response.json({ error: "JSON body with { workspace } required" }, { status: 400 });
  }
  if (typeof workspace !== "string" || !workspace.trim()) {
    return Response.json({ error: "workspace required" }, { status: 400 });
  }
  const ws = await resolveWorkspaceForCompany(workspace, auth.companyId);
  if (!ws) return Response.json({ error: "workspace not found" }, { status: 404 });
  if (ws.kind === "example") {
    return Response.json(
      { error: "example systems are read-only — their reports are refreshed by the operator" },
      { status: 403 }
    );
  }

  // one run at a time per workspace; a stalled run (dead worker) is failed
  const [active] = await query<{ id: string; stalled: boolean }>(
    `select id, started_at < now() - make_interval(mins => $2) as stalled
     from report_runs
     where workspace_id = $1 and stage not in ('done', 'failed')
     order by started_at desc limit 1`,
    [ws.id, STALL_MINUTES]
  );
  if (active && !active.stalled) {
    return Response.json({ runId: active.id, already_running: true }, { status: 409 });
  }
  if (active) {
    await query(
      `update report_runs set stage = 'failed', error = 'stalled — the worker did not finish' where id = $1`,
      [active.id]
    );
  }

  const [run] = await query<{ id: string }>(
    `insert into report_runs (workspace_id, stage) values ($1, 'queued') returning id`,
    [ws.id]
  );

  after(async () => {
    try {
      await runReport(ws.name, { runId: run.id, log: (s) => console.log(`[report ${run.id}] ${s}`) });
    } catch (e) {
      // runReport already persisted stage='failed' + error
      console.error(`[report ${run.id}] failed:`, (e as Error).message);
    }
  });
  return Response.json({ runId: run.id }, { status: 202 });
}

export async function GET(req: NextRequest) {
  const auth = await requireUser(req);
  if (auth instanceof Response) return auth;
  const workspace = req.nextUrl.searchParams.get("workspace");
  if (!workspace) return Response.json({ error: "workspace required" }, { status: 400 });
  const ws = await resolveWorkspaceForCompany(workspace, auth.companyId);
  if (!ws) return Response.json({ error: "workspace not found" }, { status: 404 });

  const [run] = await query<{
    id: string; stage: string; failed_stage: string | null; started_at: string;
    finished_at: string | null; objects_analyzed: number | null; objects_done: number;
    analyze_total: number | null; error: string | null;
  }>(
    `select id, stage, failed_stage, started_at, finished_at, objects_analyzed, objects_done,
            analyze_total, error
     from report_runs where workspace_id = $1
     order by started_at desc limit 1`,
    [ws.id]
  );
  if (!run) return Response.json({ run: null });

  const [tierRows, history] = await Promise.all([
    query<{ tier: number; n: string }>(
      `select tier, count(*) as n from findings
     where run_id = $1 and not suppressed group by tier`,
      [run.id]
    ),
    // Run history (report restructure): the last runs with their frozen
    // snapshot numbers — findings are only persisted for the latest run, so
    // older entries state what their snapshot froze at finish time.
    query<{
      id: string; stage: string; started_at: string; finished_at: string | null;
      objects_analyzed: number | null; error: string | null;
      tier1: number | null; tier2: number | null; retirement: number | null;
    }>(
      `select id, stage, started_at, finished_at, objects_analyzed, error,
            (snapshot->'tiers'->>'1')::int as tier1,
            (snapshot->'tiers'->>'2')::int as tier2,
            (snapshot->>'retirement_candidates')::int as retirement
     from report_runs where workspace_id = $1
     order by started_at desc limit 20`,
      [ws.id]
    ),
  ]);
  const tiers: Record<string, number> = { "1": 0, "2": 0, "3": 0 };
  for (const t of tierRows) tiers[String(t.tier)] = Number(t.n);
  return Response.json({ run, tiers, history });
}
