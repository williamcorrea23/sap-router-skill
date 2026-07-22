/**
 * Change Order 03 gate: a user from company B can never read company A's
 * rows. Verified two independent ways:
 *
 *  1. API: a real `next dev` server is spawned and hit with two test users
 *     (Bearer tokens) — workspace list, objects, chat sessions.
 *  2. RLS: the same checks straight against Postgres through the anon key —
 *     the defense that remains if app-level checks ever regress.
 *
 * Plus the invitation-acceptance journey (token → account → profile → login).
 * Everything is created under names prefixed __tenancy_test and removed in
 * teardown. Requires .env.local (DATABASE_URL + Supabase keys); the suite
 * skips itself when those are missing.
 */
import { spawn, type ChildProcess } from "node:child_process";
import { randomBytes } from "node:crypto";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { Client } from "pg";
import { afterAll, beforeAll, describe, expect, it } from "vitest";

// vitest does not load .env.local (unit tests must stay env-free) — this
// suite needs it, so parse it directly.
try {
  const env = readFileSync(join(__dirname, "..", ".env.local"), "utf8");
  for (const line of env.split("\n")) {
    const m = line.match(/^([A-Z_]+)=(.*)$/);
    if (m && !process.env[m[1]]) process.env[m[1]] = m[2];
  }
} catch {
  // no .env.local — suite will skip
}

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL;
const ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
const SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
const DATABASE_URL = process.env.DATABASE_URL;
const hasEnv = !!(SUPABASE_URL && ANON_KEY && SERVICE_KEY && DATABASE_URL);

const PORT = 3199;
const BASE = `http://localhost:${PORT}`;
const PREFIX = "__tenancy_test";
const EMAIL_A = `${PREFIX}-a@example.com`;
const EMAIL_B = `${PREFIX}-b@example.com`;
const EMAIL_C = `${PREFIX}-c@example.com`;
const PASSWORD = "tenancy-test-pw-1";

describe.runIf(hasEnv)("company-level tenancy isolation", () => {
  let db: Client;
  let admin: SupabaseClient;
  let server: ChildProcess | undefined;
  let companyA: string;
  let companyB: string;
  let workspaceA: string;
  let sessionA: string;
  let tokenA: string;
  let tokenB: string;

  async function deleteTestUsers() {
    const { data } = await admin.auth.admin.listUsers({ page: 1, perPage: 1000 });
    for (const u of data?.users ?? []) {
      if ((u.email ?? "").startsWith(PREFIX)) await admin.auth.admin.deleteUser(u.id);
    }
  }

  async function createUser(email: string, companyId: string): Promise<string> {
    const { data, error } = await admin.auth.admin.createUser({
      email,
      password: PASSWORD,
      email_confirm: true,
    });
    if (error || !data.user) throw new Error(`createUser ${email}: ${error?.message}`);
    await db.query(
      `insert into profiles (user_id, company_id, display_name, role) values ($1, $2, $3, 'admin')`,
      [data.user.id, companyId, email.split("@")[0]]
    );
    return data.user.id;
  }

  async function signIn(email: string): Promise<string> {
    const client = createClient(SUPABASE_URL!, ANON_KEY!, {
      auth: { persistSession: false, autoRefreshToken: false },
    });
    const { data, error } = await client.auth.signInWithPassword({ email, password: PASSWORD });
    if (error || !data.session) throw new Error(`signIn ${email}: ${error?.message}`);
    return data.session.access_token;
  }

  /** Anon-key Postgres access as a signed-in user — exercises RLS directly. */
  function rlsClient(token: string): SupabaseClient {
    return createClient(SUPABASE_URL!, ANON_KEY!, {
      auth: { persistSession: false, autoRefreshToken: false },
      global: { headers: { Authorization: `Bearer ${token}` } },
    });
  }

  async function api(path: string, token?: string, init?: RequestInit) {
    return fetch(`${BASE}${path}`, {
      ...init,
      headers: {
        ...(init?.headers ?? {}),
        ...(token ? { authorization: `Bearer ${token}` } : {}),
      },
    });
  }

  beforeAll(async () => {
    db = new Client({ connectionString: DATABASE_URL });
    await db.connect();
    admin = createClient(SUPABASE_URL!, SERVICE_KEY!, {
      auth: { persistSession: false, autoRefreshToken: false },
    });

    // Idempotent cleanup of any earlier aborted run.
    await deleteTestUsers();
    await db.query(`delete from companies where name like '${PREFIX}%'`);

    companyA = (
      await db.query(`insert into companies (name) values ('${PREFIX}_company_a') returning id`)
    ).rows[0].id;
    companyB = (
      await db.query(`insert into companies (name) values ('${PREFIX}_company_b') returning id`)
    ).rows[0].id;

    const userA = await createUser(EMAIL_A, companyA);
    await createUser(EMAIL_B, companyB);

    // Company A's private (ingested) workspace with an object and a chat.
    workspaceA = (
      await db.query(
        `insert into workspaces (name, source, kind, company_id)
         values ('${PREFIX}-private-ws', 'file:///tenancy-test', 'ingested', $1) returning id`,
        [companyA]
      )
    ).rows[0].id;
    await db.query(
      `insert into objects (workspace_id, name, object_type, parse_status, source)
       values ($1, 'ZCL_TENANCY_SECRET', 'CLAS', 'ok', 'CLASS zcl_tenancy_secret DEFINITION. ENDCLASS.')`,
      [workspaceA]
    );
    sessionA = (
      await db.query(
        `insert into chat_sessions (workspace_id, company_id, created_by, title)
         values ($1, $2, $3, 'A-private conversation') returning id`,
        [workspaceA, companyA, userA]
      )
    ).rows[0].id;
    await db.query(
      `insert into chat_messages (session_id, role, content_md) values ($1, 'user', 'secret question')`,
      [sessionA]
    );

    tokenA = await signIn(EMAIL_A);
    tokenB = await signIn(EMAIL_B);

    // Real HTTP server for the API half of the gate.
    server = spawn("npx", ["next", "dev", "-p", String(PORT)], {
      cwd: join(__dirname, ".."),
      stdio: "ignore",
      detached: true,
    });
    const deadline = Date.now() + 90_000;
    for (;;) {
      try {
        const res = await fetch(`${BASE}/login`);
        if (res.status < 500) break;
      } catch {
        // not up yet
      }
      if (Date.now() > deadline) throw new Error("next dev did not come up on port " + PORT);
      await new Promise((r) => setTimeout(r, 1000));
    }
  }, 150_000);

  afterAll(async () => {
    if (server?.pid) {
      try {
        process.kill(-server.pid, "SIGTERM");
      } catch {
        server.kill("SIGTERM");
      }
    }
    if (admin) await deleteTestUsers();
    if (db) {
      await db.query(`delete from companies where name like '${PREFIX}%'`);
      await db.end();
    }
  }, 60_000);

  // ---------------- API (two real users over HTTP) ----------------

  it("rejects unauthenticated API access", async () => {
    const res = await fetch(`${BASE}/api/workspaces`);
    expect(res.status).toBe(401);
  });

  it("A sees its private workspace; B does not (workspace list)", async () => {
    const listA = (await (await api("/api/workspaces", tokenA)).json()).workspaces.map(
      (w: { name: string }) => w.name
    );
    const listB = (await (await api("/api/workspaces", tokenB)).json()).workspaces.map(
      (w: { name: string }) => w.name
    );
    expect(listA).toContain(`${PREFIX}-private-ws`);
    expect(listB).not.toContain(`${PREFIX}-private-ws`);
  }, 30_000);

  it("both companies see example workspaces", async () => {
    const listB = (await (await api("/api/workspaces", tokenB)).json()).workspaces as {
      name: string;
      kind: string;
    }[];
    expect(listB.some((w) => w.kind === "example")).toBe(true);
  });

  it("B cannot read A's objects through the API", async () => {
    const forB = await api(`/api/objects?workspace=${PREFIX}-private-ws`, tokenB);
    expect(forB.status).toBe(404); // indistinguishable from nonexistent
    const forA = await api(`/api/objects?workspace=${PREFIX}-private-ws`, tokenA);
    expect(forA.status).toBe(200);
    const objects = (await forA.json()).objects.map((o: { name: string }) => o.name);
    expect(objects).toContain("ZCL_TENANCY_SECRET");
  }, 30_000);

  it("B cannot list or open A's chat sessions", async () => {
    const list = await api(`/api/chat/sessions?workspace=${PREFIX}-private-ws`, tokenB);
    expect(list.status).toBe(404);
    const open = await api(`/api/chat/sessions/${sessionA}`, tokenB);
    expect(open.status).toBe(404);
    const openA = await api(`/api/chat/sessions/${sessionA}`, tokenA);
    expect(openA.status).toBe(200);
  }, 30_000);

  // ---------------- RLS (anon key straight to Postgres) ----------------

  it("RLS: B's anon-key queries return none of A's rows", async () => {
    const b = rlsClient(tokenB);
    const ws = await b.from("workspaces").select("name");
    expect((ws.data ?? []).map((w) => w.name)).not.toContain(`${PREFIX}-private-ws`);

    const objects = await b.from("objects").select("name").eq("workspace_id", workspaceA);
    expect(objects.data).toEqual([]);

    const sessions = await b.from("chat_sessions").select("id");
    expect((sessions.data ?? []).map((s) => s.id)).not.toContain(sessionA);

    const messages = await b.from("chat_messages").select("id").eq("session_id", sessionA);
    expect(messages.data).toEqual([]);
  });

  it("RLS: A's anon-key queries do see its own rows", async () => {
    const a = rlsClient(tokenA);
    const ws = await a.from("workspaces").select("name");
    expect((ws.data ?? []).map((w) => w.name)).toContain(`${PREFIX}-private-ws`);
    const sessions = await a.from("chat_sessions").select("id");
    expect((sessions.data ?? []).map((s) => s.id)).toContain(sessionA);
  });

  it("RLS: example workspaces are readable by all but writable by none", async () => {
    const b = rlsClient(tokenB);
    const examples = await b.from("workspaces").select("id, name, kind").eq("kind", "example");
    expect((examples.data ?? []).length).toBeGreaterThan(0);

    const target = examples.data![0];
    const update = await b
      .from("workspaces")
      .update({ name: "hijacked" })
      .eq("id", target.id)
      .select();
    // RLS silently filters the row from the UPDATE — zero rows affected.
    expect(update.data ?? []).toEqual([]);
    const after = await b.from("workspaces").select("name").eq("id", target.id);
    expect(after.data![0].name).toBe(target.name);
  });

  // ---------------- invitation journey ----------------

  it("invitation acceptance creates a working, correctly-scoped account", async () => {
    const token = randomBytes(24).toString("base64url");
    await db.query(
      `insert into invitations (company_id, email, role, token, expires_at)
       values ($1, $2, 'member', $3, now() + interval '7 days')`,
      [companyB, EMAIL_C, token]
    );

    const accept = await api("/api/invitations/accept", undefined, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, password: PASSWORD, display_name: "Test C" }),
    });
    expect(accept.status).toBe(200);

    // Token is single-use.
    const again = await api("/api/invitations/accept", undefined, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, password: PASSWORD, display_name: "Test C" }),
    });
    expect(again.status).toBe(400);

    const tokenC = await signIn(EMAIL_C);
    const profile = await (await api("/api/profile", tokenC)).json();
    expect(profile.company).toBe(`${PREFIX}_company_b`);
    expect(profile.role).toBe("member");

    // …and the new colleague still can't see company A's data.
    const forC = await api(`/api/objects?workspace=${PREFIX}-private-ws`, tokenC);
    expect(forC.status).toBe(404);
  }, 30_000);
});
