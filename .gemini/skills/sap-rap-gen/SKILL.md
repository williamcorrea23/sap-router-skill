---
name: sap-rap-gen
description: SAP RAP Generator — generate complete RAP business objects (BDEF, behavior implementation, CDS views, service definition, service binding) from templates or specifications, RAP BO scaffolding, CRUD and transactional patterns, managed vs unmanaged scenario generation, draft-enabled BO generation, custom entity and value help generation. Use when generating RAP business objects from scratch, scaffolding RAP services, creating RAP CRUD applications, or accelerating RAP development with code generation.
---

# SAP RAP Generator

Generate complete RAP business objects from specifications or templates — accelerates RAP development from days to minutes.

## What It Generates

```
RAP Business Object "Z_I_PRODUCT"
├── Z_I_PRODUCT (CDS View Entity) — Data model
├── Z_C_PRODUCT (CDS Projection View) — Consumption layer
├── Z_R_PRODUCT (Behavior Definition) — Transactional model
├── ZBP_I_PRODUCT (Behavior Implementation) — ABAP logic
├── Z_SRV_PRODUCT (Service Definition) — Service interface
├── Z_SRV_PRODUCT (Service Binding) — OData V4 endpoint
└── Z_D_PRODUCT (Draft table, if draft enabled) — Draft persistence
```

## Generating a Managed BO

### From Specification (using this skill)

```
You: "generate RAP BO for Product entity with fields:
      product_guid (UUID, key), material (CHAR18, semantic key),
      material_type (CHAR4, mandatory), description (CHAR40),
      plant (CHAR4), created_at (timestamp)
      Enable: create, update, delete, draft, ETag, numbering"

Skill: sap-rap-gen

Generated output:
  - Z_I_PRODUCT CDS view entity
  - Behavior definition (managed, draft enabled, late numbering)
  - Behavior implementation (determinations for audit fields)
  - Service definition + binding recommendation
```

### Generated Behavior Definition

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

  mapping for zproduct
    {
      product_guid  = product_guid;
      material      = material;
      material_type = material_type;
      description   = description;
      plant         = plant;
      created_at    = created_at;
      last_changed_at = last_changed_at;
    }
}
```

### Generated CDS View Entity

```cds
@AbapCatalog.sqlViewName: 'ZPRODUCTV'
@AbapCatalog.compiler.compareFilter: true
@AbapCatalog.preserveKey: true
@AccessControl.authorizationCheck: #CHECK
@EndUserText.label: 'Product Master Data'
@ObjectModel.representativeKey: 'Material'
@ObjectModel.semanticKey: ['Material']
define view entity Z_I_PRODUCT
  as select from zproduct
{
  key product_guid   as ProductGuid,
      material       as Material,
      @ObjectModel.mandatory: true
      material_type  as MaterialType,
      @Search.defaultSearchElement: true
      description    as Description,
      plant          as Plant,
      @Semantics.systemDate.createdAt: true
      created_at     as CreatedAt,
      @Semantics.systemDate.lastChangedAt: true
      last_changed_at as LastChangedAt
}
```

### Generated Behavior Implementation

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
      ENTITY product UPDATE
      FIELDS ( created_at last_changed_at )
      WITH VALUE #( FOR ls IN lt_products (
        %tky = ls-%tky
        created_at = COND #( WHEN ls-created_at IS INITIAL
          THEN utclong_current( ) ELSE ls-created_at )
        last_changed_at = utclong_current( )
      ) ).
  ENDMETHOD.
ENDCLASS.
```

## Generated Service Definition

```cds
@EndUserText.label: 'Product Service'
define service Z_SRV_PRODUCT {
  expose Z_C_PRODUCT as Product;
  expose Z_I_PLANT as Plant;       // Value help
  expose I_MaterialType as MaterialType;  // Value help
}
```

## Managed vs Unmanaged Decision

| Scenario | Use Managed | Use Unmanaged |
|---|---|---|
| Greenfield (new table) | ✅ | ❌ |
| Standard CRUD with draft | ✅ | ❌ |
| Legacy table with complex validation | ❌ | ✅ |
| External API calls in save sequence | ❌ | ✅ (custom SAVE) |
| Multi-table atomics (LUW) | ❌ | ✅ |
| Custom locking beyond ETag | ❌ | ✅ |

## Draft-Enabled BO

```abap
" BDEF with draft
draft table z_d_product

" Generated draft actions:
" - Edit (create active instance from draft)
" - Activate (promote draft to active)
" - Discard (delete draft)
" - Resume (edit existing draft)
" - Prepare (create draft from active)
```

## Custom Entity (Non-persistent)

```cds
" For value help and custom UI entities
@ObjectModel.query.implementedBy: 'ABAP:ZCL_CUSTOM_QUERY'
define custom entity Z_C_CUSTOM_SEARCH
{
  key search_id   : sysuuid_x16;
      search_term : string;
      result_count: int4;
}
```

## Quick Start Commands

```bash
# Generate RAP BO from spec (skill auto-triggered)
"generate RAP BO for <entity> with fields: <field_list>"

# Check existing BDEF
aibap: get_object_info(name="Z_I_PRODUCT")

# Activate generated objects
aibap: activate_objects(["Z_I_PRODUCT","Z_C_PRODUCT","Z_R_PRODUCT"])

# Run ABAP Unit on generated BO
aibap: run_unit_tests(["ZBP_I_PRODUCT"])
```

## Gotchas

- **Managed BO uses late numbering** by default for UUID keys
- **Draft table auto-named**: CDS view name + '_D' → Z_D_PRODUCT
- **Strict(2) enables all RAP features** — use strict(1) for S/4HANA 2020 compat
- **Service binding type**: OData V4 UI for Fiori Elements, OData V4 API for programmatic
- **BDEF name = CDS view name** — automatically linked at activation
- **MAPPING clause**: maps CDS field names to DB table field names (must match if identical)
