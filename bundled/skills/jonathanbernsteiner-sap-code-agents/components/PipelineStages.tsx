"use client";

/**
 * CO-06 — pipeline stage view, shared by the ingestion progress screen and
 * the report-run progress card. A horizontal sequence of stage cards
 * (wrapping on small screens) joined by a subtle connector line; each card
 * carries a status chip and a short detail line. Detail numbers come from
 * SQL/job counters — callers never pass LLM output here.
 */

export interface StageView {
  key: string;
  title: string;
  status: "pending" | "running" | "done" | "failed";
  /** short detail line: running-state label or done-state numbers */
  detail?: string;
  /** failure reason, shown beneath a failed stage */
  error?: string;
}

export default function PipelineStages({ stages }: { stages: StageView[] }) {
  return (
    <div style={{ display: "flex", alignItems: "stretch", flexWrap: "wrap", gap: "8px 0" }}>
      <style>{`@keyframes co06-pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.45; } }`}</style>
      {stages.map((s, i) => (
        <div key={s.key} style={{ display: "flex", alignItems: "center", flex: "1 1 150px", minWidth: 150 }}>
          {i > 0 && <div style={{ width: 14, minWidth: 8, height: 1, backgroundColor: "#E8E2DB", flexShrink: 1 }} />}
          <div
            style={{
              flex: 1,
              border: `1px solid ${s.status === "failed" ? "#F04E0D" : "#E8E2DB"}`,
              borderRadius: 10,
              padding: "10px 12px",
              backgroundColor: s.status === "pending" ? "#FAF8F5" : "#FFFFFF",
              opacity: s.status === "pending" ? 0.75 : 1,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
              <StatusChip status={s.status} />
              <span style={{ fontSize: 13, fontWeight: 600, color: s.status === "pending" ? "#A49C95" : "#1B1817" }}>
                {s.title}
              </span>
            </div>
            {s.detail && (
              <div style={{ fontSize: 11, color: "#6E6660", lineHeight: 1.4 }}>{s.detail}</div>
            )}
            {s.status === "failed" && s.error && (
              <div style={{ fontSize: 11, color: "#CC420B", marginTop: 4, lineHeight: 1.4 }}>{s.error}</div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function StatusChip({ status }: { status: StageView["status"] }) {
  const base = {
    width: 16,
    height: 16,
    borderRadius: 8,
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 10,
    fontWeight: 700,
    flexShrink: 0,
  } as const;
  switch (status) {
    case "done":
      return <span style={{ ...base, color: "#FFFFFF", backgroundColor: "#F04E0D" }}>✓</span>;
    case "running":
      return (
        <span
          style={{ ...base, backgroundColor: "#F04E0D", animation: "co06-pulse 1.2s ease-in-out infinite" }}
        />
      );
    case "failed":
      return <span style={{ ...base, color: "#FFFFFF", backgroundColor: "#CC420B" }}>✕</span>;
    default:
      return <span style={{ ...base, backgroundColor: "#F0EDE8" }} />;
  }
}
