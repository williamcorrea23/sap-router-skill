"use client";

import LegacyWorkspaceRedirect from "../../../components/LegacyWorkspaceRedirect";

// Legacy route — Overview now lives at /w/<workspace>/overview.
export default function LegacyOverview() {
  return <LegacyWorkspaceRedirect tab="overview" />;
}
