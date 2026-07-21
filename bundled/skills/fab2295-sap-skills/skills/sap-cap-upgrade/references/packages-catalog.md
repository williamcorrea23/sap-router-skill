# Packages Catalog — In-Scope Libraries

The `sap-cap-upgrade` skill operates **only** on packages whose name matches the regex below. Anything else in `package.json` (including `@sap/xssec`, `@sap/approuter`, `@sap/hana-client`, `@sap/audit-logging` if present as standalone, etc.) is left untouched — even when listed in the same file.

## Why this scope?

The skill's value comes from **anchoring every reported bug to an entry in an official changelog mirror** (the strict A∧B∧C rule in `bug-attribution-rules.md`). That anchor only works for package families whose vendor publishes a structured release log this skill ships a mirror of:

- **`@sap/cds*`** — CAP framework. Changelog mirror: `references/changelogs/cap/`.
- **`@cap-js/*`** — official CAP community plugins, all governed by the same CAP release cadence and changelog. Mirror: `references/changelogs/cap/`.
- **`@sap-cloud-sdk/*`** — SAP Cloud SDK for JavaScript. Changelog mirror: `references/changelogs/cloud-sdk-js/`.
- **`@sap/eslint-plugin-cds`** — the CDS-aware ESLint plugin. Same CAP release log.

A package that does NOT have a mirror in `references/changelogs/` cannot be attributed safely:

- A failure after the bump cannot be matched to a concrete changelog entry (criterion B fails), so it would always end up in `discarded[]`.
- "Version crossing" (criterion C) cannot be checked without a structured release log.
- Without those anchors, "version-caused" becomes a guess, which violates the skill's first promise (no soft-reporting).

Anything outside the four families above — **even other `@sap/*` packages** (`@sap/xssec`, `@sap/approuter`, `@sap/hana-client`, `@sap/audit-logging` standalone, `@sap/instance-manager`, `@sap/textbundle`, `@sap/hdi-deploy`, `@sap/cds-dbm`) and any non-SAP runtime dependency (`express`, `axios`, `lodash`, `passport`, `sqlite3`, `better-sqlite3`, etc.) — is **out of scope by design**, not by oversight:

- These packages have their own release cadence, security policies and breaking-change conventions which the skill does not mirror.
- Bumping them without anchored attribution would dilute the safety guarantee of every other finding in the report.
- Upgrading them safely belongs to a different tool (Renovate / Dependabot / `npm-check-updates`), where the user reviews each change in context.

The regex is the **authoritative gate**. Adding a new package family to it requires (a) shipping a changelog mirror for that family under `references/changelogs/<family>/`, (b) extending the routing table below, and (c) bumping the skill version. Until then, no `@sap/*` outside the four families is bumped, period.

## Aggregate regex (authoritative)

```
^(@sap/cds(-.*)?|@cap-js/.+|@sap-cloud-sdk/.+|@sap/eslint-plugin-cds)$
```

Each match is routed to **exactly one** changelog source. The skill must use the routing table below to decide which mirror to consult during bug attribution.

## Routing table

| Family | npm name pattern | Changelog source | Local mirror folder |
|---|---|---|---|
| CAP framework | `@sap/cds`, `@sap/cds-dk`, `@sap/cds-lsp`, `@sap/cds-compiler`, `@sap/cds-mtxs`, `@sap/cds-fiori`, `@sap/cds-hana` | https://cap.cloud.sap/docs/releases/ | `references/changelogs/cap/` |
| CAP plugins (community) | `@cap-js/sqlite`, `@cap-js/postgres`, `@cap-js/hana`, `@cap-js/openapi`, `@cap-js/asyncapi`, `@cap-js/telemetry`, `@cap-js/mcp-server`, `@cap-js/audit-logging`, `@cap-js/attachments`, `@cap-js/change-tracking`, all other `@cap-js/*` | https://cap.cloud.sap/docs/releases/ | `references/changelogs/cap/` |
| CAP lint | `@sap/eslint-plugin-cds` | https://cap.cloud.sap/docs/releases/ | `references/changelogs/cap/` |
| SAP Cloud SDK for JavaScript | `@sap-cloud-sdk/connectivity`, `http-client`, `odata-common`, `odata-v2`, `odata-v4`, `openapi`, `generator`, `resilience`, `util`, `eslint-config`, all other `@sap-cloud-sdk/*` | https://sap.github.io/cloud-sdk/docs/js/release-notes | `references/changelogs/cloud-sdk-js/` |

## Out of scope (never bumped, never blamed)

These packages may exist in `package.json` but are deliberately ignored by `sap-cap-upgrade`:

- `@sap/xssec`, `@sap/approuter`, `@sap/hana-client`, `@sap/audit-logging` (the standalone non-`@cap-js/*` variant), `@sap/instance-manager`, `@sap/textbundle`, `@sap/hdi-deploy`, `@sap/cds-dbm`
- Anything not under `@sap/cds*`, `@cap-js/*`, `@sap-cloud-sdk/*`, or `@sap/eslint-plugin-cds`
- Dev/runtime peers (`express`, `passport`, `sqlite3`, `better-sqlite3`, etc.)

## Disambiguation

When a package matches **both** `@sap/cds(-.*)?` and another rule (it cannot in practice), CAP wins. When a name has historical aliases (e.g. some `@sap/audit-logging` features migrated to `@cap-js/audit-logging`), only the package literally present in `package.json` is bumped — no automatic re-mapping.
