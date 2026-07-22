-- Report restructure: every finished report run freezes its numbers.
--
--  snapshot           jsonb — grade distribution, usage coverage, category
--                      counts, tier counts, retirement candidates: computed by
--                      SQL at the end of the run (lib/report/summary.ts) and
--                      never recomputed, so the report and its run history
--                      keep stating what was true when the run finished.
--  executive_summary  text — 3–4 sentences of generated prose whose numbers
--                      are injected from the snapshot (traced LLM call with a
--                      deterministic numeric guard + fallback; never a source
--                      of numbers itself).
alter table report_runs
  add column executive_summary text,
  add column snapshot jsonb;

-- Backfill: freeze a snapshot for each workspace's LATEST finished run from
-- the current tables (findings only exist for the latest run, so this is the
-- exact data those reports render today). Older runs keep snapshot = null —
-- the run history shows their timing/status only. executive_summary stays
-- null (needs an LLM); readers fall back to the deterministic template.
with latest as (
  select distinct on (workspace_id) id, workspace_id
  from report_runs
  where finished_at is not null
  order by workspace_id, finished_at desc
)
update report_runs r
set snapshot = jsonb_build_object(
  'total_objects', (select count(*) from objects o where o.workspace_id = r.workspace_id),
  'parse_ok', (select count(*) from objects o where o.workspace_id = r.workspace_id and o.parse_status = 'ok'),
  'tiers', jsonb_build_object(
    '1', (select count(*) from findings f where f.run_id = r.id and f.tier = 1 and not f.suppressed),
    '2', (select count(*) from findings f where f.run_id = r.id and f.tier = 2 and not f.suppressed),
    '3', (select count(*) from findings f where f.run_id = r.id and f.tier = 3 and not f.suppressed)),
  'affected_objects', (select count(distinct f.object_id) from findings f
                       where f.run_id = r.id and f.tier in (1, 2) and not f.suppressed),
  'grades', (select coalesce(jsonb_object_agg(g.grade, g.n), '{}'::jsonb)
             from (select og.grade, count(*) as n
                   from object_risk_grades og
                   where og.workspace_id = r.workspace_id and og.grade is not null
                   group by og.grade) g),
  'usage', jsonb_build_object(
    'rows', (select count(*) from usage_stats u where u.workspace_id = r.workspace_id),
    'coverage_pct', (select case when count(o.id) = 0 then 0
                            else round(100.0 * (select count(*) from usage_stats u where u.workspace_id = r.workspace_id)
                                       / count(o.id))
                            end
                     from objects o where o.workspace_id = r.workspace_id),
    'simulated', (select w.simulated_usage from workspaces w where w.id = r.workspace_id)),
  'categories', (select coalesce(jsonb_agg(jsonb_build_object('category', c.category, 'n', c.n)
                                           order by c.n desc, c.category), '[]'::jsonb)
                 from (select o.category, count(*) as n
                       from objects o where o.workspace_id = r.workspace_id
                       group by o.category) c),
  'retirement_candidates',
    case when (select count(*) from usage_stats u where u.workspace_id = r.workspace_id) = 0 then null
         else (select count(*) from usage_stats u
               where u.workspace_id = r.workspace_id and u.call_count_24m = 0
                 and not exists (select 1 from call_edges e
                                 where e.workspace_id = r.workspace_id
                                   and e.callee_id = u.object_id and e.caller_id <> u.object_id))
    end)
where r.id in (select id from latest);
