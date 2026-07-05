CLASS zcl_zrouter_handler_basis DEFINITION PUBLIC FINAL CREATE PUBLIC
  INHERITING FROM zcl_zrouter_handler_abstract.
  PUBLIC SECTION.
    METHODS constructor
      IMPORTING
        io_logger TYPE REF TO zif_zrouter_logger
        io_config TYPE REF TO zif_zrouter_config.
  PROTECTED SECTION.
    METHODS handle_custom_action REDEFINITION.
  PRIVATE SECTION.
    METHODS create_request
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS release_request
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS st22_scan
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS code_analysis
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
ENDCLASS.


CLASS zcl_zrouter_handler_basis IMPLEMENTATION.
  METHOD constructor.
    super->constructor( io_logger = io_logger io_config = io_config iv_module = 'BASIS' ).
  ENDMETHOD.

  METHOD handle_custom_action.
    CASE to_upper( iv_action ).
      WHEN 'CREATE_REQUEST'.
        rs_result = create_request( iv_payload ).
      WHEN 'RELEASE_REQUEST'.
        rs_result = release_request( iv_payload ).
      WHEN 'ST22_SCAN'.
        rs_result = st22_scan( iv_payload ).
      WHEN 'CODE_ANALYSIS'.
        rs_result = code_analysis( iv_payload ).
      WHEN OTHERS.
        RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = |Unknown BASIS action: { iv_action }|.
    ENDCASE.
  ENDMETHOD.

  METHOD create_request.
    DATA: ls_params TYPE zrouter_basis_tr_params,
          lv_request TYPE trkorr.

    " Parse JSON payload
    /ui2/cl_json=>deserialize(
      EXPORTING json = iv_payload
      CHANGING  data = ls_params ).

    CALL FUNCTION 'TR_INSERT_REQUEST_WITH_TASKS'
      EXPORTING
        iv_type     = ls_params-request_type
        iv_text     = ls_params-owner_text
        iv_target   = ls_params-target_system
      IMPORTING
        ev_request  = lv_request
      EXCEPTIONS
        OTHERS      = 99.
    IF sy-subrc <> 0.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Transport request creation failed, subrc={ sy-subrc }| ).
    ELSE.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Transport request created' iv_data = lv_request ).
    ENDIF.
  ENDMETHOD.

  METHOD release_request.
    CALL FUNCTION 'TR_RELEASE_REQUEST'
      EXPORTING
        iv_trkorr = iv_payload
      EXCEPTIONS
        OTHERS    = 99.
    IF sy-subrc <> 0.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Release failed, subrc={ sy-subrc }| ).
    ELSE.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Transport request released' ).
    ENDIF.
  ENDMETHOD.

  METHOD st22_scan.
    DATA: lt_snap TYPE TABLE OF snap,
          lv_count TYPE i.
    SELECT COUNT(*) INTO @lv_count
      FROM snap
      WHERE datum BETWEEN @iv_payload AND @sy-datum
      UP TO 1 ROWS.
    rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'ST22 scan complete' iv_data = |{ lv_count } dumps found| ).
  ENDMETHOD.

  METHOD code_analysis.
    DATA: lt_ret TYPE TABLE OF bapiret2.
    CALL FUNCTION 'TRINT_INSPECT_OBJECTS'
      EXPORTING
        iv_mode = 'N'.
    rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Code analysis triggered' ).
  ENDMETHOD.
ENDCLASS.