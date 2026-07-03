---
name: claude-abap-skills
description: Claude ABAP development skills (matt1as/claude-abap-skills). Reference for syntax highlighting, linting rules, and quick object creation templates.
trigger:
  keywords: [abaplint, abap lint, lint rules, abap syntax check, abap templates, create abap object, quick object creation, abap ci, lint report]
  intent: Lint ABAP sources locally or in CI, apply lint rule categories, and create ABAP objects quickly via abap-mcp tools or repo templates
prerequisites:
  - Node.js with repo devDependencies installed (npm install pulls @abaplint/cli)
  - ABAP sources under templates/**/*.abap (lint target of all abap:* scripts)
  - abap-mcp MCP server connected (for object creation and syntax checks on a live system)
  - SAP ADT access via arc-1 or abap-mcp (only for activate/deploy steps)
---

# Claude ABAP Skills — Lint, Rules, Quick Object Creation

Adapted from matt1as/claude-abap-skills for this orchestrator: abaplint wiring, rule
categories, and fast ABAP object scaffolding via abap-mcp tools and repo templates.

## 1. Scope

| Area | Coverage |
| --- | --- |
| **Linting** | abaplint over `templates/**/*.abap`, local + CI + gates |
| **Rules** | Syntax, security, and Clean ABAP rule categories |
| **Object creation** | abap-mcp create_* tools against a live SAP system |
| **Templates** | 4 ready `.abap` sources in `templates/` (ZROUTER family) |

## 2. Lint Workflow (Local)

```bash
# Static analysis of all ABAP templates
npm run abap:lint

# Auto-fix what abaplint can fix (pretty-print, keywords case)
npm run abap:lint:fix

# Watch mode while editing templates/
npm run abap:lint:watch

# Lint only files changed since last commit
npm run abap:lint:changed
```

No `abaplint.json` exists at the repo root — abaplint runs with its default ruleset.
To pin rules, generate a config once and commit it:

```bash
npx abaplint --default > abaplint.json
```

## 3. Lint in CI and Review Gates

```bash
# JSON report for CI consumption (writes abaplint-report.json)
npm run abap:lint:ci

# Full review: lint + security gate + clean code gate
npm run abap:review

# Pre-release transport gate (blocks on findings)
npm run abap:review:transport

# HTML report (writes abap-review-report.html)
npm run abap:review:report
```

`abap:review:*` pipes abaplint JSON into `scripts/abap-review-gate.js` with
`--mode security|clean|transport`. Run `abap:review:transport` before releasing
any transport; see the abap-code-review skill for the 9-dimension GO/NO-GO gate.

## 4. Lint Rule Categories

| Category | Example rules | Gate |
| --- | --- | --- |
| **Syntax** | parser errors, obsolete statements, unknown types | abap:lint |
| **Security** | SQL injection sinks, hardcoded credentials, missing AUTHORITY-CHECK | abap:review:security |
| **Clean code** | method length, naming conventions, unused variables, pretty-print | abap:review:clean |

Fix order: syntax first (everything else is noise until it parses), then security,
then clean code.

## 5. Quick Object Creation via abap-mcp

Use abap-mcp MCP tools to scaffold objects directly on the connected SAP system:

```text
create_abap_class        → new global class (pass name, description, package)
create_abap_program      → new report/program
create_abap_interface    → new global interface
create_function_group    → new function group container
create_database_table    → new DDIC table
create_cds_view          → new CDS DDL source
```

Standard flow after creation:

```text
run_syntax_check         → validate source before activation
activate_abap_object     → activate (fails on syntax errors)
run_unit_tests           → execute ABAP Unit for the object
run_atc_check            → ATC quality/cloud-readiness check
```

Always syntax-check before activating; activation of a broken object leaves it
inactive and pollutes the inactive object list.

## 6. Template Usage

Four templates ship in `templates/` and are the lint target set:

| Template | Purpose |
| --- | --- |
| `ZROUTER_DISPATCH.abap` | ZROUTER RFC dispatch handler skeleton |
| `ZROUTER_DB_TABLES.abap` | ZROUTER DDIC table definitions |
| `ZROUTER_CODE_SEARCH.abap` | Code search helper for ZROUTER |
| `ZCL_ABAP_REPL_V2.abap` | ABAP REPL class (snippet execution) |

```bash
# Copy a template as starting point, then lint before deploying
cp templates/ZROUTER_DISPATCH.abap templates/ZMY_HANDLER.abap
npm run abap:lint
```

Deploy edited templates via abap-mcp `write_abap_source` + `activate_abap_object`,
or via `npm run zrouter:install:force` for the ZROUTER set.

## Pitfalls

- **`abap:lint` passes but code fails in SAP** → Cause: abaplint is static and offline; it cannot see DDIC or released-API violations. Solution: run abap-mcp `run_syntax_check` and `run_atc_check` on the live system before transport.
- **Glob matches nothing on Windows shells** → Cause: `templates/**/*.abap` expansion differs per shell. Solution: run through npm scripts (abaplint expands the glob itself), not by pasting the pattern into PowerShell.
- **`abap:lint:fix` rewrites more than expected** → Cause: auto-fix applies all fixable default rules (case, pretty-print). Solution: commit before running fix; review the diff with `git diff templates/`.
- **New rule expectations not enforced** → Cause: no `abaplint.json` in repo, so defaults apply. Solution: generate one with `npx abaplint --default > abaplint.json`, trim to desired rules, commit.
- **create_* tool fails with package error** → Cause: target package missing or not modifiable. Solution: create it first (abap-mcp `create_package`) or use `$TMP` for throwaway objects.

## Verification

```bash
# Lint must exit 0 on the shipped templates
npm run abap:lint

# CI report generated and valid JSON
npm run abap:lint:ci
node -e "JSON.parse(require('fs').readFileSync('abaplint-report.json'))"

# Transport gate returns GO
npm run abap:review:transport
```

On a live system: `run_syntax_check` on the created object returns no errors and
`activate_abap_object` reports active status.

## Related

- **clean-abap** — Clean ABAP style rules behind the `abap:review:clean` gate
- **abap-code-patterns** — BAPI/RFC patterns and ZROUTER handler implementation
- **abap-code-review** — 9-dimension pre-release GO/NO-GO review (wraps `abap:review:transport`)
- **Source repo** — matt1as/claude-abap-skills (upstream skill collection)
