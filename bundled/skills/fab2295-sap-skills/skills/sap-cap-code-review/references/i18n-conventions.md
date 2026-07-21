# i18n / message externalization (Medium)

Anchored in capire — Localization & i18n: https://cap.cloud.sap/docs/guides/i18n and https://cap.cloud.sap/docs/node.js/best-practices#use-i18n-keys-for-error-messages

Every user-facing text emitted by a CAP service handler — error messages, validation messages, status descriptions, log lines that surface to clients — must be looked up via i18n keys, not hardcoded literals. Keys live in `_i18n/messages.properties` (default locale) and `_i18n/messages_<locale>.properties` (translations).

If a finding doesn't match a Rule ID below, do not classify it as Medium/i18n.

---

## I18N-001 — Hardcoded literal in `req.error`

**Trigger.** Any of:
- `req.error(<code>, '<literal string>')`
- `req.error(<code>, "<literal string>")`
- `req.error(<code>, \`...\`)` (template literal containing **only** static text — no `${}` interpolation)

…where the second argument is a non-key literal. A "key" matches `^[A-Z_][A-Z0-9_]*$` (e.g. `BOOK_NOT_FOUND`) or starts with `{i18n>` for binding form.

**Reference.** capire — *"Use i18n keys for error messages so the client gets the message in the request's locale; the framework looks them up via `cds.i18n.messages`."*

**Why.** Hardcoded English strings ship as the only user-visible text regardless of the caller's locale. Users in other locales receive untranslated technical strings. Also, the same message gets duplicated across handlers and drifts.

**Suggested fix anchor.** Move the literal to `_i18n/messages.properties` and call `req.error(<code>, 'BOOK_NOT_FOUND', [...args])`. CAP's runtime resolves the key against `cds.context.locale` and interpolates positional args.

```properties
# _i18n/messages.properties
BOOK_NOT_FOUND = Book {0} not found.
```

```js
req.error(404, 'BOOK_NOT_FOUND', [bookId])
```

---

## I18N-002 — Hardcoded literal in `req.reject`

**Trigger.** Same as I18N-001 but with `req.reject(<code>, '<literal>')`.

**Reference.** capire — same as I18N-001. `req.reject` is the synchronous-error variant of `req.error`; both go through the same i18n resolver.

**Why.** Identical to I18N-001.

---

## I18N-003 — Hardcoded literal in `throw new Error(...)` from a handler

**Trigger.** Inside an event handler (`this.on/before/after/with(...)`), `throw new Error('<literal>')` or `throw new <Subclass>('<literal>')` where the message is a non-key literal that will be returned to the client.

**Reference.** capire — *"Errors thrown inside handlers are caught by the dispatcher and translated to OData errors; the message is sent to the client. Use i18n keys instead of raw text."*

**Why.** The thrown message is surfaced to the OData consumer in the response body. Same translation problem as `req.error`.

**Suggested fix anchor.** Prefer `req.error(code, 'KEY', [args])` over `throw`. If `throw` is structurally required, use `throw Object.assign(new Error('KEY'), { code, args })` and rely on the dispatcher's i18n resolution.

---

## I18N-004 — Hardcoded literal in `@assert.*` annotation arguments

**Trigger.** A CDS annotation like `@assert.range: [..., 'Out of range']` or `@assert.format: ['^\\d+$', 'Must be digits']` where the message argument is a literal English string instead of a key.

**Reference.** capire — *"Validation messages can be externalized via i18n keys, e.g. `@assert.range: [0, 100, 'OUT_OF_RANGE']`"*.

**Why.** Validation errors return to the client; localization applies to them too.

**Suggested fix anchor.** Replace the literal with an UPPER_SNAKE key and add the entry to `_i18n/messages.properties`.

---

## I18N-005 — Same literal duplicated across handlers (drift risk)

**Trigger.** The exact same string literal (≥ 4 words or ≥ 30 chars) appearing in `req.error`/`req.reject`/`throw` in two or more files of the changed scope.

**Reference.** capire — *"i18n keys deduplicate user-facing copy and prevent drift between similar handlers."*

**Why.** Without a single source of truth, fixes to wording diverge over time and translations drift between two near-identical strings.

**Suggested fix anchor.** Extract once to `_i18n/messages.properties` and reference by key from every callsite.

---

## I18N-006 — Hardcoded literal in CDS `@title` / `@description` / `@Common.Label`

**Trigger.** `@title: 'Some text'`, `@description: 'Some text'`, `@Common.Label: 'Some text'`, `@UI.LineItem: [{ Label: 'Some text', ... }]` where the value is a literal string instead of a `{i18n>KEY}` binding.

**Reference.** capire — *"For Fiori UI labels, use `{i18n>KEY}` bindings so labels translate per session locale."*

**Why.** Fiori UIs render the literal as-is in every locale; translations are silently dropped.

**Suggested fix anchor.** Replace with `{i18n>KEY}` and add the key under the appropriate `_i18n/i18n.properties` (UI namespace).

---

## What this section is NOT

- It does NOT validate that the i18n key actually exists in `_i18n/messages.properties` — that's a build-time check; flag missing entries via `cds build` warnings instead.
- It does NOT flag `console.log` / `cds.log(...)` lines (those are operator-facing, not user-facing).
- It does NOT flag OData metadata strings (`@Common.Description` for technical docs that target API consumers, not end users).
- Internal-only error messages (errors caught and re-thrown without reaching the client) are out of scope.

## When in doubt — do not flag

If you cannot determine whether a literal will reach the end user (e.g. it is thrown deep in a util that may be caught further up), prefer to NOT flag. The rubric's anti-rubric forbids invented severities. Comment in the report's "Considered but not flagged" appendix only if the user opts in.
