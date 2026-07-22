-- Change Order 04 (Part 1): deterministic Migration Risk Grades.
--
-- severity is seeded reference data on incompatibility_rules (maintained in
-- lib/rules/rules.json, like the note-verification status). The scale:
--   high   — the construct is removed outright in S/4HANA (transaction,
--            function module, or functionality no longer available/filled):
--            hard runtime failure or silently wrong results.
--   medium — the data model is replaced but compatibility views cover
--            transitional read access: must be adapted, does not fail
--            immediately.
alter table incompatibility_rules
  add column severity text not null default 'medium'
    check (severity in ('high', 'medium', 'low'));

update incompatibility_rules set severity = 'high'
 where id in ('mb-transactions-migo', 'customer-vendor-business-partner',
              'credit-management-fscm', 'mm-im-classic-goods-movement-fm',
              'sd-rebates-vbox', 'foreign-trade-eikp-eipo');

-- Grade view indexes: latest finished run per workspace + findings by object.
create index report_runs_ws_finished on report_runs (workspace_id, finished_at desc)
  where finished_at is not null;
create index findings_object_run on findings (object_id, run_id, tier);

-- Migration Risk Grade per object, derived exclusively from the persisted
-- findings of the workspace's latest finished report run — a view, so grades
-- recompute automatically per run and can never go stale:
--   D — ≥1 Tier-1 finding from a severity-high rule
--   C — ≥1 Tier-1 finding, none from a severity-high rule
--   B — ≥1 Tier-2 finding, zero Tier-1
--   A — zero Tier-1 and Tier-2 findings
--   null (ungraded) — no finished report run covers this workspace yet;
--                     rendered as a muted "–", never as A.
-- security_invoker: anon-key access goes through the underlying tables' RLS.
create view object_risk_grades with (security_invoker = true) as
select
  o.id as object_id,
  o.workspace_id,
  o.company_id,
  r.id as run_id,
  case
    when r.id is null then null
    when exists (select 1 from findings f
                 join incompatibility_rules ir on ir.id = f.rule_id
                 where f.object_id = o.id and f.run_id = r.id
                   and not f.suppressed and f.tier = 1 and ir.severity = 'high')
      then 'D'
    when exists (select 1 from findings f
                 where f.object_id = o.id and f.run_id = r.id
                   and not f.suppressed and f.tier = 1)
      then 'C'
    when exists (select 1 from findings f
                 where f.object_id = o.id and f.run_id = r.id
                   and not f.suppressed and f.tier = 2)
      then 'B'
    else 'A'
  end as grade
from objects o
left join lateral (
  select rr.id from report_runs rr
  where rr.workspace_id = o.workspace_id and rr.finished_at is not null
  order by rr.finished_at desc
  limit 1
) r on true;

grant select on object_risk_grades to authenticated;
