-- Change Order 01: report quality (A2 suppression list, A4 report runs,
-- A6 note verification status) + in-app ingestion (B1 jobs, workspace kind).

-- A2 — known-false-positive suppression list. Data, not code: a new
-- false-positive class is one INSERT. kind='regex' rules apply their
-- case-insensitive pattern to the finding's title + detail; kind='category'
-- rules activate a coded check in lib/report/suppress.ts by category id.
create table suppression_rules (
  id         text primary key,
  kind       text not null check (kind in ('regex', 'category')),
  pattern    text,
  category   text,
  reason     text not null,
  created_at timestamptz not null default now()
);

insert into suppression_rules (id, kind, pattern, category, reason) values
  (
    'werks-field-length',
    'regex',
    '(\bwerks\b|\bplant\b[^.]*\bfield\b)[^.]*\b(length|char|size|width)\b|\b(length|char|size|width)\b[^.]*\bwerks\b',
    null,
    'WERKS (plant) is CHAR 4 in both ECC and S/4HANA — the field length is unchanged. Any field-length observation on WERKS is a known false positive.'
  ),
  (
    'non-matnr-field-length',
    'category',
    null,
    'non-matnr-field-length',
    'Field-length claims are only actionable for MATNR (extended to 40 chars in S/4HANA) unless the finding is tied to a seeded incompatibility rule. Length observations on other fields (e.g. amount fields cited against plain table declarations) are a known false-positive class.'
  );

-- Findings: suppression flags + the report run they belong to.
alter table findings
  add column suppressed boolean not null default false,
  add column suppression_reason text,
  add column run_id uuid;

-- A4 — one row per report generation; exports cite id + timing.
create table report_runs (
  id               uuid primary key default gen_random_uuid(),
  workspace_id     uuid not null references workspaces(id) on delete cascade,
  started_at       timestamptz not null default now(),
  finished_at      timestamptz,
  llm_pass         boolean not null default true,
  objects_analyzed int
);

alter table findings
  add constraint findings_run_fk foreign key (run_id)
    references report_runs(id) on delete cascade;

-- A6 — SAP Note verification is data: reports may render a note number only
-- when the rule's source has been explicitly web-verified.
alter table incompatibility_rules
  add column source_status text not null default 'unverified'
    check (source_status in ('unverified', 'verified')),
  add column verified_at timestamptz;

-- B1 — ingestion jobs, processed in chunks by serverless invocations that
-- re-queue themselves; the progress screen polls this row.
create table ingestion_jobs (
  id                uuid primary key default gen_random_uuid(),
  git_url           text not null,
  workspace_name    text not null,
  status            text not null default 'queued'
    check (status in ('queued', 'cloning', 'parsing', 'summarizing', 'ready', 'failed')),
  error             text,
  files_total       int,
  files_parsed      int,
  objects_total     int,
  edges_total       int,
  summaries_planned int,
  summaries_done    int not null default 0,
  workspace_id      uuid references workspaces(id) on delete set null,
  -- chunk lease: a worker invocation holds this while processing; a stale
  -- lease means the worker died and the job may be picked up again
  lease_expires_at  timestamptz,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now()
);
create index ingestion_jobs_status on ingestion_jobs (status, created_at);

-- B3 — example workspaces vs user-ingested ones (badging + delete policy).
alter table workspaces
  add column kind text not null default 'example'
    check (kind in ('example', 'ingested'));
