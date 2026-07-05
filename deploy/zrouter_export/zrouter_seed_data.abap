*&---------------------------------------------------------------------*
*& Report ZROUTER_SEED_DATA — Seed ZROUTER_CONFIG with default actions
*& Execute AFTER creating DDIC tables and all ZROUTER classes
*&---------------------------------------------------------------------*
REPORT zrouter_seed_data.

START-OF-SELECTION.
  WRITE: / 'Seeding ZROUTER_CONFIG with default actions...'.

  " MM actions
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'MM' action = 'CREATE_MATERIAL' active = 'X' batchable = 'X' timeout = 60 ) ).
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'MM' action = 'CHANGE_MATERIAL' active = 'X' batchable = 'X' timeout = 60 ) ).
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'MM' action = 'GET_MATERIAL'    active = 'X' batchable = '' timeout = 30 ) ).
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'MM' action = 'CREATE_PO'       active = 'X' batchable = 'X' timeout = 60 ) ).
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'MM' action = 'CHANGE_PO'       active = 'X' batchable = 'X' timeout = 60 ) ).
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'MM' action = 'CHECK_CONFIG'    active = 'X' batchable = '' timeout = 10 ) ).

  " SD actions
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'SD' action = 'CREATE_ORDER'    active = 'X' batchable = 'X' timeout = 60 ) ).
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'SD' action = 'CHANGE_ORDER'    active = 'X' batchable = 'X' timeout = 60 ) ).
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'SD' action = 'CREATE_DELIVERY' active = 'X' batchable = 'X' timeout = 60 ) ).
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'SD' action = 'CREATE_INVOICE'  active = 'X' batchable = 'X' timeout = 60 ) ).

  " FI actions
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'FI' action = 'POST_DOCUMENT'   active = 'X' batchable = 'X' timeout = 60 ) ).
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'FI' action = 'GET_BALANCE'     active = 'X' batchable = '' timeout = 30 ) ).

  " QM actions
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'QM' action = 'CREATE_INSPECTION' active = 'X' batchable = 'X' timeout = 60 ) ).
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'QM' action = 'RECORD_RESULTS'  active = 'X' batchable = '' timeout = 60 ) ).

  " PP actions
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'PP' action = 'CREATE_ORDER'    active = 'X' batchable = 'X' timeout = 60 ) ).
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'PP' action = 'CONFIRM_ORDER'   active = 'X' batchable = '' timeout = 60 ) ).
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'PP' action = 'READ_BOM'        active = 'X' batchable = '' timeout = 30 ) ).

  " WM actions
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'WM' action = 'GOODS_MOVEMENT'  active = 'X' batchable = 'X' timeout = 60 ) ).
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'WM' action = 'CREATE_TO'       active = 'X' batchable = '' timeout = 60 ) ).

  " CO actions
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'CO' action = 'CREATE_INTERNAL_ORDER' active = 'X' batchable = 'X' timeout = 60 ) ).
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'CO' action = 'ACTIVITY_ALLOC'  active = 'X' batchable = '' timeout = 60 ) ).

  " HCM actions
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'HCM' action = 'READ_EMPLOYEE'  active = 'X' batchable = '' timeout = 30 ) ).
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'HCM' action = 'CREATE_INFOTYPE' active = 'X' batchable = '' timeout = 60 ) ).

  " BASIS actions
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'BASIS' action = 'CREATE_REQUEST'  active = 'X' batchable = '' timeout = 60 ) ).
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'BASIS' action = 'RELEASE_REQUEST' active = 'X' batchable = '' timeout = 60 ) ).
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'BASIS' action = 'ST22_SCAN'       active = 'X' batchable = '' timeout = 30 ) ).
  INSERT zrouter_config FROM @( VALUE #(
    client = sy-mandt module = 'BASIS' action = 'CODE_ANALYSIS'   active = 'X' batchable = '' timeout = 60 ) ).

  COMMIT WORK.

  WRITE: / 'Seed complete. 28 actions registered across 9 modules.',
         / 'Verify: SE16N -> ZROUTER_CONFIG'.
