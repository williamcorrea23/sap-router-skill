-- Synthetic usage is operator-only again (npm run gen-usage): it was briefly
-- offered as an ingest option, which risked invented execution counts in a
-- real client assessment. The per-job flag is gone from the code (deployed
-- before this migration runs), so the column is dropped.
alter table ingestion_jobs drop column if exists simulated_usage;
