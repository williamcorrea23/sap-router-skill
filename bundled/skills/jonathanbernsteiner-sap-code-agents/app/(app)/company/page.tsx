import { redirect } from "next/navigation";

// Company settings moved under the Settings area (kept so old links work).
export default function CompanyRedirect() {
  redirect("/settings/company");
}
