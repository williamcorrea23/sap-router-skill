"use client";

import { useRef, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  LayoutGrid,
  FileText,
  Upload,
  Settings,
  type LucideIcon,
} from "lucide-react";
import { navItems } from "../../lib/navigation";

// Map the string names in lib/navigation.ts to real lucide icons.
// Add an icon here whenever you add one to the nav list.
const iconMap: Record<string, LucideIcon> = {
  LayoutDashboard,
  LayoutGrid,
  FileText,
  Upload,
  Settings,
};

export default function Sidebar() {
  const pathname = usePathname();
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

  return (
    <aside
      style={{ backgroundColor: "#171412", width: 56 }}
      className="fixed top-0 left-0 h-screen flex flex-col z-40"
    >
      {/* Logo placeholder — swap in the real product mark later */}
      <div
        className="flex items-center justify-center"
        style={{ paddingTop: 12, paddingBottom: 16 }}
      >
        <div
          className="rounded-full flex items-center justify-center"
          style={{ width: 32, height: 32, backgroundColor: "#F04E0D" }}
        />
      </div>

      {/* Nav items */}
      <nav className="flex-1 flex flex-col items-center" style={{ paddingTop: 4 }}>
        {navItems.map((item) => {
          const Icon = iconMap[item.icon];
          const isActive =
            pathname === item.path || pathname?.startsWith(item.path + "/");
          const isHovered = hoveredItem === item.key;

          return (
            <div
              key={item.key}
              className="relative flex items-center justify-center"
              style={{ width: 56, height: 56 }}
              onMouseEnter={() => handleMouseEnter(item.key)}
              onMouseLeave={handleMouseLeave}
            >
              <Link
                href={item.path}
                className="flex items-center justify-center"
                style={{
                  width: 40,
                  height: 40,
                  borderRadius: 8,
                  backgroundColor:
                    isActive || isHovered ? "#F04E0D" : "transparent",
                  transition: "background-color 150ms ease",
                }}
              >
                {Icon && (
                  <Icon size={22} style={{ color: "#FFFFFF" }} className="flex-shrink-0" />
                )}
              </Link>

              {/* Tooltip label — appears on hover (after 200ms), hides on leave */}
              <div
                className="absolute top-1/2 pointer-events-none"
                style={{
                  left: "calc(100% + 8px)",
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
        })}
      </nav>
    </aside>
  );
}
