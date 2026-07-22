"use client";

import { usePathname } from "next/navigation";
import { Building2, UserRound } from "lucide-react";
import SectionSidebar from "../../../components/layout/SectionSidebar";
import { useProfile } from "../../../components/useProfile";

// Settings area: section sidebar on the left (design-guidance SettingsShell
// layout), the active section's page on the right. Company settings only
// appears for admins.
export default function SettingsLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const profile = useProfile();

  const items = [
    { key: "profile", label: "Profile", path: "/settings", icon: <UserRound size={16} /> },
    ...(profile.role === "admin"
      ? [{ key: "company", label: "Company", path: "/settings/company", icon: <Building2 size={16} /> }]
      : []),
  ];

  const activeKey = pathname?.startsWith("/settings/company") ? "company" : "profile";

  return (
    <div className="flex" style={{ backgroundColor: "#F6F4F1", minHeight: "calc(100vh - 56px)" }}>
      <SectionSidebar heading="Settings" items={items} activeKey={activeKey} />
      {/* Shared content container: full pane width, same padding everywhere. */}
      <div className="flex-1 overflow-y-auto" style={{ padding: 32 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {children}
        </div>
      </div>
    </div>
  );
}
