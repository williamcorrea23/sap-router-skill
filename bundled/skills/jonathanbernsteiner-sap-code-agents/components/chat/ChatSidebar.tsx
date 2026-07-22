"use client";

import { useState } from "react";
import { Check, Plus, Trash2, X } from "lucide-react";
import WorkspaceSwitcher from "../WorkspaceSwitcher";
import type { WorkspaceInfo } from "../useWorkspace";

export interface SessionInfo {
  id: string;
  title: string;
  updated_at: string;
  /** False for colleagues' sessions ("All company chats" view). */
  is_mine?: boolean;
  creator_name?: string;
}

/** "2m ago" / "3h ago" / "5d ago" — coarse on purpose. */
export function relativeTime(iso: string): string {
  const ms = Date.now() - new Date(iso).getTime();
  const min = Math.floor(ms / 60_000);
  if (min < 1) return "just now";
  if (min < 60) return `${min}m ago`;
  const h = Math.floor(min / 60);
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  if (d < 30) return `${d}d ago`;
  return new Date(iso).toLocaleDateString();
}

/** Button twin of SectionSidebar's SidebarItem — identical look, but an
 *  action/selection instead of a route link. */
function RailButton({
  icon,
  label,
  active,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  const [hovered, setHovered] = useState(false);
  const showWhiteBg = active || hovered;
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 10,
        padding: "10px 16px",
        fontSize: 14,
        fontWeight: active ? 600 : 400,
        color: active ? "#1B1817" : "#6E6660",
        background: showWhiteBg ? "#FFFFFF" : "transparent",
        border: "none",
        borderLeft: active ? "2px solid #F04E0D" : "2px solid transparent",
        borderRadius: "0 6px 6px 0",
        cursor: "pointer",
        textAlign: "left",
        width: "100%",
        boxShadow: active ? "0 1px 2px rgba(0,0,0,0.04)" : "none",
        transition: "background 0.15s, color 0.15s",
        fontFamily: "inherit",
      }}
    >
      {icon}
      {label}
    </button>
  );
}

// The chat rail mirrors the workspace area's second-level rail exactly
// (SectionSidebar pattern): SYSTEM heading + shared WorkspaceSwitcher on
// top, then New chat / scope selection as rail items, then the history.
export default function ChatSidebar({
  workspaces,
  selected,
  onSelectWorkspace,
  sessions,
  activeSessionId,
  scope,
  onScopeChange,
  onNewChat,
  onOpenSession,
  onDeleteSession,
}: {
  workspaces: WorkspaceInfo[];
  selected: string;
  onSelectWorkspace: (name: string) => void;
  sessions: SessionInfo[];
  activeSessionId: string | null;
  scope: "mine" | "company";
  onScopeChange: (scope: "mine" | "company") => void;
  onNewChat: () => void;
  onOpenSession: (id: string) => void;
  onDeleteSession: (id: string) => void;
}) {
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);

  return (
    <nav
      className="shrink-0"
      style={{
        width: 240,
        display: "flex",
        flexDirection: "column",
        borderRight: "1px solid #E8E2DB",
        backgroundColor: "#F6F4F1",
      }}
      aria-label="Chat sections"
    >
      <div style={{ padding: "20px 16px 8px 16px", fontSize: 12, fontWeight: 600, color: "#A49C95", letterSpacing: 1, textTransform: "uppercase" }}>
        System
      </div>
      <div style={{ padding: "0 16px 14px" }}>
        <WorkspaceSwitcher current={selected || "…"} workspaces={workspaces} onSelect={onSelectWorkspace} />
      </div>

      <div className="flex flex-col gap-0.5 px-2 pt-1" style={{ borderTop: "1px solid #E8E2DB", paddingTop: 10 }}>
        <RailButton icon={<Plus size={16} />} label="New chat" active={false} onClick={onNewChat} />
      </div>

      <div style={{ padding: "16px 16px 6px", fontSize: 12, fontWeight: 600, color: "#A49C95", letterSpacing: 1, textTransform: "uppercase" }}>
        History
      </div>
      {/* Scope is a filter on the history list, not navigation — a quiet
          segmented toggle, so the rail's active card keeps meaning "you are
          here". */}
      <div
        role="tablist"
        aria-label="Chat history scope"
        style={{
          display: "flex",
          gap: 2,
          margin: "0 16px 8px",
          padding: 2,
          borderRadius: 8,
          backgroundColor: "#ECE7E1",
        }}
      >
        {(
          [
            ["mine", "My chats"],
            ["company", "Company chats"],
          ] as const
        ).map(([value, label]) => {
          const active = scope === value;
          return (
            <button
              key={value}
              role="tab"
              aria-selected={active}
              onClick={() => onScopeChange(value)}
              style={{
                flex: 1,
                fontSize: 12,
                fontWeight: active ? 600 : 400,
                whiteSpace: "nowrap",
                padding: "5px 6px",
                borderRadius: 6,
                border: "none",
                cursor: "pointer",
                fontFamily: "inherit",
                backgroundColor: active ? "#FFFFFF" : "transparent",
                color: active ? "#1B1817" : "#6E6660",
                boxShadow: active ? "0 1px 2px rgba(0,0,0,0.06)" : "none",
                transition: "background 0.15s, color 0.15s",
              }}
            >
              {label}
            </button>
          );
        })}
      </div>
      <div style={{ flex: 1, overflowY: "auto", padding: "0 8px 12px" }}>
        {sessions.length === 0 && (
          <div style={{ fontSize: 12, color: "#A49C95", padding: "4px 8px" }}>
            {scope === "mine"
              ? "No conversations of yours yet in this system."
              : "No company conversations yet in this system."}
          </div>
        )}
        {sessions.map((s) => {
          const active = s.id === activeSessionId;
          const confirming = confirmDelete === s.id;
          return (
            <div
              key={s.id}
              className="group"
              style={{
                display: "flex",
                alignItems: "center",
                gap: 4,
                background: active ? "#FFFFFF" : "transparent",
                borderLeft: active ? "2px solid #F04E0D" : "2px solid transparent",
                borderRadius: "0 6px 6px 0",
                boxShadow: active ? "0 1px 2px rgba(0,0,0,0.04)" : "none",
                marginBottom: 2,
              }}
            >
              <button
                onClick={() => onOpenSession(s.id)}
                style={{
                  flex: 1,
                  minWidth: 0,
                  padding: "7px 8px 7px 14px",
                  border: "none",
                  backgroundColor: "transparent",
                  cursor: "pointer",
                  fontFamily: "inherit",
                  textAlign: "left",
                }}
              >
                <div
                  style={{
                    fontSize: 13,
                    fontWeight: active ? 600 : 400,
                    color: active ? "#1B1817" : "#6E6660",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {s.title}
                </div>
                <div style={{ fontSize: 11, color: "#A49C95" }}>
                  {scope === "company" && s.is_mine === false && s.creator_name
                    ? `${s.creator_name} · `
                    : ""}
                  {relativeTime(s.updated_at)}
                </div>
              </button>
              {s.is_mine === false ? null : confirming ? (
                <span style={{ display: "flex", gap: 2, paddingRight: 6, flexShrink: 0 }}>
                  <button
                    onClick={() => {
                      setConfirmDelete(null);
                      onDeleteSession(s.id);
                    }}
                    aria-label="Confirm delete"
                    title="Delete conversation"
                    style={{ border: "none", background: "none", cursor: "pointer", padding: 4, color: "#CC420B" }}
                  >
                    <Check size={14} />
                  </button>
                  <button
                    onClick={() => setConfirmDelete(null)}
                    aria-label="Cancel delete"
                    style={{ border: "none", background: "none", cursor: "pointer", padding: 4, color: "#6E6660" }}
                  >
                    <X size={14} />
                  </button>
                </span>
              ) : (
                <button
                  onClick={() => setConfirmDelete(s.id)}
                  aria-label={`Delete "${s.title}"`}
                  title="Delete conversation"
                  className="opacity-0 group-hover:opacity-100"
                  style={{
                    border: "none",
                    background: "none",
                    cursor: "pointer",
                    padding: "4px 8px 4px 4px",
                    color: "#A49C95",
                    flexShrink: 0,
                    transition: "opacity 120ms ease",
                  }}
                >
                  <Trash2 size={14} />
                </button>
              )}
            </div>
          );
        })}
      </div>
    </nav>
  );
}
