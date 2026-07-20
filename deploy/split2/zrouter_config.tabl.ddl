// ZROUTER_CONFIG -- action config registry read by ZCL_ZROUTER_CONFIG.
// SELECT module, action, active, batchable, timeout FROM zrouter_config WHERE client = @sy-mandt.
// dataMaintenance ALLOWED so rows can be seeded/maintained via SM30.
@EndUserText.label : 'ZROUTER Action Config Registry'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #ALLOWED
define table zrouter_config {
  key client    : abap.clnt not null;
  key module    : abap.char(10) not null;
  key action    : abap.char(40) not null;
  active        : abap.char(1);
  batchable     : abap.char(1);
  timeout       : abap.int4;
}
