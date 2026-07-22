/**
 * Streaming chat endpoint (Change Order 02): POST { workspace, sessionId?, message }
 * → NDJSON stream. First event is {type:"session", id, title, created} so the UI
 * can show the conversation in history immediately; the agent's events follow
 * (text deltas, tool calls with durations), then {type:"title"} once the traced
 * Haiku auto-title lands, then {type:"done"}.
 *
 * Persistence: the user message is stored up front; the assistant message is
 * stored after completion with its tool-call summary (inline offsets +
 * durations) and the agent trace id.
 */
import { NextRequest } from "next/server";
import { runAgent, type AgentEvent } from "../../../lib/agent/loop";
import { requireUser, resolveWorkspaceForCompany } from "../../../lib/auth/server";
import { query } from "../../../lib/db/client";
import {
  addMessage,
  buildAgentContext,
  createSession,
  fallbackTitle,
  generateTitle,
  getMessages,
  getSession,
  type StoredToolCall,
} from "../../../lib/chat/store";

export const runtime = "nodejs";
export const maxDuration = 300;

export async function POST(req: NextRequest) {
  const auth = await requireUser(req);
  if (auth instanceof Response) return auth;
  const body = await req.json().catch(() => null);
  const workspace = body?.workspace;
  const sessionId = body?.sessionId;
  const message = typeof body?.message === "string" ? body.message.trim() : "";
  if (typeof workspace !== "string" || !message) {
    return Response.json(
      { error: "expected { workspace, sessionId?, message }" },
      { status: 400 }
    );
  }

  const ws = await resolveWorkspaceForCompany(workspace, auth.companyId);
  if (!ws) return Response.json({ error: `workspace '${workspace}' not found` }, { status: 404 });

  // Resolve or create the session before streaming so errors surface as HTTP.
  // Continuing a session is creator-only — colleagues' chats are read-only.
  let session;
  let created = false;
  if (sessionId) {
    session = await getSession(String(sessionId));
    if (!session || session.workspace_id !== ws.id || session.company_id !== auth.companyId) {
      return Response.json({ error: "session not found in this system" }, { status: 404 });
    }
    if (session.created_by !== auth.userId) {
      return Response.json(
        { error: "colleagues' chats are read-only — start your own chat to continue the topic" },
        { status: 403 }
      );
    }
  } else {
    session = await createSession(ws.id, auth.companyId, auth.userId, fallbackTitle(message));
    created = true;
  }

  const priorMessages = await getMessages(session.id);
  await addMessage(session.id, "user", message);

  // Auto-title runs concurrently with the agent; the UI shows the fallback
  // title immediately and swaps it when the "title" event arrives.
  const titlePromise = created ? generateTitle(ws.id, auth.companyId, message) : null;

  const { contextNote, turns } = await buildAgentContext(session, [
    ...priorMessages.map((m) => ({ role: m.role, content_md: m.content_md })),
    { role: "user" as const, content_md: message },
  ]);

  const encoder = new TextEncoder();
  const finalSession = session;
  const stream = new ReadableStream({
    async start(controller) {
      const emit = (e: object) => controller.enqueue(encoder.encode(JSON.stringify(e) + "\n"));
      emit({ type: "session", id: finalSession.id, title: finalSession.title, created });

      // Reconstruct inline tool rows later: track the char offset in the
      // assistant text at which each call happened, and its wall duration.
      const toolCalls: (StoredToolCall & { startedAt?: number })[] = [];
      let textLen = 0;
      let traceId: number | null = null;

      let finalText = "";
      try {
        finalText = await runAgent({
          workspaceName: workspace,
          companyId: auth.companyId,
          turns,
          contextNote,
          onTraceId: (id) => {
            traceId = id;
          },
          onEvent: (e: AgentEvent) => {
            if (e.type === "text") textLen += e.delta.length;
            if (e.type === "tool_use") {
              toolCalls.push({
                name: e.name,
                input: e.input,
                duration_ms: null,
                at: textLen,
                startedAt: Date.now(),
              });
            }
            if (e.type === "tool_result") {
              const open = toolCalls.find((t) => t.name === e.name && t.duration_ms === null);
              if (open?.startedAt) {
                open.duration_ms = Date.now() - open.startedAt;
                emit({ ...e, duration_ms: open.duration_ms });
                return;
              }
            }
            emit(e);
          },
        });
      } catch (e) {
        emit({ type: "error", message: (e as Error).message });
      }

      try {
        // Store even an empty/errored turn so the transcript keeps alternating.
        await addMessage(
          finalSession.id,
          "assistant",
          finalText,
          toolCalls.map(({ name, input, duration_ms, at }) => ({ name, input, duration_ms, at })),
          traceId
        );
        if (titlePromise) {
          const title = await titlePromise;
          if (title !== finalSession.title) {
            await query(`update chat_sessions set title = $2 where id = $1`, [
              finalSession.id,
              title,
            ]);
          }
          emit({ type: "title", id: finalSession.id, title });
        }
      } catch (e) {
        emit({ type: "error", message: `failed to persist message: ${(e as Error).message}` });
      } finally {
        controller.close();
      }
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "application/x-ndjson; charset=utf-8",
      "Cache-Control": "no-cache",
    },
  });
}
