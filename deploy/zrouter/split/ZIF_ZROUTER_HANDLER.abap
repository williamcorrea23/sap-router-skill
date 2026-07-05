INTERFACE zif_zrouter_handler PUBLIC.
  TYPES:
    BEGIN OF ty_action_result,
      status    TYPE string,
      message   TYPE string,
      data      TYPE string,
      module    TYPE string,
      action    TYPE string,
      timestamp TYPE timestampl,
    END OF ty_action_result.

  METHODS handle_action
    IMPORTING
      iv_action        TYPE string
      iv_payload       TYPE string
    RETURNING
      VALUE(rs_result) TYPE ty_action_result
    RAISING
      cx_zrouter.
ENDINTERFACE.