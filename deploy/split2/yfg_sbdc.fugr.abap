*&---------------------------------------------------------------------*
*& YFG_SBDC - SHDB/BDC Function Group
*& Batch Input recording and replay for transactions without BAPI
*&
*& Contains:
*&   Y_SBDC_RECORD - Record a BDC session (store bdcdata as JSON)
*&   Y_SBDC_REPLAY - Replay a stored BDC session via CALL TRANSACTION
*&   Y_SBDC_DELETE - Delete a stored session
*&   Y_SBDC_LIST   - List all stored sessions
*&   Y_SBDC_EXPORT - Export session as JSON for MCP consumption
*&---------------------------------------------------------------------*
FUNCTION-POOL yfg_sbdc.

* DDIC tables used (create via SE11):
*   YSBDC_SESSION - session_id, tcode, recording_name, bdcdata_json,
*                   created_by, created_at, last_used
*   YSBDC_RESULT  - session_id, execution_id, status, message,
*                   executed_at, executed_by

*&---------------------------------------------------------------------*
*& Y_SBDC_RECORD - Store a BDC recording as JSON
*&---------------------------------------------------------------------*
FUNCTION y_sbdc_record.
  IMPORTING
    iv_tcode         TYPE sytcode
    iv_recording_name TYPE string
    it_bdcdata       TYPE TABLE OF bdcdata
  EXPORTING
    ev_session_id    TYPE sysuuid_c32
    ev_status        TYPE string
  EXCEPTIONS
    recording_failed.

  DATA: ls_session TYPE ysbdc_session,
        lv_json    TYPE string,
        lv_guid    TYPE sysuuid_c32.

  " Generate session ID
  TRY.
      lv_guid = cl_system_uuid=>create_uuid_c32_static( ).
    CATCH cx_uuid_error.
      ev_status = 'ERROR: UUID generation failed'.
      RAISE recording_failed.
  ENDTRY.

  " Serialize bdcdata to JSON
  lv_json = /ui2/cl_json=>serialize(
    data        = it_bdcdata
    compress    = abap_true
    pretty_name = /ui2/cl_json=>pretty_mode-camel_case ).

  " Store in DB
  ls_session-session_id     = lv_guid.
  ls_session-tcode          = iv_tcode.
  ls_session-recording_name = iv_recording_name.
  ls_session-bdcdata_json   = lv_json.
  ls_session-created_by     = sy-uname.
  GET TIME STAMP FIELD ls_session-created_at.

  INSERT ysbdc_session FROM ls_session.
  IF sy-subrc <> 0.
    ev_status = 'ERROR: Insert failed - duplicate session_id?'.
    RAISE recording_failed.
  ELSE.
    COMMIT WORK AND WAIT.
    ev_session_id = lv_guid.
    ev_status     = 'RECORDED'.
  ENDIF.

ENDFUNCTION.

*&---------------------------------------------------------------------*
*& Y_SBDC_REPLAY - Replay a stored BDC session
*&---------------------------------------------------------------------*
FUNCTION y_sbdc_replay.
  IMPORTING
    iv_session_id    TYPE sysuuid_c32 OPTIONAL
    iv_recording_name TYPE string OPTIONAL
    iv_mode          TYPE char1 DEFAULT 'N'
    iv_update        TYPE char1 DEFAULT 'S'
  EXPORTING
    ev_status        TYPE string
    ev_message       TYPE string
    et_messages      TYPE bdcmsgcoll_tab
  EXCEPTIONS
    session_not_found
    replay_failed.

  DATA: ls_session   TYPE ysbdc_session,
        lt_bdcdata   TYPE TABLE OF bdcdata,
        lt_messtab   TYPE TABLE OF bdcmsgcoll,
        lv_execution TYPE sysuuid_c32,
        ls_result    TYPE ysbdc_result.

  " Resolve session by ID or recording name
  IF iv_session_id IS NOT INITIAL.
    SELECT SINGLE * FROM ysbdc_session
      INTO ls_session
      WHERE session_id = iv_session_id.
  ELSEIF iv_recording_name IS NOT INITIAL.
    SELECT SINGLE * FROM ysbdc_session
      INTO ls_session
      WHERE recording_name = iv_recording_name
      ORDER BY created_at DESCENDING.
  ELSE.
    ev_status  = 'ERROR'.
    ev_message = 'Provide iv_session_id or iv_recording_name'.
    RAISE session_not_found.
  ENDIF.

  IF sy-subrc <> 0.
    ev_status  = 'ERROR'.
    ev_message = 'Session not found'.
    RAISE session_not_found.
  ENDIF.

  " Deserialize bdcdata from JSON
  /ui2/cl_json=>deserialize(
    EXPORTING json = ls_session-bdcdata_json
    CHANGING  data = lt_bdcdata ).

  IF lt_bdcdata IS INITIAL.
    ev_status  = 'ERROR'.
    ev_message = 'Session has no bdcdata'.
    RAISE replay_failed.
  ENDIF.

  " Generate execution ID for tracking
  TRY.
      lv_execution = cl_system_uuid=>create_uuid_c32_static( ).
    CATCH cx_uuid_error.
      lv_execution = 'FALLBACK-001'.
  ENDTRY.

  " Execute BDC
  CALL TRANSACTION ls_session-tcode
    USING lt_bdcdata
    MODE iv_mode
    UPDATE iv_update
    MESSAGES INTO lt_messtab.

  " Collect results
  et_messages = lt_messtab.

  " Check for errors in messages
  READ TABLE lt_messtab TRANSPORTING NO FIELDS
    WITH KEY msgtyp = 'E'.
  IF sy-subrc = 0.
    ev_status  = 'ERROR'.
    ev_message = 'BDC errors detected. Check et_messages.'.
  ELSE.
    READ TABLE lt_messtab TRANSPORTING NO FIELDS
      WITH KEY msgtyp = 'A'.
    IF sy-subrc = 0.
      ev_status  = 'ERROR'.
      ev_message = 'BDC aborted. Check et_messages.'.
    ELSE.
      ev_status  = 'SUCCESS'.
      ev_message = |Transaction { ls_session-tcode } completed|.
    ENDIF.
  ENDIF.

  " Log execution result
  ls_result-session_id   = ls_session-session_id.
  ls_result-execution_id = lv_execution.
  ls_result-status       = ev_status.
  ls_result-message      = ev_message.
  ls_result-executed_by  = sy-uname.
  GET TIME STAMP FIELD ls_result-executed_at.

  INSERT ysbdc_result FROM ls_result.
  IF sy-subrc = 0.
    COMMIT WORK AND WAIT.
  ENDIF.

  " Update last_used on session
  GET TIME STAMP FIELD ls_session-last_used.
  UPDATE ysbdc_session SET last_used = ls_session-last_used
    WHERE session_id = ls_session-session_id.
  COMMIT WORK AND WAIT.

ENDFUNCTION.

*&---------------------------------------------------------------------*
*& Y_SBDC_DELETE - Delete a stored session
*&---------------------------------------------------------------------*
FUNCTION y_sbdc_delete.
  IMPORTING
    iv_session_id TYPE sysuuid_c32
  EXPORTING
    ev_status     TYPE string
    ev_message    TYPE string.

  DELETE FROM ysbdc_session WHERE session_id = iv_session_id.
  IF sy-subrc = 0.
    ev_status  = 'SUCCESS'.
    ev_message = |Session { iv_session_id } deleted|.
    COMMIT WORK AND WAIT.
  ELSE.
    ev_status  = 'ERROR'.
    ev_message = |Session { iv_session_id } not found|.
  ENDIF.

ENDFUNCTION.

*&---------------------------------------------------------------------*
*& Y_SBDC_LIST - List all stored sessions
*&---------------------------------------------------------------------*
FUNCTION y_sbdc_list.
  IMPORTING
    iv_tcode  TYPE sytcode OPTIONAL
  EXPORTING
    et_sessions TYPE ysbdc_session_tab
    ev_count    TYPE i.

  IF iv_tcode IS NOT INITIAL.
    SELECT * FROM ysbdc_session
      INTO TABLE et_sessions
      WHERE tcode = iv_tcode
      ORDER BY created_at DESCENDING.
  ELSE.
    SELECT * FROM ysbdc_session
      INTO TABLE et_sessions
      ORDER BY created_at DESCENDING.
  ENDIF.

  ev_count = lines( et_sessions ).

ENDFUNCTION.

*&---------------------------------------------------------------------*
*& Y_SBDC_EXPORT - Export session as JSON (for MCP/claude consumption)
*&---------------------------------------------------------------------*
FUNCTION y_sbdc_export.
  IMPORTING
    iv_session_id    TYPE sysuuid_c32 OPTIONAL
    iv_recording_name TYPE string OPTIONAL
  EXPORTING
    ev_json   TYPE string
    ev_status TYPE string
  EXCEPTIONS
    not_found.

  DATA: ls_session   TYPE ysbdc_session,
        lt_bdcdata   TYPE TABLE OF bdcdata,
        BEGIN OF ls_export,
          session_id     TYPE sysuuid_c32,
          tcode          TYPE sytcode,
          recording_name TYPE string,
          created_by     TYPE syuname,
          created_at     TYPE timestampl,
          bdcdata        TYPE TABLE OF bdcdata WITH NON-UNIQUE DEFAULT KEY,
        END OF ls_export.

  " Resolve session
  IF iv_session_id IS NOT INITIAL.
    SELECT SINGLE * FROM ysbdc_session
      INTO ls_session
      WHERE session_id = iv_session_id.
  ELSEIF iv_recording_name IS NOT INITIAL.
    SELECT SINGLE * FROM ysbdc_session
      INTO ls_session
      WHERE recording_name = iv_recording_name
      ORDER BY created_at DESCENDING.
  ENDIF.

  IF sy-subrc <> 0.
    ev_status = 'NOT_FOUND'.
    RAISE not_found.
  ENDIF.

  " Deserialize bdcdata
  /ui2/cl_json=>deserialize(
    EXPORTING json = ls_session-bdcdata_json
    CHANGING  data = lt_bdcdata ).

  " Build export structure
  ls_export-session_id     = ls_session-session_id.
  ls_export-tcode          = ls_session-tcode.
  ls_export-recording_name = ls_session-recording_name.
  ls_export-created_by     = ls_session-created_by.
  ls_export-created_at     = ls_session-created_at.
  ls_export-bdcdata        = lt_bdcdata.

  " Serialize to JSON
  ev_json = /ui2/cl_json=>serialize(
    data        = ls_export
    compress    = abap_true
    pretty_name = /ui2/cl_json=>pretty_mode-camel_case ).

  ev_status = 'SUCCESS'.

ENDFUNCTION.
