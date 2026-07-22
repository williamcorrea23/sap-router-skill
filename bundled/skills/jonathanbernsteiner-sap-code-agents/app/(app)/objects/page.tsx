"use client";

import LegacyWorkspaceRedirect from "../../../components/LegacyWorkspaceRedirect";

// Legacy route — Objects now lives at /w/<workspace>/objects.
export default function LegacyObjects() {
  return <LegacyWorkspaceRedirect tab="objects" />;
}
