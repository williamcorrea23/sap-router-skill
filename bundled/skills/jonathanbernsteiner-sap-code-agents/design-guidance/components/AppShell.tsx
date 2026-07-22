"use client";

import Sidebar from "./layout/Sidebar";
import TopBar from "./layout/TopBar";

// Wraps every page: fixed 56px icon sidebar on the left, fixed 56px top bar,
// and the page content offset to clear both. Import this once in app/layout.tsx.
export default function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Sidebar />
      <TopBar />
      <main
        style={{ marginLeft: 56, paddingTop: 56 }}
        className="min-h-screen"
      >
        {children}
      </main>
    </>
  );
}
