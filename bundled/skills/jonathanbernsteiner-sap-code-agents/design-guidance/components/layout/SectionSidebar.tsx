"use client";

import { useState } from "react";

export interface SectionSidebarItem {
  key: string;
  label: string;
  icon: React.ReactNode;
}

interface SectionSidebarProps {
  heading: string;
  items: SectionSidebarItem[];
  activeKey: string;
  onSelect: (key: string) => void;
}

// The inner (second-level) sidebar used inside Settings: 240px wide, gray
// background, uppercase heading, active-item card with left accent border + shadow.
export default function SectionSidebar({
  heading,
  items,
  activeKey,
  onSelect,
}: SectionSidebarProps) {
  return (
    <nav
      className="shrink-0"
      style={{
        width: 240,
        borderRight: "1px solid #E8E2DB",
        backgroundColor: "#F6F4F1",
      }}
    >
      <div
        style={{
          padding: "20px 16px 8px 16px",
          fontSize: 12,
          fontWeight: 600,
          color: "#A49C95",
          letterSpacing: 1,
          textTransform: "uppercase",
        }}
      >
        {heading}
      </div>
      <div className="flex flex-col gap-0.5 px-2 pt-1">
        {items.map((item) => (
          <SidebarItem
            key={item.key}
            item={item}
            active={activeKey === item.key}
            onSelect={onSelect}
          />
        ))}
      </div>
    </nav>
  );
}

function SidebarItem({
  item,
  active,
  onSelect,
}: {
  item: SectionSidebarItem;
  active: boolean;
  onSelect: (key: string) => void;
}) {
  const [hovered, setHovered] = useState(false);
  const showWhiteBg = active || hovered;
  return (
    <button
      onClick={() => onSelect(item.key)}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 10,
        padding: "10px 16px",
        fontSize: 14,
        fontWeight: active ? 600 : 400,
        color: active ? "#1B1817" : "#6E6660",
        background: showWhiteBg ? "#FFFFFF" : "transparent",
        border: "none",
        borderLeft: active ? "2px solid #F04E0D" : "2px solid transparent",
        borderRadius: "0 6px 6px 0",
        cursor: "pointer",
        textAlign: "left",
        width: "100%",
        boxShadow: active ? "0 1px 2px rgba(0,0,0,0.04)" : "none",
        transition: "background 0.15s, color 0.15s",
      }}
    >
      {item.icon}
      {item.label}
    </button>
  );
}
