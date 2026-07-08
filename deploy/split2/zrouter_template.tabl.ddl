@EndUserText.label : 'ZROUTER Template'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrouter_template {
  key client      : abap.clnt not null;
  key module      : abap.char(10) not null;
  key action      : abap.char(40) not null;
  template_name   : abap.char(80);
  template_json   : abap.string;
  created_by      : abap.char(12);
  created_at      : abap.timestampl;
  changed_by      : abap.char(12);
  changed_at      : abap.timestampl;
}
