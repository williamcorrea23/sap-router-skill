/**
 * DIAGNOSTICS tool handlers: get_short_dumps, get_short_dump_detail, get_traces, get_trace_detail
 */

import type { ADTClient } from "abap-adt-api";
import type { ToolResult } from "../../types.js";
import { S_GetDumps, S_GetDumpDetail, S_GetTraces, S_GetTraceDetail } from "../../schemas.js";
import { ADT_RUNTIME_DUMPS } from "../../adt-endpoints.js";
import { cfg } from "../../config.js";

function ok(text: string): ToolResult { return { content: [{ type: "text", text }] }; }
function err(text: string): ToolResult { return { content: [{ type: "text", text }], isError: true }; }

export async function handleGetShortDumps(client: ADTClient, args: Record<string, unknown>): Promise<ToolResult> {
  const p = S_GetDumps.parse(args);
  const res = await client.dumps(p.user);
  const all = res.dumps ?? [];
  const limit = p.maxResults ?? cfg.maxDumps;
  const limited = all.slice(0, limit);
  const note = all.length > limited.length
    ? ` (showing ${limited.length} of ${all.length} — limit ${limit})`
    : "";
  return ok(`${limited.length} short dump(s)${note}:\n\n${JSON.stringify(limited, null, 2)}`);
}

export async function handleGetShortDumpDetail(client: ADTClient, args: Record<string, unknown>): Promise<ToolResult> {
  const p = S_GetDumpDetail.parse(args);
  try {
    const res = await client.httpClient.request(
      `${ADT_RUNTIME_DUMPS}/${encodeURIComponent(p.dumpId)}`, { method: "GET" }
    );
    return ok(typeof res.body === "string" ? res.body : JSON.stringify(res.body, null, 2));
  } catch {
    const feed = await client.dumps();
    const dump = feed.dumps?.find(d => d.id === p.dumpId);
    if (!dump) return err(`Dump '${p.dumpId}' not found.`);
    return ok(JSON.stringify(dump, null, 2));
  }
}

export async function handleGetTraces(client: ADTClient, args: Record<string, unknown>): Promise<ToolResult> {
  const p = S_GetTraces.parse(args);
  const res = await client.tracesList(p.user);
  const limit = p.maxResults ?? 10;
  const allRuns = res.runs ?? [];
  const limited = { ...res, runs: allRuns.slice(0, limit) };
  const note = allRuns.length > limit ? ` (showing ${limit} of ${allRuns.length} runs)` : "";
  return ok(`Traces${note}:\n\n${JSON.stringify(limited, null, 2)}`);
}

export async function handleGetTraceDetail(client: ADTClient, args: Record<string, unknown>): Promise<ToolResult> {
  const p = S_GetTraceDetail.parse(args);
  const res = await client.tracesHitList(p.traceId, true);
  return ok(JSON.stringify(res, null, 2));
}
