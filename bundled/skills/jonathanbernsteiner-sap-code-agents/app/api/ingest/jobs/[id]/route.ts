/**
 * B1 — job status for the progress screen: GET /api/ingest/jobs/<id>
 * Company-scoped. If the job is active but no worker holds its lease (a
 * chunk died), the poll re-kicks the worker — polling doubles as stall
 * recovery.
 */
import { NextRequest, after } from "next/server";
import { requireUser } from "../../../../../lib/auth/server";
import { query } from "../../../../../lib/db/client";
import { getJob, isActive } from "../../../../../lib/ingest/jobs";
import { kickWorker } from "../../../../../lib/ingest/worker-auth";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const auth = await requireUser(req);
  if (auth instanceof Response) return auth;
  const { id } = await params;
  const job = await getJob(id);
  if (!job || job.company_id !== auth.companyId) {
    return Response.json({ error: "job not found" }, { status: 404 });
  }

  if (isActive(job)) {
    const [lease] = await query<{ stale: boolean }>(
      `select (lease_expires_at is null or lease_expires_at < now()) as stale
       from ingestion_jobs where id = $1`,
      [id]
    );
    if (lease?.stale) {
      const origin = req.nextUrl.origin;
      after(async () => {
        await kickWorker(origin);
      });
    }
  }
  return Response.json({ job });
}

/**
 * Dismiss a finished/failed job row (Connections page). Active jobs cannot
 * be dismissed — they hold the single ingestion slot until they finish or
 * fail. Admin-only, mirroring workspace deletion.
 */
export async function DELETE(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const auth = await requireUser(req);
  if (auth instanceof Response) return auth;
  if (auth.role !== "admin") {
    return Response.json({ error: "only company admins can dismiss ingestion jobs" }, { status: 403 });
  }
  const { id } = await params;
  const job = await getJob(id);
  if (!job || job.company_id !== auth.companyId) {
    return Response.json({ error: "job not found" }, { status: 404 });
  }
  if (isActive(job)) {
    return Response.json({ error: "job is still running" }, { status: 409 });
  }
  await query(`delete from ingestion_jobs where id = $1`, [id]);
  return Response.json({ deleted: id });
}
