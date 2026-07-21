# Changelog — sap-cap-nodejs-dev

All notable changes to this skill are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the skill is
versioned **independently** of the other skills in this repo and of the repo
itself. Versions referenced here track `metadata.version` in
[`SKILL.md`](SKILL.md) frontmatter.

> **Note on the version line.** This skill descends from the
> `sap-cap-capire` (Senua) family that lived in `~/.claude/skills/` before the
> monorepo. The `3.x` series in `metadata.version` continues that family line;
> `3.1.0` is the first version published under the new name
> `sap-cap-nodejs-dev` in this repo.

## [Unreleased]

_No unreleased changes._

## [3.2.0] — 2026-05-13

### Added

- Four new reference files and one i18n extension ([455464b](https://github.com/Fab2295/sap-skills/commit/455464b)):
  - [`references/concurrency-control.md`](references/concurrency-control.md) — CAP OOTB concurrency: `@odata.etag` on `managed.modifiedAt` (optimistic), `.forUpdate()` / `.forShareLock()` on the **base** entity (capire restriction), draft serialization, SQLite/H2 limits. Source: https://cap.cloud.sap/docs/guides/services/served-ootb#concurrency-control.
  - [`references/race-conditions.md`](references/race-conditions.md) — four buckets of races and the declarative fix for each: cross-request TOCTOU, multi-statement atomicity (`cds.tx(req).run`), bootstrap race in `cds.on('served')` (vs. `init()`), event-consumer idempotency.
  - [`references/sql-injection.md`](references/sql-injection.md) — why CQL parameterizes (including the safe template-literal pattern inside `.where({ like })`); identifier allow-list for `orderBy(req.data.X)`; native-SQL escape hatch with positional `?` placeholders; payload-shape tests.
  - [`references/status-flow.md`](references/status-flow.md) — `@flow.status` + `@from` + `@to` state-machine modeling, `$flow.previous` rollback target, capire limitations, Gamma-stability caveat. Source: https://cap.cloud.sap/docs/guides/services/status-flows.
- [`references/localization-temporal.md`](references/localization-temporal.md) gained a new section **"Localized Error Messages (`messages.properties`)"** documenting the dedicated `messages` bundle (separate from `i18n`), the `req.error` / `req.reject` / `req.info` / `req.warn` / `req.notify` resolution flow, and the built-in keys CAP raises automatically: `ASSERT_MANDATORY`, `ASSERT_NOT_NULL`, `ASSERT_RANGE`, `ASSERT_ENUM`, `ASSERT_FORMAT`, `ASSERT_TARGET`, `MULTIPLE_ERRORS`.

### Changed

- **Decision order extended from 5 to 7 steps**, in both [`SKILL.md`](SKILL.md) and [`references/domain-first.md`](references/domain-first.md):
  1. Schema
  2. Annotations
  3. Views / projections
  4. **Status Flows** ← NEW — use when the use case is a true state machine
  5. CAP plugins
  6. **Concurrency control** ← NEW — `@odata.etag` first, `.forUpdate()` when invariants span rows
  7. Event handlers (last resort)
  The rule is explicit: never re-implement what `@from`/`@to`, `@odata.etag`, `@assert.*`, `@requires`, or a projection already does for free.
- [`SKILL.md`](SKILL.md) "Bundled resources" index reorganized — new group "State, concurrency & safety" lists the four new refs side-by-side; richer one-liner on the i18n entry naming the seven built-in error keys.

## [3.1.0] — 2026-05-13

### Added

- **Initial release** in the sap-skills monorepo ([d1feab4](https://github.com/Fab2295/sap-skills/commit/d1feab4)). Replaces the predecessor `sap-cap-capire` (Senua) skill that previously lived outside the monorepo. Same Capire-anchored knowledge, narrower scope, stricter API hygiene.
- **Strict scope guardrails** ([`SKILL.md`](SKILL.md) §1). The skill MUST refuse, with an explicit message:
  - Frontend / UI implementation (Fiori Elements custom code, UI5 controls, React, Vue, plain HTML/CSS/JS). CAP-side `@UI.*` annotations in `.cds` are in scope; the UI itself is not.
  - Backend in any other language or stack (Java CAP, Spring, plain Node/Express, NestJS, Python, Go, .NET, serverless outside CAP, microservices not built on `@sap/cds`).
  - Any non-CAP architecture (custom OData providers, hand-rolled REST frameworks, ad-hoc GraphQL servers that don't go through `@cap-js/graphql`).
- **Public-API-only rule** ([`SKILL.md`](SKILL.md) §2). The skill only imports from documented, stable entry points: `@sap/cds`, `@sap/cds/common`, `@cap-js/sqlite`, `@cap-js/hana`, `@cap-js/postgres`, `@cap-js/attachments`, `@cap-js/audit-logging`, `@cap-js/change-tracking`, `@cap-js/telemetry`, `@cap-js/graphql`, `@cap-js/mcp-server`, `@sap/cds-mtxs`. Never reaches into `@sap/cds/lib/*`, `_private`, `__internal`; never uses deprecated / `@experimental` / `@internal` / `@protected` APIs.
- **Domain-first decision order** ([`SKILL.md`](SKILL.md) §3, [`references/domain-first.md`](references/domain-first.md)) — Schema → Annotations → Views → Plugins → Handler (last resort). Anchored to the capire principle "Less code → Less mistakes": https://cap.cloud.sap/docs/get-started/features#less-code-%E2%86%92-less-mistakes.
- **Bundled references** (22 files mirroring the relevant Capire sections) and **templates** (8 files: bookshop schema, catalog service, Fiori annotations, MTA, package.json, JS / TS service handlers, xs-security.json).
- **41-vector security audit** shipped as [`SECURITY.md`](SECURITY.md) plus [`references/security-audit.md`](references/security-audit.md). Covers prompt injection, MCP/tool poisoning, supply chain, eval, command, SSRF, path traversal, unsafe deserialization, credential / token leakage, overpermission, unauthorized deploy, telemetry leakage. Reproducible `grep` / Python checks for `skills.sh` to re-verify the posture on every release.
- Hardenings applied during the audit:
  - Postgres example moved into a `[development]`/`[production]` profile split with an explicit warning that production credentials must come from `cds bind` / VCAP / env vars.
  - Mocked authentication block (`alice`/`bob`) labeled DEV-ONLY.
  - `cds.User.Privileged` carries an explicit "Bypasses ALL authorization — never derive from `req.*`" warning.

### Removed (compared to the predecessor Senua skill)

- Java CAP content. The skill is **Node.js only**; the `java-runtime.md` reference was dropped, and Java sections were stripped from `databases.md`, `plugins-reference.md`, `extensibility-multitenancy.md`, `consuming-services-deployment.md`, `tools-complete.md`, and `mcp-integration.md`.
- The legacy `Senua` name in the frontmatter. Skill name is now `sap-cap-nodejs-dev`.

[Unreleased]: https://github.com/Fab2295/sap-skills/compare/455464b...HEAD
[3.2.0]: https://github.com/Fab2295/sap-skills/compare/d1feab4...455464b
[3.1.0]: https://github.com/Fab2295/sap-skills/commit/d1feab4
