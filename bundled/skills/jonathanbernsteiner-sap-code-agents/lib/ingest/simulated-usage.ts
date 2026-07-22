/**
 * Deterministic simulated-usage model — OPERATOR-ONLY, for example and demo
 * systems. Reachable solely through the CLI (`npm run gen-usage`, directly or
 * `--workspace <name>`); deliberately NOT exposed in the connect flow or the
 * ingest API, so a client assessment can never contain invented execution
 * counts. Real usage comes from the SAP system's own statistics (ST03N /
 * SCMON / UPL) via the extraction adapter; when it is absent the product says
 * so instead of estimating. Everything written here is labeled SIMULATED via
 * usage_stats.simulated + workspaces.simulated_usage.
 *
 *   call_count_24m = base(type) × (1 + 2·inbound_edges) × jitter(name)
 *
 * Fixed seed and name-hashed PRNG → identical numbers for identical graphs.
 * Dead set (retirement demo): zero inbound references AND a legacy-marker
 * name — deterministic and documented, no hand-picked objects.
 */
import { query } from "../db/client";

export const SEED = 20260719;
export const BASE_BY_TYPE: Record<string, number> = { PROG: 180, CLAS: 900 };
/** Names that mark intentionally-kept dead code in ABAP shops. */
export const LEGACY_MARKER = /LEGACY|OBSOLETE|BACKUP|_OLD(_|$)/i;

/** mulberry32 PRNG — tiny, deterministic */
export function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function hashName(name: string): number {
  let h = 0;
  for (const ch of name) h = (Math.imul(h, 31) + ch.charCodeAt(0)) | 0;
  return h >>> 0;
}

export interface SimulatedUsageRow {
  callCount24m: number;
  lastExecuted: string | null; // ISO date or null (never executed)
}

/**
 * The pure model: null for non-executable types (they have no usage rows),
 * a zero row for dead objects, otherwise the seeded count + recency.
 */
export function simulatedUsageFor(
  objectType: string,
  name: string,
  inboundRefs: number,
  anchor: Date
): SimulatedUsageRow | null {
  const base = BASE_BY_TYPE[objectType.toUpperCase()];
  if (base === undefined) return null;
  if (inboundRefs === 0 && LEGACY_MARKER.test(name)) {
    return { callCount24m: 0, lastExecuted: null };
  }
  const rand = mulberry32(SEED ^ hashName(name));
  const callCount24m = Math.round(base * (1 + 2 * inboundRefs) * (0.75 + 0.5 * rand()));
  const daysAgo = Math.floor(rand() * 14);
  const lastExecuted = new Date(anchor.getTime() - daysAgo * 86_400_000).toISOString().slice(0, 10);
  return { callCount24m, lastExecuted };
}

/**
 * Generate and store simulated usage for a workspace from its stored graph;
 * flags the workspace simulated_usage. Anchor defaults to generation time so
 * "last executed" reads recent (the fixture CSV path keeps its fixed anchor
 * for byte-identical regeneration).
 */
export async function generateSimulatedUsage(
  workspaceId: string,
  anchor: Date = new Date()
): Promise<{ rows: number; dead: number }> {
  const objects = await query<{ id: string; name: string; object_type: string; inbound: number }>(
    `select o.id, o.name, o.object_type,
            (select count(*) from call_edges e
             where e.workspace_id = $1 and e.callee_id = o.id and e.caller_id <> o.id)::int as inbound
     from objects o where o.workspace_id = $1 order by o.name`,
    [workspaceId]
  );
  await query(`delete from usage_stats where workspace_id = $1`, [workspaceId]);
  let rows = 0;
  let dead = 0;
  for (const obj of objects) {
    const row = simulatedUsageFor(obj.object_type, obj.name, obj.inbound, anchor);
    if (!row) continue;
    await query(
      `insert into usage_stats (workspace_id, object_id, call_count_24m, last_executed, simulated)
       values ($1, $2, $3, $4, true)`,
      [workspaceId, obj.id, row.callCount24m, row.lastExecuted]
    );
    rows++;
    if (row.callCount24m === 0) dead++;
  }
  await query(`update workspaces set simulated_usage = true where id = $1`, [workspaceId]);
  return { rows, dead };
}
