# Agent Skills for SAP

A community-maintained collection of reusable AI agent skills for developers and
solution architects working with SAP technologies. This repository is designed
as a multi-skill catalog that can grow to cover additional SAP-related
capabilities over time, and it is compatible with AI coding assistants that
support the Agent Skills format.

> [!IMPORTANT]
> This is an independent community project. It is not affiliated with,
> sponsored by, or endorsed by SAP SE.

## Overview

Each skill in this repository packages procedural guidance, reference
documentation, and — where useful — accompanying Python scripts that let an
AI coding assistant safely automate a specific SAP-related workflow. Skills
are intended to supplement, not replace, existing SAP tooling, MCP servers,
and authorization controls. The default distribution model is **source
only**: no prebuilt executable is committed to the default branch.

The repository is intentionally vendor-neutral and works with any AI coding
assistant that understands the Agent Skills format, including Claude Code,
Codex, Cursor, OpenCode, and GitHub Copilot-compatible clients. Installation
support and behavior depend on the specific AI client.

## Guides

- [Register New Skills on the SAP AI Skills Library](docs/register-new-skills-on-sap-ai-skills-library.md)

## Skill Catalog

| Skill                                                    | Description                                                                                                                                                                 | Status    |
| -------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| [`sap-adt-commands`](skills/sap-adt-commands/)           | Direct SAP ADT REST operations for ABAP development workflows when existing MCP tooling does not expose the required operation.                                             | Available |
| [`sap-skills-creator`](skills/sap-skills-creator/)       | Creates, refactors, audits, and validates secure SAP-related Agent Skills that follow the Agent Skills specification and SAP AI Skills Library readiness requirements.       | Available |

Additional SAP-related skills will be added to this table as they land in the
`skills/` directory.

## Installation

The recommended way to install skills from this repository is through the
Skills CLI:

```bash
# Install every skill in the repository
npx skills add leotrinh/agent-skills-for-sap

# Install a specific skill only
npx skills add leotrinh/agent-skills-for-sap --skill sap-adt-commands

# List available skills without installing
npx skills add leotrinh/agent-skills-for-sap --list
```

Installation support depends on the AI client and the Skills CLI version. Some
clients also accept a manual copy of the skill directory into their local
skills folder — consult your client's documentation for the exact location.

## Repository Structure

Every skill follows this convention:

```text
skills/
└── <skill-name>/
    ├── SKILL.md
    ├── scripts/
    ├── references/
    └── assets/
```

Prebuilt executables are not shipped from the default branch. If a future
skill needs a compiled artifact, it will be published through GitHub
Releases with a controlled build process, not committed to `main`.

The main entry point for each skill is:

```text
skills/<skill-slug>/SKILL.md
```

`SKILL.md` contains the frontmatter, activation criteria, and high-level agent
guidance. Detailed material lives in `references/`, and supporting scripts or
templates live in `scripts/` or `assets/`.

## Security

- **Credentials must be supplied outside the skill** through environment
  variables, secret managers, or another secure local mechanism. Skills never
  request SAP passwords in an AI conversation.
- **Contributors must never commit** SAP passwords, tokens, session cookies,
  certificates, customer URLs, private system metadata, or proprietary customer
  source code.
- **Destructive SAP operations require explicit human authorization** at the
  moment the operation is about to run. Agents should not infer authorization
  from a broader task description.
- **Security vulnerabilities should be reported** according to
  [`SECURITY.md`](SECURITY.md). Do not disclose exploitable issues in a public
  issue.

## Contributing

Contributions of new SAP-related skills, improvements to existing skills, and
documentation fixes are welcome. Start with [`CONTRIBUTING.md`](CONTRIBUTING.md)
for the required repository layout, frontmatter, and quality gates.

## License

Content in this repository is licensed under the Apache License 2.0 unless a
specific file explicitly states otherwise. See [`LICENSE`](LICENSE) for the full
text.

Contributions are submitted under Apache License 2.0 unless explicitly agreed
otherwise; see [`CONTRIBUTING.md`](CONTRIBUTING.md) for details.

---

SAP and other SAP products and services mentioned in this repository are
trademarks or registered trademarks of SAP SE in Germany and other countries.
Their use does not imply any affiliation with or endorsement by SAP SE.
