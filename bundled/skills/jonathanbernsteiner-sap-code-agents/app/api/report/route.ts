/**
 * Migration report data: GET /api/report?workspace=<name>[&debug=1]
 * All data comes from lib/report/data.ts (shared with the exports):
 * suppressed findings excluded, note numbers gated on verified sources,
 * headline numbers SQL-only. debug=1 additionally returns suppressed
 * findings for the debug view.
 */
import { NextRequest } from "next/server";
import { requireUser, resolveWorkspaceForCompany } from "../../../lib/auth/server";
import { getReportData } from "../../../lib/report/data";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const auth = await requireUser(req);
  if (auth instanceof Response) return auth;
  const workspace = req.nextUrl.searchParams.get("workspace");
  if (!workspace) return Response.json({ error: "workspace required" }, { status: 400 });
  if (!(await resolveWorkspaceForCompany(workspace, auth.companyId))) {
    return Response.json({ error: "workspace not found" }, { status: 404 });
  }
  const debug = req.nextUrl.searchParams.get("debug") === "1";
  const data = await getReportData(workspace, { includeSuppressed: debug });
  if (!data) return Response.json({ error: "workspace not found" }, { status: 404 });
  return Response.json(data);
}
