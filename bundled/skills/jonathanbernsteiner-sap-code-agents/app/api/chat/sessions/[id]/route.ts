/**
 * One chat session: GET → full transcript (company-visible, so colleagues
 * can read each other's chats), DELETE → creator only.
 */
import { NextRequest } from "next/server";
import { requireUser } from "../../../../../lib/auth/server";
import { query } from "../../../../../lib/db/client";
import { deleteSession, getMessages, getSession } from "../../../../../lib/chat/store";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest, ctx: { params: Promise<{ id: string }> }) {
  const auth = await requireUser(req);
  if (auth instanceof Response) return auth;
  const { id } = await ctx.params;
  const session = await getSession(id);
  if (!session || session.company_id !== auth.companyId) {
    return Response.json({ error: "session not found" }, { status: 404 });
  }
  const [wsRows, messages] = await Promise.all([
    query<{ name: string }>(`select name from workspaces where id = $1`, [session.workspace_id]),
    getMessages(session.id),
  ]);
  return Response.json({
    session: {
      id: session.id,
      title: session.title,
      workspace: wsRows[0]?.name,
      is_mine: session.created_by === auth.userId,
      created_at: session.created_at,
      updated_at: session.updated_at,
    },
    messages: messages.map((m) => ({
      id: m.id,
      role: m.role,
      content_md: m.content_md,
      tool_calls: m.tool_calls_json,
      trace_id: m.trace_id,
      created_at: m.created_at,
    })),
  });
}

export async function DELETE(req: NextRequest, ctx: { params: Promise<{ id: string }> }) {
  const auth = await requireUser(req);
  if (auth instanceof Response) return auth;
  const { id } = await ctx.params;
  const session = await getSession(id);
  if (!session || session.company_id !== auth.companyId) {
    return Response.json({ error: "session not found" }, { status: 404 });
  }
  const deleted = await deleteSession(id, auth.userId);
  if (!deleted) {
    return Response.json({ error: "only the session's creator can delete it" }, { status: 403 });
  }
  return Response.json({ deleted: true });
}
