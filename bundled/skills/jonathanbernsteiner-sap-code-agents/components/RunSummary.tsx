"use client";

import GradeBar from "./ui/GradeBar";
import { NOT_AVAILABLE } from "../lib/empty-values";

/**
 * The run's headline, rendered identically on the Overview and inside the
 * Report's snapshot: how many objects were analyzed, how they split by risk,
 * and the two evidence tiers behind that split. One component so the two
 * pages cannot describe the same run in two different shapes — the earlier
 * versions had drifted into a dashboard card and a three-band derivation
 * diagram showing the same numbers.
 *
 * Deliberately compact: the grade bar carries the distribution, the tier
 * tiles carry the evidence, and the recommendation sentence carries the
 * actions — so no separate disposition tiles restating it.
 */
export default function RunSummary({
  totalObjects,
  grades,
  tier1,
  tier2,
  affectedObjects,
  retirementCandidates,
  recommendation,
  onGradeClick,
}: {
  totalObjects: number;
  grades: Record<string, number>;
  tier1: number;
  tier2: number;
  affectedObjects: number;
  /** null when the system has no usage data at all */
  retirementCandidates: number | null;
  recommendation: string | null;
  onGradeClick?: (grade: string) => void;
}) {
  const num = (v: number) => Number(v).toLocaleString("en-US");
  return (
    <>
      <p style={{ fontSize: 12.5, color: "#6E6660", marginTop: 0, marginBottom: 12, lineHeight: 1.55 }}>
        <strong style={{ color: "#1B1817" }}>{num(totalObjects)} objects</strong> analyzed. Each one is
        graded by its worst finding — the bar below is that split — and the grade decides the
        recommended action.
      </p>

      <GradeBar grades={grades} onClick={onGradeClick} detailed />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 12, marginTop: 16 }}>
        <Metric
          label="Tier 1 · machine-verified"
          value={num(tier1)}
          accent
          hint="A rule-specific deterministic validator confirmed the incompatibility on the cited line — a static check over the stored source, not a language model. These break in S/4HANA."
        />
        <Metric
          label="Tier 2 · evidence-linked"
          value={num(tier2)}
          hint="The cited line is real and was located verbatim in the source, but the interpretation still needs an expert to confirm it."
        />
        <Metric
          label="Affected objects"
          value={num(affectedObjects)}
          hint={`Objects carrying at least one Tier-1 or Tier-2 finding, out of ${num(totalObjects)}.`}
        />
        <Metric
          label="Retirement candidates"
          value={retirementCandidates === null ? NOT_AVAILABLE : num(retirementCandidates)}
          hint={
            retirementCandidates === null
              ? "No execution statistics for this system, so dead code cannot be identified."
              : "Zero recorded executions and nothing references them — delete instead of migrating, whatever their grade."
          }
        />
      </div>

      {recommendation && (
        <p style={{ fontSize: 13.5, fontWeight: 600, color: "#1B1817", lineHeight: 1.6, marginTop: 14, marginBottom: 0 }}>
          {recommendation}
        </p>
      )}
    </>
  );
}

function Metric({ label, value, accent, hint }: { label: string; value: string; accent?: boolean; hint?: string }) {
  return (
    <div>
      <div style={{ fontSize: 20, fontWeight: 600, color: accent ? "#CC420B" : "#1B1817" }}>{value}</div>
      <div style={{ fontSize: 12, color: "#6E6660" }}>{label}</div>
      {hint && <div style={{ fontSize: 11, color: "#A49C95", marginTop: 3, lineHeight: 1.45 }}>{hint}</div>}
    </div>
  );
}
