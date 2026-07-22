-- Change Order 07 — rule source layer (knowledge inspectability).
-- source_excerpt: short verbatim quote from the rule's public source, curated
--   and human-approved at seeding time; never generated from model memory.
-- remediation_effort / effort_rationale: seeded reference data, same trust
--   model as severity — a deterministic effort band per rule, never per-object
--   estimates and never LLM-assigned.
-- verified_release: the S/4HANA release documentation set the rule's
--   note-to-topic association was last checked against.
alter table incompatibility_rules
  add column if not exists source_excerpt text,
  add column if not exists excerpt_source_url text,
  add column if not exists remediation_effort text
    check (remediation_effort in ('low', 'medium', 'high')),
  add column if not exists effort_rationale text,
  add column if not exists verified_release text;
