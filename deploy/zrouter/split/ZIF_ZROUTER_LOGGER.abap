INTERFACE zif_zrouter_logger PUBLIC.
  TYPES:
    BEGIN OF ty_log_entry,
      guid      TYPE sysuuid_c32,
      module    TYPE string,
      action    TYPE string,
      status    TYPE string,
      message   TYPE string,
      payload   TYPE string,
      result    TYPE string,
      username  TYPE syuname,
      timestamp TYPE timestampl,
    END OF ty_log_entry.

  METHODS log_action
    IMPORTING
      iv_module      TYPE string
      iv_action      TYPE string
      iv_status      TYPE string
      iv_message     TYPE string
      iv_payload     TYPE string OPTIONAL
      iv_result      TYPE string OPTIONAL
    RETURNING
      VALUE(rv_guid) TYPE sysuuid_c32
    RAISING
      cx_zrouter.

  METHODS get_logs
    IMPORTING
      iv_module      TYPE string OPTIONAL
      iv_date        TYPE dats OPTIONAL
    RETURNING
      VALUE(rt_logs) TYPE STANDARD TABLE OF ty_log_entry WITH EMPTY KEY.
ENDINTERFACE.