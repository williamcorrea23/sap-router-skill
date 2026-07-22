"! RFC inbound stub: the MES / weighbridge system calls this endpoint to hand
"! over scale tickets. In the real system this is the RFC-enabled function
"! Z_GM_RECEIVE_TICKET forwarding here; the class is the testable core.
CLASS zcl_gm_scale_rfc_stub DEFINITION PUBLIC FINAL CREATE PUBLIC.

  PUBLIC SECTION.
    METHODS receive_ticket
      IMPORTING
        is_ticket TYPE zif_gm_movement_types=>ty_scale_ticket
      RETURNING
        VALUE(rv_accepted) TYPE abap_bool.

  PRIVATE SECTION.
    METHODS is_duplicate
      IMPORTING
        iv_ticket_id TYPE zif_gm_movement_types=>ty_scale_ticket-ticket_id
      RETURNING
        VALUE(rv_duplicate) TYPE abap_bool.

ENDCLASS.

CLASS zcl_gm_scale_rfc_stub IMPLEMENTATION.

  METHOD receive_ticket.
    DATA ls_db TYPE zgm_scale_ticket.

    rv_accepted = abap_false.
    IF is_ticket-ticket_id IS INITIAL OR is_ticket-matnr IS INITIAL.
      RETURN.
    ENDIF.
    IF is_duplicate( is_ticket-ticket_id ) = abap_true.
      RETURN.
    ENDIF.

    MOVE-CORRESPONDING is_ticket TO ls_db.
    GET TIME STAMP FIELD ls_db-received_at.
    INSERT zgm_scale_ticket FROM ls_db.
    IF sy-subrc = 0.
      rv_accepted = abap_true.
      " hand off to the movement service for posting
      DATA(lo_service) = NEW zcl_gm_movement_service( ).
      lo_service->process_open_tickets( iv_werks = is_ticket-werks ).
    ENDIF.
  ENDMETHOD.

  METHOD is_duplicate.
    DATA lv_ticket_id TYPE zgm_scale_ticket-ticket_id.
    SELECT SINGLE ticket_id FROM zgm_scale_ticket
      INTO lv_ticket_id
      WHERE ticket_id = iv_ticket_id.
    rv_duplicate = boolc( sy-subrc = 0 ).
  ENDMETHOD.

ENDCLASS.
