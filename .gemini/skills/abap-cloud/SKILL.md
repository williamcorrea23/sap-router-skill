---
name: abap-cloud
description: >-
  ABAP Cloud / Steampunk — ABAP Cloud restrictions (IF_RESTRICTED), released APIs only,
  ADT-only development, embedded Steampunk in S/4HANA, ABAP Cloud project in BTP,
  SCOPE_OPEN/CLOSE rules, class pool restrictions, no dynpro, no DB access bypass,
  cloud-ABAP lifecycle, API contract versioning, C1 release contract, SYSTEM-LOCAL license.
trigger:
  keywords: [abap-cloud, steampunk, released-api, embedded-steampunk, btp-abap, restricted-abap, api-contract, c1-release, cloud-ready, cloud-development]
  intent: >-
    ABAP Cloud development with released APIs only, ADT-only, BTP ABAP Environment, and cloud-ABAP lifecycle management.
---

# ABAP Cloud / Steampunk

Complete reference for the **ABAP for Cloud Development** language version — the restricted
ABAP dialect mandatory on SAP BTP ABAP Environment, SAP S/4HANA Cloud Public Edition, and
recommended for clean-core on-premise via embedded Steampunk. Covers the dual-pillar
restriction model (syntax subset + released-API whitelist), the release-contract system
(C0-C4), object-type and statement allowlists, migration from classic ABAP, and integration
with ZROUTER's ADT toolchain.

## Why This Matters

SAP enforces a strict boundary between custom code and SAP core in cloud ABAP systems.
Developing with the **Standard ABAP** language version on a cloud system produces a hard
syntax error at activation time. The restriction is enforced at two independent levels:

1. **Syntax restriction** — only a defined subset of ABAP statements is valid.
2. **Released-object check** — every external repository object reference (class, function
   module, CDS view, DDIC element, BAdI, table, structure, type pool, etc.) is validated
   against SAP's whitelist at syntax-check time.

There is no escape hatch. The language version is a property of the ABAP object itself and
is automatically set at creation time in cloud systems. It cannot be overridden
retroactively on SAP BTP ABAP Environment. On S/4HANA on-premise with embedded Steampunk,
developers can choose the language version per object, but once chosen, changing it
requires a formal object deletion and recreation.

## ABAP Language Versions

| Version | Environment | Assignment |
|---------|-------------|------------|
| **ABAP for Cloud Development** | SAP BTP ABAP Environment, S/4HANA Cloud Public, embedded Steampunk | Auto-set at object creation in cloud; manual choice in on-prem |
| **ABAP for Key Users** | S/4HANA Cloud, on-prem key user tools | Auto-set by key user extensibility tools |
| **Standard ABAP (Unicode)** | S/4HANA on-premise, ECC, classic ABAP systems | Default in on-prem systems |

On SAP BTP ABAP Environment, _every_ object carries the **ABAP for Cloud Development**
language version. On S/4HANA on-premise systems (2020+), objects can be created in either
Standard ABAP or ABAP for Cloud Development. The latter is the "embedded Steampunk" model
— cloud compliance inside the on-prem stack.

## The Two-Pillar Restriction Model

### Pillar 1: Restricted Syntax

Only a curated subset of the ABAP language tree is permitted. The check runs at
activation time and cannot be bypassed. The subset excludes:

- All dynpro statements (`REPORT`, `CALL SCREEN`, `LOAD-OF-PROGRAM`, `INITIALIZATION`,
  `AT SELECTION-SCREEN`, `START-OF-SELECTION`, `END-OF-SELECTION`, etc.)
- All classic list-processing statements (`WRITE`, `ULINE`, `SKIP`, `NEW-PAGE`, etc.)
- All obsolete statements (`COMPUTE`, `MOVE`, `TABLES`, `DATA … WITH HEADER LINE`,
  `DESCRIBE`, `SEARCH`, `MAXIMUM`/`MINIMUM`, `EXPORT … TO MEMORY`,
  `EXPORT … TO SHARED MEMORY`, `IMPORT … FROM MEMORY`, etc.)
- Low-level database access (`EXEC SQL`, `EXIT FROM SQL`, `OPEN CURSOR`, `CLOSE CURSOR`,
  `SELECT CLIENT SPECIFIED`, `SELECT USING CLIENT`)
- File-system operations (`OPEN DATASET`, `READ DATASET`, `TRANSFER`, `CLOSE DATASET`,
  `GET DATASET`, `DELETE DATASET`)
- Low-level system calls (`CALL 'SYSTEM'`, `SYSTEM-CALL`, `CALL CFUNCTION`)
- `GET REFERENCE OF` (replaced by `REF #( )` constructor operator)
- Classic ALV (`CL_SALV_TABLE`, `CL_GUI_ALV_GRID`, `REUSE_ALV_*` function modules)
- SAP GUI-dependent frameworks (classic dynpro, selection screens, SAPscript)

### Pillar 2: Released-Object Whitelist

Every external SAP-delivered object referenced by your code must carry a **release
contract** and must be visible to the ABAP for Cloud Development language version.
Non-released objects produce a syntax error:

```abap
" ERROR: Table SPFLI is not released for ABAP Cloud
SELECT carrid, connid FROM spfli WHERE carrid = 'LH' INTO TABLE @DATA(flights).

" OK: Released CDS view abstracts the underlying table
SELECT * FROM i_travel WHERE TravelID = @travel_id INTO TABLE @DATA(travels).
```

SAP has released thousands of CDS views (prefixed `I_*`, `C_*`, `E_*`, `R_*`, `P_*`),
interfaces, classes, and DDIC types for cloud use. The canonical reference is the
**Released Objects** tree in ADT's Project Explorer. The whitelist differs between SAP
BTP ABAP Environment and S/4HANA Cloud — the latter has a larger set because it includes
industry-specific and LoB-specific releases.

## Release Contracts (C0-C4)

Every released SAP object carries exactly one release contract that defines its stability
guarantee and compatibility rules.

| Contract | Name | Purpose | Visibility Options |
|----------|------|---------|-------------------|
| **C0** | Extend | Stability at BAdI / enhancement spots for extension | CLOUD_DEVELOPMENT, KEY_USER_APPS |
| **C1** | Use System-Internally | Stable public interface for system-internal consumption within the same AS ABAP | CLOUD_DEVELOPMENT, KEY_USER_APPS, or both |
| **C2** | Use as Remote API | Stable interface for external/remote consumption (OData, SOAP, RFC) | CLOUD_DEVELOPMENT |
| **C3** | Manage Configuration Content | Stable persistence layer for configuration content (BC set, customizing) | CLOUD_DEVELOPMENT |
| **C4** | Use in AMDP | Stable interface for ABAP-Managed Database Procedures | CLOUD_DEVELOPMENT |

### C1 Contract Rules (most common for application APIs)

C1 ("Use System-Internally") is the workhorse contract for ABAP Cloud development. Its
compatibility rules govern what an API provider may change between releases:

**Provider obligations:**
- Existing parameters, elements, and associations must not be **changed or removed**.
- Adding **optional** parameters, elements, or associations is permitted.
- Alphanumeric elements may be **lengthened** but never shortened.
- Data types of existing elements must remain **structurally compatible**.
- An already-released class method's `IMPORTING`/`EXPORTING`/`CHANGING`/`RETURNING`
  parameter list cannot be reduced.

**Consumer obligations:**
- Code must not depend on internal implementation details of a released API.
- Code must be robust against the addition of new optional parameters.
- Code should use released types rather than manually reconstructing structure shapes,
  because the structure may gain new components in a future release.

### Checking a Release Contract in ADT

Right-click any SAP-delivered object in ADT → **Properties** → **API State** tab:

```
API State:              Released
Release Contract:       C1 - Use System-Internally
Visibility:
  [x] Use in Cloud Development
  [ ] Use in Key User Apps
API Release Date:       2023-10-15
```

The **Released Objects** virtual node in the ADT Project Explorer provides a filterable
view of all released objects available on the current system, grouped by software component.

### Contract Compatibility Matrix (ATC Check `API_COMPATIBILITY`)

SAP enforces compatibility mechanically through ATC. The `API_COMPATIBILITY` check variant
validates every released API against its declared contract rules at upgrade/build time. If
SAP accidentally removes a C1 parameter, the check fails and the build is blocked — the
change never reaches a production system.

## SCOPE_OPEN / SCOPE_CLOSE and IF_RESTRICTED

These mechanisms provide controlled, traceable escape hatches for exceptional cases where
a non-released object must be accessed temporarily during a migration window.

### SCOPE_OPEN / SCOPE_CLOSE Pattern

In **Standard ABAP** language version objects (on-prem only), `SCOPE_OPEN` and
`SCOPE_CLOSE` are macros defined as part of the restrictable API infrastructure. They
toggle the restriction scope so that a block of code can temporarily reference
non-released objects:

```abap
" ONLY in Standard ABAP language version, on-premise systems
SCOPE_OPEN.
  " Block where non-released APIs can be called
  CALL FUNCTION 'Z_SOME_UNRELEASED_FM'
    EXPORTING
      iv_param = lv_value.
SCOPE_CLOSE.
```

- `SCOPE_OPEN` disables the restriction check for the subsequent block.
- `SCOPE_CLOSE` re-enables the restriction check.
- The pair must be balanced — an open without a close produces a syntax error.
- Nesting is not permitted — you cannot `SCOPE_OPEN` inside another `SCOPE_OPEN`.
- These macros are **not available in ABAP for Cloud Development** language version. They
  exist solely in Standard ABAP for migration-window scenarios.
- In BTP ABAP Environment, there is no `SCOPE_OPEN` — all code must use released APIs
  unconditionally.

### IF_RESTRICTED Interface

`IF_RESTRICTED` (`if_restricted`) is a marker/tagging interface in the ABAP class library.
Classes implementing `IF_RESTRICTED` signal to the restriction framework that they contain
code that may reference non-released APIs:

```abap
CLASS zcl_my_restricted_class DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC
  IMPLEMENTING if_restricted.

  PUBLIC SECTION.
    METHODS do_restricted_work.
ENDCLASS.

CLASS zcl_my_restricted_class IMPLEMENTATION.
  METHOD do_restricted_work.
    " This method may access non-released APIs
    " Only callable from Standard ABAP language version
    CALL FUNCTION 'Z_LEGACY_HELPER' ...
  ENDMETHOD.
ENDCLASS.
```

- Classes implementing `IF_RESTRICTED` get a relaxed syntax check for the body.
- They remain **invisible** to ABAP for Cloud Development callers — a cloud object cannot
  instantiate an `IF_RESTRICTED` class.
- On SAP BTP ABAP Environment, `IF_RESTRICTED` objects do not exist — the interface
  itself is not released, so it cannot even be referenced.

## Object-Type Restrictions

### Not Supported in ABAP for Cloud Development

| Object Type | Reason |
|-------------|--------|
| Executable programs (type `1` / reports) | Depends on dynpro, selection screens, list output |
| Module pools (type `M` / dynpro) | SAP GUI screen technology |
| Function groups (type `F`) supporting unreleased FMs | Only individual released FMs are callable |
| Classic class pools (type `K`) | Replaced by global ABAP classes |
| Type groups (type `TYPE_POOL`) | Use released type pools or free type definitions |
| Classic BSP applications | Replaced by RAP-based Fiori apps |
| Web Dynpro ABAP | Replaced by Fiori |
| Enhancement implementations against non-released spots | Only released BAdI definitions are available |

### Fully Supported

| Object Type | Notes |
|-------------|-------|
| Global ABAP classes (type `CLAS`) | Primary development container |
| Global ABAP interfaces (type `INTF`) | |
| CDS views / entities (type `DDLS`) | The only data-access layer |
| CDS abstract entities | No persistence, pure modeling |
| CDS table functions | AMDP-backed if needed |
| CDS custom entities | For external data sources |
| Behavior definitions (type `BDEF`) | RAP transactional model |
| Behavior implementations (type `BIL`) | |
| Service definitions (type `SRVD`) | |
| Service bindings (type `SRVB`) | OData V2, OData V4 |
| DDIC tables / structures / data elements (type `TABL`/`DTEL`/`DOMA`) | Custom only (type `Z*`/`Y*`); SAP DDIC is accessed via released CDS views |
| Released function modules | Called individually, not via function group |

## Statement-Level Restrictions (Detailed)

### Forbidden Statements

```
Classic dynpro:
  REPORT, CALL SCREEN, SET SCREEN, LEAVE SCREEN, LEAVE TO SCREEN,
  LOAD-OF-PROGRAM, INITIALIZATION, AT SELECTION-SCREEN, AT LINE-SELECTION,
  AT USER-COMMAND, START-OF-SELECTION, END-OF-SELECTION, TOP-OF-PAGE,
  END-OF-PAGE, AT PFnn, CALL DIALOG

Classic list output:
  WRITE, ULINE, SKIP, NEW-PAGE, NEW-LINE, FORMAT, SET BLANK LINES,
  SET MARGIN, RESERVE, BACK, POSITION, SCROLL, SET PF-STATUS,
  SET TITLEBAR, SET LEFT SCROLL-BOUNDARY

Low-level database:
  EXEC SQL, EXIT FROM SQL, OPEN CURSOR, CLOSE CURSOR, FETCH NEXT CURSOR,
  SELECT CLIENT SPECIFIED, SELECT USING CLIENT, NATIVE SQL

File system:
  OPEN DATASET, CLOSE DATASET, READ DATASET, TRANSFER, GET DATASET,
  DELETE DATASET

Obsolete (even in Standard ABAP):
  COMPUTE, MOVE, MOVE-CORRESPONDING (as statement), ADD, SUBTRACT,
  MULTIPLY, DIVIDE, ADD-CORRESPONDING, SUBTRACT-CORRESPONDING,
  TABLES, DATA ... WITH HEADER LINE, DESCRIBE (as statement),
  DO ... VARYING, SEARCH, CONDENSE ... NO-GAPS (as statement),
  GET REFERENCE OF, EXPORT ... TO MEMORY, EXPORT ... TO SHARED MEMORY,
  IMPORT ... FROM MEMORY, IMPORT ... FROM SHARED MEMORY,
  CALL 'SYSTEM', SYSTEM-CALL, CALL CFUNCTION
```

### Allowed Statements (with Modern Patterns)

```abap
" ---------- Data declarations ----------
DATA lv_name TYPE string.
DATA lt_table TYPE STANDARD TABLE OF string.
TYPES: BEGIN OF ty_struct,
         field1 TYPE string,
         field2 TYPE i,
       END OF ty_struct.

" ---------- String operations ----------
" Use string templates, not CONCATENATE
lv_name = |Hello { lv_prefix } { lv_suffix }|.
" Use && for concatenation
lv_name = lv_prefix && lv_suffix.

" ---------- Internal table operations ----------
" Use lines( ), not DESCRIBE TABLE ... LINES
DATA(lv_count) = lines( lt_table ).
" Use VALUE #( ), not APPEND
lt_table = VALUE #( ( `line1` ) ( `line2` ) ).
" Use REF #( ), not GET REFERENCE OF
DATA(lr_ref) = REF #( lv_value ).

" ---------- Modern arithmetic ----------
lv_result = lv_a + lv_b.         " Not ADD lv_b TO lv_a
lv_result = lv_result * 2.       " Not MULTIPLY lv_result BY 2

" ---------- ABAP SQL ----------
" Only against released CDS views or custom tables
SELECT * FROM i_travel WHERE TravelID = @id INTO TABLE @DATA(lt_travels).
INSERT INTO zcustom_table VALUES @( ls_row ).
DELETE FROM zcustom_table WHERE key = @key.

" Dynamic SQL: compiles but is checked at runtime by cl_abap_dyn_prg
DATA(lv_tabname) = 'ZCUSTOM_TABLE'.
SELECT * FROM (lv_tabname) INTO TABLE @DATA(lt_dyn_result).

" ---------- Exception handling (modern) ----------
TRY.
    DATA(lo_obj) = NEW zcl_my_class( ).
    lo_obj->do_something( ).
  CATCH cx_root INTO DATA(lx_error).
    out->write( lx_error->get_text( ) ).
ENDTRY.

" ---------- Functional methods on released classes ----------
DATA(lv_date) = cl_abap_context_info=>get_system_date( ).
DATA(lv_time) = cl_abap_context_info=>get_system_time( ).
DATA(lv_tzone) = cl_abap_context_info=>get_user_time_zone( ).

" ---------- Dynamic programming (via released API) ----------
DATA(lv_valid) = cl_abap_dyn_prg=>check_table_name_str(
  val = 'ZCUSTOM_TABLE' ).
```

## Key Released SAP API Replacements

When migrating classic ABAP to ABAP Cloud, replace these common non-released APIs:

| Classic ABAP (Not Released) | ABAP Cloud Replacement (Released, C1) |
| --- | --- |
| `sy-datum`, `sy-uzeit`, `sy-zonlo` | `cl_abap_context_info=>get_system_date( )`, `get_system_time( )`, `get_user_time_zone( )` |
| `IF_HTTP_CLIENT` | `IF_WEB_HTTP_CLIENT` |
| `CL_HTTP_CLIENT=>CREATE( )` | `CL_WEB_HTTP_CLIENT_MANAGER=>get_http_client( )` |
| `CALL FUNCTION ... STARTING NEW TASK` | `CL_ABAP_PARALLEL` (implements `IF_ABAP_PARALLEL`) |
| `CL_SALV_TABLE=>FACTORY( )` | RAP-based Fiori list report or ABAP2UI5 |
| `BAL_LOG_CREATE`, `BAL_DB_SAVE` | `CL_BALI_LOG`, `CL_BALI_LOG_DB`, `CL_BALI_OBJECT_HANDLER` |
| `SM36`/`SM37` job scheduling | `CL_APJ_RT_API=>schedule_job( )` with `CL_APJ_DT_CATALOG` |
| `ENQUEUE_E_TABLE`, `DEQUEUE_E_TABLE` | `CL_ABAP_LOCK_OBJECT_FACTORY` |
| `NUMBER_GET_NEXT` (SNRO) | `CL_NUMBERRANGE_OBJECTS`, `CL_NUMBERRANGE_RUNTIME` |
| `REPLACE ALL OCCURRENCES OF REGEX` | `CL_ABAP_MATCHER` or `XCO_CP_REGULAR_EXPRESSION` |
| Direct `E070`/`E071` transport access | `XCO_CP_CTS`, `XCO_CP_TRANSPORT` classes |
| `GUILT_TITLE` / `F4IF_*` (F4 help) | Released CDS value helps via annotations |
| `BAPI_MATERIAL_SAVEREPLICA` | RAP BO `I_PRODUCTTP_2` behavior implementation |
| `BAPI_SALESORDER_CREATEFROMDAT2` | RAP BO `I_SALESORDERTP` behavior implementation |
| `CDHDR`/`CDPOS` direct table access | Generated `*CL_*_CHDO` change-document classes, `CL_CHDO_READ_TOOLS` |
| `SO_NEW_DOCUMENT_SEND_API1` | `CL_BCS_MAIL_MESSAGE` (released) |
| `GUI_DOWNLOAD`, `GUI_UPLOAD` | `CL_ABAP_FILE_UTILITIES` or XCO file I/O |

## Data Access Strategy

### The Golden Rule

**Never read SAP-delivered database tables directly in ABAP Cloud.** Always use the
released CDS view that abstracts the table.

```abap
" WRONG — table KNA1 is not released
SELECT SINGLE name1 FROM kna1 WHERE kunnr = '1000' INTO @DATA(lv_name).

" CORRECT — CDS view I_Customer is released (C1)
SELECT SINGLE CustomerName FROM i_customer WHERE Customer = '1000'
  INTO @DATA(lv_name).
```

### Common CDS View Replacements

| SAP Table (not released) | Released CDS View |
| --- | --- |
| `KNA1` (Customer Master) | `I_CUSTOMER` |
| `LFA1` (Supplier Master) | `I_SUPPLIER` |
| `MARA` (Material Master) | `I_PRODUCT` |
| `MAKT` (Material Descriptions) | `I_PRODUCTTEXT` |
| `VBAK` (Sales Order Header) | `I_SALESDOCUMENT` |
| `VBAP` (Sales Order Item) | `I_SALESDOCUMENTITEM` |
| `EKKO` (Purchase Order Header) | `I_PURCHASEORDER` |
| `EKPO` (Purchase Order Item) | `I_PURCHASEORDERITEM` |
| `BKPF` (Accounting Document Header) | `I_JOURNALENTRY` |
| `BSEG` (Accounting Document Item) | `I_JOURNALENTRYITEM` |
| `MARC` (Plant Data) | `I_PRODUCTPLANT` |
| `MBEW` (Material Valuation) | `I_PRODUCTVALUATION` |
| `PA0001` (HR Master Record) | `I_WORKFORCEPERSON` (S/4HANA Cloud) |

### Custom Tables

Custom DDIC tables (`Z*`/`Y*`) are fully accessible via standard ABAP SQL within the
same software component. Cross-software-component access to custom tables requires the
target table to be released with a C1 contract.

## ABAP Cloud Lifecycle and API Contract Versioning

### Deprecation Flow

SAP follows a structured deprecation lifecycle for released APIs:

1. **Released (active)** — API is fully supported and guaranteed for the declared
   compatibility scope.
2. **Deprecated** — API is still functional but a successor has been declared. Deprecated
   APIs produce an ATC warning, not an error. SAP commits to supporting the deprecated
   API for at least one release cycle after deprecation is announced.
3. **Not Released (decommissioned)** — The API is removed from the released-object
   whitelist. Any code referencing it will fail syntax check after the next upgrade.

### Deprecated API Successor Information

In ADT, when you open the **API State** tab for a deprecated object, the successor is
listed explicitly. Example:

```
API State:     Deprecated
Successor:     CL_UOM_CONVERSION
Deprecated Since: SAP S/4HANA 2023
```

### Upgrade Stability

The release-contract system ensures that ABAP Cloud code survives system upgrades without
modification:

- SAP guarantees forward-compatibility for all C1-released APIs within a major release.
- The `API_COMPATIBILITY` ATC check prevents SAP from accidentally shipping breaking
  changes.
- A customer's custom code that uses only released APIs can be activated on the upgraded
  system without modification.

### Software Component Boundaries

In SAP BTP ABAP Environment and S/4HANA Cloud, custom code lives in a dedicated
customer software component (`ZLOCAL` or similar). SAP-delivered code lives in separate
software components (`SAP_BASIS`, `SAP_ABA`, industry components). The released-object
check operates across software-component boundaries: a Z-object can only reference
SAP-delivered objects that carry a release contract with visibility `CLOUD_DEVELOPMENT`.

## Cloud-Readiness Verification

### For Classic ABAP Systems (ATC Check)

To evaluate whether existing custom code can move to ABAP Cloud:

1. In ADT, right-click a class/package → **Run As** → **ABAP Test Cockpit With...**
2. Select check variant: **`ABAP_CLOUD_READINESS`**
3. Results appear in the **ATC Problems** view

Common violations found:
- Direct read of database table `KNA1` → replace with CDS view `I_CUSTOMER`
- Usage of `CALL FUNCTION 'Z_*'` where the FM is not released → migrate to released class
- `sy-datum` reference → replace with `cl_abap_context_info=>get_system_date( )`
- `WRITE` statement → replace with `out->write( )` or Fiori UI
- Usage of `IF_HTTP_CLIENT` → replace with `IF_WEB_HTTP_CLIENT`

### For New Development (Language Version Switch)

On S/4HANA on-premise, you can switch an existing object's language version:

1. Right-click object → **Properties** → **General**
2. Click **Edit** next to **ABAP Language Version**
3. Select **ABAP for Cloud Development**
4. Activate — any violations will produce hard activation errors

## ADT-Only Development Rule

ABAP Cloud development is **exclusively via ADT (ABAP Development Tools for Eclipse)**.
On SAP BTP ABAP Environment:

- There is **no SAP GUI access** to the ABAP system.
- Transaction codes (`SE80`, `SE24`, `SE38`, `SE11`, `SE37`, `SM36`, `SM37`, etc.) do not
  exist.
- The ABAP Development Tools (Eclipse) are the only supported IDE.
- The ADT back-end system exposes a dedicated communication scenario
  (`SAP_COM_0510` for ABAP development).
- On embedded Steampunk (S/4HANA on-prem), the SAP GUI exists for the Standard ABAP
  context, but objects with the ABAP for Cloud Development language version must be edited
  in ADT.

## RAP: The Only Transactional Programming Model

The **ABAP RESTful Application Programming Model (RAP)** is the mandatory transactional
framework for ABAP Cloud:

```
CDS Data Model  →  Behavior Definition  →  Behavior Implementation  →  Service Definition  →  Service Binding
    (DDLS)            (BDEF)                   (BIL classes)              (SRVD)               (SRVB → OData)
```

Non-RAP patterns (BSP, Web Dynpro, classic function-module-based services) are not
available in ABAP for Cloud Development. For simple non-transactional output, use the
`IF_OO_ADT_CLASSRUN` interface:

```abap
CLASS zcl_my_cloud_app DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.
ENDCLASS.

CLASS zcl_my_cloud_app IMPLEMENTATION.
  METHOD if_oo_adt_classrun~main.
    out->write( |ABAP Cloud is running| ).
    out->write( |System date: { cl_abap_context_info=>get_system_date( ) }| ).
  ENDMETHOD.
ENDCLASS.
```

Press F9 in ADT to execute. Output appears in the ADT console.

## XCO Library (Extension Components)

The XCO library (`xco_cp=>...`) is a released family of classes providing standard
operations without needing to memorize individual released class names:

```abap
" --- Date/Time operations ---
DATA(lv_date_iso) = xco_cp=>sy->date( xco_cp_time=>time_zone->user
  )->as( xco_cp_time=>format->iso_8601_extended )->value.

DATA(lv_time_iso) = xco_cp=>sy->time( xco_cp_time=>time_zone->user
  )->as( xco_cp_time=>format->iso_8601_extended )->value.

" --- Transport requests ---
DATA(lo_transport) = xco_cp_cts=>transport->for(
  xco_cp_abap_sql=>constraint->equal(
    iv_field = 'TRKORR'
    iv_value = 'DEVK900123'
  )
).

" --- Regular expressions ---
DATA(lo_regex) = xco_cp_regular_expression=>pcire=>greedy( iv_pattern = '[A-Z]{2}\d{3}' ).
```

## Common Gotchas

1. **Type incompatibility from future API evolution:** Defining `TYPE RANGE OF i` manually
   produces a syntax warning because it may diverge from `IF_ABAP_PROB_TYPES=>int_range`.
   Always use the released type.

2. **Dynamic SQL still compiles:** Dynamic SQL (`SELECT ... FROM (lv_tabname)`) compiles
   cleanly but fails at runtime if the target table is not released. Validate dynamically
   with `CL_ABAP_DYN_PRG=>check_table_name_str( )`.

3. **`SY-` fields are whitelisted on BTP:** Some `sy-*` fields are still readable but
   produce a warning. Avoid them — use `CL_ABAP_CONTEXT_INFO` or XCO instead.

4. **`BREAK-POINT` compiles but is meaningless:** In BTP ABAP Environment, there is no
   interactive debugger you can attach via SAP GUI. ADT-based debugging is available but
   with limitations.

5. **Function groups cannot be created:** Individual released function modules can be
   called, but you cannot navigate to or create a function group. Use global classes
   instead.

6. **No `COMMIT WORK` with `WAIT`:** On BTP ABAP Environment, `COMMIT WORK AND WAIT` is
   restricted. Use RAP's save sequence instead.

7. **SEGW is fully unavailable:** Migration path: keep the underlying DDIC tables, create
   CDS views on top, and expose them as OData services via RAP (behavior definition +
   service definition + service binding).

8. **`SUBMIT` is not available:** You cannot call one program from another via `SUBMIT`.
   Use class method calls or RAP actions instead.

9. **Authorization checks:** In ABAP Cloud, authority checks are declarative — defined
   via CDS access controls (`DCLS`) or behavior-definition authorization masters. Manual
   `AUTHORITY-CHECK` is not supported in the ABAP for Cloud Development language version
   on BTP (it is allowed on embedded Steampunk for migration).

10. **Obsolete statement treatment differs:** `ABAP for Key Users` is stricter on obsolete
    statements than `ABAP for Cloud Development` — the latter is more lenient to ease
    migration of existing on-prem code.

## Integration with ZROUTER

The ZROUTER orchestrator (see `sap-router-orchestrator` SKILL.md) interacts with ABAP
Cloud systems through two paths:

### ARC-1 ADT Path (Direct Source Code)

For ABAP Cloud systems, ZROUTER uses the ARC-1 ADT connector to:
- Read/write ABAP source in cloud objects (classes, CDS views, behavior definitions)
- Run syntax checks against the ABAP for Cloud Development language version
- Search for released APIs in the **Released Objects** virtual tree
- Verify API release state (contract, visibility, deprecation status)

```python
# sap_router.py routing logic for cloud objects
if target_system.abap_language_version == 'CLOUD_DEVELOPMENT':
    route_to_adt(source_operation)  # ADT is the only path
else:
    route_to_rfc(batch_operation)   # ZROUTER RFC for classic operations
```

### ZROUTER RFC Path (Batch Operations)

When operating on **embedded Steampunk** systems (S/4HANA on-prem with mixed language
versions), ZROUTER may route classic ABAP batch operations through the ZROUTER function
group while routing cloud-object operations through ADT:

| Operation | Language Version | Path |
|-----------|-----------------|------|
| Read cloud CDS view source | ABAP for Cloud Development | ARC-1 ADT |
| Activate cloud class | ABAP for Cloud Development | ARC-1 ADT |
| Mass read classic tables | Standard ABAP | ZROUTER RFC |
| ST22 dump analysis | Standard ABAP | ZROUTER RFC |
| BAdI implementation scan | Standard ABAP | ZROUTER RFC |

### MEMORY.md Context

The ZROUTER `MEMORY.md` captures ABAP Cloud-related session state:
- Current system's ABAP language version profile
- Released SAP objects previously verified
- ATC cloud-readiness results cached from prior runs
- Software component boundaries detected

## SAP Documentation References

- [ABAP Cloud: Background Concepts and Overview](https://help.sap.com/docs/abap-cloud/abap-cloud/public-released-apis)
- [Released APIs | ABAP Keyword Documentation](https://help.sap.com/doc/abapdocu_cp_index_htm/CLOUD/en-US/abenabap_api_release.html)
- [ABAP Language Versions](https://help.sap.com/doc/abapdocu_cp_index_htm/CLOUD/en-US/ABENABAP_LANGUAGE_VERSIONS.html)
- [Contract C1: Use System-Internally](https://help.sap.com/docs/abap-cloud/abap-development-tools-user-guide/use-system-internally-c1)
- [Compatibility Checks for Released APIs](https://help.sap.com/doc/abapdocu_cp_index_htm/CLOUD/en-US/ABENRESTRICTED_APIS_ATC_COMPA.html)
- [Release Contracts](https://help.sap.com/doc/abapdocu_816_index_htm/8.16/en-US/ABENABAP_RELEASE_CONTRACTS.html)
- [Cloud-Optimized ABAP Language](https://help.sap.com/docs/abap-cloud/abap-cloud/abap-language)
- [Working with ABAP for Cloud Development](https://help.sap.com/docs/ABAP_PLATFORM_NEW/b5670aaaa2364a29935f40b16499972d/ef0301f6b908409c8e0802270a96a316.html)
- [SAP Community: Restricted ABAP for BTP ABAP Environment](https://community.sap.com/t5/technology-blog-posts-by-sap/restricted-abap-for-sap-btp-abap-environment/bc-p/13448419)
- [SAP-samples: ABAP Cheat Sheets — ABAP for Cloud Development](https://github.com/SAP-samples/abap-cheat-sheets/blob/main/19_ABAP_for_Cloud_Development.md)
- [ABAP Language Versions — SAP Community FAQ](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-sap/abap-language-versions-faqs/bc-p/13537679)

## Related Skills

- `released-abap-classes` — detailed catalog of released SAP classes, XCO library, C0-C4 contract reference
- `btp-abap-environment` — BTP ABAP Environment instance creation, ADT connection, service bindings
- `atc-cloudification` — ATC check variants, cloud-readiness validation, exemption management
- `clean-abap` — clean ABAP coding standards applicable inside the cloud restriction envelope
- `abap-sql-amdp` — ABAP SQL patterns and AMDP for CDS table functions
- `sap-bapi-integration` — BAPI/RFC integration for systems where remote calls bridge cloud/on-prem
