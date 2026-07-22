/**
 * Persist the user's last-used workspace (per user, not per browser): the
 * /w/[id] layout records every visit; the app root ("/") routes back to it.
 * Company-scoped: only workspaces the caller can see can be recorded.
 */
import { NextRequest } from "next/server";
import { requireUser, resolveWorkspaceForCompany } from "../../../../lib/auth/server";
import { query } from "../../../../lib/db/client";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  const auth = await requireUser(req);
  if (auth instanceof Response) return auth;
  const body = await req.json().catch(() => null);
  const workspace = typeof body?.workspace === "string" ? body.workspace : null;
  if (!workspace) return Response.json({ error: "workspace required" }, { status: 400 });
  const ws = await resolveWorkspaceForCompany(workspace, auth.companyId);
  if (!ws) return Response.json({ error: "workspace not found" }, { status: 404 });
  await query(`update profiles set last_workspace_id = $2 where user_id = $1`, [auth.userId, ws.id]);
  return Response.json({ ok: true });
}
