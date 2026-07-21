---
name: sap-cap-nodejs-dev
description: |
  SAP Cloud Application Programming Model (CAP) development skill for the **Node.js runtime only**.
  Domain-first: prefers CDS schema, annotations, projections, and CAP's generic providers over
  hand-written handler code ("less code → less mistakes").

  Use when the user asks to: build CAP applications, define CDS models, design entities /
  associations / views / projections, add annotations (validation, authorization, UI, search,
  drafts), configure databases (SQLite / HANA / PostgreSQL through CAP), deploy to SAP BTP
  (Cloud Foundry or Kyma), wire multitenancy / messaging, or add CAP plugins.

  Strict scope — this skill ONLY develops SAP CAP Node.js. It MUST refuse, and tell the user why,
  whenever a request is:
  - Frontend / UI implementation (Fiori Elements custom code, UI5 controls, React, Vue, HTML/CSS/JS
    UI work, any browser-side code). CAP-side `@UI.*` annotations in `.cds` are in scope; writing
    the UI itself is not.
  - Backend in any other language or stack (Java CAP, Spring, plain Node/Express, NestJS, Python,
    Go, .NET, serverless functions outside CAP, microservices not built on `@sap/cds`).
  - Any non-CAP architecture (custom OData providers, hand-rolled REST frameworks, ad-hoc
    GraphQL servers that don't go through `@cap-js/graphql`).

  Public-API hygiene — this skill only uses **public, supported, non-deprecated** CAP interfaces:
  - Public: anything documented at https://cap.cloud.sap/docs/ for the current `@sap/cds` major.
  - Forbidden: internal modules (paths like `@sap/cds/lib/...`, `_private`, `__internal`),
    `@protected` / `@internal` / `@experimental` APIs, anything marked deprecated or removed in
    the changelog. Always prefer the documented public interface; if no public API exists, say so
    and stop — do not reach into internals.
license: GPL-3.0
metadata:
  version: "3.2.0"
  last_verified: "2026-05-13"
  runtime: "Node.js only"
  cap_version: "@sap/cds 9.7.x"
  mcp_version: "@cap-js/mcp-server 0.0.3+"
  lsp_version: "@sap/cds-lsp 9.7.x"
---

# SAP CAP Node.js Development Skill

## 1. Scope guardrails (read first, every time)

Before doing anything, classify the request:

1. **CAP Node.js development?** → proceed.
2. **UI / frontend work?** → refuse: "This skill is SAP CAP Node.js only. UI/frontend
   implementation (Fiori custom code, UI5, React, Vue, plain HTML/CSS/JS) is out of scope.
   CAP-side UI *annotations* in `.cds` are in scope; the UI app itself is not."
3. **Backend in another language or stack?** → refuse: "This skill is SAP CAP Node.js only.
   Java CAP, Spring, plain Node/Express, NestJS, Python, Go, .NET, and non-CAP microservices
   are out of scope."
4. **Non-CAP architecture (custom OData/REST/GraphQL outside CAP)?** → refuse with the same
   message. CAP must be the framework (`@sap/cds` + `cds.ApplicationService`, or documented
   `@cap-js/*` plugins).
5. **Uses a private / protected / deprecated API?** → refuse and propose the documented public
   alternative. If none exists, say so and stop.

When in doubt, ask the user to confirm the request fits the CAP Node.js scope before writing code.

## 2. Public-API rule

- Only import from documented, stable entry points: `@sap/cds`, `@sap/cds/common`,
  `@cap-js/sqlite`, `@cap-js/hana`, `@cap-js/postgres`, `@cap-js/attachments`,
  `@cap-js/audit-logging`, `@cap-js/change-tracking`, `@cap-js/telemetry`, `@cap-js/graphql`,
  `@cap-js/mcp-server`, `@sap/cds-mtxs`.
- Never reach into `@sap/cds/lib/*`, `node_modules/@sap/cds/lib/*`, or any path the docs do not
  describe.
- Never use methods/options that the changelog flags as **deprecated** or **removed**.
- Never rely on undocumented behavior of a documented API ("it happens to work today").
- If the public surface cannot do what the user wants, say so — do not fall back to internals.

## 3. Domain-first / Less code → Less mistakes

> "Every line of code not written is free of errors." — SAP Capire
> https://cap.cloud.sap/docs/get-started/features#less-code-%E2%86%92-less-mistakes

CAP captures **domain knowledge and intent declaratively** ("What, not How"). This skill
follows that principle: prefer the CDS model, annotations, projections, and CAP's generic
providers over hand-written handlers and SQL.

**CAP's generic providers already handle**: CRUD, nested documents, drafts, media, search,
pagination, sorting, authentication / authorization, localization, input validation,
auto-generated keys, concurrency control. **Do not re-implement these in code.**

**Decision order** when adding a new behavior — only drop to the next step if the previous one
cannot express it:

1. **Schema** — types, associations, compositions, aspects from `@sap/cds/common`.
2. **Annotations** — `@mandatory`, `@assert.*`, `@readonly`, `@insertonly`, `@requires`,
   `@restrict`, `@cds.persistence.*`, `@cds.search`, `@odata.draft.enabled`, `@odata.etag`,
   `@UI.*`.
3. **Views / projections** — expose subsets, filter rows, compute fields, join entities in CDS.
4. **Status Flows** — when the behavior is a state machine (row walks through named states),
   use `@flow.status` + `@from` + `@to`. CAP validates the entry state and writes the target
   state. See [references/status-flow.md](references/status-flow.md). ⚠ Currently Gamma in
   capire — only adopt with explicit team acceptance.
5. **CAP plugins** — `@cap-js/attachments`, `@cap-js/audit-logging`, `@cap-js/change-tracking`,
   `@cap-js/telemetry`, `@cap-js/graphql`, etc.
6. **Concurrency control** — `@odata.etag` (via `managed.modifiedAt`) for optimistic locking;
   `cds.tx(req)` with `.forUpdate()` on the base entity when invariants span multiple rows.
   See [references/concurrency-control.md](references/concurrency-control.md) and
   [references/race-conditions.md](references/race-conditions.md).
7. **Event handlers** (last resort) — only for behavior that is genuinely business logic and
   cannot be expressed declaratively by steps 1–6. Never re-implement what `@from`/`@to`,
   `@odata.etag`, `@assert.*`, `@requires`, or a projection already does for free.

Full explanation, examples, and the "is this PR domain-first?" checklist:
[references/domain-first.md](references/domain-first.md).

## 4. Where to put what

| Concern                              | Where it lives                                   |
|--------------------------------------|--------------------------------------------------|
| Keys, types, relationships           | `db/schema.cds`                                  |
| Required / range / format / unique   | CDS `@mandatory`, `@assert.*`                    |
| Computed fields                      | CDS calculated elements (`= expr`, `stored`)     |
| Exposed subset / filtered rows       | `srv/*.cds` projection                           |
| Joins across entities                | CDS view (`as select from … join …`)             |
| Authorization (who can do what)      | `@requires`, `@restrict`                         |
| Fiori UI shape                       | `@UI.*`, `@Common.*` annotations in CDS          |
| i18n texts                           | `_i18n/` `.properties` files                     |
| Seed / reference data                | CSV in `db/data/`                                |
| Cross-cutting concerns               | `@cap-js/*` plugin (configured, not coded)       |
| Genuine business logic               | Node.js event handler in `srv/*.js`              |

The `app/` folder (UI applications) is **out of scope** for this skill.

## 5. Project structure

```
project/
├── app/              # UI content                            ← out of scope
├── srv/              # Service definitions (.cds, .js/.ts)  ← in scope
├── db/               # Data models, views, seed data         ← in scope
│   ├── schema.cds
│   └── data/
├── package.json      # Dependencies + CDS config             ← in scope
└── .cdsrc.json       # CDS configuration (optional)
```

## 6. Quick start (minimal)

```sh
npm i -g @sap/cds-dk @sap/cds-lsp
cds init <project-name>
cds watch
```

Add capabilities as needed (`cds add hana | sqlite | xsuaa | mta | multitenancy | typescript`).
Full CLI reference: [references/cli-complete.md](references/cli-complete.md) and
[references/tools-complete.md](references/tools-complete.md).

**Domain-first starter** — model first, expose with a projection, no handler needed:

```cds
// db/schema.cds
using { cuid, managed } from '@sap/cds/common';
namespace my.bookshop;

entity Books : cuid, managed {
  title : String(111) @mandatory;
  stock : Integer     @assert.range: [0, 99999];
  price : Decimal(9,2);
}
```

```cds
// srv/catalog-service.cds
using { my.bookshop as my } from '../db/schema';

@requires: 'authenticated-user'
service CatalogService {
  @readonly entity Books as projection on my.Books where stock > 0;
}
```

That's a working, validated, authorized, searchable OData service — zero JS.

For more entity / projection / view / annotation patterns, see the templates folder and the
references below.

## 7. MCP integration

The skill integrates with the official CAP MCP server, giving the agent live access to the
project's compiled CSN model and CAP docs:

- `search_model` — fuzzy search entities, services, actions, and relationships in the CSN.
- `search_docs` — semantic search through CAP documentation.

Setup: [references/mcp-integration.md](references/mcp-integration.md).
Use cases: [references/mcp-use-cases.md](references/mcp-use-cases.md).

## 8. Bundled resources (index)

### Philosophy & rules
- [domain-first.md](references/domain-first.md) — "Less code → less mistakes", decision order,
  annotations and views to prefer over code, anti-patterns.
- [best-practices.md](references/best-practices.md) — full DO / DON'T, code smells, review
  checklist.
- [security-audit.md](references/security-audit.md) — audit matrix against the AI-agent /
  supply-chain attack surface (prompt injection, MCP poisoning, supply chain, eval,
  SSRF, credential leakage, etc.) and the standing rules the skill enforces on agent output.

### Language & query
- [cdl-syntax.md](references/cdl-syntax.md) — CDL syntax reference.
- [annotations-reference.md](references/annotations-reference.md) — annotations catalog.
- [cql-queries.md](references/cql-queries.md) — CQL basics.
- [cql-patterns.md](references/cql-patterns.md) — CQL usage patterns.
- [csn-cqn-cxn.md](references/csn-cqn-cxn.md) — Core Schema Notation and query APIs.
- [sql-injection.md](references/sql-injection.md) — why CAP's CQL prevents injection, when raw
  SQL is allowed, identifier allow-lists.

### State, concurrency & safety
- [status-flow.md](references/status-flow.md) — `@flow.status` + `@from` + `@to` for
  state-machine use cases (capire Gamma).
- [concurrency-control.md](references/concurrency-control.md) — `@odata.etag` optimistic
  locking, `.forUpdate()` pessimistic locking, draft serialization.
- [race-conditions.md](references/race-conditions.md) — TOCTOU, transactions, bootstrap
  races, event-consumer idempotency.

### Runtime & handlers (use sparingly — model first)
- [nodejs-runtime.md](references/nodejs-runtime.md) — Node.js runtime reference.
- [event-handlers-nodejs.md](references/event-handlers-nodejs.md) — handler patterns.
- [event-handlers-patterns.md](references/event-handlers-patterns.md) — extended patterns.
- [service-definitions.md](references/service-definitions.md) — service definition patterns.

### Persistence
- [databases.md](references/databases.md) — DB configuration.
- [data-privacy-security.md](references/data-privacy-security.md) — GDPR, security.
- [localization-temporal.md](references/localization-temporal.md) — i18n (UI bundle `i18n.properties` and **error-message bundle `messages.properties`** for `req.error` / `req.reject`, built-in keys `ASSERT_MANDATORY`, `ASSERT_RANGE`, `ASSERT_FORMAT`, `ASSERT_TARGET`, `MULTIPLE_ERRORS`), temporal data.

### Integration & deployment
- [consuming-services-deployment.md](references/consuming-services-deployment.md) — remote
  services, bindings, deployment.
- [deployment-cf.md](references/deployment-cf.md) — Cloud Foundry deployment details.
- [extensibility-multitenancy.md](references/extensibility-multitenancy.md) — SaaS / MTX.
- [plugins-reference.md](references/plugins-reference.md) — `@cap-js/*` plugins.
- [fiori-integration.md](references/fiori-integration.md) — CAP-side UI annotations only.

### Tooling
- [cli-complete.md](references/cli-complete.md) — `cds` CLI reference.
- [tools-complete.md](references/tools-complete.md) — full tooling overview.
- [mcp-integration.md](references/mcp-integration.md) — CAP MCP server.
- [mcp-use-cases.md](references/mcp-use-cases.md) — MCP scenarios.
- [CAP_Troubleshooting.md](references/CAP_Troubleshooting.md) — troubleshooting.

### Templates
- [templates/bookshop-schema.cds](templates/bookshop-schema.cds) — data model example.
- [templates/catalog-service.cds](templates/catalog-service.cds) — service definition.
- [templates/fiori-annotations.cds](templates/fiori-annotations.cds) — UI annotations (CDS only).
- [templates/mta.yaml](templates/mta.yaml) — MTA descriptor.
- [templates/package.json](templates/package.json) — project config.
- [templates/service-handler.js](templates/service-handler.js) — Node.js handler (use sparingly).
- [templates/service-handler.ts](templates/service-handler.ts) — TypeScript handler.
- [templates/xs-security.json](templates/xs-security.json) — XSUAA security config.

## 9. Quick links

- CAP Documentation: https://cap.cloud.sap/docs/
- CDS Language: https://cap.cloud.sap/docs/cds/
- Node.js Runtime: https://cap.cloud.sap/docs/node.js/
- Best Practices (official): https://cap.cloud.sap/docs/about/best-practices
- GitHub: https://github.com/cap-js/docs

## 10. Version

- Skill Version: 3.1.0
- Runtime: Node.js only
- CAP Version: @sap/cds 9.7.x
- MCP Version: @cap-js/mcp-server 0.0.3+
- LSP Version: @sap/cds-lsp 9.7.x
- Last Verified: 2026-05-12
- License: GPL-3.0
