# Contributing to Agent Skills for SAP

Thank you for considering a contribution to this repository. This document
describes the layout, quality expectations, and safety requirements for new
skills, updates to existing skills, and documentation improvements.

## Repository Layout

New skills must be placed at:

```text
skills/<skill-slug>/SKILL.md
```

A typical skill directory looks like this:

```text
skills/<skill-slug>/
├── SKILL.md
├── README.md          # optional but recommended for human readers
├── scripts/           # optional executable helpers
├── references/        # detailed documentation loaded on demand
└── assets/            # optional templates, images, or other resources
```

Do not add a second copy of a skill outside `skills/`. Do not create empty
placeholder directories.

## Skill Naming

Each skill must follow these naming rules:

- Lowercase ASCII letters, digits, and hyphens only.
- Maximum 64 characters.
- No leading or trailing hyphen.
- No consecutive hyphens.
- The `name` field in the frontmatter must exactly match the parent directory
  name.

Examples of acceptable names: `sap-adt-commands`, `sap-cap-service-generator`,
`btp-destination-helper`.

## Required Frontmatter

Every `SKILL.md` must start with valid YAML frontmatter. At minimum:

```yaml
---
name: example-skill
description: Explains what the skill does and when an agent should use it.
---
```

Recommended additional fields:

```yaml
license: Apache-2.0
compatibility: >-
  Describe runtime prerequisites, network requirements, and required tooling.
metadata:
  author: Your Name
  version: "1.0.0"
  category: sap-abap
  repository: <owner>/<repo>
```

All values under `metadata` should be quoted strings, including version
numbers, to avoid YAML type coercion issues (for example `"1.0.0"` rather than
`1.0.0`).

## Scope and Quality

Each skill should:

- Solve a coherent and repeatable task.
- Clearly state when the skill should activate and when it should not.
- Prefer procedural, step-by-step guidance over general educational content.
- Use specific defaults instead of listing many equal alternatives.
- Keep the main `SKILL.md` under 500 lines where practical. Aim for 250 to 400
  lines.
- Move detailed API and command documentation into `references/`.
- Reference all supporting files with relative paths from the skill root.
- Document script dependencies explicitly, including a `requirements.txt` or
  equivalent when third-party packages are needed.
- Include helpful error messages with actionable hints.
- Avoid hidden network calls, telemetry, or unrelated side effects.

## Security Requirements

Contributors must not include:

- Secrets of any kind.
- Real SAP credentials, usernames, or client identifiers tied to a specific
  customer system.
- Customer system URLs or SID information.
- Session cookies, personal access tokens, bearer tokens, or API keys.
- Private certificates or key material.
- Proprietary customer source code.
- Prebuilt executables committed to the default branch. Skills must ship
  as source (Python, TypeScript, shell, etc.). If a future skill needs an
  official compiled artifact, publish it through GitHub Releases with a
  controlled build process instead of committing the binary. A build
  configuration file (for example a PyInstaller `.spec`) is fine because
  it does not produce an executable at install time.
- Commands or prompts intentionally designed to bypass human approval for
  destructive actions.

Destructive operations must:

- Be clearly identified in the skill documentation.
- Require explicit human authorization immediately before execution.
- Avoid interpreting general implementation requests as authorization to
  delete or release production objects.
- Prefer dry-run or read-only inspection where possible.

## Pull Request Checklist

Before opening a pull request, please confirm the following:

- [ ] The skill lives under `skills/<skill-slug>/` with the correct layout.
- [ ] Frontmatter is valid YAML and starts on line 1.
- [ ] `name` in frontmatter matches the parent directory name.
- [ ] `description` clearly explains what the skill does and when to use it.
- [ ] No secrets, credentials, or private system information are included.
- [ ] All internal documentation links resolve to existing files.
- [ ] Scripts compile or pass their local checks (for Python:
      `python -m py_compile scripts/<file>.py`).
- [ ] Destructive actions are guarded and clearly documented.
- [ ] The root `README.md` skill catalog is updated when adding a new skill.
- [ ] License compatibility is confirmed for any third-party content.

## Contributor Licensing

Unless explicitly agreed otherwise, all contributions to this repository are
submitted under the terms of the Apache License 2.0. No separate Contributor
License Agreement is required. See [`LICENSE`](LICENSE) for the full license
text.

## Community Expectations

- Keep pull requests focused and reasonably sized.
- Write commit messages that describe the change and its motivation.
- Be respectful of reviewers and other contributors.
- If in doubt about a design decision, open an issue to discuss before
  investing significant time.
