/**
 * Anthropic tool-use loop (Phase 4). Model: claude-sonnet-5, four
 * workspace-scoped tools, max 10 tool calls per query, streamed.
 *
 * Hard rules enforced in the system prompt: no fabrication, unresolved names
 * stay visible, all numbers come from tool results (SQL), simulated usage is
 * always labeled, diagrams are never written by the model.
 */
import Anthropic from "@anthropic-ai/sdk";
import { PRODUCT_NAME } from "../config";
import { query } from "../db/client";
import { TOOL_DEFINITIONS, executeTool, resolveWorkspace } from "./tools";

export const AGENT_MODEL = "claude-sonnet-5";
const MAX_TOOL_CALLS = 10;
const MAX_TOKENS = 2000;

export type AgentEvent =
  | { type: "text"; delta: string }
  | { type: "tool_use"; name: string; input: Record<string, unknown> }
  | { type: "tool_result"; name: string; size: number }
  | { type: "error"; message: string }
  | { type: "done"; toolCalls: number };

export interface AgentTurn {
  role: "user" | "assistant";
  content: string;
}

function systemPrompt(workspaceName: string, simulatedUsage: boolean, contextNote?: string): string {
  return `You are the analysis agent of "${PRODUCT_NAME}", answering questions about the ingested custom ABAP workspace "${workspaceName}".

Hard rules — never violate:
1. NO FABRICATION. State only what your tools returned in this conversation. If you did not retrieve it, say you don't know or retrieve it. Never invent object names, tables, code, or behavior.
2. Unresolved references stay visible: tools mark call targets outside the workspace as "[external]" (not ingested here — likely SAP standard when the name is not Z*/Y*) — relay that status; never guess what such an object does. Targets marked "[internal]" are routines defined inside the object itself (e.g. FORMs), not dependencies.
3. Numbers come from the tools (they are computed by SQL). Never compute your own totals or percentages beyond trivially restating tool output.
4. ${simulatedUsage ? 'Usage statistics in this workspace are SIMULATED. Any time you mention a usage number, label it as simulated data.' : 'This workspace has no usage data; if asked about usage, say "no usage data available" rather than estimating.'}
5. Cite evidence: when you reference code behavior, name the object and file:line the tool showed you.
6. You have at most ${MAX_TOOL_CALLS} tool calls per question — plan them; prefer search_objects first, then targeted read_object/where_used.
7. Do not write Mermaid or any diagram syntax; diagrams are computed by the application, not by you.

Answer concisely in Markdown. If the question cannot be answered from this workspace's data, say so plainly.${
    contextNote
      ? `\n\nSummary of earlier messages in this conversation (older turns were trimmed from the transcript; treat this as prior context, not as tool-retrieved evidence):\n${contextNote}`
      : ""
  }`;
}

/**
 * Run the agent loop, emitting streaming events via onEvent.
 * Returns the final assistant text. Traces the full run to the traces table.
 */
export async function runAgent(opts: {
  workspaceName: string;
  turns: AgentTurn[];
  onEvent: (e: AgentEvent) => void | Promise<void>;
  /** Rolling summary of trimmed earlier turns (persistent sessions). */
  contextNote?: string;
  /** Receives the id of the trace row written for this run. */
  onTraceId?: (traceId: number) => void;
  /** Company scope for workspace visibility (set on all API paths). */
  companyId?: string;
}): Promise<string> {
  const { workspaceName, turns, onEvent, contextNote, onTraceId, companyId } = opts;
  const ws = await resolveWorkspace(workspaceName, companyId);
  if (!ws) {
    await onEvent({ type: "error", message: `workspace '${workspaceName}' not found` });
    await onEvent({ type: "done", toolCalls: 0 });
    return "";
  }

  const client = new Anthropic();
  const messages: Anthropic.MessageParam[] = turns.map((t) => ({ role: t.role, content: t.content }));
  const started = Date.now();
  let toolCalls = 0;
  let finalText = "";
  let inputTokens = 0;
  let outputTokens = 0;
  const toolLog: { name: string; input: unknown }[] = [];

  for (;;) {
    const stream = client.messages.stream({
      model: AGENT_MODEL,
      max_tokens: MAX_TOKENS,
      system: systemPrompt(workspaceName, ws.simulated_usage, contextNote),
      tools: TOOL_DEFINITIONS,
      messages,
    });

    stream.on("text", (delta) => {
      finalText += delta;
      void onEvent({ type: "text", delta });
    });

    const message = await stream.finalMessage();
    inputTokens += message.usage.input_tokens;
    outputTokens += message.usage.output_tokens;

    const toolUses = message.content.filter(
      (b): b is Anthropic.ToolUseBlock => b.type === "tool_use"
    );
    if (toolUses.length === 0 || toolCalls >= MAX_TOOL_CALLS) break;

    messages.push({ role: "assistant", content: message.content });
    const results: Anthropic.ToolResultBlockParam[] = [];
    for (const tu of toolUses) {
      toolCalls++;
      const input = tu.input as Record<string, unknown>;
      toolLog.push({ name: tu.name, input });
      await onEvent({ type: "tool_use", name: tu.name, input });
      let result: string;
      if (toolCalls > MAX_TOOL_CALLS) {
        result = JSON.stringify({ error: "tool call budget exhausted — answer with what you have" });
      } else {
        try {
          result = await executeTool(ws.id, tu.name, input);
        } catch (e) {
          result = JSON.stringify({ error: `tool failed: ${(e as Error).message}` });
        }
      }
      await onEvent({ type: "tool_result", name: tu.name, size: result.length });
      results.push({ type: "tool_result", tool_use_id: tu.id, content: result });
    }
    messages.push({ role: "user", content: results });

    if (message.stop_reason !== "tool_use") break;
  }

  try {
    const traceRows = await query<{ id: string }>(
      `insert into traces (workspace_id, kind, model, input, output, input_tokens, output_tokens, duration_ms)
       values ($1, 'agent', $2, $3, $4, $5, $6, $7)
       returning id`,
      [
        ws.id,
        AGENT_MODEL,
        JSON.stringify({ question: turns[turns.length - 1]?.content?.slice(0, 2000), tool_log: toolLog }),
        JSON.stringify({ text: finalText.slice(0, 8000), tool_calls: toolCalls }),
        inputTokens,
        outputTokens,
        Date.now() - started,
      ]
    );
    if (traceRows[0]) onTraceId?.(Number(traceRows[0].id));
  } catch {
    // tracing must never break the answer path
  }

  await onEvent({ type: "done", toolCalls });
  return finalText;
}
