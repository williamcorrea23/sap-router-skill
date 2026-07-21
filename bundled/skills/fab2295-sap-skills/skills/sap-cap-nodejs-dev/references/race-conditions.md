# Race Conditions in CAP Node.js

> Related: [concurrency-control.md](concurrency-control.md), [event-handlers-nodejs.md](event-handlers-nodejs.md), [event-handlers-patterns.md](event-handlers-patterns.md), [cql-patterns.md](cql-patterns.md#transaction-patterns)
> Capire anchors: https://cap.cloud.sap/docs/node.js/cds-tx, https://cap.cloud.sap/docs/node.js/events#serving

Race conditions in CAP Node.js fall into four buckets. For each one, the table tells you which **declarative** mechanism to use first; handler code is the last resort.

| Bucket | Symptom | Fix order |
|---|---|---|
| **Cross-request TOCTOU** | Read row → check → write back, but two requests interleave | 1) `@odata.etag` on `modifiedAt` (see [concurrency-control.md](concurrency-control.md#1-optimistic-locking-with-etags)) → 2) `cds.tx(req)` wrapping the read+write → 3) `.forUpdate()` on the underlying entity |
| **Multi-statement non-atomicity** | Step 1 writes, step 2 crashes, step 1's effect remains | `cds.tx(req).run(async tx => { … })` |
| **Bootstrap / `cds.on('served')` race** | Handlers registered too late, or `cds.connect.to('db')` inside a sync hook | Use `cds.on('served', async () => …)` correctly — see §3 |
| **Eventing without idempotency** | Duplicate consumer invocation produces duplicate state | Idempotency key + `@odata.etag` check on write, see §4 |

---

## 1. TOCTOU between two requests on the same row

### Wrong

```js
this.on('submitOrder', async req => {
  const { bookID, qty } = req.data;
  const book = await SELECT.one.from(Books).where({ ID: bookID });
  if (book.stock < qty) req.reject(409, 'Out of stock');
  await UPDATE(Books, bookID).set({ stock: book.stock - qty });   // ← race
});
```

Two concurrent calls both pass the check, both write a stale `book.stock - qty`. Stock goes negative.

### Right — optimistic (preferred)

Add `@odata.etag` on `modifiedAt` (already provided by `managed`). Client must send `If-Match`. CAP returns 412 on stale. No handler change needed for plain CRUD; for the action above, do the check inside a single transaction with `cds.tx(req)`:

```js
this.on('submitOrder', async req => {
  const { bookID, qty } = req.data;
  await cds.tx(req).run(async tx => {
    const ok = await tx.run(
      UPDATE(Books, bookID).set({ stock: { '-=': qty } }).where({ stock: { '>=': qty } })
    );
    if (!ok) req.reject(409, 'Out of stock or stale state');
  });
});
```

The `WHERE stock >= qty` makes the decrement atomic at the DB level — no read needed, no race window.

### Right — pessimistic (when invariants span multiple rows)

```js
this.on('submitOrder', async req => {
  await cds.tx(req).run(async tx => {
    const book = await tx.run(
      SELECT.one.from(Books).where({ ID: req.data.bookID }).forUpdate({ wait: 5 })
    );
    if (book.stock < req.data.qty) req.reject(409, 'Out of stock');
    await tx.run(UPDATE(Books, book.ID).set({ stock: book.stock - req.data.qty }));
    await tx.run(INSERT.into(OrderLines).entries({ book_ID: book.ID, qty: req.data.qty, price: book.price }));
  });
});
```

SQLite does not support `forUpdate` — verify in HANA / Postgres ([concurrency-control.md §2](concurrency-control.md#2-pessimistic-locking-db-level-row-lock)).

---

## 2. Multi-statement atomicity

A `before`/`on` handler that runs several `INSERT`/`UPDATE`/`DELETE` MUST wrap them in `cds.tx(req).run(...)`. If anything throws inside, the transaction rolls back — partial writes never reach the DB.

```js
await cds.tx(req).run(async tx => {
  await tx.run(INSERT.into(Orders).entries(order));
  await tx.run(UPDATE(Books, order.book_ID).set({ stock: { '-=': order.qty } }));
  await tx.run(srv.emit('OrderCreated', { id: order.ID }));   // outbox-aware emit
});
```

**Never** mix `cds.db.run(...)` (default transaction) with `cds.tx(req).run(...)` (explicit) in the same operation — you get two transactions and lose atomicity.

---

## 3. Bootstrap / `cds.on('served')` race

CAP fires `served` synchronously to all registered listeners. Two mistakes the skill must avoid:

### Wrong

```js
cds.on('served', async () => {
  const db = await cds.connect.to('db');     // ← DANGER: race condition (CAP_Troubleshooting.md)
  await db.run(SELECT.from('Books'));
});
```

`served` listeners are invoked in series-with-await **only if** they all return promises that CAP awaits. Mixing `await cds.connect.to(...)` here can race handler registration in adjacent services. The CAP team's guidance: connect during `cds.on('bootstrap')` or inside a service's `init()`.

### Right

```js
// srv/cat-service.js
module.exports = class CatalogService extends cds.ApplicationService {
  async init() {
    this.db = await cds.connect.to('db');   // ← happens before any handler fires
    this.on('myAction', this.myActionHandler);
    return super.init();
  }
}
```

`init()` is awaited by CAP before serving any request — handlers and connections set up here are race-free.

### Audit pointer

[CAP_Troubleshooting.md](CAP_Troubleshooting.md) lines 95–105 cover this exact pattern. The skill should flag any `cds.on('served', async () => { await cds.connect.to(...) })` in user code.

---

## 4. Event-driven races (consumer idempotency)

When a service emits an event and a remote consumer processes it, networks duplicate messages. Without idempotency, double consumption double-decrements stock / charges twice / etc.

### Pattern

1. Producer **MUST** include a stable `eventID` (UUID) on every emit.
2. Consumer **MUST** record processed `eventID`s and short-circuit duplicates within a transactional outbox.
3. The actual mutation MUST be conditional (CAP CQL `where`-clause) so a concurrent retry can't undo a successful first write.

```js
// Producer
await srv.emit('OrderCreated', { eventID: cds.utils.uuid(), orderID: order.ID });

// Consumer
this.on('OrderCreated', async msg => {
  const { eventID, orderID } = msg.data;
  const seen = await SELECT.one.from(ProcessedEvents).where({ ID: eventID });
  if (seen) return;
  await cds.tx(msg).run(async tx => {
    await tx.run(INSERT.into(ProcessedEvents).entries({ ID: eventID, at: new Date() }));
    await tx.run(UPDATE(Inventory, orderID).set({ reserved: { '+=': 1 } }));
  });
});
```

Use the transactional outbox provided by `cds.messaging` so the emit + state update happen in the producer's same transaction.

---

## 5. Anti-patterns the skill rejects

- **Read-then-write without ETag, transaction, or atomic `where` clause.** Always one of the three.
- **`cds.connect.to('db')` inside `cds.on('served', async () => …)`** — bootstrap race.
- **Sharing a transaction handle across requests** (`cds.tx({})` cached at module load). Each request gets its own via `cds.tx(req)`.
- **Holding `.forUpdate()` across `await remoteService.run(...)`** — the remote call's latency leaks into the lock window.
- **Catching and swallowing errors inside `cds.tx(req).run(async tx => { … })`** — CAP relies on the thrown exception to roll back. Wrapping in `try/catch` without rethrowing silently commits a half-finished transaction.
- **Idempotent design via "if exists, skip"** read in JS — same TOCTOU bug as §1. Use a unique index + `INSERT ... ON CONFLICT DO NOTHING` (via plugin) or a recorded `processedEvents` row in the same transaction.

---

## 6. Audit checklist (for `sap-cap-code-review`)

- [ ] Every action that mutates a row also reads it inside the same `cds.tx(req)` transaction (or the mutation has an atomic `where` clause that encodes the invariant).
- [ ] No `cds.connect.to(...)` is called inside `cds.on('served', ...)`; service-to-service connections live in `init()`.
- [ ] No `await` happens between `.forUpdate()` and the dependent write, except trivial in-memory work.
- [ ] Every consumer of a domain event de-duplicates by `eventID` and records it in the same transaction as the side effect.
- [ ] No handler catches an error inside `cds.tx(req).run(...)` without rethrowing.
