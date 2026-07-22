/**
 * Migration Risk Grade scale — single source of truth for the grade palette
 * and plain-language meanings, shared by the UI components (GradeBadge /
 * GradeBar) and the server-side PDF renderer so every surface draws grades
 * identically. Dependency-free on purpose: importable from client components
 * and from pdfkit code alike. Sequential orange ramp (light = low risk),
 * CVD-validated; identity is never color-alone (the letter is the label).
 */

export const GRADE_ORDER = ["A", "B", "C", "D", "Ungraded"] as const;

export const GRADE_COLORS: Record<string, { bg: string; text: string }> = {
  A: { bg: "#F8E2D1", text: "#1B1817" },
  B: { bg: "#F09C63", text: "#1B1817" },
  C: { bg: "#D9560E", text: "#FFFFFF" },
  D: { bg: "#8F2F08", text: "#FFFFFF" },
  Ungraded: { bg: "#D8D2CB", text: "#1B1817" },
};

/** Per-grade plain-language meaning: short name + one-line description. */
export const GRADE_MEANINGS: Record<string, { name: string; description: string }> = {
  A: { name: "Clean", description: "No S/4HANA incompatibilities found." },
  B: { name: "Review", description: "Evidence-linked findings only (Tier 2) — worth a look, not confirmed blockers." },
  C: { name: "Needs fixes", description: "Machine-verified incompatibilities (Tier 1) that must be adapted." },
  // named for the action it implies, matching the object's disposition —
  // one concept must not carry two words across two screens
  D: { name: "Redesign", description: "Uses constructs removed outright in S/4HANA — code must be rewritten." },
  Ungraded: { name: "Ungraded", description: "Not covered by a report run yet." },
};

export const GRADE_SCALE_EXPLANATION =
  "Migration Risk Grade — computed per report run from persisted findings: " +
  ["A", "B", "C", "D", "Ungraded"]
    .map((g) => `${g === "Ungraded" ? "–" : g} = ${GRADE_MEANINGS[g].description.replace(/\.$/, "")}`)
    .join(" · ") +
  ".";
