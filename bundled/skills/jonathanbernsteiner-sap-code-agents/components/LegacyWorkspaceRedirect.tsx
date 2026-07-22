"use client";

/**
 * Workspace-resolving redirect.
 *
 * With a `tab`: serves pre-restructure deep links (/overview, /objects?grade=…,
 * /report) that carry no workspace in the URL — forwards to
 * /w/<stored-workspace>/<tab>, keeping the query string so ?focus/?grade/?area
 * stay alive.
 *
 * Without a `tab`: the smart landing ("/") — forwards to /w/<stored-workspace>,
 * which resolves to that workspace's last-opened tab.
 *
 * The stored selection is validated against the live workspace list; without
 * a (still existing) selection the workspace list is the destination.
 */
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function LegacyWorkspaceRedirect({ tab }: { tab?: "overview" | "objects" | "report" }) {
  const router = useRouter();

  useEffect(() => {
    let cancelled = false;
    const search = window.location.search;
    const stored = localStorage.getItem("workspace");
    fetch("/api/workspaces")
      .then((r) => r.json())
      .then((d) => {
        if (cancelled) return;
        const list: { name: string }[] = d.workspaces ?? [];
        const target =
          stored && list.some((w) => w.name === stored) ? stored : tab ? list[0]?.name : undefined;
        if (target) {
          router.replace(`/w/${encodeURIComponent(target)}${tab ? `/${tab}${search}` : ""}`);
        } else {
          router.replace("/connections");
        }
      })
      .catch(() => {
        if (!cancelled) router.replace("/connections");
      });
    return () => {
      cancelled = true;
    };
  }, [router, tab]);

  return (
    <div style={{ padding: 24 }}>
      <p style={{ fontSize: 14, color: "#A49C95" }}>Redirecting…</p>
    </div>
  );
}
