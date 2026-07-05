FUNCTION ZROUTER_DISPATCH_FM.
*"----------------------------------------------------------------------
*"*"Interface Local:
*"  IMPORTING
*"     VALUE(IV_MODULE) TYPE STRING
*"     VALUE(IV_ACTION) TYPE STRING
*"     VALUE(IV_PAYLOAD) TYPE STRING
*"  EXPORTING
*"     VALUE(EV_RESULT) TYPE STRING
*"     VALUE(EV_STATUS) TYPE STRING
*"     VALUE(EV_RETURN_MESSAGE) TYPE STRING
*"----------------------------------------------------------------------
  DATA(lo_dispatch) = NEW zcl_zrouter_dispatch( ).
  DATA(ls_result) = lo_dispatch->dispatch(
    iv_module  = iv_module
    iv_action  = iv_action
    iv_payload = iv_payload
  ).
  ev_status         = ls_result-status.
  ev_result         = ls_result-data.
  ev_return_message = ls_result-message.
ENDFUNCTION.