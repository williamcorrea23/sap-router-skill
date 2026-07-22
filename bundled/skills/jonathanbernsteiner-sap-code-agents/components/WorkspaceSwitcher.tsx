"use client";

/**
 * Workspace switcher — the workspace name in the /w header is the trigger.
 * Panel lists every visible workspace (example workspaces badged) and ends
 * with "Manage connections →". Follows the custom-dropdown pattern of
 * components/ui/Select.tsx (panel below trigger, no native select).
 */
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Check, ChevronDown } from "lucide-react";
import type { WorkspaceInfo } from "./useWorkspace";

export default function WorkspaceSwitcher({
  current,
  workspaces,
  onSelect,
}: {
  current: string;
  workspaces: WorkspaceInfo[];
  onSelect: (name: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const boxRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onDown = (e: MouseEvent) => {
      if (boxRef.current && !boxRef.current.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("mousedown", onDown);
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("mousedown", onDown);
      window.removeEventListener("keydown", onKey);
    };
  }, []);

  return (
    <div ref={boxRef} style={{ position: "relative", display: "block", width: "100%" }}>
      {/* select-style trigger — fills its container (the 240px system rail) */}
      <button
        onClick={() => setOpen((o) => !o)}
        aria-haspopup="listbox"
        aria-expanded={open}
        style={{
          display: "flex", alignItems: "center", justifyContent: "space-between", gap: 6, width: "100%",
          fontSize: 13, fontWeight: 600, color: "#1B1817",
          fontFamily: "JetBrains Mono, monospace",
          backgroundColor: "#FFFFFF", border: `1px solid ${open ? "#F04E0D" : "#E8E2DB"}`,
          padding: "8px 10px", borderRadius: 8, cursor: "pointer",
          transition: "border-color 120ms ease",
        }}
      >
        <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{current}</span>
        <ChevronDown size={15} style={{ color: "#A49C95", flexShrink: 0, transform: open ? "rotate(180deg)" : "none", transition: "transform 120ms ease" }} />
      </button>

      {open && (
        <div
          role="listbox"
          style={{
            position: "absolute", top: "calc(100% + 6px)", left: 0, right: 0, zIndex: 60,
            backgroundColor: "#FFFFFF", border: "1px solid #E8E2DB", borderRadius: 10,
            boxShadow: "0 8px 24px rgba(23,20,18,0.12)", overflow: "hidden", padding: "6px 0",
          }}
        >
          {workspaces.map((w) => {
            const active = w.name === current;
            return (
              <button
                key={w.name}
                role="option"
                aria-selected={active}
                onClick={() => {
                  setOpen(false);
                  if (!active) onSelect(w.name);
                }}
                onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#FCEDE4")}
                onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "transparent")}
                style={{
                  display: "flex", alignItems: "center", gap: 8, width: "100%",
                  padding: "8px 14px", background: "none", border: "none",
                  cursor: "pointer", fontFamily: "inherit", textAlign: "left",
                }}
              >
                <span style={{ width: 16, display: "inline-flex", flexShrink: 0 }}>
                  {active && <Check size={15} style={{ color: "#F04E0D" }} />}
                </span>
                <span style={{ fontSize: 13, fontWeight: 600, color: "#1B1817", fontFamily: "JetBrains Mono, monospace", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {w.name}
                </span>
                {w.kind === "example" && (
                  <span style={{ marginLeft: "auto", fontSize: 10, fontWeight: 600, color: "#CC420B", backgroundColor: "#FCEDE4", borderRadius: 5, padding: "1px 6px", flexShrink: 0 }}>
                    EXAMPLE
                  </span>
                )}
              </button>
            );
          })}
          <div style={{ borderTop: "1px solid #E8E2DB", margin: "6px 0 0" }}>
            <Link
              href="/connections/systems"
              onClick={() => setOpen(false)}
              style={{ display: "block", padding: "9px 14px 5px", fontSize: 12.5, fontWeight: 600, color: "#CC420B", textDecoration: "none" }}
            >
              Manage connections →
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
