# Learn — RAP concepts

This file is a **concept primer** for the ABAP RESTful Application
Programming Model (RAP). Every section links to the artifact-specific
reference where the concept is implemented.

> **Anchored to**: https://help.sap.com/docs/abap-cloud/abap-rap/abap-rap.html

---

## 1. What RAP is

RAP is the strategic programming model for building cloud-ready,
OData-based, Fiori-enabled business applications on the ABAP platform.

A working **Business Object (BO)** in RAP gives you, for free:

- A persisted, transactional, multi-user domain entity.
- A generated OData V4 (or V2 / REST / SQL) service.
- Optimistic concurrency control (ETag).
- Drafts — server-persisted unsaved edits, resumable across sessions.
- Field-level mandatory / read-only / suppress control.
- Standard CRUD plus typed actions and functions.
- Server-side validations and determinations at well-defined lifecycle
  points.
- Side effects for the Fiori UI to refresh the right fields after a change.
- Authorization checks tied to PFCG / IAM business catalogs.
- A no-code Fiori Elements preview launched from the service binding.

The developer writes **CDS views + a behavior definition** (declarative),
plus, when the model can't express it declaratively, an **ABAP behavior
pool** with handler methods (procedural).

---

## 2. Business Object structure

A BO is:

- **One root entity** — a CDS `define root view entity`.
- Zero or more **child entities** reached by **composition** from the root.

Compositions form a tree. Everything in the tree is locked, drafted, and
saved together as one transactional unit. Cross-tree references between
different BOs use **association**, not composition.

```
Travel  (root)
  └── Booking            (composition child of Travel)
        └── BookingSupplement   (composition child of Booking)

Travel ──association──▶ Agency    (separate BO)
Travel ──association──▶ Customer  (separate BO)
```

Implemented in: [cds-view-entity.md](cds-view-entity.md).

---

## 3. Implementation types

| Type           | Persistence owner | Locking owner | When                                                |
|----------------|-------------------|---------------|-----------------------------------------------------|
| **Managed**    | RAP runtime       | RAP           | Greenfield BOs on RAP-controlled tables. **Default.** |
| **Unmanaged**  | Application code  | Application   | Wrap a legacy persistence (BAPI, classic update, RFC, external system). |
| **Projection** | Inherited from base | Inherited   | Behavior on a projection view of an existing BO.    |

A common practical variant is **managed with additional save** — managed
mode plus a saver class hooking `save_modified` for domain events, audit
rows, outbox writes, without taking over the actual write.

Implemented in: [behavior-definition.md](behavior-definition.md),
[behavior-implementation.md](behavior-implementation.md).

---

## 4. Lifecycle concepts

### 4.1 Draft

A per-user, server-persisted snapshot of an unsaved edit. Drafts let users
pause, log out, return, and resume; let server-side validations and
determinations run on un-activated data; recover from accidental tab close.

Draft actions: `Edit`, `Resume`, `Activate`, `Discard`, `Prepare` (the
managed action that re-runs determinations/validations on draft data
without activating).

Implemented in: [behavior-definition.md §9](behavior-definition.md#9-draft-block).

### 4.2 ETag (optimistic concurrency)

A hash of "what version of this row the client last saw". The client sends
it on the next change; if the row has moved on server-side, RAP returns
HTTP 412 Precondition Failed.

The BDEF declares the ETag field — typically `LocalLastChangedAt` (set by
RAP on every modify) — and aggregates up the composition tree via
`total etag <field>`.

Implemented in: [behavior-definition.md §1.2](behavior-definition.md#12-header-clauses).

### 4.3 Determinations

Server-side computations triggered at a defined lifecycle point:

- `on modify` — fires when watched fields/operations are modified.
- `on save` — fires once just before save.

Used for: default values on create, status transitions, derived fields,
propagation across the composition.

Implemented in: [behavior-definition.md §6](behavior-definition.md#6-determinations),
[behavior-implementation.md §3](behavior-implementation.md#3-determination-handler).

### 4.4 Validations

Server-side checks that can mark an instance invalid and emit a UI message:

- `on save` — runs once before save (most common).
- `on modify` — runs immediately on each modify of the watched fields.

Implemented in: [behavior-definition.md §5](behavior-definition.md#5-validations),
[behavior-implementation.md §4](behavior-implementation.md#4-validation-handler).

### 4.5 Side effects

A UI hint: "if the user changed field X, refresh field Y / entity Z / the
whole object". Not a server-side action — just metadata for Fiori
Elements.

Implemented in: [behavior-definition.md §8](behavior-definition.md#8-side-effects).

### 4.6 Actions and functions

| Kind                | What it does                                                     |
|---------------------|------------------------------------------------------------------|
| **Action**          | Typed, named non-CRUD operation that modifies data.              |
| **Factory action**  | Action that produces a new instance.                             |
| **Static action**   | Action not tied to a specific instance.                          |
| **Function**        | Read-only counterpart to an action.                              |
| **Internal action** | Callable via EML by sibling BOs; not exposed on the service.     |

Implemented in: [behavior-definition.md §7](behavior-definition.md#7-actions-and-functions),
[behavior-implementation.md §5](behavior-implementation.md#5-action-handler).

### 4.7 Numbering

How keys are assigned:

| Strategy             | Who picks the key   | When                            | Typical use                          |
|----------------------|---------------------|---------------------------------|--------------------------------------|
| **Managed early**    | RAP runtime         | Immediately on create           | UUID keys (`sysuuid_x16`).           |
| **Managed late**     | RAP runtime         | At save time                    | Number-range keys (don't burn on drafts). |
| **Unmanaged early**  | Application code    | Immediately on create           | App sets key in modify handler.      |
| **Unmanaged late**   | Application code    | At save time                    | App sets key in saver class.         |

Implemented in: [behavior-definition.md §3](behavior-definition.md#3-field-controls).

### 4.8 Authorization

`@AccessControl.authorizationCheck` on the CDS view declares whether reads
enforce DCL access control. The BDEF marks one BO as **`authorization
master`** for the composition tree; granularity is `( instance )`,
`( global )`, or both. Children inherit the master's decisions.

Implemented in: [behavior-definition.md §1.2](behavior-definition.md#12-header-clauses),
[behavior-implementation.md §7](behavior-implementation.md#7-authorization-handler).

### 4.9 Locking

The root is the **lock master** for its composition tree. Lock granularity
is `total` (one lock covers the whole tree) or per-instance. Cross-BO
locking does not cascade through associations — each BO has its own lock
master.

Implemented in: [behavior-definition.md §1.2](behavior-definition.md#12-header-clauses).

---

## 5. Layered architecture

```
┌──────────────────────────────────────────────┐
│ Service binding   (OData V4 / V2 / REST / SQL)│  → service-binding.md
├──────────────────────────────────────────────┤
│ Service definition  (define service { … })   │  → service-definition.md
├──────────────────────────────────────────────┤
│ Projection layer    (R_… + projection BDEF)  │  → cds-projection-view.md
├──────────────────────────────────────────────┤
│ Business object     (I_… + interface BDEF)   │  → cds-view-entity.md
│                                              │     behavior-definition.md
│                                              │     behavior-implementation.md
├──────────────────────────────────────────────┤
│ Persistence         (DDIC table / table entity) │ → cds-table-entity.md
└──────────────────────────────────────────────┘
```

Each layer is the contract for the layer above. You can refactor storage
without breaking consumers as long as the interface view stays stable; you
can reshape the service without breaking the BO.

---

## 6. RAP vs. older ABAP frameworks

| Concern              | Classic                              | RAP                                  |
|----------------------|--------------------------------------|--------------------------------------|
| Domain model         | DDIC tables + classes                | CDS root + child view entities       |
| Behavior             | Hand-written ABAP + frameworks like BOPF | BDEF + behavior pool             |
| OData exposure       | SEGW (Gateway Service Builder)       | Service definition + binding         |
| UI shape             | Annotations in SEGW / `MPC_EXT`      | `@UI.*` in CDS                       |
| Authorization        | Custom code + auth-checks            | `@AccessControl` + DCL + RAP master  |
| Drafts               | Custom or BOPF draft                 | Built-in (`with draft`)              |
| Locking              | `ENQUEUE_*`                          | Declarative (`lock master`)          |
| Concurrency          | Custom                               | Declarative ETag                     |

RAP is the strategic model on ABAP Cloud and S/4HANA Cloud, public
edition; classic frameworks are not available there.

---

## 7. Where RAP runs

See [release-support.md](release-support.md) for the platform matrix and
the feature availability table.

- SAP BTP, ABAP Environment — full ABAP Cloud, RAP-only.
- S/4HANA Cloud, public edition — RAP for customer/partner code.
- S/4HANA Cloud, private edition — RAP plus wider classic surface.
- On-stack ABAP Platform (S/4HANA on-prem) — RAP alongside classic.

---

## 8. Where to go next

- **You're writing a new BO** → start at [cds-view-entity.md](cds-view-entity.md),
  then [cds-table-entity.md](cds-table-entity.md), then
  [behavior-definition.md](behavior-definition.md).
- **You're extending an SAP BO** → [metadata-extension.md](metadata-extension.md).
- **You're consuming a RAP BO from ABAP** → [eml.md](eml.md).
- **You're shaping the OData service** → [cds-projection-view.md](cds-projection-view.md),
  [service-definition.md](service-definition.md), [service-binding.md](service-binding.md).
- **You're writing handlers** → [behavior-implementation.md](behavior-implementation.md).
- **You're testing** → [testing-rap.md](testing-rap.md).
- **You're adding value helps** → [value-help.md](value-help.md).
- **You're annotating for Fiori** → [cds-annotations.md](cds-annotations.md).
- **You're checking cloud-readiness** → [released-apis.md](released-apis.md).
- **You're wondering if a feature is available on your platform** →
  [release-support.md](release-support.md).
- **You need a term defined** → [glossary.md](glossary.md).

---

## 9. Anchor references

- RAP overview: https://help.sap.com/docs/abap-cloud/abap-rap/abap-rap.html
- Architecture: https://help.sap.com/docs/abap-cloud/abap-rap/architecture
- ABAP Cloud: https://help.sap.com/docs/abap-cloud
