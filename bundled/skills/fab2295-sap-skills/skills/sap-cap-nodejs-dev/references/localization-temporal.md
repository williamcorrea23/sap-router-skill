# Localization and Temporal Data Reference

**Source**: [https://cap.cloud.sap/docs/guides/](https://cap.cloud.sap/docs/guides/)

## Internationalization (i18n)

### Text Bundle Structure

Text bundles use properties files with locale suffixes:

```
_i18n/
├── i18n.properties          # Default fallback
├── i18n_en.properties       # English
├── i18n_de.properties       # German
├── i18n_fr.properties       # French
└── i18n_zh_TW.properties    # Traditional Chinese
```

### Properties File Format

```properties
# i18n_en.properties
Book = Book
Books = Books
Author = Author
title = Title
description = Description
stock = Stock
price = Price

# Error messages
error.title.required = Title is required
error.stock.negative = Stock cannot be negative
```

### Using in CDS

```cds
entity Books {
  key ID : UUID;
  title  : String @title: '{i18n>title}';
  descr  : String @title: '{i18n>description}';
  stock  : Integer @title: '{i18n>stock}';
}
```

### CSV Alternative

```csv
key;en;de;fr
Book;Book;Buch;Livre
Author;Author;Autor;Auteur
title;Title;Titel;Titre
```

### Locale Determination (Priority Order)

1. `sap-locale` URL parameter
2. `sap-language` URL parameter
3. `Accept-Language` HTTP header

### Configuration

```json
{
  "cds": {
    "i18n": {
      "default_language": "en",
      "folders": ["_i18n", "i18n"],
      "preserved_locales": ["zh_CN", "zh_TW", "en_GB", "fr_CA"]
    }
  }
}
```

---

## Localized Error Messages (`messages.properties`)

> Capire: https://cap.cloud.sap/docs/node.js/events#req-error

CAP resolves error messages from a **dedicated bundle named `messages`** — separate from
the UI/label bundle (`i18n`). Use it for `req.error()` / `req.reject()` / `req.info()` /
`req.warn()` / `req.notify()` payloads.

### Where the bundle lives

```
i18n/                              ← or _i18n/, per cds.i18n.folders
├── messages.properties            ← default (English-equivalent fallback)
├── messages_en.properties
├── messages_de.properties
├── messages_pt_BR.properties
└── messages_zh_TW.properties
```

The folder is the same as the UI bundle; only the **file basename** (`messages`)
differs. CAP looks the key up in `messages.<locale>.properties` first, then falls
back to `messages.properties`.

### File format

```properties
# i18n/messages_en.properties
BOOK_NOT_AVAILABLE      = Book {0} is out of stock (requested {1}, available {2}).
ORDER_LIMIT_EXCEEDED    = Order total {0} exceeds the per-customer limit ({1}).
INVALID_DISCOUNT_CODE   = "{0}" is not a valid discount code.
```

```properties
# i18n/messages_pt_BR.properties
BOOK_NOT_AVAILABLE      = Livro {0} sem estoque (pediu {1}, disponível {2}).
ORDER_LIMIT_EXCEEDED    = Total do pedido {0} excede o limite por cliente ({1}).
INVALID_DISCOUNT_CODE   = "{0}" não é um código de desconto válido.
```

### Calling from a handler

CAP's `req.error(...)` / `req.reject(...)` signatures accept an i18n key in the
`code`/`message` slot. The framework resolves it against the user's `Accept-Language`:

```js
// srv/cat-service.js
this.on('submitOrder', async req => {
  const { bookID, qty } = req.data;
  const book = await SELECT.one.from(Books).where({ ID: bookID });

  if (!book) {
    return req.reject({
      code: 'BOOK_NOT_AVAILABLE',
      target: 'bookID',
      status: 404,
      args: [bookID, qty, 0]
    });
  }

  if (book.stock < qty) {
    return req.reject({
      code: 'BOOK_NOT_AVAILABLE',
      target: 'bookID',
      status: 409,
      args: [bookID, qty, book.stock]
    });
  }
});
```

The `args` array fills numbered placeholders (`{0}`, `{1}`, `{2}`) in the resolved
message. `code` is the i18n key. `target` is the CDS path the error refers to (Fiori
uses it to highlight the field). `status` is the HTTP code (defaults: `error` → 500,
`reject` → 400).

> Capire (verbatim): "If `code` is given, and a string, it is used to look up a
> user-readable error `message` from the `i18n/messages` bundles."

If only `message` is provided (no `code`), CAP **uses the message string itself
as the i18n key**, and the original string ends up as the `code` field in the
response. Prefer the explicit `code` form — it's easier to evolve a message
text without changing the lookup key.

### Built-in keys CAP raises automatically

These are emitted by the generic providers when a declarative rule fails. The
skill should NOT re-implement them in a handler — adding the annotation is enough.
Override the message text by setting the same key in `messages.properties`:

| Annotation / situation | i18n key |
|---|---|
| `@mandatory` | `ASSERT_MANDATORY` (falls back to `ASSERT_NOT_NULL`) |
| `@assert.range: [min, max]` | `ASSERT_RANGE` |
| `@assert.range` on an enum element | `ASSERT_ENUM` |
| `@assert.format: '<regex>'` | `ASSERT_FORMAT` |
| `@assert.target` (referential integrity) | `ASSERT_TARGET` |
| Several validation errors collected at once | `MULTIPLE_ERRORS` |

Example override:

```properties
# i18n/messages_pt_BR.properties
ASSERT_MANDATORY = O campo {0} é obrigatório.
ASSERT_RANGE     = {0} fora do intervalo permitido (entre {1} e {2}).
ASSERT_FORMAT    = "{0}" não corresponde ao formato esperado.
```

CAP picks the override automatically — no handler change required.

### Decision order (where this fits in domain-first)

1. **Annotation** — if the error is `@mandatory` / `@assert.*`, just add the
   annotation. The built-in key handles the rest.
2. **Custom code in `messages.properties` + `req.reject({ code, args })`** —
   when the error is genuinely application-specific (business rule, multi-row
   invariant). NEVER inline the user-facing English string into the handler;
   always go through the bundle.
3. **Hardcoded English string in `req.error('English text')`** — forbidden in
   user-facing flows. Acceptable only in internal background jobs where there
   is no UI consumer.

### Anti-patterns

- `req.reject(400, 'Title is required')` — hard-codes English, breaks i18n.
  Use `req.reject({ code: 'TITLE_REQUIRED' })` or, better, `title : String @mandatory`.
- Duplicating built-in keys (`MY_NOT_NULL = ...`) when overriding `ASSERT_NOT_NULL`
  would do.
- Sticking message text in the UI bundle (`i18n.properties`) instead of the
  message bundle — CAP only looks in `messages*.properties` for `req.*` lookups.
- Stuffing structured data into the message text (`"User 42 (admin@…) failed"`) —
  use `args` and let the translator place `{0}` / `{1}`.

---

## Localized Data

### Declaration

Mark fields that need translations:

```cds
entity Books {
  key ID : UUID;
  title  : localized String(111);
  descr  : localized String(1111);
  stock  : Integer;  // Not localized
}
```

### Auto-Generated Entities

The compiler generates:

**1. Texts Entity:**
```cds
entity Books.texts {
  key locale : sap.common.Locale;  // e.g., 'en', 'de'
  key ID : UUID;
  title : String(111);
  descr : String(1111);
}
```

**2. Association to Localized:**
```cds
entity Books {
  // ... original fields
  texts : Composition of many Books.texts on texts.ID = ID;
  localized : Association to Books.texts on localized.ID = ID
              and localized.locale = $user.locale;
}
```

**3. Localized View:**
```cds
entity localized.Books as select from Books {
  *,
  coalesce(localized.title, title) as title,
  coalesce(localized.descr, descr) as descr
};
```

### Reading Localized Data

```js
// Returns data in user's locale (with fallback)
await SELECT.from('Books');

// Access all translations
await SELECT.from('Books').columns('*', { texts: ['*'] });

// Specific locale
await SELECT.from('Books.texts').where({ locale: 'de' });
```

### Writing Localized Data

```js
// Deep insert with translations
await INSERT.into('Books').entries({
  ID: 'book-1',
  title: 'Default Title',
  descr: 'Default Description',
  texts: [
    { locale: 'de', title: 'Deutscher Titel', descr: 'Deutsche Beschreibung' },
    { locale: 'fr', title: 'Titre Français', descr: 'Description Française' }
  ]
});

// Update specific translation
await UPDATE('Books.texts')
  .set({ title: 'Neuer Titel' })
  .where({ ID: bookId, locale: 'de' });
```

### Initial Data (CSV)

**Books.csv (default language):**
```csv
ID;title;descr;stock
book-1;Wuthering Heights;A classic novel;100
```

**Books_texts.csv (translations):**
```csv
ID;locale;title;descr
book-1;de;Sturmhöhe;Ein klassischer Roman
book-1;fr;Les Hauts de Hurlevent;Un roman classique
```

---

## Temporal Data

### Declaration

**Using Annotations:**
```cds
entity WorkAssignments {
  key ID : UUID;
  employee : Association to Employees;
  role : String(100);
  validFrom : Date @cds.valid.from;
  validTo : Date @cds.valid.to;
}
```

**Using Temporal Aspect:**
```cds
using { temporal } from '@sap/cds/common';

entity WorkAssignments : temporal {
  key ID : UUID;
  employee : Association to Employees;
  role : String(100);
}
// Adds validFrom : Timestamp and validTo : Timestamp
```

### Time Slice Keys

Primary key becomes: `(ID, validFrom)`

```cds
// Exposed as single key in OData
entity WorkAssignments {
  key ID : UUID;
  // validFrom is implicitly part of the key
}
```

### Reading Temporal Data

**Current Data (as of now):**
```http
GET /WorkAssignments
```

**Time-Travel Query (historical snapshot):**
```http
GET /WorkAssignments?sap-valid-at=date'2022-01-01'
```

**Time-Period Query (history since date):**
```http
GET /WorkAssignments?sap-valid-from=date'2020-01-01'
```

### Programmatic Access

```js
// Current time slices
await SELECT.from('WorkAssignments');

// Specific date
cds.context = { timestamp: new Date('2022-01-01') };
await SELECT.from('WorkAssignments');

// All time slices
await SELECT.from('WorkAssignments')
  .columns('*')
  .where`ID = ${id}`;
```

### Writing Temporal Data

Temporal writes require custom handlers:

```js
// Create new time slice
await INSERT.into('WorkAssignments').entries({
  ID: 'wa-1',
  employee_ID: 'emp-1',
  role: 'Developer',
  validFrom: '2023-01-01',
  validTo: '9999-12-31'
});

// End current slice and start new one
this.on('UPDATE', 'WorkAssignments', async (req) => {
  const { ID } = req.params[0];
  const today = new Date().toISOString().split('T')[0];

  // End current slice
  await UPDATE('WorkAssignments')
    .set({ validTo: today })
    .where({ ID, validTo: '9999-12-31' });

  // Create new slice
  await INSERT.into('WorkAssignments').entries({
    ID,
    ...req.data,
    validFrom: today,
    validTo: '9999-12-31'
  });
});
```

### Temporal Aspect Definition

```cds
// From @sap/cds/common
aspect temporal {
  validFrom : Timestamp @cds.valid.from;
  validTo   : Timestamp @cds.valid.to;
}
```

### Limitations

- SQLite doesn't support `sap-valid-at` queries (no session context)
- Temporal writes require custom implementation
- Transitive temporal queries may produce redundant results
