/**
 * Workspace seeder CLI.
 *
 * Usage:
 *   npm run seed -- --workspace <name> --source <git-url-or-local-path>
 *                   [--skip-summaries] [--kind example|ingested]
 *
 * Pipeline: clone/read source → parse every .abap (+ .tabl.xml) file with
 * abaplint via lib/parser/extract → write workspace, objects, call edges,
 * table accesses to Postgres → load usage.csv if present (marked simulated)
 * → Haiku summary pass, capped at SUMMARY_CAP objects by inbound-edge count
 * (the rest are summarized lazily on first access).
 *
 * The DB-insert and summary code is shared with the in-app ingestion job:
 * lib/ingest/pipeline.ts (B1 — one pipeline, two entrypoints).
 *
 * Parser failures never block the run: the object is stored with
 * parse_status='failed' plus raw source. Re-seeding a workspace name replaces
 * it atomically (delete cascade + fresh insert).
 */
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync } from "node:fs";
import { join, relative } from "node:path";
import { closePool, query } from "../lib/db/client";
import {
  insertWorkspaceGraph,
  planSummaryIds,
  summarizeStoredObjects,
  SUMMARY_CAP,
  SUMMARY_MODEL,
  type ObjectIndex,
} from "../lib/ingest/pipeline";
import { extractWorkspace, type ParseInput } from "../lib/parser/extract";

function arg(name: string): string | undefined {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 ? process.argv[i + 1] : undefined;
}

function resolveSource(source: string): string {
  if (/^(https?:|git@)/.test(source)) {
    const dir = join(
      process.cwd(),
      ".seed-cache",
      source.replace(/.*\//, "").replace(/\.git$/, "") + "-" + createHash("sha1").update(source).digest("hex").slice(0, 8)
    );
    if (!existsSync(dir)) {
      mkdirSync(join(process.cwd(), ".seed-cache"), { recursive: true });
      console.log(`cloning ${source} (shallow) → ${relative(process.cwd(), dir)}`);
      execFileSync("git", ["clone", "--depth", "1", source, dir], { stdio: "inherit" });
    }
    return dir;
  }
  // reuse the parse-proof clone for the canonical abapGit source
  if (source === "abapgit-cache") return join(process.cwd(), ".seed-cache", "abapGit");
  return source;
}

function listSourceFiles(dir: string): string[] {
  const out = execFileSync(
    "find",
    [dir, "-type", "f", "(", "-name", "*.abap", "-o", "-name", "*.tabl.xml", ")"],
    { encoding: "utf8" }
  );
  return out.split("\n").filter(Boolean).sort();
}

async function loadUsage(workspaceId: string, sourceDir: string, index: ObjectIndex) {
  const csvPath = join(sourceDir, "usage.csv");
  if (!existsSync(csvPath)) return { loaded: 0, simulated: false };
  const lines = readFileSync(csvPath, "utf8").trim().split("\n").slice(1).filter(Boolean);
  let loaded = 0;
  let skipped = 0;
  for (const line of lines) {
    const [name, count, lastExecuted] = line.split(",");
    const objectId = index.byName.get(name.trim().toUpperCase());
    if (!objectId) {
      skipped++;
      continue;
    }
    await query(
      `insert into usage_stats (workspace_id, object_id, call_count_24m, last_executed, simulated)
       values ($1, $2, $3, $4, true)
       on conflict (workspace_id, object_id) do update set call_count_24m = excluded.call_count_24m`,
      [workspaceId, objectId, Number(count), lastExecuted?.trim() || null]
    );
    loaded++;
  }
  if (skipped) console.warn(`usage.csv: ${skipped} rows referenced unknown objects (skipped)`);
  if (loaded) await query(`update workspaces set simulated_usage = true where id = $1`, [workspaceId]);
  return { loaded, simulated: loaded > 0 };
}

async function main() {
  const workspace = arg("workspace");
  const source = arg("source");
  const kind = arg("kind") ?? "example";
  if (!workspace || !source) {
    console.error("usage: npm run seed -- --workspace <name> --source <git-url-or-path> [--skip-summaries] [--kind example|ingested]");
    process.exit(1);
  }

  const sourceDir = resolveSource(source);
  const paths = listSourceFiles(sourceDir);
  if (paths.length === 0) {
    console.error(`no .abap/.tabl.xml files found under ${sourceDir}`);
    process.exit(1);
  }
  const inputs: ParseInput[] = paths.map((p) => ({
    path: relative(sourceDir, p),
    contents: readFileSync(p, "utf8"),
  }));
  console.log(`parsing ${inputs.length} files from ${sourceDir} ...`);
  const result = extractWorkspace(inputs);
  const { totals } = result;
  const fileRate = ((100 * (totals.inputFiles - result.unattachedFiles.length)) / totals.inputFiles).toFixed(2);
  console.log(
    `parse summary: ${totals.objects} objects (${totals.objectsOk} ok, ${totals.objectsFailed} failed), ` +
      `${totals.inputFiles} files (${fileRate}% attached), ${result.unattachedFiles.length} unattached`
  );

  // fixture manifest categories (optional)
  const categories = new Map<string, string>();
  const manifestPath = join(sourceDir, "manifest.json");
  if (existsSync(manifestPath)) {
    const manifest = JSON.parse(readFileSync(manifestPath, "utf8"));
    for (const o of manifest.objects ?? []) {
      if (o.name && o.category) categories.set(o.name, o.category);
    }
  }

  // replace workspace atomically-enough: cascade delete, then insert fresh.
  // Post-Change-Order-03 schemas require an owning company (operator seeds
  // belong to the operator company); pre-CO-03 schemas have no such column.
  await query(`delete from workspaces where name = $1`, [workspace]);
  const [hasCompanies] = await query<{ ok: boolean }>(
    `select exists (select 1 from information_schema.columns
                    where table_name = 'workspaces' and column_name = 'company_id') as ok`
  );
  const companyName = arg("company") ?? "Operator (examples)";
  // record the canonical upstream URL for the cached abapGit clone so the UI
  // can show repo-level provenance (file deep links stay ingested-only)
  const recordedSource = source === "abapgit-cache" ? "https://github.com/abapGit/abapGit" : source;
  const [ws] = hasCompanies?.ok
    ? await query<{ id: string }>(
        `insert into workspaces (name, source, kind, company_id)
         values ($1, $2, $3, (select id from companies where name = $4)) returning id`,
        [workspace, recordedSource, kind, companyName]
      )
    : await query<{ id: string }>(
        `insert into workspaces (name, source, kind) values ($1, $2, $3) returning id`,
        [workspace, recordedSource, kind]
      );

  const { index, edgeCount, accessCount } = await insertWorkspaceGraph(ws.id, result, categories);
  const usage = await loadUsage(ws.id, sourceDir, index);

  console.log(`inserted: ${index.byKey.size} objects, ${edgeCount} call edges, ${accessCount} table accesses`);
  console.log(`usage stats: ${usage.loaded} rows${usage.simulated ? " (SIMULATED — labeled)" : " (none — renders as 'no usage data available')"}`);

  if (!process.argv.includes("--skip-summaries")) {
    const planned = await planSummaryIds(ws.id, SUMMARY_CAP);
    console.log(
      `Haiku summary pass (${SUMMARY_MODEL}) over ${planned.length}/${index.byKey.size} objects` +
        (planned.length < index.byKey.size ? ` (capped at ${SUMMARY_CAP} by inbound edges; rest summarized lazily on first access)` : "") +
        " ..."
    );
    const s = await summarizeStoredObjects(ws.id, planned, { log: console.log });
    console.log(`summaries: ${s.done} written, ${s.failed} failed`);
  } else {
    console.log("summaries skipped (--skip-summaries)");
  }

  // sanity SQL — the same numbers the product would show
  const [sanity] = await query<Record<string, string>>(
    `select
       (select count(*) from objects where workspace_id = $1) as objects,
       (select count(*) from objects where workspace_id = $1 and parse_status = 'failed') as parse_failed,
       (select count(*) from call_edges where workspace_id = $1) as edges,
       (select count(*) from call_edges where workspace_id = $1 and callee_id is not null) as resolved_edges,
       (select count(*) from table_accesses where workspace_id = $1) as table_accesses,
       (select count(*) from usage_stats where workspace_id = $1) as usage_rows,
       (select count(*) from objects where workspace_id = $1 and summary is not null) as summaries,
       (select count(*) from traces where workspace_id = $1 and kind = 'summary') as summary_traces`,
    [ws.id]
  );
  console.log("sanity:", sanity);
  await closePool();
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
