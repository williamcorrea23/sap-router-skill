"use client";

/**
 * Browser Supabase client (cookie-based session, shared with the server via
 * @supabase/ssr). Used only for auth flows — sign in/out, password reset,
 * password change. Data access always goes through the API routes.
 */
import { createBrowserClient } from "@supabase/ssr";

export function supabaseBrowser() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}
