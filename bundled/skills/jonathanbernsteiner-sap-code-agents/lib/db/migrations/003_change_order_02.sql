-- Change Order 02: persistent chat sessions per workspace.

create table chat_sessions (
  id           uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references workspaces(id) on delete cascade,
  title        text not null,
  -- rolling summary of messages that fell out of the 20-message context
  -- window, regenerated via one traced LLM call when the window slides
  context_note text,
  -- how many of the oldest messages context_note covers
  context_note_covers int not null default 0,
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);
create index chat_sessions_ws_updated on chat_sessions (workspace_id, updated_at desc);

create table chat_messages (
  id              uuid primary key default gen_random_uuid(),
  session_id      uuid not null references chat_sessions(id) on delete cascade,
  role            text not null check (role in ('user', 'assistant')),
  content_md      text not null,
  -- [{name, input, duration_ms, at}] — `at` is the char offset in content_md
  -- where the call happened, so reopened transcripts re-render the rows inline
  tool_calls_json jsonb not null default '[]',
  trace_id        bigint references traces(id) on delete set null,
  created_at      timestamptz not null default now()
);
create index chat_messages_session on chat_messages (session_id, created_at);
