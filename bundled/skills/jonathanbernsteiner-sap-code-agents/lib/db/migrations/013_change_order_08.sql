-- Change Order 08 — deterministic Tier 2 (root-cause merge).
-- A Tier-2 finding may now carry additional evidence locations: findings on
-- the same object whose claimed tokens overlap merge into one finding with
-- all citations. [{file, line, evidence}, ...]; null for single-citation
-- findings.
alter table findings
  add column if not exists extra_evidence jsonb;
