/**
 * Shared ingestion pipeline (B1) — the DB-insert and summarization core used
 * by BOTH the CLI seeder (scripts/seed.ts) and the in-app ingestion job
 * (lib/ingest/jobs.ts). One code path, two entrypoints.
 */
import Anthropic from "@anthropic-ai/sdk";
import { query } from "../db/client";
import type { ExtractedObject, ExtractResult } from "../parser/extract";

export const SUMMARY_MODEL = "claude-haiku-4-5-20251001";
export const SUMMARY_CONCURRENCY = 8;
const SUMMARY_SOURCE_LIMIT = 24_000; // chars of source sent to Haiku

/**
 * B2 — summaries are the cost driver: at ingestion time only the first
 * SUMMARY_CAP objects (by inbound-edge count) are summarized; the rest get
 * summaries lazily on first access (ensureSummary).
 */
export const SUMMARY_CAP = 800;

function chunk<T>(arr: T[], n: number): T[][] {
  const out: T[][] = [];
  for (let i = 0; i < arr.length; i += n) out.push(arr.slice(i, i + n));
  return out;
}

/** id lookup: exact (type|name) for owners; by-name for call-target resolution,
 *  preferring code objects over DDIC ones when names collide (e.g. ZABAPGIT
 *  exists as both PROG and TABL in abapGit). */
export interface ObjectIndex {
  byKey: Map<string, string>;
  byName: Map<string, string>;
}

const RESOLVE_PREFERENCE = ["CLAS", "INTF", "PROG", "FUGR"];

/**
 * Deterministic category from data already in the object row — no manifest
 * needed, so GitHub-ingested systems categorize too. User-exit includes
 * follow SAP's ZX* naming convention and hook into standard code, hence
 * "enhancement"; unknown types stay null (shown as Uncategorized) rather
 * than guessed. A fixture manifest still overrides per object.
 */
export function deriveCategory(objectType: string, name: string): string | null {
  const type = objectType.toUpperCase();
  if (type === "ENHO" || type === "SMOD") return "enhancement";
  if (type === "PROG" && /^ZX/i.test(name)) return "enhancement";
  if (type === "CLAS" || type === "PROG" || type === "FUGR") return "abap";
  if (type === "TABL") return "custom_table";
  if (type === "INTF") return "interface";
  return null;
}

export async function insertObjects(
  workspaceId: string,
  objects: ExtractedObject[],
  categories: Map<string, string>
): Promise<ObjectIndex> {
  const byKey = new Map<string, string>();
  const byName = new Map<string, string>();
  const typeByName = new Map<string, string>();
  for (const batch of chunk(objects, 50)) {
    const values: unknown[] = [];
    const rowsSql = batch
      .map((o, i) => {
        const b = i * 8;
        values.push(
          workspaceId,
          o.name,
          o.type,
          JSON.stringify(o.files),
          o.parseStatus,
          JSON.stringify(o.parseErrors),
          o.source,
          deriveCategory(o.type, o.name)
        );
        return `($${b + 1}, $${b + 2}, $${b + 3}, $${b + 4}, $${b + 5}, $${b + 6}, $${b + 7}, $${b + 8})`;
      })
      .join(",");
    const rows = await query<{ id: string; name: string; object_type: string }>(
      `insert into objects (workspace_id, name, object_type, files, parse_status, parse_errors, source, category)
       values ${rowsSql} returning id, name, object_type`,
      values
    );
    for (const r of rows) {
      byKey.set(`${r.object_type}|${r.name}`, r.id);
      const existingType = typeByName.get(r.name);
      const rank = (t: string) => {
        const i = RESOLVE_PREFERENCE.indexOf(t);
        return i === -1 ? RESOLVE_PREFERENCE.length : i;
      };
      if (existingType === undefined || rank(r.object_type) < rank(existingType)) {
        byName.set(r.name, r.id);
        typeByName.set(r.name, r.object_type);
      }
    }
  }
  // categories from the fixture manifest, if any — override the derivation
  for (const [name, category] of categories) {
    await query(`update objects set category = $1 where workspace_id = $2 and name = $3`, [
      category,
      workspaceId,
      name.toUpperCase(),
    ]);
  }
  return { byKey, byName };
}

export type EdgeTargetKind = "internal" | "workspace" | "external";

/**
 * Classify a call target at extraction time — never at render time. Internal
 * wins over a same-name workspace object (ABAP resolves locally first), so an
 * internal edge never links to a foreign object either.
 */
export function classifyEdgeTarget(call: { internal: boolean }, resolvedId: string | null): EdgeTargetKind {
  if (call.internal) return "internal";
  return resolvedId ? "workspace" : "external";
}

export async function insertEdges(
  workspaceId: string,
  objects: ExtractedObject[],
  index: ObjectIndex
): Promise<number> {
  type EdgeRow = {
    callerId: string;
    calleeId: string | null;
    calleeName: string;
    kind: string;
    targetKind: EdgeTargetKind;
    file: string;
    line: number;
  };
  const edges: EdgeRow[] = [];
  for (const obj of objects) {
    const callerId = index.byKey.get(`${obj.type}|${obj.name}`);
    if (!callerId) continue;
    const seen = new Set<string>();
    for (const call of obj.calls) {
      const targetKind = classifyEdgeTarget(call, index.byName.get(call.target) ?? null);
      // interface/type refs that neither resolve to a workspace object nor are
      // defined locally are DDIC noise — dropped, never guessed. Unresolved
      // function/perform/class calls are kept and visibly marked.
      if (call.kind === "interface" && targetKind === "external") continue;
      const key = `${call.target}|${call.kind}`;
      if (seen.has(key)) continue;
      seen.add(key);
      edges.push({
        callerId,
        calleeId: targetKind === "workspace" ? (index.byName.get(call.target) as string) : null,
        calleeName: call.target,
        kind: call.kind,
        targetKind,
        file: call.file,
        line: call.line,
      });
    }
  }
  for (const batch of chunk(edges, 500)) {
    const values: unknown[] = [];
    const rowsSql = batch
      .map((e, i) => {
        const b = i * 8;
        values.push(workspaceId, e.callerId, e.calleeId, e.calleeName, e.kind, e.targetKind, e.file, e.line);
        return `($${b + 1}, $${b + 2}, $${b + 3}, $${b + 4}, $${b + 5}, $${b + 6}, $${b + 7}, $${b + 8})`;
      })
      .join(",");
    await query(
      `insert into call_edges (workspace_id, caller_id, callee_id, callee_name, kind, target_kind, file, line) values ${rowsSql}`,
      values
    );
  }
  return edges.length;
}

export async function insertAccesses(
  workspaceId: string,
  objects: ExtractedObject[],
  index: ObjectIndex
): Promise<number> {
  let count = 0;
  for (const obj of objects) {
    const objectId = index.byKey.get(`${obj.type}|${obj.name}`);
    if (!objectId || obj.tableAccesses.length === 0) continue;
    for (const batch of chunk(obj.tableAccesses, 500)) {
      const values: unknown[] = [];
      const rowsSql = batch
        .map((t, i) => {
          const b = i * 8;
          values.push(workspaceId, objectId, t.op, t.table, t.dynamic, t.file, t.line, t.evidence);
          return `($${b + 1}, $${b + 2}, $${b + 3}, $${b + 4}, $${b + 5}, $${b + 6}, $${b + 7}, $${b + 8})`;
        })
        .join(",");
      await query(
        `insert into table_accesses (workspace_id, object_id, op, table_name, dynamic, file, line, evidence) values ${rowsSql}`,
        values
      );
      count += batch.length;
    }
  }
  return count;
}

/** Insert the full parsed graph for a fresh workspace. */
export async function insertWorkspaceGraph(
  workspaceId: string,
  result: ExtractResult,
  categories: Map<string, string>
): Promise<{ index: ObjectIndex; edgeCount: number; accessCount: number }> {
  const index = await insertObjects(workspaceId, result.objects, categories);
  const edgeCount = await insertEdges(workspaceId, result.objects, index);
  const accessCount = await insertAccesses(workspaceId, result.objects, index);
  return { index, edgeCount, accessCount };
}

/**
 * Pick the objects to summarize at ingestion time: first SUMMARY_CAP by
 * inbound-edge count (most-referenced objects are what search/chat surface
 * first). Everything else is summarized lazily on first access.
 */
export async function planSummaryIds(workspaceId: string, cap = SUMMARY_CAP): Promise<string[]> {
  const rows = await query<{ id: string }>(
    `select o.id
     from objects o
     where o.workspace_id = $1 and o.summary is null
     order by (select count(*) from call_edges e
               where e.workspace_id = $1 and (e.callee_id = o.id or e.callee_name = o.name)) desc,
              o.name
     limit $2`,
    [workspaceId, cap]
  );
  return rows.map((r) => r.id);
}

interface SummarizableRow {
  id: string;
  name: string;
  object_type: string;
  parse_status: string;
  source: string;
}

async function summarizeOne(workspaceId: string, obj: SummarizableRow, client: Anthropic, lazy: boolean) {
  const truncated = obj.source.length > SUMMARY_SOURCE_LIMIT;
  const source = obj.source.slice(0, SUMMARY_SOURCE_LIMIT);
  const prompt = `Summarize this ABAP ${obj.object_type} object named ${obj.name} in 2-4 sentences for a developer audit report. Start directly with the description — never repeat the object name and never add a heading or prefix such as "Summary" or "Table Summary". State only what is visible in the source: purpose, key tables/functions it touches, notable patterns. No speculation about anything not shown.${obj.object_type === "TABL" ? " The TABCLASS value determines what this is: INTTAB means a structure (no database storage), TRANSP means a transparent database table — use the correct term." : ""}${truncated ? " (Source truncated.)" : ""}${obj.parse_status === "failed" ? " Note: this object did not fully parse; describe what is recognizable." : ""}\n\n\`\`\`abap\n${source}\n\`\`\``;
  const started = Date.now();
  const res = await client.messages.create({
    model: SUMMARY_MODEL,
    max_tokens: 400,
    messages: [{ role: "user", content: prompt }],
  });
  const text = res.content
    .filter((b) => b.type === "text")
    .map((b) => (b as { text: string }).text)
    .join("");
  await query(`update objects set summary = $1, summary_model = $2 where id = $3`, [text, SUMMARY_MODEL, obj.id]);
  await query(
    `insert into traces (workspace_id, object_id, kind, model, input, output, input_tokens, output_tokens, duration_ms)
     values ($1, $2, 'summary', $3, $4, $5, $6, $7, $8)`,
    [
      workspaceId,
      obj.id,
      SUMMARY_MODEL,
      JSON.stringify({ prompt_chars: prompt.length, truncated, lazy }),
      JSON.stringify({ text }),
      res.usage.input_tokens,
      res.usage.output_tokens,
      Date.now() - started,
    ]
  );
}

/**
 * Summarize the given (not-yet-summarized) objects by id. Traced. Returns
 * done/failed counts; failures never block the run.
 */
export async function summarizeStoredObjects(
  workspaceId: string,
  objectIds: string[],
  opts: { concurrency?: number; lazy?: boolean; log?: (s: string) => void } = {}
): Promise<{ done: number; failed: number }> {
  if (objectIds.length === 0) return { done: 0, failed: 0 };
  const log = opts.log ?? (() => {});
  const client = new Anthropic();
  const rows = await query<SummarizableRow>(
    `select id, name, object_type, parse_status, source from objects
     where workspace_id = $1 and id = any($2) and summary is null`,
    [workspaceId, objectIds]
  );
  const queue = [...rows];
  let done = 0;
  let failed = 0;
  async function worker() {
    for (;;) {
      const obj = queue.shift();
      if (!obj) return;
      try {
        await summarizeOne(workspaceId, obj, client, opts.lazy ?? false);
        done++;
        if (done % 50 === 0) log(`  summaries: ${done}/${rows.length}`);
      } catch (e) {
        failed++;
        log(`  summary failed for ${obj.name}: ${(e as Error).message}`);
      }
    }
  }
  await Promise.all(Array.from({ length: opts.concurrency ?? SUMMARY_CONCURRENCY }, worker));
  return { done, failed };
}

/**
 * B2 — lazy summary on first access: generate, store, trace. Returns the
 * summary text (null if generation failed or the object has no source).
 */
export async function ensureSummary(workspaceId: string, objectId: string): Promise<string | null> {
  const [existing] = await query<{ summary: string | null }>(
    `select summary from objects where id = $1`,
    [objectId]
  );
  if (existing?.summary) return existing.summary;
  const result = await summarizeStoredObjects(workspaceId, [objectId], { concurrency: 1, lazy: true });
  if (result.done === 0) return null;
  const [after] = await query<{ summary: string | null }>(`select summary from objects where id = $1`, [objectId]);
  return after?.summary ?? null;
}
