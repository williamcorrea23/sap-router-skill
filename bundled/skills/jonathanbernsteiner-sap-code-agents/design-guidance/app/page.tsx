import { redirect } from "next/navigation";

// Home ("/") redirects to the Overview page.
export default function Home() {
  redirect("/overview");
}
