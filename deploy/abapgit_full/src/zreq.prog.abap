*&---------------------------------------------------------------------*
*& ZREQ - Transport Request Copy Utility
*& Creates a copy of an existing transport request with optional target
*&---------------------------------------------------------------------*
REPORT zreq.

PARAMETERS:
  p_srcrq  TYPE trkorr OBLIGATORY LOWER CASE,
  p_dsttxt TYPE as4text OBLIGATORY LOWER CASE DEFAULT 'Copy of',
  p_target TYPE tarsystem LOWER CASE.

DATA:
  lv_new_request  TYPE trkorr,
  lt_objects      TYPE TABLE OF e071,
  lt_keys         TYPE TABLE OF e071k,
  lt_users        TYPE TABLE OF e070,
  lv_task         TYPE trkorr,
  lv_dsttxt       TYPE as4text.

INITIALIZATION.
  CONCATENATE p_dsttxt sy-datum sy-uzeit INTO lv_dsttxt
    SEPARATED BY space.

START-OF-SELECTION.
  " AUTH check
  AUTHORITY-CHECK OBJECT 'S_TRANSPRT'
    ID 'ACTVT' FIELD '02'.
  IF sy-subrc <> 0.
    WRITE: / 'Not authorized for transport changes.'.
    RETURN.
  ENDIF.

  " Step 1: Read source request
  CALL FUNCTION 'TR_READ_REQUEST'
    EXPORTING
      iv_trkorr             = p_srcrq
    IMPORTING
      et_objects            = lt_objects
      et_keys               = lt_keys
    EXCEPTIONS
      error_reading_request = 1
      OTHERS                = 2.

  IF sy-subrc <> 0.
    WRITE: / 'ERROR: Cannot read request', p_srcrq.
    RETURN.
  ENDIF.

  " Step 2: Create new request (let SAP generate the number)
  CLEAR lv_new_request.
  CALL FUNCTION 'TR_COPY_REQUEST'
    EXPORTING
      iv_dialog            = abap_false
      iv_source_request    = p_srcrq
    IMPORTING
      ev_target_request    = lv_new_request
    EXCEPTIONS
      request_not_found    = 1
      request_not_copyable = 2
      OTHERS               = 3.

  IF sy-subrc = 0 AND lv_new_request IS NOT INITIAL.
    " Step 3: Update description and target
    CALL FUNCTION 'TR_MODIFY_REQUEST'
      EXPORTING
        iv_trkorr     = lv_new_request
        iv_as4text    = lv_dsttxt
        iv_trfunction = 'W'
      EXCEPTIONS
        OTHERS        = 1.

    IF p_target IS NOT INITIAL.
      CALL FUNCTION 'TR_SET_TARGET'
        EXPORTING
          iv_trkorr    = lv_new_request
          iv_tarsystem = p_target
        EXCEPTIONS
          OTHERS       = 1.
    ENDIF.

    WRITE: / 'SUCCESS: Request copied'.
    WRITE: / 'Source:', p_srcrq.
    WRITE: / 'Copy  :', lv_new_request.
    WRITE: / 'Target:', p_target.
    WRITE: / 'Use SE09 to verify and release.'.
  ELSE.
    " Fallback: manual copy
    WRITE: / 'TR_COPY_REQUEST failed. Trying manual copy...'.

    CALL FUNCTION 'TR_INSERT_REQUEST_WITH_TASKS'
      EXPORTING
        iv_type        = 'W'
        iv_text        = lv_dsttxt
        iv_target      = p_target
        it_users       = lt_users
      IMPORTING
        ev_trkorr      = lv_new_request
        ev_task        = lv_task
      EXCEPTIONS
        insert_failed  = 1
        enqueue_failed = 2
        OTHERS         = 3.

    IF sy-subrc <> 0.
      WRITE: / 'ERROR: Could not create copy request.'.
      RETURN.
    ENDIF.

    " Copy objects to new request
    LOOP AT lt_objects ASSIGNING FIELD-SYMBOL(<ls_obj>).
      <ls_obj>-trkorr = lv_new_request.
    ENDLOOP.

    CALL FUNCTION 'TR_INSERT_OBJECTS'
      EXPORTING
        iv_trkorr    = lv_new_request
        it_objects   = lt_objects
      EXCEPTIONS
        cancel       = 1
        wrong_client = 2
        OTHERS       = 3.

    IF sy-subrc = 0.
      WRITE: / 'SUCCESS: Manual copy created'.
      WRITE: / 'New request:', lv_new_request.
      WRITE: / 'Objects copied:', lines( lt_objects ).
    ELSE.
      WRITE: / 'ERROR inserting objects into new request.'.
    ENDIF.
  ENDIF.

  SKIP.
  WRITE: / 'Open SE09 to verify: transaction SE09 ->', lv_new_request.
