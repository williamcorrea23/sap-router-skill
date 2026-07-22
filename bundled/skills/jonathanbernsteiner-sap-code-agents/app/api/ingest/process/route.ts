/**
 * B1 — ingestion chunk worker: POST /api/ingest/process
 * Each invocation processes one chunk of the oldest active job (clone+parse
 * +persist, or one summary batch) and re-queues itself while work remains.
 * Concurrency and FIFO order are enforced by the DB lease in
 * lib/ingest/jobs.ts, so duplicate triggers are harmless.
 *
 * Auth: service-role bearer only (server-to-server kicks) — no user session
 * reaches this route.
 */
import { NextRequest, after } from "next/server";
import { isActive, processChunk } from "../../../../lib/ingest/jobs";
import { isWorkerRequest, kickWorker } from "../../../../lib/ingest/worker-auth";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 300;

export async function POST(req: NextRequest) {
  if (!isWorkerRequest(req)) {
    return Response.json({ error: "not authorized" }, { status: 401 });
  }
  const job = await processChunk();
  if (job && isActive(job)) {
    const origin = req.nextUrl.origin;
    after(async () => {
      await kickWorker(origin);
    });
  }
  return Response.json({ job });
}
