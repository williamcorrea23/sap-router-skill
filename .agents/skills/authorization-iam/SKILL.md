---
name: authorization-iam
description: >-
  SAP authorization and IAM — AUTHORITY-CHECK, auth objects (SU21), roles (PFCG),
  S/4HANA IAM business roles/catalogs, CDS DCL access control, OData auth, BTP XSUAA.
  Use when implementing AUTHORITY-CHECK, designing roles, creating DCL sources, or
  configuring IAM in S/4HANA or BTP.
trigger:
  keywords:
    - AUTHORITY-CHECK
    - authorization object
    - PFCG
    - SU01
    - SU21
    - SU53
    - S_TABU_DIS
    - auth check
    - role design
    - DCL access control
    - IAM business role
    - XSUAA
    - pfcg_auth
  file_patterns:
    - "*.abap"
    - "*.cds"
    - "xs-security.json"
  intent: "implement or troubleshoot SAP authorization, roles, or access control"
---

# SAP Authorization & IAM

Authorization in SAP is a chain: **user → role → profile → auth object → field values**.
Every `AUTHORITY-CHECK` walks this chain at runtime.

## Prerequisites

- SAP GUI or ADT access (SU01, SU21, PFCG, SU53)
- ABAP development rights (S_DEVELOP with ACTVT 03+)
- For S/4HANA IAM: Fiori launchpad admin access
- For BTP: `cf` CLI + XSUAA service instance

## 1. AUTHORITY-CHECK (ABAP)

Always check `sy-subrc` immediately — no exceptions.

```abap
" Check before any sensitive operation
AUTHORITY-CHECK OBJECT 'M_MATE_MAN'
  ID 'ACTVT' FIELD '01'        " 01=Create 02=Change 03=Display 06=Delete
  ID 'WERKS' FIELD lv_plant.

IF sy-subrc <> 0.
  RAISE EXCEPTION TYPE cx_zrouter
    EXPORTING mv_text = |No authorization for plant { lv_plant }|.
ENDIF.
```

**Custom auth object** (create via SU21):

```abap
" Object: ZROUTER | Class: ZR | Fields: ACTVT, MODULE
AUTHORITY-CHECK OBJECT 'ZROUTER'
  ID 'ACTVT' FIELD '03'
  ID 'MODULE' FIELD 'MM'.
IF sy-subrc = 0.
  " User has display auth for MM module
ENDIF.
```

## 2. S_TABU_DIS — Table-Level Authorization

Controls access via SM30, SM31, SE16, SE16N.

```abap
AUTHORITY-CHECK OBJECT 'S_TABU_DIS'
  ID 'ACTVT' FIELD '03'          " 03=Display 02=Change
  ID 'DICBERICH' FIELD lv_group. " Authorization group (e.g. 'ZMM')
IF sy-subrc <> 0.
  " Denied — user cannot view tables in group lv_group
ENDIF.
```

> Find auth group of a table: SE11 → table → Delivery/Maintenance tab → Auth. Group.
> Tables without a group use `&NC&`.

## 3. Role Design (PFCG)

```
Role: ZROUTER_MM_DISPLAY
├── ZROUTER: ACTVT=03, MODULE=MM
└── S_DEVELOP: ACTVT=03, DEVCLASS=ZROUTER*

Role: ZROUTER_MM_FULL
├── ZROUTER: ACTVT=*, MODULE=MM
└── S_TABU_DIS: ACTVT=02, DICBERICH=ZMM
```

PFCG workflow: `1. SU24 → maintain default auth values → 2. PFCG → single role → add transactions → generate profile → 3. User tab → assign users → User Comparison (full) → 4. Verify: SU53 / SUIM`

> **Rule**: Always run user comparison after assigning users. Uncompared roles are inactive.

## 4. S/4HANA IAM (Business Roles & Catalogs)

S/4HANA replaces PFCG roles with **business roles** built from **business catalogs**.

```
Business Role: ZBR_PURCHASER
├── Catalog: SAP_MM_BC_PURCHASING_PC  (Restrictions: Plant=1000,2000)
├── Catalog: SAP_FI_BC_GL_POST        (Restrictions: CompanyCode=1000)
└── Assigned via Maintain Business Roles app
```

Create custom catalogs via **IAM Information System** (app `SUI`).
> Business catalogs are SAP-delivered. Never modify standard catalogs — create overlays instead.

## 5. CDS Access Control (DCL)

Row-level security at the database layer. Separate from ABAP `AUTHORITY-CHECK`.

```cds
@EndUserText.label: 'Access control for Product CDS'
@MappingRole: true
define role Z_I_PRODUCT {
  grant select on Z_I_PRODUCT
    where ( plant ) = aspect pfcg_auth( 'M_MATE_WRK', werks, actvt = '03' );
}
```

**CAP @restrict annotations** (Node.js/Java services):

```cds
service CatalogService @(requires: 'authenticated-user') {
  entity Products @(restrict: [
    { grant: 'READ' },
    { grant: 'WRITE', to: 'Vendor' }
  ]) { /*...*/ }

  entity Orders @(restrict: [
    { grant: '*', to: 'Customer', where: (CreatedBy = $user) }
  ]) { /*...*/ }
}
```

## 6. OData Service Authorization

```abap
METHOD products_get_entity.
  AUTHORITY-CHECK OBJECT 'M_MATE_WRK'
    ID 'ACTVT' FIELD '03'
    ID 'WERKS' FIELD io_tech_request_context->get_parameter( 'WERKS' ).
  IF sy-subrc <> 0.
    RAISE EXCEPTION TYPE /iwbep/cx_mgw_auth.
  ENDIF.
ENDMETHOD.
```

> Also maintain `S_SERVICE` auth object for the OData service IWFND node.

## 7. BTP XSUAA Integration

```json
{
  "scopes": [
    { "name": "$XSAPPNAME.MM.Read",  "description": "Read MM data" },
    { "name": "$XSAPPNAME.MM.Write", "description": "Write MM data" }
  ],
  "role-templates": [
    { "name": "MM_User",  "scope-references": ["$XSAPPNAME.MM.Read"] },
    { "name": "MM_Admin", "scope-references": ["$XSAPPNAME.MM.Read","$XSAPPNAME.MM.Write"] }
  ]
}
```

Generate from CAP model: `cds add xsuaa`

## Pitfalls

- **sy-subrc semantics**: `0` = authorized. Non-zero = denied **or auth object not in profile**. Auth object absent from user's profile returns non-zero.
- **Missing auth object**: If an auth object is not maintained anywhere, `AUTHORITY-CHECK` always fails. Use SU53 to diagnose.
- **SU53 only shows LAST failed check** — instruct users to run it immediately after denial.
- **DCL roles != ABAP auth checks**: CDS DCL filters rows at DB level; AUTHORITY-CHECK validates in ABAP. Both needed for full coverage.
- **User comparison forgotten**: PFCG roles without comparison are inactive.
- **SAP_ALL in production**: Never assign SAP_ALL in PRD. Use SAP_NEW only temporarily during upgrades.
- **Wildcard `*` in ACTVT**: Grants all activities including delete. Use sparingly.
- **SU24 defaults skipped**: Not maintaining SU24 means PFCG won't propose auth objects automatically.

## Verification

```bash
# SU53  → Last failed auth check (run immediately after denial)
# SUIM  → User → Roles → By role name
# SU56  → Display user's authorization buffer
# ST01  → Authorization trace (activate, reproduce, analyze)
# PFCG  → Role → Authorizations tab → green status = generated
# ABAP: AUTHORITY-CHECK OBJECT obj ID 'ACTVT' FIELD act → sy-subrc=0 = authorized
# BTP:  cf security groups; cf roles --user <email>
```
