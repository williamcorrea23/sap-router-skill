/**
 * Deterministic synthetic usage generator (Phase 2 + demo mode). The model
 * lives in lib/ingest/simulated-usage.ts (shared with the ingest-time demo
 * option); this script is its CLI.
 *
 * Two modes:
 * - default (fixtures): dead set from manifest `dead: true`; writes
 *   fixtures/usage.csv with the FIXED anchor date, loaded by the seeder with
 *   simulated=true — regeneration is byte-identical.
 * - `--workspace <name>`: DEMO mode for an ingested workspace — same model
 *   computed from the stored graph and written straight to usage_stats
 *   (simulated=true, workspace flagged simulated_usage). Operator-run and
 *   opt-in; every surface labels it SIMULATED.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { join, relative } from "node:path";
import { extractWorkspace, type ParseInput } from "../lib/parser/extract";
import { simulatedUsageFor } from "../lib/ingest/simulated-usage";

const FIXTURES = join(process.cwd(), "fixtures");
const ANCHOR_DATE = new Date("2026-07-18T00:00:00Z"); // fixed, not "today"

/** DEMO mode — delegate to the shared generator against the stored graph. */
async function generateForWorkspace(name: string) {
  const { query, closePool } = await import("../lib/db/client");
  const { generateSimulatedUsage } = await import("../lib/ingest/simulated-usage");
  const [ws] = await query<{ id: string }>(`select id from workspaces where name = $1`, [name]);
  if (!ws) {
    console.error(`workspace '${name}' not found`);
    process.exit(1);
  }
  const { rows, dead } = await generateSimulatedUsage(ws.id);
  console.log(
    `${name}: ${rows} SIMULATED usage rows written (${dead} dead by legacy-marker heuristic); workspace flagged simulated_usage`
  );
  await closePool();
}

function main() {
  const paths = execFileSync("find", [join(FIXTURES, "src"), "-type", "f"], { encoding: "utf8" })
    .split("\n")
    .filter(Boolean)
    .sort();
  const inputs: ParseInput[] = paths.map((p) => ({
    path: relative(join(FIXTURES, "src"), p),
    contents: readFileSync(p, "utf8"),
  }));
  const result = extractWorkspace(inputs);

  const manifest = JSON.parse(readFileSync(join(FIXTURES, "manifest.json"), "utf8"));
  const dead = new Set<string>(
    (manifest.objects ?? []).filter((o: { dead: boolean }) => o.dead).map((o: { name: string }) => o.name.toUpperCase())
  );

  // inbound edges: how many other objects reference this one (resolved names only)
  const names = new Set(result.objects.map((o) => o.name));
  const inbound = new Map<string, number>();
  for (const obj of result.objects) {
    const targets = new Set(obj.calls.map((c) => c.target).filter((t) => names.has(t)));
    for (const t of targets) inbound.set(t, (inbound.get(t) ?? 0) + 1);
  }

  const rows: string[] = ["object_name,call_count_24m,last_executed"];
  for (const obj of [...result.objects].sort((a, b) => a.name.localeCompare(b.name))) {
    // manifest dead flag wins over the model's own heuristic
    const row = dead.has(obj.name)
      ? { callCount24m: 0, lastExecuted: null }
      : simulatedUsageFor(obj.type, obj.name, inbound.get(obj.name) ?? 0, ANCHOR_DATE);
    if (!row) continue; // non-executable (INTF, TABL)
    rows.push(`${obj.name},${row.callCount24m},${row.lastExecuted ?? ""}`);
  }

  const out = join(FIXTURES, "usage.csv");
  writeFileSync(out, rows.join("\n") + "\n");
  console.log(`wrote ${out}:`);
  console.log(rows.join("\n"));
}

const wsIdx = process.argv.indexOf("--workspace");
if (wsIdx >= 0 && process.argv[wsIdx + 1]) {
  generateForWorkspace(process.argv[wsIdx + 1]).catch((e) => {
    console.error(e);
    process.exit(1);
  });
} else {
  main();
}
