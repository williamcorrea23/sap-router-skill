# Value help

A **value help** populates the dropdown / search-help dialog when a user
fills an input field. In RAP, value helps are declared in CDS and consumed
by the Fiori UI through OData metadata.

> **Anchored to**:
> https://help.sap.com/docs/abap-cloud/abap-cds-development-user/value-help-annotations
> https://help.sap.com/docs/abap-cloud/abap-rap/value-helps

---

## 1. The three value-help flavors

| Flavor                                  | Source                                                              | When to use                                            |
|-----------------------------------------|---------------------------------------------------------------------|--------------------------------------------------------|
| **Fixed values**                        | Domain fixed values (`abap.numc` / `abap.char` with `value list`)   | Tiny, stable enums (currencies via T006, units via T006).|
| **CDS value help (recommended)**        | A CDS view marked as a value-help source.                           | Anything bigger than a domain — the default for RAP.   |
| **Search help (legacy)**                | Classic DDIC search help (`SH_…`)                                   | Only when consuming legacy data with a dedicated SH.   |

For RAP, **CDS value helps** are the strategic mechanism.

---

## 2. CDS value help — minimal example

A CDS view marked for use as a value help:

```abap
@EndUserText.label: 'Agency — value help'
@AccessControl.authorizationCheck: #NOT_REQUIRED
@Search.searchable: true
@ObjectModel.resultSet.sizeCategory: #S
define view entity I_AgencyVH
  as select from /dmo/agency
{
      @Search.defaultSearchElement: true
  key agency_id   as AgencyID,

      @Search.defaultSearchElement: true
      @Semantics.text: true
      name        as Name,

      city,
      country_code as CountryCode
}
```

Annotations to know:

| Annotation                               | Purpose                                                    |
|------------------------------------------|------------------------------------------------------------|
| `@ObjectModel.resultSet.sizeCategory`    | Hint to the consumer about result size: `#XS`, `#S`, `#M`, `#L`, `#XL`. Influences UI behavior. |
| `@Search.searchable: true`               | Marks this view as searchable (`$search` supported).       |
| `@Search.defaultSearchElement: true`     | Fields included in the default `$search` scope.            |
| `@Semantics.text: true`                  | Marks the descriptive text element.                        |

---

## 3. Binding the value help to a field

On the consuming projection:

```abap
define root view entity R_Travel
  provider contract transactional_query
  as projection on I_Travel
{
  key TravelUUID,

      @Consumption.valueHelpDefinition: [
        { entity:        { name: 'I_AgencyVH', element: 'AgencyID' },
          additionalBinding: [
            { localElement: 'CurrencyCode', element: 'CountryCurrencyCode' } ] } ]
      AgencyID,

      ...
}
```

Building blocks:

| Element                                  | Meaning                                                    |
|------------------------------------------|------------------------------------------------------------|
| `entity.name`                            | The value-help view.                                       |
| `entity.element`                         | The field returned to the consumer.                        |
| `additionalBinding`                      | Optional: pre-fill *other* fields on the consumer from the picked row. |
| `localElement` / `element`               | Mapping: local field on the consumer ↔ field on the VH.   |

The Fiori list-report / object-page automatically shows a value-help
dialog when the field's input control is clicked.

---

## 4. Composite value help (collective)

A collective value help groups multiple alternative VH sources behind one
field — the dialog has tabs.

```abap
@Consumption.valueHelpDefinition: [
  { entity: { name: 'I_AgencyVH',      element: 'AgencyID' }, label: 'Active agencies' },
  { entity: { name: 'I_AgencyArchive', element: 'AgencyID' }, label: 'Archived agencies' }
]
AgencyID,
```

---

## 5. Value help with parameters

When the VH view has CDS parameters, pass them via the binding:

```abap
@Consumption.valueHelpDefinition: [
  { entity: { name: 'I_FlightByDate', element: 'FlightID' },
    additionalBinding: [
      { localElement: 'BeginDate', element: 'p_date', usage: #FILTER_AND_RESULT } ] } ]
FlightID,
```

`usage` values:

| Value                  | Meaning                                              |
|------------------------|------------------------------------------------------|
| `#FILTER`              | Only used to filter the VH list (consumer's value → VH parameter). |
| `#RESULT`              | Only used as a return (VH field → consumer field).    |
| `#FILTER_AND_RESULT`   | Both (default).                                       |
| `#PRESELECT`           | Used to pre-fill, but consumer can edit.              |

---

## 6. Text annotation pattern

To show a descriptive text next to a key in the UI:

```abap
@ObjectModel.text.element: ['AgencyName']
@UI.textArrangement: #TEXT_FIRST
AgencyID,

@Semantics.text: true
AgencyName,
```

Combined with a value help, the field becomes searchable by name *and*
displays "AgencyName (AgencyID)" in the list. `@UI.textArrangement` values:
`#TEXT_FIRST`, `#TEXT_LAST`, `#TEXT_ONLY`, `#TEXT_SEPARATE`.

---

## 7. Reuse value helps from SAP

SAP delivers released value-help views for common reference data:

| Domain               | Released VH view (example)                              |
|----------------------|---------------------------------------------------------|
| Currency             | `I_CurrencyStdVH` / `I_CurrencyText`                    |
| Unit of measure      | `I_UnitOfMeasureStdVH`                                  |
| Country              | `I_CountryStdVH`                                        |
| Language             | `I_LanguageStdVH`                                       |
| User                 | `I_UserStdVH`                                           |

Check the released-objects view in ADT for the current catalog. Reusing
delivered VHs gives you consistent UX across apps and avoids re-inventing
domain reference data.

---

## 8. Common gotchas

- ❌ Marking the VH view's element as `key` when it isn't a real semantic
  key — confuses the consumer. The `entity.element` referenced by
  `valueHelpDefinition` should be the field actually returned to the
  consumer.
- ❌ Forgetting `@Search.searchable: true` — `$search` doesn't work, only
  exact-match filters do.
- ❌ Using `@Search.defaultSearchElement: true` on too many fields — every
  field with this flag participates in fuzzy `$search`, which gets slow.
- ❌ Mixing `usage: #FILTER` with a field that needs to come back into the
  consumer — the user picks a row, but the value isn't returned.
- ❌ Hard-coding value lists in CDS calculated elements (`case … end`)
  instead of a real value-help view — works for a handful of values but
  doesn't scale and can't be searched.

---

## 9. Anchor references

- Value-help annotations:
  https://help.sap.com/docs/abap-cloud/abap-cds-development-user/value-help-annotations
- Value helps in RAP:
  https://help.sap.com/docs/abap-cloud/abap-rap/value-helps
- Text annotations:
  https://help.sap.com/docs/abap-cloud/abap-cds-development-user/text-annotations

Related skill files: [cds-view-entity.md](cds-view-entity.md),
[cds-projection-view.md](cds-projection-view.md),
[cds-annotations.md](cds-annotations.md).
