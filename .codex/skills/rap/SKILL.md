---
name: rap
description: RESTful ABAP Programming (RAP) — managed and unmanaged scenarios, behavior definitions (BDEF), behavior implementations, EML (Entity Manipulation Language), determinations, validations, actions, draft handling, side effects, authorization, numbering, feature control, lock handling. Use when implementing RAP business objects, writing behavior implementations, using EML, or designing RAP managed scenarios.
---

# RESTful ABAP Programming (RAP)

Modern ABAP programming model for S/4HANA and ABAP Cloud.

## Architecture Layers

```
┌─────────────────────────────────────┐
│         Service Binding (OData V4)  │  UI Layer
├─────────────────────────────────────┤
│    Service Definition (SRVD)        │
├─────────────────────────────────────┤
│  Behavior Implementation (ABAP)     │  Transactional Layer
├─────────────────────────────────────┤
│  Behavior Definition (BDEF)         │
├─────────────────────────────────────┤
│  CDS Data Model (View Entity)       │  Data Layer
├─────────────────────────────────────┤
│  Database Table (DDIC)              │
└─────────────────────────────────────┘
```

## Behavior Definition (BDEF)

```abap
" Managed scenario — framework handles CRUD
managed implementation in class zbp_i_product unique;

define behavior for z_i_product alias Product
persistent table zproduct
lock master
authorization master ( instance )
etag master LocalChangedTime
{
  create;
  update;
  delete;

  field (mandatory) MaterialType, Description;
  field (readonly) ProductGuid;

  determination setDescription on modify { create; }
  validation checkMaterialType on save { create; update; }
  action cancelProduct result [1] $self;

  mapping for zproduct
    {
      ProductGuid    = product_guid;
      Material       = material;
      MaterialType   = material_type;
      Description    = description;
    }
}
```

## Behavior Implementation

```abap
CLASS lhc_product DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    METHODS setdescription FOR DETERMINE ON MODIFY
      IMPORTING keys FOR product~setdescription.
    METHODS checkmaterialtype FOR VALIDATE ON SAVE
      IMPORTING keys FOR product~checkmaterialtype.
    METHODS cancelproduct FOR MODIFY
      IMPORTING keys FOR ACTION product~cancelproduct RESULT result.
ENDCLASS.

CLASS lhc_product IMPLEMENTATION.
  METHOD setdescription.
    READ ENTITIES OF z_i_product IN LOCAL MODE
      ENTITY product FIELDS ( description ) WITH CORRESPONDING #( keys )
      RESULT DATA(lt_products).
    MODIFY ENTITIES OF z_i_product IN LOCAL MODE
      ENTITY product UPDATE
      FIELDS ( description )
      WITH VALUE #( FOR ls IN lt_products
        ( %tky = ls-%tky description = |Product: { ls-description }| ) ).
  ENDMETHOD.

  METHOD checkmaterialtype.
    READ ENTITIES OF z_i_product IN LOCAL MODE
      ENTITY product FIELDS ( materialtype ) WITH CORRESPONDING #( keys )
      RESULT DATA(lt_products).
    LOOP AT lt_products INTO DATA(ls).
      IF ls-materialtype = 'ZXX'.
        APPEND VALUE #( %tky = ls-%tky ) TO failed-product.
        APPEND VALUE #( %tky = ls-%tky
          %msg = new_message( id = 'ZROUTER' number = '001' severity = 'E' )
        ) TO reported-product.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD cancelproduct.
    MODIFY ENTITIES OF z_i_product IN LOCAL MODE
      ENTITY product UPDATE
      FIELDS ( status )
      WITH VALUE #( FOR ls IN keys
        ( %tky = ls-%tky status = 'CANCELLED' ) ).
    READ ENTITIES OF z_i_product IN LOCAL MODE
      ENTITY product ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT result.
  ENDMETHOD.
ENDCLASS.
```

## EML (Entity Manipulation Language)

```abap
" Create
MODIFY ENTITIES OF z_i_product
  ENTITY product CREATE
  FIELDS ( material materialtype description )
  WITH VALUE #( ( %cid = 'CID1' material = 'MAT001' materialtype = 'FERT'
                  description = 'Test Product' ) )
  MAPPED DATA(ls_mapped)
  FAILED DATA(ls_failed)
  REPORTED DATA(ls_reported).

" Read
READ ENTITIES OF z_i_product
  ENTITY product ALL FIELDS
  WITH VALUE #( ( productguid = 'ABC123' ) )
  RESULT DATA(lt_products).

" Update
MODIFY ENTITIES OF z_i_product
  ENTITY product UPDATE
  FIELDS ( description )
  WITH VALUE #( ( %tky-productguid = 'ABC123' description = 'Updated' ) )
  FAILED ls_failed
  REPORTED ls_reported.

" Delete
MODIFY ENTITIES OF z_i_product
  ENTITY product DELETE
  WITH VALUE #( ( %tky-productguid = 'ABC123' ) ).
```

## Managed vs Unmanaged

| Feature | Managed | Unmanaged |
|---|---|---|
| CRUD | Framework handles | Manual (SAVE method) |
| Draft | Built-in | Manual |
| Lock | Auto (lock master) | Manual (ENQUEUE) |
| Numbering | Built-in (early/late) | Manual |
| When to use | Greenfield, ABAP Cloud | Complex legacy integration |

## Gotchas

- **BDEF names**: behavior definition name = CDS view name (Z_I_PRODUCT)
- **EML is always AUTHORITY-CHECK free** — authorization is in BDEF layer
- **%tky** is the temporal key — not the business key
- **Draft table** auto-created with name = CDS view + 'D'
