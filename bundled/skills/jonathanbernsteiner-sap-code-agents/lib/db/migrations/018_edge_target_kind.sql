-- Edge target classification, decided at extraction time and stored — never
-- guessed at render time from "does an object with this name exist?".
--   internal  = defined in the caller's own compilation unit (FORMs, local
--               classes, own-group function modules) — implementation detail,
--               not a dependency
--   workspace = resolves to another ingested object
--   external  = does not resolve within the system (SAP standard or missing)
-- Table accesses stay in table_accesses (their own edge class).
-- Null = legacy row awaiting scripts/backfill-target-kind.ts (derived from
-- stored source, so existing systems correct without re-ingesting).
alter table call_edges add column if not exists target_kind text
  check (target_kind in ('internal', 'workspace', 'external'));

create index if not exists call_edges_target_kind
  on call_edges (workspace_id, target_kind);
