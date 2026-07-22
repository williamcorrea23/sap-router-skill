import { redirect } from "next/navigation";

// Legacy route — the connect form lives on /connections now.
export default function LegacyWorkspacesNew() {
  redirect("/connections");
}
