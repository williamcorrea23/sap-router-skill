/**
 * Chat history for one workspace: GET /api/chat/sessions?workspace=<name>
 * [&scope=mine|company]. Own sessions by default; scope=company adds
 * colleagues' sessions (read-only), never anything outside the company.
 */
import { NextRequest } from "next/server";
import { requireUser, resolveWorkspaceForCompany } from "../../../../lib/auth/server";
import { listSessions } from "../../../../lib/chat/store";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const auth = await requireUser(req);
  if (auth instanceof Response) return auth;
  const workspace = req.nextUrl.searchParams.get("workspace");
  const scope = req.nextUrl.searchParams.get("scope") === "company" ? "company" : "mine";
  if (!workspace) return Response.json({ error: "workspace is required" }, { status: 400 });
  const ws = await resolveWorkspaceForCompany(workspace, auth.companyId);
  if (!ws) return Response.json({ error: `workspace '${workspace}' not found` }, { status: 404 });
  return Response.json({
    sessions: await listSessions(ws.id, auth.companyId, auth.userId, scope),
  });
}
