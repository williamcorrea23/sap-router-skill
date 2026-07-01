/**
 * ABAP MCP Server — Source Object Cache
 *
 * A small in-memory, TTL-bounded cache for `getObjectSource` results. Reads of
 * the same object (e.g. analyze_abap_context → read_abap_method → contract on
 * the same class) are common, and each round-trip to ADT is expensive. Writes
 * and deletes MUST invalidate the affected entry so we never serve stale source
 * after a mutation — that invalidation is the correctness-critical part and is
 * wired into the write workflow and delete handler.
 *
 * The cache is intentionally simple: no ETag negotiation (the abap-adt-api
 * surface does not expose conditional requests uniformly across releases), just
 * a short TTL plus explicit invalidation on write. TTL defaults to 30s and can
 * be tuned via SOURCE_CACHE_TTL_MS; set it to 0 to disable caching entirely.
 */

import type { ADTClient } from "abap-adt-api";

interface Entry {
  source: string;
  ts: number;
}

const TTL_MS = (() => {
  const raw = process.env.SOURCE_CACHE_TTL_MS;
  if (raw === undefined || raw.trim() === "") return 30_000;
  const n = parseInt(raw, 10);
  return Number.isFinite(n) && n >= 0 ? n : 30_000;
})();

const store = new Map<string, Entry>();

/** Normalize an object URL to a stable cache key (strip trailing /source/main). */
function keyFor(url: string): string {
  return url.replace(/\/source\/main$/, "");
}

/**
 * Read object source, served from cache when a fresh entry exists. Always
 * resolves to a string (JSON-stringifies non-string payloads, mirroring the
 * existing handlers). TTL of 0 disables caching.
 */
export async function getObjectSourceCached(client: ADTClient, sourceUrl: string): Promise<string> {
  const key = keyFor(sourceUrl);
  if (TTL_MS > 0) {
    const hit = store.get(key);
    if (hit && Date.now() - hit.ts < TTL_MS) return hit.source;
  }
  const raw = await client.getObjectSource(sourceUrl.endsWith("/source/main") ? sourceUrl : `${key}/source/main`);
  const text = typeof raw === "string" ? raw : JSON.stringify(raw);
  if (TTL_MS > 0) store.set(key, { source: text, ts: Date.now() });
  return text;
}

/** Invalidate a single object (called after a successful write/delete). */
export function invalidateSource(url: string): void {
  store.delete(keyFor(url));
}

/** Drop the entire cache (used by tests and on session reset). */
export function clearSourceCache(): void {
  store.clear();
}

/** Test/diagnostic helper: current number of cached entries. */
export function sourceCacheSize(): number {
  return store.size;
}
