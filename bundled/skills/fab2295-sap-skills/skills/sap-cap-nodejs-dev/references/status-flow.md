# Status Flows (Status-Transition Modeling)

> Source: https://cap.cloud.sap/docs/guides/services/status-flows
> Related: [domain-first.md](domain-first.md), [annotations-reference.md](annotations-reference.md), [event-handlers-nodejs.md](event-handlers-nodejs.md)

## 1. What it is

Status Flows let the agent **model lifecycle transitions declaratively** instead of writing JS guards in `before(ACTION)` handlers. Capire:

> "Ensure transitions are explicitly modeled, validated, and executed in a controlled and reliable way, thereby eliminating the need for extensive custom coding."

CAP's generic handlers do the work:

- **Entry validation** — the row's current status must match `@from`; on mismatch, CAP returns **409 Conflict**.
- **State transition** — on success, CAP automatically updates the status field to `@to`.

That removes the entire "read current status → check → write new status" handler pattern from user code.

> ⚠ **Gamma (experimental).** Capire flags Status Flows as Gamma. The skill's general public-API rule (no `@experimental` / `@internal`) makes this a **conditional recommendation**: prefer Status Flows when (a) the team has accepted the Gamma stability tier in writing, AND (b) the use case is a true state-machine. For everything else (CRUD with permission gates, simple boolean flips, anything that doesn't model a graph of states), stay on `@requires` / `@restrict` / `@readonly` / `@assert.*`.

## 2. Decision order — where Status Flow fits

This refinement of the [domain-first.md](domain-first.md) decision order applies whenever the use case involves a **lifecycle**: a row that walks through a finite set of named states (Open → Accepted/Rejected, Draft → Submitted → Approved → Paid, etc.).

```
1. Schema             ─ types, associations, aspects from @sap/cds/common
2. Annotations        ─ @mandatory, @assert.*, @readonly, @requires, @restrict, …
3. Views / projections
4. Status Flows       ─ @flow.status + @from + @to    ◀ NEW — use this for state-machine use cases
5. CAP plugins        ─ @cap-js/* (attachments, audit-logging, change-tracking, …)
6. Event handlers     ─ last resort, only when 1–5 cannot express the behavior
```

Rule: **if Status Flow can express the lifecycle, use it.** Only fall through to a handler when the rest of the order has nothing to offer and the behavior is genuinely business logic (external call, multi-row invariant, event emission).

## 3. The three annotations

| Annotation | Where | Purpose |
|---|---|---|
| `@flow.status` | Entity-level | Names the element that holds the lifecycle state and lists the bound actions that drive transitions. |
| `@from: [ #State, … ]` | Action | Allowed entry states. Mismatch ⇒ 409. |
| `@to: #State` or `@to: $flow.previous` | Action | Target state CAP writes after the action runs. `$flow.previous` rolls back to the last state automatically tracked. |

## 4. End-to-end example

### 4.1 The schema (Travels with Open/Accepted/Rejected)

```cds
// db/schema.cds
type TravelStatusCode : String enum {
  Open     = 'O';
  Accepted = 'A';
  Rejected = 'X';
};

entity Travels {
  key ID    : UUID;
  title     : String(111);
  @readonly Status : TravelStatusCode default 'O';
}
```

### 4.2 The service (actions + flow annotations)

```cds
// srv/travel-service.cds
using { Travels } from '../db/schema';

service TravelService {
  entity Travels as projection on Travels actions {
    action acceptTravel();
    action rejectTravel();
    action deductDiscount();
  };
}

annotate TravelService.Travels with @flow.status: Status actions {
  acceptTravel    @from: [ #Open ]  @to: #Accepted;
  rejectTravel    @from: [ #Open ]  @to: #Rejected;
  deductDiscount  @from: [ #Open ];                       // no @to ⇒ status unchanged
}
```

**That is a complete state-machine.** Zero JS. CAP enforces:

- `POST /TravelService/Travels(<id>)/TravelService.acceptTravel` is **allowed only when** `Status == 'O'`; CAP writes `Status = 'A'` automatically.
- `POST /TravelService/Travels(<id>)/TravelService.rejectTravel` likewise; sets `Status = 'X'`.
- Same call against a row already in `Accepted` ⇒ **409 Conflict**, no DB write.

### 4.3 Custom handler ON TOP (rare — only when domain-first is not enough)

If the action needs side effects (send mail, emit event, call remote service), keep the flow declarative and add the **business-logic part** in a handler:

```js
// srv/travel-service.js
module.exports = class TravelService extends cds.ApplicationService {
  init() {
    const { Travels } = this.entities;

    // CAP already validated @from and will set @to AFTER this returns.
    // Use after() so the side effect runs only on the successful transition.
    this.after('acceptTravel', Travels, async (_, req) => {
      await this.emit('TravelAccepted', { travelID: req.params[0].ID });
    });

    return super.init();
  }
}
```

**Do NOT** re-check the status in a `before` handler — CAP already did that. **Do NOT** write the status field in JS — CAP does that.

### 4.4 Returning to the previous state

```cds
annotate TravelService.Travels with @flow.status: Status actions {
  reopen  @from: [ #Accepted, #Rejected ]  @to: $flow.previous;
}
```

`$flow.previous` instructs CAP to set the status back to whatever it was **before** the most recent transition (CAP tracks that automatically).

## 5. Current limitations (capire — verbatim)

- **Draft-enabled entities**: actions are disabled while in draft state; transitions only run on **active** entities.
- **CRUD and DRAFT operations cannot be restricted by status flows** — only **bound actions** are governed by `@flow.status`. To prevent edits while in a given status, keep using `@readonly` / `@restrict` / `@assert.*` alongside the flow.
- **Gamma stability** — see §1 warning.

## 6. Where Status Flow ≠ the right answer

| Scenario | Use this instead |
|---|---|
| "Field can only be edited by admin" | `@restrict: [{ grant: 'WRITE', to: 'admin' }]` |
| "After created, field is read-only" | `@readonly` + `@insertonly` on the right element |
| "Value must be one of a fixed set" | `enum {...}` in CDS (not a flow) |
| "Two entities go together — parent owns child" | Composition |
| "Run side effect when row changes" | `after('UPDATE')` handler — not a flow |
| "Soft-delete: hide rows where deleted=true" | View / projection with `where deleted = false` |

Status Flow is for lifecycles. Don't shoehorn a permission gate or a validation rule into it.

## 7. Anti-patterns the skill rejects

- Writing `before(action)` handlers that re-read the row and check the current status, when `@from` already does that.
- Setting the `Status` field manually inside an action handler, when `@to` already does that.
- Calling Status Flow actions in a loop from JS to "fast-forward" a row through multiple states — model the intermediate transitions if they matter; otherwise add a direct transition.
- Using `$flow.previous` as a generic "undo" for arbitrary state changes — it only undoes the last flow-driven transition.
- Mixing Status Flow with hand-written status fields on the **same** element — pick one mechanism per entity.

## 8. Audit checklist (for `sap-cap-code-review`)

- [ ] Every action that mutates a status field is declared in a `@flow.status` block OR has a documented reason for opting out.
- [ ] No `before` handler re-validates a status that `@from` already guards.
- [ ] No `on`/`after` handler writes the status field that `@to` already updates.
- [ ] If `@odata.draft.enabled` is set on the entity, transitions are only invoked on active rows (capire limitation).
- [ ] The team has signed off on the Gamma stability tier (or the skill should refuse and recommend annotation-based gates instead).
