# Concurrency Control (CAP OOTB)

> Source: https://cap.cloud.sap/docs/guides/services/served-ootb#concurrency-control
> Related: [race-conditions.md](race-conditions.md), [event-handlers-nodejs.md](event-handlers-nodejs.md), [annotations-reference.md](annotations-reference.md)

CAP's generic providers ship concurrency control out of the box. The skill MUST prefer the declarative mechanisms below over hand-rolled "read-then-write" handler logic. Decision order: **ETag-based optimistic** first, **pessimistic** only when the operation must serialize at DB level.

---

## 1. Optimistic locking with ETags

### How CAP wires it

Mark one element with `@odata.etag` (or `@cds.etag`) and CAP:

1. Echoes the element's value in the response `ETag` header.
2. Validates incoming `If-Match` / `If-None-Match` headers on `UPDATE` / `DELETE`.
3. Returns **412 Precondition Failed** when the supplied ETag is stale — without touching the database.

### Recommended pattern

Use the `managed` aspect's `modifiedAt` as the ETag source. It's already auto-updated by CAP on every write, so you get conflict detection for free:

```cds
using { managed } from '@sap/cds/common';

entity Books : managed {
  key ID : UUID;
  title  : String(111);
  stock  : Integer;
}

annotate Books with {
  modifiedAt @odata.etag;
}
```

No JS handler needed. CAP populates `ETag` and validates `If-Match` automatically.

### Header semantics (verbatim from capire)

| Header | Behavior | On mismatch |
|---|---|---|
| `If-Match: <etag>` | Proceed only if current ETag matches | **412 Precondition Failed** |
| `If-None-Match: <etag>` | Read only if changed | **304 Not Modified** |

### Client flow (illustrative)

```
1. POST   /Books        → 201   ETag: "2026-05-13T08:00:00.000Z"
2. PATCH  /Books(<id>)  with If-Match: "2026-05-13T08:00:00.000Z"  → 200, new ETag
3. PATCH  /Books(<id>)  with If-Match: "2026-05-13T08:00:00.000Z"  → 412  (stale)
```

> "If the ETag validation detects a conflict, the request typically needs to be retried by the client." — capire

### When the user has no `managed` aspect

If the entity does not extend `managed`, designate any monotonically updated column as ETag — but the agent is responsible for ensuring it gets updated on every write. Easier path: add `managed` and forget about it.

```cds
entity Inventory {
  key ID    : UUID;
  qty       : Integer;
  version   : Integer default 0;
}

annotate Inventory with {
  version @odata.etag;
}
```

Combine with a `before('UPDATE')` that increments `version`. **Avoid this** if `managed.modifiedAt` is an option — adding `managed` is one line and gives audit fields too.

### What NOT to do

- Don't read the row in a handler, check a value, then write — that's a TOCTOU race. Use `@odata.etag` instead.
- Don't return a freshly-computed ETag from a custom field while writing different fields — the ETag must reflect the actual row state CAP just wrote.
- Don't expose the same entity in two services with **different** ETag elements — clients will get inconsistent precondition failures.

---

## 2. Pessimistic locking (DB-level row lock)

Use only when optimistic isn't enough — typically: same-transaction multi-step updates where stale reads would corrupt invariants (e.g., decrement stock by N, then insert order line that references that exact stock value).

### `SELECT … FOR UPDATE` via CQL

```js
const tx = cds.tx(req);
const book = await tx.run(
  SELECT.one.from(Books)
    .where({ ID: bookId })
    .forUpdate({ wait: 5 })           // exclusive lock, wait up to 5s
);
if (book.stock < quantity) req.reject(409, 'Out of stock');
await tx.run(UPDATE(Books, bookId).set({ stock: book.stock - quantity }));
```

### Shared (read) lock variant

```js
await tx.run(
  SELECT.from(Books).where({ ID: bookId })
    .forShareLock()                   // blocks other writers/exclusive
);
```

### CAP lock options summary

| API | Lock | Blocks |
|---|---|---|
| `.forUpdate()` | exclusive | other readers (DB-dependent), writers, exclusive lockers |
| `.forUpdate({ wait: N })` | exclusive with N-second wait | as above; throws after timeout |
| `.forUpdate({ wait: 0 })` | exclusive, fail fast | as above; throws immediately if locked |
| `.forShareLock()` | shared | exclusive lockers and writers only |

Locks are released when the surrounding `cds.tx(...)` commits or rolls back. Never hold a lock across an `await` that hits an external service.

### Restrictions (capire)

- **SQLite**: pessimistic locking is **not supported**. Plan a different strategy for dev (or use the same `@odata.etag` flow as in prod).
- **H2**: exclusive locks only (no share locks).
- **HANA / Postgres**: full support.
- Locking applies to **domain entities only** — not to projections or views.
  - To lock through a projection, run the `forUpdate` against the **underlying** entity (`cds.db.entities.<Name>`), not the service-level projection.

---

## 3. Drafts (Fiori) and concurrency

`@odata.draft.enabled` already serializes per-draft work on the **active edit session**: CAP issues a lock for the draft owner and rejects concurrent activations from other sessions with 409. The skill should NOT add custom mutexes on top of drafts — CAP owns the lifecycle.

```cds
@odata.draft.enabled
entity Books as projection on db.Books;
```

The draft mechanism gives:

- One active draft per `(entity, key, user)` tuple
- Auto-release on activation or cancel
- Conflict response when a second user tries to edit the same row

If the project mixes draft and non-draft paths to the same table, the agent MUST also wire `@odata.etag` on the table — drafts only protect the draft path.

---

## 4. Combining mechanisms

| Scenario | Recommended |
|---|---|
| Standard CRUD over OData | `@odata.etag` on `modifiedAt` (via `managed`) |
| Fiori with edit drafts | `@odata.draft.enabled` (+ `@odata.etag` if non-draft writes also exist) |
| Multi-row invariant in a transaction (stock, balance, quota) | `cds.tx` + `.forUpdate({ wait: N })` against the **base** entity, then write |
| Cross-service event flow | Idempotency key + `@odata.etag` on the destination row; never rely on event ordering for correctness |
| Long-running batch import | Lock per batch chunk with `.forUpdate({ wait: 0 })` and retry; do NOT lock the whole table |

---

## 5. Anti-patterns the skill rejects

- **Read-modify-write without ETag/lock** — TOCTOU. Always rely on `@odata.etag` or `.forUpdate`.
- **Custom version field maintained by hand** when `managed.modifiedAt` would do.
- **Holding a `.forUpdate` lock across `await cds.connect.to('<remote>').run(...)`** — the remote call can stall the lock for the whole HTTP timeout.
- **Querying CAP entities with raw SQL `SELECT … FOR UPDATE`** — use `.forUpdate()` on the CQL builder so CAP renders the dialect-correct statement (HANA vs. Postgres differ).
- **Pessimistic locking on a view / projection** — capire explicitly restricts that; lock the underlying domain entity.

## 6. Audit checklist (for `sap-cap-code-review`)

A reviewer should flag the following in CAP Node.js code:

- [ ] Every mutable entity exposed in an OData service either uses `managed`+`@odata.etag` or has a documented reason it's read-only.
- [ ] No handler reads a row, checks a field, then writes back without either `If-Match` flow or a `.forUpdate` inside the same `cds.tx`.
- [ ] No `.forUpdate()` is held across calls to a remote service or another DB connection.
- [ ] Drafts (`@odata.draft.enabled`) are not stacked with home-made mutexes.
- [ ] SQLite dev profile does not exercise code paths that rely on pessimistic locking (since SQLite has no support — they would silently behave differently in prod).
