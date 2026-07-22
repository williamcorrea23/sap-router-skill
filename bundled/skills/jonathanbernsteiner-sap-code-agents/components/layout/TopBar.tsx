"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { Search } from "lucide-react";
import { navItems } from "../../lib/navigation";
import { PRODUCT_NAME } from "../../lib/config";
import { stripMarkdown } from "../Markdown";
import AccountMenu from "./AccountMenu";

interface SearchHit {
  name: string;
  object_type: string;
  summary_snippet: string;
}

export default function TopBar() {
  const pathname = usePathname();
  const router = useRouter();

  // /w/<name>/… routes: the name + switcher + badges live in the workspace
  // header only — the top bar shows the section title ("Workspace"), never
  // the workspace name. routeWorkspace still scopes the object search.
  const routeWorkspace = pathname?.startsWith("/w/")
    ? decodeURIComponent(pathname.split("/")[2] ?? "")
    : null;

  const pageTitle = pathname?.startsWith("/settings")
    ? "Settings"
    : navItems.find(
        (n) => pathname === n.path || pathname?.startsWith(n.path + "/")
      )?.label ?? PRODUCT_NAME;

  // ---- search ----
  const [query, setQuery] = useState("");
  const [hits, setHits] = useState<SearchHit[]>([]);
  const [open, setOpen] = useState(false);
  const [highlight, setHighlight] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const boxRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        inputRef.current?.focus();
      }
      if (e.key === "Escape") {
        setOpen(false);
        inputRef.current?.blur();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (boxRef.current && !boxRef.current.contains(e.target as Node)) setOpen(false);
    };
    window.addEventListener("mousedown", onClick);
    return () => window.removeEventListener("mousedown", onClick);
  }, []);

  useEffect(() => {
    if (!query.trim()) {
      setHits([]);
      return;
    }
    // Scope to the open workspace route; otherwise the stored selection.
    const workspace = routeWorkspace ?? localStorage.getItem("workspace");
    if (!workspace) return;
    const t = setTimeout(() => {
      fetch(`/api/objects?workspace=${encodeURIComponent(workspace)}&q=${encodeURIComponent(query.trim())}`)
        .then((r) => r.json())
        .then((d) => {
          setHits((d.objects ?? []).slice(0, 8));
          setHighlight(0);
        })
        .catch(() => setHits([]));
    }, 150);
    return () => clearTimeout(t);
  }, [query, routeWorkspace]);

  const go = (name: string) => {
    setOpen(false);
    setQuery("");
    const workspace = routeWorkspace ?? localStorage.getItem("workspace");
    if (!workspace) return;
    router.push(`/w/${encodeURIComponent(workspace)}/objects?focus=${encodeURIComponent(name)}`);
  };

  return (
    <header
      style={{
        position: "fixed",
        top: 0,
        left: 56,
        right: 0,
        height: 56,
        zIndex: 50,
        backgroundColor: "#FFFFFF",
        borderBottom: "1px solid #E8E2DB",
        display: "flex",
        alignItems: "center",
        padding: "0 24px",
      }}
    >
      <h1 style={{ fontSize: 18, fontWeight: 600, color: "#1B1817", margin: 0, whiteSpace: "nowrap" }}>
        {pageTitle}
      </h1>

      {/* Search — scoped to the selected workspace, results navigate to Objects */}
      <div
        ref={boxRef}
        style={{
          position: "absolute",
          left: "50%",
          transform: "translateX(-50%)",
          width: 450,
          maxWidth: "calc(100vw - 320px)",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            padding: "6px 12px",
            border: "1px solid #E8E2DB",
            borderRadius: 8,
            backgroundColor: "#FAF8F5",
          }}
        >
          <Search size={14} style={{ color: "#A49C95", flexShrink: 0 }} />
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setOpen(true);
            }}
            onFocus={() => setOpen(true)}
            onKeyDown={(e) => {
              if (e.key === "ArrowDown") {
                e.preventDefault();
                setHighlight((h) => Math.min(h + 1, hits.length - 1));
              }
              if (e.key === "ArrowUp") {
                e.preventDefault();
                setHighlight((h) => Math.max(h - 1, 0));
              }
              if (e.key === "Enter" && hits[highlight]) go(hits[highlight].name);
            }}
            placeholder="Search objects…"
            style={{
              flex: 1,
              fontSize: 13,
              border: "none",
              outline: "none",
              backgroundColor: "transparent",
              color: "#1B1817",
              fontFamily: "inherit",
            }}
          />
          <kbd
            style={{
              fontSize: 11,
              fontWeight: 500,
              color: "#A49C95",
              backgroundColor: "#F3EFEA",
              border: "1px solid #E8E2DB",
              borderRadius: 4,
              padding: "1px 5px",
            }}
          >
            ⌘K
          </kbd>
        </div>

        {open && query.trim() && (
          <div
            style={{
              position: "absolute",
              top: "calc(100% + 6px)",
              left: 0,
              right: 0,
              backgroundColor: "#FFFFFF",
              border: "1px solid #E8E2DB",
              borderRadius: 10,
              boxShadow: "0 8px 24px rgba(23,20,18,0.12)",
              overflow: "hidden",
            }}
          >
            {hits.length === 0 && (
              <div style={{ padding: "10px 14px", fontSize: 13, color: "#A49C95" }}>
                No objects match “{query.trim()}” in this system.
              </div>
            )}
            {hits.map((h, i) => (
              <button
                key={h.name}
                onClick={() => go(h.name)}
                onMouseEnter={() => setHighlight(i)}
                style={{
                  display: "block",
                  width: "100%",
                  textAlign: "left",
                  padding: "8px 14px",
                  border: "none",
                  cursor: "pointer",
                  backgroundColor: i === highlight ? "#FCEDE4" : "#FFFFFF",
                  fontFamily: "inherit",
                }}
              >
                <span style={{ fontSize: 13, fontWeight: 600, fontFamily: "JetBrains Mono, monospace", color: "#1B1817" }}>
                  {h.name}
                </span>
                <span style={{ fontSize: 11, color: "#A49C95", marginLeft: 8 }}>{h.object_type}</span>
                <div
                  style={{
                    fontSize: 12,
                    color: "#6E6660",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {stripMarkdown(h.summary_snippet || "")}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Account — who is signed in, settings links, logout */}
      <AccountMenu />
    </header>
  );
}
