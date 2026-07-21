# Changelog — sap-cap-test

All notable changes to this skill are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the skill is
versioned **independently** of the other skills in this repo and of the repo
itself. Versions referenced here track `metadata.version` in
[`SKILL.md`](SKILL.md) frontmatter.

## [Unreleased]

_No unreleased changes._

## [0.1.0] — 2026-05-11

### Added

- Initial release as part of the sap-skills monorepo ([27829a9](https://github.com/Fab2295/sap-skills/commit/27829a9)).
- Test-only skill for SAP CAP Node.js projects: scaffolds and runs tests via `cds test` (Node.js test runner wrapper).
- Opt-in coverage with `c8` — must be requested explicitly by the user.
- Writes test files under `test/` (or the project's existing test folder) and emits two report files at the project root:
  - `CAP-TEST-REPORT.md` — successful-run summary (always emitted on a clean run).
  - `CAP-TEST-FAILURE.md` — failure report (only when at least one test fails).
- Strict negatives codified in `SKILL.md`: never edits production code (`srv/**`, `db/**`, `app/**`, `package.json`, `.cdsrc.json`, `mta.yaml`, `xs-security.json`); never runs git mutations; never installs dependencies on its own.

[Unreleased]: https://github.com/Fab2295/sap-skills/compare/27829a9...HEAD
[0.1.0]: https://github.com/Fab2295/sap-skills/commit/27829a9
