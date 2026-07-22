/**
 * Public (pre-auth) invitation lookup: GET ?token= → who is being invited
 * where, so the accept page can render. Reveals nothing beyond what the
 * invite link itself already grants.
 */
import { NextRequest } from "next/server";
import { query } from "../../../../lib/db/client";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const token = req.nextUrl.searchParams.get("token") ?? "";
  if (!token) return Response.json({ error: "token required" }, { status: 400 });
  const rows = await query<{
    email: string;
    role: string;
    company: string;
    expires_at: string;
    accepted_at: string | null;
  }>(
    `select i.email, i.role, c.name as company, i.expires_at, i.accepted_at
     from invitations i join companies c on c.id = i.company_id
     where i.token = $1`,
    [token]
  );
  const inv = rows[0];
  if (!inv) return Response.json({ valid: false, reason: "not_found" });
  if (inv.accepted_at) return Response.json({ valid: false, reason: "accepted" });
  if (new Date(inv.expires_at).getTime() < Date.now()) {
    return Response.json({ valid: false, reason: "expired" });
  }
  return Response.json({ valid: true, email: inv.email, role: inv.role, company: inv.company });
}
