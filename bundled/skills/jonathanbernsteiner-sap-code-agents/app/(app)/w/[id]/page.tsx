"use client";

/**
 * /w/<name> — resolves to the workspace's last-opened tab (recorded by the
 * layout in localStorage), falling back to Overview. Client-side because the
 * memory lives in the browser.
 */
import { useEffect } from "react";
import { useParams, useRouter } from "next/navigation";

const TABS = ["overview", "objects", "report"];

export default function WorkspaceIndex() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const name = decodeURIComponent(params.id);

  useEffect(() => {
    const stored = localStorage.getItem(`ws-tab:${name}`);
    const tab = stored && TABS.includes(stored) ? stored : "overview";
    router.replace(`/w/${encodeURIComponent(name)}/${tab}`);
  }, [name, router]);

  return null; // the workspace layout already renders the header + tabs
}
