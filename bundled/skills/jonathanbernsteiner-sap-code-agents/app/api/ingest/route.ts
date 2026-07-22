/**
 * B1 — trigger ingestion: POST /api/ingest { url, name? }
 * `name` (optional) overrides the URL-derived workspace name (slug-normalized
 * server-side). Creates (or returns the company's already-active) job and
 * kicks the chunk worker. The progress screen polls /api/ingest/jobs/<id>.
 */
import { NextRequest, after } from "next/server";
import { requireUser } from "../../../lib/auth/server";
import { createJob } from "../../../lib/ingest/jobs";
import { kickWorker } from "../../../lib/ingest/worker-auth";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  const auth = await requireUser(req);
  if (auth instanceof Response) return auth;
  let url: unknown;
  let name: unknown;
  try {
    ({ url, name } = await req.json());
  } catch {
    return Response.json({ error: "JSON body with { url } required" }, { status: 400 });
  }
  if (typeof url !== "string" || !url.trim()) {
    return Response.json({ error: "url required" }, { status: 400 });
  }
  if (name !== undefined && typeof name !== "string") {
    return Response.json({ error: "name must be a string" }, { status: 400 });
  }
  const result = await createJob(url, auth.companyId, name as string | undefined);
  if ("error" in result) return Response.json({ error: result.error }, { status: 400 });

  const origin = req.nextUrl.origin;
  after(async () => {
    await kickWorker(origin);
  });
  return Response.json({ job: result.job }, { status: 202 });
}
