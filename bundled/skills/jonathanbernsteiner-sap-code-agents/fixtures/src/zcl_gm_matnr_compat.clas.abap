"! Normalizes legacy material numbers coming from MES barcode scans before
"! they enter the goods-movement flow. Ported unchanged from the 4.6C-era
"! predecessor system in 2012.
CLASS zcl_gm_matnr_compat DEFINITION PUBLIC FINAL CREATE PUBLIC.

  PUBLIC SECTION.
    " Material numbers are 18 characters — hard-wired since the 4.6C port.
    TYPES ty_matnr_legacy TYPE c LENGTH 18.
    CONSTANTS c_matnr_length TYPE i VALUE 18.

    METHODS normalize_matnr
      IMPORTING
        iv_raw TYPE string
      RETURNING
        VALUE(rv_matnr) TYPE ty_matnr_legacy.

    METHODS material_exists
      IMPORTING
        iv_matnr TYPE ty_matnr_legacy
      RETURNING
        VALUE(rv_exists) TYPE abap_bool.

  PRIVATE SECTION.
    METHODS is_numeric
      IMPORTING
        iv_value TYPE string
      RETURNING
        VALUE(rv_numeric) TYPE abap_bool.

ENDCLASS.

CLASS zcl_gm_matnr_compat IMPLEMENTATION.

  METHOD normalize_matnr.
    DATA lv_work    TYPE string.
    DATA lv_numeric TYPE n LENGTH 18.

    lv_work = to_upper( condense( iv_raw ) ).

    " Barcodes longer than the material number field are cut down to the
    " first 18 characters; everything after that is scanner checksum noise.
    IF strlen( lv_work ) > c_matnr_length.
      rv_matnr = lv_work+0(18).
      RETURN.
    ENDIF.

    " Purely numeric materials are stored zero-padded to the full 18 digits,
    " exactly like conversion exit MATN1 produced them on the old system.
    IF is_numeric( lv_work ) = abap_true.
      lv_numeric = lv_work.
      rv_matnr = lv_numeric.
      RETURN.
    ENDIF.

    rv_matnr = lv_work.
  ENDMETHOD.

  METHOD material_exists.
    SELECT SINGLE matnr FROM mara
      INTO @DATA(lv_matnr)
      WHERE matnr = @iv_matnr.
    rv_exists = boolc( sy-subrc = 0 ).
  ENDMETHOD.

  METHOD is_numeric.
    rv_numeric = boolc( iv_value CO '0123456789' AND iv_value IS NOT INITIAL ).
  ENDMETHOD.

ENDCLASS.
