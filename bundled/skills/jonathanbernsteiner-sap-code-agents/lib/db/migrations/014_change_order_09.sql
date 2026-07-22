-- Change Order 09 (Part 1): deterministic per-object dispositions.
--
-- The consultant deliverable: every object gets a recommended disposition,
-- derived exclusively from data the system already computes — never
-- LLM-assigned. Precedence:
--   retire   — retirement candidate (zero executions in 24 months, no inbound
--              references from other objects, usage data present). Retirement
--              wins over any grade: dead code is deleted, not fixed.
--   redesign — grade D (severity-high Tier-1 finding: construct removed)
--   adapt    — grade C (Tier-1 findings, compatibility-view class)
--   review   — grade B (Tier-2 findings only: expert confirmation needed)
--   keep     — grade A (no Tier-1/Tier-2 findings)
--   null     — ungraded (no finished report run yet)
-- security_invoker: anon-key access goes through the underlying tables' RLS.
create view object_dispositions with (security_invoker = true) as
select
  g.object_id,
  g.workspace_id,
  g.company_id,
  g.grade,
  (u.object_id is not null
   and u.call_count_24m = 0
   and not exists (select 1 from call_edges e
                   where e.workspace_id = g.workspace_id
                     and e.callee_id = g.object_id
                     and e.caller_id <> g.object_id)) as is_retirement_candidate,
  case
    when u.object_id is not null
         and u.call_count_24m = 0
         and not exists (select 1 from call_edges e
                         where e.workspace_id = g.workspace_id
                           and e.callee_id = g.object_id
                           and e.caller_id <> g.object_id)
      then 'retire'
    when g.grade = 'D' then 'redesign'
    when g.grade = 'C' then 'adapt'
    when g.grade = 'B' then 'review'
    when g.grade = 'A' then 'keep'
    else null
  end as disposition
from object_risk_grades g
left join usage_stats u on u.object_id = g.object_id;
