// Sidebar navigation for the new portal.
// Edit labels / paths / icons here — the Sidebar reads from this list.
// `icon` must match a key in the iconMap inside components/layout/Sidebar.tsx.

export interface NavItem {
  key: string;
  label: string;
  path: string;
  icon: string;
}

export const navItems: NavItem[] = [
  { key: "overview",   label: "Overview",   path: "/overview",   icon: "LayoutDashboard" },
  { key: "page-two",   label: "Page Two",   path: "/page-two",   icon: "LayoutGrid" },
  { key: "page-three", label: "Page Three", path: "/page-three", icon: "FileText" },
  { key: "upload",     label: "Upload",     path: "/upload",     icon: "Upload" },
  { key: "settings",   label: "Settings",   path: "/settings",   icon: "Settings" },
];
