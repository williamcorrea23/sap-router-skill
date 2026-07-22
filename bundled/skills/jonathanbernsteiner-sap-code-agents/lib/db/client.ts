/**
 * Postgres access via `pg` over DATABASE_URL (server-side only).
 * All numbers shown anywhere in the product come from SQL run through here.
 */
import { Pool } from "pg";

let pool: Pool | undefined;

export function getPool(): Pool {
  if (!pool) {
    const url = process.env.DATABASE_URL;
    if (!url) throw new Error("DATABASE_URL is not set");
    // Prod runs through Supabase's SESSION-mode pooler, which allows only 15
    // clients across ALL function instances. Keep each instance's slice small
    // and release idle connections fast — parallel query batches (Promise.all
    // in the API routes) queue on this in-process pool instead of opening one
    // pooler session per query.
    pool = new Pool({
      connectionString: url,
      max: 3,
      idleTimeoutMillis: 5_000,
      allowExitOnIdle: true,
    });
  }
  return pool;
}

export async function query<T = Record<string, unknown>>(
  text: string,
  params: unknown[] = []
): Promise<T[]> {
  const res = await getPool().query(text, params);
  return res.rows as T[];
}

export async function closePool(): Promise<void> {
  if (pool) {
    await pool.end();
    pool = undefined;
  }
}
