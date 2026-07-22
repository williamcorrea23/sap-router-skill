-- Change Order 06 (Part 3): pipeline stage visualization.
--
-- Ingestion gains a distinct 'graph' status (the job processor already runs
-- graph-building as its own step inside the parse invocation); report runs
-- gain a persisted stage + live counters so the UI can render the
-- analyze → validate → deliver pipeline. All values are job counters —
-- never LLM output.

alter table ingestion_jobs drop constraint ingestion_jobs_status_check;
alter table ingestion_jobs add constraint ingestion_jobs_status_check
  check (status in ('queued', 'cloning', 'parsing', 'graph', 'summarizing', 'ready', 'failed'));

alter table report_runs
  add column stage text not null default 'queued'
    check (stage in ('queued', 'analyzing', 'validating', 'rendering', 'done', 'failed')),
  -- live "n of m objects" for the analyze stage (m = the pass's scope)
  add column objects_done  int not null default 0,
  add column analyze_total int,
  add column error         text;

-- Backfill history: finished runs are done; unfinished ones are dead workers.
-- Failed runs never receive finished_at, so the object_risk_grades view keeps
-- grading from the latest successful run only.
update report_runs set stage = 'done' where finished_at is not null;
update report_runs set stage = 'failed', error = 'no stage recorded (run predates Change Order 06 and never finished)'
  where finished_at is null;
