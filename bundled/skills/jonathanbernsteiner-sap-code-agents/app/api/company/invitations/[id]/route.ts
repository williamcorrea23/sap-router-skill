/**
 * Revoke a pending invitation (admins only).
 */
import { NextRequest } from "next/server";
import { requireUser } from "../../../../../lib/auth/server";
import { query } from "../../../../../lib/db/client";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function DELETE(req: NextRequest, ctx: { params: Promise<{ id: string }> }) {
  const auth = await requireUser(req);
  if (auth instanceof Response) return auth;
  if (auth.role !== "admin") return Response.json({ error: "admins only" }, { status: 403 });
  const { id } = await ctx.params;
  const rows = await query<{ id: string }>(
    `delete from invitations
     where id = $1 and company_id = $2 and accepted_at is null
     returning id`,
    [id, auth.companyId]
  );
  if (rows.length === 0) return Response.json({ error: "invitation not found" }, { status: 404 });
  return Response.json({ revoked: true });
}
