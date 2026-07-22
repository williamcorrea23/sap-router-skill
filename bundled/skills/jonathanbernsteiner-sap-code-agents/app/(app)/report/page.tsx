"use client";

import LegacyWorkspaceRedirect from "../../../components/LegacyWorkspaceRedirect";

// Legacy route — the Migration Report now lives at /w/<workspace>/report.
export default function LegacyReport() {
  return <LegacyWorkspaceRedirect tab="report" />;
}
