REPORT zgm_daily_movement_report.

"* Daily goods-movement reconciliation: compares the custom audit log
"* (ZGM_MOVEMENT_LOG) against the material documents in MKPF/MSEG.

PARAMETERS p_werks TYPE werks_d OBLIGATORY.
PARAMETERS p_budat TYPE budat DEFAULT sy-datum.

TYPES: BEGIN OF ty_line,
         mblnr TYPE mblnr,
         matnr TYPE matnr,
         menge TYPE menge_d,
         bwart TYPE bwart,
       END OF ty_line.

DATA gt_documents TYPE STANDARD TABLE OF ty_line WITH DEFAULT KEY.
DATA gt_log       TYPE STANDARD TABLE OF zgm_movement_log WITH DEFAULT KEY.

START-OF-SELECTION.
  PERFORM load_material_documents.
  PERFORM load_audit_log.
  PERFORM reconcile.

FORM load_material_documents.
  " NOTE: classic MKPF/MSEG join — in S/4HANA both are compatibility views
  " over MATDOC; this join should be replaced by a single MATDOC read.
  SELECT g~mblnr i~matnr i~menge i~bwart
    INTO TABLE gt_documents
    FROM mkpf AS g INNER JOIN mseg AS i
      ON g~mblnr = i~mblnr AND g~mjahr = i~mjahr
    WHERE g~budat = p_budat
      AND i~werks = p_werks.
ENDFORM.

FORM load_audit_log.
  SELECT * FROM zgm_movement_log
    INTO TABLE gt_log
    WHERE werks = p_werks.
ENDFORM.

FORM reconcile.
  DATA lo_reader TYPE REF TO zcl_gm_stock_reader.
  DATA lv_missing TYPE i.

  CREATE OBJECT lo_reader.
  DATA(lv_total) = lo_reader->count_movements_today( p_werks ).

  LOOP AT gt_log INTO DATA(ls_log).
    READ TABLE gt_documents TRANSPORTING NO FIELDS
      WITH KEY mblnr = ls_log-mblnr.
    IF sy-subrc <> 0.
      lv_missing = lv_missing + 1.
      WRITE: / 'Logged movement without material document:', ls_log-ticket_id.
    ENDIF.
  ENDLOOP.

  WRITE: / 'Documents today:', lv_total.
  WRITE: / 'Log entries without document:', lv_missing.
ENDFORM.
