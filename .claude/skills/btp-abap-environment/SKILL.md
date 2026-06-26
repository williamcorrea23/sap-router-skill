---
name: btp-abap-environment
description: SAP BTP ABAP Environment — ABAP Cloud projects, ADT connection, communication arrangements, service bindings, released APIs, BTP cockpit management. Use when creating ABAP Cloud projects, configuring BTP ABAP Environment, setting up ADT for Steampunk, managing service instances, or working with cloud-ABAP lifecycle.
---

# BTP ABAP Environment

SAP BTP ABAP Environment (Steampunk) — cloud-native ABAP Platform-as-a-Service on SAP BTP Cloud Foundry.

## Architecture

```
SAP BTP Subaccount
├── ABAP Environment Instance
│   ├── ABAP System (tenant)
│   │   ├── Custom ABAP code (cloud-compliant)
│   │   ├── CDS Views (only data access layer)
│   │   └── Released APIs only
│   └── Service Key (ADT connection)
├── Cloud Foundry Org/Space
└── Other BTP Services (Destination, XSUAA, etc.)
```

## Service Instance Creation

### BTP Cockpit
1. Navigate to subaccount → Service Marketplace
2. Search for "ABAP Environment"
3. Create instance with plan `standard` or `abap_cloud`

### CF CLI
```bash
cf create-service abap standard my-abap-system -c '{"size_of_runtime":1,"size_of_persistence":4}'
```

### ADT Connection
1. ADT → New ABAP Cloud Project
2. Select service key JSON from BTP Cockpit
3. Logon with ABAP cloud user (CB* or custom IAM user)

## Communication Management

### Released Communication Scenarios

| Scenario ID | Purpose | Protocol |
|---|---|---|
| SAP_COM_0001 | Foundation (basic auth + user propagation) | HTTP/RFC |
| SAP_COM_0008 | OData Services | OData V2/V4 |
| SAP_COM_0064 | RFC Destinations | RFC |
| SAP_COM_0465 | SOAP Services | SOAP/HTTP |

### Communication Arrangement (F2288 App)

```abap
" Create communication arrangement programmatically
DATA(lo_arr_factory) = cl_com_arrangement_factory=>create_instance( ).

TRY.
    DATA(lo_arr) = lo_arr_factory->create(
      iv_scenario_id  = 'SAP_COM_0008'
      iv_service_id   = 'Z_MY_ODATA_SRV'
      iv_system_id    = 'MY_RECEIVER_SYS'
    ).
    lo_arr->save( ).
  CATCH cx_com_arrangement INTO DATA(lx).
    " Handle error
ENDTRY.
```

## Service Binding Flow

```
CDS View Entity (data model)
  → Service Definition (SRVD object)
    → Service Binding (SRVB object) - OData V2/V4, REST
```

```abap
" Service Definition
DEFINE SERVICE z_my_srvd {
  EXPOSE z_i_product AS Product;
  EXPOSE z_i_salesorder AS SalesOrder;
}

" Service Binding (created via ADT wizard or generated code)
```

## Released APIs — Key Classes

| Area | Key Released Classes | Release Contract |
|---|---|---|
| HTTP Client | cl_http_destination, cl_web_http_client | C1 |
| JSON Serialization | /ui2/cl_json | C1 |
| XML Parsing | cl_xco_cp_xml | C1 |
| File Handling | cl_bc_file_upload_download | C1 (cloud-appropriate) |
| Mail | cl_bcs_mail_message | C1 |
| Database | CDS Views only | N/A (no direct table access) |
| Number Ranges | cl_numberrange_factory | C1 |
| UUID | cl_system_uuid | C1 |
| Application Log | cl_bali_log | C1 (new BAL) |
| ABAP Unit | cl_abap_unit_assert | C1 |

## Restricted APIs

In ABAP Cloud, these are NOT available:
- `OPEN SQL` on database tables → Use CDS views
- `CALL TRANSACTION` → Use released APIs or RAP actions
- `SUBMIT REPORT` → Use Application Jobs
- `FILE OPEN DATASET` → Use Document Management Service
- `Dynpro / Selection Screens` → Use Fiori Elements
- `RFC function modules (custom)` → Use released RFC scenarios
- Custom ATC exemptions → Only standard-released exceptions

## Cloud Lifecycle

```
Development (DEV tenant)
  → Transport (via CTS+ or gCTS)
    → Test (TST tenant)
      → Production (PRD tenant)
```

## Gotchas

- **Only released SAP APIs (C1 contract)** are available. Check with:
  ```abap
  cl_abap_objectdescr=>get_object_type_info( EXPORTING p_name = 'CL_HTTP_CLIENT' IMPORTING p_release_contract = DATA(lv_contract) ).
  ```
- **No custom database tables accessible via OPEN SQL** — only CDS views
- **No Dynpro screens** — UI must be Fiori Elements or custom via OData
- **Transport via gCTS** — git-based transport, not traditional CTS
- **Software component (ZLOCAL)** for local development objects

## ZROUTER Integration

ZROUTER_DISPATCH can target ABAP Cloud via:
1. HTTP calls to OData services exposed from ABAP Cloud
2. Released RFC scenarios via SAP_COM_0064
3. BTP Destination service for automated connectivity
