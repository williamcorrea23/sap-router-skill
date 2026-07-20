CLASS zcl_zrouter_handler_wm DEFINITION PUBLIC FINAL CREATE PUBLIC
  INHERITING FROM zcl_zrouter_handler_abstract.
  PUBLIC SECTION.
    METHODS constructor
      IMPORTING
        io_logger TYPE REF TO zif_zrouter_logger
        io_config TYPE REF TO zif_zrouter_config.
  PROTECTED SECTION.
    METHODS handle_custom_action REDEFINITION.
  PRIVATE SECTION.
    METHODS goods_movement
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS create_to
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
ENDCLASS.


CLASS zcl_zrouter_handler_wm IMPLEMENTATION.
  METHOD constructor.
    super->constructor( io_logger = io_logger io_config = io_config iv_module = 'WM' ).
  ENDMETHOD.

  METHOD handle_custom_action.
    CASE to_upper( iv_action ).
      WHEN 'GOODS_MOVEMENT'.
        rs_result = goods_movement( iv_payload ).
      WHEN 'CREATE_TO'.
        rs_result = create_to( iv_payload ).
      WHEN OTHERS.
        RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = |Unknown WM action: { iv_action }|.
    ENDCASE.
  ENDMETHOD.

  METHOD goods_movement.
    DATA: ls_header TYPE bapi2017_gm_head_01,
          ls_params TYPE zrouter_wm_gm_params,
          lt_item   TYPE TABLE OF bapi2017_gm_item_create,
          lt_ret    TYPE TABLE OF bapiret2,
          ls_ret    TYPE bapiret2,
          lv_mdoc   TYPE bapi2017_gm_head_01-mat_doc.

    " Parse JSON payload
    /ui2/cl_json=>deserialize(
      EXPORTING json = iv_payload
      CHANGING  data = ls_params ).
    ls_header = CORRESPONDING #( ls_params ).
    IF ls_header-pstng_date IS INITIAL.
      ls_header-pstng_date = sy-datum.
      ls_header-doc_date   = sy-datum.
    ENDIF.

    APPEND INITIAL LINE TO lt_item ASSIGNING FIELD-SYMBOL(<ls_item>).
    IF <ls_item> IS ASSIGNED.
      <ls_item>-material = ls_params-material.
      <ls_item>-plant    = ls_params-plant.
      <ls_item>-stge_loc = ls_params-stor_loc.
      <ls_item>-move_type = ls_params-move_type.
      <ls_item>-entry_qnt = ls_params-quantity.
    ENDIF.

    CALL FUNCTION 'BAPI_GOODSMVT_CREATE'
      EXPORTING
        goodsmvt_header  = ls_header
        goodsmvt_code    = ls_params-gm_code
      IMPORTING
        materialdocument = lv_mdoc
      TABLES
        goodsmvt_item    = lt_item
        return           = lt_ret.
    READ TABLE lt_ret INTO ls_ret INDEX 1.
    IF sy-subrc = 0 AND ls_ret-type CA 'EA'.
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Goods movement failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Goods movement posted' iv_data = |{ lv_mdoc }| ).
    ENDIF.
  ENDMETHOD.

  METHOD create_to.
    DATA: ls_params TYPE zrouter_wm_to_params,
          lv_tanum  TYPE ltak-tanum.

    " Parse JSON payload
    /ui2/cl_json=>deserialize(
      EXPORTING json = iv_payload
      CHANGING  data = ls_params ).

    CALL FUNCTION 'L_TO_CREATE_SINGLE'
      EXPORTING
        i_lgnum       = ls_params-warehouse
        i_bwlvs       = ls_params-move_type
        i_matnr       = ls_params-material
        i_werks       = ls_params-plant
        i_vltyp       = ls_params-source_stor_type
        i_vlpla       = ls_params-source_stor_bin
        i_nltyp       = ls_params-dest_stor_type
        i_nlpla       = ls_params-dest_stor_bin
        i_anfme       = ls_params-quantity
        i_altme       = ls_params-base_uom
        i_commit_work = 'X'
      IMPORTING
        e_tanum       = lv_tanum
      EXCEPTIONS
        OTHERS        = 99.
    IF sy-subrc <> 0.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Transfer order creation failed, subrc={ sy-subrc }| ).
    ELSE.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Transfer order created' iv_data = |{ lv_tanum }| ).
    ENDIF.
  ENDMETHOD.
ENDCLASS.