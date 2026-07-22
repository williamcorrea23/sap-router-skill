-- Core schema (Phase 2): workspaces, objects, call edges, table accesses,
-- usage stats, incompatibility rules, findings, traces.

create extension if not exists pgcrypto;

create table workspaces (
  id          uuid primary key default gen_random_uuid(),
  name        text not null unique,
  source      text not null,
  -- true when usage stats for this workspace are synthetic; every surface
  -- that shows usage numbers must render the label
  simulated_usage boolean not null default false,
  seeded_at   timestamptz not null default now()
);

create table objects (
  id           uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references workspaces(id) on delete cascade,
  name         text not null,
  object_type  text not null,           -- CLAS / INTF / PROG / TABL / FUGR ...
  files        jsonb not null default '[]',
  parse_status text not null check (parse_status in ('ok', 'failed')),
  parse_errors jsonb not null default '[]',
  source       text not null,           -- raw source, kept even on parse failure
  summary      text,                    -- Haiku auto-doc (traced)
  summary_model text,
  category     text,                    -- fixture manifest: abap|enhancement|custom_table|interface
  unique (workspace_id, object_type, name)
);
create index objects_ws_name on objects (workspace_id, name);

create table call_edges (
  id           bigint generated always as identity primary key,
  workspace_id uuid not null references workspaces(id) on delete cascade,
  caller_id    uuid not null references objects(id) on delete cascade,
  -- null when the target is not an object in this workspace (SAP standard or
  -- genuinely unknown) — unresolved names stay visible, never invented
  callee_id    uuid references objects(id) on delete cascade,
  callee_name  text not null,
  kind         text not null check (kind in ('function', 'perform', 'class', 'interface')),
  file         text not null,
  line         int  not null
);
create index call_edges_caller on call_edges (workspace_id, caller_id);
create index call_edges_callee on call_edges (workspace_id, callee_id);
create index call_edges_callee_name on call_edges (workspace_id, callee_name);

create table table_accesses (
  id           bigint generated always as identity primary key,
  workspace_id uuid not null references workspaces(id) on delete cascade,
  object_id    uuid not null references objects(id) on delete cascade,
  op           text not null check (op in ('select', 'insert', 'update', 'modify', 'delete')),
  table_name   text not null,
  dynamic      boolean not null default false,
  file         text not null,
  line         int  not null,
  evidence     text not null            -- verbatim source line
);
create index table_accesses_ws_table on table_accesses (workspace_id, table_name);
create index table_accesses_object on table_accesses (workspace_id, object_id);

create table usage_stats (
  workspace_id  uuid not null references workspaces(id) on delete cascade,
  object_id     uuid not null references objects(id) on delete cascade,
  call_count_24m bigint not null,
  last_executed date,
  simulated     boolean not null,
  primary key (workspace_id, object_id)
);

create table incompatibility_rules (
  id            text primary key,        -- slug, e.g. 'konv-prcd-elements'
  title         text not null,
  description   text not null,
  sap_note      text not null,           -- citation: SAP Note number
  simplification_item text,
  source_url    text,
  detection     jsonb not null,          -- {type: table_access|call_transaction|function_call, ...}
  replacement   text,
  tier1_eligible boolean not null default false
);

create table findings (
  id            bigint generated always as identity primary key,
  workspace_id  uuid not null references workspaces(id) on delete cascade,
  object_id     uuid not null references objects(id) on delete cascade,
  rule_id       text references incompatibility_rules(id),
  tier          smallint not null check (tier in (1, 2, 3)),
  title         text not null,
  detail        text not null,
  evidence_file text,
  evidence_line int,
  evidence      text,                    -- verbatim cited source
  validator     text,                    -- validator id that confirmed a Tier-1 finding
  validator_passed boolean,
  created_at    timestamptz not null default now()
);
create index findings_ws on findings (workspace_id, tier);
create index findings_object on findings (workspace_id, object_id);

create table traces (
  id            bigint generated always as identity primary key,
  workspace_id  uuid references workspaces(id) on delete cascade,
  object_id     uuid references objects(id) on delete cascade,
  kind          text not null,           -- 'summary' | 'agent'
  model         text not null,
  input         jsonb not null,
  output        jsonb not null,
  input_tokens  int,
  output_tokens int,
  duration_ms   int,
  created_at    timestamptz not null default now()
);
create index traces_ws_kind on traces (workspace_id, kind);
