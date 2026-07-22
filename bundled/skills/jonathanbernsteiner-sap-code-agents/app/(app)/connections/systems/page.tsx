"use client";

/**
 * Connections → Connected systems. Every connected source with its ingestion
 * pipeline status, re-ingest, delete (cascade per CO-03). Cards open the
 * system's Overview; day-to-day navigation between systems happens via the
 * workspace switcher in the workspace header, not here.
 */
import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { GitBranch, MoreHorizontal } from "lucide-react";
import Card from "../../../../components/ui/Card";
import GradeBar from "../../../../components/ui/GradeBar";
import { isRepoUrl, repoBaseUrl, repoDisplayName } from "../../../../lib/source-links";
import type { ActiveReportRun, IngestionJobInfo, PendingJob, WorkspaceInfo } from "../../../../components/useWorkspace";

const ACTIVE_STATUSES = ["queued", "cloning", "parsing", "graph", "summarizing"];

function jobStageLabel(j: IngestionJobInfo): string {
  switch (j.status) {
    case "queued":
      return "queued";
    case "cloning":
      return "cloning repository";
    case "parsing":
      return j.files_total ? `parsing ${j.files_parsed ?? 0}/${j.files_total} files` : "parsing";
    case "graph":
      return "building call graph";
    case "summarizing":
      return j.summaries_planned
        ? `auto-docs ${j.summaries_done ?? 0}/${j.summaries_planned}`
        : "generating auto-docs";
    default:
      return j.status;
  }
}

/** Plain-language stage for an in-flight report run, shown on the card. */
function reportStageLabel(r: ActiveReportRun): string {
  switch (r.stage) {
    case "queued":
      return "starting";
    case "analyzing":
      return r.analyze_total ? `analyzing ${r.objects_done}/${r.analyze_total} objects` : "analyzing objects";
    case "validating":
      return "running validators";
    case "rendering":
      return "rendering report";
    default:
      return r.stage;
  }
}

export default function ConnectedSystemsPage() {
  const [workspaces, setWorkspaces] = useState<WorkspaceInfo[] | null>(null);
  const [pendingJobs, setPendingJobs] = useState<PendingJob[]>([]);
  const [error, setError] = useState<string | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const load = useCallback(async () => {
    try {
      const d = await fetch("/api/workspaces").then((r) => r.json());
      setWorkspaces(d.workspaces ?? []);
      setPendingJobs(d.pending_jobs ?? []);
      return { workspaces: (d.workspaces ?? []) as WorkspaceInfo[], pending: (d.pending_jobs ?? []) as PendingJob[] };
    } catch {
      return null;
    }
  }, []);

  // poll while any ingestion OR report run is active, so both kinds of
  // progress update live on this page rather than on the tab we no longer
  // redirect to
  useEffect(() => {
    let stopped = false;
    async function tick() {
      if (stopped) return;
      const res = await load();
      const active =
        !!res &&
        (res.pending.some((j) => ACTIVE_STATUSES.includes(j.status)) ||
          res.workspaces.some((w) => w.last_job && ACTIVE_STATUSES.includes(w.last_job.status)) ||
          res.workspaces.some((w) => !!w.active_report_run));
      timer.current = setTimeout(tick, active ? 2000 : 15000);
    }
    tick();
    return () => {
      stopped = true;
      if (timer.current) clearTimeout(timer.current);
    };
  }, [load]);

  const startIngest = async (url: string, name?: string): Promise<string | null> => {
    try {
      const res = await fetch("/api/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, ...(name ? { name } : {}) }),
      });
      const data = await res.json();
      if (!res.ok) return data.error ?? "Ingestion could not be started.";
      await load();
      return null;
    } catch {
      return "Ingestion could not be started.";
    }
  };

  const remove = async (name: string) => {
    if (!window.confirm(`Delete system "${name}" and all its analysis data? This cannot be undone.`)) return;
    setError(null);
    const res = await fetch(`/api/workspaces?name=${encodeURIComponent(name)}`, { method: "DELETE" });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      setError(data.error ?? "Delete failed.");
    }
    await load();
  };

  const dismissJob = async (id: string) => {
    setError(null);
    const res = await fetch(`/api/ingest/jobs/${id}`, { method: "DELETE" });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      setError(data.error ?? "Could not dismiss the job.");
    }
    await load();
  };

  return (
    <>
      {error && (
        <div style={{ fontSize: 13, color: "#CC420B", backgroundColor: "#FCEDE4", border: "1px solid #F6D9CB", borderRadius: 8, padding: "10px 12px" }}>
          {error}
        </div>
      )}

      <Card>
        <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 12 }}>Connected systems</h2>
        {workspaces === null && <p style={{ fontSize: 13, color: "#A49C95" }}>Loading…</p>}
        {workspaces !== null && workspaces.length === 0 && pendingJobs.length === 0 && (
          <p style={{ fontSize: 13, color: "#6E6660" }}>
            No systems connected yet.{" "}
            <Link href="/connections" style={{ color: "#CC420B", fontWeight: 600 }}>
              Connect a system →
            </Link>
          </p>
        )}
        {/* transient states (running/failed ingestions without a workspace
            row) stay full-width rows — they carry actions and error text */}
        {pendingJobs.length > 0 && (
          <div style={{ display: "flex", flexDirection: "column", gap: 10, marginBottom: 12 }}>
            {pendingJobs.map((j) => (
              <PendingJobRow key={j.id} job={j} onRetry={startIngest} onDismiss={dismissJob} />
            ))}
          </div>
        )}
        {/* connected sources as full-width bars, one per system */}
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {(workspaces ?? []).map((w) => (
            <SourceCard key={w.name} w={w} onReingest={startIngest} onDelete={remove} onReportStarted={load} />
          ))}
        </div>
      </Card>
    </>
  );
}

function Badge({ children, tone }: { children: React.ReactNode; tone: "accent" | "muted" | "failed" }) {
  return (
    <span
      style={{
        fontSize: 11, fontWeight: 600, borderRadius: 6, padding: "2px 8px", whiteSpace: "nowrap",
        color: tone === "muted" ? "#6E6660" : "#CC420B",
        backgroundColor: tone === "muted" ? "#F0EDE8" : "#FCEDE4",
      }}
    >
      {children}
    </span>
  );
}

function StatusChip({ job }: { job: IngestionJobInfo }) {
  if (ACTIVE_STATUSES.includes(job.status)) {
    return (
      <span style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 11, fontWeight: 600, color: "#CC420B" }}>
        <span style={{ width: 7, height: 7, borderRadius: "50%", backgroundColor: "#F04E0D" }} />
        INGESTING — {jobStageLabel(job)}
      </span>
    );
  }
  if (job.status === "failed") {
    return <Badge tone="failed">FAILED</Badge>;
  }
  return <span style={{ fontSize: 11, fontWeight: 600, color: "#A49C95" }}>READY</span>;
}

function ActionButton({ label, onClick, danger, disabled }: { label: string; onClick: () => void; danger?: boolean; disabled?: boolean }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        fontSize: 12, fontWeight: 600, color: danger ? "#CC420B" : "#1B1817",
        backgroundColor: "#FFFFFF", border: "1px solid #E8E2DB", borderRadius: 8,
        padding: "6px 12px", cursor: disabled ? "default" : "pointer", fontFamily: "inherit",
        opacity: disabled ? 0.5 : 1, flexShrink: 0,
      }}
    >
      {label}
    </button>
  );
}

interface KebabItem {
  label: string;
  onClick: () => void;
  danger?: boolean;
  disabled?: boolean;
}

/** ⋯ menu on a connected-source card. Stops propagation so the clickable
 *  card underneath never navigates when the menu is used. */
function KebabMenu({ items }: { items: KebabItem[] }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    window.addEventListener("mousedown", onClick);
    return () => window.removeEventListener("mousedown", onClick);
  }, [open]);

  return (
    <div ref={ref} style={{ position: "relative", flexShrink: 0 }} onClick={(e) => e.stopPropagation()}>
      <button
        onClick={() => setOpen((o) => !o)}
        aria-label="Source actions"
        aria-expanded={open}
        style={{
          display: "inline-flex", alignItems: "center", justifyContent: "center",
          width: 30, height: 30, backgroundColor: open ? "#F0EDE8" : "transparent",
          border: "none", borderRadius: 8, cursor: "pointer", color: "#6E6660",
        }}
      >
        <MoreHorizontal size={18} />
      </button>
      {open && (
        <div
          style={{
            position: "absolute", right: 0, top: "calc(100% + 4px)", minWidth: 150, zIndex: 30,
            backgroundColor: "#FFFFFF", border: "1px solid #E8E2DB", borderRadius: 10,
            boxShadow: "0 8px 24px rgba(23,20,18,0.12)", overflow: "hidden", padding: 4,
          }}
        >
          {items.map((item) => (
            <button
              key={item.label}
              disabled={item.disabled}
              onClick={() => {
                setOpen(false);
                item.onClick();
              }}
              style={{
                display: "block", width: "100%", textAlign: "left", fontSize: 13, fontFamily: "inherit",
                color: item.danger ? "#CC420B" : "#1B1817", backgroundColor: "transparent",
                border: "none", borderRadius: 6, padding: "7px 10px",
                cursor: item.disabled ? "default" : "pointer", opacity: item.disabled ? 0.5 : 1,
              }}
              onMouseEnter={(e) => {
                if (!item.disabled) e.currentTarget.style.backgroundColor = "#FAF8F5";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = "transparent";
              }}
            >
              {item.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

/** A source with no workspace row yet — fresh ingestion or failed attempt. */
function PendingJobRow({
  job, onRetry, onDismiss,
}: {
  job: PendingJob;
  onRetry: (url: string, name?: string) => Promise<string | null>;
  onDismiss: (id: string) => void;
}) {
  const active = ACTIVE_STATUSES.includes(job.status);
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "12px 14px", border: "1px solid #E8E2DB", borderRadius: 10, backgroundColor: "#FFFFFF" }}>
      <GitBranch size={18} style={{ color: "#A49C95", flexShrink: 0 }} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 2, flexWrap: "wrap" }}>
          <span style={{ fontSize: 14, fontWeight: 600, fontFamily: "JetBrains Mono, monospace", color: "#1B1817" }}>
            {job.workspace_name}
          </span>
          <Badge tone="muted">{job.git_url}</Badge>
          <StatusChip job={job} />
        </div>
        {job.status === "failed" && job.error && (
          <div style={{ fontSize: 12, color: "#CC420B", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {job.error}
          </div>
        )}
        {active && (
          <Link href={`/ingest/${job.id}`} style={{ fontSize: 12, color: "#CC420B", fontWeight: 600 }}>
            View pipeline →
          </Link>
        )}
      </div>
      {job.status === "failed" && (
        <>
          <ActionButton label="Retry" onClick={() => onRetry(job.git_url, job.workspace_name)} />
          <ActionButton label="Dismiss" onClick={() => onDismiss(job.id)} danger />
        </>
      )}
    </div>
  );
}

function SourceCard({
  w, onReingest, onDelete, onReportStarted,
}: {
  w: WorkspaceInfo;
  onReingest: (url: string, name?: string) => Promise<string | null>;
  onReportStarted: () => Promise<unknown>;
  onDelete: (name: string) => void;
}) {
  const router = useRouter();
  const [reingesting, setReingesting] = useState(false);
  const [startingReport, setStartingReport] = useState(false);
  const [hovered, setHovered] = useState(false);
  const active = !!w.last_job && ACTIVE_STATUSES.includes(w.last_job.status);
  const report = w.active_report_run;
  const reportBusy = !!report || startingReport;
  const findings = Number(w.tier1_findings) + Number(w.tier2_findings);

  // straight to Overview — the sidebar "Workspace" item takes over, no
  // visual discontinuity
  const open = () => router.push(`/w/${encodeURIComponent(w.name)}/overview`);

  // Trigger a report run from the card and STAY HERE. The list already polls,
  // so the card shows the run's progress in place and picks up its grades when
  // it finishes — clicking never moves you off the page you chose to be on.
  // (409 = already running, which is equally fine.)
  const runReport = async () => {
    setStartingReport(true);
    try {
      const res = await fetch("/api/report/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ workspace: w.name }),
      });
      if (res.status === 202 || res.status === 409) {
        await onReportStarted();
      } else {
        const body = await res.json().catch(() => ({}));
        window.alert(body.error ?? "The report run could not be started.");
      }
    } catch {
      window.alert("The report run could not be started.");
    }
    setStartingReport(false);
  };

  const reingest = async () => {
    if (!window.confirm(`Re-ingest "${w.name}" from ${w.source}? The system is replaced by the fresh ingestion.`)) return;
    setReingesting(true);
    const err = await onReingest(w.source, w.name);
    if (err) window.alert(err);
    setReingesting(false);
  };

  const menuItems: KebabItem[] = [
    { label: "Open", onClick: open },
    ...(w.kind === "ingested"
      ? [
          {
            label: startingReport ? "Starting…" : w.grades ? "Re-run migration report" : "Run migration report",
            onClick: runReport,
            disabled: startingReport || active,
          },
          { label: reingesting ? "Starting…" : "Re-ingest", onClick: reingest, disabled: reingesting || active },
          { label: "Delete", onClick: () => onDelete(w.name), danger: true, disabled: active },
        ]
      : []),
  ];

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={open}
      onKeyDown={(e) => {
        if (e.key === "Enter" && e.target === e.currentTarget) open();
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display: "flex", flexDirection: "column", gap: 6, padding: "14px 16px",
        border: `1px solid ${hovered ? "#F04E0D" : "#E8E2DB"}`, borderRadius: 10,
        backgroundColor: "#FFFFFF", cursor: "pointer", transition: "border-color 150ms ease",
      }}
    >
      {/* header: icon + name + truthful badges, kebab top-right */}
      <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
        <GitBranch size={18} style={{ color: "#A49C95", flexShrink: 0, marginTop: 5 }} />
        <div style={{ flex: 1, minWidth: 0, display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap", paddingTop: 3 }}>
          <span style={{ fontSize: 14, fontWeight: 600, color: "#1B1817", fontFamily: "JetBrains Mono, monospace" }}>
            {w.name}
          </span>
          {/* badges only where true — fixtures keep EXAMPLE (+ SIMULATED
              USAGE); repo-ingested systems get the provenance subtitle */}
          {w.kind === "example" && <Badge tone="accent">EXAMPLE</Badge>}
          {w.simulated_usage && <Badge tone="accent">SIMULATED USAGE</Badge>}
          {w.kind === "ingested" && w.last_job && <StatusChip job={w.last_job} />}
        </div>
        <KebabMenu items={menuItems} />
      </div>
      {/* provenance — quiet repo link when the upstream URL is known (repo
          level only; file deep links stay ingested-only), plain marker for
          bundled fixture data */}
      <div style={{ fontSize: 12, color: "#6E6660", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
        {isRepoUrl(w.source) ? (
          <a
            href={repoBaseUrl(w.source)}
            target="_blank"
            rel="noreferrer"
            onClick={(e) => e.stopPropagation()}
            style={{ color: "#6E6660", textDecoration: "underline", textUnderlineOffset: 2 }}
          >
            {repoDisplayName(w.source)}
          </a>
        ) : (
          "bundled example data"
        )}
        {w.kind === "ingested" && ` · ingested ${String(w.seeded_at).slice(0, 10)}`}
      </div>
      {/* single stats line — the bar spans the page, width is ample */}
      <div style={{ fontSize: 12, color: "#6E6660", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
        {Number(w.objects).toLocaleString("en-US")} objects · {Number(w.call_edges).toLocaleString("en-US")} call edges
        {findings > 0 ? ` · ${findings.toLocaleString("en-US")} findings (T1+T2)` : " · no report run yet"}
        {Number(w.usage_rows) > 0 ? ` · usage data${w.simulated_usage ? " (simulated)" : ""}` : " · no usage data"}
      </div>
      {/* no report run yet on an ingested system — offer the run right here
          instead of sending the user through Overview first */}
      {w.kind === "ingested" && !w.grades && !active && !report && (
        <div style={{ paddingTop: 2 }}>
          <button
            onClick={(e) => {
              e.stopPropagation();
              runReport();
            }}
            disabled={reportBusy}
            style={{
              fontSize: 12, fontWeight: 600, color: "#FFFFFF",
              backgroundColor: reportBusy ? "#A49C95" : "#F04E0D",
              border: "none", borderRadius: 8, padding: "7px 14px",
              cursor: reportBusy ? "default" : "pointer", fontFamily: "inherit",
            }}
          >
            {reportBusy ? "Starting…" : "Run migration report"}
          </button>
        </div>
      )}
      {/* progress stays on this page — no redirect to the report tab */}
      {report && (
        <div style={{ fontSize: 12, color: "#CC420B", fontWeight: 600, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          Report running — {reportStageLabel(report)}
        </div>
      )}
      {w.last_job?.status === "failed" && w.last_job.error && (
        <div style={{ fontSize: 12, color: "#CC420B", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          Last ingestion failed: {w.last_job.error}
        </div>
      )}
      {active && w.last_job && (
        <Link
          href={`/ingest/${w.last_job.id}`}
          onClick={(e) => e.stopPropagation()}
          style={{ fontSize: 12, color: "#CC420B", fontWeight: 600, alignSelf: "flex-start" }}
        >
          View pipeline →
        </Link>
      )}
      {/* mini grade-distribution bar pinned to the tile bottom; only where a
          report run has graded the objects (grades = null means no run yet) */}
      {w.grades && (
        <div style={{ marginTop: "auto", paddingTop: 6 }}>
          <GradeBar grades={w.grades} compact />
        </div>
      )}
    </div>
  );
}
