/**
 * Invite a member (admins only): POST { email, role } → invitation row +
 * best-effort Supabase invite email. The response always includes the invite
 * link so the admin can hand it over directly when no mailer is configured.
 */
import { randomBytes } from "node:crypto";
import { NextRequest } from "next/server";
import { supabaseAdmin } from "../../../../lib/auth/admin";
import { requireUser } from "../../../../lib/auth/server";
import { query } from "../../../../lib/db/client";
import { siteUrl } from "../../../../lib/config";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const INVITE_TTL_DAYS = 7;

export async function POST(req: NextRequest) {
  const auth = await requireUser(req);
  if (auth instanceof Response) return auth;
  if (auth.role !== "admin") return Response.json({ error: "admins only" }, { status: 403 });

  const body = await req.json().catch(() => null);
  const email = typeof body?.email === "string" ? body.email.trim().toLowerCase() : "";
  const role = body?.role === "admin" ? "admin" : "member";
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return Response.json({ error: "a valid email is required" }, { status: 400 });
  }

  const existing = await query<{ user_id: string }>(
    `select p.user_id from profiles p join auth.users u on u.id = p.user_id
     where lower(u.email) = $1`,
    [email]
  );
  if (existing.length > 0) {
    return Response.json({ error: "this email already belongs to a member" }, { status: 409 });
  }

  const token = randomBytes(24).toString("base64url");
  const rows = await query<{ id: string; expires_at: string }>(
    `insert into invitations (company_id, email, role, invited_by, token, expires_at)
     values ($1, $2, $3, $4, $5, now() + interval '${INVITE_TTL_DAYS} days')
     returning id, expires_at`,
    [auth.companyId, email, role, auth.userId, token]
  );
  const inviteUrl = `${siteUrl()}/invite/${token}`;

  // Best-effort email via Supabase's invite mailer; the copyable link is the
  // fallback (and works even if the email never arrives).
  let emailSent = false;
  try {
    const { error } = await supabaseAdmin().auth.admin.inviteUserByEmail(email, {
      redirectTo: inviteUrl,
    });
    emailSent = !error;
  } catch {
    emailSent = false;
  }

  return Response.json({
    id: rows[0].id,
    email,
    role,
    expires_at: rows[0].expires_at,
    invite_url: inviteUrl,
    email_sent: emailSent,
  });
}
