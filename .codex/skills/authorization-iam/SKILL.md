---
name: authorization-iam
description: Authorization and IAM patterns — AUTHORITY-CHECK syntax, auth object creation (SU21), role design (PFCG), S/4HANA IAM business roles and catalogs, restrictions, CDS access control (DCL), OData authorization, BTP XSUAA integration. Use when implementing AUTHORITY-CHECK, designing roles, creating DCL sources, or configuring IAM in S/4HANA.
---

# Authorization and IAM

SAP authorization concepts from classic ABAP to S/4HANA IAM.

## Classic AUTHORITY-CHECK

```abap
" Check authorization before sensitive operation
AUTHORITY-CHECK OBJECT 'M_MATE_MAN'
  ID 'ACTVT' FIELD '01'
  ID 'WERKS' FIELD lv_plant.

IF sy-subrc <> 0.
  RAISE EXCEPTION TYPE cx_zrouter
    EXPORTING mv_text = |No authorization for plant { lv_plant }|.
ENDIF.
```

## Auth Object Creation (SU21)

```abap
" Custom auth object: ZROUTER
" Fields:
"   ACTVT — Activity (01=Create, 02=Change, 03=Display, 06=Delete)
"   MODULE — Module filter (MM, SD, FI, ...)

AUTHORITY-CHECK OBJECT 'ZROUTER'
  ID 'ACTVT' FIELD '03'
  ID 'MODULE' FIELD 'MM'.

IF sy-subrc = 0.
  " User has display auth for MM module
ENDIF.
```

## Role Design (PFCG)

```
Role: ZROUTER_MM_DISPLAY
├── Authorization Object: ZROUTER
│   ├── ACTVT = 03 (Display)
│   └── MODULE = MM
└── Authorization Object: S_DEVELOP
    ├── ACTVT = 03
    └── DEVCLASS = ZROUTER*

Role: ZROUTER_MM_FULL
├── Authorization Object: ZROUTER
│   ├── ACTVT = * (All activities)
│   └── MODULE = MM
```

## S/4HANA IAM

### Business Catalogs
```
SAP Business Catalog (SAP_MM_BC_PURCHASING_PC)
  ├── Restrictions:
  │   ├── Plant: 1000, 2000
  │   └── Purchasing Group: P01, P02
  └── Assigned to Business Role: Z_PURCHASER
```

### Business Role
```
Business Role: Z_PURCHASER (ZBR_PURCHASER)
├── Business Catalogs:
│   ├── SAP_MM_BC_PURCHASING_PC
│   └── SAP_FI_BC_GL_POST
└── Restrictions:
    └── Company Code: 1000 (overlay restriction)
```

## CDS Access Control (DCL)

```cds
@EndUserText.label: 'Access control for Product CDS'
@MappingRole: true
define role Z_I_PRODUCT {
  grant select on Z_I_PRODUCT
    where ( plant ) = aspect pfcg_auth( 'M_MATE_WRK', werks, actvt = '03' );
}
```

## OData Authorization

```abap
" OData service with auth check at entity level
METHOD products_get_entity.
  AUTHORITY-CHECK OBJECT 'M_MATE_WRK'
    ID 'ACTVT' FIELD '03'
    ID 'WERKS' FIELD io_tech_request_context->get_parameter( 'WERKS' ).
  IF sy-subrc <> 0.
    RAISE EXCEPTION TYPE /iwbep/cx_mgw_auth.
  ENDIF.
ENDMETHOD.
```

## BTP XSUAA Integration

```json
// xs-security.json
{
  "scopes": [
    { "name": "$XSAPPNAME.MM.Read", "description": "Read MM data" },
    { "name": "$XSAPPNAME.MM.Write", "description": "Write MM data" }
  ],
  "role-templates": [
    { "name": "MM_User", "scope-references": ["$XSAPPNAME.MM.Read"] },
    { "name": "MM_Admin", "scope-references": ["$XSAPPNAME.MM.Read","$XSAPPNAME.MM.Write"] }
  ]
}
```

## Gotchas

- **sy-subrc = 0** means authorized. Non-zero = not authorized (or auth object not maintained)
- **AUTHORITY-CHECK always succeeds** if auth object is not in user profile — check with SU53
- **Business catalogs are SAP-delivered** — create custom catalogs via IAM Information System (SUI)
- **DCL roles are CDS-level** — separate from ABAP AUTHORITY-CHECK
