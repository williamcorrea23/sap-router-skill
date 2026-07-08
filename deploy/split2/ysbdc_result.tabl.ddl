@EndUserText.label : 'YFG SBDC Result'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table ysbdc_result {
  key client      : abap.clnt not null;
  key execution_id : sysuuid_c32 not null;
  session_id      : sysuuid_c32;
  status          : abap.string;
  message         : abap.string;
  executed_at     : abap.timestampl;
  executed_by     : abap.char(12);
}
