# Best Practices — SAP CAP Node.js

This skill follows the CAP **domain-first / less-code** principle. See
[domain-first.md](domain-first.md) for the philosophy and decision order. The rules below
are the day-to-day patterns the skill applies.

## DO

### Modeling
- Use `cuid`, `managed`, `temporal` aspects from `@sap/cds/common` — don't reinvent keys,
  audit fields, or validity periods.
- Keep the domain model in `db/`, the service surface in `srv/`. UI lives in `app/` and is
  out of scope for this skill (CAP-side `@UI.*` annotations in `.cds` are fine).
- Use **managed associations** — let CAP own the foreign keys.
- Use **compositions** for parent/child ownership (cascading delete, draft inclusion).
- Design **single-purpose services** per use case (one service per UI / consumer).

### Declarative over imperative
- Validate with `@mandatory`, `@assert.range`, `@assert.format`, `@assert.unique`.
- Authorize with `@requires` / `@restrict`. Never check roles by hand in handlers.
- Expose subsets with projections (`entity X as projection on Y where …`).
- Compute fields with CDS calculated elements (`= expr`, `stored`).
- Join with CDS views instead of orchestrating multiple queries in JS.
- Use `@odata.draft.enabled` for Fiori draft flows.
- Use `@cds.search` for search; let `$search` do the work.

### Persistence
- Start with SQLite for development (`@cap-js/sqlite`), switch to HANA for production.
- Always go through the CQL builder (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) — never
  concatenate SQL strings.
- Use `cds.tx(req).run(...)` to wrap multi-step writes in a transaction.
- Use CSV files in `db/data/` for seed / reference data.

### Handlers (when truly needed)
- Use class-based services extending `cds.ApplicationService`.
- Prefer `before` for validation/enrichment, `on` for replacing default behavior, `after`
  for post-processing.
- Use `req.error(...)` for accumulating errors, `req.reject(...)` to abort immediately.
- Connect to other services via `await cds.connect.to('<name>')`.
- Emit domain events with `await srv.emit('Name', payload)`.

### Public-API hygiene
- Import only from documented entry points: `@sap/cds`, `@sap/cds/common`, `@cap-js/*`,
  `@sap/cds-mtxs`.
- If the docs don't show it, don't use it.

## DON'T

### Modeling
- Don't model UI structure into the domain entities. UI shape goes in `@UI.*` annotations.
- Don't write polymorphic god-entities. Split them.
- Don't repeat across services what aspects already provide.

### Imperative drift
- Don't implement validation in handlers when an annotation can express it.
- Don't check `req.user.is(...)` when `@requires` / `@restrict` can express it.
- Don't write a custom `READ` handler that only runs the query and returns it.
- Don't reinvent draft semantics, pagination, `$search`, `$expand`, or `$count`.
- Don't write a custom OData / REST / GraphQL provider. Use CAP's; for GraphQL,
  use `@cap-js/graphql`.

### Persistence
- Don't use `SELECT *` — be explicit about projections.
- Don't bypass CQL with raw SQL strings.
- Don't hardcode credentials in config files. Use service bindings, `cds bind`, or env vars.
- Don't put production credentials in `package.json` or commit them to git.

### APIs
- Don't import from `@sap/cds/lib/...`, `_private`, `__internal`, or any undocumented path.
- Don't use methods/options marked `@deprecated`, `@experimental`, `@internal`, or
  `@protected`.
- Don't rely on undocumented behavior of a documented API ("it happens to work today").

### Architecture
- Don't split into microservices prematurely.
- Don't introduce a second backend in another language to "complement" CAP. If it can't be
  done in CAP Node.js, it's outside this skill's scope.
- Don't write UI code in this skill.

## Code smells (review triggers)

If you see any of these in a diff, stop and reshape the model first:

- A handler that mirrors what `@assert.*` / `@mandatory` would do.
- `if (!req.user.is('admin'))` in JS — should be `@restrict`.
- A handler that runs `SELECT` + filter + return — should be a projection.
- `cds.db.run(<sql string>)` — should be CQL.
- `require('@sap/cds/lib/...')` — internal, replace.
- Repeated audit / change tracking code — use `@cap-js/audit-logging` or
  `@cap-js/change-tracking`.
- Custom file upload plumbing — use `@cap-js/attachments`.
- Manual `where like '%…%'` for search — use `@cds.search` + `$search`.

## Reference checklist for "Is this PR domain-first?"

- [ ] Each new entity uses an aspect from `@sap/cds/common` where it fits (`cuid`,
      `managed`, `temporal`).
- [ ] Validation lives in annotations, not in `before` handlers.
- [ ] Authorization lives in annotations, not in handler role checks.
- [ ] Any new `on` handler is genuine business logic, not framework reimplementation.
- [ ] No imports from internal / undocumented paths.
- [ ] No deprecated APIs reintroduced.
- [ ] No raw SQL strings.
- [ ] No UI / non-CAP-Node.js code.
