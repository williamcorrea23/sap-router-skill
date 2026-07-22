"use client";

import { GRADE_COLORS, GRADE_MEANINGS } from "./GradeBadge";

export const GRADE_ORDER = ["A", "B", "C", "D", "Ungraded"] as const;

/**
 * Horizontal stacked bar of the grade distribution. Sequential orange ramp
 * (light → dark = rising risk), 2px surface gaps between segments; the legend
 * below carries letter + count so identity is never color-alone. Used by the
 * workspace Overview tab and the report's Run Snapshot.
 */
export default function GradeBar({
  grades,
  onClick,
  compact,
  detailed,
}: {
  grades: Record<string, number>;
  onClick?: (g: string) => void;
  /** thin bar without the legend — for list rows (tooltips carry the counts) */
  compact?: boolean;
  /** per-grade tiles with large counts and plain-language meanings instead of the inline legend */
  detailed?: boolean;
}) {
  const total = GRADE_ORDER.reduce((a, g) => a + (grades[g] ?? 0), 0);
  if (total === 0) return <p style={{ fontSize: 13, color: "#6E6660" }}>No objects.</p>;
  const interactive = !!onClick;
  return (
    <>
      <div style={{ display: "flex", gap: 2, height: compact ? 10 : 28, borderRadius: compact ? 5 : 6, overflow: "hidden" }}>
        {GRADE_ORDER.filter((g) => (grades[g] ?? 0) > 0).map((g) => (
          <button
            key={g}
            onClick={() => onClick?.(g)}
            title={`${g} · ${GRADE_MEANINGS[g].name}: ${grades[g].toLocaleString("en-US")} objects — ${GRADE_MEANINGS[g].description}${interactive ? " Click to show in list." : ""}`}
            style={{
              flexGrow: grades[g],
              flexBasis: 0,
              minWidth: 14,
              border: "none",
              cursor: interactive ? "pointer" : "default",
              backgroundColor: GRADE_COLORS[g].bg,
              padding: 0,
            }}
          />
        ))}
      </div>
      {compact ? null : detailed ? (
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 10, marginTop: 14 }}>
        {GRADE_ORDER.map((g) => (
          <button
            key={g}
            onClick={() => onClick?.(g)}
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 4,
              textAlign: "left",
              background: "#FAF8F6",
              border: "1px solid #EDE8E3",
              borderRadius: 10,
              padding: "10px 12px",
              cursor: interactive ? "pointer" : "default",
              fontFamily: "inherit",
              opacity: (grades[g] ?? 0) === 0 ? 0.55 : 1,
            }}
          >
            <span style={{ display: "inline-flex", alignItems: "center", gap: 7, fontSize: 12, fontWeight: 600, color: "#6E6660" }}>
              <span style={{ width: 11, height: 11, borderRadius: 3, backgroundColor: GRADE_COLORS[g].bg, flexShrink: 0 }} />
              {g === "Ungraded" ? "Ungraded" : `${g} · ${GRADE_MEANINGS[g].name}`}
            </span>
            <span style={{ fontSize: 24, fontWeight: 600, color: "#1B1817", lineHeight: 1.1 }}>
              {(grades[g] ?? 0).toLocaleString("en-US")}
            </span>
            <span style={{ fontSize: 11.5, color: "#8A8178", lineHeight: 1.45 }}>{GRADE_MEANINGS[g].description}</span>
          </button>
        ))}
      </div>
      ) : (
      <div style={{ display: "flex", gap: 14, marginTop: 10, flexWrap: "wrap" }}>
        {GRADE_ORDER.map((g) => (
          <button
            key={g}
            onClick={() => onClick?.(g)}
            title={GRADE_MEANINGS[g].description}
            style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 12, color: "#6E6660", background: "none", border: "none", cursor: interactive ? "pointer" : "default", padding: 0, fontFamily: "inherit" }}
          >
            <span style={{ width: 10, height: 10, borderRadius: 3, backgroundColor: GRADE_COLORS[g].bg }} />
            {g === "Ungraded" ? "Ungraded" : g} · {(grades[g] ?? 0).toLocaleString("en-US")}
          </button>
        ))}
      </div>
      )}
    </>
  );
}
