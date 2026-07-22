/**
 * Company settings data (admins only): member list + pending invitations.
 */
import { NextRequest } from "next/server";
import { requireUser } from "../../../lib/auth/server";
import { query } from "../../../lib/db/client";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const auth = await requireUser(req);
  if (auth instanceof Response) return auth;
  if (auth.role !== "admin") return Response.json({ error: "admins only" }, { status: 403 });

  const [members, invitations] = await Promise.all([
    query(
      `select p.user_id, p.display_name, p.role, p.created_at, u.email
       from profiles p join auth.users u on u.id = p.user_id
       where p.company_id = $1
       order by p.created_at`,
      [auth.companyId]
    ),
    query(
      `select id, email, role, created_at, expires_at
       from invitations
       where company_id = $1 and accepted_at is null and expires_at > now()
       order by created_at desc`,
      [auth.companyId]
    ),
  ]);
  return Response.json({ company: auth.companyName, members, invitations });
}
