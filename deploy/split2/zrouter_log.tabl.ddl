// ZROUTER_LOG -- action log written by ZCL_ZROUTER_LOGGER (INSERT), read by get_logs.
// Field names match the ABAP struct ZROUTER_LOG used in the logger class.
// RESULT is reserved in DDIC on older NetWeaver (see memory: zrouter-abap-compatibility-fixes),
// so the column is ZRESULT; zcl_zrouter_logger reads it back with "zresult AS result"
// so the external ty_log_entry contract keeps the field name RESULT.
@EndUserText.label : 'ZROUTER Action Log'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrouter_log {
  key client    : abap.clnt not null;
  key guid      : sysuuid_c32 not null;
  module        : abap.char(10);
  action        : abap.char(40);
  status        : abap.char(10);
  message       : abap.string;
  payload       : abap.string;
  zresult       : abap.string;
  username      : abap.char(12);
  timestamp     : abap.timestampl;
}
