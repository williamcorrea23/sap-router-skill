/**
 * Remove a member (admins only). Revokes access — deletes the profile and
 * the auth account — but keeps their past chats (created_by goes null via
 * FK). Admins cannot remove themselves.
 */
import { NextRequest } from "next/server";
import { supabaseAdmin } from "../../../../../lib/auth/admin";
import { requireUser } from "../../../../../lib/auth/server";
import { query } from "../../../../../lib/db/client";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function DELETE(req: NextRequest, ctx: { params: Promise<{ userId: string }> }) {
  const auth = await requireUser(req);
  if (auth instanceof Response) return auth;
  if (auth.role !== "admin") return Response.json({ error: "admins only" }, { status: 403 });
  const { userId } = await ctx.params;
  if (userId === auth.userId) {
    return Response.json({ error: "you cannot remove yourself" }, { status: 400 });
  }
  const rows = await query<{ user_id: string }>(
    `select user_id from profiles where user_id = $1 and company_id = $2`,
    [userId, auth.companyId]
  );
  if (rows.length === 0) return Response.json({ error: "member not found" }, { status: 404 });

  // Deleting the auth user cascades to the profile (FK) and nulls
  // chat_sessions.created_by — past chats stay with the company.
  const { error } = await supabaseAdmin().auth.admin.deleteUser(userId);
  if (error) return Response.json({ error: error.message }, { status: 500 });
  return Response.json({ removed: true });
}
