---
name: sap-claude-skills
description: SAP Claude Custom Skills collection (KEIDAI-TechTime/sap-claude-skills). Custom templates and system instructions for SAP tasks — template catalog (template_repo.py, xls_to_bapi.py), karpathy behavioral wrapper, prompt patterns for correct router dispatch, and authoring new SKILL.md files.
trigger:
  keywords: [custom skill, skill template, system instructions, prompt pattern, template catalog, seed templates, write skill, skill frontmatter, instruction stacking]
  intent: Using or authoring custom Claude skill templates and system instructions so SAP tasks are phrased, dispatched, and executed consistently through the router
prerequisites:
  - sap-router-skill repo cloned with scripts/ directory intact
  - Python 3.10+ on PATH (template_repo.py, xls_to_bapi.py, sap_router.py)
  - npm scripts available (package.json: seed, template, csv:check)
  - karpathy-guidelines skill present in .claude/skills/ (mandatory wrapper)
---

# SAP Claude Custom Skills — Templates and System Instructions

Custom skill templates and system instructions for SAP tasks (attribution: KEIDAI-TechTime/sap-claude-skills). Grounded in this repo's template machinery: ABAP snippet catalog (`template_repo.py`), BAPI CSV template generation (`xls_to_bapi.py`), the karpathy behavioral wrapper, and the SKILL.md authoring pattern that makes the router activate the right skill.

## 1. Scope

| Layer | What it provides |
| --- | --- |
| **Template catalog** | Placeholder-based ABAP snippets per module/action (`template_repo.py`) |
| **BAPI CSV templates** | Column-mapped CSV skeletons for batch BAPI input (`xls_to_bapi.py template`) |
| **System instructions** | karpathy-guidelines wrapper + caveman compression as output default |
| **Prompt patterns** | Phrasing rules so `sap_router.py` dispatches to the correct route |
| **Skill authoring** | Frontmatter pattern (trigger keywords + intent) for new SKILL.md files |

## 2. Template Catalog (template_repo.py)

Catalog of ABAP snippets with `{{PLACEHOLDER}}` slots, keyed by module + action.

```bash
# Seed starter templates for all mapped actions (MM/SD/FI/PP/...)
npm run seed                        # = python scripts/template_repo.py seed

# List catalog: id, module, action, version, line count, placeholder count
python scripts/template_repo.py list

# Add your own template from an ABAP file
python scripts/template_repo.py add --file my_bapi_call.abap \
  --module MM --action CREATE_MATERIAL --title "Material create wrapper"

# Resolve placeholders into ready-to-paste ABAP
python scripts/template_repo.py resolve --template MM_CREATE_MATERIAL \
  --values '{"HEADER":"ls_head","RETURN_STRUCT":"ls_return"}'

# Export as JSON for abapGit / nugget packaging
python scripts/template_repo.py export --template CREATE_MATERIAL --format abapgit
```

`--template` accepts a template ID prefix, `ACTION`, or `MODULE_ACTION`. Ambiguous refs list candidates instead of guessing.

## 3. BAPI CSV Templates (xls_to_bapi.py)

Generate a CSV skeleton whose columns map to BAPI fields, fill it, then validate before conversion.

```bash
# Generate CSV template for module + action
npm run template -- --output mm_material.csv --module MM --action CREATE_MATERIAL
# = python scripts/xls_to_bapi.py template ...

# Validate a filled CSV against the BAPI field mapping
npm run csv:check -- --input mm_material.csv --module MM --action CREATE_MATERIAL

# Convert validated CSV to BAPI JSON payloads
npm run convert -- --input mm_material.csv --module MM --action CREATE_MATERIAL
```

## 4. System-Instruction Layer (karpathy wrapper)

**karpathy-guidelines is the mandatory behavioral wrapper** for every SAP operation. Its 4 principles:

1. **Think** — surface assumptions before coding: BAPI parameters, transport target (DEV/QA/PRD), required auth roles, basis release. If multiple BAPIs/paths exist, present options — never pick silently.
2. **Simplify** — minimum code that solves the problem: standard BAPI over custom FM, CDS view over ABAP report for reads, no speculative abstractions.
3. **Surgical** — touch only requested objects, match existing style/naming (ZCL_ prefix, casing), transport only changed objects, remove only orphans your own change created.
4. **Goal-Verify** — define verifiable success criteria ("MATNR returned, visible in MM03") and loop until they pass: syntax check, `npm run abap:lint`, unit tests, transport consistency.

**Caveman compression is the output default**: drop articles/filler/pleasantries, fragments OK, code blocks unchanged, pattern `[thing] [action] [reason]. [next step].` Exception: security warnings and irreversible actions use full clarity.

## 5. Prompt Patterns for Router Dispatch

Phrase requests with **module + action** so the routing tree picks the right lane:

| You say | Router dispatches |
| --- | --- |
| "MM create material batch from CSV" | BAPI route (ZROUTER RFC / fallback tiers) |
| "SPRO config for pricing" | GUI route immediately (mcp-sap-gui, no ADT attempt) |
| "edit method in ZCL_HANDLER_MM" | ADT route (arc-1 primary, aibap secondary) |
| "where is X defined" / small 1-2 file edit | Caveman crew (investigator/builder/reviewer) |
| "build report from this spec" | 8-stage pipeline |

```bash
# Preview the route before executing
python scripts/sap_router.py route --action MM_CREATE_MATERIAL --module MM
python scripts/sap_router.py route --action SPRO_CONFIG

# Or via npm
npm run router -- --action MM_CREATE_MATERIAL
npm run router:gui -- --action SPRO_CONFIG      # Force GUI fallback
```

Vague prompts ("fix SAP thing") skip module/action matching and land in generic fallback — always name the module (MM/SD/FI/...) and a verb-object action.

## 6. Writing a Custom Skill Template

Skill activation is model-driven: Claude scans YAML frontmatter descriptions in `.claude/skills/*/SKILL.md`. New skills MUST follow this pattern:

```yaml
---
name: my-sap-skill                    # matches directory name exactly
description: One-line summary with the exact words users will type.
trigger:
  keywords: [6-10 lowercase phrases, tcodes, bapi names, module terms]
  intent: One sentence stating the user goal this skill serves
prerequisites:
  - Access/config the steps assume (auth, .env vars, transactions)
---
```

Body structure (max 200 lines): `# Title`, numbered `## sections` with copyable commands, `## Pitfalls` (Cause/Solution), `## Verification`, `## Related`.

**System-instruction stacking order** when a skill runs: karpathy wrapper (behavior) → caveman compression (output format) → your skill's instructions (domain steps). Skills add domain steps only — do not restate wrapper rules inside skill bodies.

After adding a skill, update ALL cross-file consistency targets: `SKILL.md` (master list), `README.md` (counts/diagrams), `scripts/healthcheck.py` (skill count threshold), `AGENTS.md`, `package.json` description.

## Pitfalls

- **`resolve` fails with KeyError** → Cause: `--values` JSON missing a `{{PLACEHOLDER}}` used by the template. Solution: run `template_repo.py list` to see placeholder count, inspect template via `export`, supply every key.
- **Seed appears to do nothing** → Cause: `seed` skips (module, action) pairs already in the repo. Solution: expected idempotence; `list` to confirm, `add` a new version to override.
- **CSV convert rejects file** → Cause: columns do not match BAPI field mapping for module/action. Solution: regenerate skeleton with `npm run template`, run `npm run csv:check` before `convert`.
- **New skill never activates** → Cause: description lacks the words users actually type, or `name` differs from directory name. Solution: put exact trigger phrases (tcodes, BAPI names) in description + keywords; keep name = folder.
- **Router picks wrong lane** → Cause: prompt omitted module or used vague verbs. Solution: phrase as "MODULE verb object" (e.g. "SD create sales order batch"); preview with `sap_router.py route`.
- **Healthcheck fails after adding a skill** → Cause: `healthcheck.py` skill-count threshold no longer matches disk count. Solution: update threshold and the other cross-file consistency targets listed in section 6.

## Verification

```bash
# Catalog seeded and listable
npm run seed
python scripts/template_repo.py list          # expect > 0 templates

# Template resolves to clean ABAP (no {{...}} left in output)
python scripts/template_repo.py resolve --template MM_CREATE_MATERIAL \
  --values '{"HEADER":"ls_h","DESCRIPTION":"ls_d","RETURN_STRUCT":"ls_r","MATERIAL_NUMBER":"lv_m","DESCRIPTION_TABLE":"lt_d"}'

# CSV template round-trip validates
npm run template -- --output /tmp/mm.csv --module MM --action CREATE_MATERIAL
npm run csv:check -- --input /tmp/mm.csv --module MM --action CREATE_MATERIAL

# New skill counted and healthy
npm run hc
```

## Related

- **karpathy-guidelines** — the mandatory 4-principle wrapper summarized in section 4
- **sap-router-skill** — master dispatch table and routing decision tree
- **run-sap-router-skill** — smoke-testing template_repo.py / xls_to_bapi.py CLIs
- **sap-bapi-integration** — BAPI call patterns the seeded templates wrap
- **caveman plugin** — compression levels and cavecrew subagent delegation
