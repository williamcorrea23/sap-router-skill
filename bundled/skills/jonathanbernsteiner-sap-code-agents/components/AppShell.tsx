"use client";

import Sidebar from "./layout/Sidebar";
import TopBar from "./layout/TopBar";

// Wraps every page: fixed 56px icon sidebar on the left, fixed 56px top bar,
// and the page content offset to clear both. Import this once in app/layout.tsx.
export default function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <>
      {/* contents = no layout impact on screen; print:hidden drops the fixed
          chrome from PDF exports (globals.css resets main's offsets) */}
      <div className="contents print:hidden">
        <Sidebar />
        <TopBar />
      </div>
      <main
        style={{ marginLeft: 56, paddingTop: 56 }}
        className="min-h-screen"
      >
        {children}
      </main>
    </>
  );
}
