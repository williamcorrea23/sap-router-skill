/**
 * Server-side auth (Change Order 03). Identity comes from Supabase Auth
 * (cookie session via @supabase/ssr, or a Bearer access token for API
 * clients/tests); company membership comes from the profiles table, read
 * over the owner pg connection. Every API route calls requireUser() and
 * scopes its queries by the returned company — RLS is defense in depth,
 * never the only line.
 */
import { createServerClient } from "@supabase/ssr";
import { createClient, type User } from "@supabase/supabase-js";
import { cookies } from "next/headers";
import type { NextRequest } from "next/server";
import { query } from "../db/client";

export interface AuthContext {
  userId: string;
  email: string;
  companyId: string;
  companyName: string;
  role: "admin" | "member";
  displayName: string;
}

function supabaseEnv() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!url || !anonKey) throw new Error("NEXT_PUBLIC_SUPABASE_URL / _ANON_KEY not set");
  return { url, anonKey };
}

/** Cookie-bound Supabase client for RSC / route handlers. */
export async function createSupabaseServerClient() {
  const { url, anonKey } = supabaseEnv();
  const cookieStore = await cookies();
  return createServerClient(url, anonKey, {
    cookies: {
      getAll: () => cookieStore.getAll(),
      setAll: (toSet) => {
        try {
          toSet.forEach(({ name, value, options }) => cookieStore.set(name, value, options));
        } catch {
          // Called from a Server Component — middleware refreshes sessions.
        }
      },
    },
  });
}

async function userFromBearer(req: NextRequest): Promise<User | null> {
  const header = req.headers.get("authorization") ?? "";
  if (!header.toLowerCase().startsWith("bearer ")) return null;
  const token = header.slice(7).trim();
  if (!token) return null;
  const { url, anonKey } = supabaseEnv();
  const bare = createClient(url, anonKey, {
    auth: { autoRefreshToken: false, persistSession: false },
  });
  const { data, error } = await bare.auth.getUser(token);
  return error ? null : data.user;
}

/** The signed-in Supabase user (Bearer token first, then cookie session). */
export async function getAuthUser(req?: NextRequest): Promise<User | null> {
  if (req) {
    const bearerUser = await userFromBearer(req);
    if (bearerUser) return bearerUser;
  }
  const supabase = await createSupabaseServerClient();
  const { data } = await supabase.auth.getUser();
  return data.user ?? null;
}

/**
 * Auth + membership for API routes. Returns the AuthContext, or a ready
 * 401/403 Response the route must return as-is.
 */
export async function requireUser(req?: NextRequest): Promise<AuthContext | Response> {
  const user = await getAuthUser(req);
  if (!user) return Response.json({ error: "not authenticated" }, { status: 401 });
  const rows = await query<{
    company_id: string;
    company_name: string;
    role: "admin" | "member";
    display_name: string;
  }>(
    `select p.company_id, c.name as company_name, p.role, p.display_name
     from profiles p join companies c on c.id = p.company_id
     where p.user_id = $1`,
    [user.id]
  );
  if (rows.length === 0) {
    return Response.json({ error: "no company membership for this account" }, { status: 403 });
  }
  return {
    userId: user.id,
    email: user.email ?? "",
    companyId: rows[0].company_id,
    companyName: rows[0].company_name,
    role: rows[0].role,
    displayName: rows[0].display_name,
  };
}

export interface WorkspaceAccess {
  id: string;
  name: string;
  kind: "example" | "ingested";
  simulated_usage: boolean;
  company_id: string;
}

/**
 * Resolve a workspace the given company may see: its own, or any example
 * workspace (globally readable, read-only). Returns null when the workspace
 * does not exist OR belongs to another company — indistinguishable on
 * purpose.
 */
export async function resolveWorkspaceForCompany(
  name: string,
  companyId: string
): Promise<WorkspaceAccess | null> {
  const rows = await query<WorkspaceAccess>(
    `select id, name, kind, simulated_usage, company_id
     from workspaces where name = $1 and (kind = 'example' or company_id = $2)`,
    [name, companyId]
  );
  return rows[0] ?? null;
}
