REPORT zrouter_activate.
* Auto-activates ZROUTER v5 objects on NW 7.40
* Uses GENERATE REPORT for programs and class pools

DATA: lv_name   TYPE string,
      lv_pool   TYPE string,
      lv_msg    TYPE string,
      lv_count  TYPE i VALUE 0,
      lv_err    TYPE i VALUE 0,
      lv_pad    TYPE i,
      lv_prefix TYPE string.

TYPES: BEGIN OF ty_object,
         name TYPE string,
         type TYPE c LENGTH 1, " P=Program, C=Class, F=FUGR
       END OF ty_object.

DATA: lt_objects TYPE TABLE OF ty_object.

START-OF-SELECTION.
  APPEND VALUE #( name = 'ZREQ'                type = 'P' ) TO lt_objects.
  APPEND VALUE #( name = 'ZROUTER_ACTIVATE'    type = 'P' ) TO lt_objects.
  APPEND VALUE #( name = 'ZCL_ZROUTER_HTTP'     type = 'C' ) TO lt_objects.
  APPEND VALUE #( name = 'ZCL_ZROUTER_LOGGER'   type = 'C' ) TO lt_objects.
  APPEND VALUE #( name = 'ZCL_ZROUTER_AUTHORITY' type = 'C' ) TO lt_objects.
  APPEND VALUE #( name = 'ZCL_ZROUTER_DISPATCH' type = 'C' ) TO lt_objects.
  APPEND VALUE #( name = 'ZCL_ZROUTER_CONFIG'   type = 'C' ) TO lt_objects.
  APPEND VALUE #( name = 'ZCL_ZROUTER_BATCH'    type = 'C' ) TO lt_objects.
  APPEND VALUE #( name = 'ZCX_ZROUTER'          type = 'C' ) TO lt_objects.
  APPEND VALUE #( name = 'YFG_SBDC'            type = 'F' ) TO lt_objects.

  WRITE: / 'ZROUTER Activation v5.1 — NW 7.40'.
  WRITE: / 'Objects:', lines( lt_objects ).
  ULINE.

  LOOP AT lt_objects INTO DATA(ls_obj).
    TRY.
        CASE ls_obj-type.
          WHEN 'P'. " Program
            GENERATE REPORT ls_obj-name.
            IF sy-subrc = 0.
              lv_msg = |OK|.
              lv_count = lv_count + 1.
            ELSE.
              lv_msg = |FAIL (subrc={ sy-subrc })|.
              lv_err = lv_err + 1.
            ENDIF.

          WHEN 'C'. " Class — generate class pool
            " Class pool naming: CL_<classname> padded with = to 28 chars + CP
            CONCATENATE 'CL' ls_obj-name INTO lv_pool SEPARATED BY '_'.
            lv_pad = 28 - strlen( lv_pool ).
            IF lv_pad > 0.
              DO lv_pad TIMES.
                CONCATENATE lv_pool '=' INTO lv_pool.
              ENDDO.
            ENDIF.
            CONCATENATE lv_pool 'CP' INTO lv_pool.
            GENERATE REPORT lv_pool.
            IF sy-subrc = 0.
              lv_msg = |OK (pool={ lv_pool })|.
              lv_count = lv_count + 1.
            ELSE.
              lv_msg = |FAIL pool={ lv_pool } (subrc={ sy-subrc })|.
              lv_err = lv_err + 1.
            ENDIF.

          WHEN 'F'. " Function group
            " FUGR pool: SAPL<fg_name>
            CONCATENATE 'SAPL' ls_obj-name INTO lv_pool.
            GENERATE REPORT lv_pool.
            IF sy-subrc = 0.
              lv_msg = |OK (pool={ lv_pool })|.
              lv_count = lv_count + 1.
            ELSE.
              lv_msg = |FAIL pool={ lv_pool } (subrc={ sy-subrc })|.
              lv_err = lv_err + 1.
            ENDIF.
        ENDCASE.

      CATCH cx_root INTO DATA(lx).
        lv_msg = |DUMP: { lx->get_text( ) }|.
        lv_err = lv_err + 1.
    ENDTRY.
    WRITE: / |{ ls_obj-name } ({ ls_obj-type }): { lv_msg }|.
  ENDLOOP.

  ULINE.
  WRITE: / |Activated: { lv_count }, Failed: { lv_err }|.
  WRITE: / 'Done.'.
