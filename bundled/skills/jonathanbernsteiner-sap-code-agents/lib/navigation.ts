// Sidebar navigation. `icon` must match a key in the iconMap inside
// components/layout/Sidebar.tsx.

export interface NavItem {
  key: string;
  label: string;
  path: string;
  icon: string;
}

export const navItems: NavItem[] = [
  // "Workspace" = the analysis surface (/w/[id]/… with Overview | Objects |
  // Report tabs and the switcher in its header). Its sidebar href is dynamic
  // (last-active workspace's Overview; Connections when none exists) — see
  // Sidebar.tsx. The "/w" path makes the generic active-state and top-bar
  // title rules cover every workspace tab route.
  { key: "workspace", label: "System", path: "/w", icon: "Server" },
  { key: "chat", label: "Chat", path: "/chat", icon: "MessageSquare" },
  { key: "connections", label: "Connections", path: "/connections", icon: "Link2" },
  // CO-07: the inspectable S/4HANA knowledge base — global reference data,
  // not workspace-scoped, hence a top-level rail item.
  { key: "rules", label: "S/4HANA rules", path: "/rules", icon: "BookOpen" },
  // Settings is the pinned gear in the sidebar footer (see Sidebar.tsx).
];
