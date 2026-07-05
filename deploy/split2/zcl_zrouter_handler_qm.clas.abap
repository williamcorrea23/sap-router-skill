CLASS zcl_zrouter_handler_qm DEFINITION PUBLIC FINAL CREATE PUBLIC
  INHERITING FROM zcl_zrouter_handler_abstract.
  PUBLIC SECTION.
    METHODS constructor
      IMPORTING
        io_logger TYPE REF TO zif_zrouter_logger
        io_config TYPE REF TO zif_zrouter_config.
  PROTECTED SECTION.
    METHODS handle_custom_action REDEFINITION.
  PRIVATE SECTION.
    METHODS create_inspection_lot
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS record_results
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
ENDCLASS.


CLASS zcl_zrouter_handler_qm IMPLEMENTATION.
  METHOD constructor.
    super->constructor( io_logger = io_logger io_config = io_config iv_module = 'QM' ).
  ENDMETHOD.

  METHOD handle_custom_action.
    CASE to_upper( iv_action ).
      WHEN 'CREATE_INSPECTION'.
        rs_result = create_inspection_lot( iv_payload ).
      WHEN 'RECORD_RESULTS'.
        rs_result = record_results( iv_payload ).
      WHEN OTHERS.
        RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = |Unknown QM action: { iv_action }|.
    ENDCASE.
  ENDMETHOD.

  METHOD create_inspection_lot.
    DATA: ls_params   TYPE zrouter_qm_insp_params,
          lt_ret      TYPE TABLE OF bapiret2,
          lv_insp_lot TYPE qplos.

    " Parse JSON payload
    /ui2/cl_json=>deserialize(
      EXPORTING json = iv_payload
      CHANGING  data = ls_params ).

    CALL FUNCTION 'CO_QM_INSPECTION_LOT_CREATE'
      EXPORTING
        i_material   = ls_params-material
        i_werk       = ls_params-plant
        i_insp_type  = ls_params-insp_type
        i_insp_qty   = ls_params-lot_quantity
      IMPORTING
        e_inspection = lv_insp_lot
      TABLES
        t_return     = lt_ret.
    IF sy-subrc <> 0 OR line_exists( lt_ret[ type = 'E' ] )
                       OR line_exists( lt_ret[ type = 'A' ] ).
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      READ TABLE lt_ret WITH KEY type = 'E' INTO DATA(ls_qm_ret).
      rs_result = build_result( iv_status = 'ERROR'
          iv_message = |Inspection lot creation failed: { ls_qm_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Inspection lot created' iv_data = |{ lv_insp_lot }| ).
    ENDIF.
  ENDMETHOD.

  METHOD record_results.
    DATA: ls_ret TYPE bapiret2.
    CALL FUNCTION 'BAPI_INSPOPER_RECORDRESULTS'
      EXPORTING
        insplot  = iv_payload
      IMPORTING
        return   = ls_ret.
    IF ls_ret-type = 'E'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Results recording failed: { ls_ret-message }| ).
    ELSE.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Results recorded' ).
    ENDIF.
  ENDMETHOD.
ENDCLASS.