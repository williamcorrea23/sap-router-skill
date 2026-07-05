CLASS zcl_zrouter_handler_hcm DEFINITION PUBLIC FINAL CREATE PUBLIC
  INHERITING FROM zcl_zrouter_handler_abstract.
  PUBLIC SECTION.
    METHODS constructor
      IMPORTING
        io_logger TYPE REF TO zif_zrouter_logger
        io_config TYPE REF TO zif_zrouter_config.
  PROTECTED SECTION.
    METHODS handle_custom_action REDEFINITION.
  PRIVATE SECTION.
    METHODS read_employee
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS create_infotype
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
ENDCLASS.


CLASS zcl_zrouter_handler_hcm IMPLEMENTATION.
  METHOD constructor.
    super->constructor( io_logger = io_logger io_config = io_config iv_module = 'HCM' ).
  ENDMETHOD.

  METHOD handle_custom_action.
    CASE to_upper( iv_action ).
      WHEN 'READ_EMPLOYEE'.
        rs_result = read_employee( iv_payload ).
      WHEN 'CREATE_INFOTYPE'.
        rs_result = create_infotype( iv_payload ).
      WHEN OTHERS.
        RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = |Unknown HCM action: { iv_action }|.
    ENDCASE.
  ENDMETHOD.

  METHOD read_employee.
    DATA: lt_return TYPE TABLE OF bapiret2.
    CALL FUNCTION 'BAPI_EMPLOYEE_GETDATA'
      EXPORTING
        employee_id = iv_payload
      TABLES
        return      = lt_return.
    READ TABLE lt_return INTO DATA(ls_ret) INDEX 1.
    IF sy-subrc = 0 AND ls_ret-type = 'E'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Employee read failed: { ls_ret-message }| ).
    ELSE.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Employee data retrieved' ).
    ENDIF.
  ENDMETHOD.

  METHOD create_infotype.
    DATA: ls_params TYPE zrouter_hcm_infotype_params,
          ls_ret    TYPE bapiret2.

    " Parse JSON payload
    /ui2/cl_json=>deserialize(
      EXPORTING json = iv_payload
      CHANGING  data = ls_params ).

    CALL FUNCTION 'BAPI_EMPLOYEE_ENQUEUE'
      EXPORTING
        employee_id = ls_params-employee_id.
    IF sy-subrc <> 0.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Employee enqueue failed| ).
      RETURN.
    ENDIF.

    CALL FUNCTION 'PA_INFOTYPE_INSERT'
      EXPORTING
        employee_id  = ls_params-employee_id
        infotype     = ls_params-infotype
        subtype      = ls_params-subtype
        begda        = ls_params-begin_date
        endda        = ls_params-end_date
      IMPORTING
        return       = ls_ret.
    IF ls_ret-type CA 'EA'.
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Infotype insert failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Infotype record created' ).
    ENDIF.
  ENDMETHOD.
ENDCLASS.