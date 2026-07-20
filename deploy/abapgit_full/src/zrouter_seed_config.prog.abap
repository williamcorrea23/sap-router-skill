REPORT zrouter_seed_config.

*&---------------------------------------------------------------------*
*& ZROUTER_SEED_CONFIG
*&
*& Seeds ZROUTER_CONFIG with every action the v5 handlers dispatch.
*& Source of truth: the WHEN '<action>' branches in each
*& ZCL_ZROUTER_HANDLER_<module>->handle_custom_action, plus PING
*& (handled by the abstract handler for every module).
*&
*& Idempotent: MODIFY upserts by key, so the report is safely re-runnable.
*& Run: SE38 -> ZROUTER_SEED_CONFIG -> F8 (ADT execute API is unavailable
*& on NetWeaver 7.40, so run from SAP GUI).
*&
*& Conventions:
*&   active    = 'X'  -> action enabled (is_action_allowed returns true)
*&   batchable = 'X'  -> may appear in a POST /batch call (writes); '' for reads
*&   timeout          -> seconds; reads 30, writes 120, transports 60, ping 10
*&---------------------------------------------------------------------*

TYPES: BEGIN OF ty_seed,
         module    TYPE zrouter_config-module,
         action    TYPE zrouter_config-action,
         active    TYPE zrouter_config-active,
         batchable TYPE zrouter_config-batchable,
         timeout   TYPE zrouter_config-timeout,
       END OF ty_seed.

DATA: lt_seed TYPE STANDARD TABLE OF ty_seed,
      ls_cfg  TYPE zrouter_config,
      lv_rows TYPE i.

lt_seed = VALUE #(
  " -- MM --
  ( module = 'MM'    action = 'CREATE_MATERIAL'       active = 'X' batchable = 'X' timeout = 120 )
  ( module = 'MM'    action = 'CHANGE_MATERIAL'       active = 'X' batchable = 'X' timeout = 120 )
  ( module = 'MM'    action = 'GET_MATERIAL'          active = 'X' batchable = ''  timeout = 30 )
  ( module = 'MM'    action = 'CREATE_PO'             active = 'X' batchable = 'X' timeout = 120 )
  ( module = 'MM'    action = 'CHANGE_PO'             active = 'X' batchable = 'X' timeout = 120 )
  ( module = 'MM'    action = 'CHECK_CONFIG'          active = 'X' batchable = ''  timeout = 30 )
  " -- SD --
  ( module = 'SD'    action = 'CREATE_ORDER'          active = 'X' batchable = 'X' timeout = 120 )
  ( module = 'SD'    action = 'CHANGE_ORDER'          active = 'X' batchable = 'X' timeout = 120 )
  ( module = 'SD'    action = 'CREATE_DELIVERY'       active = 'X' batchable = 'X' timeout = 120 )
  ( module = 'SD'    action = 'CREATE_INVOICE'        active = 'X' batchable = 'X' timeout = 120 )
  ( module = 'SD'    action = 'CHECK_CONFIG'          active = 'X' batchable = ''  timeout = 30 )
  " -- FI --
  ( module = 'FI'    action = 'POST_DOCUMENT'         active = 'X' batchable = 'X' timeout = 120 )
  ( module = 'FI'    action = 'GET_BALANCE'           active = 'X' batchable = ''  timeout = 30 )
  " -- QM --
  ( module = 'QM'    action = 'CREATE_INSPECTION'     active = 'X' batchable = 'X' timeout = 120 )
  ( module = 'QM'    action = 'RECORD_RESULTS'        active = 'X' batchable = 'X' timeout = 120 )
  " -- PP --
  ( module = 'PP'    action = 'CREATE_ORDER'          active = 'X' batchable = 'X' timeout = 120 )
  ( module = 'PP'    action = 'CONFIRM_ORDER'         active = 'X' batchable = 'X' timeout = 120 )
  ( module = 'PP'    action = 'READ_BOM'              active = 'X' batchable = ''  timeout = 30 )
  ( module = 'PP'    action = 'READ_ROUTING'          active = 'X' batchable = ''  timeout = 30 )
  " -- WM --
  ( module = 'WM'    action = 'GOODS_MOVEMENT'        active = 'X' batchable = 'X' timeout = 120 )
  ( module = 'WM'    action = 'CREATE_TO'             active = 'X' batchable = 'X' timeout = 120 )
  " -- CO --
  ( module = 'CO'    action = 'CREATE_INTERNAL_ORDER' active = 'X' batchable = 'X' timeout = 120 )
  ( module = 'CO'    action = 'ACTIVITY_ALLOC'        active = 'X' batchable = 'X' timeout = 120 )
  " -- HCM --
  ( module = 'HCM'   action = 'READ_EMPLOYEE'         active = 'X' batchable = ''  timeout = 30 )
  ( module = 'HCM'   action = 'CREATE_INFOTYPE'       active = 'X' batchable = 'X' timeout = 120 )
  " -- BASIS --
  ( module = 'BASIS' action = 'CREATE_REQUEST'        active = 'X' batchable = 'X' timeout = 60 )
  ( module = 'BASIS' action = 'RELEASE_REQUEST'       active = 'X' batchable = 'X' timeout = 60 )
  ( module = 'BASIS' action = 'ST22_SCAN'             active = 'X' batchable = ''  timeout = 30 )
  ( module = 'BASIS' action = 'CODE_ANALYSIS'         active = 'X' batchable = ''  timeout = 30 )
  " -- PING (handled by abstract handler for every module) --
  ( module = 'MM'    action = 'PING'                  active = 'X' batchable = ''  timeout = 10 )
  ( module = 'SD'    action = 'PING'                  active = 'X' batchable = ''  timeout = 10 )
  ( module = 'FI'    action = 'PING'                  active = 'X' batchable = ''  timeout = 10 )
  ( module = 'QM'    action = 'PING'                  active = 'X' batchable = ''  timeout = 10 )
  ( module = 'PP'    action = 'PING'                  active = 'X' batchable = ''  timeout = 10 )
  ( module = 'WM'    action = 'PING'                  active = 'X' batchable = ''  timeout = 10 )
  ( module = 'CO'    action = 'PING'                  active = 'X' batchable = ''  timeout = 10 )
  ( module = 'HCM'   action = 'PING'                  active = 'X' batchable = ''  timeout = 10 )
  ( module = 'BASIS' action = 'PING'                  active = 'X' batchable = ''  timeout = 10 )
).

LOOP AT lt_seed INTO DATA(ls_seed).
  CLEAR ls_cfg.
  " The client key field is filled automatically from sy-mandt on MODIFY.
  ls_cfg-module    = ls_seed-module.
  ls_cfg-action    = ls_seed-action.
  ls_cfg-active    = ls_seed-active.
  ls_cfg-batchable = ls_seed-batchable.
  ls_cfg-timeout   = ls_seed-timeout.
  MODIFY zrouter_config FROM ls_cfg.
  IF sy-subrc = 0.
    lv_rows = lv_rows + 1.
  ENDIF.
ENDLOOP.

COMMIT WORK.

WRITE: / |ZROUTER_CONFIG seeded:|, lv_rows, |rows (of|, lines( lt_seed ), |).|.
