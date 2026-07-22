"! Read-only stock and movement lookups used by the daily report.
CLASS zcl_gm_stock_reader DEFINITION PUBLIC FINAL CREATE PUBLIC.

  PUBLIC SECTION.
    TYPES: BEGIN OF ty_stock,
             matnr TYPE matnr,
             werks TYPE werks_d,
             lgort TYPE lgort_d,
             labst TYPE labst,
           END OF ty_stock.
    TYPES ty_stocks TYPE STANDARD TABLE OF ty_stock WITH DEFAULT KEY.

    METHODS get_unrestricted_stock
      IMPORTING
        iv_matnr TYPE matnr
        iv_werks TYPE werks_d
      RETURNING
        VALUE(rt_stock) TYPE ty_stocks.

    METHODS count_movements_today
      IMPORTING
        iv_werks TYPE werks_d
      RETURNING
        VALUE(rv_count) TYPE i.

ENDCLASS.

CLASS zcl_gm_stock_reader IMPLEMENTATION.

  METHOD get_unrestricted_stock.
    SELECT matnr werks lgort labst FROM mard
      INTO TABLE rt_stock
      WHERE matnr = iv_matnr
        AND werks = iv_werks.
  ENDMETHOD.

  METHOD count_movements_today.
    " NOTE: counts line items in the classic MSEG table; in S/4HANA this is a
    " compatibility view over MATDOC and this aggregate belongs on MATDOC.
    SELECT COUNT(*) FROM mseg
      INTO rv_count
      WHERE werks = iv_werks
        AND budat_mkpf = sy-datum.
  ENDMETHOD.

ENDCLASS.
