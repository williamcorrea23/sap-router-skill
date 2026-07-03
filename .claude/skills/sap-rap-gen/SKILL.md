---
name: sap-rap-gen
description: Generate complete SAP RAP business objects — BDEF, behavior implementation, CDS views, service definition, service binding. Managed/unmanaged, draft-enabled, custom entities.
trigger:
  keywords:
    - generate rap
    - rap business object
    - behavior definition
    - bdef
    - cds view entity
    - rap service
    - draft enabled bo
    - restful application programming model
  intent: >-
    Generate complete SAP RAP business objects with BDEF, behavior implementation, CDS views, and service bindings.
  patterns:
    - "generate.*rap.*bo"
    - "create.*behavior definition"
    - "scaffold.*rap"
    - "rap.*managed.*implementation"
---

# SAP RAP Generator

RAP = CDS data model + behavior definition + behavior implementation + service exposure.
One root entity per BO. Compositions link child nodes. Managed = runtime handles CRUD automatically.
## Prerequisites

- ABAP 7.57+ (Cloud or on-premise S/4HANA 2020+); ADT with RAP support
- Authorization to create DDIC tables, CDS views, BDEF, classes, service definitions
- Existing persistent table (e.g. `ZPRODUCT`) with key fields

## Architecture (generate in this order)

```
ZPRODUCT (DB table)
  └─ Z_I_PRODUCT   → CDS View Entity (data model, root)
  └─ Z_R_PRODUCT   → Behavior Definition (transactional contract)
  └─ ZBP_I_PRODUCT → Behavior Implementation (ABAP class)
  └─ Z_C_PRODUCT   → CDS Projection (consumption layer)
  └─ Z_SRV_PRODUCT → Service Definition + Binding (OData V4)
  └─ Z_D_PRODUCT   → Draft table (only if draft-enabled)
```

## Step 1 — CDS View Entity

```cds
@AccessControl.authorizationCheck: #CHECK
@EndUserText.label: 'Product Master Data'
@ObjectModel.semanticKey: ['Material']
define view entity Z_I_PRODUCT
  as select from zproduct
  composition [0..*] of Z_I_STOCK as _Stock
{
  key product_guid    as ProductGuid,
      material        as Material,
      @ObjectModel.mandatory: true
      material_type   as MaterialType,
      @Search.defaultSearchElement: true
      description     as Description,
      plant           as Plant,
      @Semantics.systemDate.createdAt: true
      created_at      as CreatedAt,
      @Semantics.systemDate.lastChangedAt: true
      last_changed_at as LastChangedAt,
      _Stock
}
```

## Step 2 — Behavior Definition (Managed + Draft)

```abap
managed implementation in class zbp_i_product unique;
strict(2);

define behavior for z_i_product alias Product
persistent table zproduct
draft table z_d_product
lock master total etag last_changed_at
authorization master ( instance )
etag master last_changed_at
{
  create;
  update;
  delete;

  field (mandatory) material_type, description;
  field (readonly) product_guid, created_at;
  field (readonly:update) material;

  determination set_audit_fields on modify { create; update; }

  mapping for zproduct {
    product_guid = product_guid; material = material;
    material_type = material_type; description = description;
    plant = plant; created_at = created_at;
    last_changed_at = last_changed_at;
  }
}
```

## Step 3 — Behavior Implementation

```abap
CLASS lhc_product DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    METHODS set_audit_fields FOR DETERMINE ON MODIFY
      IMPORTING keys FOR product~set_audit_fields.
ENDCLASS.

CLASS lhc_product IMPLEMENTATION.
  METHOD set_audit_fields.
    READ ENTITIES OF z_i_product IN LOCAL MODE
      ENTITY product FIELDS ( created_at last_changed_at )
      WITH CORRESPONDING #( keys )
      RESULT DATA(lt_products).

    MODIFY ENTITIES OF z_i_product IN LOCAL MODE
      ENTITY product UPDATE FIELDS ( created_at last_changed_at )
      WITH VALUE #( FOR ls IN lt_products (
        %tky = ls-%tky
        created_at = COND #( WHEN ls-created_at IS INITIAL
                             THEN utclong_current( ) ELSE ls-created_at )
        last_changed_at = utclong_current( ) ) ).
  ENDMETHOD.
ENDCLASS.
```

## Step 4 — Projection View

```cds
@AccessControl.authorizationCheck: #CHECK
@Metadata.allowExtensions: true
define root view entity Z_C_PRODUCT as projection on Z_I_PRODUCT
{
  key ProductGuid, Material, MaterialType, Description,
      Plant, CreatedAt, LastChangedAt,
      _Stock : redirected to Z_C_STOCK
}
```

## Step 5 — Service Definition + Binding

```cds
@EndUserText.label: 'Product Service'
define service Z_SRV_PRODUCT { expose Z_C_PRODUCT as Product; }
```

Bind: right-click service definition → **New Service Binding** → `OData V4 - UI` → Activate.

## Managed vs Unmanaged

- **Managed**: runtime auto-implements CRUD, draft, locking, ETag. Use for greenfield tables.
- **Unmanaged**: you write `READ`, `CREATE`, `UPDATE`, `DELETE`, `SAVE`. Use for legacy tables, external APIs, multi-table LUWs.

## Quick Commands

```bash
# Trigger generation (skill auto-activates)
"generate RAP BO for Product with fields: product_guid(UUID,key), material(CHAR18), description(CHAR40), draft enabled"

# Check existing BDEF
aibap: get_object_info(name="Z_I_PRODUCT")

# Activate all generated objects (dependency order)
aibap: activate_objects(["Z_I_PRODUCT","Z_C_PRODUCT","Z_R_PRODUCT","ZBP_I_PRODUCT","Z_SRV_PRODUCT"])

# Run unit tests on behavior implementation
aibap: run_unit_tests(["ZBP_I_PRODUCT"])
```

## Pitfalls

- **BDEF name = CDS view name** — linked automatically at activation, no manual mapping.
- **strict(2)** requires S/4HANA 2021+; use `strict(1)` for 2020 compat.
- **Draft table**: must match active table fields + draft-specific columns (`mandt`, `draftentityoperationcode`). Generate via ADT "Generate Draft Table".
- **MAPPING clause**: required when CDS aliases differ from DB column names; omit only if identical.
- **Projection view**: must redirect compositions via `: redirected to` — missing redirect breaks activation.
- **Service binding**: `OData V4 - UI` for Fiori Elements, `OData V4 - API` for programmatic.
- **Late numbering**: managed BOs with UUID keys use late numbering — keys assigned in save sequence.
- **Never** use `READ ENTITIES` outside `IN LOCAL MODE` inside determinations — breaks transactional buffer.
- **Never** call `COMMIT ENTITIES` from within a determination or validation method.

## Verification

```abap
" 1. Activate in order: Table → CDS → BDEF → Impl → Projection → Svc Def → Svc Binding
" 2. Preview service binding → OData $metadata must list entity + draft actions
" 3. Test draft flow: Create → Edit → Save → Verify active record in ZPRODUCT
" 4. Run behavior unit tests: aibap: run_unit_tests(["ZBP_I_PRODUCT"])
" 5. Verify ETag: LastChangedAt must update on each modify
```

## Custom Entity (query-only, no persistence)
```cds
@ObjectModel.query.implementedBy: 'ABAP:ZCL_CUSTOM_QUERY'
define custom entity Z_C_CUSTOM_SEARCH {
  key search_id : sysuuid_x16; search_term : string; result_count : int4;
}
```
