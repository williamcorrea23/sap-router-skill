# sap-cap-nodejs-dev

A Claude Code skill for **SAP CAP development on the Node.js runtime, and nothing else.**

## What this skill does

Helps build CAP applications: CDS modeling, service definitions, Node.js event handlers, CQL,
database setup (SQLite / HANA / PostgreSQL via CAP), authorization, multitenancy, messaging,
CAP plugins, and BTP deployment (Cloud Foundry / Kyma) — all through the public, documented
CAP interfaces.

## What this skill does NOT do

The skill MUST refuse and tell the user why when the request falls into any of these buckets:

- **Frontend / UI implementation** — Fiori Elements custom code, UI5 controls, React, Vue, plain
  HTML/CSS/JS, any browser-side logic. (UI **annotations** inside `.cds` files are fine; the UI
  app itself is not.)
- **Backend in another language or stack** — Java CAP, Spring, plain Node/Express, NestJS,
  Python, Go, .NET, serverless functions outside CAP, microservices not built on `@sap/cds`.
- **Non-CAP architectures** — custom OData providers, hand-rolled REST frameworks, GraphQL
  servers that don't go through `@cap-js/graphql`.

## Public-API only

The skill is restricted to **public, supported, non-deprecated** CAP interfaces.

- **Allowed entry points**: `@sap/cds`, `@sap/cds/common`, `@cap-js/sqlite`, `@cap-js/hana`,
  `@cap-js/postgres`, `@cap-js/attachments`, `@cap-js/audit-logging`, `@cap-js/change-tracking`,
  `@cap-js/telemetry`, `@cap-js/graphql`, `@cap-js/mcp-server`, `@sap/cds-mtxs`.
- **Forbidden**: internal modules (`@sap/cds/lib/...`, `_private`, `__internal`),
  `@protected` / `@internal` / `@experimental` APIs, anything marked deprecated or removed in
  the changelog.
- If no public API exists for what the user wants, the skill says so and stops — it does not
  reach into internals.

## When to use this skill

- Creating CAP Node.js projects (`cds init`, structure, configuration)
- Defining data models in CDS (entities, types, associations, compositions)
- Implementing services (projections, actions, functions) in `.cds`
- Writing Node.js event handlers (before / on / after)
- Working with databases through CAP (SQLite for dev, HANA / PostgreSQL for prod)
- Adding CAP-side UI annotations to `.cds`
- Deploying via Cloud Foundry / Kyma / MTA
- Configuring authorization (`@requires`, `@restrict`, XSUAA)
- Enabling multitenancy (MTX, `@sap/cds-mtxs`)
- Using CAP messaging (`srv.emit`, file-based and Enterprise Messaging)
- Integrating documented `@cap-js/*` plugins
- Wiring the CAP MCP server (`@cap-js/mcp-server`)

## Directory Structure

```
sap-cap-nodejs-dev/
├── SKILL.md                          # Main skill file (scope, rules, quickstart)
├── README.md                         # This file
├── references/                       # Reference files (Node.js only)
│   ├── annotations-reference.md
│   ├── cdl-syntax.md
│   ├── cql-queries.md
│   ├── csn-cqn-cxn.md
│   ├── data-privacy-security.md
│   ├── databases.md
│   ├── deployment-cf.md
│   ├── event-handlers-nodejs.md
│   ├── extensibility-multitenancy.md
│   ├── fiori-integration.md          # CAP-side annotations only
│   ├── localization-temporal.md
│   ├── nodejs-runtime.md
│   ├── plugins-reference.md
│   ├── tools-complete.md
│   ├── consuming-services-deployment.md
│   ├── service-definitions.md
│   ├── event-handlers-patterns.md
│   ├── cql-patterns.md
│   ├── cli-complete.md
│   ├── mcp-integration.md
│   ├── mcp-use-cases.md
│   └── CAP_Troubleshooting.md
└── templates/                        # 8 template files
    ├── bookshop-schema.cds
    ├── catalog-service.cds
    ├── fiori-annotations.cds
    ├── mta.yaml
    ├── package.json
    ├── service-handler.js
    ├── service-handler.ts
    └── xs-security.json
```

## Documentation Links

- **CAP Documentation**: https://cap.cloud.sap/docs/
- **CAP GitHub**: https://github.com/cap-js/docs
- **CDS Language**: https://cap.cloud.sap/docs/cds/
- **Node.js Runtime**: https://cap.cloud.sap/docs/node.js/
- **Plugins**: https://cap.cloud.sap/docs/plugins/

## Version

- **Skill Version**: 3.0.0
- **Runtime**: Node.js only
- **CAP Version**: @sap/cds 9.7.x
- **MCP Version**: @cap-js/mcp-server 0.0.3+
- **Last Verified**: 2026-05-12
- **License**: GPL-3.0
