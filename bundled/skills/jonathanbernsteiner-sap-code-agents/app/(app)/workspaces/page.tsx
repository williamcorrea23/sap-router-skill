import { redirect } from "next/navigation";

// Legacy route — source management lives at /connections now.
export default function LegacyWorkspaces() {
  redirect("/connections");
}
