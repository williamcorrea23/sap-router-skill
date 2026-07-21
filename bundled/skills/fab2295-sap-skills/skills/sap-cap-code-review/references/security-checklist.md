# Security checklist (Critical)

Anchored in capire — Security & Data Privacy: https://cap.cloud.sap/docs/guides/security/ and https://cap.cloud.sap/docs/guides/data-privacy/

Every rule below carries:
- A **Rule ID** (e.g. `SEC-001`)
- A **Trigger** — what the analyzer must detect
- A **Reference** — the capire principle the rule derives from
- A **Why** — the threat model

If a finding doesn't match a Rule ID below, do not classify it as Critical/Security.

---

## SEC-001 — Raw SQL with user-controlled values

**Trigger.** Any of these patterns where the value substituted into the SQL string comes from `req.data.*`, `req.params.*`, `req.query.*`, an HTTP header, or any function argument that flows from a service handler:
- `cds.run('... ' + variable + ' ...')`
- `cds.run(\`... ${variable} ...\`)` (regular template literal — NOT the tagged variant)
- `db.run(\`... ${variable} ...\`)`
- string concatenation feeding `.where(...)` as a raw string

**Reference.** capire — *"Best Practices › Don't bypass CAP's query API with raw SQL"* and *CQL automatically protects against SQL injection when using parameterized queries or tagged template literals*.

**Why.** Direct concatenation lets an attacker inject SQL via OData inputs. CAP's CQN/parameterized API is injection-safe by construction; raw SQL with `${}` interpolation is not.

**Suggested fix anchor.** Replace with parameterized CQN: `SELECT.from(Books).where({ author_ID: authorId })` or with a tagged template: `SELECT.from(Books).where\`author_ID = ${authorId}\``.

---

## SEC-002 — Service or entity exposed without authorization

**Trigger.** A `service X { ... }` block in `srv/*.cds` whose definition has no `@requires` and contains entities or actions, AND there is no project-wide auth in `package.json` (`cds.requires.auth.kind === 'dummy'` or missing).

Also flag: `entity Y` declared inside a service without entity-level `@restrict` AND no service-level `@requires`.

**Reference.** capire — *"By default, all services are public. Use @requires for service-level auth and @restrict for fine-grained control."*

**Why.** A service without `@requires` and an entity without `@restrict` is reachable by anonymous users in any non-mocked deployment.

**Suggested fix anchor.** Add `@requires: 'authenticated-user'` (or a real role) to the service, and `@restrict: [...]` for per-action/per-row rules.

---

## SEC-003 — Mock auth in production-bound config

**Trigger.** `cds.requires.auth.kind === 'mocked'` or `'dummy'` in `package.json` under a profile that is not strictly `[development]` (i.e. it appears in the default config or under `[production]`/`[hybrid]`).

**Reference.** capire — *"Mocked authentication is for local development only."*

**Why.** Ships a dev-only auth strategy to production: every request bypasses identity checks.

**Suggested fix anchor.** Move `mocked` under `"[development]"` and configure `xsuaa` / `ias` / `jwt` for production profiles.

---

## SEC-004 — Authorization decided in handler code instead of model

**Trigger.** An `if (req.user.id ...)`, `if (req.user.is(...))`, `if (req.user.attr.tenant ...)` check inside a handler that conditionally returns data or rejects the request, where the same access policy could be expressed declaratively via `@restrict where: ...` or `@requires`.

**Reference.** capire — *"Prefer declarative @restrict over imperative checks: declarative rules are enforced before queries hit the DB and are visible to tooling."*

**Why.** Handler-side checks are easy to forget on new endpoints, are not introspectable by tooling, and run AFTER the query (so denied rows still cost the DB roundtrip).

**Suggested fix anchor.** Move the rule to `@restrict: [{ grant: '...', where: 'buyer_ID = $user' }]` on the entity or service.

---

## SEC-005 — User input flowed into shell, fs, or external HTTP without validation

**Trigger.** `req.data.X` (or any value derived from a request) reaching:
- `child_process.exec`, `execSync`, `spawn` first arg as a string
- `fs.readFile`, `fs.writeFile`, `fs.unlink`, `path.resolve` with the value as a path component, without an explicit allowlist or `path.basename(...)` first
- `fetch`, `axios`, `cds.connect.to('...').send(...)` URL or path with raw concatenation

**Reference.** capire — *"Input Validation"* + general OWASP A03/A10. Capire references the `@assert.format`, `@assert.range`, and `@mandatory` annotations as the model-level validation layer.

**Why.** Command injection, path traversal, SSRF.

**Suggested fix anchor.** Validate at the model layer (`@assert.format`, `@assert.range`, `@assert.notNull`); for filesystem paths use `path.basename()` + an allowlist; for shell commands, use `spawn(cmd, [args])` (array form).

---

## SEC-006 — CSRF disabled or weak CORS in production

**Trigger.** In `package.json` or `cds-plugin` config:
- `cds.server.csrf` set to `false` under any profile other than `[development]`
- `cds.server.cors.origin = '*'` under any profile other than `[development]`
- An express `app.use(cors())` call without an allowlist

**Reference.** capire — *"Security › CORS and CSRF defaults: enabled for OData requests by default; loosen only with intent."*

**Why.** Cross-origin attackers can trigger authenticated state-changing requests from a victim browser.

**Suggested fix anchor.** Set explicit `cors.origin: ['https://app.example.com']` and keep `csrf: true` for protected profiles.

---

## SEC-007 — Secrets / credentials inlined in source

**Trigger.** Any of these patterns in `srv/`, `db/`, `app/`, `package.json`, `.cdsrc.json`, `mta.yaml`, `xs-security.json`:
- `apiKey: '<non-empty literal>'`
- `password: '<literal>'`
- `clientSecret: '<literal>'`
- A token-shaped literal: `eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}` (JWT)
- A 40-char hex literal under `secret`, `token`, `key` (likely API key)

**Reference.** capire — *"Don't hardcode credentials in config files. Use service bindings (`cds.requires.<service>.credentials`) or environment variables."*

**Why.** Secret in git history is forever; a single leaked commit becomes a breach.

**Suggested fix anchor.** Move to `cds.env`, `process.env`, or a CF/Kyma service binding referenced via `cds.requires.<X>.binding`.

**Evidence redaction (mandatory).** SEC-007's whole purpose is to flag the presence of an inlined secret. The Evidence block MUST NOT include the secret value — not even partially. Use the fixed format from `secret-redaction.md` §"Trigger D":

```
<key-or-variable-name>: [REDACTED:found-secret]
```

The `Location` field (`<file>:<line>`) is what allows the human to navigate to the original. The report itself MUST be safe to share.

---

## SEC-008 — Personal data without `@PersonalData` annotation

**Trigger.** An entity field with type `String` named like `email`, `phone`, `taxId`, `ssn`, `dateOfBirth`, `address*`, `firstName`, `lastName`, `fullName`, `iban`, `creditCard*`, AND the containing entity has no `@PersonalData.EntitySemantics` annotation, AND the field has no `@PersonalData.FieldSemantics` annotation.

**Reference.** capire — *"Data Privacy › Annotate personal data so the audit-log plugin and data subject right requests can find it."*

**Why.** GDPR / LGPD obligations (right to be forgotten, audit trail). Unannotated personal data won't appear in subject access exports and won't be redacted on deletion.

**Suggested fix anchor.** Add `@PersonalData.EntitySemantics: 'DataSubject'` (or `DataSubjectDetails`) on the entity and `@PersonalData.FieldSemantics: 'DataSubjectID'` on key fields. Also enable `@cap-js/audit-logging`.

---

## SEC-009 — Disabled SSL / certificate verification in remote service config

**Trigger.** In `package.json` `cds.requires.<remoteService>` or in a manual `axios`/`fetch` call:
- `rejectUnauthorized: false`
- `strictSSL: false`
- `NODE_TLS_REJECT_UNAUTHORIZED=0` set in code

**Reference.** capire — *"Consuming Services › TLS verification is on by default. Disabling it is only acceptable in local mocks."*

**Why.** Trivial MITM in any non-loopback environment.

**Suggested fix anchor.** Remove the flag; if a self-signed cert is intentionally used in dev, restrict the override to `[development]` profile.

---

## SEC-010 — `req.user` checked but never enforced (audit-only auth)

**Trigger.** A service handler that reads `req.user.id` or `req.user.is(...)` for *logging* but does not branch on the result, on an entity that has no `@restrict`. Pattern: `console.log(req.user.id); ... return <data>` with no role gate.

**Reference.** capire — *"Authentication is not authorization. Identifying the caller without restricting their actions is not security."*

**Why.** Gives a false sense of safety; the endpoint remains open.

**Suggested fix anchor.** Either add `@requires`/`@restrict` at the model layer, or add an explicit `if (!req.user.is('Role')) return req.reject(403)` in the handler.

---

## SEC-011 — `cds.context.user.attr` used without origin check

**Trigger.** `req.user.attr.<X>` or `cds.context.user.attr.<X>` accessed and used in a SQL `where` clause, without verifying that the attribute was set by a trusted IDP.

**Reference.** capire — *"User attributes propagate from the identity provider's claims; ensure the IDP is configured to pass only attributes you trust."*

**Why.** A misconfigured IDP can let users inject arbitrary attributes that bypass row-level filtering.

**Suggested fix anchor.** Pin attributes to known IDP keys via `xs-security.json` `attributes`, and avoid using attributes that aren't whitelisted there.

---

## What this section is NOT

- It is not a substitute for a real SAST. It catches SAP-CAP-shaped issues anchored in capire. For OWASP-wide coverage, run `npm audit`, `osv-scanner`, or a dedicated SAST.
- It does NOT review `npm audit` advisories. Those are out of scope.
- It does NOT analyze TLS cipher suites, JWT validation logic of `@sap/xssec`, or KMS key rotation. Those live below the CAP layer.
