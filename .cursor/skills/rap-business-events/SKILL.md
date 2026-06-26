---
name: rap-business-events
description: >-
  RAP business events — event definitions in BDEF, event consumption via
  Event Mesh, event binding in SAP BTP, raise event from RAP handler, event
  payload structure, CloudEvents format, event choreography vs orchestration,
  RAP event publishing and subscribing. Use when working with RAP business
  event, event mesh, business event, event binding, BDEF event, CloudEvents,
  event choreography, event publishing, or event subscription topics.
---

# RAP Business Events

Event-driven extensions for RAP business objects -- defining, raising, and
consuming business events natively inside the ABAP RESTful Application
Programming model, integrated with SAP Event Mesh on SAP BTP for cross-system
publish/subscribe patterns.

## Purpose

This skill provides authoritative guidance on business events in RAP:

- **Event definitions in BDEF**: declare raised events, event parameters, and
  entity bindings using the `event` syntax in behavior definitions.
- **Event raising in behavior implementations**: raise events from RAP handler
  methods with `RAISE ENTITY EVENT` and proper payload construction.
- **CloudEvents specification**: understand the standard event envelope that
  RAP generates, including `specversion`, `type`, `source`, `subject`,
  `datacontenttype`, and `data` fields.
- **Event Mesh integration**: connect RAP business events to SAP Event Mesh
  (formerly SAP Enterprise Messaging), configure queues, topics, and
  subscriptions on SAP BTP.
- **Event binding configuration**: map BDEF event definitions to SAP Event
  Mesh channels via communication arrangements and event bindings.
- **Event choreography vs orchestration**: choose the right event-driven
  pattern for your use case -- fire-and-forget vs BTP-based orchestration.
- **ZROUTER integration**: use the ZROUTER dispatch engine to consume RAP
  business events from Event Mesh and route them to handler logic.

## Architecture Overview

```
RAP Business Object
  │
  ├── BDEF: event OrderCreated parameter ZDEMO_R_Order;
  │
  ├── Behavior Pool handler
  │     RAISE ENTITY EVENT ZDEMO_R_Order~OrderCreated
  │       FROM VALUE #( ... );
  │
  ├── [Transactional buffer -- event is queued until COMMIT ENTITIES]
  │
  ├── Save sequence
  │     │
  │     └── Event is dispatched AFTER successful database commit
  │           │
  │           ├── Local handler (IN LOCAL MODE, same LUW)
  │           └── Remote consumer (SAP Event Mesh on BTP)
  │                 │
  │                 ├── Event Mesh Queue / Topic
  │                 ├── Webhook subscription (HTTP POST CloudEvents)
  │                 ├── CAP service consumer (cds.emit / on-event)
  │                 ├── S/4HANA Cloud inbound event
  │                 └── ZROUTER dispatch handler
  │
  └── CloudEvents v1.0 envelope wraps the entity payload
```

## Business Event Concepts

### What RAP Business Events Are

RAP business events represent **significant occurrences** in the lifecycle
of a RAP business object. They are:

- **Declared in BDEF** as part of the behavior definition, alongside CRUD
  operations, actions, determinations, and validations.
- **Raised in behavior pool handlers** using `RAISE ENTITY EVENT`.
- **Dispatched after COMMIT ENTITIES** -- the event is not fired during the
  transactional save sequence but only after the database commit succeeds,
  guaranteeing at-least-once delivery semantics for remote consumers.
- **CloudEvents v1.0 compliant** -- every RAP event is automatically wrapped
  in the CloudEvents envelope by the RAP framework.
- **Typed** -- event parameters define the entity or structure payload the
  event carries.

### Event Lifecycle

```
1. EML operation (CREATE / UPDATE / action) modifies buffer
2. Behavior handler calls RAISE ENTITY EVENT (queued in buffer)
3. COMMIT ENTITIES triggers save sequence
4. Database commit succeeds
5. RAP event infrastructure serializes event to CloudEvents
6. Event is published to configured channel (local or Event Mesh)
7. Consumer receives event (HTTP Webhook / AMQP / CAP service)
```

**Critical**: the event does NOT fire if the database commit fails. This
ensures that consumers never receive events for data that was not persisted.
Events are only dispatched for successfully committed changes.

## BDEF Event Definitions

### Event Parameter Type: Entity (most common)

Binds the event payload to a RAP entity, so the event carries the full entity
data structure.

```abap
managed implementation in class zbp_demo_order unique;
strict(2);

define behavior for ZDEMO_R_Order alias Order
persistent table zdemo_order
lock master
authorization master ( instance )
{
  create;
  update;
  delete;

  " Event on entity creation
  event OrderCreated parameter ZDEMO_R_Order;

  " Event on status change
  event OrderApproved parameter ZDEMO_R_Order;

  " Event on cancellation
  event OrderCancelled parameter ZDEMO_R_Order;

  action approve;
  action cancel;
}
```

### Event Parameter Type: Projection View

In a RAP projection layer, events can reference the projected entity.

```abap
projection;
strict(2);

define behavior for C_Order alias OrderProj
{
  use create;
  use update;
  use delete;

  use action approve;
  use action cancel;

  " Re-export the event from the base BO
  use event OrderCreated;
  use event OrderApproved;
  use event OrderCancelled;
}
```

### Event Parameter Type: Custom Structure

When you need a payload that is not an entity (e.g., aggregated data, custom
shape), define the event with a DDIC structure.

```abap
define behavior for ZDEMO_R_Order alias Order
{
  " ... operations ...

  " Event with custom DDIC structure parameter
  event OrderMetricsCalculated parameter ZDEMO_S_OrderMetrics;
}
```

```abap
" DDIC structure definition
@EndUserText.label: 'Order Metrics Event Payload'
define structure ZDEMO_S_OrderMetrics {
  OrderId           : zdemo_order_id;
  TotalAmount       : zdemo_amount;
  ItemCount         : abap.int4;
  AverageItemPrice  : zdemo_amount;
  ProcessingTimeSec : abap.int4;
}
```

## Raising Events from RAP Handlers

### Basic Event Raising

Events are raised using `RAISE ENTITY EVENT` inside behavior pool handler
methods. The event is queued in the transactional buffer and dispatched
after successful commit.

```abap
CLASS lhc_order DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    METHODS approve FOR MODIFY
      IMPORTING keys FOR ACTION Order~approve RESULT result.
ENDCLASS.

CLASS lhc_order IMPLEMENTATION.
  METHOD approve.
    " Read current state from buffer
    READ ENTITIES OF ZDEMO_R_Order IN LOCAL MODE
      ENTITY Order
        ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(lt_orders).

    " Validate and update
    LOOP AT lt_orders INTO DATA(ls_order).
      IF ls_order-Status = 'X'.
        APPEND VALUE #( %tky = ls_order-%tky ) TO failed-order.
        APPEND VALUE #(
          %tky = ls_order-%tky
          %msg = new_message(
            id       = 'ZDEMO_MSG'
            number   = '001'
            severity = if_abap_behv_message=>severity-error )
          %element-Status = if_abap_behv=>mk-on
        ) TO reported-order.
        CONTINUE.
      ENDIF.
    ENDLOOP.

    CHECK failed-order IS INITIAL.

    " Update status
    MODIFY ENTITIES OF ZDEMO_R_Order IN LOCAL MODE
      ENTITY Order
        UPDATE FIELDS ( Status ApprovedAt ApprovedBy )
        WITH VALUE #( FOR order IN lt_orders (
          %tky       = order-%tky
          Status     = 'X'
          ApprovedAt = utclong_current( )
          ApprovedBy = sy-uname ) )
      REPORTED DATA(update_reported).

    reported = CORRESPONDING #( DEEP update_reported ).

    " Raise event -- queued until COMMIT ENTITIES succeeds
    RAISE ENTITY EVENT ZDEMO_R_Order~OrderApproved
      FROM VALUE #( FOR order IN lt_orders (
        %tky   = order-%tky
        %param = order ) ).
  ENDMETHOD.
ENDCLASS.
```

### Raising Events on CREATE

The RAP framework can automatically raise events on entity creation without
explicit handler code, but explicit raising gives more control.

**Option 1: Explicit raising in determination (recommended)**

```abap
" BDEF: determination raiseOrderCreated on modify { create; }

CLASS lhc_order DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    METHODS raiseOrderCreated FOR DETERMINE ON MODIFY
      IMPORTING keys FOR Order~raiseOrderCreated.
ENDCLASS.

CLASS lhc_order IMPLEMENTATION.
  METHOD raiseOrderCreated.
    " Re-read to get full entity state after determinations populated defaults
    READ ENTITIES OF ZDEMO_R_Order IN LOCAL MODE
      ENTITY Order
        ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(lt_orders).

    RAISE ENTITY EVENT ZDEMO_R_Order~OrderCreated
      FROM VALUE #( FOR order IN lt_orders (
        %tky   = order-%tky
        %param = order ) ).
  ENDMETHOD.
ENDCLASS.
```

**Option 2: Raising in saver's finalize step (for post-commit semantics)**

```abap
CLASS lsc_order DEFINITION INHERITING FROM cl_abap_behavior_saver.
  PROTECTED SECTION.
    METHODS finalize REDEFINITION.
ENDCLASS.

CLASS lsc_order IMPLEMENTATION.
  METHOD finalize.
    " finalize runs after the database commit is confirmed
    " Events are collected and dispatched immediately after this method
    " Rarely needed -- prefer determination-based raising in most cases
  ENDMETHOD.
ENDCLASS.
```

### Raising Events from Multiple Sources

A single handler can raise multiple events for different conditions.

```abap
METHOD approve.
  " ... read and validate ...

  " Update status
  MODIFY ENTITIES OF ZDEMO_R_Order IN LOCAL MODE
    ENTITY Order
      UPDATE FIELDS ( Status )
      WITH VALUE #( FOR order IN lt_orders ( %tky = order-%tky Status = 'X' ) )
    REPORTED DATA(update_reported).
  reported = CORRESPONDING #( DEEP update_reported ).

  " Raise standard approval event
  RAISE ENTITY EVENT ZDEMO_R_Order~OrderApproved
    FROM VALUE #( FOR order IN lt_orders (
      %tky   = order-%tky
      %param = order ) ).

  " Conditionally raise high-value event
  LOOP AT lt_orders INTO DATA(ls_order)
      WHERE GrossAmount > 100000.
    APPEND VALUE #(
      %tky   = ls_order-%tky
      %param = ls_order
    ) TO DATA(lt_high_value).
  ENDLOOP.

  IF lt_high_value IS NOT INITIAL.
    RAISE ENTITY EVENT ZDEMO_R_Order~HighValueOrderApproved
      FROM lt_high_value.
  ENDIF.
ENDMETHOD.
```

### Important Rules for Event Raising

- **Events cannot be raised in validations**. Validations are for rejecting
  changes; use determinations or actions for event raising.
- **Events are queued, not sent immediately**. The event is stored in the
  transactional buffer and only dispatched after `COMMIT ENTITIES` succeeds.
- **Events from `IN LOCAL MODE` operations work correctly** -- the event
  payload is resolved from the buffer at dispatch time.
- **Multiple raises of the same event accumulate** -- all instances across
  all raises for the same event type are collected and sent as a batch.
- **No event is raised if the instance is in `failed`**. The event subsystem
  checks the `%failed` indicator before dispatching.

## CloudEvents Format

Every RAP business event is automatically serialized into the
[CloudEvents v1.0](https://cloudevents.io/) envelope by the RAP runtime.

### CloudEvents Envelope Structure

```json
{
  "specversion": "1.0",
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "source": "/sap/opu/odata/sap/ZDEMO_R_ORDER_CDS/Order",
  "type": "sap.s4.beh.zdemororder.v1.ZDEMO_R_Order.OrderCreated.v1",
  "subject": "1000001",
  "time": "2026-06-25T14:30:00Z",
  "datacontenttype": "application/json",
  "data": {
    "DocumentID": "1000001",
    "Description": "Office Supplies",
    "GrossAmount": "1500.00",
    "CurrencyCode": "EUR",
    "Status": "N",
    "CreatedAt": "2026-06-25T14:30:00Z"
  },
  "sap_btp_destination": "S4HANACLOUD_ORDER_SRV",
  "sap_message_processing_log_filter": "ZDEMO_R_Order.OrderCreated"
}
```

### CloudEvents Attributes Generated by RAP

| CloudEvents Field | Source in RAP | Example Value |
|---|---|---|
| `specversion` | Hardcoded by framework | `"1.0"` |
| `id` | Auto-generated UUID | `"a1b2c3d4-e5f6-..."` |
| `source` | OData service path + entity name | `"/sap/opu/odata/sap/ZDEMO_SRV/Order"` |
| `type` | Fully qualified event type | `"sap.s4.beh.demo.v1.ZDEMO_R_Order.OrderCreated.v1"` |
| `subject` | Entity key field value (first key) | `"1000001"` |
| `time` | Timestamp when event was raised | `"2026-06-25T14:30:00Z"` |
| `datacontenttype` | Hardcoded by framework | `"application/json"` |
| `data` | The `%param` structure as JSON | Entity fields as JSON object |
| `dataschema` | (optional) Schema reference if configured | URI to EDMX or JSON Schema |

### Event Type Naming Convention

```
sap.s4.beh.<namespace>.<version>.<entity>.<eventname>.<version>
```

- `sap.s4.beh` -- SAP S/4HANA business event prefix
- `<namespace>` -- derived from the business object's namespace
- `<version>` -- BO version (always `v1` initially)
- `<entity>` -- the CDS entity name (with underscores)
- `<eventname>` -- the event name from BDEF (case-sensitive)
- `<version>` -- event version

### Event Data for Different Parameter Types

**Entity parameter**: The `data` field contains the serialized entity fields
as they exist after the commit (all non-internal/non-suppressed fields).

**Custom structure parameter**: The `data` field contains the structure
fields directly.

**Multi-key entities**: For entities with multiple key fields, `subject`
contains only the first key field value. If you need all keys in the subject,
consider including a semantic key.

## Event Mesh Integration

SAP Event Mesh is the BTP-based message broker that routes RAP business
events to external consumers.

### Architecture

```
S/4HANA Cloud / ABAP Environment (Event Producer)
  │
  ├── RAP BO raises event
  ├── Event is serialized to CloudEvents
  │
  └── Outbound event binding (Communication Arrangement)
        │
        └── SAP Event Mesh (BTP Service)
              │
              ├── Queue (point-to-point, at-least-once delivery)
              │     └── Consumer A (Webhook / AMQP)
              │
              └── Topic (publish-subscribe, fan-out)
                    ├── Consumer B (CAP service)
                    ├── Consumer C (Webhook endpoint)
                    └── Consumer D (ZROUTER dispatch)
```

### Step 1: Create Event Mesh Instance on BTP

```bash
# Using BTP CLI
btp create services/instance \
  --subaccount <subaccount-id> \
  --offering-name enterprise-messaging \
  --plan-name default \
  --name my-event-mesh-instance
```

### Step 2: Configure Event Channel Binding in BDEF

The event binding connects a BDEF event to an Event Mesh channel. This is
configured in the ADT Event Binding editor (or via the `event` annotation
syntax).

```abap
" In the behavior definition -- the @event annotation in CDS
" (This is usually managed via the ADT Event Binding wizard,
"  not hand-coded; shown here for reference)

" The framework generates an outbound event binding that maps:
"   BDEF event ZDEMO_R_Order~OrderCreated
"   to a channel in Event Mesh:
"     namespace: sap/s4/beh
"     topic:     zdemororder/v1/orderevents
```

### Step 3: Create Communication Arrangement

In S/4HANA Cloud or ABAP Environment:

1. App **Communication Arrangements** (F1613 in S/4HANA Cloud)
2. Select scenario **SAP_COM_0092** (Enterprise Event Enablement)
3. Create arrangement with Event Mesh service instance as destination
4. Select the outbound event bindings to activate
5. Events matching the binding are routed to Event Mesh

### Step 4: Subscribe from CAP Service

```javascript
// In CAP (Cloud Application Programming) project
// srv/event-consumer.js
const cds = require('@sap/cds');

module.exports = cds.service.impl(async function () {
  // Subscribe to RAP business event via Event Mesh
  const em = await cds.connect.to('enterprise-messaging');

  em.on('sap/s4/beh/zdemororder/v1/Order/OrderCreated', async (msg) => {
    const { data, subject } = msg;
    console.log(`Order ${subject} created:`, data);

    // React to the event -- create audit log, notify user, etc.
    await INSERT.into('OrderAuditLog').entries({
      OrderID:   subject,
      EventType: 'OrderCreated',
      Timestamp: new Date(),
      Payload:   JSON.stringify(data)
    });
  });

  // Listen for approval events
  em.on('sap/s4/beh/zdemororder/v1/Order/OrderApproved', async (msg) => {
    // Trigger downstream process
    await this.sendNotifyOrderApproved(msg.data.DocumentID);
  });
});
```

### Step 5: Inbound Event Subscription (S/4HANA Cloud)

S/4HANA Cloud can also **consume** events from other systems:

```abap
" In the BDEF of the consuming RAP BO:
" (This is defined using event consumption -- see event binding wizard)

" The inbound event is tied to an action or determination
" via the @event_binding annotation on the consumption model.
" When the event arrives from Event Mesh, the associated
" action/determination is triggered automatically.
```

### Event Mesh Configuration Reference

| Property | Description | Example |
|---|---|---|
| `namespace` | Event namespace in Event Mesh | `sap/s4/beh` |
| `topic` | Topic pattern for fan-out | `zdemororder/v1/orderevents` |
| `queue` | Queue name for point-to-point | `queue-order-events` |
| `subscription` | Subscription binding topic to queue | Maps topic to consumer endpoint |
| `webhook_url` | Target HTTP endpoint | `https://my-app.cfapps.eu10.hana.ondemand.com/events` |
| `authentication` | XSUAA / OAuth2 / Client Cert | OAuth client credentials flow |

## RAP Event Handler Method Types

### 1. FOR RAISE (Explicit Event Raising)

Used when events are raised by an action.

```abap
" BDEF
" event OrderApproved parameter ZDEMO_R_Order;
"
" action approve;

CLASS lhc_order DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    METHODS approve FOR MODIFY
      IMPORTING keys FOR ACTION Order~approve RESULT result.
ENDCLASS.

CLASS lhc_order IMPLEMENTATION.
  METHOD approve.
    " ... update logic ...

    " RAISE ENTITY EVENT always used inside MODIFY handler
    RAISE ENTITY EVENT ZDEMO_R_Order~OrderApproved
      FROM VALUE #( FOR order IN lt_orders (
        %tky   = order-%tky
        %param = order ) ).
  ENDMETHOD.
ENDCLASS.
```

### 2. Automatic Event Raising on CRUD

In recent RAP releases (ABAP Cloud 2308+), events can be auto-raised on
CRUD operations without a handler.

```abap
" BDEF with automatic event on CREATE
define behavior for ZDEMO_R_Order alias Order
{
  create;
  update;
  delete;

  " Auto-raise OrderCreated on every successful create
  event OrderCreated parameter ZDEMO_R_Order for create;

  " Auto-raise OrderChanged on every successful update
  event OrderChanged parameter ZDEMO_R_Order for update;

  " Auto-raise OrderDeleted on every successful delete
  event OrderDeleted parameter ZDEMO_R_Order for delete;
}
```

**Advantages of automatic raising**:
- No handler code required
- Guarantees event is raised for every successful operation
- Consistent behavior regardless of how the create/update was triggered
  (EML, OData, or internal)

**Limitations**:
- Cannot conditionally suppress events (e.g., skip event for certain
  field values)
- No custom payload transformation
- For fine-grained control, use explicit `RAISE ENTITY EVENT` in a
  determination or action instead.

### 3. Event in Determination (for computed payloads)

```abap
" BDEF: determination sendOrderEvent on save { create; update; }

CLASS lhc_order DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    METHODS sendOrderEvent FOR DETERMINE ON SAVE
      IMPORTING keys FOR Order~sendOrderEvent.
ENDCLASS.

CLASS lhc_order IMPLEMENTATION.
  METHOD sendOrderEvent.
    " Re-read all fields needed for the event payload
    READ ENTITIES OF ZDEMO_R_Order IN LOCAL MODE
      ENTITY Order
        ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(lt_orders).

    " Separate orders by event type
    DATA(lt_high_value) = VALUE response for event Order~HighValueOrderCreated(
      FOR order IN lt_orders
      WHERE ( GrossAmount > 100000 )
      ( %tky   = order-%tky
        %param = order ) ).

    DATA(lt_normal) = VALUE response for event Order~OrderCreated(
      FOR order IN lt_orders
      WHERE ( GrossAmount <= 100000 )
      ( %tky   = order-%tky
        %param = order ) ).

    IF lt_high_value IS NOT INITIAL.
      RAISE ENTITY EVENT ZDEMO_R_Order~HighValueOrderCreated
        FROM lt_high_value.
    ENDIF.

    IF lt_normal IS NOT INITIAL.
      RAISE ENTITY EVENT ZDEMO_R_Order~OrderCreated
        FROM lt_normal.
    ENDIF.
  ENDMETHOD.
ENDCLASS.
```

## Event Choreography vs Orchestration

### Event Choreography (Decentralized)

Each service reacts to events independently. No central coordinator.

```
Order Service           Inventory Service        Shipping Service
    │                         │                         │
    ├─ OrderCreated ─────────►│                         │
    │                         ├─ StockReserved ────────►│
    │                         │                         ├─ ShipmentCreated
    │◄────────────────────────┼─────────────────────────┤
    │                         │                         │
```

**When to use choreography**:
- Services are independently developed and deployed
- Loose coupling is paramount
- No complex saga/compensation logic needed
- Flow is straightforward and linear

**RAP implementation**:
```abap
" Order service raises event -- downstream services react independently
RAISE ENTITY EVENT ZDEMO_R_Order~OrderCreated
  FROM VALUE #( ( %tky = <key> %param = <order> ) ).

" No orchestrator -- Inventory service subscribes to OrderCreated
" and decides whether to reserve stock. Shipping subscribes to
" StockReserved and triggers shipment. Each is independent.
```

### Event Orchestration (Centralized)

A central orchestrator coordinates the flow. SAP Build Process Automation
or BTP Workflow service for complex multi-step processes.

```
                    Orchestrator
                         │
          ┌──────────────┼──────────────┐
          │              │              │
    Order Service  Inventory Service  Shipping
          │              │              │
          └──────┬───────┴──────┬───────┘
                 │              │
            Event Mesh     Event Mesh
```

**When to use orchestration**:
- Complex decision logic between steps
- Saga patterns requiring compensating transactions on failure
- Human approval steps in the flow
- Need for process visibility and monitoring dashboard
- Compliance requirements for audit trails

**RAP implementation**:
```abap
" Order service raises event -- orchestrator picks it up
RAISE ENTITY EVENT ZDEMO_R_Order~OrderCreated
  FROM VALUE #( ( %tky = <key> %param = <order> ) ).

" The BTP Workflow / SAP Build Process Automation orchestrator:
" 1. Receives OrderCreated event
" 2. Calls ReserveStock (via API or EML)
" 3. On success: triggers shipping
" 4. On failure: triggers compensating action (CancelOrder)
" 5. Each step is tracked with process trace
```

### Decision Matrix

| Criterion | Choreography | Orchestration |
|---|---|---|
| Coupling | Very loose | Tighter (orchestrator knows all steps) |
| Visibility | Hard to trace end-to-end | Full process visibility |
| Failure handling | Each service handles its own | Centralized saga/compensation |
| Complexity ceiling | Low to moderate | High (complex workflows) |
| Operational overhead | Low | Higher (orchestrator HA, monitoring) |
| RAP events used | Yes (primary mechanism) | Yes (trigger for orchestrator) |
| Human steps | Not suited | Supported (BTP Workflow) |

## Event Testing and Troubleshooting

### Local Event Testing (No Event Mesh Required)

Even without Event Mesh configured, RAP events are dispatched locally.

```abap
" Unit test -- events are raised but not sent externally
" if no Event Mesh binding is configured

CLASS ltc_order_events DEFINITION FINAL FOR TESTING
  DURATION SHORT RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    METHODS test_ordercreated_event FOR TESTING.
ENDCLASS.

CLASS ltc_order_events IMPLEMENTATION.
  METHOD test_ordercreated_event.
    " Create order via EML
    MODIFY ENTITIES OF ZDEMO_R_Order
      ENTITY Order
        CREATE SET FIELDS WITH VALUE #(
          ( %cid        = 'c1'
            Description = 'Test Order'
            GrossAmount = 2500
            CurrencyCode = 'EUR' ) )
      MAPPED DATA(ls_mapped)
      FAILED DATA(ls_failed)
      REPORTED DATA(ls_reported).

    cl_abap_unit_assert=>assert_initial( ls_failed-order ).

    COMMIT ENTITIES
      RESPONSE OF ZDEMO_R_Order
      FAILED DATA(ls_commit_failed)
      REPORTED DATA(ls_commit_reported).

    cl_abap_unit_assert=>assert_initial( ls_commit_failed-order ).

    " Event OrderCreated should have been raised -- verify via log
    " or by asserting side-effects in subscribing code
  ENDMETHOD.
ENDCLASS.
```

### Event Mesh Monitoring

| Tool | Purpose | Access |
|---|---|---|
| BTP Cockpit -> Event Mesh | Dashboard, queue depth, message rate | BTP subaccount |
| S/4HANA -> `SAP_COM_0092` logs | Outbound event dispatch logs | S/4HANA Fiori |
| Event Mesh REST API | GET /v1/management/queues/stats | OAuth scoped access |
| Application Log (SLG1) | Event publishing errors in ABAP | Object: `EVENT_RAISE` |
| Event Mesh Webhook Tester | Manual event injection for testing | BTP Cockpit |

### Common Event Dispatch Errors

| Error | Cause | Resolution |
|---|---|---|
| Event not dispatched | `COMMIT ENTITIES` failed or was not called | Check `%failed`; ensure proper commit flow |
| Event Mesh destination unreachable | Communication Arrangement not active | Verify destination, check certs |
| Event type not found in Event Mesh | Event binding not published to Event Mesh | Re-publish event binding in ADT |
| `BEHAVIOR_BAD_HANDLER_RESPONSE` | Event raised from validation or FOR DETERMINATION ON SAVE with `%failed` | Only raise events from MODIFY handlers or ensure `%failed` clean |
| Payload too large | Entity has many fields exceeding Event Mesh limit (1 MB default) | Reduce payload fields via projection or use custom structure |
| CloudEvents `subject` null | Entity has no key field or key is not populated at event time | Ensure key is assigned before event raising (early numbering) |

## Best Practices

### 1. Choose the Right Event Granularity

```
TOO FINE (antipattern):        CORRECT:
event OrderLineChanged          event OrderChanged
event OrderHeaderChanged        (one event, consumers filter by fields)
event OrderStatusChanged
event OrderAmountChanged
```

**Guideline**: One event per meaningful business state transition, not per
field change. Consumers can inspect the `data` to react to specific field
changes if needed.

### 2. Define Clear Event Ownership

Every event should have exactly one producer (the BO that owns the state
change) and potentially many consumers.

```
" Order service owns OrderCreated, OrderApproved, OrderCancelled
" Inventory service owns StockReserved, StockDepleted
" Shipping service owns ShipmentCreated, ShipmentDelivered
```

### 3. Include Semantic Keys in Event Payload

If your entity uses a technical UUID as the key, the CloudEvents `subject`
will be a UUID -- not human-readable. Consider including a semantic key
(like order number) in the entity itself for consumer readability.

```abap
define behavior for ZDEMO_R_Order alias Order
persistent table zdemo_order
{
  " DocumentID is the semantic key (external order number)
  " OrderUUID is the technical key
  field ( readonly ) DocumentID;

  event OrderCreated parameter ZDEMO_R_Order;
}
```

### 4. Use Published Events for Cross-System Integration

Events are the **recommended pattern** for cross-system integration on
SAP BTP. Prefer events over direct API calls when:

- The producing system should not be coupled to consumer availability
  (fire-and-forget)
- Multiple consumers need the same data (fan-out)
- The consumer only needs to react, not to query historical data
- The integration flow is asynchronous by nature

Use direct APIs (OData, RFC) when:
- The consumer needs synchronous responses
- The data must be confirmed as processed immediately
- The consumer needs to query arbitrary data (not just event-driven)

### 5. Idempotent Event Handling

Event Mesh guarantees **at-least-once** delivery. Consumers MUST implement
idempotency.

```javascript
// CAP consumer -- idempotent event handling
module.exports = cds.service.impl(async function () {
  const em = await cds.connect.to('enterprise-messaging');

  em.on('sap/s4/beh/zdemororder/v1/Order/OrderApproved', async (msg) => {
    const tx = cds.transaction(msg);

    // Check if already processed using the event ID (unique per event)
    const existing = await tx.run(
      SELECT.one.from('ProcessedEvents').where({ EventID: msg.id })
    );

    if (existing) {
      console.log(`Event ${msg.id} already processed -- skipping`);
      return; // Idempotent: skip duplicate delivery
    }

    // Process the event
    await tx.run(
      INSERT.into('ProcessedEvents').entries({ EventID: msg.id })
    );
    // ... business logic ...
  });
});
```

### 6. Event Versioning

Plan for event evolution. When changing an event parameter structure,
publish a new version rather than breaking existing consumers.

```abap
" BDEF -- v1 of the event
event OrderCreated parameter ZDEMO_R_Order;

" BDEF -- v2 (extended with more data)
event OrderCreatedV2 parameter ZDEMO_R_Order_extended;
```

**Versioning guidelines**:
- Additive changes (new fields) -- safe, no new event needed
- Field type changes -- new event version
- Field removal -- new event version, deprecate old
- Semantic change (e.g., Amount now inclusive of tax) -- new event version

### 7. Security and Authorization

Events bypass standard RAP authorization because they are dispatched by the
framework after commit. Ensure:

- Event payload data does NOT include sensitive fields. Use `field (
  suppress )` in the entity or use a custom DDIC structure that excludes
  sensitive fields.
- Event Mesh destinations use X.509 or OAuth2 client credentials, never
  basic authentication over the public internet.
- Queue access is scoped to specific consumers via Event Mesh access policies.

### 8. Event Payload Size Management

Event Mesh has a default 1 MB message size limit. For large entities:

```abap
" Option A: Create a slim projection for the event
define view entity ZDEMO_R_OrderEvent
  as projection on ZDEMO_R_Order
{
  key DocumentID,
      Description,
      GrossAmount,
      CurrencyCode,
      Status,
      CreatedAt
}
" -- only essential fields, not full order detail

" Option B: Use a custom DDIC structure with only needed fields
" Option C: Include only a reference key in the event and let
"           consumers call back via OData to get full details
```

## Common Gotchas

| Gotcha | Explanation | Fix |
|---|---|---|
| Event not received by consumer | Event binding not published to Event Mesh | Run the ADT "Publish Events" wizard; verify Communication Arrangement |
| Event raised but payload is empty | Entity fields are `field ( suppress )` or internal | Check `%control` in the event's `%param`; only non-suppressed fields are serialized |
| `RAISE ENTITY EVENT` in validation handler | Validations run during save and cannot raise events | Move event raising to determination ON SAVE or to the MODIFY handler |
| Event fires for both draft and active versions | Draft save also triggers events (if draft table persists) | Check draft status flag; conditional event raising based on `%is_draft` |
| `COMMIT ENTITIES` called but event not sent | Commit failed silently (`%failed` populated) | Always check `%failed` after COMMIT ENTITIES |
| Event Mesh queue accumulating messages | Consumer not active or processing too slowly | Monitor via BTP Cockpit; implement dead-letter queue strategy |
| Events delivered out of order | Event Mesh processes messages asynchronously | Do NOT rely on strict ordering; use event time for ordering at consumer |
| Double events for same entity | Multiple handlers raise the same event for the same instance | Centralize event raising in a single determination or action |
| Event type mismatch in Event Mesh | Event binding topic does not match consumer subscription topic | Verify topic patterns in both producer binding and consumer subscription |
| Large binary data in event payload | Event Mesh 1 MB limit; binary data inflates rapidly | Asynchronous upload; include URL, not binary data |
| Missing `sap_message_processing_log_filter` | Event not appearing in message processing log | Verify `SAP_COM_0092` is correctly configured as communication scenario |

## ZROUTER Integration

RAP business events can be integrated with the ZROUTER dispatch engine in
two modes.

### Mode 1: ZROUTER as Event Mesh Consumer (Recommended)

The ZROUTER Python routing engine registers as a webhook consumer of Event
Mesh. When a RAP business event is published, ZROUTER receives it and
dispatches to the appropriate ABAP handler.

```
RAP BO on S/4HANA          Event Mesh on BTP           ZROUTER Engine
     │                           │                         │
     ├── OrderCreated event ────►│                         │
     │                           ├── Webhook POST ────────►│
     │                           │                         ├── route to handler
     │                           │                         │   zcl_zt_evt_order
     │                           │                         │   ->on_order_created()
     │                           │                         │
     │                           │◄── HTTP 200 ACK ────────┤
```

**ZROUTER dispatch configuration**:

```python
# sap_router.py event routing configuration
EVENT_ROUTES = {
    "sap.s4.beh.zdemororder.v1.ZDEMO_R_Order.OrderCreated.v1": {
        "handler": "ZCL_ZT_EVT_ORDER",
        "method": "on_order_created",
        "mode": "async",          # fire-and-forget
        "retry": {
            "max_attempts": 3,
            "backoff": "exponential",
            "dead_letter": "ZDEAD_LETTER"
        }
    },
    "sap.s4.beh.zdemororder.v1.ZDEMO_R_Order.OrderApproved.v1": {
        "handler": "ZCL_ZT_EVT_ORDER",
        "method": "on_order_approved",
        "mode": "async"
    }
}
```

**ZROUTER handler ABAP class**:

```abap
CLASS zcl_zt_evt_order DEFINITION
  PUBLIC FINAL CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES zif_zrouter_handler.

    METHODS on_order_created
      IMPORTING iv_payload TYPE string
      RETURNING VALUE(rv_result) TYPE string
      RAISING cx_zrouter.

    METHODS on_order_approved
      IMPORTING iv_payload TYPE string
      RETURNING VALUE(rv_result) TYPE string
      RAISING cx_zrouter.

ENDCLASS.

CLASS zcl_zt_evt_order IMPLEMENTATION.
  METHOD zif_zrouter_handler~handle_action.
    " Dispatch by CloudEvents type field
    DATA(lo_event) = /ui2/cl_json=>generate(
      json = iv_payload ).
    ASSIGN lo_event->* TO FIELD-SYMBOL(<event>).

    ASSIGN COMPONENT 'type' OF STRUCTURE <event>
      TO FIELD-SYMBOL(<type>).
    IF sy-subrc <> 0.
      RAISE EXCEPTION TYPE cx_zrouter
        EXPORTING mv_text = 'Missing CloudEvents type field'.
    ENDIF.

    CASE <type>.
      WHEN 'sap.s4.beh.zdemororder.v1.ZDEMO_R_Order.OrderCreated.v1'.
        rv_result = on_order_created( iv_payload ).
      WHEN 'sap.s4.beh.zdemororder.v1.ZDEMO_R_Order.OrderApproved.v1'.
        rv_result = on_order_approved( iv_payload ).
      WHEN OTHERS.
        RAISE EXCEPTION TYPE cx_zrouter
          EXPORTING mv_text = |Unknown event type: { <type> }|.
    ENDCASE.
  ENDMETHOD.

  METHOD on_order_created.
    " Extract data from CloudEvents payload
    DATA: BEGIN OF ls_cloud_event,
            id              TYPE string,
            source          TYPE string,
            type            TYPE string,
            subject         TYPE string,
            datacontenttype TYPE string,
            data            TYPE string,
          END OF ls_cloud_event.

    /ui2/cl_json=>deserialize(
      EXPORTING json = iv_payload
      CHANGING  data = ls_cloud_event ).

    " Deserialize event data to entity structure
    DATA lt_order TYPE STANDARD TABLE OF zdemo_order.
    /ui2/cl_json=>deserialize(
      EXPORTING json = ls_cloud_event-data
      CHANGING  data = lt_order ).

    " Process the order creation event
    LOOP AT lt_order INTO DATA(ls_order).
      " Business logic: create audit log, trigger notifications, etc.
      INSERT zdemo_audit_log FROM TABLE @( VALUE #(
        ( event_type  = 'OrderCreated'
          event_id    = ls_cloud_event-id
          document_id = ls_order-document_id
          timestamp   = utclong_current( ) ) ) ).
    ENDLOOP.

    rv_result = '{"status":"OK","processed":' &&
                |{ lines( lt_order ) }}|.
  ENDMETHOD.

  METHOD on_order_approved.
    " ... similar pattern for approval processing ...
    rv_result = '{"status":"OK"}'.
  ENDMETHOD.
ENDCLASS.
```

### Mode 2: ZROUTER Webhook Endpoint Receiving CloudEvents

The ZROUTER engine can also expose a raw HTTP webhook endpoint that receives
CloudEvents directly from Event Mesh. This is useful when the ABAP handler
should not be called synchronously during event delivery.

```python
# scripts/sap_router.py -- webhook endpoint
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook/events', methods=['POST'])
def receive_cloud_event():
    """
    Receives CloudEvents from SAP Event Mesh webhook subscription.
    Dispatches to the appropriate ZROUTER handler.
    """
    cloud_event = request.get_json()

    # Validate CloudEvents spec version
    if cloud_event.get('specversion') != '1.0':
        return jsonify({'error': 'Unsupported specversion'}), 400

    event_type = cloud_event.get('type', '')
    event_id   = cloud_event.get('id', '')
    event_data = cloud_event.get('data', {})

    # Route to handler based on event type
    route = EVENT_ROUTES.get(event_type)
    if not route:
        return jsonify({'error': f'No route for {event_type}'}), 404

    # Dispatch to ABAP handler via ZROUTER
    result = dispatch_to_handler(
        handler_class=route['handler'],
        method=route['method'],
        payload=event_data,
        event_id=event_id,
        event_type=event_type
    )

    # Return 200 ACK so Event Mesh removes message from queue
    # Non-200 response causes retry per queue policy
    if result.get('status') == 'ERROR' and route['mode'] == 'sync':
        return jsonify(result), 500

    return jsonify({'status': 'ACK', 'event_id': event_id}), 200
```

### Mode 3: ZROUTER as Event Producer (Sending Back to SAP)

ZROUTER can also publish CloudEvents-compliant messages back to Event Mesh,
which can be consumed by RAP inbound event handlers.

```python
# Publish event from ZROUTER to Event Mesh
# This event can trigger an inbound RAP event handler in S/4HANA

from sap_event_mesh_client import EventMeshClient

client = EventMeshClient(
    url=EVENT_MESH_URL,
    client_id=OAUTH_CLIENT_ID,
    client_secret=OAUTH_CLIENT_SECRET
)

client.publish(
    topic="sap/s4/beh/zdemororder/v1/orderevents",
    cloud_event={
        "specversion": "1.0",
        "type": "sap.s4.beh.zdemororder.v1.ZDEMO_R_Order.OrderCreated.v1",
        "source": "/zrouter/dispatch",
        "id": generate_uuid(),
        "data": {
            "DocumentID": "1000001",
            "Description": "Order created via ZROUTER",
            "GrossAmount": "1500.00",
            "CurrencyCode": "EUR"
        }
    }
)
```

## SAP Documentation References

| Topic | Reference |
|---|---|
| RAP Business Events Overview | [SAP Help: Business Events in RAP](https://help.sap.com/docs/abap-cloud/abap-rap/business-events) |
| BDEF Event Syntax | [SAP ABAP Docu: event in BDEF](https://help.sap.com/doc/abapdocu_cp_index_htm/CLOUD/en-US/ABENBDL_EVENT.html) |
| RAISE ENTITY EVENT | [SAP ABAP Docu: RAISE ENTITY EVENT](https://help.sap.com/doc/abapdocu_cp_index_htm/CLOUD/en-US/ABAPRAISE_ENTITY_EVENT.html) |
| CloudEvents v1.0 Specification | [CloudEvents Spec](https://github.com/cloudevents/spec/blob/v1.0/spec.md) |
| SAP Event Mesh Documentation | [SAP Help: Event Mesh](https://help.sap.com/docs/SAP_EM) |
| Event Mesh REST API | [SAP API Business Hub: Event Mesh](https://api.sap.com/package/SAPEventMesh/rest) |
| Enterprise Event Enablement | [SAP Help: SAP_COM_0092](https://help.sap.com/docs/SAP_S4HANA_CLOUD/0f69f8fb28ac4bf48d2b57b9637e81fa/2e9196295c0133b0e10000000a4450e5.html) |
| CAP Event Mesh Integration | [CAP Cookbook: Messaging](https://cap.cloud.sap/docs/guides/messaging/) |
| RAP Business Events openSAP | [openSAP: Building with RAP](https://open.sap.com/courses/cp13) |
| ABAP Environment Event Enablement | [SAP Help: Event Enablement Setup](https://help.sap.com/docs/abap-cloud/abap-development-tools-user-guide/configuring-business-events) |
| Event Binding Best Practices | [SAP Community: Event-Driven Architecture on BTP](https://community.sap.com/topics/event-driven-architecture) |

## Related Skills

| Skill | Relationship |
|---|---|
| `rap` | Core RAP framework -- BDEF, EML, determinations, validations, actions |
| `btp-abap-environment` | ABAP Cloud / Steampunk environment where RAP events are developed |
| `cds-view-entities` | CDS data models consumed by RAP BDEFs (entity parameter types for events) |
| `abap-unit-testing` | ABAP Unit for testing RAP event raising and behavior implementations |
| `clean-abap` | Clean ABAP coding standards applied to RAP event handler code |
| `authorization-iam` | Authorization considerations for event payload data |
| `sap-transport-management` | Transport lifecycle for RAP artifacts including event bindings |
| `abap-code-review` | Pre-release quality reviews including event-related code |
| `sap-integration-wiki` | Cross-system integration patterns including Event Mesh |
