-- Ingest-time demo option: generate labeled SIMULATED usage for the ingested
-- workspace. Explicit per-job flag — never applied silently.
alter table ingestion_jobs
  add column if not exists simulated_usage boolean not null default false;
