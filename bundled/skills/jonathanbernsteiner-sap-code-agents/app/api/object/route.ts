/**
 * Object detail: GET /api/object?workspace=<name>&name=<object>
 * Includes source, summary, edges, table accesses, usage, findings and the
 * computed dependency diagram (Mermaid text — computed, never LLM-written).
 */
import { NextRequest } from "next/server";
import { requireUser, resolveWorkspaceForCompany } from "../../../lib/auth/server";
import { query } from "../../../lib/db/client";
import { diagramForObject } from "../../../lib/diagram";
import { ensureSummary } from "../../../lib/ingest/pipeline";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const auth = await requireUser(req);
  if (auth instanceof Response) return auth;
  const workspace = req.nextUrl.searchParams.get("workspace");
  const name = (req.nextUrl.searchParams.get("name") ?? "").toUpperCase();
  if (!workspace || !name) return Response.json({ error: "workspace and name required" }, { status: 400 });

  const ws = await resolveWorkspaceForCompany(workspace, auth.companyId);
  if (!ws) return Response.json({ error: "workspace not found" }, { status: 404 });
  const wsId = ws.id;
  // provenance for file:line deep links (null source_branch falls back to
  // HEAD) — independent of the object lookup, so fetched in parallel with it
  const [wsSourceRows, objects] = await Promise.all([
    query<{ source: string; source_branch: string | null }>(
      `select source, source_branch from workspaces where id = $1`,
      [wsId]
    ),
    query<{ id: string; [k: string]: unknown }>(
      `select id, name, object_type, category, files, parse_status, parse_errors,
              summary, summary_model, source
       from objects where workspace_id = $1 and name = $2
       order by case object_type when 'CLAS' then 0 when 'INTF' then 1 when 'PROG' then 2 else 3 end
       limit 1`,
      [wsId, name]
    ),
  ]);
  const [wsSource] = wsSourceRows;
  if (objects.length === 0) return Response.json({ error: "object not found" }, { status: 404 });
  const obj = objects[0];

  // Everything below depends only on the resolved object/workspace ids — one
  // parallel batch instead of five sequential round-trips. The lazy summary
  // and the diagram are best-effort: a failure there degrades the detail view
  // (no summary / no diagram) instead of failing the whole request.
  const [usageRows, findings, gradeRows, processAreas, diagram, lazySummary] = await Promise.all([
    query(
      `select call_count_24m, last_executed, simulated from usage_stats where workspace_id = $1 and object_id = $2`,
      [wsId, obj.id]
    ),
    query(
      `select f.tier, f.title, f.detail, f.evidence_file, f.evidence_line, f.evidence,
              f.validator, f.validator_passed, r.severity, r.replacement,
              case when r.source_status = 'verified' then r.sap_note else null end as sap_note,
              case when r.source_status = 'verified' then r.source_url else null end as source_url
       from findings f left join incompatibility_rules r on r.id = f.rule_id
       where f.workspace_id = $1 and f.object_id = $2 and not f.suppressed
       order by f.tier, f.title`,
      [wsId, obj.id]
    ),
    query<{ grade: string | null }>(
      `select grade from object_risk_grades where object_id = $1`,
      [obj.id]
    ),
    query<{ process_area: string }>(
      `select process_area from object_process_areas where object_id = $1 order by process_area`,
      [obj.id]
    ).catch(() => []), // view arrives with Change Order 05
    diagramForObject(wsId, name).catch(() => null),
    // B2 — lazy summaries: objects beyond the ingestion-time cap get their
    // summary generated (and stored + traced) on first access.
    obj.summary
      ? Promise.resolve(null)
      : ensureSummary(wsId, obj.id).catch(() => null),
  ]);
  const [usage] = usageRows;
  const [gradeRow] = gradeRows;
  if (lazySummary) {
    obj.summary = lazySummary;
    obj.summary_model = (
      await query<{ summary_model: string }>(`select summary_model from objects where id = $1`, [obj.id])
    )[0]?.summary_model;
  }

  return Response.json({
    object: obj,
    workspace: {
      kind: ws.kind,
      source: wsSource?.source ?? null,
      source_branch: wsSource?.source_branch ?? null,
    },
    grade: gradeRow?.grade ?? null,
    process_areas: processAreas.map((p) => p.process_area),
    usage: usage ?? null,
    simulated_usage: ws.simulated_usage,
    findings,
    mermaid: diagram?.mermaid ?? null,
    // set when the diagram falls back to internal structure because the
    // object has no workspace/external dependencies at all
    diagram_internal_only: diagram?.internalOnly ?? false,
  });
}
