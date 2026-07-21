# Domain-First / Less Code → Less Mistakes

> "Every line of code not written is free of errors."
> — SAP Capire, *Avoid Technical Debt*
> https://cap.cloud.sap/docs/get-started/features#less-code-%E2%86%92-less-mistakes

CAP is built on the principle of capturing **domain knowledge and intent declaratively**
("What, not How"), not by writing imperative code. This skill follows that principle: it
prefers the CDS model, annotations, projections, and CAP's generic providers over hand-rolled
handlers and SQL.

## What CAP serves out of the box

For every entity defined in CDS, the generic providers automatically deliver:

- CRUD operations
- Nested document serving (deep reads / writes through compositions)
- Draft support (Fiori draft handling, `@odata.draft.enabled`)
- Media data handling
- Search, pagination, sorting
- Authentication and authorization (from `@requires` / `@restrict`)
- Localization (translated texts, currencies)
- Input validation (`@mandatory`, `@assert.*`)
- Auto-generated keys (`cuid`)
- Concurrency control (managed `ETag` / `@odata.etag`)

If the framework already does it, **do not re-implement it** in a handler.

## Decision order (use this every time)

When you need a behavior, ask in this order — only drop to the next step if the previous
one cannot express it:

1. **Schema** — model it as types, associations, compositions, aspects.
2. **Annotations** — `@mandatory`, `@assert.range`, `@assert.unique`, `@assert.format`,
   `@readonly`, `@insertonly`, `@requires`, `@restrict`, `@cds.persistence.*`,
   `@cds.search`, `@Core.Computed`, etc.
3. **Views / projections** — expose subsets, filter rows, compute fields, join entities
   in CDS instead of in JS.
4. **Status Flows** — when the use case is a true state machine (a row walks through a
   finite set of named states), model transitions declaratively with `@flow.status` +
   `@from` + `@to`. CAP validates the entry state and writes the target state
   automatically. See [status-flow.md](status-flow.md). Caveat: Status Flows are
   currently **Gamma** in capire; only adopt with explicit team acceptance of that
   stability tier — otherwise stay on annotations from step 2.
5. **CAP plugins** — `@cap-js/attachments`, `@cap-js/audit-logging`,
   `@cap-js/change-tracking`, `@cap-js/telemetry`, `@cap-js/graphql`. Don't re-invent
   what a documented plugin already does.
6. **Concurrency control** — when reads and writes can interleave across requests,
   reach for `@odata.etag` (via `managed.modifiedAt`) and, when invariants span multiple
   rows, `cds.tx(req)` with `.forUpdate()` on the base entity. See
   [concurrency-control.md](concurrency-control.md) and [race-conditions.md](race-conditions.md).
7. **Event handlers** (last resort) — write a `before` / `on` / `after` handler **only**
   for behavior that is genuinely business logic and cannot be expressed declaratively
   by steps 1–6. Never re-implement what `@from`/`@to`, `@odata.etag`, `@assert.*`,
   `@requires`, or a projection already does for free.

> If you find yourself writing a handler that reads, filters, and returns an entity, stop
> and model it as a projection.

## What goes where

| Concern                              | Where to put it                                  |
|--------------------------------------|--------------------------------------------------|
| Keys, types, relationships           | `db/schema.cds` (CDS entities + aspects)          |
| Required / range / format / unique   | CDS `@mandatory`, `@assert.*`                    |
| Computed fields                      | CDS calculated elements (`= expr`, `stored`)     |
| Exposed subset / filtered rows       | `srv/*.cds` projection (`as projection on …`)    |
| Joins across entities                | CDS view (`as select from … join …`)             |
| Auth (who can do what)               | `@requires`, `@restrict` in CDS                  |
| UI shape (Fiori Elements)            | CDS `@UI.*`, `@Common.*` annotations             |
| i18n texts                           | `_i18n/` `.properties` files                     |
| Seed / reference data                | CSV in `db/data/`                                |
| Cross-cutting concerns (audit, etc.) | `@cap-js/*` plugin (configured, not coded)       |
| Genuine business logic               | Node.js event handler in `srv/*.js`              |

## Annotations to prefer over code

### Validation
```cds
entity Books {
  key ID    : UUID;
  title     : String(111) @mandatory;
  isbn      : String      @assert.format: '^[0-9-]{10,17}$';
  stock     : Integer     @assert.range: [0, 99999];
  price     : Decimal(9,2) @assert.range: [0, 999999.99];
}
```
No `req.error(400, …)` needed.

### Authorization
```cds
@requires: 'authenticated-user'
service CatalogService {
  @restrict: [
    { grant: 'READ',  to: 'any' },
    { grant: 'WRITE', to: 'admin' }
  ]
  entity Books as projection on db.Books;
}
```
No manual `req.user.is('admin')` checks.

### Read-only / insert-only
```cds
entity Orders {
  key ID     : UUID;
  createdAt  : Timestamp @readonly;
  orderNo    : String    @readonly;
  status     : String;
}
```

### Search
```cds
@cds.search: { title, author.name }
entity Books { … }
```
No custom `where like '%…%'` handler.

### Drafts (Fiori)
```cds
@odata.draft.enabled
entity Books as projection on db.Books;
```
Draft lifecycle is handled by CAP.

## Views and projections to prefer over handlers

### Filtered exposure
```cds
entity AvailableBooks as projection on db.Books
  where stock > 0;
```

### Computed field
```cds
entity Books : managed {
  key ID      : UUID;
  stock       : Integer;
  isAvailable : Boolean = (stock > 0) stored;
}
```

### Aggregated view
```cds
entity AuthorStats as
  select from db.Authors {
    ID,
    name,
    count(books.ID) as bookCount : Integer
  } group by ID, name;
```

### Joined view
```cds
entity BookRows as
  select from db.Books {
    ID, title,
    author.name as authorName,
    currency.symbol as currencySymbol
  };
```

## When a handler IS the right answer

A handler is appropriate when:

- The behavior depends on **external state** (call another service, send mail, publish event).
- The behavior is a **multi-step business transaction** (e.g., `submitOrder`: check stock,
  insert order, decrement stock, emit event) that cannot be expressed as a projection.
- You need to **enrich** computed runtime data that doesn't belong in the database.
- You need to **emit** a domain event via `srv.emit(...)`.

Even then, keep the handler short. Push everything you can back to the model.

## Anti-patterns this skill rejects

- Writing a custom `READ` handler that just runs the query and returns it — CAP already does that.
- Looping through `req.data` to validate fields one by one — use `@mandatory` / `@assert.*`.
- Implementing a "search endpoint" by hand — use `@cds.search` or `$search`.
- Re-implementing draft semantics — use `@odata.draft.enabled`.
- Writing raw SQL through `cds.db.run(<sql string>)` when CQL can express it.
- Reaching into `@sap/cds/lib/*` to "get more control" — internals are not a public API.
- Bypassing `@restrict` and writing role checks in handlers.

## Reference checklist before adding a handler

Before writing a new `.on` / `.before` / `.after`, confirm:

- [ ] The behavior can't be expressed as a CDS calculated element.
- [ ] It can't be expressed as a projection or view.
- [ ] It can't be expressed as an annotation (`@assert.*`, `@restrict`, `@mandatory`, etc.).
- [ ] No `@cap-js/*` plugin already does it.
- [ ] It is genuine business logic, not infrastructure.

If any box is unchecked, fix the model first.
