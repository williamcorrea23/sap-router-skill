/**
 * Auth callback: Supabase email links (password recovery, invites) land here
 * with a one-time code; we exchange it for a cookie session and forward to
 * `next` (e.g. /reset-password). Public route by design.
 */
import { NextRequest, NextResponse } from "next/server";
import { createSupabaseServerClient } from "../../../lib/auth/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const code = req.nextUrl.searchParams.get("code");
  const next = req.nextUrl.searchParams.get("next") ?? "/";
  // Only ever forward within the app.
  const target = next.startsWith("/") ? next : "/";

  if (code) {
    const supabase = await createSupabaseServerClient();
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    if (!error) return NextResponse.redirect(new URL(target, req.nextUrl.origin));
  }
  const url = new URL("/login", req.nextUrl.origin);
  url.searchParams.set("error", "auth-link");
  return NextResponse.redirect(url);
}
