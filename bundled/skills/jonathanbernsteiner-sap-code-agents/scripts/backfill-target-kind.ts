/**
 * Backfill call_edges.target_kind for workspaces ingested before migration 018.
 *
 * The classification is re-derived from STORED source (objects.source keeps
 * every file verbatim behind `* ===== <path> =====` markers), re-parsed with
 * the exact extraction code new ingests use — no re-ingest, no guessing:
 *   internal  = target defined in the caller's own compilation unit
 *               (callee_id is also cleared: an internal call must never link
 *               to — or count as a reference of — a same-named other object)
 *   workspace = callee_id resolves to an ingested object
 *   external  = everything else
 *
 * Idempotent: reclassifies every edge on each run. `--workspace <name>`
 * limits the run to one workspace.
 */
import { extractWorkspace, type ParseInput } from "../lib/parser/extract";

const FILE_MARKER = /^\* ===== (.+?) =====$/gm;

/** objects.source → the per-file inputs it was concatenated from */
export function splitStoredSource(source: string): ParseInput[] {
  const markers = [...source.matchAll(FILE_MARKER)];
  return markers.map((m, i) => {
    const start = (m.index ?? 0) + m[0].length + 1; // past the marker line
    const end = i + 1 < markers.length ? (markers[i + 1].index ?? source.length) : source.length;
    // strip the blank separator the concatenation added between files
    return { path: m[1], contents: source.slice(start, end).replace(/\n\n$/, "\n") };
  });
}

async function main() {
  const { query, closePool } = await import("../lib/db/client");
  const wsFilter = process.argv.includes("--workspace")
    ? process.argv[process.argv.indexOf("--workspace") + 1]
    : null;

  const workspaces = await query<{ id: string; name: string }>(
    wsFilter ? `select id, name from workspaces where name = $1` : `select id, name from workspaces order by name`,
    wsFilter ? [wsFilter] : []
  );
  if (wsFilter && workspaces.length === 0) {
    console.error(`workspace '${wsFilter}' not found`);
    process.exit(1);
  }

  for (const ws of workspaces) {
    const objects = await query<{ id: string; name: string; object_type: string; source: string }>(
      `select o.id, o.name, o.object_type, o.source from objects o
       where o.workspace_id = $1
         and exists (select 1 from call_edges e where e.caller_id = o.id)`,
      [ws.id]
    );

    // re-parse each caller's stored files and collect its internal (kind, target) pairs
    const inputs: ParseInput[] = [];
    for (const obj of objects) inputs.push(...splitStoredSource(obj.source));
    const extraction = extractWorkspace(inputs);
    const internalByCaller = new Map<string, string[]>();
    for (const obj of extraction.objects) {
      const internal = [...new Set(obj.calls.filter((c) => c.internal).map((c) => `${c.kind}|${c.target}`))];
      if (internal.length > 0) internalByCaller.set(`${obj.type}|${obj.name}`, internal);
    }

    let internalCount = 0;
    let unlinked = 0;
    for (const obj of objects) {
      const internal = internalByCaller.get(`${obj.object_type}|${obj.name}`);
      if (!internal) continue;
      const relinked = await query<{ had_callee: boolean }>(
        `with old as (select id, callee_id from call_edges
                      where caller_id = $1 and kind || '|' || callee_name = any($2::text[]))
         update call_edges e set target_kind = 'internal', callee_id = null
         from old where e.id = old.id
         returning (old.callee_id is not null) as had_callee`,
        [obj.id, internal]
      );
      internalCount += relinked.length;
      // rows that previously carried a (wrong) resolution to a same-named object
      unlinked += relinked.filter((r) => r.had_callee).length;
    }
    const [{ n: wsN }] = await query<{ n: string }>(
      `with u as (update call_edges set target_kind = 'workspace'
                  where workspace_id = $1 and callee_id is not null
                    and coalesce(target_kind, '') <> 'workspace' returning 1)
       select count(*) as n from u`,
      [ws.id]
    );
    const [{ n: extN }] = await query<{ n: string }>(
      `with u as (update call_edges set target_kind = 'external'
                  where workspace_id = $1 and callee_id is null
                    and coalesce(target_kind, '') not in ('internal', 'external') returning 1)
       select count(*) as n from u`,
      [ws.id]
    );
    const totals = await query<{ target_kind: string; n: string }>(
      `select target_kind, count(*) as n from call_edges where workspace_id = $1 group by target_kind order by target_kind`,
      [ws.id]
    );
    console.log(
      `${ws.name}: reclassified ${internalCount} internal (${unlinked} had a false resolution), ` +
        `${wsN} → workspace, ${extN} → external · now: ` +
        totals.map((t) => `${t.target_kind ?? "null"}=${t.n}`).join(" ")
    );
  }
  await closePool();
}

// splitStoredSource is imported by the unit tests — only run as a CLI
if (process.argv[1]?.endsWith("backfill-target-kind.ts")) {
  main().catch((e) => {
    console.error(e);
    process.exit(1);
  });
}
