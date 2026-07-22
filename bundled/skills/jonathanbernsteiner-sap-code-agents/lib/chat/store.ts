/**
 * Persistent chat sessions (Change Order 02). All queries are
 * workspace-scoped; deleting a workspace cascades to sessions and messages.
 */
import Anthropic from "@anthropic-ai/sdk";
import { query } from "../db/client";

export const TITLE_MODEL = "claude-haiku-4-5-20251001";
/** Max prior messages passed verbatim to the agent; older ones are summarized. */
export const CONTEXT_MESSAGE_CAP = 20;

export interface ChatSession {
  id: string;
  workspace_id: string;
  company_id: string;
  created_by: string | null;
  title: string;
  context_note: string | null;
  context_note_covers: number;
  created_at: string;
  updated_at: string;
}

export interface StoredToolCall {
  name: string;
  input: Record<string, unknown>;
  duration_ms: number | null;
  /** Char offset in content_md where the call happened (inline rendering). */
  at: number;
}

export interface ChatMessageRow {
  id: string;
  role: "user" | "assistant";
  content_md: string;
  tool_calls_json: StoredToolCall[];
  trace_id: string | null;
  created_at: string;
}

/**
 * Chat history (Change Order 03): the caller's own sessions by default;
 * scope "company" additionally returns colleagues' sessions (read-only in
 * the UI), each labeled with its creator's display name.
 */
export async function listSessions(
  workspaceId: string,
  companyId: string,
  userId: string,
  scope: "mine" | "company" = "mine"
) {
  return query<{
    id: string;
    title: string;
    created_at: string;
    updated_at: string;
    is_mine: boolean;
    creator_name: string;
  }>(
    `select s.id, s.title, s.created_at, s.updated_at,
            (s.created_by = $3) as is_mine,
            coalesce(nullif(p.display_name, ''), split_part(u.email, '@', 1), 'former member') as creator_name
     from chat_sessions s
     left join profiles p on p.user_id = s.created_by
     left join auth.users u on u.id = s.created_by
     where s.workspace_id = $1 and s.company_id = $2
       ${scope === "mine" ? "and s.created_by = $3" : ""}
     order by s.updated_at desc`,
    [workspaceId, companyId, userId]
  );
}

export async function getSession(sessionId: string): Promise<ChatSession | undefined> {
  const rows = await query<ChatSession>(
    `select id, workspace_id, company_id, created_by, title, context_note, context_note_covers,
            created_at, updated_at
     from chat_sessions where id = $1`,
    [sessionId]
  );
  return rows[0];
}

export async function getMessages(sessionId: string): Promise<ChatMessageRow[]> {
  return query<ChatMessageRow>(
    `select id, role, content_md, tool_calls_json, trace_id, created_at
     from chat_messages where session_id = $1 order by created_at, id`,
    [sessionId]
  );
}

/**
 * company_id is set explicitly (not left to the workspace trigger): chats on
 * a globally readable example workspace still belong to the chatting user's
 * company, never to the operator company that owns the example data.
 */
export async function createSession(
  workspaceId: string,
  companyId: string,
  userId: string,
  title: string
): Promise<ChatSession> {
  const rows = await query<ChatSession>(
    `insert into chat_sessions (workspace_id, company_id, created_by, title)
     values ($1, $2, $3, $4)
     returning id, workspace_id, company_id, created_by, title, context_note, context_note_covers,
               created_at, updated_at`,
    [workspaceId, companyId, userId, title]
  );
  return rows[0];
}

/** Only the creator may delete a session; colleagues' view is read-only. */
export async function deleteSession(sessionId: string, userId: string): Promise<boolean> {
  const rows = await query<{ id: string }>(
    `delete from chat_sessions where id = $1 and created_by = $2 returning id`,
    [sessionId, userId]
  );
  return rows.length > 0;
}

export async function addMessage(
  sessionId: string,
  role: "user" | "assistant",
  contentMd: string,
  toolCalls: StoredToolCall[] = [],
  traceId: number | null = null
): Promise<void> {
  await query(
    `insert into chat_messages (session_id, role, content_md, tool_calls_json, trace_id)
     values ($1, $2, $3, $4, $5)`,
    [sessionId, role, contentMd, JSON.stringify(toolCalls), traceId]
  );
  await query(`update chat_sessions set updated_at = now() where id = $1`, [sessionId]);
}

/** Deterministic fallback title: the first user message, truncated. */
export function fallbackTitle(firstMessage: string): string {
  const clean = firstMessage.replace(/\s+/g, " ").trim();
  return clean.length > 60 ? clean.slice(0, 57) + "…" : clean || "New chat";
}

/**
 * Auto-title from the first user message: one small traced Haiku call.
 * Falls back to the truncated message on any failure.
 */
export async function generateTitle(
  workspaceId: string,
  companyId: string,
  firstMessage: string
): Promise<string> {
  const started = Date.now();
  try {
    const client = new Anthropic();
    const res = await client.messages.create({
      model: TITLE_MODEL,
      max_tokens: 30,
      messages: [
        {
          role: "user",
          content: `Write a title for a chat that starts with the user message below. At most 6 words. No quotes, no trailing punctuation. Reply with the title only.\n\nUser message: ${firstMessage.slice(0, 500)}`,
        },
      ],
    });
    const raw = res.content
      .filter((b): b is Anthropic.TextBlock => b.type === "text")
      .map((b) => b.text)
      .join(" ")
      .replace(/["'“”]/g, "")
      .replace(/\s+/g, " ")
      .trim();
    const title = raw && raw.split(" ").length <= 10 ? raw : fallbackTitle(firstMessage);
    await query(
      `insert into traces (workspace_id, company_id, kind, model, input, output, input_tokens, output_tokens, duration_ms)
       values ($1, $8, 'chat_title', $2, $3, $4, $5, $6, $7)`,
      [
        workspaceId,
        TITLE_MODEL,
        JSON.stringify({ first_message: firstMessage.slice(0, 500) }),
        JSON.stringify({ title }),
        res.usage.input_tokens,
        res.usage.output_tokens,
        Date.now() - started,
        companyId,
      ]
    );
    return title;
  } catch {
    return fallbackTitle(firstMessage);
  }
}

/**
 * Keep the session's context note in sync with the 20-message window: when
 * more than CONTEXT_MESSAGE_CAP messages exist, the older ones are summarized
 * into a single note via one traced Haiku call and stored on the session.
 * Returns { contextNote, turns } — the turns to pass to the agent verbatim.
 */
export async function buildAgentContext(
  session: ChatSession,
  allMessages: { role: "user" | "assistant"; content_md: string }[]
): Promise<{ contextNote: string | undefined; turns: { role: "user" | "assistant"; content: string }[] }> {
  let start = Math.max(0, allMessages.length - CONTEXT_MESSAGE_CAP);
  // The Anthropic transcript must start with a user turn.
  while (start < allMessages.length && allMessages[start].role !== "user") start++;
  const turns = allMessages.slice(start).map((m) => ({ role: m.role, content: m.content_md }));

  if (start === 0) return { contextNote: undefined, turns };
  if (session.context_note && session.context_note_covers === start) {
    return { contextNote: session.context_note, turns };
  }

  const older = allMessages.slice(0, start);
  let note: string;
  const started = Date.now();
  try {
    const client = new Anthropic();
    const transcript = older
      .map((m) => `${m.role === "user" ? "User" : "Agent"}: ${m.content_md.slice(0, 1500)}`)
      .join("\n\n");
    const res = await client.messages.create({
      model: TITLE_MODEL,
      max_tokens: 400,
      messages: [
        {
          role: "user",
          content: `Summarize this ABAP-analysis chat excerpt in under 150 words so the conversation can continue without it. Keep object/table names exact; keep open questions and established facts. Reply with the summary only.\n\n${transcript.slice(0, 30_000)}`,
        },
      ],
    });
    note =
      res.content
        .filter((b): b is Anthropic.TextBlock => b.type === "text")
        .map((b) => b.text)
        .join(" ")
        .trim() || "(earlier messages could not be summarized)";
    await query(
      `insert into traces (workspace_id, company_id, kind, model, input, output, input_tokens, output_tokens, duration_ms)
       values ($1, $8, 'chat_context', $2, $3, $4, $5, $6, $7)`,
      [
        session.workspace_id,
        TITLE_MODEL,
        JSON.stringify({ session_id: session.id, messages_summarized: older.length }),
        JSON.stringify({ note }),
        res.usage.input_tokens,
        res.usage.output_tokens,
        Date.now() - started,
        session.company_id,
      ]
    );
    await query(
      `update chat_sessions set context_note = $2, context_note_covers = $3 where id = $1`,
      [session.id, note, start]
    );
  } catch {
    // summarization must never block the answer; fall back to any stale note
    note = session.context_note ?? "";
  }
  return { contextNote: note || undefined, turns };
}
