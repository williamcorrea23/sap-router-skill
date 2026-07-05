
CLASS zcl_zrouter_batch DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    TYPES:
      BEGIN OF ty_batch_action,
        seqnr   TYPE i,
        module  TYPE string,
        action  TYPE string,
        payload TYPE string,
      END OF ty_batch_action,
      ty_batch_actions TYPE STANDARD TABLE OF ty_batch_action WITH EMPTY KEY,

      BEGIN OF ty_batch_item_result,
        seqnr   TYPE i,
        module  TYPE string,
        action  TYPE string,
        status  TYPE string,
        message TYPE string,
        data    TYPE string,
      END OF ty_batch_item_result,
      ty_batch_results TYPE STANDARD TABLE OF ty_batch_item_result WITH EMPTY KEY,

      BEGIN OF ty_batch_result,
        batch_guid TYPE sysuuid_c32,
        status     TYPE string,
        results    TYPE ty_batch_results,
      END OF ty_batch_result.

    METHODS execute_batch
      IMPORTING it_actions       TYPE ty_batch_actions
      RETURNING VALUE(rs_result) TYPE ty_batch_result.

    METHODS constructor
      IMPORTING io_dispatch TYPE REF TO zcl_zrouter_dispatch OPTIONAL.

  PRIVATE SECTION.
    DATA mo_dispatch TYPE REF TO zcl_zrouter_dispatch.
    DATA mo_logger   TYPE REF TO zif_zrouter_logger.
    METHODS save_batch_result
      IMPORTING
        iv_batch_guid TYPE sysuuid_c32
        iv_seqnr      TYPE i
        iv_module     TYPE string
        iv_action     TYPE string
        iv_status     TYPE string
        iv_message    TYPE string
        iv_payload    TYPE string
        iv_result     TYPE string.
    METHODS generate_guid RETURNING VALUE(rv_guid) TYPE sysuuid_c32.
ENDCLASS.