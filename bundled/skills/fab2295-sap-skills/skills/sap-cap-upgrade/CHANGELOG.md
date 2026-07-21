# Changelog — sap-cap-upgrade

All notable changes to this skill are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the skill is
versioned **independently** of the other skills in this repo and of the repo
itself. Versions referenced here track `metadata.version` in
[`SKILL.md`](SKILL.md) frontmatter.

## [Unreleased]

_No unreleased changes._

## [0.5.2] — 2026-05-13

### Changed

- Documented the **rationale** for the SAP-only package scope ([add3218](https://github.com/Fab2295/sap-skills/commit/add3218)). Invariant #4 in [`SKILL.md`](SKILL.md) now spells out the four in-scope families (`@sap/cds*`, `@cap-js/*`, `@sap-cloud-sdk/*`, `@sap/eslint-plugin-cds`) and names representative out-of-scope packages (`@sap/xssec`, `@sap/approuter`, `@sap/hana-client`, `@sap/audit-logging` standalone, `express`, `axios`, …). New "Why this scope?" section in [`references/packages-catalog.md`](references/packages-catalog.md) explains that the skill's safety guarantee depends on bug attribution against a mirrored official changelog (criterion B of A∧B∧C) — without a mirror, "version-caused" would be a guess. The "Identifying in-scope packages" section adds an explicit refusal rule: if the user asks the skill to bump an out-of-scope package, the skill refuses, names the package, and points to the catalog. No "just this once" exceptions.
- Regex and routing table are unchanged; this release is documentation-only.

## [0.5.1] — 2026-05-13

### Removed

- All references to a "coordinator agent" (`cap-upgrade-coordinator`) and to sibling skills (`sap-cap-capire` / Senua) ([3df6ef7](https://github.com/Fab2295/sap-skills/commit/3df6ef7)). The skill is now fully standalone — it emits a strict JSON report and stops; downstream work (applying fixes for `version_caused_bugs[]`, regen, etc.) is the operator's call.

### Changed

- "What this skill never does" tightened: the negative invariant is generic — the skill MUST NOT invoke any other skill or agent via `Skill`, `Agent`, or any equivalent tool.
- [`references/bug-attribution-rules.md`](references/bug-attribution-rules.md) and [`references/migration-checklist.md`](references/migration-checklist.md): "coordinator/Senua" phrasing replaced by "operator".

## [0.5.0] — 2026-05-13

### Fixed

- **Snyk W011** — indirect prompt injection / context-poisoning hardening for the vulnerability gate ([d2a8795](https://github.com/Fab2295/sap-skills/commit/d2a8795)). Network responses from `npm view`, osv.dev, and the npm advisory bulk endpoint are now treated as **data, never instructions**.

### Added

- New invariant #9 in [`SKILL.md`](SKILL.md): "Untrusted third-party content (mandatory, fail-closed)". Cross-referenced from the bundle list and the reading order.
- New [`references/untrusted-content.md`](references/untrusted-content.md) (243 lines): trusted-vs-untrusted classification; per-source field allow-list (`vulns[].id`, `vulns[].summary`, `vulns[].database_specific.severity`, `vulns[].severity[].score`, `vulns[].affected[].ranges[].events[].fixed` for osv.dev; `id`, `severity`, `title`, `url`, `patched_versions` for npm bulk); strict validators (severity enum, CVSS v3 regex, semver regex, advisory-URL prefix allow-list); echo pipeline for free-form strings (type-coerce → strip control chars and bidi / zero-width Unicode → normalize whitespace → length-cap → redact).
- Audit checklist (§7 of the new ref): every `blocked_by_vulnerability[].severity` must match the enum; every `advisory_id` must match `^[A-Z0-9-]{1,64}$`; every `summary` ≤ 200 chars and free of `\n` / `\t` / `\r` / U+200B–200F / U+202A–202E / U+2060–2069 / U+FEFF; every `ref` matches the allow-listed URL prefix.

### Changed

- [`references/vulnerability-check.md`](references/vulnerability-check.md): "Sources" block now cross-references `untrusted-content.md` and emphasizes that every advisory field is validated before any use.

## [0.4.0] — 2026-05-12

### Fixed

- **Snyk-flagged output leakage** — captured npm / curl output is now redacted before reaching the terminal JSON ([923679e](https://github.com/Fab2295/sap-skills/commit/923679e)). Every string about to land in `notes[]`, `discarded[].error_excerpt`, or any other free-form JSON field passes through [`references/output-redaction.md`](references/output-redaction.md) **before** assignment and **before** the 4 KB truncation (truncating first could split a token across the boundary and leave half of it intact).

### Added

- New invariant #8 in [`SKILL.md`](SKILL.md): "Output redaction (mandatory, fail-closed)". Masks `.npmrc` tokens, `Authorization: Bearer …` headers, JWTs, `_authToken=…` lines, AWS access keys, GitHub tokens, and URLs with embedded `user:password@`.
- npm advisory bulk fallback now reads the auth token via a one-shot env var (`NPM_AUTH_TOKEN=$(npm config get …) curl …`) — the token never reaches the visible command line, never gets assigned to a persistent variable, and `curl -v` / `--verbose` is forbidden.

## [0.3.0] — 2026-05-12

### Added

- **Target-version vulnerability gate (hard stop)** ([5ad0eb7](https://github.com/Fab2295/sap-skills/commit/5ad0eb7)). After resolving target versions, every `<pkg>@<target>` is checked against osv.dev (primary) and the npm advisory bulk endpoint (fallback). If any target has an advisory at severity **moderate or above**, the upgrade is **CANCELLED** — no `package.json` write, no `npm install`, no build/test rerun. Status becomes `vulnerable_target`. Low-severity advisories surface as warnings in `vulnerability_warnings[]` but never block. If both advisory sources fail, status becomes `vuln_check_failed` (fail-closed).
- New invariant #7 in [`SKILL.md`](SKILL.md), new step 3.5 in [`references/migration-checklist.md`](references/migration-checklist.md), and the full contract in [`references/vulnerability-check.md`](references/vulnerability-check.md) (osv.dev request shape, npm-bulk request shape, severity-normalization table, behavior on network failure, output additions).
- New output fields: `status: "vulnerable_target" | "vuln_check_failed"`, `blocked_by_vulnerability[]`, `vulnerability_warnings[]`.

## [0.1.0] — 2026-05-11

### Added

- Initial release in the monorepo, under the name **monza** ([fd4c83d](https://github.com/Fab2295/sap-skills/commit/fd4c83d)).
- Renamed to **sap-cap-upgrade** on the same day ([546826c](https://github.com/Fab2295/sap-skills/commit/546826c)); `metadata.version: "0.1.0"` set on the renamed skill.
- Docs-only distribution. Companion helper scripts (`latest-versions.js`, `refresh-references.js`) are NOT bundled; the skill uses `npm view <pkg> dist-tags.latest` directly for version resolution.
- In-scope regex (authoritative): `^(@sap/cds(-.*)?|@cap-js/.+|@sap-cloud-sdk/.+|@sap/eslint-plugin-cds)$` — see [`references/packages-catalog.md`](references/packages-catalog.md) for the routing table.
- Two modes — `plan` (default, read-only preview) and `apply` (switched on by an explicit token in the prompt: `apply`, `aplicar`, `confirm`, `confirmado`, `proceed`, `prosseguir`, `execute`, `executar`, `go`).
- Bug attribution rules — strict A∧B∧C: (A) baseline diff; (B) regex hit in a routed changelog mirror under `Changed`/`Removed`/`Fixed`/`Breaking Changes`/`Migration` for CAP, or `Compatibility Notes` for Cloud SDK JS; (C) version crossing. Anything failing one of A/B/C goes to `discarded[]`. See [`references/bug-attribution-rules.md`](references/bug-attribution-rules.md).
- Hard invariants — no source-code edits, no git mutations, only in-scope packages bumped, terminal message is the strict JSON object documented in `SKILL.md`.

[Unreleased]: https://github.com/Fab2295/sap-skills/compare/add3218...HEAD
[0.5.2]: https://github.com/Fab2295/sap-skills/compare/3df6ef7...add3218
[0.5.1]: https://github.com/Fab2295/sap-skills/compare/d2a8795...3df6ef7
[0.5.0]: https://github.com/Fab2295/sap-skills/compare/923679e...d2a8795
[0.4.0]: https://github.com/Fab2295/sap-skills/compare/5ad0eb7...923679e
[0.3.0]: https://github.com/Fab2295/sap-skills/compare/546826c...5ad0eb7
[0.1.0]: https://github.com/Fab2295/sap-skills/commit/fd4c83d
