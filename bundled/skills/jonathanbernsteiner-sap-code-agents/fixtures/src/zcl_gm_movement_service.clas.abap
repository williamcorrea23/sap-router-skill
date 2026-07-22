"! Core goods-movement service: turns unprocessed scale tickets into goods
"! movements via BAPI_GOODSMVT_CREATE and writes the custom audit log.
CLASS zcl_gm_movement_service DEFINITION PUBLIC FINAL CREATE PUBLIC.

  PUBLIC SECTION.
    METHODS process_open_tickets
      IMPORTING
        iv_werks TYPE werks_d
      RETURNING
        VALUE(rv_posted) TYPE i.

    METHODS verify_material_document
      IMPORTING
        iv_mblnr TYPE mblnr
        iv_mjahr TYPE mjahr
      RETURNING
        VALUE(rv_exists) TYPE abap_bool.

  PRIVATE SECTION.
    METHODS post_movement
      IMPORTING
        is_ticket TYPE zgm_scale_ticket
      RETURNING
        VALUE(rv_mblnr) TYPE mblnr.

    METHODS write_log
      IMPORTING
        is_ticket TYPE zgm_scale_ticket
        iv_mblnr  TYPE mblnr.

ENDCLASS.

CLASS zcl_gm_movement_service IMPLEMENTATION.

  METHOD process_open_tickets.
    DATA lt_tickets TYPE STANDARD TABLE OF zgm_scale_ticket WITH DEFAULT KEY.

    rv_posted = 0.
    SELECT * FROM zgm_scale_ticket
      INTO TABLE lt_tickets
      WHERE werks = iv_werks
        AND processed = abap_false.

    LOOP AT lt_tickets INTO DATA(ls_ticket).
      " material must exist and not be flagged for deletion
      SELECT SINGLE matnr FROM mara
        INTO @DATA(lv_matnr)
        WHERE matnr = @ls_ticket-matnr
          AND lvorm = @abap_false.
      IF sy-subrc <> 0.
        CONTINUE.
      ENDIF.

      DATA(lv_mblnr) = post_movement( ls_ticket ).
      IF lv_mblnr IS NOT INITIAL.
        write_log( is_ticket = ls_ticket iv_mblnr = lv_mblnr ).
        ls_ticket-processed = abap_true.
        MODIFY zgm_scale_ticket FROM ls_ticket.
        rv_posted = rv_posted + 1.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD post_movement.
    DATA ls_header  TYPE bapi2017_gm_head_01.
    DATA ls_code    TYPE bapi2017_gm_code.
    DATA lt_items   TYPE STANDARD TABLE OF bapi2017_gm_item_create WITH DEFAULT KEY.
    DATA lt_return  TYPE STANDARD TABLE OF bapiret2 WITH DEFAULT KEY.
    DATA ls_headret TYPE bapi2017_gm_head_ret.

    ls_header-pstng_date = sy-datum.
    ls_header-doc_date   = sy-datum.
    ls_code-gm_code      = '05'.

    APPEND VALUE #( material  = is_ticket-matnr
                    plant     = is_ticket-werks
                    move_type = zif_gm_movement_types=>c_bwart_goods_receipt
                    entry_qnt = is_ticket-gross_weight - is_ticket-tare_weight
                    entry_uom = 'KG' ) TO lt_items.

    CALL FUNCTION 'BAPI_GOODSMVT_CREATE'
      EXPORTING
        goodsmvt_header  = ls_header
        goodsmvt_code    = ls_code
      IMPORTING
        goodsmvt_headret = ls_headret
      TABLES
        goodsmvt_item    = lt_items
        return           = lt_return.

    READ TABLE lt_return TRANSPORTING NO FIELDS WITH KEY type = 'E'.
    IF sy-subrc = 0.
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      CLEAR rv_mblnr.
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT'
        EXPORTING
          wait = 'X'.
      rv_mblnr = ls_headret-mat_doc.
    ENDIF.
  ENDMETHOD.

  METHOD verify_material_document.
    " NOTE: direct read of the classic material document header table.
    " In S/4HANA MKPF is a compatibility view over MATDOC.
    SELECT SINGLE mblnr FROM mkpf
      INTO @DATA(lv_mblnr)
      WHERE mblnr = @iv_mblnr
        AND mjahr = @iv_mjahr.
    rv_exists = boolc( sy-subrc = 0 ).
  ENDMETHOD.

  METHOD write_log.
    DATA ls_log TYPE zgm_movement_log.

    TRY.
        ls_log-log_id = cl_system_uuid=>create_uuid_x16_static( ).
      CATCH cx_uuid_error.
        RETURN.
    ENDTRY.
    ls_log-ticket_id = is_ticket-ticket_id.
    ls_log-matnr     = is_ticket-matnr.
    ls_log-werks     = is_ticket-werks.
    ls_log-bwart     = zif_gm_movement_types=>c_bwart_goods_receipt.
    ls_log-menge     = is_ticket-gross_weight - is_ticket-tare_weight.
    ls_log-mblnr     = iv_mblnr.
    GET TIME STAMP FIELD ls_log-posted_at.
    INSERT zgm_movement_log FROM ls_log.
  ENDMETHOD.

ENDCLASS.
