---
name: cds-view-entities
description: CDS View Entities — DEFINE VIEW ENTITY, DDL source, CDS annotations (@Semantics, @ObjectModel, @EndUserText), associations and compositions, path expressions, input parameters, EXTEND VIEW ENTITY, CDS hierarchy, CDS table functions, Metadata Extensions (MDE). Use when defining CDS views, writing DDL sources, annotating CDS entities for Fiori/OData, or extending SAP CDS views.
trigger:
  keywords: [CDS, DEFINE VIEW ENTITY, DDL, annotation, @Semantics, @ObjectModel, association, composition, EXTEND VIEW, Metadata Extension, MDE, table function, hierarchy]
  intent: >-
    Define CDS view entities, write DDL sources, apply annotations for Fiori/OData, and extend SAP CDS views.
---

# CDS View Entities

Core Data Services — semantic data modeling layer for S/4HANA and ABAP Cloud.

## DEFINE VIEW ENTITY

```cds
@AccessControl.authorizationCheck: #CHECK
@EndUserText.label: 'Product Master Data'
define view entity Z_I_PRODUCT
  as select from zproduct
  association [0..1] to Z_I_PLANT as _Plant on $projection.Plant = _Plant.Plant
{
  key product_guid as ProductGuid,
      material     as Material,
      material_type as MaterialType,
      description  as Description,
      plant        as Plant,
      created_at   as CreatedAt,

      _Plant
}
```

## Annotations

```cds
@AbapCatalog.sqlViewName: 'ZPRODUCTV'
@AbapCatalog.compiler.compareFilter: true
@AbapCatalog.preserveKey: true
@AccessControl.authorizationCheck: #CHECK
@EndUserText.label: 'Product List for Fiori'
@ObjectModel.representativeKey: 'Material'
@ObjectModel.semanticKey: ['Material']
@Search.searchable: true
define view entity Z_C_PRODUCT_LIST
  as select from zproduct
{
  @UI.lineItem: [{ position: 10, importance: #HIGH }]
  @UI.selectionField: [{ position: 10 }]
  key material as Material,

  @UI.lineItem: [{ position: 20 }]
  @Semantics.text: true
  description as Description,

  @UI.lineItem: [{ position: 30 }]
  material_type as MaterialType,

  @UI.hidden: true
  plant as Plant
}
```

## Association vs Composition

```cds
" Association — independent entity
association [1] to Z_I_PLANT as _Plant on $projection.Plant = _Plant.Plant

" Composition — child depends on parent
composition [0..*] of Z_I_PRODUCT_TEXT as _Text
  on $projection.ProductGuid = _Text.ProductGuid
```

## Path Expressions

```cds
" Navigate associations in CDS views directly
define view entity Z_C_PRODUCT_DETAIL
  as select from Z_I_PRODUCT
{
  key ProductGuid,
  Material,
  Description,
  _Plant.PlantName,
  _Plant.CompanyCode,
  _Text[1: spras = 'E'].ProductDescription as EnglishDescription
}
```

## Input Parameters

```cds
define view entity Z_I_PRODUCT_BY_TYPE
  with parameters
    @Consumption.defaultValue: 'FERT'
    p_material_type : matkl
  as select from zproduct
{
  key material,
  description
}
where material_type = $parameters.p_material_type

" Consumption:
" SELECT * FROM Z_I_PRODUCT_BY_TYPE(p_material_type = 'HAWA')
```

## EXTEND VIEW ENTITY

```cds
" Extend SAP standard CDS view with custom fields
extend view entity I_Product with Z_I_PRODUCT_EXT
{
  product.custom_field_1 as CustomField1,
  product.custom_field_2 as CustomField2
}
```

## CDS Hierarchy

```cds
" Parent-child hierarchy for organizational structures
define hierarchy Z_H_COSTCENTER
  with parameters
    p_controlling_area : kokrs
  as parent child hierarchy(
    source Z_I_COSTCENTER(p_controlling_area: $parameters.p_controlling_area)
    child to parent association _Parent
    start where ControllingArea = $parameters.p_controlling_area
    siblings order by CostCenter
  )
{
  key CostCenter,
  ControllingArea,
  _Parent
}
```

## Metadata Extension (MDE)

```cds
" Separate UI annotations into extension file
@Metadata.layer: #CUSTOMER
annotate view Z_C_PRODUCT_LIST with
{
  @UI.facet: [
    { id: 'General', type: #COLLECTION, label: 'General Information' },
    { id: 'Details', type: #IDENTIFICATION_REFERENCE, label: 'Details' }
  ]
  Material;

  @UI.facet: [{ id: 'General', purpose: #STANDARD }]
  Description;
}
```

## Gotchas

- **sqlViewName max 16 chars** — ABAP dictionary limit for view name
- **@AccessControl.authorizationCheck: #CHECK** requires DCL role
- **Composition = dependent lifecycle** — child deleted when parent deleted
- **Path expressions in WHERE** — use `_assoc.field` not JOIN
- **MDE annotations override CDS annotations** — layer priority: CORE → INDUSTRY → PARTNER → CUSTOMER
