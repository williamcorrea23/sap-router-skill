"* Enhancement: user-exit include ZXMBCU01 (customer part of MB_CUA /
"* EXIT_SAPMM07M_001). Appends every posted material document line to the
"* custom audit log so the reconciliation report has full coverage.

FORM exit_update_movement_log
  USING is_mkpf TYPE mkpf
        it_mseg TYPE ty_t_mseg.

  DATA ls_log TYPE zgm_movement_log.

  LOOP AT it_mseg INTO DATA(ls_mseg).
    CLEAR ls_log.
    TRY.
        ls_log-log_id = cl_system_uuid=>create_uuid_x16_static( ).
      CATCH cx_uuid_error.
        RETURN.
    ENDTRY.
    ls_log-matnr = ls_mseg-matnr.
    ls_log-werks = ls_mseg-werks.
    ls_log-bwart = ls_mseg-bwart.
    ls_log-menge = ls_mseg-menge.
    ls_log-mblnr = is_mkpf-mblnr.
    GET TIME STAMP FIELD ls_log-posted_at.
    INSERT zgm_movement_log FROM ls_log.
  ENDLOOP.
ENDFORM.
