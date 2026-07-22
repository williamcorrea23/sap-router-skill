"use client";

/**
 * B1/B3 + CO-06 — live ingestion progress as a pipeline stage view: polls
 * /api/ingest/jobs/<id> while the chunked worker runs
 * (fetch → parse → graph → summarize → ready) and hands off to the workspace
 * when ready. Polling doubles as stall recovery. All detail numbers are job
 * counters. The failing stage is derived from which counters were reached:
 * no files_total → fetch, no files_parsed → parse, no objects_total → graph,
 * else summarize.
 */
import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Card from "../../../../components/ui/Card";
import PipelineStages, { type StageView } from "../../../../components/PipelineStages";

interface Job {
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
}

const num = (v: number | null | undefined) => Number(v ?? 0).toLocaleString("en-US");

const ACTIVE_STATUSES: Job["status"][] = ["cloning", "parsing", "graph", "summarizing"];

// 'ready' ranks past the Ready card (pos > stagePos → done): the terminal
// status renders as a completed stage, not a running one.
const STAGE_ORDER = { queued: 0, cloning: 1, parsing: 2, graph: 3, summarizing: 4, ready: 6, failed: -1 } as const;

function failedStageKey(job: Job): "fetch" | "parse" | "graph" | "summarize" {
  if (job.files_total == null) return "fetch";
  if (job.files_parsed == null) return "parse";
  if (job.objects_total == null) return "graph";
  return "summarize";
}

function buildStages(job: Job): StageView[] {
  const pos = STAGE_ORDER[job.status];
  const failedAt = job.status === "failed" ? failedStageKey(job) : null;
  const parseRate =
    job.files_total && job.files_parsed != null
      ? `${((100 * job.files_parsed) / job.files_total).toFixed(1)}%`
      : null;
  const lazyNote =
    job.summaries_planned != null && job.objects_total != null && job.summaries_planned < job.objects_total
      ? " — rest generated on first access"
      : "";

  const stage = (
    key: StageView["key"],
    title: string,
    stagePos: number,
    runningDetail: string,
    doneDetail: string | null
  ): StageView => {
    if (failedAt === key) return { key, title, status: "failed", error: job.error ?? "unknown error" };
    if (failedAt) {
      // earlier completed stages stay done; later ones stay pending
      const failedPos = { fetch: 1, parse: 2, graph: 3, summarize: 4 }[failedAt];
      return stagePos < failedPos
        ? { key, title, status: "done", detail: doneDetail ?? undefined }
        : { key, title, status: "pending" };
    }
    if (pos > stagePos) return { key, title, status: "done", detail: doneDetail ?? undefined };
    if (pos === stagePos) return { key, title, status: "running", detail: runningDetail };
    return { key, title, status: "pending" };
  };

  return [
    stage("fetch", "Fetch", 1, "Cloning repository…", job.files_total != null ? `${num(job.files_total)} files` : null),
    stage("parse", "Parse", 2, "Parsing ABAP sources…", parseRate ? `parse success ${parseRate}` : null),
    stage(
      "graph",
      "Graph",
      3,
      "Building dependency graph…",
      job.objects_total != null ? `${num(job.objects_total)} objects · ${num(job.edges_total)} edges` : null
    ),
    stage(
      "summarize",
      "Summarize",
      4,
      `Generating documentation… ${job.summaries_done}/${num(job.summaries_planned)}`,
      job.summaries_planned != null ? `${job.summaries_done}/${num(job.summaries_planned)} summaries${lazyNote}` : null
    ),
    stage("ready", "Ready", 5, "", job.status === "ready" ? "system available" : null),
  ];
}

export default function IngestProgressPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [job, setJob] = useState<Job | null>(null);
  const [notFound, setNotFound] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    let stopped = false;
    async function poll() {
      if (stopped) return;
      try {
        const res = await fetch(`/api/ingest/jobs/${id}`);
        if (res.status === 404) {
          setNotFound(true);
          return;
        }
        const data = await res.json();
        if (data.job) {
          setJob(data.job);
          if (data.job.status === "ready" || data.job.status === "failed") return;
        }
      } catch {
        // transient — keep polling
      }
      timer.current = setTimeout(poll, 1500);
    }
    poll();
    return () => {
      stopped = true;
      if (timer.current) clearTimeout(timer.current);
    };
  }, [id]);

  const openWorkspace = (target: "chat" | "report" | "overview") => {
    if (!job) return;
    localStorage.setItem("workspace", job.workspace_name);
    // Chat is a global surface scoped by the stored selection; Overview and
    // Report live under the workspace's own routes.
    router.push(target === "chat" ? "/chat" : `/w/${encodeURIComponent(job.workspace_name)}/${target}`);
  };

  return (
    <div style={{ padding: 24 }}>
      <Card>
        {notFound && <p style={{ fontSize: 13, color: "#CC420B" }}>Ingestion job not found.</p>}
        {!job && !notFound && <p style={{ fontSize: 13, color: "#A49C95" }}>Loading…</p>}
        {job && (
          <>
            <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 2 }}>
              Ingesting <span style={{ fontFamily: "JetBrains Mono, monospace" }}>{job.workspace_name}</span>
            </h2>
            <p style={{ fontSize: 12, color: "#6E6660", marginBottom: 16, fontFamily: "JetBrains Mono, monospace" }}>
              {job.git_url}
            </p>

            {job.status === "queued" && (
              <p style={{ fontSize: 13, color: "#6E6660", marginBottom: 12 }}>
                Queued — another ingestion is running; this one starts automatically when it finishes.
              </p>
            )}

            <PipelineStages stages={buildStages(job)} />

            {ACTIVE_STATUSES.includes(job.status) && (
              <p style={{ fontSize: 12, color: "#A49C95", marginTop: 10 }}>
                Processing — this can take a while for larger repositories.
              </p>
            )}

            {job.status === "ready" && (
              <div style={{ display: "flex", gap: 16, marginTop: 16, fontSize: 13, color: "#6E6660" }}>
                <span><strong style={{ color: "#1B1817" }}>{num(job.files_total)}</strong> files</span>
                <span><strong style={{ color: "#1B1817" }}>{num(job.objects_total)}</strong> objects</span>
                <span><strong style={{ color: "#1B1817" }}>{num(job.edges_total)}</strong> call edges</span>
                <span><strong style={{ color: "#1B1817" }}>{job.summaries_done}</strong> summaries</span>
              </div>
            )}

            <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
              {job.status === "ready" && (
                <>
                  <button
                    onClick={() => openWorkspace("chat")}
                    style={{ fontSize: 13, fontWeight: 600, color: "#FFFFFF", backgroundColor: "#F04E0D", border: "none", borderRadius: 8, padding: "9px 16px", cursor: "pointer", fontFamily: "inherit" }}
                  >
                    Open chat
                  </button>
                  <button
                    onClick={() => openWorkspace("report")}
                    style={{ fontSize: 13, fontWeight: 600, color: "#1B1817", backgroundColor: "#FFFFFF", border: "1px solid #E8E2DB", borderRadius: 8, padding: "9px 16px", cursor: "pointer", fontFamily: "inherit" }}
                  >
                    Run report
                  </button>
                </>
              )}
              <button
                onClick={() => router.push("/connections/systems")}
                style={{ fontSize: 13, fontWeight: 600, color: "#1B1817", backgroundColor: "#FFFFFF", border: "1px solid #E8E2DB", borderRadius: 8, padding: "9px 16px", cursor: "pointer", fontFamily: "inherit" }}
              >
                Back to connections
              </button>
            </div>
          </>
        )}
      </Card>
    </div>
  );
}
