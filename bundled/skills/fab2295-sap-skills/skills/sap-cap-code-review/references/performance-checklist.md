# Performance checklist (High)

Anchored in capire — Best Practices: https://cap.cloud.sap/docs/node.js/best-practices and CQL patterns: https://cap.cloud.sap/docs/node.js/cds-ql

If a finding doesn't match a Rule ID below, do not classify it as High/Performance.

---

## PERF-001 — N+1 SELECT inside a loop

**Trigger.** A `for`/`while`/`for...of` loop that contains `await SELECT...`, `await UPDATE...`, `await INSERT...`, or `await DELETE...` whose WHERE clause depends on the loop variable.

Pattern:
```js
for (const order of orders) {
  const book = await SELECT.one.from(Books).where({ ID: order.book_ID })
  // ...
}
```

**Reference.** capire — *"Use joins or `expand` instead of fetching related rows one by one. Each round-trip costs ~1 ms locally, multi-ms in production."*

**Why.** Linear DB round-trips. 1000 orders ≈ 1000 SELECTs. Latency dominates everything.

**Suggested fix anchor.** Replace with one query using `expand`/`columns` traversal, or batch with `WHERE ID IN (?, ?, ...)`:

```js
const ids = orders.map(o => o.book_ID)
const books = await SELECT.from(Books).where({ ID: { in: ids } })
```

---

## PERF-002 — `SELECT *` on a wide table

**Trigger.** `SELECT.from(E)` or `SELECT.from('E')` without `.columns(...)`, on an entity with ≥ 8 declared elements OR with at least one `LargeString` / `LargeBinary` field.

**Reference.** capire — *"Be specific. Select only the columns you need; SELECT * pulls every column including blobs."*

**Why.** Wire payload bloats; `LargeBinary` columns can be megabytes. The runtime serializes/deserializes every byte.

**Suggested fix anchor.** Add `.columns('id', 'title', 'stock')` listing exactly the fields the handler reads.

---

## PERF-003 — `.columns(...)` over an unbounded `expand`

**Trigger.** `SELECT.from(E).columns(b => { b.relation('*') })` or any `expand` with `*` on a to-many association without `.limit(...)`.

**Reference.** capire — *"Bound `expand` of to-many associations to a sensible page size; otherwise a single read can pull the entire child collection."*

**Why.** A single read fetching all children of a popular parent (e.g. all 100k orders of a customer) is a worst-case query.

**Suggested fix anchor.** Add `.limit(50)` (or paginate explicitly) on the to-many side.

---

## PERF-004 — Missing `.limit(...)` on user-facing READ

**Trigger.** A custom `this.on('READ', E, ...)` handler that returns `SELECT.from(E)` without `.limit(...)` and the entity has no `@cds.query.limit` annotation.

**Reference.** capire — *"OData READ default page size kicks in only when the framework dispatches the query. Custom handlers that bypass the dispatcher must paginate explicitly."*

**Why.** Custom READ handlers can return unbounded result sets that bypass OData paging.

**Suggested fix anchor.** Use `req.query` (the dispatcher hands you the query already paginated). If you must build from scratch, copy the page size from `req.query.SELECT.limit` or set a hard `.limit(100)`.

---

## PERF-005 — Heavy work inside `before` handler that runs on every request

**Trigger.** A `this.before('READ', '*', ...)` or `this.before(['READ','UPDATE'], '*', ...)` whose body does:
- a remote HTTP call
- a `SELECT.from(...)` not derived from the request key
- a synchronous JSON parse / regex over a large constant

**Reference.** capire — *"`before` handlers run for every request before the dispatcher proceeds. They are the wrong place for expensive setup; do it once at `init()` time and cache the result."*

**Why.** The cost multiplies by every request.

**Suggested fix anchor.** Move static work to `init()` with `await this.prepended(async () => {...})` or top-level constants; cache HTTP responses with the standard `cds.requires.<svc>.cache` config.

---

## PERF-006 — Sequential `await`s that could be parallel

**Trigger.** Two or more `await` statements in series whose right-hand sides are independent (no shared variable), inside the same handler.

Pattern:
```js
const books = await SELECT.from(Books)
const authors = await SELECT.from(Authors)
```

**Reference.** capire — *"Use `Promise.all` for independent reads to overlap latency."*

**Why.** Each `await` adds the round-trip latency in series. Parallel reads halve the wall time.

**Suggested fix anchor.**
```js
const [books, authors] = await Promise.all([
  SELECT.from(Books),
  SELECT.from(Authors)
])
```

---

## PERF-007 — `cds.connect.to(...)` called inside a handler

**Trigger.** `await cds.connect.to('Service')` inside `this.on/before/after`, executed on every request rather than once at service `init()`.

**Reference.** capire — *"`cds.connect.to` is idempotent but does work on each call (lookup, plugin chain). Call once at `init()` and reuse the returned service."*

**Why.** Adds avoidable per-request overhead and complicates testing/mocking.

**Suggested fix anchor.** In `init()`, do `this._other = await cds.connect.to('Other')`; in handlers, use `this._other`.

---

## PERF-008 — `JSON.parse(JSON.stringify(...))` deep clone on hot path

**Trigger.** `JSON.parse(JSON.stringify(x))` inside a handler or in code reachable per request.

**Reference.** capire — general Node.js performance guidance referenced from *"Best Practices › Avoid expensive serialization on the request path."*

**Why.** Two full passes over potentially-large request payloads. Especially bad for `expand`ed responses.

**Suggested fix anchor.** Use `structuredClone(x)` (Node ≥ 17), or refactor so cloning isn't needed.

---

## PERF-009 — Using array `.includes(...)` for repeated lookups in a hot path

**Trigger.** `array.includes(x)` inside a loop or per-request handler with a static `array` of length ≥ 10.

**Reference.** capire — performance neutral; this is a Node.js Big-O concern that capire's best-practices section nods to under *"avoid linear scans in handler bodies"*.

**Why.** O(n) per check; over loops becomes O(n²).

**Suggested fix anchor.** Build a `Set` once at `init()` time and use `set.has(x)` (O(1)) inside the handler.

---

## PERF-010 — `await` of an already-resolved value in a tight loop

**Trigger.** `await constant` or `await synchronousFunction()` inside a hot loop where the awaited value is not a promise, OR where awaiting it is unnecessary (the function returns synchronously).

**Reference.** capire — general Node.js perf; capire warns against scattering needless `await` because it forces microtask boundaries that the V8 optimizer can't elide.

**Why.** Each `await` is a microtask hop; in tight loops this adds up to measurable overhead.

**Suggested fix anchor.** Drop the `await` if the function is synchronous; or pre-await the value once outside the loop.

---

## PERF-011 — Disabled `cds.requires.db.pool` settings without justification

**Trigger.** In `package.json`: `cds.requires.db.pool = false` or pool settings that disable connection reuse (`max: 1` with high concurrency expected).

**Reference.** capire — *"Connection pooling is enabled by default; disabling it is a perf hit unless you have a specific reason (e.g. PostgreSQL with PgBouncer in transaction mode)."*

**Why.** Every request opens/closes a DB connection. At sustained traffic, the connection establishment cost dominates.

**Suggested fix anchor.** Remove the override; let the default pool apply. If a specific limit is needed, document it in a comment and set `min`/`max` to sensible values.

---

## PERF-012 — `req.query` ignored — re-running an unconditional SELECT in a custom READ

**Trigger.** A `this.on('READ', E, async (req) => { ... })` handler that issues `SELECT.from(E)` (or a fresh CQN) instead of `SELECT.from(req.query.SELECT.from)` / `cds.run(req.query)`.

**Reference.** capire — *"Custom READ handlers should respect the user's `$filter`, `$top`, `$skip`, `$expand`. The simplest way is `await next()` (delegate) or `await cds.run(req.query)`."*

**Why.** Bypassing `req.query` discards filter/paging from the OData layer, returning the full table to a client that asked for one row.

**Suggested fix anchor.** Prefer `return next()` or `return await cds.run(req.query)` if you only need to add side effects; only build a fresh CQN when the use case really differs.

---

## What this section is NOT

- Not a profiler. Real perf regressions come from production telemetry; this is static guesswork.
- Not a CDN/HTTP/cache-control review. Those live above the CAP layer.
- Not a SQL plan review (no `EXPLAIN`). The skill cannot tell you whether an index is being used.
