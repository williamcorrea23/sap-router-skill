REPORT zgm_legacy_upload.

"* LEGACY: one-off desktop CSV upload of scale tickets, used during the 2018
"* MES migration. Replaced by the RFC feed (ZCL_GM_SCALE_RFC_STUB). Dead code.

PARAMETERS p_file TYPE c LENGTH 128 LOWER CASE.

TYPES: BEGIN OF ty_raw,
         line TYPE c LENGTH 200,
       END OF ty_raw.

DATA gt_raw TYPE STANDARD TABLE OF ty_raw WITH DEFAULT KEY.

START-OF-SELECTION.
  PERFORM upload_file.
  PERFORM store_tickets.

FORM upload_file.
  DATA lv_filename TYPE string.
  lv_filename = p_file.
  " NOTE: WS_UPLOAD has been obsolete for years; kept verbatim from 2018.
  CALL FUNCTION 'WS_UPLOAD'
    EXPORTING
      filename = lv_filename
      filetype = 'ASC'
    TABLES
      data_tab = gt_raw
    EXCEPTIONS
      OTHERS   = 1.
  IF sy-subrc <> 0.
    WRITE: / 'Upload failed.'.
  ENDIF.
ENDFORM.

FORM store_tickets.
  DATA ls_ticket TYPE zgm_scale_ticket.
  LOOP AT gt_raw INTO DATA(ls_raw).
    SPLIT ls_raw-line AT ';' INTO ls_ticket-ticket_id ls_ticket-matnr ls_ticket-werks.
    GET TIME STAMP FIELD ls_ticket-received_at.
    INSERT zgm_scale_ticket FROM ls_ticket.
  ENDLOOP.
ENDFORM.
