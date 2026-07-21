# SAP Skills Creator

Agent Skill for turning verified SAP engineering knowledge into a scoped,
secure, validated skill folder. The material below is for human readers.
The agent-facing entry point is [`SKILL.md`](SKILL.md).

> [!IMPORTANT]
> This is part of an independent community project. It is not affiliated
> with, sponsored by, or endorsed by SAP SE. The skill does not claim SAP
> certification or approval on behalf of any project.

## Overview

`sap-skills-creator` guides an AI coding agent — and the humans working
with it — through the ten-phase workflow required to produce a
high-quality SAP-related Agent Skill:

```text
Discover → Scope → Research → Design → Generate → Security review →
Validate → Evaluate → Integrate → Prepare submission
```

The skill assumes that real expertise already exists (a completed task,
a runbook, code, an API spec, a review) and shapes that expertise into a
skill folder that follows the Agent Skills specification, progressive
disclosure, and the conventions of this repository.

## What It Creates

A finished run produces:

- `skills/<slug>/SKILL.md` — agent instructions.
- `skills/<slug>/README.md` — human onboarding.
- `skills/<slug>/references/*.md` — focused, load-on-demand documentation.
- `skills/<slug>/assets/*` — reusable templates and checklists.
- `skills/<slug>/scripts/*` — deterministic operations, when justified.
- Updated repository files (root `README.md` catalog entry, tests) where
  the convention requires them.

## When to Use It

Activate this skill when:

- A team wants to package a real, completed SAP engineering task as a
  reusable Agent Skill.
- An existing skill has grown oversized, vague, insecure, or hard to
  trigger.
- A skill folder needs an independent structural, security, and
  triggering audit.
- A skill must be integrated into a multi-skill repository with a
  catalog, license, and security policy.
- A skill must be prepared for SAP AI Skills Library registration.

Do not use it to write generic SAP tutorials, to invent SAP APIs, to run
SAP operations, or to publish skills automatically.

## Workflow

Every mode follows the same ten phases. The mode determines which files
are created, refactored, or only reviewed.

- **Create.** Start from a verified source of expertise and produce a
  new `skills/<slug>/` folder.
- **Refactor.** Take an existing oversized or poorly organised skill and
  reshape it into progressive disclosure without losing intended
  behaviour.
- **Audit.** Read-only review that produces findings and recommendations.
- **Repository integration.** Wire a skill into a multi-skill
  repository — catalog entry, tests, discovery.
- **Submission preparation.** Draft the SAP AI Skills Library
  registration content without submitting anything.

Detailed instructions per phase live in [`SKILL.md`](SKILL.md) and the
[references](references/) directory.

## Installation

Through the Skills CLI (once this skill is available in the repository):

```bash
npx skills add leotrinh/agent-skills-for-sap --skill sap-skills-creator
```

Installation support depends on the AI client. Some clients also accept
a manual copy of the skill directory into their local skills folder.

## Example Requests

Prompts that reliably activate this skill:

```text
Create an Agent Skill from this SAP CAP deployment runbook.
Audit our SAP Integration Suite skill for security and structure.
Refactor this 900-line SKILL.md using progressive disclosure.
Prepare this new SAP ABAP skill for our multi-skill repository.
Generate the SAP AI Skills Library registration context, but do not
submit it.
```

Prompts that should not activate this skill:

```text
Explain what SAP BTP is.
Fix this single Java syntax error.
Give me a generic summary of SAP Integration Suite.
```

## Validation

The bundled validator checks structure, frontmatter, size, links,
progressive disclosure, and security heuristics. It uses the Python
standard library only and never contacts the network.

```powershell
python .\skills\sap-skills-creator\scripts\validate_skill.py `
  .\skills\<slug> `
  --repository-root .
```

Options:

- `--json` — machine-readable output.
- `--strict` — treat warnings as failures for the exit code.
- `--repository-root <path>` — enable repository-readiness checks.

Exit codes:

- `0` — valid, no failures.
- `1` — validation failures.
- `2` — invalid invocation or internal error.

Unit tests live at
[`tests/test_sap_skills_creator_validator.py`](../../tests/test_sap_skills_creator_validator.py).
Run the repository test suite from the repository root:

```powershell
python -m unittest discover -s .\tests -v
```

## Security Model

- The validator never contacts the network and never emits secret
  values.
- The workflow requires the created skill to resolve credentials outside
  the AI conversation.
- Destructive SAP operations designed inside a generated skill must
  follow the
  inspect–confirm–preview–authorize–execute–verify–report sequence.
- Public-release preparation includes license, sanitisation, and
  non-affiliation checks.
- No prebuilt executable is distributed from the default branch.

Full security guidance lives in
[`references/security-review.md`](references/security-review.md) and the
repository-level [`SECURITY.md`](../../SECURITY.md).

## Repository Integration

Guidance for wiring a new skill into a multi-skill repository is in
[`references/repository-integration.md`](references/repository-integration.md).
Highlights:

- Every skill lives at `skills/<slug>/SKILL.md`.
- The root `README.md` catalog table is the single source of truth for
  skill discovery in the browser.
- Root `LICENSE`, `SECURITY.md`, and `CONTRIBUTING.md` must be present
  and current.
- Tests for scripts live under `tests/` in the repository, using the
  existing framework.

## SAP AI Skills Library Preparation

Guidance for preparing an SAP AI Skills Library registration is in
[`references/sap-library-submission.md`](references/sap-library-submission.md).
The template in
[`assets/sap-library-submission-template.md`](assets/sap-library-submission-template.md)
provides the reusable fields for the registration issue.

The creator skill never submits the registration issue. A human
maintainer opens the issue on the SAP AI Skills Library repository.

## Limitations

- The skill does not carry broad SAP product knowledge. It requires a
  verified source of expertise.
- The skill does not replace SAP domain review. Every SAP-specific claim
  in a generated skill must be verified against an official source.
- The skill does not certify correctness or safety.
- The skill does not publish, tag, or submit anything automatically.
- The skill does not connect to an SAP system.
- The skill does not imply any affiliation with or endorsement by SAP SE.

## Documentation

- Agent-facing guide: [`SKILL.md`](SKILL.md).
- References: [`references/`](references/).
- Templates: [`assets/`](assets/).
- Repository-level docs: [`../../README.md`](../../README.md),
  [`../../SECURITY.md`](../../SECURITY.md),
  [`../../CONTRIBUTING.md`](../../CONTRIBUTING.md).

## License

Apache License 2.0. See [`../../LICENSE`](../../LICENSE) for the full
text.

## Disclaimer

Public skills produced with this creator require sanitisation and legal
review appropriate to the maintaining team before public release. SAP and
other SAP products and services referenced in generated skills are
trademarks or registered trademarks of SAP SE. Their use does not imply
any affiliation with or endorsement by SAP SE.
