"use client";

import { useEffect, useState } from "react";

export interface WorkspaceInfo {
  name: string;
  source: string;
  /** branch recorded at ingestion (null for fixtures / older ingestions) */
  source_branch: string | null;
  kind: "example" | "ingested";
  simulated_usage: boolean;
  objects: string;
  parse_failed: string;
  call_edges: string;
  table_accesses: string;
  usage_rows: string;
  summaries: string;
  tier1_findings: string;
  tier2_findings: string;
  tier3_findings: string;
  /** grade → object count from the latest finished run; null = no run yet */
  grades: Record<string, number> | null;
  /** null when the workspace has no usage data */
  retirement_candidates: string | null;
  /** latest ingestion job of the caller's company for this source (null for
   *  example workspaces / pre-job seeds) */
  last_job: IngestionJobInfo | null;
  /** an in-flight report run, so a card can show progress without navigating */
  active_report_run: ActiveReportRun | null;
  seeded_at: string;
}

export interface ActiveReportRun {
  id: string;
  stage: "queued" | "analyzing" | "validating" | "rendering";
  objects_done: number;
  analyze_total: number | null;
}

export interface IngestionJobInfo {
  id: string;
  status: "queued" | "cloning" | "parsing" | "graph" | "summarizing" | "ready" | "failed";
  error: string | null;
  files_parsed: number | null;
  files_total: number | null;
  summaries_done: number | null;
  summaries_planned: number | null;
  created_at: string;
}

/** An ingestion with no workspace row yet (fresh source or failed attempt). */
export interface PendingJob extends IngestionJobInfo {
  git_url: string;
  workspace_name: string;
}

/** Shared workspace selection (persisted in localStorage) + workspace list. */
export function useWorkspace() {
  const [workspaces, setWorkspaces] = useState<WorkspaceInfo[]>([]);
  const [selected, setSelectedState] = useState<string>("");

  useEffect(() => {
    fetch("/api/workspaces")
      .then((r) => r.json())
      .then((d) => {
        const list: WorkspaceInfo[] = d.workspaces ?? [];
        setWorkspaces(list);
        const stored = localStorage.getItem("workspace");
        if (stored && list.some((w) => w.name === stored)) setSelectedState(stored);
        else if (list.length > 0) setSelectedState(list[0].name);
      })
      .catch(() => setWorkspaces([]));
  }, []);

  const setSelected = (name: string) => {
    localStorage.setItem("workspace", name);
    setSelectedState(name);
  };

  const current = workspaces.find((w) => w.name === selected);
  return { workspaces, selected, setSelected, current };
}
