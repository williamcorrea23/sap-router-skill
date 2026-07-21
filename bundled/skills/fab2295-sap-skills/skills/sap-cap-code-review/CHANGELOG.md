# Changelog — sap-cap-code-review

All notable changes to this skill are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the skill is
versioned **independently** of the other skills in this repo and of the repo
itself. This skill does not yet expose a `metadata.version` in its
[`SKILL.md`](SKILL.md) frontmatter; the versions below are tracked here for
release-note purposes only.

## [Unreleased]

_No unreleased changes._

## [0.1.1] — 2026-05-12

### Fixed

- **Snyk W007** — secret redaction in Evidence excerpts ([6358555](https://github.com/Fab2295/sap-skills/commit/6358555)). Every Evidence and Suggested-fix block written to `CAP-CODE-REVIEW.md` now passes through a fail-closed filter ([`references/secret-redaction.md`](references/secret-redaction.md)) before being rendered. Credential-shaped keys (`clientSecret`, `password`, `token`, `apiKey`, `privateKey`, `connectionString`, …) and value-shape patterns (JWTs, `Bearer …`, PEM blocks, URLs with embedded `user:password@`, long hex/base64 blobs) are replaced with `[REDACTED:<kind>]`. Excerpts from credential-shaped files (`xs-security.json`, `manifest.yaml`, `mta.yaml`, `default-services.json`, `default-env.json`, `.env*`, `secrets/`) are replaced wholesale when any redaction trigger matches inside them. SEC-007 (secrets inlined in source) uses a fixed redaction format — the value is never written to the report.
- The filter is fail-closed: when a line contains something that "looks secret" but cannot be safely classified, the line is dropped. When the redacted excerpt would be empty, the code block is omitted entirely and a `<path>:<line>` pointer is used instead.

## [0.1.0] — 2026-05-11

### Added

- Initial release as part of the sap-skills monorepo ([27829a9](https://github.com/Fab2295/sap-skills/commit/27829a9)).
- Read-only static analysis of SAP CAP Node.js code (a PR, a branch comparison, or an explicit file list).
- Classifies findings as **Critical / High / Medium / Low** per [`references/severity-rubric.md`](references/severity-rubric.md). Findings without a Rule ID anchor are not emitted.
- Writes one artifact: `CAP-CODE-REVIEW.md` at the project root, rendered from [`templates/report.md`](templates/report.md).
- Each finding records: short title + Rule ID, category, `file:line`, function/class symbol, the offending Evidence excerpt (≤ 10 lines), a one-sentence rationale, a Capire-anchored reference, and a Suggested fix (≤ 5 lines) flagged as needing human validation.
- Strict negatives codified in `SKILL.md`: never edits any source file, never creates projects or scaffolds, never runs `git add`/`commit`/`push` or any git mutation, never makes a claim that is not anchored in capire docs under `references/`. Refuses Java CAP / non-CAP / generic Node.js with an explicit message.

[Unreleased]: https://github.com/Fab2295/sap-skills/compare/6358555...HEAD
[0.1.1]: https://github.com/Fab2295/sap-skills/commit/6358555
[0.1.0]: https://github.com/Fab2295/sap-skills/commit/27829a9
