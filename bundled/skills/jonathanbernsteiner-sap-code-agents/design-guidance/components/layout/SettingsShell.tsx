"use client";

import { useState } from "react";
import {
  UserCircle,
  Building2,
  Plug,
  Mail,
  ListChecks,
  Users as UsersIcon,
} from "lucide-react";
import SectionSidebar from "./SectionSidebar";
import Card from "../ui/Card";

// Mirrors the settings layout of the original app: a 240px section sidebar on
// the left with tabs, and placeholder content on the right. Add real editors
// per tab as you build them.
type TabKey =
  | "preferences"
  | "profile"
  | "integrations"
  | "email_templates"
  | "data_fields"
  | "users";

const TABS: { key: TabKey; label: string; icon: React.ReactNode }[] = [
  { key: "preferences",    label: "Personal preferences", icon: <UserCircle size={16} /> },
  { key: "profile",        label: "Profile",              icon: <Building2 size={16} /> },
  { key: "integrations",   label: "Integrations",         icon: <Plug size={16} /> },
  { key: "email_templates",label: "Email Templates",      icon: <Mail size={16} /> },
  { key: "data_fields",    label: "Data Fields",          icon: <ListChecks size={16} /> },
  { key: "users",          label: "Users",                icon: <UsersIcon size={16} /> },
];

export default function SettingsShell() {
  const [activeTab, setActiveTab] = useState<TabKey>("preferences");
  const active = TABS.find((t) => t.key === activeTab)!;

  return (
    <div className="flex" style={{ backgroundColor: "#F6F4F1", minHeight: "calc(100vh - 56px)" }}>
      <SectionSidebar
        heading="Settings"
        activeKey={activeTab}
        onSelect={(k) => setActiveTab(k as TabKey)}
        items={TABS.map((t) => ({ key: t.key, label: t.label, icon: t.icon }))}
      />

      {/* Content area — placeholder per tab */}
      <div className="flex-1 overflow-y-auto" style={{ backgroundColor: "#F6F4F1", padding: 32 }}>
        <div style={{ maxWidth: 640 }} className="space-y-6">
          <Card>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
              <span style={{ color: "#F04E0D", display: "flex" }}>{active.icon}</span>
              <h2 style={{ fontSize: 16, fontWeight: 600, color: "#1B1817", margin: 0 }}>
                {active.label}
              </h2>
            </div>
            <p style={{ fontSize: 14, color: "#6E6660", margin: 0 }}>
              Placeholder for the <strong>{active.label}</strong> settings. Replace
              this card with the real editor when you build it.
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
}
