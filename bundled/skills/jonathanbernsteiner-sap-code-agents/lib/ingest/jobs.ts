/**
 * B1 — ingestion job state machine.
 *
 * Jobs run in chunks so no single serverless invocation exceeds its time
 * budget: the 'queued' chunk does clone → parse → persist (fast, no LLM);
 * 'summarizing' chunks each do one batch of Haiku summaries and re-queue.
 * Claiming is FIFO with a lease: only the oldest non-terminal job may hold
 * the lease, which enforces exactly one concurrent ingestion (B2); further
 * jobs stay queued. A stale lease (dead worker) is re-claimable.
 *
 * Guardrails (B2): public HTTPS URLs only, size caps enforced before
 * parsing, minimum-ABAP check before persisting — a failed job persists
 * nothing.
 */
import { rmSync } from "node:fs";
import { readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, relative } from "node:path";
import { query } from "../db/client";
import { extractWorkspace, type ParseInput } from "../parser/extract";
import { clonedBranch, cloneRepo, listSourceFiles, normalizeWorkspaceName, validateGitUrl, workspaceNameForUrl } from "./git";
import { insertWorkspaceGraph, planSummaryIds, summarizeStoredObjects, SUMMARY_CAP } from "./pipeline";

export const MAX_ABAP_FILES = 3000;
export const MAX_SOURCE_BYTES = 25 * 1024 * 1024;
export const MIN_PARSEABLE_FILES = 5;
const SUMMARY_BATCH = 16;
const LEASE_SECONDS = 240;

export interface IngestionJob {
  id: string;
  git_url: string;
  workspace_name: string;
  status: "queued" | "cloning" | "parsing" | "graph" | "summarizing" | "ready" | "failed";
  error: string | null;
  files_total: number | null;
  files_parsed: number | null;
  objects_total: number | null;
  edges_total: number | null;
  summaries_planned: number | null;
  summaries_done: number;
  workspace_id: string | null;
  company_id: string | null;
  created_at: string;
  updated_at: string;
}

const JOB_COLUMNS = `id, git_url, workspace_name, status, error, files_total, files_parsed,
  objects_total, edges_total, summaries_planned, summaries_done, workspace_id, company_id,
  created_at, updated_at`;

export async function getJob(id: string): Promise<IngestionJob | null> {
  const [job] = await query<IngestionJob>(
    `select ${JOB_COLUMNS} from ingestion_jobs where id = $1`,
    [id]
  );
  return job ?? null;
}

export async function createJob(
  rawUrl: string,
  companyId: string,
  customName?: string
): Promise<{ job: IngestionJob } | { error: string }> {
  const validated = validateGitUrl(rawUrl);
  if (!validated.ok) return { error: validated.error };
  const url = validated.url;

  let name: string;
  if (customName !== undefined && customName.trim() !== "") {
    const normalized = normalizeWorkspaceName(customName);
    if (!normalized.ok) return { error: normalized.error };
    name = normalized.name;
  } else {
    name = workspaceNameForUrl(url);
  }

  const [existingWs] = await query<{ kind: string; company_id: string | null; source: string }>(
    `select kind, company_id, source from workspaces where name = $1`,
    [name]
  );
  if (existingWs?.kind === "example") {
    return { error: `System name '${name}' collides with a built-in example system.` };
  }
  // A custom name may replace a workspace only when it re-ingests the SAME
  // source (that is the re-ingest flow); never silently swallow an unrelated
  // workspace of this company.
  if (
    customName !== undefined &&
    customName.trim() !== "" &&
    existingWs &&
    existingWs.company_id === companyId &&
    existingWs.source !== url
  ) {
    return { error: `System name '${name}' is already used by another of your systems.` };
  }

  // idempotency: this company's active job for the same URL is returned, not
  // duplicated
  const [active] = await query<IngestionJob>(
    `select ${JOB_COLUMNS} from ingestion_jobs
     where git_url = $1 and company_id = $2 and status in ('queued','cloning','parsing','graph','summarizing')
     order by created_at limit 1`,
    [url, companyId]
  );
  if (active) return { job: active };

  const [job] = await query<IngestionJob>(
    `insert into ingestion_jobs (git_url, workspace_name, company_id)
     values ($1, $2, $3) returning ${JOB_COLUMNS}`,
    [url, name, companyId]
  );
  return { job };
}

/** True when this job could use a worker invocation right now. */
export function isActive(job: IngestionJob): boolean {
  return ["queued", "cloning", "parsing", "graph", "summarizing"].includes(job.status);
}

async function update(jobId: string, fields: Record<string, unknown>): Promise<void> {
  const keys = Object.keys(fields);
  const sets = keys.map((k, i) => `${k} = $${i + 2}`).join(", ");
  await query(`update ingestion_jobs set ${sets}, updated_at = now() where id = $1`, [
    jobId,
    ...keys.map((k) => fields[k]),
  ]);
}

async function failJob(job: IngestionJob, message: string, createdWorkspaceId?: string | null) {
  if (createdWorkspaceId) {
    // a failed job persists nothing
    await query(`delete from workspaces where id = $1`, [createdWorkspaceId]);
  }
  await update(job.id, { status: "failed", error: message.slice(0, 500), lease_expires_at: null });
}

/**
 * Atomically claim the oldest non-terminal job. Returns null when there is
 * nothing to do or the oldest job is already being worked on (its lease is
 * live) — that is the one-concurrent-ingestion rule.
 */
async function claimNext(): Promise<IngestionJob | null> {
  const [job] = await query<IngestionJob>(
    `update ingestion_jobs j
     set lease_expires_at = now() + make_interval(secs => $1), updated_at = now()
     where j.id = (
       select id from ingestion_jobs
       where status in ('queued','cloning','parsing','graph','summarizing')
       order by created_at
       limit 1
       for update skip locked
     )
     and (j.lease_expires_at is null or j.lease_expires_at < now())
     returning ${JOB_COLUMNS}`,
    [LEASE_SECONDS]
  );
  return job ?? null;
}

/** clone → caps → parse → persist. Runs in one invocation; no LLM. */
async function runIngestPhase(job: IngestionJob): Promise<void> {
  const dir = join(tmpdir(), "sap-code-agents-ingest", job.id);
  let createdWorkspaceId: string | null = null;
  try {
    await update(job.id, { status: "cloning" });
    await cloneRepo(job.git_url, dir);
    // default branch of the single-branch clone — powers file:line deep links
    const sourceBranch = await clonedBranch(dir);

    const files = listSourceFiles(dir);
    // Emit the file count before the cap checks: the fetch stage's done
    // detail, and it pins cap/no-ABAP failures to the parse stage in the UI
    // (stage derivation goes by which counters are set).
    await update(job.id, { status: "parsing", files_total: files.abap.length + files.tabl.length });
    // B2 — size caps, enforced before parsing
    if (files.abap.length > MAX_ABAP_FILES) {
      throw new Error(
        `Repository exceeds the ingestion cap: ${files.abap.length.toLocaleString("en-US")} ABAP files found, maximum is ${MAX_ABAP_FILES.toLocaleString("en-US")}.`
      );
    }
    if (files.abap.length < MIN_PARSEABLE_FILES) {
      throw new Error(
        `No ABAP sources found: this repository contains ${files.abap.length} .abap file(s); at least ${MIN_PARSEABLE_FILES} parseable ABAP files are required.`
      );
    }
    const allPaths = [...files.abap, ...files.tabl];
    const inputs: ParseInput[] = [];
    let totalBytes = 0;
    for (const p of allPaths) {
      const contents = readFileSync(p, "utf8");
      totalBytes += Buffer.byteLength(contents);
      if (totalBytes > MAX_SOURCE_BYTES) {
        throw new Error(
          `Repository exceeds the ingestion cap: ABAP source volume is over ${Math.round(MAX_SOURCE_BYTES / 1024 / 1024)} MB.`
        );
      }
      inputs.push({ path: relative(dir, p), contents });
    }

    const result = extractWorkspace(inputs);
    const parseableAbapFiles = new Set(
      result.objects
        .filter((o) => o.parseStatus === "ok")
        .flatMap((o) => o.files)
        .filter((f) => f.endsWith(".abap"))
    );
    if (parseableAbapFiles.size < MIN_PARSEABLE_FILES) {
      throw new Error(
        `No ABAP sources found: only ${parseableAbapFiles.size} ABAP file(s) parsed successfully; at least ${MIN_PARSEABLE_FILES} are required.`
      );
    }
    // Parse done → graph-building begins (its own visible pipeline stage).
    await update(job.id, { status: "graph", files_parsed: parseableAbapFiles.size });

    // persist — replace this company's previous ingestion of the same name;
    // if another company owns the name (workspaces.name is globally unique),
    // pick a free suffixed name instead
    await query(`delete from workspaces where name = $1 and kind = 'ingested' and company_id = $2`, [
      job.workspace_name,
      job.company_id,
    ]);
    let wsName = job.workspace_name;
    for (let suffix = 2; ; suffix++) {
      const [taken] = await query<{ id: string }>(`select id from workspaces where name = $1`, [wsName]);
      if (!taken) break;
      wsName = `${job.workspace_name}-${suffix}`;
    }
    if (wsName !== job.workspace_name) await update(job.id, { workspace_name: wsName });
    const [ws] = await query<{ id: string }>(
      `insert into workspaces (name, source, kind, company_id, source_branch) values ($1, $2, 'ingested', $3, $4) returning id`,
      [wsName, job.git_url, job.company_id, sourceBranch]
    );
    createdWorkspaceId = ws.id;
    const { index, edgeCount } = await insertWorkspaceGraph(ws.id, result, new Map());
    const planned = await planSummaryIds(ws.id, SUMMARY_CAP);

    await update(job.id, {
      status: planned.length > 0 ? "summarizing" : "ready",
      objects_total: index.byKey.size,
      edges_total: edgeCount,
      summaries_planned: planned.length,
      workspace_id: ws.id,
      lease_expires_at: null,
    });
  } catch (e) {
    await failJob(job, (e as Error).message, createdWorkspaceId);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

/** One batch of Haiku summaries; marks the job ready when the plan is done. */
async function runSummarizeChunk(job: IngestionJob): Promise<void> {
  try {
    if (!job.workspace_id) throw new Error("job has no workspace");
    const remaining = (job.summaries_planned ?? 0) - job.summaries_done;
    if (remaining <= 0) {
      await update(job.id, { status: "ready", lease_expires_at: null });
      return;
    }
    const ids = await planSummaryIds(job.workspace_id, Math.min(SUMMARY_BATCH, remaining));
    if (ids.length === 0) {
      await update(job.id, { status: "ready", lease_expires_at: null });
      return;
    }
    const result = await summarizeStoredObjects(job.workspace_id, ids, { log: console.warn });
    if (result.done === 0 && result.failed > 0) {
      // zero progress (e.g. API credit exhaustion or a poison batch): shrink
      // the plan so the job converges; unsummarized objects fall back to the
      // lazy on-first-access path
      await update(job.id, {
        summaries_planned: Math.max(job.summaries_done, (job.summaries_planned ?? 0) - result.failed),
        lease_expires_at: null,
      });
      return;
    }
    const done = job.summaries_done + result.done;
    const finished = done >= (job.summaries_planned ?? 0);
    await update(job.id, {
      summaries_done: done,
      status: finished ? "ready" : "summarizing",
      lease_expires_at: null,
    });
  } catch (e) {
    await failJob(job, (e as Error).message);
  }
}

/**
 * Process one chunk of the oldest active job. Returns the job it worked on
 * (with fresh state) or null when there was nothing claimable.
 */
export async function processChunk(): Promise<IngestionJob | null> {
  const job = await claimNext();
  if (!job) return null;
  if (job.status === "queued" || job.status === "cloning" || job.status === "parsing" || job.status === "graph") {
    // 'cloning'/'parsing'/'graph' here means a previous worker died mid-phase
    // and the lease expired — restart the phase from the top (it is
    // idempotent: the partial workspace is replaced)
    await runIngestPhase(job);
  } else if (job.status === "summarizing") {
    await runSummarizeChunk(job);
  }
  return getJob(job.id);
}
