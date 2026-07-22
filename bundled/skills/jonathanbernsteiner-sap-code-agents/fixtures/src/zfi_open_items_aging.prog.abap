REPORT zfi_open_items_aging.

"* Customer open-item aging list for the credit desk. Reads the classic FI
"* open/cleared item index tables (BSID/BSAD) directly.

PARAMETERS p_bukrs TYPE c LENGTH 4 OBLIGATORY.
PARAMETERS p_stida TYPE d DEFAULT sy-datum.

TYPES: BEGIN OF ty_item,
         kunnr TYPE c LENGTH 10,
         belnr TYPE c LENGTH 10,
         budat TYPE d,
         dmbtr TYPE p LENGTH 13 DECIMALS 2,
       END OF ty_item.

DATA gt_open    TYPE STANDARD TABLE OF ty_item WITH DEFAULT KEY.
DATA gt_cleared TYPE STANDARD TABLE OF ty_item WITH DEFAULT KEY.

START-OF-SELECTION.
  PERFORM load_open_items.
  PERFORM load_cleared_items.
  PERFORM write_aging.

FORM load_open_items.
  " NOTE: BSID is an S/4HANA compatibility view over ACDOCA/BSEG; direct reads
  " are redundant and slow. Replace with ACDOCA or the released CDS views.
  SELECT kunnr belnr budat dmbtr
    INTO TABLE gt_open
    FROM bsid
    WHERE bukrs = p_bukrs
      AND budat <= p_stida.
ENDFORM.

FORM load_cleared_items.
  SELECT kunnr belnr budat dmbtr
    INTO TABLE gt_cleared
    FROM bsad
    WHERE bukrs = p_bukrs
      AND augdt > p_stida.
ENDFORM.

FORM write_aging.
  DATA lv_bucket_30 TYPE p LENGTH 13 DECIMALS 2.
  DATA lv_bucket_60 TYPE p LENGTH 13 DECIMALS 2.
  DATA lv_bucket_90 TYPE p LENGTH 13 DECIMALS 2.

  LOOP AT gt_open INTO DATA(ls_item).
    DATA(lv_age) = p_stida - ls_item-budat.
    IF lv_age <= 30.
      lv_bucket_30 = lv_bucket_30 + ls_item-dmbtr.
    ELSEIF lv_age <= 60.
      lv_bucket_60 = lv_bucket_60 + ls_item-dmbtr.
    ELSE.
      lv_bucket_90 = lv_bucket_90 + ls_item-dmbtr.
    ENDIF.
  ENDLOOP.

  WRITE: / 'Open items:',        lines( gt_open ).
  WRITE: / 'Cleared (late):',    lines( gt_cleared ).
  WRITE: / '0-30 days:',  lv_bucket_30.
  WRITE: / '31-60 days:', lv_bucket_60.
  WRITE: / '> 60 days:',  lv_bucket_90.
ENDFORM.
