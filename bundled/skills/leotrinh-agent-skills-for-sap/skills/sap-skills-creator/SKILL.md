---
name: sap-skills-creator
description: >-
  Creates, refactors, audits, and validates SAP-related Agent Skills from
  project knowledge, completed engineering tasks, runbooks, source code, or
  existing skill drafts. Use when a team needs a secure, well-scoped,
  triggerable skill that follows the Agent Skills specification, progressive
  disclosure, repository conventions, and SAP AI Skills Library readiness
  requirements. Do not use to write generic SAP tutorials, invent SAP APIs,
  or publish skills automatically.
license: Apache-2.0
compatibility: >-
  Requires filesystem access to a skill repository. Web research may be
  needed for current SAP product documentation and current Agent Skills or
  SAP AI Skills Library requirements. No SAP system access is required.
metadata:
  author: Leo Trinh
  version: "1.0.0"
  category: sap-tooling
  repository: leotrinh/agent-skills-for-sap
---

# SAP Skills Creator

Procedural guidance for producing high-quality SAP-related Agent Skills. The
skill turns real engineering knowledge into a scoped, secure, validated
skill folder — never a vague SAP encyclopedia.

## Purpose

Take verified project knowledge (a runbook, a completed task, code, an API
spec, review feedback) and produce a triggerable Agent Skill that:

- Solves one coherent, repeatable SAP-related task.
- States exactly when it should activate.
- Uses procedures instead of vague declarations.
- Handles credentials, TLS, destructive operations, and reporting safely.
- Passes structural and security validation before review.

## When to Use

Activate this skill when any of the following is true:

- A team wants to package a completed SAP engineering task as a reusable
  skill.
- An existing skill is too large, vague, insecure, or hard to trigger.
- A skill folder needs an independent structural, security, and trigger
  audit.
- A new skill must be integrated into a multi-skill repository with a
  catalog, license, and security policy.
- A skill must be prepared for SAP AI Skills Library registration.

## When Not to Use

Do not activate this skill for:

- Writing generic SAP tutorials or encyclopedic product overviews.
- Fixing a single defect in the target SAP codebase.
- Running SAP operations directly against a live system.
- Publishing, tagging, or registering a skill automatically.
- Producing prebuilt executables.
- Replacing domain expertise that has not been verified.

## Core Principles

1. **Start from real expertise.** Reject vague prompts such as "create a
   complete skill about all of SAP BTP." Narrow the scope before writing.
2. **Design a coherent unit.** One responsibility, clear inputs, clear
   outputs, clear activation, composable with other skills.
3. **Prefer procedures.** Replace vague declarations ("follow best
   practices") with sequences, defaults, decision criteria, and stop
   conditions.
4. **Use progressive disclosure.** Keep `SKILL.md` focused, move detail to
   `references/`, put templates in `assets/`, put deterministic operations
   in `scripts/`.
5. **Match control to risk.** Higher-risk operations require preconditions,
   dry-run, human authorization, and explicit reporting.
6. **Never invent SAP APIs.** Do not fabricate endpoints, authorization
   objects, CDS entities, BTP service plans, destination properties, ADT
   commands, CAP APIs, Fiori annotations, or Integration Suite
   capabilities.
7. **Public releases require sanitization.** Remove customer data, real
   hostnames, secrets, and proprietary code before public distribution.

Load [references/skill-design.md](references/skill-design.md) for the
detailed design framework.

## Operating Modes

Choose an explicit mode at the start of the workflow. Do not switch modes
silently.

| Mode | Trigger | Output |
|------|---------|--------|
| **Create** | No skill exists yet | New `skills/<slug>/` folder + validation report |
| **Refactor** | A skill exists but is oversized, vague, insecure, or poorly organized | Reorganized skill + change report |
| **Audit** | A skill exists and only a review is requested | Findings report; no file writes |
| **Repository integration** | A skill must be wired into a multi-skill repository | Updated catalog, tests, and repository files |
| **Submission preparation** | A skill will be registered with the SAP AI Skills Library | Registration payload draft; no submission |

Mode-specific rules live in
[references/skill-design.md](references/skill-design.md) and
[references/repository-integration.md](references/repository-integration.md).

## Required Inputs

Before generating anything, capture or infer:

- Skill objective and target users.
- Target agents or clients.
- SAP product or technology in scope.
- The repeatable workflow (inputs, steps, outputs).
- Positive and negative activation triggers.
- Required tools, credentials, and network access.
- Read, write, and destructive operations.
- Expected failure modes.
- Source materials (task history, runbook, code, docs, spec).
- Distribution target (internal team or public).
- Repository target and license.
- Validation approach.

When the source materials answer these, inspect them first. Ask the user
only about gaps that block a safe design. Priority order is:

1. Objective and workflow.
2. Source expertise.
3. Risk and credentials.
4. Inputs and outputs.
5. Distribution target.
6. Validation.

The full interview protocol is in
[references/discovery-and-scoping.md](references/discovery-and-scoping.md).

## Workflow

Execute the phases in order. Do not skip a phase, and do not merge phases
just because the user asked for speed.

```text
Discover → Scope → Research → Design → Generate → Security review →
Validate → Evaluate → Integrate → Prepare submission
```

## Phase 1: Discover the Source Expertise

Load [references/discovery-and-scoping.md](references/discovery-and-scoping.md).

1. Identify the concrete source of expertise: completed task, runbook,
   code, API doc, review notes, incident log.
2. Confirm the workflow is repeatable and not a one-off fix.
3. Extract the actual steps that were taken, the tools used, and the
   decisions that mattered.
4. List the failure modes that were encountered or are known.

Stop and clarify when there is no verified source of expertise. Generic
LLM knowledge alone is not a valid source.

## Phase 2: Scope the Skill

1. Write one problem statement:

   ```text
   This skill helps <target user or agent> perform <repeatable task> in
   <context>, especially when <trigger condition>.
   ```

2. Draft the proposed skill slug (lowercase, hyphenated, ≤ 64 characters).
3. Fill in the requirements template
   ([assets/skill-requirements-template.md](assets/skill-requirements-template.md))
   with the captured inputs.
4. Reject the scope when it is too broad ("all of SAP BTP"), too narrow
   ("fix this one error"), or overlaps with an existing skill without
   reason.

## Phase 3: Research and Verify

Load [references/sap-domain-research.md](references/sap-domain-research.md).

1. Prefer official SAP sources for technical facts: SAP Help Portal, SAP
   Developers, SAP GitHub organisations, official API documentation, and
   release notes.
2. Distinguish official product behaviour, community convention, repository
   convention, and inference.
3. Record any version-sensitive assumptions.
4. Do not invent SAP endpoints, authorization objects, CDS entities, BTP
   service plans, destination properties, ADT commands, CAP APIs, Fiori
   annotations, or Integration Suite capabilities.
5. Stop and report unresolved conflicts between sources.

## Phase 4: Design the Skill

Load [references/skill-design.md](references/skill-design.md).

1. Decide the responsibility boundary. One skill, one job.
2. Choose the operating modes the skill itself will expose (for example
   "read-only inspect" versus "write and activate").
3. Draft decision trees for the main branches of the workflow.
4. Choose defaults instead of listing many equivalent alternatives.
5. Design an explicit output contract: what the agent will report at the
   end of a successful run and after each stop condition.
6. Classify the skill by risk. Load
   [references/security-review.md](references/security-review.md) for the
   risk taxonomy.

## Phase 5: Generate the Skill Package

Load [references/progressive-disclosure.md](references/progressive-disclosure.md)
and [references/frontmatter-and-triggering.md](references/frontmatter-and-triggering.md).

1. Create the directory:

   ```text
   skills/<slug>/
   ├── SKILL.md
   ├── README.md
   ├── references/
   ├── assets/
   └── scripts/
   ```

2. Write frontmatter first. Required fields:

   ```yaml
   ---
   name: <slug>
   description: >-
     <capability>. Use when <activation conditions>. Do not use for
     <important exclusions>.
   license: <license>
   compatibility: <runtime prerequisites>
   metadata:
     author: <name>
     version: "<version>"
     category: <category>
     repository: <owner/repo>
   ---
   ```

3. Keep `SKILL.md` focused. Target 300–450 lines. Hard limit 500 lines.
4. Move detailed technical documentation, command catalogues, and long
   procedures into focused reference files under `references/`.
5. Put reusable templates and static resources in `assets/`.
6. Put deterministic operations (validators, formatters, parsers) in
   `scripts/`. Load
   [references/scripts-and-resources.md](references/scripts-and-resources.md)
   before adding any script.
7. Use relative links from the skill root. Avoid deeply nested reference
   chains.

## Phase 6: Security Review

Load [references/security-review.md](references/security-review.md).

Walk the skill through every category:

- Credentials and secrets.
- Network behaviour.
- Filesystem behaviour.
- Shell and subprocess behaviour.
- SAP-specific operational risks.
- Dependency and supply-chain review.
- Public-release review.

Reject the skill until each finding is either fixed or explicitly
documented as accepted risk.

## Phase 7: Validate

Load [references/validation-and-evaluation.md](references/validation-and-evaluation.md).

Run the validator against the target skill:

```powershell
python .\skills\sap-skills-creator\scripts\validate_skill.py `
  .\skills\<slug> `
  --repository-root .
```

The validator checks structure, frontmatter, size, links, and security
heuristics. Read the human-readable output first, then rerun with `--json`
if a machine-readable payload is needed:

```powershell
python .\skills\sap-skills-creator\scripts\validate_skill.py `
  .\skills\<slug> `
  --repository-root . `
  --json
```

Exit codes:

- `0` — valid, no failures.
- `1` — validation failures.
- `2` — invalid invocation or internal error.

Treat every `FAIL` as blocking. Triage each `WARN` explicitly: fix, or
document the reason it is intentional.

## Phase 8: Evaluate Against Real Tasks

Load [references/validation-and-evaluation.md](references/validation-and-evaluation.md).

Structural validation does not prove the skill activates correctly. Run a
behavioural evaluation:

1. Craft at least three positive trigger prompts derived from real user
   intents.
2. Craft at least three negative trigger prompts (topics the skill should
   ignore).
3. Run each prompt through the AI client that will consume the skill.
4. Assess: trigger precision, instruction adherence, tool selection,
   safety behaviour, output correctness, failure reporting, and context
   efficiency.
5. Revise the description, structure, or references until the prompts
   activate the skill for positive cases and leave it dormant for negative
   cases.

At least one execute-review-revise cycle is mandatory. Record the results
in [assets/skill-review-report-template.md](assets/skill-review-report-template.md).

## Phase 9: Integrate Into the Repository

Load [references/repository-integration.md](references/repository-integration.md).

1. Confirm the skill lives at `skills/<slug>/SKILL.md`.
2. Update the root `README.md` skill catalog with a concise row.
3. Confirm the repository has a root `LICENSE`, `SECURITY.md`, and
   `CONTRIBUTING.md` where the convention requires them.
4. Add unit tests for any script under `tests/`.
5. Run local discovery to confirm the skill can be found:

   ```powershell
   npx skills add . --list
   ```

6. Do not commit, push, tag, publish, or open GitHub issues.

## Phase 10: Prepare Submission

Load [references/sap-library-submission.md](references/sap-library-submission.md).

For SAP AI Skills Library preparation:

1. Fill in
   [assets/sap-library-submission-template.md](assets/sap-library-submission-template.md).
2. Verify the repository is public and the skill discovery command
   succeeds against the public URL.
3. Draft the registration issue body without submitting it.
4. Hand the draft to a maintainer for review.

Do not submit the registration form. Do not claim SAP approval, SAP
certification, or SAP endorsement.

## Output Contract

At the end of a successful run, report:

- Mode used (Create, Refactor, Audit, Repository integration, Submission
  preparation).
- Skill slug and directory.
- Files created, modified, or removed with paths.
- Root files touched (typically `README.md`).
- Frontmatter summary (name, description length, compatibility length,
  metadata keys).
- Validator result summary (`PASS` / `WARN` / `FAIL` counts).
- Behavioural evaluation summary (positive prompts, negative prompts,
  activation results).
- Outstanding blockers, warnings, and informational findings, kept
  separate.
- Suggested but unexecuted next steps (commit, submission, etc.).

Use [assets/skill-review-report-template.md](assets/skill-review-report-template.md)
for structured reports.

## Failure and Stop Conditions

Stop the workflow and report when:

- The user cannot produce a verified source of expertise.
- The scope stays broader than one coherent unit after clarification.
- The validator returns `FAIL` and the cause is not immediately fixable.
- A finding classified as **Critical** in the review report is
  unresolved.
- The user asks the skill to invent SAP APIs, publish automatically, or
  bypass human authorization for destructive operations.
- The user requests inclusion of secrets, real customer hostnames, or
  proprietary source code in a public skill without sanitization and
  authorization.

Never claim a skill is ready, secure, SAP-certified, or SAP-approved on
behalf of any project or organization.

## Bundled Resources

- [`references/discovery-and-scoping.md`](references/discovery-and-scoping.md)
- [`references/skill-design.md`](references/skill-design.md)
- [`references/frontmatter-and-triggering.md`](references/frontmatter-and-triggering.md)
- [`references/progressive-disclosure.md`](references/progressive-disclosure.md)
- [`references/sap-domain-research.md`](references/sap-domain-research.md)
- [`references/security-review.md`](references/security-review.md)
- [`references/scripts-and-resources.md`](references/scripts-and-resources.md)
- [`references/validation-and-evaluation.md`](references/validation-and-evaluation.md)
- [`references/repository-integration.md`](references/repository-integration.md)
- [`references/sap-library-submission.md`](references/sap-library-submission.md)
- [`references/review-checklists.md`](references/review-checklists.md)
- [`assets/skill-requirements-template.md`](assets/skill-requirements-template.md)
- [`assets/skill-review-report-template.md`](assets/skill-review-report-template.md)
- [`assets/sap-library-submission-template.md`](assets/sap-library-submission-template.md)
- [`scripts/validate_skill.py`](scripts/validate_skill.py)

## Completion Checklist

Before reporting a skill complete, verify:

- [ ] Mode used is explicit in the report.
- [ ] `SKILL.md` frontmatter passes structural validation.
- [ ] `SKILL.md` is between 300 and 450 lines (hard limit 500).
- [ ] Every referenced file exists and is linked from `SKILL.md` or from
      another linked file.
- [ ] The security review categories were walked and the findings are
      recorded.
- [ ] The validator was executed and its report was retained.
- [ ] At least one execute-review-revise behavioural evaluation cycle was
      completed.
- [ ] Root repository files were updated only where necessary.
- [ ] No secrets, customer data, or proprietary code were introduced.
- [ ] No commit, push, tag, publish, or issue creation was performed
      automatically.
