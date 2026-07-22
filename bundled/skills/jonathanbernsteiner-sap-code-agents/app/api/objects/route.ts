/**
 * Object list for a workspace: GET /api/objects?workspace=<name>&q=<filter>
 * Usage numbers come straight from SQL joins; simulated flag included.
 */
import { NextRequest } from "next/server";
import { requireUser, resolveWorkspaceForCompany } from "../../../lib/auth/server";
import { query } from "../../../lib/db/client";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const auth = await requireUser(req);
  if (auth instanceof Response) return auth;
  const workspace = req.nextUrl.searchParams.get("workspace");
  const q = req.nextUrl.searchParams.get("q") ?? "";
  // CO-04/05 filters: grade 'A'|'B'|'C'|'D'|'Ungraded', process area by name
  const grade = req.nextUrl.searchParams.get("grade") ?? "";
  const processArea = req.nextUrl.searchParams.get("process_area") ?? "";
  if (!workspace) return Response.json({ error: "workspace required" }, { status: 400 });
  const ws = await resolveWorkspaceForCompany(workspace, auth.companyId);
  if (!ws) return Response.json({ error: "workspace not found" }, { status: 404 });

  const rows = await query(
    `select o.name, o.object_type, o.category, o.parse_status,
            left(coalesce(o.summary, ''), 200) as summary_snippet,
            u.call_count_24m, u.last_executed, u.simulated,
            g.grade,
            (select array_agg(pa.process_area order by pa.process_area)
             from object_process_areas pa where pa.object_id = o.id) as process_areas,
            (select count(*) from call_edges e where e.workspace_id = o.workspace_id and (e.callee_id = o.id or e.callee_name = o.name)) as inbound_refs
     from objects o
     left join usage_stats u on u.object_id = o.id
     left join object_risk_grades g on g.object_id = o.id
     where o.workspace_id = $1 and ($2 = '' or o.name ilike '%' || $2 || '%')
       and ($3 = '' or coalesce(g.grade, 'Ungraded') = $3)
       and ($4 = '' or exists (select 1 from object_process_areas pa
                               where pa.object_id = o.id and pa.process_area = $4))
     order by inbound_refs desc, o.name
     limit 800`,
    [ws.id, q, grade, processArea]
  );
  return Response.json({ objects: rows });
}
