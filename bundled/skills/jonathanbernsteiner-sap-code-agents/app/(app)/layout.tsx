import AppShell from "../../components/AppShell";

// Authenticated app area: sidebar + top bar. The auth pages ((auth) group)
// render without the shell; middleware guarantees a session here.
export default function AppLayout({ children }: { children: React.ReactNode }) {
  return <AppShell>{children}</AppShell>;
}
