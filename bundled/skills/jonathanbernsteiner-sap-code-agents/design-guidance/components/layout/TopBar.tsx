"use client";

import { usePathname } from "next/navigation";
import { Search } from "lucide-react";
import { navItems } from "../../lib/navigation";

export default function TopBar() {
  const pathname = usePathname();

  // Title = the matching nav item's label, or the portal name on unknown routes.
  const pageTitle =
    navItems.find(
      (n) => pathname === n.path || pathname?.startsWith(n.path + "/"),
    )?.label ?? "Portal";

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
      <h1
        style={{
          fontSize: 18,
          fontWeight: 600,
          color: "#1B1817",
          margin: 0,
          whiteSpace: "nowrap",
        }}
      >
        {pageTitle}
      </h1>

      {/* Centered search box (visual placeholder — wire it up later) */}
      <div
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
            cursor: "pointer",
            backgroundColor: "#FAF8F5",
            transition: "border-color 150ms",
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLElement).style.borderColor = "#A49C95";
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLElement).style.borderColor = "#E8E2DB";
          }}
        >
          <Search size={14} style={{ color: "#A49C95" }} />
          <span style={{ fontSize: 13, color: "#A49C95", flex: 1 }}>Search...</span>
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
      </div>

      {/* Right side — avatar placeholder */}
      <div style={{ marginLeft: "auto", display: "flex", alignItems: "center" }}>
        <div
          style={{
            width: 32,
            height: 32,
            borderRadius: "50%",
            backgroundColor: "#E8E2DB",
            color: "#6E6660",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 13,
            fontWeight: 600,
          }}
        >
          U
        </div>
      </div>
    </header>
  );
}
