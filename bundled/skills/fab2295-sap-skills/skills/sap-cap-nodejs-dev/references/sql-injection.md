# SQL Injection (and how CAP prevents it)

> Related: [cql-queries.md](cql-queries.md), [cql-patterns.md](cql-patterns.md), [databases.md](databases.md#native-queries), [best-practices.md](best-practices.md), [domain-first.md](domain-first.md)
> Capire anchors: https://cap.cloud.sap/docs/cds/cql, https://cap.cloud.sap/docs/node.js/cds-ql

CAP applications **should never produce SQL strings by hand**. The CQL builder always parameterizes values; raw SQL is the only place where injection becomes possible, and the skill restricts that path tightly.

---

## 1. Rule of thumb

| Goal | Use | Why it's safe |
|---|---|---|
| Read / write entities | CQL builder (`SELECT.from`, `INSERT.into`, `UPDATE`, `DELETE`) | Values are bound as parameters by the runtime; the SQL text never contains the user-supplied value. |
| Search across fields | `@cds.search` + `$search` | Translates to a parameterized `LIKE` server-side. |
| Filter by request data | `.where({ field: req.data.X })` or `.where({ field: { like: pattern } })` | Object syntax passes values as bind variables. |
| Native SQL (last resort) | `cds.db.run('… ?', [value])` with **positional placeholders** | The driver binds; the value is never interpolated into the SQL text. |

If the agent finds itself building an SQL string with template literals or `+`, **stop and rewrite as CQL**. That is the most common path to CWE-89.

---

## 2. Safe patterns (CQL)

```js
// Plain equality from request data
await SELECT.from(Books).where({ author_ID: req.data.authorID });

// Range filter
await SELECT.from(Books).where({ price: { between: 10, and: 50 } });

// Multi-condition
await SELECT.from(Books)
  .where({ stock: { '>': 0 } })
  .and({ author_ID: req.data.authorID });

// Pattern match (parameterized by CAP — value goes as a bind variable)
await SELECT.from(Books).where({ title: { like: `%${req.data.q}%` } });

// IN clause
await SELECT.from(Books).where({ ID: { in: req.data.ids } });
```

The `${req.data.q}` template literal in the `like` example **is safe** because the CQL builder treats the resolved string as a value to bind — not as SQL text. It produces a prepared statement like `WHERE title LIKE ?` with the `'%…%'` value as the parameter. The skill must understand this distinction: template literals are JS string assembly; they become injection only when the resulting string is handed to `cds.db.run` as the **SQL text**.

---

## 3. Unsafe patterns (forbidden)

### 3.1 String-concatenated raw SQL

```js
// 🚫 SQL INJECTION
await cds.db.run(`SELECT * FROM my_bookshop_Books WHERE title LIKE '%${req.data.q}%'`);
await cds.db.run(`UPDATE my_bookshop_Books SET stock = ${req.data.stock} WHERE ID = '${req.data.id}'`);
await cds.db.run('SELECT * FROM ' + req.data.tableName);
```

A request payload of `q = "x'); DROP TABLE my_bookshop_Books;--"` ends the application. **Rewrite as CQL** — the same operations are one line each with the builder.

### 3.2 Ordering / column names from request data

CQL parameterizes **values**, not **identifiers**. Dynamic column names taken from `req.data` are an injection vector even when passed through `.where({...})`:

```js
// 🚫 — req.data.sortBy reaches the SQL identifier slot
await SELECT.from(Books).orderBy(req.data.sortBy);
```

Validate identifiers against an explicit allow-list before they touch the query:

```js
const ALLOWED_SORT = new Set(['title', 'price', 'modifiedAt']);
const col = ALLOWED_SORT.has(req.data.sortBy) ? req.data.sortBy : 'title';
await SELECT.from(Books).orderBy(col);
```

### 3.3 Native SQL without placeholders

```js
// 🚫
await cds.db.run(`SELECT * FROM my_bookshop_Books WHERE stock > ${req.data.minStock}`);

// ✓ — values bound as parameters
await cds.db.run('SELECT * FROM my_bookshop_Books WHERE stock > ?', [req.data.minStock]);
```

If the operation **cannot** be expressed in CQL (rare: vendor-specific HANA function, partitioning hint, etc.), the skill MUST use positional `?` placeholders and pass values in the array argument. Concatenating values into the SQL text is a defect, full stop.

### 3.4 "Validation in JS, then use raw"

```js
// 🚫 — even with a regex check, the wrapping pattern is forbidden
if (!/^[a-z0-9_-]+$/i.test(req.data.id)) req.reject(400);
await cds.db.run(`DELETE FROM Books WHERE ID = '${req.data.id}'`);
```

JS-side validation is not a substitute for parameter binding. Use `DELETE.from(Books, req.data.id)`. Validation belongs to `@assert.format` in CDS.

---

## 4. Native SQL escape hatch — when and how

The escape hatch exists because some HANA features (vector ops, ST geometry, specific window-function syntax, partitioning) don't map to CQL yet. When you reach for it:

1. Confirm CQL cannot express the operation. Check [cql-queries.md](cql-queries.md) and [cql-patterns.md](cql-patterns.md). If it can — use CQL.
2. Use `cds.db.run('<sql>', [<bound-values>])` with `?` placeholders for every user-supplied value. **Identifier slots** (table / column names) get the allow-list treatment from §3.2.
3. Add a comment explaining why CQL was not enough — the next reviewer needs the rationale.

```js
// Why native: HANA-specific FUZZY() operator with weight tuning, not yet in CQL
const rows = await cds.db.run(
  `SELECT TOP 20 ID, SCORE() AS s FROM my_bookshop_Books
     WHERE CONTAINS(title, ?, FUZZY(0.7))
     ORDER BY s DESC`,
  [req.data.q]
);
```

---

## 5. Validation belongs to the schema, not handlers

Most "I need raw SQL to validate" reflexes are really "I need an annotation":

| Concern | Declarative answer |
|---|---|
| Required field | `@mandatory` |
| Range | `@assert.range: [min, max]` |
| Regex / format | `@assert.format: '<regex>'` |
| Unique | `@assert.unique: { key: [col] }` |
| Set of allowed values | `enum { … }` or association to code-list entity |
| Cross-row invariant | `@assert.integrity` (FK constraint) or composition |

Putting validation in CDS removes both the temptation to build SQL strings and the duplicate-validation bug where the JS check and the DB check disagree.

---

## 6. Audit checklist (for `sap-cap-code-review`)

A reviewer should fail the diff if any of the below appear:

- [ ] `cds.db.run` called with a template-literal SQL containing `${…}` interpolation, **without** a positional placeholder.
- [ ] `cds.db.run` called with `+` string concatenation involving any variable that traces back to `req.*`, headers, env, or another service's response.
- [ ] CQL `.orderBy(req.data.X)` / `.from(req.data.X)` without an identifier allow-list step right above it.
- [ ] User-facing validation written entirely in JS when an equivalent `@assert.*` or `@mandatory` exists.
- [ ] Any `eval`, `new Function`, or `vm.*` used to "build a query" — never the right answer in CAP.

---

## 7. Tests worth having

For every action that touches user input on a query:

- Feed it strings containing `'`, `"`, `;`, `--`, `\n`, `%`, `_`, `\\`. Expect a normal 4xx/empty-result response, never a 500 with `SQL error`.
- Feed it the unicode equivalents that some validators miss (`U+FF07` "ＦＵＬＬＷＩＤＴＨ APOSTROPHE", `U+2018`/`U+2019` smart quotes).
- For paginated reads, request `$top=1; DROP TABLE …` style query strings. CAP parses `$top` strictly; the test makes that explicit.
