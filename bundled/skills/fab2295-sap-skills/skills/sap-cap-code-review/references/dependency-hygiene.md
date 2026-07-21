# Dependency hygiene (High)

Anchored in capire — *"Don't bypass CAP's APIs"* (https://cap.cloud.sap/docs/about/best-practices) and the public Node.js facade exposed by `@sap/cds` and `@cap-js/*`.

This file defines two related rules:
- Stay on the **public** surface of `@sap/cds` and CAP plugins. Do not consume deprecated, private, or internal symbols.
- Stay on the **CAP / Node native / @cap-js** stack. Don't pull external libraries to do something CAP or Node already does.

If a finding doesn't match a Rule ID below, do not classify it as High/DependencyHygiene.

---

## DEP-001 — Import from `@sap/cds`'s internal/private path

**Trigger.** A `require(...)` or `import` whose specifier reaches **below** the public facade of `@sap/cds`. Examples flagged:
- `require('@sap/cds/lib/...')`
- `require('@sap/cds/libx/...')`
- `require('@sap/cds/dist/...')`
- `import ... from '@sap/cds/lib/...'`

The public surface is the package root: `require('@sap/cds')` and the documented submodules listed in capire (`@sap/cds/lib/index.js` is internal).

**Reference.** capire — *"Use the public `cds` facade. Anything under `@sap/cds/lib/...` or `@sap/cds/libx/...` is private and changes between minor releases without notice. eslint-plugin-cds rule `no-deep-sap-cds-import` enforces this since v4."*

**Why.** Private internals get renamed/moved/deleted in minor releases. Code that imports them breaks silently on every CAP upgrade.

**Suggested fix anchor.** Use the public API: `const cds = require('@sap/cds')` and access `cds.entities`, `cds.connect.to`, `cds.context`, etc. If you can't find the symbol on the public facade, the use case might be wrong — discuss with a CAP maintainer or open a feature request.

---

## DEP-002 — Use of a documented-deprecated CAP API

**Trigger.** Any of these patterns (each is documented as deprecated in capire's release notes):
- `cds.outboxed(srv)` / `cds.unboxed(srv)` — replaced by `cds.queued(srv)` / `cds.unqueued(srv)` (cds@9.0)
- `CDL`, `CQL`, `CXL` global helpers — replaced by `cds.ql.*` (cds@8.6)
- `CREATE`, `DROP` globals — replaced by `cds.ql.CREATE` / `cds.ql.DROP` (cds@8.6)
- `req.diff()` reading individual children sequentially — superseded behavior change (cds@9.0; behavior, not API rename)
- `cds.User.tokenInfo` — replaced by `cds.context.user.authInfo.token` (cds@9.3)
- `cds.context.http.req.authInfo` — replaced by `cds.context.user.authInfo` (cds@9.3)
- `express.Request.user`, `express.Request.tenant` — never public; use `cds.context.user/tenant`

**Reference.** capire release notes — each entry above is anchored in the corresponding monthly changelog entry. If a project uses `sap-cap-upgrade`'s changelog mirror (`~/.claude/skills/sap-cap-upgrade/references/changelogs/cap/`), cite the exact line.

**Why.** Deprecated APIs get a deprecation warning today and a removal next major. Code on a deprecated API ages into a breaking change.

**Suggested fix anchor.** Replace 1:1 with the documented successor; do not silence the deprecation warning.

---

## DEP-003 — Reaching into a CAP plugin's private exports

**Trigger.** A `require('@cap-js/<plugin>/internal/...')` or `require('@cap-js/<plugin>/lib/...')` (anything other than the package root).

**Reference.** capire / `@cap-js/*` README files — *"Each `@cap-js/*` plugin documents only the package root as public API. Subpaths are subject to change."*

**Why.** Same as DEP-001 but for plugins.

**Suggested fix anchor.** Use the plugin's public API; if missing, file an issue at the plugin's repo and stay on the public surface in the meantime.

---

## DEP-004 — Calling a `_` -prefixed or `#` private member of a CAP class

**Trigger.** Code that accesses `cds.<X>._<priv>`, `srv._<priv>`, or any class field starting with `_` (the CAP-Node convention for private), where `<X>` is from `@sap/cds` or `@cap-js/*`.

**Reference.** capire — convention; the JS-side facade does not use TypeScript `private`/`protected` keywords, so the underscore prefix marks "do not consume from outside the package."

**Why.** Private members can be removed, renamed, or change semantics in any release. Production breaks silently after `npm ci`.

**Suggested fix anchor.** Use the documented public method/property. If none exists, open a feature request.

---

## DEP-005 — External library duplicating a CAP / Node-native capability

**Trigger.** A `dependencies` entry in `package.json` that is one of these (and the project uses it from `srv/`/`db/`):

| External lib | Native / CAP replacement |
|---|---|
| `lodash` (full) | Native: `Array.prototype.*`, `Object.fromEntries`, `structuredClone`, `Map`, `Set`. Most lodash helpers have direct replacements. |
| `axios`, `node-fetch`, `got` | `cds.connect.to('remote-service').send(...)`; for ad-hoc HTTP, Node 18+ ships `globalThis.fetch`. |
| `uuid` (or `nanoid`) | `cds.utils.uuid()` |
| `moment`, `dayjs` (when only formatting/parsing ISO) | Native: `Date`, `Intl.DateTimeFormat`. CAP types map Timestamp ↔ ISO string. |
| `dotenv` | CAP reads `process.env` and `default-env.json` natively via `cds.env`. |
| `joi`, `zod`, `ajv` (for API input validation) | CDS annotations: `@assert.format`, `@assert.range`, `@mandatory`, `@assert.notNull`, `cds.validate()`. |
| `bcrypt`, `crypto-js` (for non-password hashing) | Node `node:crypto` (native). |
| `winston`, `pino` (for app logs) | `cds.log('namespace')` (CAP's logger wraps the chosen sink). |
| `mocha` / `jest` (for new test setup, when project already uses cds-test/mocha) | Stay on the project's chosen runner; don't add a parallel one. |

The rule fires only if the external lib is **referenced from production code** under `srv/` or `db/` (test files using mocha/jest are fine).

**Reference.** capire — *"Best Practices › Prefer CAP native facilities over generic alternatives."*

**Why.** External libs add: bundle size, supply-chain attack surface, version-skew risk on CAP upgrades, and onboarding friction. CAP/Node already cover the use case.

**Suggested fix anchor.** Replace with the native/CAP equivalent shown in the table. If you have a use case that genuinely needs the external lib (e.g. lodash's `debounce` outside a request path), document it inline.

---

## DEP-006 — Adding a new direct dependency without rationale

**Trigger.** A `package.json` change in this PR adds a new entry under `dependencies` (not `devDependencies`), AND there is no commit message line, code comment, or PR description that justifies it.

**Reference.** capire / general — *"Each direct dependency is a long-lived commitment; add only if clearly justified and reviewed."*

**Why.** Dependencies grow silently and never shrink. Each one is a future maintenance + security cost.

**Suggested fix anchor.** Either remove it (if not actually needed), move it to `devDependencies` (if dev-only), or add a comment explaining why this lib is needed and what was tried first.

---

## DEP-007 — `eval`, `new Function`, dynamic `require`

**Trigger.**
- `eval(...)` anywhere
- `new Function(...)` anywhere
- `require(<dynamic expression>)` (i.e., the argument is not a string literal) inside a handler

**Reference.** capire — general; capire's *"Don't write custom OData providers"* and *"Stay on documented APIs"* implicitly outlaw dynamic code execution as an extension mechanism.

**Why.** Code injection surface, opaque to static analysis, defeats every other security/perf/lint check, blows up with bundlers.

**Suggested fix anchor.** Use static `require(...)` at top of file; for dynamic dispatch use a `Map` of strategies, or move dynamic logic to configuration.

---

## What this section is NOT

- It does NOT block adding `@cap-js/*` plugins, `@sap/cds-*` add-ons, or new `@sap-cloud-sdk/*` packages — those are in-scope CAP ecosystem deps.
- It does NOT flag transitive deps. The rule is on direct deps in *this* `package.json`.
- It does NOT enforce a ban on a specific lib globally. The list above is curated to "duplicates CAP native"; libs not on the list are out of scope for this rule.
- It does NOT validate semver ranges. Use `sap-cap-upgrade` for version-bump analysis.
