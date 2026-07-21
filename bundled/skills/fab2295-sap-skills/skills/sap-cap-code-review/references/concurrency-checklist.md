# Concurrency checklist (Critical)

Anchored in capire — Transactions: https://cap.cloud.sap/docs/node.js/cds-tx and https://cap.cloud.sap/docs/guides/databases#optimistic-concurrency

CAP wraps each request in a managed transaction (`cds.tx`). Most concurrency problems in CAP services come from circumventing that envelope, fanning out to parallel branches without their own transactions, or skipping `@cds.on.update` ETag handling on multi-writer entities.

If a finding doesn't match a Rule ID below, do not classify it as Critical/Concurrency.

---

## CONC-001 — Read-then-write without optimistic-concurrency token

**Trigger.** A handler that does a SELECT followed by an UPDATE/DELETE based on the SELECTed value (typical "load, mutate, save"), on an entity that does NOT have a `@cds.on.update` ETag field (e.g. `modifiedAt`, `version`).

Pattern:
```js
const row = await SELECT.one.from(E).where({ ID })
if (row.field === 'X') {
  await UPDATE(E).set({ field: 'Y' }).where({ ID })
}
```

**Reference.** capire — *"Use `@cds.on.update` (e.g. `modifiedAt: Timestamp @cds.on.update: $now`) to enable optimistic concurrency. The runtime adds an ETag check; concurrent writers see a 412 Precondition Failed."*

**Why.** Two requests that hit this code in parallel will both read the same `row`, both pass the predicate, and both write — the second silently overwrites the first ("lost update").

**Suggested fix anchor.** Add an ETag field on the entity (`modifiedAt: Timestamp @cds.on.update: $now;` + `@odata.etag`). The OData PATCH/PUT path then enforces the check; for explicit handler-driven flows, include the ETag in the WHERE.

---

## CONC-002 — Mutating shared state in handlers

**Trigger.** Module-level `let`/`var` mutated inside a `this.before/on/after` handler. Examples: `let counter = 0; ...; this.on('foo', () => counter++)`. Class-level `this.<field>` mutated by a request handler when the class is instantiated once per service.

**Reference.** capire — *"Service handlers run concurrently. Don't share mutable state between requests; use `cds.context` (request-scoped) or the database for state."*

**Why.** Each in-flight request reads/writes the same variable; counters lose updates, caches see stale entries, and subtle bugs surface only under load.

**Suggested fix anchor.** Move counters to the DB; use `cds.context.locale`/`req.context` for request-scoped data; use `cds.tx(req).run(...)` to bind to the request transaction.

---

## CONC-003 — Parallel `Promise.all` writes without per-task transaction

**Trigger.** `await Promise.all(items.map(item => UPDATE/INSERT/DELETE...))` in a handler without an explicit `cds.tx({ ... }).run(...)` wrapping each branch, AND the items contain potentially overlapping primary keys.

**Reference.** capire — *"Each `cds.tx` is its own transaction boundary. `Promise.all` over the same `db` runs branches inside the SAME tx by default; failures in one branch can leave others in an undefined state."*

**Why.** Two effects:
1. If the entity has triggers/cascades, parallel writes inside one tx can deadlock.
2. If error handling is per-branch (catch inside the `.map`), a partial-success state can be committed.

**Suggested fix anchor.** Either run sequentially (`for (const item of items) { await UPDATE(...) }`), or open a fresh tx per branch (`Promise.all(items.map(item => cds.tx({}).run(tx => tx.update(...))))`) — but only if you actually want independent transactions.

---

## CONC-004 — `await` inside `forEach` (silent fire-and-forget)

**Trigger.** `array.forEach(async item => { await ... })` where the surrounding scope expects the work to complete before continuing.

**Reference.** capire — general Node.js best practice; capire's *"Asynchronous handlers"* section warns that handler functions returning a non-awaited promise lose their transaction context.

**Why.** `Array.prototype.forEach` ignores the returned promises — the surrounding code proceeds before the callbacks finish, the request's transaction is committed/rolled back without the writes, and errors disappear.

**Suggested fix anchor.** Use a `for...of` loop with `await`, or `await Promise.all(array.map(async item => ...))` if parallelism is wanted.

---

## CONC-005 — Cross-service call without binding to current tx

**Trigger.** `cds.connect.to('OtherService')` inside a handler, then a `srv.run(...)` or `srv.send(...)` without `tx(req)` or `.tx(req)`.

Pattern:
```js
const other = await cds.connect.to('OtherService')
await other.send('doStuff', payload)   // ← not bound to the caller's tx
```

**Reference.** capire — *"To inherit the current transaction, use `srv.tx(req)` (alias `cds.tx(req).run(srv => ...)`); otherwise the call runs in its own transaction and `req.rollback()` won't roll it back."*

**Why.** If the outer request fails after the cross-service call, the side effects of the inner call are NOT rolled back. You get a half-committed system.

**Suggested fix anchor.** `await srv.tx(req).send('doStuff', payload)` — the inner call now joins the request's transaction.

---

## CONC-006 — Background work scheduled with `setTimeout` / `setImmediate` from a handler

**Trigger.** `setTimeout(...)`, `setImmediate(...)`, `process.nextTick(...)` inside a handler that performs DB writes or service calls.

**Reference.** capire — *"For deferred work, use the persistent task queue (`cds.queued()`/`cds.unqueued()`, since cds@9). Don't fire timers inside a request — the request transaction commits/rolls back independently of the timer's eventual run."*

**Why.** The timer callback runs *after* the request transaction has been committed. The deferred work either fails silently (no transaction context) or commits in an unrelated tx that can't be rolled back if the request fails.

**Suggested fix anchor.** For queues, prefer `await cds.queued(srv).send('doLater', data)`. For older versions, use the outbox: `await cds.outboxed(srv).send('doLater', data)`.

---

## CONC-007 — `db.run(raw SQL)` outside the request's tx

**Trigger.** `cds.db.run(...)` or a stored `db = await cds.connect.to('db')` reused across requests with `db.run(...)` inside a handler, instead of `tx = cds.tx(req); tx.run(...)`.

**Reference.** capire — *"`cds.db` is the long-lived connection. Use `cds.tx(req)` (or `srv.tx(req)`) to attach to the current request transaction; otherwise statements may execute outside the unit of work."*

**Why.** Statements run outside the request's tx. They commit immediately and won't roll back with the request.

**Suggested fix anchor.** Replace `cds.db.run(stmt)` with `await cds.tx(req).run(stmt)` (or simply `await stmt` inside an `srv.on(...)` handler — CAP auto-binds to the request tx for handler-scoped queries).

---

## CONC-008 — Reading `cds.context` from a deferred callback

**Trigger.** `cds.context` accessed inside `setTimeout`, `setImmediate`, a `Promise.then(...)` chain detached from `await`, or a top-level callback registered outside the handler scope.

**Reference.** capire — *"`cds.context` is request-local via async-local-storage. It is only valid inside the synchronous chain of the current handler; deferred callbacks see an undefined or stale value."*

**Why.** `cds.context` is bound through Node's AsyncLocalStorage. Once the handler returns, deferred callbacks run in a different async context and either see `undefined` or another request's context — leading to data leaking between users.

**Suggested fix anchor.** Capture the values you need (`const tenant = cds.context.tenant`) BEFORE leaving the handler scope, and pass them as arguments to the deferred callback.

---

## CONC-009 — Long-running handler holding a transaction

**Trigger.** A handler that does external HTTP calls, file I/O, or `cds.connect.to('remote')` calls *between* DB writes inside the same tx, with no `srv.tx(req)` segregation.

**Reference.** capire — *"Don't keep DB transactions open across slow I/O. The DB lock surface grows with handler duration; concurrent writers queue or deadlock."*

**Why.** The DB transaction stays open while the handler waits on HTTP. Other requests block on the same rows.

**Suggested fix anchor.** Split into "short DB tx → external call → short DB tx" with explicit `cds.tx({}).run(...)` for each segment, or move the slow work to the task queue.

---

## What this section is NOT

- It does not check actual deadlocks against a real DB. It flags patterns that are known to deadlock under capire's transaction model.
- It does not analyze SAP HANA-specific isolation levels. If the project uses non-default isolation, that is out of scope.
- It does not check business-process race conditions (e.g. "two users approving the same record"). Those need domain context the skill doesn't have.
