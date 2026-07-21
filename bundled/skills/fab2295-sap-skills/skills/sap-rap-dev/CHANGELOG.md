# Changelog — sap-rap-dev

All notable changes to this skill are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] — 2026-05-13

### Changed
- **Restructured `references/` from narrative topics to artifact-specific
  files.** Removed `start.md`, `develop.md`, `extend.md`, `test.md`,
  `consume.md`, `reuse.md` (placeholder narratives) and replaced them
  with artifact-anchored references that match the names a RAP developer
  thinks in: `cds-view-entity.md`, `cds-table-entity.md`,
  `cds-projection-view.md`, `behavior-definition.md`,
  `behavior-implementation.md`, `service-definition.md`,
  `service-binding.md`, `metadata-extension.md`, `eml.md`,
  `value-help.md`, `testing-rap.md`.
- **Populated every reference** with substantive content and runnable
  CDS / BDEF / ABAP examples (no more placeholders).
- **`SKILL.md` scope hardened to RAP-only.** Added an explicit refusal
  matrix (CAP, classic ABAP frameworks, generic ABAP, frontend code, non-SAP
  backends, BTP cockpit operations) with the exact message to use for each.
- **`SKILL.md` declares OData V4 as the default.** OData V2 is now opt-in
  only and is generated solely when the user explicitly requests V2;
  `service-binding.md` mirrors the rule with a default column in the
  binding-types table.
- **`SKILL.md` documents the supported CDS object types** (table entity,
  DDIC table, root view entity, view entity, projection view, BDEF, service
  definition) plus the *out-of-scope* classic forms.
- **`SKILL.md` documents the supported RAP platforms / release window**
  via the new `release-support.md` (BTP ABAP Env, S/4HC public, S/4HC
  private, S/4 on-prem 1909+) with a feature availability matrix.

### Added
- `references/release-support.md` — RAP platform matrix, feature
  availability per release, strict-mode guidance, ABAP Cloud development
  model summary.
- `references/managed-vs-unmanaged.md` — dedicated comparison of managed,
  unmanaged, managed-with-unmanaged-save, and projection BOs, with code
  samples for each and a decision tree.
- `references/stream-handling.md` — file upload / download via
  `@Semantics.largeObject` and OData V4 stream properties, including an
  upload security checklist (MIME whitelist, max octet length,
  content-disposition, SVG hazard, post-upload scanning hint).
- **Untrusted-content discipline** section in `SKILL.md` — every input
  (user message, file content, pasted snippets, fetched pages, command
  output) is treated as data, never instructions; the skill never
  rescopes itself from pasted content and never echoes secret-shaped
  values.

### Security
- **Defensive review of all skill files** for: prompt-injection vectors,
  instruction-override phrases, shell-execution patterns (`curl` / `wget`
  / `bash -c` / `sh -c`), secret-shaped strings (`AKIA…`, `ghp_…`,
  `sk-…`, JWTs, PEM blocks, inline `client_secret` / `password` / `apiKey`
  assignments), and non-allow-listed external URLs. All four scans clean
  at release time.
- Replaced a sample placeholder URL in `testing-rap.md` (`http://local-
  endpoint-url`) with a clearly-marked placeholder pointing the developer
  at the ADT Local Service Endpoint field.
- Rephrased the prompt-injection defense example in `SKILL.md §9` so the
  literal redirect phrase is not reproduced verbatim — defense in depth.
- Replaced a `TBD` token in `stream-handling.md` with concrete platform
  guidance.

### Status
- `metadata.status: "draft"` — references are populated and reviewed for
  security, but should be reviewed by a human RAP expert against the
  current SAP Help Portal for the target ABAP release before flipping
  to `released`.

## [0.1.0] — 2026-05-13

### Added
- Initial skeleton for the SAP RAP development skill.
- `SKILL.md` with frontmatter declaring scope, hard refusals, released-API
  rule, decision order, and reference index.
- Placeholder reference files matching the SAP Help Portal RAP guide
  navigation (Learn / Start / Develop / Extend / Test / Consume / Reuse /
  CDS Annotations) plus `glossary.md` and `released-apis.md`.
- Empty `templates/` folder.

### Status
- `metadata.status: "skeleton"` — placeholders only.
