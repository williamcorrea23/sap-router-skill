@EndUserText.label : 'YFG SBDC Session'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table ysbdc_session {
  key client      : abap.clnt not null;
  key session_id  : sysuuid_c32 not null;
  tcode           : abap.char(20);
  recording_name  : abap.char(80);
  bdcdata_json    : abap.string;
  created_by      : abap.char(12);
  created_at      : abap.timestampl;
  last_used       : abap.timestampl;
}
