# Changelog — sap-skills (repo)

All notable repository-level events (skill added / removed / renamed, license,
shared policies, layout) are documented here. **Per-skill changes go in each
skill's own `CHANGELOG.md`** — this file does not duplicate them.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Skills are versioned **independently** of the repo; entries here reference the
skill version at the moment of the change.

## [Unreleased]

_No unreleased repo-level changes._

## 2026-05-13 — sap-rap-dev added (ABAP / RAP family bootstrapped)

### Added
- New skill **sap-rap-dev** (`0.2.0`, status `draft`). SAP ABAP RESTful
  Application Programming Model (RAP) development guide. End-to-end scope:
  CDS table/view/projection entities, behavior definitions and
  implementations (managed / unmanaged / projection / extension), service
  definitions + bindings, metadata extensions, value helps, file
  upload/download via `@Semantics.largeObject` streams, RAP testing.
  Default OData version: **V4**; V2 is opt-in only. Refuses CAP
  (Node.js/Java), classic ABAP frameworks (BOPF, FPM, Web Dynpro, SAP
  GUI), generic ABAP, UI5/Fiori frontend code, non-SAP backends, and any
  `NOT_RELEASED` / `NOT_TO_BE_RELEASED` / deprecated API. First skill
  in the **SAP ABAP / RAP** family — the section in the README is now
  populated.
- 18 artifact-anchored reference files under
  [`skills/sap-rap-dev/references/`](skills/sap-rap-dev/references/):
  `cds-view-entity.md`, `cds-table-entity.md`, `cds-projection-view.md`,
  `behavior-definition.md`, `behavior-implementation.md`,
  `managed-vs-unmanaged.md`, `service-definition.md`,
  `service-binding.md`, `metadata-extension.md`, `eml.md`,
  `value-help.md`, `stream-handling.md`, `testing-rap.md`,
  `cds-annotations.md`, `release-support.md`, `released-apis.md`,
  `learn.md`, `glossary.md`. Each populated with substantive guidance
  and runnable CDS / BDEF / ABAP examples.
- Root [README.md](README.md): new row in the **SAP ABAP / RAP** family
  table, dedicated section "sap-rap-dev (RAP development)" with the
  allowed-write-targets table, V4-default rule, released-API rule, and
  untrusted-content discipline, plus a new entry in the layout tree.

### Changed
- The **SAP ABAP / RAP** section in the README is no longer a "_No skills
  yet._" placeholder.

### Security
- The new skill ships with the same security scans the rest of the repo
  uses: prompt-injection / instruction-override phrases, shell-exec
  patterns, secret-shaped strings, and non-allow-listed external URLs.
  All four scans clean at release time. The skill declares an explicit
  **untrusted-content discipline** in `SKILL.md §9` — every input (user
  messages, file contents, pasted CDS/ABAP snippets, fetched help pages,
  command output) is treated as data, never instructions; the skill
  never rescopes itself from pasted directives and never echoes
  secret-shaped values back into its output.

## 2026-05-13 — repo re-framed, changelogs adopted

### Changed

- **Root README re-framed**: the repo is now described as a monorepo of **SAP-focused** skills (not "SAP CAP" specifically). Skills are grouped by SAP technology family — current coverage is **SAP CAP (Node.js)**, with explicit "no skills yet" sections for **SAP ABAP / RAP** and **SAP BTP services / S/4HANA / Fiori Elements / SAP Build** so the gaps are visible. New "Adding a new skill" section documents the contract for proposing skills in any family.
- **Shared principles** rule #4 generalized: instead of hard-coding "CAP Node.js only", the principle is now "each skill declares its own scope in its SKILL.md and refuses out-of-scope requests with an explicit message" — today that scope is CAP Node.js for every skill, but the framework supports future ABAP / RAP / S/4HANA skills declaring and enforcing their own scope.
- **Shared principles** gained rule #6: "independently versioned and changelog'd". Each skill now ships its own `CHANGELOG.md` tracking `metadata.version`; the root `CHANGELOG.md` (this file) is reserved for repo-level events.

### Added

- This `CHANGELOG.md` (repo-level events).
- Per-skill changelogs:
  - [`skills/sap-cap-test/CHANGELOG.md`](skills/sap-cap-test/CHANGELOG.md) (current: `0.1.0`).
  - [`skills/sap-cap-code-review/CHANGELOG.md`](skills/sap-cap-code-review/CHANGELOG.md) (current: `0.1.1`, backfilled).
  - [`skills/sap-cap-upgrade/CHANGELOG.md`](skills/sap-cap-upgrade/CHANGELOG.md) (current: `0.5.2`, backfilled across `0.1.0` → `0.3.0` → `0.4.0` → `0.5.0` → `0.5.1` → `0.5.2`).
  - [`skills/sap-cap-nodejs-dev/CHANGELOG.md`](skills/sap-cap-nodejs-dev/CHANGELOG.md) (current: `3.2.0`, backfilled across `3.1.0` → `3.2.0`).
- Each per-skill `CHANGELOG.md` was backfilled from the git history of this repo, grouped by conventional-commit scope, and uses the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format with comparison links.

## 2026-05-13

### Added
- New skill **sap-cap-nodejs-dev** (`3.1.0`) ([d1feab4](https://github.com/Fab2295/sap-skills/commit/d1feab4)). CAP Node.js development guide. Domain-first ("less code → less mistakes"). Refuses UI/frontend, Java CAP, non-CAP backends and any internal/protected/deprecated CAP API. Ships [SECURITY.md](skills/sap-cap-nodejs-dev/SECURITY.md) with a 41-vector audit matrix and reproducible `grep`/Python checks.
- Root [README.md](README.md): new row in the skills table, dedicated section "sap-cap-nodejs-dev (CAP Node.js development)", and a new entry in the layout tree.

## 2026-05-11

### Added
- Initial repository ([27829a9](https://github.com/Fab2295/sap-skills/commit/27829a9)). Two skills bundled: **sap-cap-test** (`0.1.0`) and **sap-cap-code-review** (`0.1.0`).
- skills.sh badge in the root README ([2a8b40d](https://github.com/Fab2295/sap-skills/commit/2a8b40d)).
- New skill **monza** (CAP upgrade, docs-only) ([fd4c83d](https://github.com/Fab2295/sap-skills/commit/fd4c83d)).

### Changed
- **monza** renamed to **sap-cap-upgrade** ([546826c](https://github.com/Fab2295/sap-skills/commit/546826c)). Folder, frontmatter `name`, and root README updated. Initial version `0.1.0` published under the new name.

---

## Shared policies (always-on, no per-release entry)

These apply to **every** skill in this repo, regardless of which SAP technology
it targets, and are not re-listed on each version bump:

1. **Read-mostly.** Writes are confined to a documented allowlist per skill.
2. **No git mutations.** Read-only git (`status`, `diff`, `log`, `show`, `merge-base`, `rev-parse`, `ls-files`) is allowed; nothing that changes refs / working tree / staging.
3. **No unsolicited installs.** A skill may surface a package install command (`npm i -D <package>`, `abapGit pull <repo>`, etc.) and wait for the user; it never runs it.
4. **Declared scope, hard refusal.** Each skill names its scope in its `SKILL.md` and refuses out-of-scope requests with an explicit message. Today every skill targets SAP CAP Node.js and refuses Java CAP / non-CAP / generic Node.js. Future ABAP / RAP / S/4HANA / BTP skills will declare and enforce their own scope the same way.
5. **Anchored to an authoritative source.** Every behavior or finding traces back to a file under that skill's `references/`, which mirrors the relevant section of the vendor docs (capire for CAP, SAP Help Portal for ABAP/RAP, etc.).
6. **Independently versioned and changelog'd.** Each skill carries its own `metadata.version` in `SKILL.md` and its own `CHANGELOG.md`. This root file records only repo-level events.

Changes to these policies WOULD produce a repo-level CHANGELOG entry.

## How to read this together with the per-skill logs

| Question | Where to look |
|---|---|
| "What changed in `sap-cap-upgrade` between 0.4.0 and 0.5.2?" | [`skills/sap-cap-upgrade/CHANGELOG.md`](skills/sap-cap-upgrade/CHANGELOG.md) |
| "Which skills exist in the repo and when were they added?" | This file |
| "Did the LICENSE or the shared rules change?" | This file |
| "Why was monza renamed?" | This file (the entry on 2026-05-11) |
