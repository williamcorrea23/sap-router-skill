# JSDoc conventions (Medium)

Anchored in capire — *"Documenting Service Implementations"* under https://cap.cloud.sap/docs/node.js/best-practices and the @cap-js/cds-types JSDoc support.

The skill flags missing or wrong JSDoc on the **public surface** of a CAP service: handlers for actions/functions, exported helpers used by handlers, and class-level service definitions. Internal pure functions are out of scope unless they are the only place a behavior is documented.

If a finding doesn't match a Rule ID below, do not classify it as Medium/JSDoc.

---

## DOC-001 — Handler for a CDS action/function without JSDoc

**Trigger.** `this.on('<actionName>', async (req) => { ... })`, `this.on('<functionName>', ...)`, or a free function used as `this.on('X', myHandler)` whose declaration has no JSDoc immediately above it, AND the action/function appears in a `srv/*.cds` file (i.e. it is part of the public service contract).

**Reference.** capire — *"Document handlers that implement a public action or function so that consumers reading the impl alongside the model understand pre/post-conditions."*

**Why.** The CDS signature shows arity and types but not pre-conditions, side effects, error codes, or transactional semantics. Without JSDoc, a future maintainer must reverse-engineer the contract from the body.

**Suggested fix anchor.** Add a JSDoc with at least:
```js
/**
 * Submits an order for the given book/quantity.
 *
 * @param {Object} req - CAP request.
 * @param {Object} req.data
 * @param {string} req.data.book - UUID of the Book.
 * @param {number} req.data.quantity - Positive integer.
 * @returns {Promise<Object>} The created Order row.
 * @throws 400 if quantity ≤ 0; 404 if book not found; 409 if discontinued or out of stock.
 */
this.on('submitOrder', async (req) => { ... })
```

---

## DOC-002 — Handler JSDoc missing `@throws` for documented error codes

**Trigger.** A handler with JSDoc that mentions `req.error(<code>, ...)` calls in the body but has no `@throws` tag listing those codes.

**Reference.** capire — *"`@throws` is the only place where a reader of the impl finds the error contract; CDS itself doesn't declare error codes."*

**Why.** Consumers (UI, API clients) need the error code list to handle them; without `@throws` they must read the body.

**Suggested fix anchor.** Add a `@throws 4xx — <i18n key or short reason>` line per `req.error/reject` call.

---

## DOC-003 — Public exported helper without JSDoc

**Trigger.** A function declared at module top-level that is `module.exports = ...`, `exports.X = ...`, or referenced from another file via `require(...)`, AND has no JSDoc.

**Reference.** capire — general; capire's *"Project Structure"* nudges toward small, documented helpers under `srv/_lib` or `srv/utils`.

**Why.** Cross-file callers depend on the function's contract; without JSDoc, types/refactors are guesswork.

**Suggested fix anchor.** Add JSDoc with `@param` and `@returns`. If the function uses CAP-specific types (`req`, `cds.Service`), document those explicitly.

---

## DOC-004 — JSDoc `@param` types out of sync with CDS signature

**Trigger.** A handler whose JSDoc lists `@param {string} req.data.X` but the CDS action declares `X : Integer` (or vice versa).

**Reference.** capire — *"Keep JSDoc types in sync with the CDS signature; mismatches cause type-checker drift and onboarding confusion."*

**Why.** Future maintainers trust the JSDoc; a wrong type leads to wrong assumptions about coercion, validation, and downstream usage.

**Suggested fix anchor.** Update the JSDoc to match the CDS type — string ↔ `string`, Integer/Decimal ↔ `number`, Boolean ↔ `boolean`, Date/Timestamp ↔ `string` (ISO) or `Date`.

---

## DOC-005 — Class-level JSDoc missing on `cds.ApplicationService` subclass

**Trigger.** `module.exports = class FooService extends cds.ApplicationService { ... }` (or `module.exports = class FooService extends cds.Service`) without a JSDoc block immediately above the class declaration.

**Reference.** capire — *"A service implementation class corresponds to a `service` block in CDS; document its purpose, the entities/actions it serves, and any cross-cutting behaviors set up in `init()`."*

**Why.** The class is the entry point; readers should understand what it does without first reading every handler.

**Suggested fix anchor.**
```js
/**
 * CatalogService implementation — exposes browseable Books with stock-aware
 * read enrichment, custom order submission, and discontinue/archive actions.
 *
 * @extends cds.ApplicationService
 */
module.exports = class CatalogService extends cds.ApplicationService { ... }
```

---

## DOC-006 — JSDoc claims behavior that the code doesn't do

**Trigger.** JSDoc says `@returns {Order}` but the handler returns a plain object, `void`, or throws. JSDoc says `@throws 404` but no `req.error(404, ...)` exists in the handler body.

**Reference.** capire — *"Stale JSDoc is worse than missing JSDoc."*

**Why.** Confidently wrong documentation actively misleads.

**Suggested fix anchor.** Either remove the inaccurate tag or align the implementation with the documented behavior. The skill does NOT pick which — it is a human decision.

---

## What this section is NOT

- The skill does NOT enforce a specific JSDoc style (TypeScript-flavored vs classic). Either is acceptable as long as the public surface is described.
- It does NOT flag missing JSDoc on private internal helpers (`_helper`, `#priv`) or on test files.
- It does NOT validate JSDoc tag syntax. A malformed tag is not caught here; use `eslint-plugin-jsdoc` for that.
- It does NOT flag CDS comments (`/** ... */` in `.cds`). CDS doc comments are out of scope.
