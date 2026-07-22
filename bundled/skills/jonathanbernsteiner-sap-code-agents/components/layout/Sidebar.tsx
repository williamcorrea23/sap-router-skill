"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BookOpen,
  Link2,
  MessageSquare,
  Server,
  Settings,
  type LucideIcon,
} from "lucide-react";
import { navItems, type NavItem } from "../../lib/navigation";
import { PRODUCT_NAME } from "../../lib/config";
import { useProfile } from "../useProfile";

// Rendered as the last nav item (after the items from lib/navigation.ts).
const settingsItem: NavItem = { key: "settings", label: "Settings", path: "/settings", icon: "Settings" };

// Map the string names in lib/navigation.ts to real lucide icons.
// Add an icon here whenever you add one to the nav list.
const iconMap: Record<string, LucideIcon> = {
  BookOpen,
  Link2,
  MessageSquare,
  Server,
  Settings,
};

export default function Sidebar() {
  const pathname = usePathname();
  const profile = useProfile();
  // "Workspace" routes to the last-active workspace's Overview; without one
  // it routes to Connections (where workspaces are created). Read after
  // mount (SSR-safe) and re-read on navigation — the /w layout keeps the
  // stored selection current.
  const [lastWorkspace, setLastWorkspace] = useState<string | null>(null);
  useEffect(() => {
    setLastWorkspace(localStorage.getItem("workspace"));
  }, [pathname]);
  // Company avatar: first letter of the company name; product initial if the
  // name is empty. No letter until the profile has loaded (avoids a flash).
  const avatarLabel = profile.company.trim() || PRODUCT_NAME;
  const avatarLetter = profile.loaded ? avatarLabel.charAt(0).toUpperCase() : "";
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);
  const [showTooltip, setShowTooltip] = useState<string | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleMouseEnter = (key: string) => {
    setHoveredItem(key);
    timerRef.current = setTimeout(() => setShowTooltip(key), 200);
  };

  const handleMouseLeave = () => {
    if (timerRef.current) clearTimeout(timerRef.current);
    setHoveredItem(null);
    setShowTooltip(null);
  };

  const renderItem = (item: NavItem) => {
    const Icon = iconMap[item.icon];
    // "/w" covers every workspace tab route (/w/<name>/…), so the Workspace
    // item is active whenever a workspace is open; Connections only on
    // /connections, etc.
    const isActive = pathname === item.path || pathname?.startsWith(item.path + "/");
    const isHovered = hoveredItem === item.key;
    const href =
      item.key === "workspace"
        ? lastWorkspace
          ? `/w/${encodeURIComponent(lastWorkspace)}/overview`
          : "/connections"
        : item.path;

    return (
      <div
        key={item.key}
        className="relative flex items-center justify-center"
        style={{ width: 56, height: 56 }}
        onMouseEnter={() => handleMouseEnter(item.key)}
        onMouseLeave={handleMouseLeave}
      >
        <Link
          href={href}
          className="flex items-center justify-center"
          style={{
            width: 40,
            height: 40,
            borderRadius: 8,
            backgroundColor: isActive || isHovered ? "#F04E0D" : "transparent",
            transition: "background-color 150ms ease",
          }}
        >
          {Icon && <Icon size={22} style={{ color: "#FFFFFF" }} className="flex-shrink-0" />}
        </Link>

        {/* Tooltip label — appears on hover (after 200ms), hides on leave */}
        <div
          className="absolute top-1/2 pointer-events-none"
          style={{
            left: "calc(100% + 10px)",
            transform: "translateY(-50%)",
            backgroundColor: "#171412",
            color: "#FFFFFF",
            fontSize: 13,
            fontWeight: 500,
            padding: "6px 12px",
            borderRadius: 6,
            boxShadow: "0 2px 8px rgba(0,0,0,0.3)",
            whiteSpace: "nowrap",
            opacity: showTooltip === item.key ? 1 : 0,
            transition: "opacity 150ms ease",
            visibility: showTooltip === item.key ? "visible" : "hidden",
            zIndex: 50,
          }}
        >
          {item.label}
        </div>
      </div>
    );
  };

  return (
    <aside
      // z-60: tooltips render to the right of the icons and must float above
      // the top bar (z-50) and page content, never clipped or covered.
      style={{ backgroundColor: "#171412", width: 56, zIndex: 60 }}
      className="fixed top-0 left-0 h-screen flex flex-col"
    >
      {/* Company avatar — first letter of the company; links home (the smart
          landing resolves to the last-used workspace or Connections) */}
      <div
        className="relative flex items-center justify-center"
        style={{ paddingTop: 12, paddingBottom: 16 }}
        onMouseEnter={() => handleMouseEnter("company-avatar")}
        onMouseLeave={handleMouseLeave}
      >
        <Link
          href="/"
          aria-label={avatarLabel}
          className="rounded-full flex items-center justify-center"
          style={{ width: 32, height: 32, backgroundColor: "#F04E0D" }}
        >
          <span
            style={{
              color: "#FFFFFF",
              fontSize: 15,
              fontWeight: 600,
              lineHeight: 1,
              // Caps sit slightly high in the em box; nudge down to center optically.
              transform: "translateY(0.5px)",
            }}
          >
            {avatarLetter}
          </span>
        </Link>

        <div
          className="absolute pointer-events-none"
          style={{
            left: "calc(100% + 10px)",
            top: "50%",
            transform: "translateY(calc(-50% - 2px))",
            backgroundColor: "#171412",
            color: "#FFFFFF",
            fontSize: 13,
            fontWeight: 500,
            padding: "6px 12px",
            borderRadius: 6,
            boxShadow: "0 2px 8px rgba(0,0,0,0.3)",
            whiteSpace: "nowrap",
            opacity: showTooltip === "company-avatar" ? 1 : 0,
            transition: "opacity 150ms ease",
            visibility: showTooltip === "company-avatar" ? "visible" : "hidden",
            zIndex: 50,
          }}
        >
          {avatarLabel}
        </div>
      </div>

      {/* Nav items — Workspace · Chat · Connections · Settings */}
      <nav className="flex-1 flex flex-col items-center" style={{ paddingTop: 4 }}>
        {[...navItems, settingsItem].map(renderItem)}
      </nav>
    </aside>
  );
}
