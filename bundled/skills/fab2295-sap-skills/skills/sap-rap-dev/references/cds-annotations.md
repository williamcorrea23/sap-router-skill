# CDS annotations — RAP-relevant catalog

CDS annotations are the declarative glue between the CDS data model and
the RAP runtime / Fiori UI / authorization layer. This file is a curated
catalog of the annotations that matter for RAP, grouped by domain, with
short examples.

> **Anchored to**:
> https://help.sap.com/docs/abap-cloud/abap-cds-development-user/cds-annotations

---

## 1. `@UI.*` — Fiori UI shape

### 1.1 Header info

```abap
@UI: {
  headerInfo: { typeName:       'Travel',
                typeNamePlural: 'Travels',
                title:          { value: 'TravelID' },
                description:    { value: 'Description' },
                imageUrl:       'AgencyLogo' }
}
```

Shown on the Fiori object page header. `typeName` / `typeNamePlural` drive
the page title; `title` / `description` drive the main / sub-title; `imageUrl`
sources an image.

### 1.2 Line item (list-report row)

```abap
@UI.lineItem: [
  { position: 10, label: 'Travel ID' },
  { position: 20, label: 'Agency' },
  { position: 30, label: 'Status', criticality: 'OverallStatusCriticality',
    type: #AS_DATAPOINT }
]
TravelID,
```

Each annotation entry is one column. `position` sets order. `criticality`
references another element whose value (`0` neutral, `1` red, `2` yellow,
`3` green) colors the cell.

### 1.3 Identification (object page form fields)

```abap
@UI.identification: [
  { position: 10, label: 'Travel ID' },
  { position: 20, label: 'Agency' }
]
TravelID,
```

Same shape as `lineItem`, but for the object-page form.

### 1.4 Selection field (list-report filter bar)

```abap
@UI.selectionField: [ { position: 10 } ]
TravelID,
```

Filter-bar slot. `position` sets order.

### 1.5 Facet (object-page section layout)

```abap
@UI.facet: [
  { id:            'TravelHeader',
    purpose:       #STANDARD,
    type:          #IDENTIFICATION_REFERENCE,
    label:         'General',
    position:      10 },
  { id:            'Bookings',
    purpose:       #STANDARD,
    type:          #LINEITEM_REFERENCE,
    label:         'Bookings',
    position:      20,
    targetElement: '_Booking' }
]
```

Lives on the projection view as a top-level annotation (not on an element).

### 1.6 Field group

```abap
@UI.fieldGroup: [ { qualifier: 'Address', position: 10, label: 'City' } ]
City,

@UI.facet: [
  { id: 'AddressGroup',
    purpose: #STANDARD,
    type: #FIELDGROUP_REFERENCE,
    targetQualifier: 'Address',
    position: 30 }
]
```

Groups related fields under a qualifier; the facet pulls the group into
the layout.

### 1.7 Data point

```abap
@UI.dataPoint: { title:       'Total Price',
                 valueFormat: { numberOfFractionalDigits: 2 },
                 criticality: 'OverallStatusCriticality' }
TotalPrice,
```

Used in analytical / overview tiles.

### 1.8 Text arrangement

```abap
@UI.textArrangement: #TEXT_FIRST
@ObjectModel.text.element: ['AgencyName']
AgencyID,
```

`#TEXT_FIRST`, `#TEXT_LAST`, `#TEXT_ONLY`, `#TEXT_SEPARATE`. Pairs the
key with its text element from `@ObjectModel.text.element`.

### 1.9 Hidden

```abap
@UI.hidden: true
OverallStatusCriticality,
```

Hidden from the UI, still in the OData payload (useful for criticality
helpers).

---

## 2. `@Search.*`

```abap
@Search.searchable: true
define root view entity I_Travel
  as select from ztravel { … }
```

```abap
@Search.defaultSearchElement: true
@Search.fuzzinessThreshold: 0.8
@Search.ranking: #HIGH
TravelID,
```

| Annotation                            | Effect                                                             |
|---------------------------------------|--------------------------------------------------------------------|
| `@Search.searchable: true`            | Marks the view searchable (enables `$search`).                      |
| `@Search.defaultSearchElement: true`  | Field participates in default `$search` scope.                      |
| `@Search.fuzzinessThreshold`          | 0.0–1.0; lower = stricter, higher = fuzzier.                        |
| `@Search.ranking: #HIGH / #MEDIUM / #LOW` | Influences relevance scoring across fields.                     |

---

## 3. `@Consumption.*`

### 3.1 Value help

```abap
@Consumption.valueHelpDefinition: [
  { entity: { name: 'I_AgencyVH', element: 'AgencyID' },
    additionalBinding: [
      { localElement: 'CurrencyCode', element: 'CountryCurrencyCode' } ] } ]
AgencyID,
```

See [value-help.md](value-help.md) for the full pattern.

### 3.2 Filter

```abap
@Consumption.filter: { selectionType: #INTERVAL, multipleSelections: true }
BeginDate,
```

| Property             | Values                                                |
|----------------------|-------------------------------------------------------|
| `selectionType`      | `#SINGLE`, `#INTERVAL`, `#RANGE`, `#HIERARCHY_NODE`. |
| `multipleSelections` | `true` / `false`.                                     |
| `mandatory`          | `true` / `false`.                                     |
| `defaultValue`       | String (a fixed default).                             |

### 3.3 Semantic object

```abap
@Consumption.semanticObject: 'Travel'
TravelID,
```

Marks the field as a navigation source for Fiori cross-app navigation
(intent-based navigation, Cross-App Navigation).

---

## 4. `@ObjectModel.*`

| Annotation                                | Purpose                                                |
|-------------------------------------------|--------------------------------------------------------|
| `@ObjectModel.semanticKey: ['TravelID']`  | Marks a non-technical key (used by Fiori for URLs).    |
| `@ObjectModel.text.element: ['Name']`     | Links a key field to its text element.                 |
| `@ObjectModel.representativeKey: 'TravelID'` | Marks the field that represents the entity for UI. |
| `@ObjectModel.foreignKey.association: '_Agency'` | Marks the field as a foreign key for an association. |
| `@ObjectModel.virtualElementCalculatedBy: 'ABAP:ZCL_…'` | Names the ABAP class computing a virtual element. |
| `@ObjectModel.resultSet.sizeCategory: #M` | Result-size hint: `#XS`, `#S`, `#M`, `#L`, `#XL`.      |

---

## 5. `@AccessControl.*`

```abap
@AccessControl.authorizationCheck: #CHECK
define view entity I_Travel { … }
```

| Value              | Meaning                                                              |
|--------------------|----------------------------------------------------------------------|
| `#CHECK`           | DCL access control enforced on read. **Default for productive views.** |
| `#NOT_REQUIRED`    | No DCL check — view is freely readable. Use for value helps, etc.     |
| `#NOT_ALLOWED`     | Disallows access entirely except via privileged consumers.            |
| `#PRIVILEGED_ONLY` | Only privileged callers (e.g. saver classes with `RAP_AUTH_*`).       |

DCL (Data Control Language) files define the actual access rules and are
linked by name to the view.

---

## 6. `@Metadata.*`

```abap
@Metadata.allowExtensions: true             " on the view — opens it to MDEs
@Metadata.layer: #CUSTOMER                  " on the MDE — declares the layer
```

Layer order (lowest priority → highest):
`#CORE → #LOCALIZATION → #INDUSTRY → #PARTNER → #CUSTOMER`.

See [metadata-extension.md](metadata-extension.md).

---

## 7. `@Semantics.*`

| Annotation                                          | Used for                                                |
|-----------------------------------------------------|---------------------------------------------------------|
| `@Semantics.amount.currencyCode: 'CurrencyCode'`    | Marks an amount field; pairs with the currency element. |
| `@Semantics.quantity.unitOfMeasure: 'Unit'`         | Marks a quantity field; pairs with the unit element.    |
| `@Semantics.currencyCode: true`                     | Marks the currency element itself.                      |
| `@Semantics.unitOfMeasure: true`                    | Marks the unit element itself.                          |
| `@Semantics.text: true`                             | Marks a descriptive text element.                       |
| `@Semantics.user.createdBy: true`                   | Created-by audit user — RAP fills.                      |
| `@Semantics.user.lastChangedBy: true`               | Last-changed-by audit user — RAP fills.                 |
| `@Semantics.systemDateTime.createdAt: true`         | Creation timestamp — RAP fills.                         |
| `@Semantics.systemDateTime.lastChangedAt: true`     | Total-etag timestamp — RAP fills on modify.             |
| `@Semantics.systemDateTime.localInstanceLastChangedAt: true` | Local-etag timestamp — RAP fills on modify.    |
| `@Semantics.boolean: true`                          | Marks a 1-char field as Boolean.                        |

---

## 8. `@EndUserText.*`

```abap
@EndUserText.label:      'Travel ID'
@EndUserText.quickInfo:  'Unique identifier for the travel booking'
@EndUserText.heading:    'Travel ID'
TravelID,
```

Display labels / tooltips / column headings. Translatable via the
standard ABAP translation tools.

---

## 9. `@AbapCatalog.*`

| Annotation                                              | Purpose                                                  |
|---------------------------------------------------------|----------------------------------------------------------|
| `@AbapCatalog.viewEnhancementCategory: [#PROJECTION_LIST]` | Declares which `extend view entity` shapes are allowed. |
| `@AbapCatalog.preserveKey: true`                        | Preserve element names exactly in the generated OData metadata. |
| `@AbapCatalog.dataMaintenance: #LIMITED`                | Whether SE16-style data maintenance is allowed.          |
| `@AbapCatalog.deliveryClass: #A`                        | Transport / client-copy class.                           |
| `@AbapCatalog.tableCategory: #TRANSPARENT`              | Database table category for `define table`.              |
| `@AbapCatalog.compiler.compareFilter: true`             | CDS view filter optimization hint.                       |

---

## 10. Where each annotation goes

Annotations live on the artifact that owns the concern:

| Concern                                | Annotation lives on                  |
|----------------------------------------|--------------------------------------|
| UI shape (Fiori Elements)              | Projection view (`R_…`)              |
| Search (UI-facing)                     | Projection view (`R_…`)              |
| Search (interface reuse)               | Interface view (`I_…`)               |
| Access control                         | Interface view (`I_…`)               |
| Audit / ETag semantics                 | Interface view (`I_…`)               |
| Foreign keys, semantic keys            | Interface view (`I_…`)               |
| Value helps (consumer side)            | Projection view (`R_…`)              |
| Extensibility gate (`allowExtensions`) | View you want extensible             |
| Layer (`@Metadata.layer`)              | Metadata extension only              |
| Catalog / table category               | DDIC / table-entity definition       |
| Enhancement category                   | Any view that should accept `extend view` |

Putting an `@UI.*` annotation on the interface view *works* but locks all
projections to the same UI shape — keep them on the projection.

---

## 11. Common gotchas

- ❌ Forgetting `@AccessControl.authorizationCheck` on a view containing
  sensitive data — defaults to `#CHECK` but always be explicit.
- ❌ `@Search.searchable: true` without any `@Search.defaultSearchElement`
  fields — `$search` returns nothing.
- ❌ Mixing `@UI.*` annotations across two projections expecting both to
  render the same way — annotations are projection-scoped.
- ❌ `@Semantics.amount.currencyCode` referencing a field not present on the
  same view — runtime error when reading.
- ❌ Adding `@Metadata.layer: #CUSTOMER` to a customer extension that
  intends to be re-shipped as part of an industry solution — wrong layer
  ordering will result.

---

## 12. Anchor references

- CDS annotations:
  https://help.sap.com/docs/abap-cloud/abap-cds-development-user/cds-annotations
- UI annotations:
  https://help.sap.com/docs/abap-cloud/abap-cds-development-user/ui-annotations
- Search annotations:
  https://help.sap.com/docs/abap-cloud/abap-cds-development-user/search-annotations
- ObjectModel annotations:
  https://help.sap.com/docs/abap-cloud/abap-cds-development-user/objectmodel-annotations
- Semantics annotations:
  https://help.sap.com/docs/abap-cloud/abap-cds-development-user/semantics-annotations

Related skill files: [cds-view-entity.md](cds-view-entity.md),
[cds-projection-view.md](cds-projection-view.md),
[value-help.md](value-help.md),
[metadata-extension.md](metadata-extension.md).
