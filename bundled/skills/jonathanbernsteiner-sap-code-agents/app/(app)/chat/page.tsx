"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ArrowUp, Asterisk, Check, ChevronRight, Copy, Wrench } from "lucide-react";
import Markdown from "../../../components/Markdown";
import ChatSidebar, { type SessionInfo } from "../../../components/chat/ChatSidebar";
import { useWorkspace, type WorkspaceInfo } from "../../../components/useWorkspace";

// ---------- message model ----------

type Segment =
  | { type: "text"; text: string }
  | { type: "tool"; name: string; input: Record<string, unknown>; durationMs: number | null; running: boolean };

interface Msg {
  role: "user" | "assistant";
  content: string; // user text, or concatenated assistant text (for copy)
  segments?: Segment[]; // assistant only
}

interface StoredToolCall {
  name: string;
  input: Record<string, unknown>;
  duration_ms: number | null;
  at: number;
}

/** Rebuild inline segments from stored content + tool-call offsets. */
function segmentsFromStored(contentMd: string, toolCalls: StoredToolCall[]): Segment[] {
  const segs: Segment[] = [];
  let pos = 0;
  for (const t of [...toolCalls].sort((a, b) => a.at - b.at)) {
    const at = Math.min(Math.max(t.at, pos), contentMd.length);
    if (at > pos) segs.push({ type: "text", text: contentMd.slice(pos, at) });
    segs.push({ type: "tool", name: t.name, input: t.input, durationMs: t.duration_ms, running: false });
    pos = at;
  }
  if (pos < contentMd.length) segs.push({ type: "text", text: contentMd.slice(pos) });
  return segs;
}

// ---------- per-workspace example chips ----------

function chipsFor(ws: WorkspaceInfo | undefined): string[] {
  if (!ws) return [];
  if (ws.name === "example-manufacturer")
    return [
      "Which objects are safe to retire?",
      "What breaks on S/4HANA?",
      "What does ZCL_GM_MOVEMENT_SERVICE do?",
      "Which programs handle goods movements?",
    ];
  if (ws.name === "abapGit")
    return [
      "What does ZCL_ABAPGIT_PERSISTENCE_DB do?",
      "Which objects access the database directly?",
      "What breaks on S/4HANA?",
    ];
  return ["What are the largest objects?", "What breaks on S/4HANA?", "Show me the dependency hotspots"];
}

// ---------- tool-call row (inline, collapsible) ----------

function shortArgs(input: Record<string, unknown>): string {
  return Object.values(input)
    .map((v) => String(v))
    .join(", ")
    .slice(0, 48);
}

function ToolRow({ seg }: { seg: Extract<Segment, { type: "tool" }> }) {
  const [open, setOpen] = useState(false);
  return (
    <div style={{ margin: "6px 0" }}>
      <button
        onClick={() => setOpen((o) => !o)}
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 6,
          fontSize: 11,
          fontFamily: "JetBrains Mono, monospace",
          color: "#6E6660",
          backgroundColor: "#FAF8F5",
          border: "1px solid #E8E2DB",
          borderRadius: 6,
          padding: "3px 8px",
          cursor: "pointer",
          maxWidth: "100%",
        }}
      >
        <ChevronRight
          size={11}
          style={{ flexShrink: 0, transform: open ? "rotate(90deg)" : "none", transition: "transform 120ms ease" }}
        />
        <Wrench size={11} style={{ flexShrink: 0, color: seg.running ? "#F04E0D" : "#A49C95" }} />
        <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {seg.name}({shortArgs(seg.input)})
        </span>
        <span style={{ color: "#A49C95", flexShrink: 0 }}>
          {seg.running ? "running…" : seg.durationMs != null ? `${(seg.durationMs / 1000).toFixed(1)}s` : ""}
        </span>
      </button>
      {open && (
        <pre
          style={{
            margin: "4px 0 0",
            padding: "8px 10px",
            fontSize: 11,
            fontFamily: "JetBrains Mono, monospace",
            color: "#1B1817",
            backgroundColor: "#FAF8F5",
            border: "1px solid #E8E2DB",
            borderRadius: 6,
            overflowX: "auto",
          }}
        >
          {JSON.stringify(seg.input, null, 2)}
        </pre>
      )}
    </div>
  );
}

// ---------- streaming activity line ----------

/** Human label for what the agent is doing right now. */
function activityLabel(m: Msg | undefined): string {
  const segs = m?.segments ?? [];
  for (let i = segs.length - 1; i >= 0; i--) {
    const s = segs[i];
    if (s.type === "tool" && s.running) {
      const name = typeof s.input.name === "string" ? s.input.name : "";
      switch (s.name) {
        case "search_objects":
          return "Searching the codebase";
        case "read_object":
          return name ? `Reading ${name}` : "Reading source";
        case "where_used":
          return name ? `Tracing usages of ${name}` : "Tracing usages";
        case "get_usage_stats":
          return "Checking usage statistics";
        default:
          return `Running ${s.name}`;
      }
    }
  }
  return m?.content.trim() ? "Answering" : "Thinking";
}

function ActivityLine({ label }: { label: string }) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 7,
        margin: "10px 0 2px",
        fontSize: 13,
        color: "#6E6660",
      }}
    >
      <Asterisk size={15} strokeWidth={2.4} className="chat-activity-star" style={{ color: "#F04E0D", flexShrink: 0 }} />
      <span>{label}</span>
      <span style={{ display: "inline-flex", gap: 2, marginLeft: -2 }}>
        <span className="chat-activity-dot">·</span>
        <span className="chat-activity-dot">·</span>
        <span className="chat-activity-dot">·</span>
      </span>
    </div>
  );
}

// ---------- copy button ----------

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={() => {
        navigator.clipboard.writeText(text).then(() => {
          setCopied(true);
          setTimeout(() => setCopied(false), 1500);
        });
      }}
      aria-label="Copy message"
      title="Copy"
      className="opacity-0 group-hover:opacity-100"
      style={{
        border: "none",
        background: "none",
        cursor: "pointer",
        padding: 4,
        color: copied ? "#F04E0D" : "#A49C95",
        transition: "opacity 120ms ease",
      }}
    >
      {copied ? <Check size={13} /> : <Copy size={13} />}
    </button>
  );
}

// ---------- page ----------

export default function ChatPage() {
  const { workspaces, selected, setSelected, current } = useWorkspace();
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  // Colleagues' chats are read-only: the composer locks for sessions that
  // aren't the current user's ("All company chats" view).
  const [activeIsMine, setActiveIsMine] = useState(true);
  const [scope, setScope] = useState<"mine" | "company">("mine");
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const deepLinkConsumed = useRef(false);
  const sessionsFetchSeq = useRef(0);

  const setSessionUrl = (id: string | null) => {
    const url = id ? `/chat?session=${id}` : "/chat";
    window.history.replaceState(null, "", url);
  };

  const loadSessions = useCallback((workspace: string, listScope: "mine" | "company") => {
    // Guard against a slow response for a previously selected workspace
    // overwriting the current one's history.
    const seq = ++sessionsFetchSeq.current;
    fetch(`/api/chat/sessions?workspace=${encodeURIComponent(workspace)}&scope=${listScope}`)
      .then((r) => r.json())
      .then((d) => {
        if (seq === sessionsFetchSeq.current) setSessions(d.sessions ?? []);
      })
      .catch(() => {
        if (seq === sessionsFetchSeq.current) setSessions([]);
      });
  }, []);

  const openSession = useCallback(
    async (id: string) => {
      try {
        const res = await fetch(`/api/chat/sessions/${id}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const d = await res.json();
        setActiveSessionId(id);
        setActiveIsMine(d.session?.is_mine !== false);
        setSessionUrl(id);
        setMessages(
          (d.messages ?? []).map(
            (m: { role: "user" | "assistant"; content_md: string; tool_calls: StoredToolCall[] }): Msg =>
              m.role === "user"
                ? { role: "user", content: m.content_md }
                : {
                    role: "assistant",
                    content: m.content_md,
                    segments: segmentsFromStored(m.content_md, m.tool_calls ?? []),
                  }
          )
        );
        // Deep link into a session of another workspace: follow the session.
        if (d.session?.workspace && d.session.workspace !== selected) setSelected(d.session.workspace);
      } catch {
        setActiveSessionId(null);
        setSessionUrl(null);
        setMessages([]);
      }
    },
    [selected, setSelected]
  );

  // Deep link (?session=...) once; runs before the workspace list settles.
  useEffect(() => {
    if (deepLinkConsumed.current) return;
    deepLinkConsumed.current = true;
    const id = new URLSearchParams(window.location.search).get("session");
    if (id) void openSession(id);
  }, [openSession]);

  // Workspace or scope change → reload the matching history.
  useEffect(() => {
    if (!selected) return;
    loadSessions(selected, scope);
  }, [selected, scope, loadSessions]);

  const newChat = () => {
    setActiveSessionId(null);
    setActiveIsMine(true);
    setSessionUrl(null);
    setMessages([]);
  };

  const switchWorkspace = (name: string) => {
    setSelected(name);
    newChat();
  };

  const deleteSession = async (id: string) => {
    setSessions((prev) => prev.filter((s) => s.id !== id));
    if (id === activeSessionId) newChat();
    await fetch(`/api/chat/sessions/${id}`, { method: "DELETE" }).catch(() => {});
  };

  async function send(text?: string) {
    const question = (text ?? input).trim();
    if (!question || busy || !selected) return;
    setInput("");
    setBusy(true);
    setMessages((prev) => [
      ...prev,
      { role: "user", content: question },
      { role: "assistant", content: "", segments: [] },
    ]);

    const patchAssistant = (fn: (m: Msg) => Msg) =>
      setMessages((prev) => {
        const next = [...prev];
        next[next.length - 1] = fn({ ...next[next.length - 1] });
        return next;
      });

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ workspace: selected, sessionId: activeSessionId ?? undefined, message: question }),
      });
      if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";
        for (const line of lines) {
          if (!line.trim()) continue;
          const event = JSON.parse(line);

          if (event.type === "session") {
            setActiveSessionId(event.id);
            setSessionUrl(event.id);
            const now = new Date().toISOString();
            setSessions((prev) => {
              const rest = prev.filter((s) => s.id !== event.id);
              const existing = prev.find((s) => s.id === event.id);
              return [{ id: event.id, title: existing?.title ?? event.title, updated_at: now }, ...rest];
            });
          } else if (event.type === "title") {
            setSessions((prev) => prev.map((s) => (s.id === event.id ? { ...s, title: event.title } : s)));
          } else if (event.type === "text") {
            patchAssistant((m) => {
              const segs = [...(m.segments ?? [])];
              const last = segs[segs.length - 1];
              if (last?.type === "text") segs[segs.length - 1] = { type: "text", text: last.text + event.delta };
              else segs.push({ type: "text", text: event.delta });
              return { ...m, content: m.content + event.delta, segments: segs };
            });
          } else if (event.type === "tool_use") {
            patchAssistant((m) => ({
              ...m,
              segments: [
                ...(m.segments ?? []),
                { type: "tool", name: event.name, input: event.input, durationMs: null, running: true },
              ],
            }));
          } else if (event.type === "tool_result") {
            patchAssistant((m) => {
              const segs = [...(m.segments ?? [])];
              for (let i = segs.length - 1; i >= 0; i--) {
                const s = segs[i];
                if (s.type === "tool" && s.running && s.name === event.name) {
                  segs[i] = { ...s, running: false, durationMs: event.duration_ms ?? null };
                  break;
                }
              }
              return { ...m, segments: segs };
            });
          } else if (event.type === "error") {
            patchAssistant((m) => ({
              ...m,
              content: m.content + `\n\n**Error:** ${event.message}`,
              segments: [...(m.segments ?? []), { type: "text", text: `\n\n**Error:** ${event.message}` }],
            }));
          }
        }
        scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
      }
    } catch (e) {
      patchAssistant((m) => ({
        ...m,
        content: `**Error:** ${(e as Error).message}`,
        segments: [{ type: "text", text: `**Error:** ${(e as Error).message}` }],
      }));
    } finally {
      setBusy(false);
    }
  }

  const chips = chipsFor(current);
  const isEmpty = messages.length === 0;

  const composer = (
    <div style={{ width: "100%" }}>
      {!activeIsMine && (
        <div
          style={{
            fontSize: 12,
            color: "#6E6660",
            backgroundColor: "#F3EFEA",
            border: "1px solid #E8E2DB",
            borderRadius: 10,
            padding: "8px 12px",
            marginBottom: 8,
            textAlign: "center",
          }}
        >
          A colleague&apos;s conversation — read-only. Start your own chat to continue the topic.
        </div>
      )}
      <div
        className="chat-composer"
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          padding: "8px 8px 8px 18px",
          borderRadius: 26,
          border: "1px solid #E8E2DB",
          backgroundColor: "#FFFFFF",
          boxShadow: "0 2px 12px rgba(23,20,18,0.06)",
        }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          autoFocus
          placeholder={
            !activeIsMine
              ? "Read-only — this is a colleague's conversation"
              : busy
                ? "Working…"
                : "Ask about this system's ABAP code…"
          }
          disabled={busy || !activeIsMine}
          style={{
            flex: 1,
            fontSize: 14,
            padding: "8px 0",
            border: "none",
            backgroundColor: "transparent",
            color: "#1B1817",
            outline: "none",
            fontFamily: "inherit",
          }}
        />
        <button
          onClick={() => send()}
          disabled={busy || !input.trim() || !activeIsMine}
          aria-label="Send message"
          title="Send"
          style={{
            width: 36,
            height: 36,
            flexShrink: 0,
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            borderRadius: 999,
            border: "none",
            cursor: busy || !input.trim() ? "default" : "pointer",
            backgroundColor: busy || !input.trim() ? "#E8E2DB" : "#F04E0D",
            color: busy || !input.trim() ? "#A49C95" : "#FFFFFF",
            transition: "background-color 150ms ease",
          }}
        >
          <ArrowUp size={17} strokeWidth={2.4} />
        </button>
      </div>
    </div>
  );

  return (
    <div style={{ display: "flex", height: "calc(100vh - 56px)" }}>
      <ChatSidebar
        workspaces={workspaces}
        selected={selected}
        onSelectWorkspace={switchWorkspace}
        sessions={sessions}
        activeSessionId={activeSessionId}
        scope={scope}
        onScopeChange={setScope}
        onNewChat={newChat}
        onOpenSession={openSession}
        onDeleteSession={deleteSession}
      />

      {/* Centered conversation column */}
      <div style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column" }}>
        <div ref={scrollRef} style={{ flex: 1, overflowY: "auto" }}>
          <div style={{ maxWidth: 760, margin: "0 auto", padding: "24px 24px 12px" }}>
            {isEmpty ? (
              <div
                style={{
                  paddingTop: "16vh",
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                }}
              >
                <h1
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    fontSize: 26,
                    fontWeight: 600,
                    letterSpacing: "-0.01em",
                    color: "#1B1817",
                    margin: 0,
                  }}
                >
                  <Asterisk size={26} strokeWidth={2.6} style={{ color: "#F04E0D" }} />
                  What do you want to know?
                </h1>
                <p style={{ fontSize: 13, color: "#A49C95", margin: "10px 0 28px", textAlign: "center" }}>
                  Answers come only from retrieved evidence; unresolved references are marked.
                </p>
                <div style={{ width: "100%", maxWidth: 640 }}>{composer}</div>
                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: 8,
                    justifyContent: "center",
                    marginTop: 20,
                    maxWidth: 640,
                  }}
                >
                  {chips.map((c) => (
                    <button
                      key={c}
                      className="chat-chip"
                      onClick={() => send(c)}
                      disabled={busy || !selected}
                      style={{
                        fontSize: 13,
                        color: "#6E6660",
                        backgroundColor: "#FFFFFF",
                        border: "1px solid #E8E2DB",
                        borderRadius: 999,
                        padding: "8px 14px",
                        cursor: "pointer",
                        fontFamily: "inherit",
                      }}
                    >
                      {c}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
                {messages.map((m, i) =>
                  m.role === "user" ? (
                    <div key={i} className="group" style={{ alignSelf: "flex-end", maxWidth: "80%", display: "flex", alignItems: "flex-start", gap: 2 }}>
                      <CopyButton text={m.content} />
                      <div
                        style={{
                          backgroundColor: "#171412",
                          color: "#FFF",
                          borderRadius: 14,
                          padding: "10px 14px",
                          fontSize: 14,
                          whiteSpace: "pre-wrap",
                        }}
                      >
                        {m.content}
                      </div>
                    </div>
                  ) : (
                    <div key={i} className="group" style={{ alignSelf: "stretch" }}>
                      {(m.segments ?? []).map((seg, j) =>
                        seg.type === "tool" ? (
                          <ToolRow key={j} seg={seg} />
                        ) : (
                          <Markdown key={j}>{seg.text}</Markdown>
                        )
                      )}
                      {busy && i === messages.length - 1 && <ActivityLine label={activityLabel(m)} />}
                      {!(busy && i === messages.length - 1) && m.content && (
                        <div style={{ marginTop: 2 }}>
                          <CopyButton text={m.content} />
                        </div>
                      )}
                    </div>
                  )
                )}
              </div>
            )}
          </div>
        </div>

        {/* Composer — centered mid-screen on the empty state (rendered above),
            docked at the bottom once a conversation exists.
            Read-only for colleagues' sessions (company chats view). */}
        {!isEmpty && (
          <div style={{ maxWidth: 760, width: "100%", margin: "0 auto", padding: "8px 24px 20px" }}>
            {composer}
          </div>
        )}
      </div>
    </div>
  );
}
