"use client";

/**
 * Migration Risk Grade badge (Change Order 04). Grades are computed by the
 * object_risk_grades SQL view from the latest finished report run — this
 * component only renders them. Sequential orange ramp (light = low risk),
 * CVD-validated; identity is never color-alone (the letter is the label).
 */

import { GRADE_COLORS, GRADE_MEANINGS, GRADE_SCALE_EXPLANATION } from "../../lib/grade-scale";

export type Grade = "A" | "B" | "C" | "D" | null;

// Palette + meanings live in lib/grade-scale.ts (shared with the PDF
// renderer); re-exported here so existing UI imports keep working.
export { GRADE_COLORS, GRADE_MEANINGS, GRADE_SCALE_EXPLANATION };

export default function GradeBadge({ grade, size = 18 }: { grade: Grade; size?: number }) {
  const c = GRADE_COLORS[grade ?? "Ungraded"];
  return (
    <span
      title={GRADE_SCALE_EXPLANATION}
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        width: size,
        height: size,
        borderRadius: 6,
        fontSize: size * 0.62,
        fontWeight: 700,
        color: grade ? c.text : "#6E6660",
        backgroundColor: c.bg,
        cursor: "help",
        flexShrink: 0,
      }}
    >
      {grade ?? "–"}
    </span>
  );
}
