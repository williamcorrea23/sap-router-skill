# Runtime exception risk (High)

Anchored in capire — Event Handlers (Node.js): https://cap.cloud.sap/docs/node.js/core-services and Best Practices: https://cap.cloud.sap/docs/node.js/best-practices

If a finding doesn't match a Rule ID below, do not classify it as High/Runtime.

---

## RTE-001 — Property access on `SELECT.one(...)` without null guard

**Trigger.** `await SELECT.one.from(E).where({...})` whose result is dereferenced (`.field`, destructured) without a `if (!row) return req.error(404, 'KEY')` check first.

Pattern:
```js
const book = await SELECT.one.from(Books).where({ ID })
return book.title    // ← throws TypeError if no row
```

**Reference.** capire — *"`SELECT.one` returns `undefined` (or `null`) when no row matches; guard before dereferencing."*

**Why.** OData clients commonly request entities by key; missing keys are routine. An unguarded handler turns a 404 into a 500.

**Suggested fix anchor.**
```js
const book = await SELECT.one.from(Books).where({ ID })
if (!book) return req.error(404, 'BOOK_NOT_FOUND', [ID])
```

---

## RTE-002 — `req.data.X` used without validation when X is optional

**Trigger.** A handler reads `req.data.fieldName` and passes it to `SELECT.where(...)`, `UPDATE.set(...)`, arithmetic, or string methods, where `fieldName` is declared as optional in the action's `.cds` signature (no `not null` and no `@mandatory`).

**Reference.** capire — *"Optional parameters can be `undefined`. Use `@mandatory` or `not null` in the action signature, or guard explicitly in the handler."*

**Why.** `undefined.toLowerCase()`, `WHERE id = undefined`, `0 - undefined === NaN` — all throw or produce silent garbage.

**Suggested fix anchor.** Either tighten the signature with `@mandatory` (preferred), or `if (req.data.fieldName == null) return req.error(400, 'MISSING_FIELD', ['fieldName'])`.

---

## RTE-003 — Unhandled promise rejection in `forEach` / detached `.then`

**Trigger.** `array.forEach(async ...)` (already in CONC-004 from a concurrency angle; flag only ONE — prefer Concurrency for the lost-tx aspect; flag here only if `forEach` has no `await` outside but uses `Promise.then` chains without `.catch`).

`promise.then(handler)` without `.catch(...)` AND not in an `await` chain.

**Reference.** capire — *"Unhandled rejections terminate the Node.js process under modern defaults. Always `await` or `.catch` promises returned by handlers."*

**Why.** A single rejected promise crashes the worker; in cluster mode this is hidden but causes per-request failures.

**Suggested fix anchor.** Use `await` in async functions; add `.catch(err => req.error(500, 'INTERNAL', [err.message]))` for fire-and-forget where unavoidable.

---

## RTE-004 — `req.error(...)` followed by code that assumes success

**Trigger.** `req.error(400, ...)` (which queues an error and **continues**) followed by code that mutates `req.data` or runs DB writes, without an early `return`.

Pattern:
```js
if (!req.data.title) req.error(400, 'TITLE_REQUIRED')
await INSERT.into(Books).entries({ title: req.data.title, ... })
// ← runs even though the error was queued
```

**Reference.** capire — *"`req.error` accumulates an error and returns; it does NOT throw. Use `return req.error(...)` to short-circuit."*

**Why.** The DB write happens with the bad/missing data; the response includes both an error AND the side effect.

**Suggested fix anchor.** Always `return req.error(...)` to exit the handler.

---

## RTE-005 — `JSON.parse(...)` on user input without try/catch

**Trigger.** `JSON.parse(req.data.X)`, `JSON.parse(req.headers['x-...'])`, `JSON.parse(req.query.X)` without a surrounding try/catch.

**Reference.** capire — general; capire's *"Input validation"* section covers `@assert.*` annotations as the preferred validation layer, not handler-side parsing.

**Why.** Malformed JSON throws `SyntaxError`; the handler never returns a controlled error. The OData adapter turns this into a 500.

**Suggested fix anchor.** Wrap in try/catch and return `req.error(400, 'INVALID_JSON')`. Better still: declare the field as a `cds.Map` or structured type and let CAP parse and validate it.

---

## RTE-006 — Blind `await` of a missing service or entity

**Trigger.** `cds.connect.to('Service')` where `'Service'` is not declared in `cds.requires.<X>` of `package.json` and not defined in any `srv/*.cds`. Detected by:
- a connect call to a string literal that doesn't match any `service X` block in the project's CDS, AND
- no entry under `cds.requires` in `package.json` matching that name.

**Reference.** capire — *"`cds.connect.to(name)` resolves the name against `cds.requires`; misspellings throw at runtime when the handler runs."*

**Why.** Typo bugs only surface in the first request to that handler.

**Suggested fix anchor.** Use the typed import (`const { Service } = await cds.connect.to('Service')` requires the symbol to exist) or add the name to `cds.requires`.

---

## RTE-007 — Implicit `+` on `req.data.X` of unknown numeric type

**Trigger.** `req.data.X + ...` (string concatenation OR arithmetic) where `X` is declared as `Decimal` or `Integer` in CDS, AND no coercion is performed.

**Reference.** capire — *"OData numbers may arrive as strings depending on protocol negotiation. Coerce explicitly with `Number(...)` or destructure with default."*

**Why.** `5 + '2'` is `'52'`, not `7`. Subtle data corruption that only shows up at certain protocol/profile combinations.

**Suggested fix anchor.** `const qty = Number(req.data.quantity)` and validate `if (!Number.isFinite(qty)) return req.error(400, 'INVALID_NUMBER')`.

---

## RTE-008 — `req.params[N]` accessed by positional index

**Trigger.** `req.params[0]`, `req.params[1]`, etc. used as a UUID/string in `where({ ID: ... })` or string operations.

**Reference.** capire — *"As of cds@9, `req.params` is an array of objects (`{ID: 'x'}`), not plain values. Even before cds@9, accessing by index is fragile across navigation paths."*

**Why.** Pre-9: works for single-keyed entities but breaks for compound keys. Post-9: returns `{ID: 'x'}` so `where({ ID: req.params[0] })` becomes `where({ ID: {ID: 'x'} })` — silently wrong query.

**Suggested fix anchor.** Use `req.data.<keyField>` (for action keys) or destructure: `const [{ ID } = {}] = req.params; where({ ID })`.

---

## RTE-009 — `Date` arithmetic on `Timestamp` field as string

**Trigger.** `new Date(row.modifiedAt) - someDate`, or `row.modifiedAt > someDate` where `row.modifiedAt` came from a CAP read that may have given an ISO string.

**Reference.** capire — *"Timestamps are returned as ISO 8601 strings; coerce with `new Date(...)` before comparing or subtracting."*

**Why.** String comparisons of ISO 8601 happen to be lexicographically correct, but subtraction/arithmetic on the raw string yields `NaN`.

**Suggested fix anchor.** `const t = new Date(row.modifiedAt)` once, then use `t`.

---

## RTE-010 — `await` skipped on `INSERT/UPDATE/DELETE`

**Trigger.** `INSERT.into(...)`, `UPDATE(...)`, `DELETE.from(...)` without `await` and not assigned to a variable that is later awaited or returned.

**Reference.** capire — *"Mutations are queries; without `await`, the runtime sees a pending Promise that never executes against the DB until evaluated."*

**Why.** The query is constructed but never sent. Silent no-op.

**Suggested fix anchor.** Add `await` and (optionally) `return` it from the handler.

---

## RTE-011 — Throwing string instead of `Error`

**Trigger.** `throw 'message'` or `throw {message: '...'}` (raw object).

**Reference.** capire — general; capire's *"Errors thrown in handlers are caught and translated; use `Error` instances or `req.error/reject`."*

**Why.** Stack traces are missing; some downstream catchers behave differently for non-Error throwables.

**Suggested fix anchor.** Prefer `req.error(code, 'KEY', args)` (or `req.reject`); if you must `throw`, use `throw new Error('KEY')`.

---

## RTE-012 — Optional chaining absent on chained navigation

**Trigger.** `row.author.name` (or longer paths) where the navigation is to a not-required association (no `not null`, no `@mandatory`) and the row was fetched without `expand`.

**Reference.** capire — *"Reading without `expand` does not populate associations. Direct property access on a missing assoc throws."*

**Why.** Without `expand`, `row.author` is undefined; `.name` throws.

**Suggested fix anchor.** Add `.columns(b => { b('*'); b.author(a => a('name')) })` to the SELECT, or use `row.author?.name` and accept it may be undefined.

---

## What this section is NOT

- It does not run the code or simulate inputs. It flags syntactic patterns that capire calls out as common pitfalls.
- It does not flag every possible undefined/null access — only the patterns that map to a Rule ID above.
