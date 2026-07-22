/**
 * Accept an invitation: POST { token, password, display_name } →
 * auth user (created, or updated if Supabase's invite email pre-created it)
 * + profile row in the inviting company + invitation marked accepted.
 * The client signs in with the password afterwards. Public route: the
 * token IS the authorization.
 */
import { NextRequest } from "next/server";
import { findAuthUserByEmail, supabaseAdmin } from "../../../../lib/auth/admin";
import { query } from "../../../../lib/db/client";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => null);
  const token = typeof body?.token === "string" ? body.token : "";
  const password = typeof body?.password === "string" ? body.password : "";
  const displayName = typeof body?.display_name === "string" ? body.display_name.trim() : "";
  if (!token || password.length < 8) {
    return Response.json(
      { error: "token and a password of at least 8 characters are required" },
      { status: 400 }
    );
  }

  const rows = await query<{
    id: string;
    company_id: string;
    email: string;
    role: "admin" | "member";
    expires_at: string;
    accepted_at: string | null;
  }>(
    `select id, company_id, email, role, expires_at, accepted_at
     from invitations where token = $1`,
    [token]
  );
  const inv = rows[0];
  if (!inv || inv.accepted_at || new Date(inv.expires_at).getTime() < Date.now()) {
    return Response.json({ error: "this invitation is invalid or has expired" }, { status: 400 });
  }

  const admin = supabaseAdmin();
  let userId: string;
  const existing = await findAuthUserByEmail(inv.email);
  if (existing) {
    // An auth user without a profile was pre-created by Supabase's invite
    // email for THIS flow. One WITH a profile is an established account —
    // never touch its password from an invite link (the inviting admin holds
    // that link too; overwriting would allow taking over the account), and
    // don't burn the token on a no-op.
    const profiles = await query<{ company_id: string }>(
      `select company_id from profiles where user_id = $1`,
      [existing.id]
    );
    if (profiles.length > 0) {
      return Response.json(
        { error: "an account with this email already exists — sign in with your existing password" },
        { status: 409 }
      );
    }
    // Pre-created by Supabase's invite email — set the chosen password and
    // confirm the address (clicking wasn't required in the link-only flow).
    const { data, error } = await admin.auth.admin.updateUserById(existing.id, {
      password,
      email_confirm: true,
    });
    if (error || !data.user) {
      return Response.json({ error: error?.message ?? "could not set password" }, { status: 500 });
    }
    userId = data.user.id;
  } else {
    const { data, error } = await admin.auth.admin.createUser({
      email: inv.email,
      password,
      email_confirm: true,
    });
    if (error || !data.user) {
      return Response.json({ error: error?.message ?? "could not create account" }, { status: 500 });
    }
    userId = data.user.id;
  }

  await query(
    `insert into profiles (user_id, company_id, display_name, role)
     values ($1, $2, $3, $4)
     on conflict (user_id) do nothing`,
    [userId, inv.company_id, displayName, inv.role]
  );
  await query(`update invitations set accepted_at = now() where id = $1`, [inv.id]);

  return Response.json({ ok: true, email: inv.email });
}
