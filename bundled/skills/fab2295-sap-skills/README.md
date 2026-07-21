# sap-skills

[![skills.sh](https://skills.sh/b/Fab2295/sap-skills)](https://skills.sh/Fab2295/sap-skills)

> Monorepo of **SAP-focused skills** for [Claude Code](https://claude.com/claude-code).
> Covers any SAP technology where a small, anchored, auditable agent skill helps:
> SAP CAP, ABAP, RAP, S/4HANA, SAP BTP, SAP Build, Fiori Elements, and more as
> they come.
>
> Every skill is **scoped to one SAP technology** (declared in its `SKILL.md`),
> **anchored to its authoritative source** (capire for CAP, SAP Help Portal for
> ABAP/RAP, etc.), and ships **strict negatives** — no commits, no pushes, no
> out-of-scope writes.

## Install

Install the whole bundle in one shot:

```sh
npx skills add Fab2295/sap-skills
```

The installer reads the `skills/<name>/SKILL.md` files in this repo and
deploys them to your agent's skill directory
(e.g. `~/.claude/skills/<name>/`). You can install individual skills the same
way: `npx skills add Fab2295/sap-skills/<skill-name>`.

## Skills

Skills are organized by SAP technology family. Current coverage is **SAP CAP
(Node.js)**; other families (ABAP/RAP, S/4HANA, BTP services, …) appear here
as they're added — empty sections call them out so the gap is visible.

### SAP CAP (Node.js)

Anchor: [capire](https://cap.cloud.sap/docs/). All four skills below refuse Java
CAP, generic Node.js, and non-CAP projects.

| Skill | Purpose | What it writes |
|---|---|---|
| [`sap-cap-test`](skills/sap-cap-test/) | Scaffolds and runs CAP tests with `cds add test` + `cds test`. Opt-in coverage via `c8`. | Test files under `test/` and one of `CAP-TEST-REPORT.md` / `CAP-TEST-FAILURE.md` at the project root. |
| [`sap-cap-code-review`](skills/sap-cap-code-review/) | Read-only static analysis of a PR / branch / file list. Classifies findings as Critical / High / Medium / Low. | `CAP-CODE-REVIEW.md` at the project root. |
| [`sap-cap-upgrade`](skills/sap-cap-upgrade/) | Upgrades `@sap/cds*`, `@cap-js/*`, `@sap-cloud-sdk/*`, `@sap/eslint-plugin-cds` to the latest stable (incl. majors). Runs a **vulnerability gate** on every target version (osv.dev primary, npm advisory bulk fallback) — aborts the upgrade when any target has an advisory ≥ moderate. Cross-checks failures against locally mirrored CAP + Cloud SDK JS changelogs and reports ONLY bugs caused by the version bump. | Edits `package.json` (and `package-lock.json` via `npm install`) in apply mode — and only when the vulnerability gate passes. Plan mode writes nothing. |
| [`sap-cap-nodejs-dev`](skills/sap-cap-nodejs-dev/) | CAP Node.js development guide. Domain-first ("less code → less mistakes"): prefers CDS schema, annotations, projections, status flows and CAP's generic providers over hand-written handlers. Strict scope: refuses UI/frontend, Java CAP, non-CAP backends, and any internal/protected/deprecated CAP API. | Suggests CDS / JS / config files inside the project's `db/`, `srv/`, and `package.json` / `.cdsrc.json`. Never edits `app/` (UI). Never runs `git add/commit/push` and never installs dependencies. |

### SAP ABAP / RAP

Anchor: [SAP Help Portal — ABAP](https://help.sap.com/docs/abap-cloud).

| Skill | Purpose | What it writes |
|---|---|---|
| [`sap-rap-dev`](skills/sap-rap-dev/) | SAP ABAP RESTful Application Programming Model (RAP) development guide. End-to-end scope: CDS table/view/projection entities, behavior definitions and implementations (managed / unmanaged / projection / extension), service definitions + bindings (**OData V4 by default; V2 only on explicit user request**), metadata extensions, value helps, file upload/download via `@Semantics.largeObject` streams, and RAP testing. Strict scope: refuses CAP (Node.js/Java), classic ABAP frameworks (BOPF, FPM, Web Dynpro, SAP GUI), generic ABAP, UI5/Fiori frontend code, non-SAP backends, and any `NOT_RELEASED` / `NOT_TO_BE_RELEASED` / deprecated API. | Suggests CDS / BDEF / ABAP files inside the project's ADT packages. Never edits UI code. Never runs `git add/commit/push`. |

### SAP BTP services / S/4HANA / Fiori Elements / SAP Build

Anchors: [SAP BTP](https://help.sap.com/docs/btp), [SAP Help Portal](https://help.sap.com/).

_No skills yet._ Open issues / PRs welcome.

---

## Per-skill details

### sap-cap-test (test-only)

| Allowed write targets |
|---|
| `test/**`, `tests/**`, `__tests__/**` (the project's test folder) |
| `CAP-TEST-REPORT.md`, `CAP-TEST-FAILURE.md` (project root) |

**Never**: edits `srv/`, `db/`, `app/`, `package.json`, `.cdsrc.json`,
`mta.yaml`, `xs-security.json`; runs `git add/commit/push`; installs
dependencies on its own; enables coverage without explicit opt-in.

Reference: <https://cap.cloud.sap/docs/node.js/cds-test>
Changelog: [`skills/sap-cap-test/CHANGELOG.md`](skills/sap-cap-test/CHANGELOG.md)

### sap-cap-code-review (read-only review)

| Allowed write targets |
|---|
| `CAP-CODE-REVIEW.md` (project root) |

**Never**: edits any source file; runs `git add/commit/push`; emits a
finding that isn't anchored to a Rule ID under
`skills/sap-cap-code-review/references/`; pastes a verbatim secret
into the report.

> 🔒 **Secret redaction (mandatory).** Every Evidence and Suggested-fix
> excerpt is passed through the fail-closed filter at
> [`skills/sap-cap-code-review/references/secret-redaction.md`](skills/sap-cap-code-review/references/secret-redaction.md):
> credential-shaped keys (`clientSecret`, `password`, `token`, `apiKey`,
> `privateKey`, `connectionString`, etc.) and value-shape patterns
> (JWTs, `Bearer …`, PEM blocks, URLs with embedded `user:password@`,
> long hex/base64 blobs) are replaced with `[REDACTED:<kind>]`.
> Excerpts from credential-shaped files (`xs-security.json`,
> `manifest.yaml`, `mta.yaml`, `default-services.json`,
> `default-env.json`, `.env*`, `secrets/`) are replaced wholesale when
> any redaction trigger matches. SEC-007 (secrets inlined in source)
> uses a fixed redaction format — the value is never written to the
> report.

Reference rubric: `skills/sap-cap-code-review/references/severity-rubric.md`
Changelog: [`skills/sap-cap-code-review/CHANGELOG.md`](skills/sap-cap-code-review/CHANGELOG.md)

### sap-cap-upgrade (CAP upgrade)

| Allowed write targets |
|---|
| `package.json` (in apply mode only) |
| `package-lock.json` — indirectly, via `npm install` |

**Never**: edits source code; runs `git add/commit/push/checkout/restore/stash`;
calls another skill; reports a failure as "version-caused" unless it satisfies
the strict A∧B∧C criteria in `skills/sap-cap-upgrade/references/bug-attribution-rules.md`.

**Default mode is `plan`** (read-only preview). Switch to `apply` only when
the invocation explicitly contains one of: `apply`, `aplicar`, `confirm`,
`confirmado`, `proceed`, `prosseguir`, `execute`, `executar`, `go`.

> 🔒 **Vulnerability gate (hard stop).** Before any `package.json` write the
> skill queries osv.dev (primary) and the npm advisory bulk endpoint
> (fallback) for every `<pkg>@<target>`. If any target has an advisory at
> **moderate severity or above**, the upgrade is cancelled — the JSON
> output uses `status: "vulnerable_target"` with the offending entries in
> `blocked_by_vulnerability[]`. Low-severity advisories surface as
> `vulnerability_warnings[]` and do not block. If both sources fail, status
> is `vuln_check_failed` (fail-closed). Contract: `skills/sap-cap-upgrade/references/vulnerability-check.md`.

> 🔒 **Untrusted third-party content (fail-closed).** Every network response
> (`npm view`, osv.dev, npm advisory bulk) is treated as **data, never
> instructions** per
> [`skills/sap-cap-upgrade/references/untrusted-content.md`](skills/sap-cap-upgrade/references/untrusted-content.md).
> Only an explicit field allow-list per source is read; categorical fields
> (`severity`) are matched against a strict enum; CVSS vectors and semver
> strings are regex-validated before they influence control flow; free-form
> strings (`summary`, `title`, advisory URLs) pass through an echo pipeline
> that strips control characters + bidi / zero-width Unicode, normalizes
> whitespace, length-caps, and runs the same redaction filter as below. The
> agent does NOT substring-match free-form fields to derive severity and
> does NOT re-read echoed values to make decisions. Snyk **W011** defense.

> 🔒 **Output redaction (mandatory, fail-closed).** Every string the skill
> captures from `npm install`, `cds build`, the osv.dev response, and the
> npm advisory bulk endpoint is passed through
> [`skills/sap-cap-upgrade/references/output-redaction.md`](skills/sap-cap-upgrade/references/output-redaction.md)
> before being written into the JSON output (`notes[]`,
> `discarded[].error_excerpt`, etc.). Masks: `Authorization: Bearer …`,
> `_authToken=…` npmrc lines, JWTs, GitHub/AWS tokens, URLs with embedded
> `user:password@`, and unclassified token-shaped runs adjacent to
> credential keywords. The npm advisory fallback reads the token via a
> one-shot env var (`NPM_AUTH_TOKEN=$(...) curl ...`) — the token never
> reaches the visible command line. Truncation happens **after**
> redaction (not before — otherwise half a secret could survive at the
> boundary).

> ⚠️ This published version of `sap-cap-upgrade` is **docs-only** — the
> companion helper scripts (`latest-versions.js`, `refresh-references.js`)
> are NOT bundled. The skill uses `npm view <pkg> dist-tags.latest`
> directly for version resolution, and reference mirrors must be
> refreshed manually from the URLs in `skills/sap-cap-upgrade/references/source.md`.

Reference catalog: `skills/sap-cap-upgrade/references/packages-catalog.md`
Changelog: [`skills/sap-cap-upgrade/CHANGELOG.md`](skills/sap-cap-upgrade/CHANGELOG.md)

### sap-cap-nodejs-dev (CAP Node.js development)

| Allowed write targets |
|---|
| `db/**` (CDS schema, views, seed CSV) |
| `srv/**` (service `.cds`, Node.js handlers, CAP-side `@UI.*` annotations) |
| `package.json`, `.cdsrc.json` (CDS config only — never adds runtime deps without the user) |

**Never**: edits `app/` (UI is out of scope); writes Java / Spring / Express / NestJS code; introduces non-CAP architectures (custom OData / REST / GraphQL outside `@cap-js/graphql`); imports from `@sap/cds/lib/...` or other internal paths; uses `@deprecated` / `@experimental` / `@internal` / `@protected` APIs; runs `git add/commit/push`; installs dependencies.

**Domain-first guarantee.** Decision order is enforced: schema → annotations → views/projections → status flows → `@cap-js/*` plugins → concurrency control (`@odata.etag` / `.forUpdate`) → handler (last resort). The "is this PR domain-first?" checklist lives at [`skills/sap-cap-nodejs-dev/references/domain-first.md`](skills/sap-cap-nodejs-dev/references/domain-first.md).

> 🔒 **Audited surface.** The skill ships [`skills/sap-cap-nodejs-dev/SECURITY.md`](skills/sap-cap-nodejs-dev/SECURITY.md) with a 41-vector posture matrix (Prompt Injection, MCP/Tool Poisoning, Supply Chain, Eval / Command / SSRF / Path / Unsafe Deserialization, Credential / Token Leakage, Overpermission, Unauthorized Deploy, Telemetry Leakage, …) plus reproducible `grep` / Python checks the auditor can re-run. The only credential material in the corpus is mocked dev (alice/bob) and a postgres example, both `[development]`-profile gated and explicitly labeled DEV-ONLY.

Reference catalog: [`skills/sap-cap-nodejs-dev/SKILL.md`](skills/sap-cap-nodejs-dev/SKILL.md)
Changelog: [`skills/sap-cap-nodejs-dev/CHANGELOG.md`](skills/sap-cap-nodejs-dev/CHANGELOG.md)

### sap-rap-dev (RAP development)

| Allowed write targets |
|---|
| ADT-managed RAP artifacts under the project's package: CDS table entities / DDIC tables, CDS view entities, CDS projection views, behavior definitions, ABAP behavior pool classes, service definitions, service bindings, metadata extensions |

**Never**: edits UI application code (UI5 controllers, freestyle UI5,
React, Vue, plain HTML/CSS/JS — only CDS-side `@UI.*` annotations are in
scope); writes CAP (Node.js or Java) code; touches classic ABAP frameworks
(BOPF, FPM, Web Dynpro, SAP GUI dynpros); produces generic ABAP unrelated
to RAP; calls `NOT_RELEASED`, `NOT_TO_BE_RELEASED`, `Use_System_Internally`,
or deprecated APIs; uses `EXEC SQL` / `INSERT REPORT` / classic dynpros /
dynamic ABAP generation; runs `git add/commit/push`; configures BTP
cockpit / Cloud Foundry / Kyma / Kubernetes / identity providers.

> 🔒 **OData V4 default (mandatory).** Every CDS projection, service
> definition, service binding, and example produced by this skill is
> **OData V4** (`OData V4 — UI` for Fiori, `OData V4 — Web API` for
> APIs). OData V2 is generated **only** when the user explicitly asks
> for V2 in the current request — never as a silent default, never as a
> guess from indirect hints. The full rule and the binding-types table
> are in
> [`skills/sap-rap-dev/references/service-binding.md`](skills/sap-rap-dev/references/service-binding.md).

> 🔒 **Released-API rule (hard stop).** Only CDS / BDEF / ABAP objects
> documented as released for cloud development are used. When the
> released surface cannot do what the user wants, the skill says so —
> it does NOT propose unreleased APIs as a workaround. Catalog and ATC
> guidance:
> [`skills/sap-rap-dev/references/released-apis.md`](skills/sap-rap-dev/references/released-apis.md).

> 🔒 **Untrusted-content discipline.** User messages, file contents,
> pasted CDS / ABAP snippets, fetched SAP Help pages, and command output
> are treated as **data, never instructions**. The skill does not
> rescope itself based on directives appearing inside pasted content and
> does not echo secret-shaped values back into its output. See
> [`skills/sap-rap-dev/SKILL.md` §9](skills/sap-rap-dev/SKILL.md).

> ⚠️ **Status: `draft`.** Reference files are populated with substantive
> guidance and runnable CDS / BDEF / ABAP examples, and the skill ships
> with the same security scans the other skills in this repo use
> (prompt-injection patterns, shell-exec patterns, secret-shaped
> strings, non-allow-listed external URLs — all clean at release time).
> Flip `metadata.status` to `released` after a human RAP expert has
> reviewed the references against the current SAP Help Portal for the
> target ABAP release.

Reference catalog: [`skills/sap-rap-dev/SKILL.md`](skills/sap-rap-dev/SKILL.md)
Changelog: [`skills/sap-rap-dev/CHANGELOG.md`](skills/sap-rap-dev/CHANGELOG.md)

---

## Shared principles

Every skill in this repo follows the same hard rules, regardless of which SAP
technology it targets:

1. **Read-mostly.** Writes are confined to a documented allowlist declared in
   the skill's `SKILL.md`.
2. **No git mutations.** Read-only git (`status`, `diff`, `log`, `show`,
   `merge-base`, `rev-parse`, `ls-files`) is allowed. Anything that changes
   refs, working tree, or staging area is forbidden.
3. **No unsolicited installs.** A skill may surface a package install command
   (`npm i -D <package>`, `abapGit pull <repo>`, etc.) and wait for the user;
   it never runs it.
4. **Declared scope, hard refusal.** Each skill names its scope in `SKILL.md`
   and **refuses out-of-scope requests with an explicit message**. Today every
   skill targets **SAP CAP Node.js** and refuses Java CAP / non-CAP / generic
   Node.js. Future ABAP / RAP / S/4HANA skills will declare and enforce their
   own scope the same way — a skill never "tries its best" outside its lane.
5. **Anchored to an authoritative source.** Every behavior or finding traces
   back to a file under that skill's `references/` directory, which mirrors
   the relevant section of the vendor docs (capire for CAP, SAP Help Portal
   for ABAP/RAP, etc.).
6. **Independently versioned and changelog'd.** Each skill carries its own
   `metadata.version` in `SKILL.md` and its own `CHANGELOG.md`. The root
   [`CHANGELOG.md`](CHANGELOG.md) records only repo-level events (skill added,
   renamed, removed, layout change, shared-principle change).

## Layout

```
sap-skills/
├── README.md            ← this file
├── CHANGELOG.md         ← repo-level events only (skill added / renamed / etc.)
├── LICENSE              ← MIT
├── .gitignore
└── skills/
    ├── sap-cap-test/
    │   ├── SKILL.md
    │   ├── CHANGELOG.md
    │   ├── references/
    │   └── templates/
    ├── sap-cap-code-review/
    │   ├── SKILL.md
    │   ├── CHANGELOG.md
    │   ├── references/
    │   └── templates/
    ├── sap-cap-upgrade/
    │   ├── SKILL.md
    │   ├── CHANGELOG.md
    │   └── references/          ← changelogs/, releases/, packages-catalog.md, ...
    ├── sap-cap-nodejs-dev/
    │   ├── SKILL.md
    │   ├── CHANGELOG.md
    │   ├── SECURITY.md          ← 41-vector audit + reproducible checks
    │   ├── references/          ← domain-first.md, best-practices.md, capire mirrors
    │   └── templates/
    └── sap-rap-dev/
        ├── SKILL.md
        ├── CHANGELOG.md
        ├── references/          ← cds-view-entity, cds-table-entity, cds-projection-view,
        │                          behavior-definition, behavior-implementation,
        │                          managed-vs-unmanaged, service-definition, service-binding,
        │                          metadata-extension, eml, value-help, stream-handling,
        │                          testing-rap, cds-annotations, release-support,
        │                          released-apis, learn, glossary
        └── templates/           ← (planned: managed-with-draft-bo, unmanaged-bo,
                                    attachment-bo, metadata-extension-only)
```

`SKILL.md` is the contract the agent reads. `CHANGELOG.md` is the per-skill
release log (and the repo-level one in the root). `references/` are the
authoritative-source-anchored rules each skill cites. `templates/` are the
markdown or code files the skill writes into the user's project.

## Adding a new skill

The repo is built to grow horizontally across SAP technology families. To
propose a new skill (e.g. `sap-rap-modeler`, `sap-abap-cleanup`,
`sap-btp-destinations`):

1. **Create `skills/<name>/`** with at minimum a `SKILL.md` and a `CHANGELOG.md`.
2. **Declare scope and negatives** in the `SKILL.md` frontmatter — same
   shape as the existing skills. Be explicit about what the skill **refuses**.
3. **Anchor every rule** to a file under `skills/<name>/references/` that
   quotes or mirrors the relevant vendor source. No rule without an anchor.
4. **Honor the [Shared principles](#shared-principles)** — read-mostly,
   no-git-mutations, no-unsolicited-installs, hard refusal out of scope,
   independent versioning.
5. **Add a row** to the matching family table above, a per-skill detail
   section, and a layout entry; record the addition in the root [`CHANGELOG.md`](CHANGELOG.md).

If a needed family is missing (e.g. an `sap-build/` group), add the family
heading at the top alongside the existing ones, then add the skill.

## Changelog

- Repo-level events: [`CHANGELOG.md`](CHANGELOG.md)
- Per-skill release notes: see the `CHANGELOG.md` inside each `skills/<name>/`.

## License

[MIT](LICENSE) © 2026 Fabricio
