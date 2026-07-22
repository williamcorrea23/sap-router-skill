/**
 * Report export: GET /api/report/export?workspace=<name>&format=md|csv|pdf
 * Rendering lives in lib/report/render.ts + lib/report/pdf.ts over
 * lib/report/data.ts (shared with the on-screen report) — the exports
 * follow the same section order as the page:
 * executive summary → run snapshot → retirement → Tier 1 by rule →
 * Tier 2 by object → Tier 3.
 */
import { NextRequest } from "next/server";
import { requireUser, resolveWorkspaceForCompany } from "../../../../lib/auth/server";
import { getReportData } from "../../../../lib/report/data";
import { renderPdf } from "../../../../lib/report/pdf";
import { renderCsv, renderMarkdown } from "../../../../lib/report/render";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const auth = await requireUser(req);
  if (auth instanceof Response) return auth;
  const workspace = req.nextUrl.searchParams.get("workspace");
  const format = req.nextUrl.searchParams.get("format") ?? "md";
  if (!workspace) return Response.json({ error: "workspace required" }, { status: 400 });
  if (!(await resolveWorkspaceForCompany(workspace, auth.companyId))) {
    return Response.json({ error: "workspace not found" }, { status: 404 });
  }
  const data = await getReportData(workspace);
  if (!data) return Response.json({ error: "workspace not found" }, { status: 404 });

  if (format === "pdf") {
    const pdf = await renderPdf(data);
    return new Response(new Uint8Array(pdf), {
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": `attachment; filename="s4hana-report-${workspace}.pdf"`,
      },
    });
  }
  if (format === "csv") {
    return new Response(renderCsv(data), {
      headers: {
        "Content-Type": "text/csv; charset=utf-8",
        "Content-Disposition": `attachment; filename="s4hana-report-${workspace}.csv"`,
      },
    });
  }
  return new Response(renderMarkdown(data), {
    headers: {
      "Content-Type": "text/markdown; charset=utf-8",
      "Content-Disposition": `attachment; filename="s4hana-report-${workspace}.md"`,
    },
  });
}
