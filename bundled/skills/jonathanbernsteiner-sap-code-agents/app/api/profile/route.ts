/**
 * Current user's profile: GET → identity + company; PATCH → display name.
 * Email and company are read-only here; password changes go through
 * Supabase Auth directly from the client.
 */
import { NextRequest } from "next/server";
import { requireUser } from "../../../lib/auth/server";
import { query } from "../../../lib/db/client";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const auth = await requireUser(req);
  if (auth instanceof Response) return auth;
  // last-used workspace (per user); the FK nulls out when it is deleted
  const [last] = await query<{ name: string }>(
    `select w.name from profiles p join workspaces w on w.id = p.last_workspace_id
     where p.user_id = $1`,
    [auth.userId]
  );
  return Response.json({
    email: auth.email,
    display_name: auth.displayName,
    role: auth.role,
    company: auth.companyName,
    last_workspace: last?.name ?? null,
  });
}

export async function PATCH(req: NextRequest) {
  const auth = await requireUser(req);
  if (auth instanceof Response) return auth;
  const body = await req.json().catch(() => null);
  const displayName = typeof body?.display_name === "string" ? body.display_name.trim() : null;
  if (displayName === null || displayName.length > 120) {
    return Response.json({ error: "expected { display_name } (max 120 chars)" }, { status: 400 });
  }
  await query(`update profiles set display_name = $2 where user_id = $1`, [
    auth.userId,
    displayName,
  ]);
  return Response.json({ ok: true, display_name: displayName });
}
