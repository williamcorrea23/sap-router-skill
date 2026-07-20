// Model template -- transparent table (client + GUID key + audit fields).
// Rename token BATCH -> your object name. Value slots (ZROUTER batch audit) live in
// annotations/comments only, so the raw template is a valid DDL source.
// This repo deploys DDIC via DDL source through scripts/deploy_all.py
// (ADT /ddic/tables/.../source/main). abapGit users obtain the .tabl.xml
// sidecar from one ADT round-trip after the first activation.
@EndUserText.label : 'ZROUTER batch audit'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zbatch_table {
  key client   : abap.clnt not null;
  key guid     : sysuuid_c32 not null;
  module       : abap.char(10);
  action       : abap.char(40);
  status       : abap.char(10);
  payload      : abap.string;
  created_by   : abap.char(12);
  created_at   : abap.timestampl;
}
