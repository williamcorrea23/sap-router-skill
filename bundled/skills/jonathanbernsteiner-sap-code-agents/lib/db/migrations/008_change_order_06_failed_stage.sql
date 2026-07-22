-- CO-06 follow-up: remember which pipeline stage a report run failed in, so
-- the UI can mark the failing stage card (stage itself becomes 'failed').
alter table report_runs
  add column failed_stage text
    check (failed_stage in ('queued', 'analyzing', 'validating', 'rendering'));
