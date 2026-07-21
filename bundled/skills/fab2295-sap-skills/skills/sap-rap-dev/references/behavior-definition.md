# Behavior definition (BDEF)

The **behavior definition** declares what a RAP business object *does*: its
operations, validations, determinations, actions, side effects, draft
handling, locking, ETag, numbering, authorization, and field controls.

It's a DSL — not ABAP — saved alongside the CDS view it's attached to.

> **Anchored to**: https://help.sap.com/docs/abap-cloud/abap-rap/behavior-definition
> and the BDL keyword reference under the same docset.

---

## 1. Header

```abap
managed implementation in class zbp_i_travel unique;
strict ( 2 );
with draft;

define behavior for I_Travel alias Travel
persistent table ztravel
draft table ztravel_d
lock master total etag LastChangedAt
authorization master ( instance )
etag master LocalLastChangedAt
{ ... }
```

### 1.1 Implementation type

| Keyword         | Meaning                                                                |
|-----------------|------------------------------------------------------------------------|
| `managed`       | RAP runtime owns persistence, locking, draft.                          |
| `unmanaged`     | Application code owns persistence and most lifecycle handlers.         |
| `projection`    | Behavior on a projection view; delegates to base BDEF via `use`.       |
| `extension`     | Behavior extension of an SAP-delivered BDEF.                           |
| `interface`     | Abstract behavior interface (composition pattern, advanced).           |

### 1.2 Header clauses

| Clause                              | Effect                                                                  |
|-------------------------------------|-------------------------------------------------------------------------|
| `implementation in class <pool>`    | The ABAP class hosting the behavior pool. Required for managed/unmanaged. |
| `unique`                            | Enforces single-class implementation (no split across classes).         |
| `strict ( N )`                      | Strict checks level (current max 2). See §10.                           |
| `with draft`                        | Enables draft handling. Requires `draft table` and ETag fields.         |
| `use draft` (projection)            | Inherits draft from base BDEF.                                          |
| `persistent table <ddic_table>`     | Active table. Mandatory for managed.                                    |
| `draft table <draft_table>`         | Draft sibling table. Mandatory when `with draft`.                       |
| `lock master total etag <field>`    | This BO owns the lock; computes total ETag from `<field>`.              |
| `lock dependent by _Parent`         | Child BO — locks via the parent.                                        |
| `authorization master ( instance )` | Owns authorization; granularity in parentheses.                         |
| `authorization dependent by _Parent`| Child — inherits authorization decisions from parent.                   |
| `etag master <field>`               | Field used for the instance-level ETag.                                 |
| `etag dependent by _Parent`         | Child — ETag derived from parent.                                       |

---

## 2. Operations

```abap
{
  create;
  update;
  delete;
}
```

| Operation      | Notes                                                                 |
|----------------|-----------------------------------------------------------------------|
| `create`       | Allowed on this entity.                                               |
| `update`       | Modify allowed.                                                       |
| `delete`       | Deletion allowed.                                                     |
| `association <name> { create; … }` | Allowed on the composition child.                  |
| `update precheck` | Enables an early `IS_UPDATE_REQUESTED` style check.                |

Operations can carry annotations:

```abap
create ( features : global );           " feature-controlled (e.g. global toggle)
update;
delete ( authorization : update );      " same authorization profile as update
```

---

## 3. Field controls

```abap
{
  field ( numbering : managed, readonly ) TravelUUID;
  field ( readonly ) LastChangedAt, LocalLastChangedAt, LastChangedBy;
  field ( mandatory ) AgencyID, CustomerID, BeginDate, EndDate, CurrencyCode;
  field ( suppress ) Description;       " not visible in service metadata
  field ( features : instance ) OverallStatus;
}
```

| Field control                              | Meaning                                                  |
|--------------------------------------------|----------------------------------------------------------|
| `numbering : managed`                      | RAP generates the value (UUID or via number range).      |
| `numbering : unmanaged`                    | Application code assigns the value.                      |
| `readonly`                                 | Field cannot be modified by the consumer.                |
| `mandatory`                                | Field is required on create / update.                    |
| `mandatory : create`                       | Required only on create.                                 |
| `suppress`                                 | Hidden from the exposed service.                         |
| `features : instance`                      | Per-row dynamic control via a handler (see [behavior-implementation.md](behavior-implementation.md)). |
| `features : global`                        | Global feature flag via a static handler.                |

---

## 4. Associations and compositions

```abap
{
  association _Booking { create; with draft; }
  association _Agency;
  association _Customer;
}
```

The composition child is reached via its association name from the parent.
`{ create; with draft; }` allows creating child rows under a parent draft.

---

## 5. Validations

```abap
{
  validation validateDates on save
    { field BeginDate, EndDate; create; update; }

  validation validateCustomer on save
    { field CustomerID; create; update; }
}
```

A validation declares **when** it runs:

- `on save` — runs once before save (most common).
- `on modify` — runs immediately on each modify of the watched fields/ops.

And **what triggers** it:

- `field <list>` — re-runs if any listed field is modified.
- `create | update | delete` — re-runs if any listed operation is targeted.

The implementation lives in the behavior pool as a `FOR VALIDATE ON SAVE`
handler — see [behavior-implementation.md](behavior-implementation.md).

---

## 6. Determinations

```abap
{
  determination setStatusToOpen on modify
    { create; }

  determination calculateTotalPrice on modify
    { field BookingFee; }

  determination clearReturnDate on save
    { field BeginDate, EndDate; }
}
```

Like validations: trigger fields/operations + a phase. Determinations
*modify* data (a validation cannot). The implementation is a
`FOR DETERMINE ON {MODIFY|SAVE}` handler.

---

## 7. Actions and functions

```abap
{
  /* instance actions */
  action ( features : instance ) acceptTravel result [1] $self;
  action ( features : instance ) rejectTravel result [1] $self;

  /* parameterized action */
  action ( features : instance ) deductDiscount
    parameter ZD_TravelDiscount  result [1] $self;

  /* factory action (creates a new instance) */
  factory action createWithDraft;

  /* static action (no instance) */
  static action archiveOlderThan parameter ZD_ArchiveCutoff;

  /* function (read-only) */
  function ( features : instance ) calcQuotedFee parameter ZD_QuoteContext result [1] ZD_QuoteResult;

  /* internal — callable via EML only, not exposed on the service */
  internal action recomputeRollup;
}
```

Result kinds:

| Result clause            | Meaning                                                  |
|--------------------------|----------------------------------------------------------|
| `result [1] $self`       | Returns the same entity (one row).                       |
| `result [0..*] $self`    | Returns multiple rows of the same entity.                |
| `result [1] <Entity>`    | Returns rows of a different entity.                      |
| `result [1] <CdsType>`   | Returns a typed structure (custom type).                 |

Parameter kinds: CDS structure types or `abap_short_name` types.

---

## 8. Side effects

```abap
{
  side effects {
    field BeginDate, EndDate affects field TotalPrice;
    field BookingFee         affects field TotalPrice;
    action acceptTravel      affects entity $self;
    action acceptTravel      affects entity _Booking;
  }
}
```

Side effects are **UI hints** — they tell Fiori Elements that after a change
the listed targets should be re-read. They don't change server-side
behavior.

---

## 9. Draft block

```abap
{
  draft action Activate optimized;     " activate the draft (save)
  draft action Discard;                " throw away the draft
  draft action Edit;                   " open active row for editing as draft
  draft action Resume;                 " resume an existing draft
  draft determine action Prepare {     " run determinations + validations on draft
    determination calculateTotalPrice;
    validation    validateDates;
    validation    validateCustomer;
  }
}
```

`optimized` on `Activate` skips the active→draft re-read when only the
draft has changed — a performance optimization.

---

## 10. Mapping

```abap
{
  mapping for ztravel
  {
    TravelUUID            = travel_uuid;
    TravelID              = travel_id;
    AgencyID              = agency_id;
    CustomerID            = customer_id;
    BeginDate             = begin_date;
    EndDate               = end_date;
    BookingFee            = booking_fee;
    TotalPrice            = total_price;
    CurrencyCode          = currency_code;
    OverallStatus         = overall_status;
    Description           = description;
    LastChangedAt         = last_changed_at;
    LocalLastChangedAt    = local_last_changed_at;
    CreatedBy             = created_by;
    CreatedAt             = created_at;
    LastChangedBy         = last_changed_by;
  }
}
```

Without an explicit mapping, RAP requires exact name matches between the
CDS interface view elements and the DB columns. Mapping bridges the
"CamelCase in CDS, snake_case in DB" gap.

---

## 11. Projection BDEF

```abap
projection;
strict ( 2 );
use draft;

define behavior for R_Travel alias Travel
{
  use create;
  use update;
  use delete;

  use association _Booking { create; with draft; }
  use association _Agency;
  use association _Customer;

  use action acceptTravel;
  use action rejectTravel;
  use action Activate;
  use action Discard;
  use action Edit;
  use action Resume;
  use action Prepare;

  use action createWithDraft;

  /* projection-only further restriction */
  field ( read only ) AgencyID;        " UI can't change Agency once chosen
}
```

A projection BDEF can only **restrict** what the interface BDEF defines, never
relax. It picks via `use` the operations/actions/associations to surface, and
optionally re-applies stricter field controls.

---

## 12. Extension BDEF

```abap
extension;
strict ( 2 );

extend behavior for I_SalesOrder
{
  determination computeYY1_DerivedField on modify
    { field YY1_BaseField; }

  validation validateYY1_CustomRule on save
    { field YY1_MyCustomField; create; update; }

  action ( features : instance ) MyCustomAction result [1] $self;
}
```

See [metadata-extension.md](metadata-extension.md) for the full extension
pattern (CDS view extension + metadata extension + behavior extension +
service extension).

---

## 13. Strict modes

| Mode          | Adds checks for…                                                              |
|---------------|-------------------------------------------------------------------------------|
| `strict ( 0 )`| Legacy / minimal — pre-2208 behavior. Avoid for new code.                     |
| `strict ( 1 )`| Mandatory feature controls, mandatory mapping completeness, etc.              |
| `strict ( 2 )`| All level-1 checks plus stricter handler/numbering rules. **Use for new code.**|

Higher strict mode = the compiler catches more potential bugs at activation
time. Always use the highest mode available for the target release.

---

## 14. Common gotchas

- ❌ `with draft` without a `draft table` clause — won't compile.
- ❌ `lock master total etag <field>` referencing a field that isn't typed
  for timestamps — RAP runtime errors at first modify.
- ❌ Missing `mapping for` when CDS / DDIC names diverge — the BO won't be
  able to read or write.
- ❌ `field ( mandatory )` on an audit field like `LastChangedAt` — the user
  cannot provide it, all creates fail.
- ❌ Putting `@UI.*` annotations on the interface view instead of the
  projection — they belong on the projection so different services can have
  different UIs.

---

## 15. Anchor references

- BDEF reference:
  https://help.sap.com/docs/abap-cloud/abap-rap/behavior-definition
- Managed BO:
  https://help.sap.com/docs/abap-cloud/abap-rap/managed-bo
- Unmanaged BO:
  https://help.sap.com/docs/abap-cloud/abap-rap/unmanaged-bo
- Draft handling:
  https://help.sap.com/docs/abap-cloud/abap-rap/draft-handling
- Strict mode:
  https://help.sap.com/docs/abap-cloud/abap-rap/strict-mode

Related skill files: [behavior-implementation.md](behavior-implementation.md),
[cds-view-entity.md](cds-view-entity.md),
[cds-projection-view.md](cds-projection-view.md),
[eml.md](eml.md).
