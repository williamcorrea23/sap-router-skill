"use client";

import Card from "./ui/Card";
import PipelineStages from "./PipelineStages";
import { reportStages, type RunStatus } from "./useReportRun";

/**
 * Live report-run progress. Rendered identically on the Overview and the
 * Report tab, so starting a run never means being sent somewhere else to
 * watch it.
 */
export default function ReportPipelineCard({
  status,
  /** shown on the Overview, where the findings are one tab away */
  linkToReport,
}: {
  status: RunStatus;
  linkToReport?: string;
}) {
  const stage = status.run?.stage;
  return (
    <Card className="print:hidden">
      <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 2 }}>Report pipeline</h3>
      <p style={{ fontSize: 12, color: "#A49C95", marginBottom: 12 }}>
        {stage === "queued"
          ? "Starting…"
          : stage === "failed"
            ? "The last report run failed."
            : "Generating the migration report — this page updates live."}
      </p>
      <PipelineStages stages={reportStages(status)} />
      {linkToReport && stage !== "failed" && (
        <p style={{ fontSize: 12, color: "#A49C95", marginTop: 12, marginBottom: 0 }}>
          Grades and findings appear here when the run finishes.{" "}
          <a href={linkToReport} style={{ color: "#CC420B", fontWeight: 600 }}>
            Open the full report →
          </a>
        </p>
      )}
    </Card>
  );
}
