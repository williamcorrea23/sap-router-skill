# Managed vs. unmanaged BO scenarios

RAP gives you three implementation types for a BO:

1. **Managed** — RAP runtime owns persistence, locking, draft.
2. **Unmanaged** — application code owns persistence and most lifecycle.
3. **Projection** — behavior on a projection view; delegates to a base
   BDEF via `use` (not a persistence variant on its own).

Plus the practical hybrid:

4. **Managed with additional save (saver hooks)** — managed mode plus a
   saver class that emits domain events / outbox rows / audit, without
   taking over the write.
5. **Managed with unmanaged save** — managed CRUD + draft, but the actual
   DB write is delegated to application code (legacy persistence under a
   managed UI experience).

This file is a side-by-side comparison and a decision guide.

> **Anchored to**:
> https://help.sap.com/docs/abap-cloud/abap-rap/managed-bo
> https://help.sap.com/docs/abap-cloud/abap-rap/unmanaged-bo

---

## 1. Side-by-side matrix

| Aspect                              | Managed                                  | Unmanaged                                                 |
|-------------------------------------|------------------------------------------|------------------------------------------------------------|
| Persistence owner                   | RAP runtime                              | Application code (saver / modify handlers)                |
| Lock owner                          | RAP runtime                              | Application code (`FOR LOCK` handler) — or "managed with unmanaged save" |
| Draft handling                      | Built-in (`with draft`)                  | Possible but more work; usually skipped or partial         |
| ETag (concurrency)                  | Declarative (`etag master <field>`)      | Must be implemented in the handler / saver                 |
| Numbering                           | Declarative (`field ( numbering : managed )`) | Application sets keys in handler / saver               |
| Authorization                       | Declarative (`authorization master`) + DCL | Same declarations, but enforcement is in handlers          |
| Validations / determinations        | Declarative (BDEF) + handler             | Declarative (BDEF) + handler                              |
| Save sequence                       | `save_modified` (side-effect hook only)  | Full custom: `finalize`, `check_before_save`, `adjust_numbers`, `save` |
| When to use                         | Greenfield BO with RAP-owned table       | Wrap legacy persistence (BAPI, classic update, RFC, external) |
| Boilerplate                         | Minimal                                  | Significantly more                                         |

---

## 2. Managed BO — the default

### 2.1 When to choose managed

- You're building a new BO with a RAP-owned DDIC table or CDS table entity.
- You want drafts, ETag, locking, numbering "for free".
- The persistence is a single backing table the RAP runtime can own.

This is **>90% of new RAP BOs**. Always start managed unless a hard
requirement forces unmanaged.

### 2.2 Managed BDEF

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
{
  create;
  update;
  delete;

  field ( numbering : managed, readonly ) TravelUUID;
  field ( readonly ) LastChangedAt, LocalLastChangedAt;
  field ( mandatory ) AgencyID, CustomerID, BeginDate, EndDate, CurrencyCode;

  validation validateDates on save { field BeginDate, EndDate; create; update; }
  determination calculateTotalPrice on modify { field BookingFee; }
  action ( features : instance ) acceptTravel result [1] $self;

  mapping for ztravel
  {
    TravelUUID         = travel_uuid;
    BeginDate          = begin_date;
    /* ... */
  }
}
```

The behavior pool implements only **business logic** (validations,
determinations, custom actions, feature controls). It does **not** write
to the table.

See [behavior-definition.md](behavior-definition.md) and
[behavior-implementation.md](behavior-implementation.md) for full
examples.

### 2.3 Managed with additional save (saver hooks)

Same BDEF as above, plus a saver class that hooks the save sequence to
emit domain events / outbox rows / audit:

```abap
CLASS lsc_travel DEFINITION
  INHERITING FROM cl_abap_behavior_saver.

  PROTECTED SECTION.
    METHODS save_modified REDEFINITION.
ENDCLASS.

CLASS lsc_travel IMPLEMENTATION.
  METHOD save_modified.
    " RAP has already written ztravel at this point.
    " Emit a domain event for each created Travel.
    LOOP AT create-travel INTO DATA(created).
      INSERT VALUE zoutbox(
        event_uuid  = cl_system_uuid=>create_uuid_x16_static( )
        event_type  = 'TRAVEL_CREATED'
        travel_uuid = created-TravelUUID
        created_at  = cl_abap_context_info=>get_system_date( ) )
        INTO TABLE zoutbox.
    ENDLOOP.
  ENDMETHOD.
ENDCLASS.
```

**Rule**: never write the BO's own table from `save_modified` — RAP did
it. Use the saver for *additional* persistence (outbox, audit, message-bus
posts), never as a replacement.

---

## 3. Unmanaged BO

### 3.1 When to choose unmanaged

- The data lives in a system RAP cannot own (an external API, a legacy
  table guarded by classic update modules, an SAP-delivered BAPI).
- You need full control over the save sequence (e.g. an atomic
  cross-system transaction).
- You're wrapping a classic ABAP API to surface it as a RAP service.

If you're undecided between managed and unmanaged for a greenfield BO,
**choose managed**. Unmanaged costs significantly more handler code.

### 3.2 Unmanaged BDEF

```abap
unmanaged implementation in class zbp_i_travel_um unique;
strict ( 2 );

define behavior for I_Travel alias Travel
lock master
authorization master ( instance )
etag master LastChangedAt
{
  create;
  update;
  delete;

  field ( numbering : unmanaged, readonly ) TravelUUID;
  field ( readonly ) LastChangedAt;

  validation validateDates on save { field BeginDate, EndDate; create; update; }
  action ( features : instance ) acceptTravel result [1] $self;
}
```

Differences from managed:

- No `persistent table` clause — there's no RAP-owned table.
- No `draft table` clause — unmanaged BOs usually skip drafts.
- `numbering : unmanaged` — application sets the key.
- The BDEF still declares validations / determinations / actions; you
  still implement them as handler classes.

### 3.3 Unmanaged handlers

You implement at minimum:

- **Modify handler** (`FOR MODIFY`) — `create`, `update`, `delete`
  operations translated to your custom persistence calls.
- **Read handler** (`FOR READ`) — `READ ENTITIES` translated to your
  custom retrieval.
- **Saver class** (`FOR SAVE`) — the save sequence: `finalize`,
  `check_before_save`, `adjust_numbers`, `save`, `cleanup`.
- **Lock handler** (`FOR LOCK`) — explicit lock acquisition.

```abap
CLASS lhc_travel DEFINITION
  INHERITING FROM cl_abap_behavior_handler.

  PRIVATE SECTION.

    METHODS create_travel FOR MODIFY
      IMPORTING entities FOR CREATE Travel.

    METHODS read_travel FOR READ
      IMPORTING keys FOR READ Travel RESULT result.

    METHODS lock_travel FOR LOCK
      IMPORTING keys FOR LOCK Travel.

ENDCLASS.

CLASS lhc_travel IMPLEMENTATION.

  METHOD create_travel.
    LOOP AT entities INTO DATA(entity).
      CALL FUNCTION 'ZBAPI_TRAVEL_CREATE'
        EXPORTING is_travel = CORRESPONDING #( entity )
        IMPORTING ev_uuid   = DATA(new_uuid)
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
        APPEND VALUE #( %cid = entity-%cid
                         %key = VALUE #( TravelUUID = new_uuid ) )
          TO mapped-travel.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD read_travel.
    LOOP AT keys INTO DATA(k).
      CALL FUNCTION 'ZBAPI_TRAVEL_READ'
        EXPORTING iv_uuid   = k-TravelUUID
        IMPORTING es_travel = DATA(s).
      APPEND CORRESPONDING #( s ) TO result.
    ENDLOOP.
  ENDMETHOD.

  METHOD lock_travel.
    " Custom locking — typically ENQUEUE_… (if available) or a tenant-aware
    " lock against the legacy system.
  ENDMETHOD.

ENDCLASS.
```

### 3.4 Unmanaged saver

```abap
CLASS lsc_travel DEFINITION
  INHERITING FROM cl_abap_behavior_saver.

  PROTECTED SECTION.
    METHODS finalize          REDEFINITION.
    METHODS check_before_save REDEFINITION.
    METHODS save              REDEFINITION.
    METHODS cleanup           REDEFINITION.
    METHODS cleanup_finalize  REDEFINITION.

  PRIVATE SECTION.
    DATA mt_create TYPE STANDARD TABLE OF I_Travel.
    DATA mt_update TYPE STANDARD TABLE OF I_Travel.
    DATA mt_delete TYPE STANDARD TABLE OF I_Travel.
ENDCLASS.

CLASS lsc_travel IMPLEMENTATION.

  METHOD finalize.
    " Capture the transactional buffer for save.
    mt_create = create-travel.
    mt_update = update-travel.
    mt_delete = delete-travel.
  ENDMETHOD.

  METHOD check_before_save.
    " Last-chance cross-row checks before COMMIT.
  ENDMETHOD.

  METHOD save.
    " Persist via the legacy BAPI/RFC. RAP does NOT call COMMIT WORK
    " for unmanaged BOs — you do.
    LOOP AT mt_create INTO DATA(c).
      CALL FUNCTION 'ZBAPI_TRAVEL_PERSIST_CREATE' EXPORTING is_travel = c.
    ENDLOOP.
    " ... update, delete ...
  ENDMETHOD.

  METHOD cleanup.
    CLEAR: mt_create, mt_update, mt_delete.
  ENDMETHOD.

  METHOD cleanup_finalize.
  ENDMETHOD.

ENDCLASS.
```

---

## 4. Managed with unmanaged save (hybrid)

Managed CRUD + draft + RAP-managed UX, but the actual write is delegated
to application code. Useful when:

- You want drafts and ETag for free (managed),
- But the table is owned by a legacy update module you cannot replace.

```abap
managed with unmanaged save implementation in class zbp_i_travel unique;
strict ( 2 );
with draft;

define behavior for I_Travel alias Travel
draft table ztravel_d
lock master total etag LastChangedAt
authorization master ( instance )
etag master LocalLastChangedAt
{ ... }
```

You implement only the saver class's `save`-phase methods; RAP handles
draft, lock, ETag, numbering as usual.

---

## 5. Decision guide

```
Greenfield BO, RAP can own the table?            → MANAGED
Greenfield BO, need outbox / event emission?     → MANAGED + saver hook
Wrap a BAPI / legacy FM?                         → MANAGED WITH UNMANAGED SAVE (if you want drafts)
                                                   or UNMANAGED (if drafts are not required)
Wrap an external system (no ABAP persistence)?   → UNMANAGED
Need full control of COMMIT timing?              → UNMANAGED
Behavior on top of an existing BO?               → PROJECTION (delegating via `use`)
```

When in doubt: **managed**. The exit ramp to unmanaged is well-trodden;
the cost of unmanaged-by-default is wasted handler code.

---

## 6. Common gotchas

- ❌ Choosing unmanaged because "managed feels magic" — managed *is*
  declarative magic, and that's the point. Unmanaged is for legacy
  integration, not architectural preference.
- ❌ Writing to the BO's table from `save_modified` of a managed BO — RAP
  already wrote it; you create a duplicate or conflict.
- ❌ Forgetting `COMMIT WORK` in an unmanaged `save` method — managed BOs
  commit for you; unmanaged ones do not.
- ❌ Mixing unmanaged BOs with `with draft` without doing the full draft
  plumbing — drafts silently break.
- ❌ Calling EML `IN LOCAL MODE` from outside a handler — only valid
  inside handlers.

---

## 7. Anchor references

- Managed BO:
  https://help.sap.com/docs/abap-cloud/abap-rap/managed-bo
- Unmanaged BO:
  https://help.sap.com/docs/abap-cloud/abap-rap/unmanaged-bo
- Managed with unmanaged save:
  https://help.sap.com/docs/abap-cloud/abap-rap/managed-with-unmanaged-save
- Save sequence:
  https://help.sap.com/docs/abap-cloud/abap-rap/save-sequence

Related skill files: [behavior-definition.md](behavior-definition.md),
[behavior-implementation.md](behavior-implementation.md),
[eml.md](eml.md).
