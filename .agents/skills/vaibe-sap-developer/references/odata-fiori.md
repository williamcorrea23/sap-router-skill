# OData V4 & Fiori Annotation Patterns
Parent skill: vaibe-sap-developer
Load when: user requests OData service exposure, Fiori Elements UI, value helps, list reports.

## Service Exposure (on projection CDS only)
```abap
@OData.publish: true
@UI.headerInfo: { typeName: 'Sales Order', typeNamePlural: 'Sales Orders' }
define root view entity ZC_SalesOrder
  as projection on ZI_SalesOrder
{
  key OrderId,
      CustomerId,
      @UI.lineItem: [{ position: 10 }]
      @UI.identification: [{ position: 10 }]
      NetAmount
}
```

## Value Help
```abap
@Consumption.valueHelpDefinition: [{ entity: { name: 'ZI_Customer', element: 'CustomerId' } }]
CustomerId;
```
Rule: value help points to interface view of the lookup entity, not its projection.

## List Report / Object Page Minimum Annotations
- `@UI.headerInfo` — required for object page title.
- `@UI.lineItem` — required for any field shown in list report table.
- `@UI.selectionField` — for filter bar fields.
- `@UI.facet` — defines object page sections (forms, tables, charts).

```abap
@UI.facet: [
  { id: 'Header', type: #COLLECTION, label: 'General', position: 10 },
  { id: 'Items', purpose: #STANDARD, type: #LINEITEM_REFERENCE,
    targetElement: '_Items', label: 'Items', position: 20 }
]
```

## Search & Filtering
```abap
@Search.searchable: true
@Search.defaultSearchElement: true
CustomerName;
```

## Common Mistake to Reject
- Publishing `@OData.publish: true` on an interface (`ZI_*`) view directly. Always route through a projection (`ZC_*`) — interface views are reuse layer, not consumption layer.
- Adding UI annotations on interface views. UI annotations belong on projection/consumption views only — keeps interface views reusable across Fiori, analytics, and integration without UI leakage.
