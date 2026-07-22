"use client";

/**
 * Workspace area (/w/[id]/…) — [id] is the workspace name (globally unique,
 * URL-safe slug). Second-level rail on the left (same pattern as Settings):
 * system switcher + provenance on top, then the Overview | Objects | Report
 * sections; each section is its own route, so every one is deep-linkable.
 * The content pane owns the full remaining width.
 */
import { useEffect } from "react";
import Link from "next/link";
import { useParams, usePathname, useRouter } from "next/navigation";
import { Boxes, FileText, LayoutDashboard } from "lucide-react";
import WorkspaceSwitcher from "../../../../components/WorkspaceSwitcher";
import { SidebarItem } from "../../../../components/layout/SectionSidebar";
import { useWorkspace } from "../../../../components/useWorkspace";

const TABS = [
  { key: "overview", label: "Overview", icon: <LayoutDashboard size={16} /> },
  { key: "objects", label: "Objects", icon: <Boxes size={16} /> },
  { key: "report", label: "Report", icon: <FileText size={16} /> },
] as const;

export default function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  const params = useParams<{ id: string }>();
  const pathname = usePathname();
  const router = useRouter();
  const name = decodeURIComponent(params.id);
  const { workspaces, current, setSelected } = useWorkspace();

  // Keep the global selection (chat scope, top-bar search) in sync with the
  // workspace being viewed, and persist it per user — the app root ("/")
  // routes back to the last-used workspace.
  useEffect(() => {
    if (!name) return;
    setSelected(name);
    fetch("/api/profile/last-workspace", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ workspace: name }),
    }).catch(() => {});
    // setSelected is stable in behavior (localStorage + state); depending on
    // it would re-run on every render of the hook.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [name]);

  // Remember the last-opened tab per workspace — /w/<name> (and the smart
  // landing on "/") resolve back to it.
  const activeTab = pathname?.split("/")[3];
  useEffect(() => {
    if (name && activeTab && TABS.some((t) => t.key === activeTab)) {
      localStorage.setItem(`ws-tab:${name}`, activeTab);
    }
  }, [name, activeTab]);

  const loaded = workspaces.length > 0;
  const info = workspaces.find((w) => w.name === name) ?? (current?.name === name ? current : undefined);
  const notFound = loaded && !info;

  return (
    // Rail + content pane; the pane scrolls on its own so the rail stays
    // fixed (the Objects section relies on the bounded height).
    <div data-print-frame style={{ display: "flex", height: "calc(100vh - 56px)", overflow: "hidden", backgroundColor: "#F6F4F1" }}>
      {/* Second-level rail — Settings' SectionSidebar pattern with the
          system identity block on top. No overflow clipping: the switcher
          dropdown (280px) extends past the 240px rail. */}
      <nav
        className="shrink-0 print:hidden"
        style={{ width: 240, borderRight: "1px solid #E8E2DB", backgroundColor: "#F6F4F1" }}
        aria-label="System sections"
      >
        <div style={{ padding: "20px 16px 8px 16px", fontSize: 12, fontWeight: 600, color: "#A49C95", letterSpacing: 1, textTransform: "uppercase" }}>
          System
        </div>
        <div style={{ padding: "0 16px 14px" }}>
          {/* System switcher — compact select-style control that fills the
              rail width; badges/provenance live on Connections, not here */}
          <WorkspaceSwitcher
            current={name}
            workspaces={workspaces}
            onSelect={(target) => {
              const tab = activeTab && TABS.some((t) => t.key === activeTab) ? activeTab : "overview";
              router.push(`/w/${encodeURIComponent(target)}/${tab}`);
            }}
          />
        </div>
        <div className="flex flex-col gap-0.5 px-2 pt-1" style={{ borderTop: "1px solid #E8E2DB", paddingTop: 10 }}>
          {TABS.map((t) => {
            const href = `/w/${encodeURIComponent(name)}/${t.key}`;
            const active = pathname === href || !!pathname?.startsWith(href + "/");
            return <SidebarItem key={t.key} item={{ key: t.key, label: t.label, path: href, icon: t.icon }} active={active} />;
          })}
        </div>
      </nav>

      <div data-print-pane style={{ flex: 1, minWidth: 0, overflowY: "auto" }}>
        {notFound ? (
          <div style={{ padding: 24 }}>
            <p style={{ fontSize: 14, color: "#6E6660" }}>
              System <span style={{ fontFamily: "JetBrains Mono, monospace" }}>{name}</span> was not found
              (or is not visible to your company).{" "}
              <Link href="/connections/systems" style={{ color: "#CC420B", fontWeight: 600 }}>
                Go to connections
              </Link>
            </p>
          </div>
        ) : (
          children
        )}
      </div>
    </div>
  );
}
