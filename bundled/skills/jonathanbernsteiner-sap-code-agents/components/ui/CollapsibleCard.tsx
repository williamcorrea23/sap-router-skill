"use client";

import { useState } from "react";
import Card from "./Card";

/**
 * A Card whose body folds away behind its own header. One visual language for
 * every foldable section (same caret, weight and hit area), so "collapsed"
 * reads as one concept rather than several bespoke toggles.
 *
 * Folding and the DEFAULT state are separate decisions. Everything below the
 * summary folds, so a reader can put away what they have finished with; only
 * reference material (appendices, operational logs, alternate views of
 * content stated above) starts collapsed. The assessment itself — disposition
 * table, Tier 1, Tier 2 — renders open, so someone opening the report cold
 * still gets the whole story by scrolling. Either way the header has to carry
 * enough (counts, latest state) that a collapsed section loses nothing at a
 * glance.
 */
export default function CollapsibleCard({
  title,
  defaultOpen = false,
  primary,
  accent,
  children,
}: {
  title: React.ReactNode;
  defaultOpen?: boolean;
  /** substantive sections keep heading weight; appendices stay muted */
  primary?: boolean;
  /** debug-only sections mark themselves in the accent colour */
  accent?: boolean;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <Card>
      <button
        onClick={() => setOpen((s) => !s)}
        aria-expanded={open}
        style={{
          display: "block",
          width: "100%",
          textAlign: "left",
          fontSize: 14,
          fontWeight: 600,
          background: "none",
          border: "none",
          cursor: "pointer",
          color: accent ? "#CC420B" : primary ? "#1B1817" : "#6E6660",
          padding: 0,
          fontFamily: "inherit",
        }}
      >
        {open ? "▾" : "▸"} {title}
      </button>
      {open && <div style={{ marginTop: 12 }}>{children}</div>}
    </Card>
  );
}
