"use client";

/**
 * App root — routes to the user's last-used workspace (persisted per user on
 * the profile; recorded by the /w layout, cleared automatically when the
 * workspace is deleted). Without one: Connections, where sources are set up.
 * /w/<name> itself then resolves to the workspace's last-opened tab.
 */
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    let cancelled = false;
    fetch("/api/profile")
      .then((r) => r.json())
      .then((d) => {
        if (cancelled) return;
        if (d.last_workspace) router.replace(`/w/${encodeURIComponent(d.last_workspace)}`);
        else router.replace("/connections");
      })
      .catch(() => {
        if (!cancelled) router.replace("/connections");
      });
    return () => {
      cancelled = true;
    };
  }, [router]);

  return (
    <div style={{ padding: 24 }}>
      <p style={{ fontSize: 14, color: "#A49C95" }}>Loading…</p>
    </div>
  );
}
