# EML — Entity Manipulation Language

**EML** is the ABAP DSL for accessing RAP BOs from ABAP code: in behavior
pool handlers, in other BOs, in test code, in custom services. It replaces
direct DB access for RAP-managed data.

> **Anchored to**: https://help.sap.com/docs/abap-cloud/abap-rap/eml

---

## 1. The five statements

| Statement              | Purpose                                                       |
|------------------------|---------------------------------------------------------------|
| `READ ENTITIES`        | Read rows + associated rows.                                  |
| `MODIFY ENTITIES`      | Create, update, delete, execute action.                       |
| `COMMIT ENTITIES`      | Trigger the save sequence (`finalize` → `save_*` → commit).   |
| `ROLLBACK ENTITIES`    | Discard the transactional buffer.                             |
| `GET PERMISSIONS`      | Inspect what the current user is authorized to do.            |

---

## 2. READ ENTITIES

### 2.1 Read by key

```abap
READ ENTITIES OF i_travel
  ENTITY Travel
    ALL FIELDS
    WITH VALUE #( ( TravelUUID = uuid ) )
  RESULT DATA(travels)
  FAILED DATA(failed)
  REPORTED DATA(reported).
```

### 2.2 Read selected fields

```abap
READ ENTITIES OF i_travel
  ENTITY Travel
    FIELDS ( TravelID BeginDate EndDate )
    WITH VALUE #( ( TravelUUID = uuid ) )
  RESULT DATA(travels).
```

### 2.3 Read via composition / association

```abap
READ ENTITIES OF i_travel
  ENTITY Travel BY \_Booking
    ALL FIELDS
    WITH VALUE #( ( TravelUUID = uuid ) )
  RESULT DATA(bookings)
  LINK DATA(link_table).
```

`\_Booking` is the **navigation arrow**: from each Travel row in the input
to all matching Booking rows. `LINK` returns the parent-child key mapping.

### 2.4 IN LOCAL MODE

Inside a behavior pool handler, use `IN LOCAL MODE`:

```abap
READ ENTITIES OF i_travel IN LOCAL MODE
  ENTITY Travel
    FIELDS ( BookingFee )
    WITH CORRESPONDING #( keys )
  RESULT DATA(travels).
```

`IN LOCAL MODE` skips authorization checks and accesses the BO's
transactional buffer directly. It's only valid inside RAP handlers — never
in arbitrary application code.

### 2.5 Draft-aware vs. active-only

```abap
READ ENTITIES OF i_travel
  ENTITY Travel
    ALL FIELDS
    WITH VALUE #( ( %tky = VALUE #( TravelUUID = uuid %is_draft = if_abap_behv=>mk-off ) ) )
  RESULT DATA(active_only).
```

Pass `%tky` (or `%key` + `%is_draft`) to choose draft / active.

---

## 3. MODIFY ENTITIES — CREATE

```abap
MODIFY ENTITIES OF i_travel
  ENTITY Travel
    CREATE FIELDS ( AgencyID CustomerID BeginDate EndDate CurrencyCode )
    WITH VALUE #( ( %cid    = 'TRAVEL_001'
                    AgencyID    = '70010'
                    CustomerID  = '000001'
                    BeginDate   = '20260601'
                    EndDate     = '20260615'
                    CurrencyCode = 'EUR' ) )
  MAPPED   DATA(mapped)
  FAILED   DATA(failed)
  REPORTED DATA(reported).
```

- `%cid` — client ID set by the caller. Required for creates.
- `mapped-travel` — RAP's response: `%cid` ↔ generated `%key` (UUID, key).

### 3.1 Create child via composition

```abap
MODIFY ENTITIES OF i_travel
  ENTITY Travel
    CREATE BY \_Booking FIELDS ( BookingID CustomerID FlightPrice CurrencyCode )
      WITH VALUE #( ( %cid_ref = 'TRAVEL_001'   " parent's %cid
                      %target  = VALUE #(
                        ( %cid       = 'BOOKING_001'
                          BookingID   = '1'
                          CustomerID  = '000001'
                          FlightPrice = '500.00'
                          CurrencyCode = 'EUR' ) ) ) )
  MAPPED   mapped
  FAILED   failed
  REPORTED reported.
```

- `%cid_ref` — references the parent's `%cid` (the parent isn't persisted
  yet; you can't use `%key`).
- `%target` — the child rows under that parent.

---

## 4. MODIFY ENTITIES — UPDATE / DELETE

```abap
MODIFY ENTITIES OF i_travel
  ENTITY Travel
    UPDATE FIELDS ( Description )
    WITH VALUE #( ( %tky = VALUE #( TravelUUID = uuid )
                    Description = 'Updated description' ) )
  FAILED   DATA(failed)
  REPORTED DATA(reported).

MODIFY ENTITIES OF i_travel
  ENTITY Travel
    DELETE FROM VALUE #( ( %tky = VALUE #( TravelUUID = uuid ) ) )
  FAILED   failed
  REPORTED reported.
```

---

## 5. MODIFY ENTITIES — EXECUTE action

```abap
MODIFY ENTITIES OF i_travel
  ENTITY Travel
    EXECUTE acceptTravel
    FROM VALUE #( ( %tky = VALUE #( TravelUUID = uuid ) ) )
  RESULT   DATA(result)
  FAILED   DATA(failed)
  REPORTED DATA(reported).
```

For parameterized actions:

```abap
MODIFY ENTITIES OF i_travel
  ENTITY Travel
    EXECUTE deductDiscount
    FROM VALUE #(
      ( %tky      = VALUE #( TravelUUID = uuid )
        %param    = VALUE #( DiscountPercent = '10' ) ) )
  RESULT   DATA(result)
  FAILED   DATA(failed)
  REPORTED DATA(reported).
```

---

## 6. COMMIT and ROLLBACK ENTITIES

```abap
COMMIT ENTITIES RESPONSE OF i_travel
  FAILED   DATA(commit_failed)
  REPORTED DATA(commit_reported).

IF commit_failed IS NOT INITIAL.
  ROLLBACK ENTITIES.
ENDIF.
```

- `COMMIT ENTITIES` triggers RAP's save sequence: `finalize` →
  `check_before_save` → `adjust_numbers` → `save` / `save_modified` →
  `cleanup_finalize` → `COMMIT WORK`.
- Always check `commit_failed` — `COMMIT ENTITIES` can still fail (late
  numbering errors, save_modified errors, optimistic-concurrency conflicts).
- `ROLLBACK ENTITIES` discards the entire transactional buffer.

---

## 7. GET PERMISSIONS

```abap
GET PERMISSIONS ONLY INSTANCE
  ENTITY i_travel
    UPDATE
    EXECUTE acceptTravel
    REQUEST VALUE #( ( %tky = VALUE #( TravelUUID = uuid ) ) )
  RESULT   DATA(perms)
  FAILED   DATA(failed)
  REPORTED DATA(reported).

IF perms[ 1 ]-%update = if_abap_behv=>auth-allowed.
  " ok to update
ENDIF.
```

Use cases:

- A pre-check before showing UI actions.
- Validating eligibility before posting to a different BO.

---

## 8. Working with the standard response tables

| Table       | Carries                                                          |
|-------------|------------------------------------------------------------------|
| `MAPPED`    | `%cid` ↔ `%key` for creates.                                     |
| `FAILED`    | Rows that failed (per-entity, e.g. `failed-travel`).             |
| `REPORTED`  | Messages (errors, warnings, info, per-entity).                   |
| `RESULT`    | Read result / action result.                                     |
| `LINK`      | Parent-child key mapping in associations.                        |

Pattern in a calling routine:

```abap
DATA: failed   TYPE RESPONSE FOR FAILED   i_travel,
      reported TYPE RESPONSE FOR REPORTED i_travel,
      mapped   TYPE RESPONSE FOR MAPPED   i_travel.

MODIFY ENTITIES OF i_travel
  ENTITY Travel CREATE …
  MAPPED   mapped
  FAILED   failed
  REPORTED reported.

IF failed IS NOT INITIAL OR reported IS NOT INITIAL.
  " handle errors — surface to caller, don't COMMIT.
  RETURN.
ENDIF.

COMMIT ENTITIES …
```

---

## 9. Calling a different BO via EML

EML is BO-scoped — `OF i_travel` reads the Travel BO. To call another BO,
use `OF <other_root_view>`:

```abap
MODIFY ENTITIES OF i_customer
  ENTITY Customer
    UPDATE FIELDS ( Status )
    WITH VALUE #( ( %tky = VALUE #( CustomerID = '000001' )
                    Status = 'ACTIVE' ) )
  REPORTED DATA(reported).

COMMIT ENTITIES RESPONSE OF i_customer
  FAILED DATA(commit_failed).
```

Each BO has its own transactional buffer. If both BOs participate in the
same business transaction, both `COMMIT ENTITIES` must succeed before
either proceeds — RAP doesn't auto-coordinate cross-BO commits.

---

## 10. Common gotchas

- ❌ Forgetting `IN LOCAL MODE` in a handler — your read hits authorization
  and may fail when running internally.
- ❌ Using `%key` to reference a row created in the same request — at that
  point the row has a `%cid`, not yet a `%key`. Use `%cid_ref`.
- ❌ Not checking `failed` / `reported` after `MODIFY ENTITIES` — partial
  failures get silently swallowed.
- ❌ Calling `COMMIT WORK` instead of `COMMIT ENTITIES` — bypasses RAP's
  save sequence, no validations / determinations / save_modified run.
- ❌ Mixing `IN LOCAL MODE` reads / modifies with `GET PERMISSIONS` — local
  mode skips the auth model that `GET PERMISSIONS` introspects; the
  results are inconsistent.

---

## 11. Anchor references

- EML overview:
  https://help.sap.com/docs/abap-cloud/abap-rap/eml
- READ ENTITIES:
  https://help.sap.com/docs/abap-cloud/abap-rap/eml-read-entities
- MODIFY ENTITIES:
  https://help.sap.com/docs/abap-cloud/abap-rap/eml-modify-entities
- COMMIT ENTITIES:
  https://help.sap.com/docs/abap-cloud/abap-rap/eml-commit-entities
- GET PERMISSIONS:
  https://help.sap.com/docs/abap-cloud/abap-rap/eml-get-permissions

Related skill files: [behavior-implementation.md](behavior-implementation.md),
[behavior-definition.md](behavior-definition.md),
[testing-rap.md](testing-rap.md).
