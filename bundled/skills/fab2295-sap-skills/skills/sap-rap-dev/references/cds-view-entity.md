# CDS view entity

The **CDS view entity** (`define view entity`) is the modern, RAP-supported
flavor of CDS view. It replaces the legacy `define view` (which generated a
classic SQL `DDLS` view artifact). Every new RAP BO is built on view
entities.

> **Anchored to**:
> https://help.sap.com/docs/abap-cloud/abap-cds-development-user/cds-view-entity
> and the BDL (Behavior Definition Language) doc set.

---

## 1. When to use which CDS object

| You need…                                                  | Use                          |
|------------------------------------------------------------|------------------------------|
| The data layer of a RAP BO                                 | `define table entity` *or* a DDIC `define table` + view entity on top |
| Internal model of a BO (the BO's stable shape)             | `define view entity` or `define root view entity` |
| Exposed/UI shape of a BO for a service                     | `define root view entity … as projection on …` (see [cds-projection-view.md](cds-projection-view.md)) |
| Reusable read-only data source for other CDS / analytics   | `define view entity`         |
| A legacy classic view (don't author new ones)              | `define view` — **avoid for new code** |
| Calculations the DB cannot push down                       | `define table function`      |
| Hierarchies                                                | `define hierarchy`           |

For RAP BOs, the rule is simple: **always `define view entity`** (with `root`
when it's the BO root). `define view` is legacy.

---

## 2. Anatomy of a view entity

```abap
@AccessControl.authorizationCheck: #CHECK
@EndUserText.label: 'Travel — interface view'
@Metadata.allowExtensions: true
@AbapCatalog.viewEnhancementCategory: [#NONE]
define root view entity I_Travel
  as select from ztravel
  composition [0..*] of I_Booking as _Booking
  association [0..1] to I_Agency  as _Agency  on $projection.AgencyID  = _Agency.AgencyID
  association [0..1] to I_Customer as _Customer on $projection.CustomerID = _Customer.CustomerID
{
  key travel_uuid                    as TravelUUID,
      travel_id                      as TravelID,
      agency_id                      as AgencyID,
      customer_id                    as CustomerID,
      begin_date                     as BeginDate,
      end_date                       as EndDate,
      @Semantics.amount.currencyCode: 'CurrencyCode'
      booking_fee                    as BookingFee,
      @Semantics.amount.currencyCode: 'CurrencyCode'
      total_price                    as TotalPrice,
      currency_code                  as CurrencyCode,
      overall_status                 as OverallStatus,
      description                    as Description,
      @Semantics.user.lastChangedBy: true
      last_changed_by                as LastChangedBy,
      @Semantics.systemDateTime.lastChangedAt: true
      last_changed_at                as LastChangedAt,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true
      local_last_changed_at          as LocalLastChangedAt,
      _Booking, _Agency, _Customer
}
```

Building blocks:

| Element                              | Meaning                                                              |
|--------------------------------------|----------------------------------------------------------------------|
| `define root view entity`            | Marks this view as a BO root (composition origin).                   |
| `define view entity`                 | A non-root view entity (composition child, or stand-alone reuse).    |
| `as select from <source>`            | The data source (table, table entity, another view).                 |
| `composition [0..*] of <child>`      | Declares a child entity in the same BO.                              |
| `association [0..1] to <other>`      | Reference to a *different* BO or reuse entity.                       |
| `as parent <root>` (on child)        | Required mirror on the composition target.                           |
| `key <field>`                        | A key element. At least one key is required.                         |
| `<alias> as <name>`                  | Renames the field as exposed by the view.                            |
| `$projection.<field>`                | Field qualifier in `on` conditions — refers to the projected name.   |

---

## 3. Root vs. non-root view entity

```abap
define root view entity I_Travel             " root of the Travel BO
  as select from ztravel
  composition [0..*] of I_Booking as _Booking
{ ... }

define view entity I_Booking                 " child of the Travel BO
  as select from zbooking
  association to parent I_Travel as _Travel on $projection.TravelUUID = _Travel.TravelUUID
{ ... }
```

- A BO has **exactly one** root view entity.
- Every composition child has an `association to parent` referencing the root
  of the composition tree.
- Compositions never cross BO boundaries — for that, use `association to`.

---

## 4. Associations vs. compositions

|                    | Composition                                  | Association                                |
|--------------------|----------------------------------------------|--------------------------------------------|
| Belongs to same BO | Yes (target is part of the BO tree)          | No (target is a different BO or reuse)     |
| RAP cascading      | CRUD / lock / draft cascade to the target    | No cascade — target is independent         |
| Direction          | Parent → child only                          | Either direction (usually navigation only) |
| Target requirement | Child must have `association to parent`      | Target need not back-reference             |
| BDEF impact        | Child appears under `association <name> { … }` in the BDEF | Read-only navigation; no behavior plumbing |

A typical Travel BO:

```
Travel  (root)
  composition  ─▶  Booking
                     composition  ─▶  BookingSupplement

Travel  association  ─▶  Agency      (different BO — Agency)
Travel  association  ─▶  Customer    (different BO — Customer)
```

---

## 5. Calculated / virtual elements

### 5.1 Calculated element (computed at view runtime)

```abap
define view entity I_Travel
  as select from ztravel
{
  key travel_uuid as TravelUUID,
      total_price as TotalPrice,
      currency_code as CurrencyCode,

      // Calculated at SQL push-down
      total_price * 1.16 as TotalPriceGross,

      // Conditional
      case overall_status
        when 'O' then 'Open'
        when 'A' then 'Accepted'
        when 'X' then 'Cancelled'
      end as OverallStatusText
}
```

### 5.2 Virtual element (computed in ABAP via exit class)

```abap
define view entity R_Travel
  as projection on I_Travel
{
  key TravelUUID,
      TotalPrice,
      CurrencyCode,

      @ObjectModel.virtualElementCalculatedBy: 'ABAP:ZCL_TRAVEL_VIRT_CALC'
      virtual TotalPriceUSD : abap.dec(15,2)
}
```

`ZCL_TRAVEL_VIRT_CALC` implements `IF_SADL_EXIT_CALC_ELEMENT_READ`.

Virtual elements are read-only and cannot be filtered/sorted by the
consumer (they're computed after the SQL result). Use them for view-time
enrichment that can't be expressed in CDS.

---

## 6. Parameters

```abap
define view entity I_TravelByStatus
  with parameters
    p_status : /dmo/overall_status
  as select from ztravel
{
  key travel_uuid as TravelUUID,
      overall_status as OverallStatus
}
where overall_status = $parameters.p_status;
```

Callers must pass parameters: `SELECT FROM i_travelbystatus( p_status = 'O' )`.
Useful in analytical and reuse views, less common in transactional BO views.

---

## 7. Joins and unions

```abap
define view entity I_TravelWithAgency
  as select from ztravel as t
    left outer to one join I_Agency as a
      on t.agency_id = a.AgencyID
{
  key t.travel_uuid as TravelUUID,
      t.agency_id   as AgencyID,
      a.Name        as AgencyName
}
```

```abap
define view entity I_AllTravels
  as select from ztravel_archive
{
  key travel_uuid as TravelUUID,
      'ARCHIVE' as Source
}
union all
  select from ztravel
{
  key travel_uuid as TravelUUID,
      'LIVE' as Source
};
```

For unions, the projected types and names must match across legs.

---

## 8. Annotations that matter for RAP

A short list — see [cds-annotations.md](cds-annotations.md) for the full
catalog.

| Annotation                                         | Effect on RAP                                              |
|----------------------------------------------------|------------------------------------------------------------|
| `@AccessControl.authorizationCheck: #CHECK`        | Enforces DCL access control on reads.                      |
| `@AbapCatalog.viewEnhancementCategory: [#…]`       | Declares which `extend view` shapes are allowed.            |
| `@Metadata.allowExtensions: true`                  | Allows partner/customer metadata extensions.               |
| `@Semantics.systemDateTime.lastChangedAt`          | Marks the field RAP uses for the total ETag (managed BO).  |
| `@Semantics.systemDateTime.localInstanceLastChangedAt` | Marks the local ETag field — required for `etag master`.|
| `@Semantics.user.lastChangedBy` / `createdBy`      | Audit user fields RAP fills in automatically.              |
| `@Semantics.amount.currencyCode` / `quantity.unitOfMeasure` | Semantic typing for amounts/quantities.            |

---

## 9. Provider contract (where it appears)

The `provider contract` clause appears on **projection views** that surface
a BO to a service. It's **not** on the underlying interface view entity. See
[cds-projection-view.md](cds-projection-view.md).

---

## 10. Anti-patterns

- ❌ Using `define view` for new RAP code — it's the legacy classic view.
  Always use `define view entity`.
- ❌ Crossing BO boundaries with `composition` — compositions belong inside a
  BO tree. Cross-BO references use `association`.
- ❌ Computed fields in handlers when CDS calculated elements can express them.
- ❌ Joining wide reference data into every projection — model it as
  `association` and let the UI navigate.
- ❌ Forgetting `association to parent` on a composition target — the BDEF
  will not compile.

---

## 11. Anchor references

- View entity (DDL):
  https://help.sap.com/docs/abap-cloud/abap-cds-development-user/cds-view-entity
- Compositions and associations:
  https://help.sap.com/docs/abap-cloud/abap-cds-development-user/cds-associations
- View enhancement category:
  https://help.sap.com/docs/abap-cloud/abap-cds-development-user/cds-view-enhancement
- Virtual elements:
  https://help.sap.com/docs/abap-cloud/abap-cds-development-user/virtual-elements

Related skill files: [cds-table-entity.md](cds-table-entity.md),
[cds-projection-view.md](cds-projection-view.md),
[behavior-definition.md](behavior-definition.md),
[cds-annotations.md](cds-annotations.md).
