---
name: released-abap-classes
description: SAP released ABAP APIs — C1/C2/C3/sAPIsC0 release contracts, released class hierarchies (cl_abap*, cl_system*, xco*, cl_bali*), API contract verification, ABAP Cloud compatibility checking, SAP API release lifecycle. Use when checking if a SAP class is released for customer use, selecting APIs for ABAP Cloud development, or verifying release contracts.
trigger:
  keywords: [released, abap, classes, apis, release-contracts, c1, c2, cloud, compatibility, sap-classes]
  intent: >-
    Use when checking SAP class release contracts (C0-C4), verifying ABAP Cloud API compatibility, or selecting released APIs for development.
---

# SAP Released ABAP APIs

SAP API release contracts and compatible ABAP APIs for cloud development.

## Release Contracts

| Contract | Meaning | Stability |
|---|---|---|
| C1 | Released for customer use | Stable — SAP guarantees compatibility |
| C2 | Released with restrictions | Stable but usage-limited |
| C3 | Released for system-internal use | May change |
| [sAPIsC0] | Cloud Platform released | Stable for ABAP Cloud |

## Key Released Class Hierarchies

### CL_ABAP_* — Core ABAP Runtime
```abap
" Character/string utilities
cl_abap_char_utilities=>newline
cl_abap_char_utilities=>horizontal_tab

" Math operations
cl_abap_math=>round( iv_number = 3.14159 iv_decimals = 2 )  " → 3.14

" UUID generation
DATA(lv_uuid) = cl_system_uuid=>create_uuid_c32_static( ).

" Random integers
DATA(lv_random) = cl_abap_random_int=>create( seed = cl_abap_random=>seed( )
  min = 1 max = 100 )->get_next( ).
```

### XCO — eXtensible Component Objects
```abap
" CDS metadata access
DATA(lo_cds) = xco_cp_cds=>object_for( 'Z_I_PRODUCT' ).
DATA(lv_exists) = lo_cds->exists( ).

" Package metadata
DATA(lo_package) = xco_cp_abap_repository=>object->devc->for( '$ZFOO' ).
DATA(lt_objects) = lo_package->list_objects( )->get( ).

" DDIC table library
DATA(lo_table) = xco_cp_ddl=>field( 'MARA' )->field( 'MATNR' ).
DATA(lv_type) = lo_table->content( )->get_data_type( ).
```

### CL_HTTP_CLIENT / CL_WEB_HTTP_CLIENT
```abap
" Released HTTP client (C1 contract)
DATA(lo_client) = cl_web_http_client_manager=>create_by_http_destination(
  i_destination = cl_http_destination_provider=>create_by_cloud_destination(
    i_name = 'MY_S4_SYSTEM' ) ).
DATA(lo_request) = lo_client->get_http_request( ).
DATA(lo_response) = lo_client->execute( i_method = if_web_http_client=>get ).
DATA(lv_body) = lo_response->get_text( ).
```

### /UI2/CL_JSON
```abap
" Released JSON serialization (C1)
DATA(lv_json) = /ui2/cl_json=>serialize( data = ls_data ).
/ui2/cl_json=>deserialize( EXPORTING json = lv_json CHANGING data = ls_data ).
```

### CL_BCS_MAIL_MESSAGE (Mail)
```abap
" Released mail client (C1)
DATA(lo_mail) = cl_bcs_mail_message=>create_instance( ).
lo_mail->set_sender( 'noreply@company.com' ).
lo_mail->add_recipient( 'user@company.com' ).
lo_mail->set_subject( 'Report Ready' ).
lo_mail->set_body( 'Your report is attached.' ).
lo_mail->send( ).
```

### CL_BALI_LOG (Application Log — new)
```abap
" New BAL API (C1 in ABAP Cloud)
DATA(lo_log) = cl_bali_log=>create( ).
lo_log->add_item( item = cl_bali_message_item=>create(
  severity = if_bali_constants=>c_severity_error
  id = 'ZROUTER' number = '001' variable_1 = 'Failed' ) ).
lo_log->save( ).
```

## Checking API Release Status

```abap
" Programmatic check
cl_abap_objectdescr=>get_object_type_info(
  EXPORTING p_name = 'CL_WEB_HTTP_CLIENT'
  IMPORTING p_release_contract = DATA(lv_contract) ).
" lv_contract = 'C1' (released) or 'C3' (not released for customer)
```

## Not Released (Avoid in ABAP Cloud)

| Class | Alternative |
|---|---|
| CL_GUI_FRONTEND_SERVICES | Not available in cloud |
| CL_ABAP_BROWSER | Not cloud-compatible |
| CL_SALV_TABLE | Use CDS + Fiori |
| Function modules (custom) | Released RFC scenarios only |
| Direct DB access | CDS views only |

## Gotchas

- **C1 does not mean "no changes"** — SAP may deprecate C1 APIs with 12-month notice
- **XCO library is the future direction** for DDIC/programmatic metadata
- **cl_http_client** is NOT released — use **cl_web_http_client** instead
- **/ui2/cl_json** is released but not in all C1 contract documents
