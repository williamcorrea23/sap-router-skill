/**
 * B1 × Change Order 03 — the ingestion chunk worker is driven by
 * server-to-server self-fetches, which carry no user session. They
 * authenticate with the service-role key as a bearer token: the session
 * middleware passes any request with an Authorization header through, and
 * the process route validates it here. The key never leaves the server.
 */
import { timingSafeEqual } from "node:crypto";
import type { NextRequest } from "next/server";

function secret(): string | null {
  return process.env.SUPABASE_SERVICE_ROLE_KEY ?? null;
}

export function isWorkerRequest(req: NextRequest): boolean {
  const s = secret();
  if (!s) return false;
  const header = req.headers.get("authorization") ?? "";
  if (!header.toLowerCase().startsWith("bearer ")) return false;
  const token = Buffer.from(header.slice(7).trim());
  const expected = Buffer.from(s);
  return token.length === expected.length && timingSafeEqual(token, expected);
}

/** Fire-and-forget kick of the chunk worker (used from after()). */
export async function kickWorker(origin: string): Promise<void> {
  const s = secret();
  if (!s) return;
  await fetch(new URL("/api/ingest/process", origin).toString(), {
    method: "POST",
    headers: { authorization: `Bearer ${s}` },
  }).catch(() => {});
}
