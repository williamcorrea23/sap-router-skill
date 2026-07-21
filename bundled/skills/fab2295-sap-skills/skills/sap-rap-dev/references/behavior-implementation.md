# Behavior implementation (behavior pool)

The **behavior pool** is the ABAP class that implements a BDEF's
determinations, validations, actions, modify handlers, read handlers, and
feature controls. It's referenced from the BDEF header
(`managed implementation in class <pool> unique;`).

```
BDEF declares     →  determination, validation, action, field-features
Behavior pool     →  ABAP class FOR BEHAVIOR OF <interface_view>
Local handler     →  INHERITING FROM cl_abap_behavior_handler
Saver class       →  INHERITING FROM cl_abap_behavior_saver
```

> **Anchored to**:
> https://help.sap.com/docs/abap-cloud/abap-rap/behavior-implementation
> https://help.sap.com/docs/abap-cloud/abap-rap/eml

---

## 1. The pool class

The behavior pool is an **abstract final** class. RAP discovers handlers by
the `FOR BEHAVIOR OF` annotation; no instance is ever created.

```abap
CLASS zbp_i_travel DEFINITION
  PUBLIC ABSTRACT FINAL
  FOR BEHAVIOR OF I_Travel.
ENDCLASS.

CLASS zbp_i_travel IMPLEMENTATION.
ENDCLASS.
```

Inside the pool's include (the `_CCIMP` "Local Types" section, edited via
ADT's "Local Types" tab), you add **local handler classes**.

---

## 2. Handler class skeleton

```abap
CLASS lhc_travel DEFINITION
  INHERITING FROM cl_abap_behavior_handler.

  PRIVATE SECTION.
    " one METHODS line per BDEF artifact (determination, validation, action, ...)
ENDCLASS.

CLASS lhc_travel IMPLEMENTATION.
  " one METHOD … ENDMETHOD per declaration above
ENDCLASS.
```

Each handler method signature follows a fixed shape per artifact type. The
ADT "Generate Method" quick-fix produces the correct shape automatically.

---

## 3. Determination handler

BDEF:
```abap
determination calculateTotalPrice on modify { field BookingFee; }
```

Handler:
```abap
METHODS calculatetotalprice FOR DETERMINE ON MODIFY
  IMPORTING keys FOR Travel~calculateTotalPrice.

METHOD calculatetotalprice.
  " 1. Read what you need from the BO
  READ ENTITIES OF i_travel IN LOCAL MODE
    ENTITY Travel
      FIELDS ( BookingFee CurrencyCode )
      WITH CORRESPONDING #( keys )
    RESULT DATA(travels).

  READ ENTITIES OF i_travel IN LOCAL MODE
    ENTITY Travel BY \_Booking
      FIELDS ( FlightPrice CurrencyCode )
      WITH CORRESPONDING #( keys )
    RESULT DATA(bookings).

  " 2. Compute
  LOOP AT travels INTO DATA(travel).
    DATA(total) = travel-BookingFee.
    LOOP AT bookings INTO DATA(booking) WHERE TravelUUID = travel-TravelUUID.
      total = total + booking-FlightPrice.
    ENDLOOP.

    " 3. Write back via EML MODIFY
    MODIFY ENTITIES OF i_travel IN LOCAL MODE
      ENTITY Travel
        UPDATE FIELDS ( TotalPrice )
        WITH VALUE #( ( %tky = travel-%tky TotalPrice = total ) )
      REPORTED DATA(update_reported).
  ENDLOOP.
ENDMETHOD.
```

Key points:

- `IN LOCAL MODE` — read/modify against the BO under handling, skipping
  authorization (only legal inside RAP handlers).
- `%tky` — the *transactional key* — primary key fields plus `%is_draft`.
- `READ ENTITIES … BY \_Booking` — navigates the composition.

---

## 4. Validation handler

BDEF:
```abap
validation validateDates on save { field BeginDate, EndDate; create; update; }
```

Handler:
```abap
METHODS validatedates FOR VALIDATE ON SAVE
  IMPORTING keys FOR Travel~validateDates.

METHOD validatedates.
  READ ENTITIES OF i_travel IN LOCAL MODE
    ENTITY Travel
      FIELDS ( TravelID BeginDate EndDate )
      WITH CORRESPONDING #( keys )
    RESULT DATA(travels).

  LOOP AT travels INTO DATA(travel).
    IF travel-BeginDate > travel-EndDate.
      APPEND VALUE #( %tky = travel-%tky ) TO failed-travel.
      APPEND VALUE #(
        %tky               = travel-%tky
        %state_area        = 'VALIDATE_DATES'
        %msg               = NEW /dmo/cm_flight_messages(
                                textid    = /dmo/cm_flight_messages=>begin_date_after_end_date
                                severity  = if_abap_behv_message=>severity-error
                                travel_id = travel-TravelID )
        %element-BeginDate = if_abap_behv=>mk-on
        %element-EndDate   = if_abap_behv=>mk-on
      ) TO reported-travel.
    ENDIF.
  ENDLOOP.
ENDMETHOD.
```

The validation contract:

- `failed-<alias>` — non-empty means this row failed; the save is aborted
  for it.
- `reported-<alias>` — messages emitted; `%state_area` lets RAP clear stale
  messages when the validation re-runs and passes.
- `%element-<field> = if_abap_behv=>mk-on` — flags the responsible fields
  so the UI can highlight them.

---

## 5. Action handler

BDEF:
```abap
action ( features : instance ) acceptTravel result [1] $self;
```

Handler:
```abap
METHODS accepttravel FOR MODIFY
  IMPORTING keys FOR ACTION Travel~acceptTravel RESULT result.

METHOD accepttravel.
  MODIFY ENTITIES OF i_travel IN LOCAL MODE
    ENTITY Travel
      UPDATE FIELDS ( OverallStatus )
      WITH VALUE #( FOR k IN keys ( %tky = k-%tky OverallStatus = 'A' ) )
    FAILED   failed
    REPORTED reported.

  READ ENTITIES OF i_travel IN LOCAL MODE
    ENTITY Travel ALL FIELDS
    WITH CORRESPONDING #( keys )
    RESULT DATA(travels).

  result = VALUE #( FOR travel IN travels ( %tky = travel-%tky %param = travel ) ).
ENDMETHOD.
```

`%param` is how the action result is shaped — for `result [1] $self`, the
whole entity goes there.

### 5.1 Static action

```abap
METHODS archiveolderthan FOR MODIFY
  IMPORTING keys FOR ACTION Travel~archiveOlderThan.
```

Static actions have no instance keys — only the action parameter.

### 5.2 Factory action

```abap
METHODS createwithdraft FOR MODIFY
  IMPORTING keys FOR ACTION Travel~createWithDraft RESULT result.
```

Factory actions return the *new* instance(s) created.

---

## 6. Feature control handler

BDEF:
```abap
action ( features : instance ) acceptTravel result [1] $self;
```

The `features : instance` clause says "ask the handler per-row whether this
action is enabled".

Handler:
```abap
METHODS get_instance_features FOR INSTANCE FEATURES
  IMPORTING keys REQUEST requested_features FOR Travel RESULT result.

METHOD get_instance_features.
  READ ENTITIES OF i_travel IN LOCAL MODE
    ENTITY Travel
      FIELDS ( OverallStatus )
      WITH CORRESPONDING #( keys )
    RESULT DATA(travels).

  result = VALUE #(
    FOR travel IN travels
    ( %tky                = travel-%tky
      %action-acceptTravel = COND #( WHEN travel-OverallStatus = 'O'
                                     THEN if_abap_behv=>fc-o-enabled
                                     ELSE if_abap_behv=>fc-o-disabled )
      %action-rejectTravel = COND #( WHEN travel-OverallStatus = 'O'
                                     THEN if_abap_behv=>fc-o-enabled
                                     ELSE if_abap_behv=>fc-o-disabled )
    ) ).
ENDMETHOD.
```

Constants from `if_abap_behv=>fc-o-*`:

| Value             | Meaning                                  |
|-------------------|------------------------------------------|
| `fc-o-enabled`    | Action / operation is enabled.           |
| `fc-o-disabled`   | Disabled (visible, grayed out).          |
| `fc-o-unauthorized` | Hidden due to authorization.            |

For field-level features the symbol set is `if_abap_behv=>fc-f-*`.

---

## 7. Authorization handler

BDEF:
```abap
authorization master ( instance );
```

Handler:
```abap
METHODS get_instance_authorizations FOR INSTANCE AUTHORIZATION
  IMPORTING keys REQUEST requested_authorizations FOR Travel RESULT result.

METHOD get_instance_authorizations.
  READ ENTITIES OF i_travel IN LOCAL MODE
    ENTITY Travel
      FIELDS ( AgencyID )
      WITH CORRESPONDING #( keys )
    RESULT DATA(travels).

  LOOP AT travels INTO DATA(travel).
    DATA(allowed) = COND abap_bool(
      WHEN abap_authority_check(
             object = 'ZAUTHTRV'
             fields = VALUE #( ( field = 'AGENCY_ID' value = travel-AgencyID )
                               ( field = 'ACTVT'     value = '02' ) ) ) = 0
      THEN abap_true ELSE abap_false ).

    APPEND VALUE #(
      %tky                = travel-%tky
      %update             = COND #( WHEN allowed = abap_true THEN if_abap_behv=>auth-allowed
                                    ELSE if_abap_behv=>auth-unauthorized )
      %delete             = COND #( WHEN allowed = abap_true THEN if_abap_behv=>auth-allowed
                                    ELSE if_abap_behv=>auth-unauthorized )
      %action-acceptTravel = COND #( WHEN allowed = abap_true THEN if_abap_behv=>auth-allowed
                                     ELSE if_abap_behv=>auth-unauthorized )
    ) TO result.
  ENDLOOP.
ENDMETHOD.
```

---

## 8. Saver class (managed-with-side-effects or unmanaged)

```abap
CLASS lsc_travel DEFINITION
  INHERITING FROM cl_abap_behavior_saver.

  PROTECTED SECTION.
    METHODS save_modified    REDEFINITION.
    METHODS cleanup          REDEFINITION.
    METHODS cleanup_finalize REDEFINITION.
ENDCLASS.

CLASS lsc_travel IMPLEMENTATION.

  METHOD save_modified.
    " Emit a domain event for each created Travel — RAP has already
    " written the row at this point; this is the right place to inform
    " other systems (outbox row, message bus, audit log).
    LOOP AT create-travel INTO DATA(created).
      INSERT VALUE zoutbox(
        event_uuid    = cl_system_uuid=>create_uuid_x16_static( )
        event_type    = 'TRAVEL_CREATED'
        travel_uuid   = created-TravelUUID
        created_at    = cl_abap_context_info=>get_system_date( ) )
        INTO TABLE zoutbox.
    ENDLOOP.
  ENDMETHOD.

  METHOD cleanup.            " release transactional resources
  ENDMETHOD.

  METHOD cleanup_finalize.   " release post-commit resources
  ENDMETHOD.

ENDCLASS.
```

Save method ordering:

```
finalize         → last chance to mutate draft → active
check_before_save → late validation, before COMMIT WORK
adjust_numbers   → late numbering (assign keys)
save             → unmanaged save: write to DB yourself
save_modified    → managed save: side effects only — DON'T write the BO's table
cleanup          → release tx resources (rollback path also)
cleanup_finalize → after commit / rollback
```

**Rule**: never write to the BO's own DB table from `save_modified` in a
managed BO — RAP already did it. Use the saver for domain events, outbox
rows, audit, message-bus posts, etc.

---

## 9. Modify handler (unmanaged only)

For `unmanaged` BDEFs, you write `FOR MODIFY` handlers that translate RAP
operations into your custom persistence calls:

```abap
METHODS create_travel FOR MODIFY
  IMPORTING entities FOR CREATE Travel.

METHOD create_travel.
  LOOP AT entities INTO DATA(entity).
    " Call your custom persistence (BAPI, RFC, external API)
    CALL FUNCTION 'ZBAPI_TRAVEL_CREATE'
      EXPORTING
        is_travel = CORRESPONDING #( entity )
      IMPORTING
        ev_uuid   = DATA(new_uuid)
        et_return = DATA(return).

    IF line_exists( return[ type = 'E' ] ).
      APPEND VALUE #( %cid = entity-%cid ) TO failed-travel.
      LOOP AT return INTO DATA(msg) WHERE type = 'E'.
        APPEND VALUE #(
          %cid = entity-%cid
          %msg = new_message( id = msg-id number = msg-number
                              v1 = msg-message_v1 v2 = msg-message_v2
                              severity = if_abap_behv_message=>severity-error )
        ) TO reported-travel.
      ENDLOOP.
    ELSE.
      APPEND VALUE #( %cid = entity-%cid %key = VALUE #( TravelUUID = new_uuid ) )
        TO mapped-travel.
    ENDIF.
  ENDLOOP.
ENDMETHOD.
```

`%cid` (client ID) is how the consumer references the not-yet-persisted
entity in the request. `mapped-travel` tells RAP "this `%cid` is now this
real `%key`".

---

## 10. Working with `%tky`, `%cid`, `%key`

| Symbol     | Definition                                              | When used                              |
|------------|---------------------------------------------------------|----------------------------------------|
| `%key`     | The persistent primary key.                              | Reads, navigations on persisted rows.  |
| `%is_draft`| `'01'` = draft, `'00'` = active.                         | Draft-aware reads/writes.              |
| `%tky`     | `%key` + `%is_draft` — the **transactional key**.        | Default — covers draft + active.       |
| `%cid`     | Client ID, set by consumer for create-then-reference.    | Create requests, referencing new rows. |
| `%pid`     | Local pre-image ID — used in tests.                      | Unit tests with cl_abap_behv_test_environment. |

Use `%tky` everywhere unless you specifically need `%key` (definitely the
active row) or `%cid` (still being created).

---

## 11. The standard tables in every handler

| Table        | Direction | Purpose                                                |
|--------------|-----------|--------------------------------------------------------|
| `keys`       | IN        | Identifies the rows the handler should act on.         |
| `entities`   | IN        | (Create handlers) — the to-be-created data.            |
| `result`     | OUT       | Handler-specific output (action result, features).     |
| `failed`     | OUT       | Rows that the handler rejected.                        |
| `reported`   | OUT       | Messages emitted (errors, warnings, info).             |
| `mapped`     | OUT       | (Create handlers) — `%cid` → `%key` mapping.           |

These are structured per BO (`failed-travel`, `failed-booking`, etc.) so
handlers can affect multiple entities in one call.

---

## 12. Common gotchas

- ❌ Writing to the BO's table in `save_modified` of a managed BO — RAP
  already wrote it; you'll duplicate or conflict.
- ❌ Forgetting `IN LOCAL MODE` on internal reads — triggers authorization
  checks that may block the handler.
- ❌ Returning `%key` from a create handler — should be `mapped-<alias>` with
  `%cid` → `%key`. Returning `%key` directly breaks the consumer round-trip.
- ❌ Skipping `failed-<alias>` when emitting a validation message — RAP
  doesn't know to abort the save for that row.
- ❌ Mutating `keys` — it's an importing parameter, treat as read-only.
- ❌ Naming a handler class without the `lhc_*` / `lsc_*` convention — works,
  but breaks team navigation and code-style tooling.

---

## 13. Anchor references

- Behavior implementation:
  https://help.sap.com/docs/abap-cloud/abap-rap/behavior-implementation
- `cl_abap_behavior_handler`:
  https://help.sap.com/docs/abap-cloud/abap-rap/cl-abap-behavior-handler
- `cl_abap_behavior_saver`:
  https://help.sap.com/docs/abap-cloud/abap-rap/cl-abap-behavior-saver
- EML:
  https://help.sap.com/docs/abap-cloud/abap-rap/eml

Related skill files: [behavior-definition.md](behavior-definition.md),
[eml.md](eml.md), [testing-rap.md](testing-rap.md).
