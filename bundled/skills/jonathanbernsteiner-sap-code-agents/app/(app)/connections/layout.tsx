"use client";

import { usePathname } from "next/navigation";
import { Plug, Server } from "lucide-react";
import SectionSidebar from "../../../components/layout/SectionSidebar";

// Connections area: section sidebar on the left (same SectionSidebar pattern
// as Settings), the active section's page on the right — Connect a system
// and Connected systems are separate routes.
export default function ConnectionsLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  const items = [
    { key: "connect", label: "Connect a system", path: "/connections", icon: <Plug size={16} /> },
    { key: "systems", label: "Connected systems", path: "/connections/systems", icon: <Server size={16} /> },
  ];

  const activeKey = pathname?.startsWith("/connections/systems") ? "systems" : "connect";

  return (
    <div className="flex" style={{ backgroundColor: "#F6F4F1", minHeight: "calc(100vh - 56px)" }}>
      <SectionSidebar heading="Connections" items={items} activeKey={activeKey} />
      {/* Shared content container: full pane width, same padding everywhere. */}
      <div className="flex-1 overflow-y-auto" style={{ padding: 32 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {children}
        </div>
      </div>
    </div>
  );
}
