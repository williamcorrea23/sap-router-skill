-- Change Order 03: authentication + company-level multi-tenancy.
--
-- Company = tenant. Every data table gains a direct company_id (kept in sync
-- by BEFORE INSERT triggers so existing insert paths stay unchanged), RLS is
-- ON everywhere, and example workspaces (kind = 'example') are globally
-- readable but writable by no one. The server (pg over DATABASE_URL, table
-- owner) bypasses RLS and enforces company membership in app code — RLS is
-- the second, independent line of defense for anon-key access.

-- ---------------------------------------------------------------------------
-- Identity tables
-- ---------------------------------------------------------------------------

create table companies (
  id         uuid primary key default gen_random_uuid(),
  name       text not null unique,
  created_at timestamptz not null default now()
);

create table profiles (
  user_id      uuid primary key references auth.users(id) on delete cascade,
  company_id   uuid not null references companies(id) on delete cascade,
  display_name text not null default '',
  role         text not null default 'member' check (role in ('admin', 'member')),
  created_at   timestamptz not null default now()
);
create index profiles_company on profiles (company_id);

create table invitations (
  id          uuid primary key default gen_random_uuid(),
  company_id  uuid not null references companies(id) on delete cascade,
  email       text not null,
  role        text not null default 'member' check (role in ('admin', 'member')),
  invited_by  uuid references auth.users(id) on delete set null,
  token       text not null unique,
  expires_at  timestamptz not null,
  accepted_at timestamptz,
  created_at  timestamptz not null default now()
);
create index invitations_company on invitations (company_id, created_at desc);
create index invitations_token on invitations (token);

-- ---------------------------------------------------------------------------
-- company_id on every data table (direct column, backfilled, trigger-filled)
-- ---------------------------------------------------------------------------

alter table workspaces      add column company_id uuid references companies(id) on delete cascade;
alter table objects         add column company_id uuid references companies(id) on delete cascade;
alter table call_edges      add column company_id uuid references companies(id) on delete cascade;
alter table table_accesses  add column company_id uuid references companies(id) on delete cascade;
alter table usage_stats     add column company_id uuid references companies(id) on delete cascade;
alter table findings        add column company_id uuid references companies(id) on delete cascade;
alter table report_runs     add column company_id uuid references companies(id) on delete cascade;
alter table chat_sessions   add column company_id uuid references companies(id) on delete cascade;
alter table chat_messages   add column company_id uuid references companies(id) on delete cascade;
alter table ingestion_jobs  add column company_id uuid references companies(id) on delete cascade;
alter table traces          add column company_id uuid references companies(id) on delete cascade;

-- Chat sessions are per-user within the company (sidebar: own history by
-- default, read-only "All company chats" toggle). Removing a member keeps
-- their past chats (created_by goes null).
alter table chat_sessions add column created_by uuid references auth.users(id) on delete set null;
create index chat_sessions_company_user on chat_sessions (company_id, created_by, updated_at desc);

-- Existing (operator-seeded) workspaces belong to the designated operator
-- company; they stay globally readable through kind = 'example'.
insert into companies (name) values ('Operator (examples)');

update workspaces set company_id = (select id from companies where name = 'Operator (examples)')
  where company_id is null;

update objects        t set company_id = w.company_id from workspaces w where t.workspace_id = w.id and t.company_id is null;
update call_edges     t set company_id = w.company_id from workspaces w where t.workspace_id = w.id and t.company_id is null;
update table_accesses t set company_id = w.company_id from workspaces w where t.workspace_id = w.id and t.company_id is null;
update usage_stats    t set company_id = w.company_id from workspaces w where t.workspace_id = w.id and t.company_id is null;
update findings       t set company_id = w.company_id from workspaces w where t.workspace_id = w.id and t.company_id is null;
update report_runs    t set company_id = w.company_id from workspaces w where t.workspace_id = w.id and t.company_id is null;
update chat_sessions  t set company_id = w.company_id from workspaces w where t.workspace_id = w.id and t.company_id is null;
update chat_messages  m set company_id = s.company_id from chat_sessions s where m.session_id = s.id and m.company_id is null;
update traces         t set company_id = w.company_id from workspaces w where t.workspace_id = w.id and t.company_id is null;

-- Workspaces must always have an owner company from here on.
alter table workspaces alter column company_id set not null;

-- Insert-path compatibility: any row inserted without an explicit company_id
-- inherits it from its workspace (or, for chat messages, its session). App
-- code may still set company_id explicitly (e.g. chat sessions on example
-- workspaces belong to the chatting user's company, not the operator company).
create or replace function public.fill_company_from_workspace() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if new.company_id is null and new.workspace_id is not null then
    select company_id into new.company_id from workspaces where id = new.workspace_id;
  end if;
  return new;
end;
$$;

create or replace function public.fill_company_from_session() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if new.company_id is null then
    select company_id into new.company_id from chat_sessions where id = new.session_id;
  end if;
  return new;
end;
$$;

create trigger fill_company before insert on objects        for each row execute function public.fill_company_from_workspace();
create trigger fill_company before insert on call_edges     for each row execute function public.fill_company_from_workspace();
create trigger fill_company before insert on table_accesses for each row execute function public.fill_company_from_workspace();
create trigger fill_company before insert on usage_stats    for each row execute function public.fill_company_from_workspace();
create trigger fill_company before insert on findings       for each row execute function public.fill_company_from_workspace();
create trigger fill_company before insert on report_runs    for each row execute function public.fill_company_from_workspace();
create trigger fill_company before insert on chat_sessions  for each row execute function public.fill_company_from_workspace();
create trigger fill_company before insert on traces         for each row execute function public.fill_company_from_workspace();
create trigger fill_company before insert on chat_messages  for each row execute function public.fill_company_from_session();

-- ---------------------------------------------------------------------------
-- RLS helpers (security definer: run as owner, so no policy recursion)
-- ---------------------------------------------------------------------------

create or replace function public.current_company_id() returns uuid
language sql stable security definer set search_path = public as
$$ select company_id from profiles where user_id = auth.uid() $$;

create or replace function public.is_company_admin() returns boolean
language sql stable security definer set search_path = public as
$$ select exists (select 1 from profiles where user_id = auth.uid() and role = 'admin') $$;

create or replace function public.is_example_workspace(ws uuid) returns boolean
language sql stable security definer set search_path = public as
$$ select exists (select 1 from workspaces w where w.id = ws and w.kind = 'example') $$;

-- ---------------------------------------------------------------------------
-- Row Level Security — ON for every table. Policies target the authenticated
-- role (anon gets nothing anywhere). Tables with no write policy are
-- read-only (or fully closed) for API-key access; the server writes as owner.
-- ---------------------------------------------------------------------------

alter table companies             enable row level security;
alter table profiles              enable row level security;
alter table invitations           enable row level security;
alter table workspaces            enable row level security;
alter table objects               enable row level security;
alter table call_edges            enable row level security;
alter table table_accesses        enable row level security;
alter table usage_stats           enable row level security;
alter table findings              enable row level security;
alter table report_runs           enable row level security;
alter table chat_sessions         enable row level security;
alter table chat_messages         enable row level security;
alter table ingestion_jobs        enable row level security;
alter table traces                enable row level security;
alter table incompatibility_rules enable row level security;
alter table suppression_rules     enable row level security;
alter table schema_migrations     enable row level security;  -- no policies: closed

create policy companies_select on companies for select to authenticated
  using (id = public.current_company_id());

create policy profiles_select on profiles for select to authenticated
  using (company_id = public.current_company_id() or user_id = auth.uid());
create policy profiles_update_own on profiles for update to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());
-- Only the display name is user-editable; role/company changes go through
-- the server (service role / owner connection).
revoke update on profiles from authenticated;
grant update (display_name) on profiles to authenticated;

create policy invitations_admin on invitations for all to authenticated
  using (company_id = public.current_company_id() and public.is_company_admin())
  with check (company_id = public.current_company_id() and public.is_company_admin());

create policy workspaces_select on workspaces for select to authenticated
  using (kind = 'example' or company_id = public.current_company_id());
create policy workspaces_insert on workspaces for insert to authenticated
  with check (company_id = public.current_company_id() and kind = 'ingested');
create policy workspaces_update on workspaces for update to authenticated
  using (company_id = public.current_company_id() and kind = 'ingested')
  with check (company_id = public.current_company_id() and kind = 'ingested');
create policy workspaces_delete on workspaces for delete to authenticated
  using (company_id = public.current_company_id() and kind = 'ingested'
         and public.is_company_admin());

-- Analysis data: readable within the company plus everyone's example
-- workspaces; never writable through the API keys (server-only writes).
create policy objects_select on objects for select to authenticated
  using (company_id = public.current_company_id() or public.is_example_workspace(workspace_id));
create policy call_edges_select on call_edges for select to authenticated
  using (company_id = public.current_company_id() or public.is_example_workspace(workspace_id));
create policy table_accesses_select on table_accesses for select to authenticated
  using (company_id = public.current_company_id() or public.is_example_workspace(workspace_id));
create policy usage_stats_select on usage_stats for select to authenticated
  using (company_id = public.current_company_id() or public.is_example_workspace(workspace_id));
create policy findings_select on findings for select to authenticated
  using (company_id = public.current_company_id() or public.is_example_workspace(workspace_id));
create policy report_runs_select on report_runs for select to authenticated
  using (company_id = public.current_company_id() or public.is_example_workspace(workspace_id));

-- Chats: company-visible reads; writes only by the session's creator.
create policy chat_sessions_select on chat_sessions for select to authenticated
  using (company_id = public.current_company_id());
create policy chat_sessions_insert on chat_sessions for insert to authenticated
  with check (company_id = public.current_company_id() and created_by = auth.uid());
create policy chat_sessions_update on chat_sessions for update to authenticated
  using (created_by = auth.uid()) with check (created_by = auth.uid());
create policy chat_sessions_delete on chat_sessions for delete to authenticated
  using (created_by = auth.uid());

create policy chat_messages_select on chat_messages for select to authenticated
  using (company_id = public.current_company_id());
create policy chat_messages_insert on chat_messages for insert to authenticated
  with check (company_id = public.current_company_id()
              and exists (select 1 from chat_sessions s
                          where s.id = session_id and s.created_by = auth.uid()));

create policy ingestion_jobs_select on ingestion_jobs for select to authenticated
  using (company_id = public.current_company_id());

create policy traces_select on traces for select to authenticated
  using (company_id = public.current_company_id());

-- Global reference data: read-only for any signed-in user.
create policy rules_select on incompatibility_rules for select to authenticated using (true);
create policy suppression_select on suppression_rules for select to authenticated using (true);
