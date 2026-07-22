REPORT zgm_legacy_mb01_batch.

"* LEGACY (predecessor of ZCL_GM_MOVEMENT_SERVICE): posts goods receipts by
"* batch-input into transaction MB01. Superseded in 2019, kept "just in case".
"* No production runs in over two years.

TYPES: BEGIN OF ty_upload,
         matnr TYPE c LENGTH 18,
         werks TYPE c LENGTH 4,
         menge TYPE c LENGTH 17,
         ebeln TYPE c LENGTH 10,
       END OF ty_upload.

DATA gt_upload TYPE STANDARD TABLE OF ty_upload WITH DEFAULT KEY.
DATA gt_bdc    TYPE STANDARD TABLE OF bdcdata WITH DEFAULT KEY.

START-OF-SELECTION.
  PERFORM build_bdc.
  PERFORM post_all.

FORM add_field USING iv_fnam TYPE clike iv_fval TYPE clike.
  APPEND VALUE bdcdata( fnam = iv_fnam fval = iv_fval ) TO gt_bdc.
ENDFORM.

FORM build_bdc.
  LOOP AT gt_upload INTO DATA(ls_upload).
    APPEND VALUE bdcdata( program = 'SAPMM07M' dynpro = '0200' dynbegin = 'X' ) TO gt_bdc.
    PERFORM add_field USING 'MKPF-BLDAT' sy-datum.
    PERFORM add_field USING 'RM07M-EBELN' ls_upload-ebeln.
    PERFORM add_field USING 'MSEG-MENGE' ls_upload-menge.
  ENDLOOP.
ENDFORM.

FORM post_all.
  " NOTE: MB01 (and MB31) were removed in S/4HANA — replaced by MIGO.
  CALL TRANSACTION 'MB01' USING gt_bdc MODE 'N' UPDATE 'S'.
  IF sy-subrc <> 0.
    CALL TRANSACTION 'MB31' USING gt_bdc MODE 'N' UPDATE 'S'.
  ENDIF.
ENDFORM.
