"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { StageView } from "./PipelineStages";

/**
 * The report run, as a workspace-level concern rather than a Report-tab one.
 * Any tab can start a run and watch it: the Overview is where people land, so
 * sending them to another tab just to see "analyzing 3 of 13" was the wrong
 * shape. Both tabs share this hook so the stage mapping, the poll cadence and
 * the failure handling cannot drift apart.
 */

export interface HistoryEntry {
  id: string;
  stage: string;
  started_at: string;
  finished_at: string | null;
  objects_analyzed: number | null;
  error: string | null;
  tier1: number | null;
  tier2: number | null;
  retirement: number | null;
}

export interface RunStatus {
  run: {
    id: string;
    stage: "queued" | "analyzing" | "validating" | "rendering" | "done" | "failed";
    failed_stage: string | null;
    objects_analyzed: number | null;
    objects_done: number;
    analyze_total: number | null;
    error: string | null;
  } | null;
  tiers?: Record<string, number>;
  history?: HistoryEntry[];
}

export const ACTIVE_STAGES = ["queued", "analyzing", "validating", "rendering"];

export function useReportRun(workspace: string, onFinished?: () => void) {
  const [status, setStatus] = useState<RunStatus | null>(null);
  const [runError, setRunError] = useState<string | null>(null);
  const [pollNonce, setPollNonce] = useState(0);
  const pollTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  // keep the callback out of the effect's deps: a caller that re-creates it
  // every render must not restart polling
  const finishedRef = useRef(onFinished);
  finishedRef.current = onFinished;

  useEffect(() => {
    if (!workspace) return;
    let stopped = false;
    let wasActive = false;
    async function poll() {
      if (stopped) return;
      try {
        const res = await fetch(`/api/report/run?workspace=${encodeURIComponent(workspace)}`);
        const next: RunStatus = await res.json();
        if (stopped) return;
        setStatus(next);
        const active = !!next.run && ACTIVE_STAGES.includes(next.run.stage);
        if (wasActive && next.run?.stage === "done") finishedRef.current?.();
        wasActive = active;
        if (active) pollTimer.current = setTimeout(poll, 1500);
      } catch {
        pollTimer.current = setTimeout(poll, 3000);
      }
    }
    poll();
    return () => {
      stopped = true;
      if (pollTimer.current) clearTimeout(pollTimer.current);
    };
  }, [workspace, pollNonce]);

  const startRun = useCallback(async () => {
    if (!workspace) return;
    setRunError(null);
    const res = await fetch("/api/report/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ workspace }),
    });
    if (res.status === 202 || res.status === 409) {
      setPollNonce((n) => n + 1); // restart the polling effect
    } else {
      const body = await res.json().catch(() => ({}));
      setRunError(body.error ?? "could not start the report run");
    }
  }, [workspace]);

  const runActive = !!status?.run && ACTIVE_STAGES.includes(status.run.stage);
  return {
    status,
    runActive,
    /** a finished-but-failed run keeps its failing stage on screen */
    showPipeline: !!status?.run && (runActive || status.run.stage === "failed"),
    startRun,
    runError,
    reset: () => setRunError(null),
  };
}

/** Map the persisted run stage + counters onto the 3 pipeline cards. */
export function reportStages(status: RunStatus): StageView[] {
  const run = status.run!;
  const tiers = status.tiers ?? {};
  const tierTotal = (tiers["1"] ?? 0) + (tiers["2"] ?? 0) + (tiers["3"] ?? 0);
  const pos = { queued: 0, analyzing: 1, validating: 2, rendering: 3, done: 4, failed: -1 }[run.stage];
  const failedPos =
    run.stage === "failed"
      ? ({ queued: 1, analyzing: 1, validating: 2, rendering: 3 } as Record<string, number>)[run.failed_stage ?? "analyzing"] ?? 1
      : null;

  const mk = (key: string, title: string, stagePos: number, runningDetail: string, doneDetail: string): StageView => {
    if (failedPos !== null) {
      if (stagePos === failedPos) return { key, title, status: "failed", error: run.error ?? "unknown error" };
      return stagePos < failedPos ? { key, title, status: "done", detail: doneDetail } : { key, title, status: "pending" };
    }
    if (pos > stagePos) return { key, title, status: "done", detail: doneDetail };
    if (pos === stagePos) return { key, title, status: "running", detail: runningDetail };
    return { key, title, status: "pending" };
  };

  return [
    mk(
      "analyze",
      "Analyze",
      1,
      run.analyze_total != null ? `Analyzing objects… ${run.objects_done} of ${run.analyze_total}` : "Analyzing objects…",
      run.analyze_total != null ? `${run.analyze_total} objects analyzed` : "analysis complete"
    ),
    mk(
      "validate",
      "Validate",
      2,
      "Running deterministic validators…",
      tierTotal > 0 ? `Tier 1: ${tiers["1"] ?? 0} · Tier 2: ${tiers["2"] ?? 0}` : "validators complete"
    ),
    mk("deliver", "Deliver", 3, "Rendering report + executive summary…", "report ready below"),
  ];
}
