"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { LogOut, Settings as SettingsIcon } from "lucide-react";
import { supabaseBrowser } from "../../lib/auth/client";
import { clearProfileCache, useProfile } from "../useProfile";

/**
 * Top-bar account control (top-right corner): avatar initials with a flyout
 * showing who is signed in (name, email, company, role) plus the Profile /
 * Company settings / Logout actions.
 */
export default function AccountMenu() {
  const router = useRouter();
  const profile = useProfile();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    window.addEventListener("mousedown", onClick);
    return () => window.removeEventListener("mousedown", onClick);
  }, []);

  const initials =
    profile.name
      .trim()
      .split(/\s+/)
      .map((p) => p[0] ?? "")
      .join("")
      .slice(0, 2)
      .toUpperCase() || (profile.email[0] ?? "•").toUpperCase();

  async function logout() {
    await supabaseBrowser().auth.signOut();
    clearProfileCache();
    router.push("/login");
    router.refresh();
  }

  const itemStyle: React.CSSProperties = {
    display: "flex",
    alignItems: "center",
    gap: 8,
    width: "100%",
    padding: "9px 14px",
    fontSize: 13,
    color: "#1B1817",
    textDecoration: "none",
    border: "none",
    background: "none",
    cursor: "pointer",
    fontFamily: "inherit",
    textAlign: "left",
  };

  return (
    <div ref={ref} style={{ position: "relative", marginLeft: "auto" }}>
      <button
        onClick={() => setOpen((o) => !o)}
        aria-label="Account menu"
        style={{
          width: 34,
          height: 34,
          borderRadius: "50%",
          backgroundColor: "#F04E0D",
          color: "#FFFFFF",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 12,
          fontWeight: 600,
          border: "none",
          cursor: "pointer",
          fontFamily: "inherit",
        }}
      >
        {initials}
      </button>

      {open && (
        <div
          style={{
            position: "absolute",
            right: 0,
            top: "calc(100% + 8px)",
            width: 240,
            backgroundColor: "#FFFFFF",
            border: "1px solid #E8E2DB",
            borderRadius: 10,
            boxShadow: "0 8px 24px rgba(23,20,18,0.16)",
            overflow: "hidden",
            zIndex: 60,
          }}
        >
          <div style={{ padding: "10px 14px", borderBottom: "1px solid #E8E2DB" }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: "#1B1817" }}>
              {profile.name || profile.email || "…"}
            </div>
            {profile.email && (
              <div style={{ fontSize: 12, color: "#6E6660" }}>{profile.email}</div>
            )}
            <div style={{ fontSize: 12, color: "#6E6660" }}>
              {profile.company}
              {profile.role ? ` · ${profile.role}` : ""}
            </div>
          </div>
          {/* Single entry — the settings area itself has the section nav. */}
          <Link href="/settings" onClick={() => setOpen(false)} style={itemStyle}>
            <SettingsIcon size={14} style={{ color: "#6E6660" }} />
            Settings
          </Link>
          <button onClick={logout} style={{ ...itemStyle, borderTop: "1px solid #E8E2DB" }}>
            <LogOut size={14} style={{ color: "#6E6660" }} />
            Log out
          </button>
        </div>
      )}
    </div>
  );
}
