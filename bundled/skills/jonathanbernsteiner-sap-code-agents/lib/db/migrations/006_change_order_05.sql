-- Change Order 05 (Part 2): deterministic process-area tagging.
--
-- table_process_map is seeded reference data (data-as-migration, like
-- suppression_rules): which SAP tables belong to which business process
-- area. Tags are derived per object by joining the parsed table accesses to
-- this map — no LLM classification anywhere; unmapped tables simply produce
-- no tag.

create table table_process_map (
  sap_table          text not null,
  process_area       text not null,
  process_step_order int  not null,
  primary key (sap_table, process_area)
);

insert into table_process_map (sap_table, process_area, process_step_order) values
  -- Purchasing
  ('EKKO', 'Purchasing', 1), ('EKPO', 'Purchasing', 2), ('EKET', 'Purchasing', 3),
  ('EKES', 'Purchasing', 4), ('EBAN', 'Purchasing', 5), ('EINA', 'Purchasing', 6),
  ('EINE', 'Purchasing', 7),
  -- Goods Movement / Inventory
  ('MKPF', 'Goods Movement / Inventory', 1), ('MSEG', 'Goods Movement / Inventory', 2),
  ('MATDOC', 'Goods Movement / Inventory', 3), ('MARD', 'Goods Movement / Inventory', 4),
  ('MCHB', 'Goods Movement / Inventory', 5),
  -- Sales
  ('VBAK', 'Sales', 1), ('VBAP', 'Sales', 2), ('VBEP', 'Sales', 3), ('VBPA', 'Sales', 4),
  ('VBUK', 'Sales', 5), ('VBUP', 'Sales', 6), ('LIKP', 'Sales', 7), ('LIPS', 'Sales', 8),
  ('VBRK', 'Sales', 9), ('VBRP', 'Sales', 10),
  -- Material Master
  ('MARA', 'Material Master', 1), ('MARC', 'Material Master', 2), ('MAKT', 'Material Master', 3),
  ('MARM', 'Material Master', 4), ('MBEW', 'Material Master', 5),
  -- Vendor Master
  ('LFA1', 'Vendor Master', 1), ('LFB1', 'Vendor Master', 2), ('LFM1', 'Vendor Master', 3),
  -- Pricing / Conditions
  ('KONV', 'Pricing / Conditions', 1), ('PRCD_ELEMENTS', 'Pricing / Conditions', 2),
  ('KONH', 'Pricing / Conditions', 3), ('KONP', 'Pricing / Conditions', 4),
  ('A017', 'Pricing / Conditions', 5),
  -- Finance
  ('BKPF', 'Finance', 1), ('BSEG', 'Finance', 2), ('BSID', 'Finance', 3),
  ('BSAD', 'Finance', 4), ('ACDOCA', 'Finance', 5),
  -- Production
  ('AUFK', 'Production', 1), ('AFKO', 'Production', 2), ('AFPO', 'Production', 3),
  ('RESB', 'Production', 4), ('PLAF', 'Production', 5);

-- Global reference data: read-only for any signed-in user (like the rules).
alter table table_process_map enable row level security;
create policy process_map_select on table_process_map for select to authenticated using (true);

-- The per-object EXISTS/array_agg lookups go by object_id alone.
create index table_accesses_object_id on table_accesses (object_id);

-- Distinct process areas per object, derived from parsed table accesses.
-- Objects with no mapped tables get no row (no "Unknown" noise).
-- security_invoker: anon-key access goes through the underlying tables' RLS.
create view object_process_areas with (security_invoker = true) as
select distinct
  ta.object_id,
  ta.workspace_id,
  ta.company_id,
  m.process_area
from table_accesses ta
join table_process_map m on m.sap_table = upper(ta.table_name);

grant select on object_process_areas to authenticated;
grant select on table_process_map to authenticated;
