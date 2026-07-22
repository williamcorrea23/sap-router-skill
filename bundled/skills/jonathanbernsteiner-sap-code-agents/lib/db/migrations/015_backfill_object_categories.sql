-- Backfill object categories for ingested workspaces. Categories previously
-- came only from the fixture manifest, so GitHub-ingested objects were all
-- Uncategorized. Same deterministic mapping as deriveCategory() in
-- lib/ingest/pipeline.ts: type is the source of truth, ZX* programs are
-- user-exit includes (enhancements), unknown types stay null.
update objects
set category = case
  when upper(object_type) in ('ENHO', 'SMOD') then 'enhancement'
  when upper(object_type) = 'PROG' and upper(name) like 'ZX%' then 'enhancement'
  when upper(object_type) in ('CLAS', 'PROG', 'FUGR') then 'abap'
  when upper(object_type) = 'TABL' then 'custom_table'
  when upper(object_type) = 'INTF' then 'interface'
end
where category is null;
