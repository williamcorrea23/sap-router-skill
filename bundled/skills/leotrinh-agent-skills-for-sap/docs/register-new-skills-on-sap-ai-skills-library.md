# Register New Skills on the SAP AI Skills Library

This guide explains how to register one or more community-maintained AI skills on the SAP AI Skills Library using the bring-your-own-repository model.

The skill source code remains in your own public GitHub repository. SAP maintainers review the registration issue and, when approved, onboard the repository so the skills can appear on the SAP AI Skills Library.

This guide uses `sap-adt-commands` as the sample skill.

---

## 1. Prerequisites

Before submitting, confirm that:

- The repository is public on `github.com`.
- Each skill is located at:

  ```text
  skills/<skill-slug>/SKILL.md
  ```

- Every `SKILL.md` contains valid YAML frontmatter with at least:

  ```yaml
  ---
  name: example-skill
  description: Explains what the skill does and when an agent should use it.
  ---
  ```

- The skill directory name exactly matches the `name` value.
- Author information is available in `README.md`, `package.json`, or skill metadata.
- License information is available in a root `LICENSE` file or package metadata.
- The repository can be discovered by the Skills CLI.

---

## 2. Sample Repository

This guide uses the following repository and skill:

| Item | Sample value |
|---|---|
| Repository | `leotrinh/agent-skills-for-sap` |
| Repository URL | `https://github.com/leotrinh/agent-skills-for-sap` |
| Skill slug | `sap-adt-commands` |
| Skill directory | `skills/sap-adt-commands` |
| Skill URL | `https://github.com/leotrinh/agent-skills-for-sap/tree/main/skills/sap-adt-commands` |
| Author | Leo Trinh |
| License | Apache-2.0 |
| Submission type | Community skill |

Expected structure:

```text
agent-skills-for-sap/
├── README.md
├── LICENSE
├── SECURITY.md
├── CONTRIBUTING.md
└── skills/
    └── sap-adt-commands/
        ├── SKILL.md
        ├── README.md
        ├── scripts/
        └── references/
```

---

## 3. Verify the Repository Before Submission

From the repository root, verify the current Git state:

```powershell
Set-Location "C:\Dev\git-leo\agent-skills-for-sap"

git status
git branch --show-current
git remote -v
git log -1 --oneline
```

Expected checks:

```text
Branch: main
Remote: https://github.com/leotrinh/agent-skills-for-sap.git
Working tree: clean
Latest changes: pushed
```

Verify that the required files are publicly accessible:

```text
README.md
LICENSE
SECURITY.md
CONTRIBUTING.md
skills/sap-adt-commands/SKILL.md
skills/sap-adt-commands/README.md
```

---

## 4. Verify Skill Discovery and Installation

List the skills available in the remote repository:

```bash
npx skills add leotrinh/agent-skills-for-sap --list
```

Expected result:

```text
Found 1 skill
sap-adt-commands
```

Install the sample skill:

```bash
npx skills add leotrinh/agent-skills-for-sap --skill sap-adt-commands
```

Confirm that the repository is cloned, the skill is discovered, and installation completes successfully.

---

## 5. Open the Registration Form

Sign in to GitHub and open the SAP AI Skills Library repository:

```text
https://github.com/SAP/ai-skills-library
```

Then navigate to:

```text
Issues
→ New issue
→ Register a New Skill
```

The direct issue-template URL is:

```text
https://github.com/SAP/ai-skills-library/issues/new?template=new-skill.yml
```

The current registration form uses a bring-your-own-repository model. The skill stays in your GitHub repository while SAP maintainers review and onboard it.

---

## 6. Fill in the Issue Title

Use a clear title that identifies the repository or submitted skills.

### General pattern

```text
Register skills from <owner>/<repository>
```

### Sample

```text
Register skills from leotrinh/agent-skills-for-sap
```

When submitting only one skill, a more specific title is also acceptable:

```text
Register sap-adt-commands
```

For a multi-skill repository intended to grow over time, the repository-based title is more reusable.

---

## 7. Fill in “Repository URL”

Enter the root URL of the public GitHub repository.

### General pattern

```text
https://github.com/<owner>/<repository>
```

### Sample

```text
https://github.com/leotrinh/agent-skills-for-sap
```

Do not enter:

- A direct `SKILL.md` URL.
- A raw GitHub URL.
- A local filesystem path.
- A link to only one skill folder.

---

## 8. Fill in “Skills in this repository”

List each skill using:

```text
<skill-slug> — <one-line description>
```

The description should explain:

- What the skill does.
- When an AI agent should use it.
- The main workflows or capability gaps it addresses.

### Sample

```text
sap-adt-commands — Executes SAP ADT REST API operations for ABAP development workflows, including object discovery, source management, object creation, activation, testing, transport handling, history, diff, and where-used analysis, especially when the required operation is unavailable through the currently configured MCP tools.
```

For multiple skills, place each skill on a separate line:

```text
sap-adt-commands — Executes SAP ADT REST API operations for ABAP development workflows when the required operation is unavailable through the currently configured MCP tools.

sap-cap-development — Guides agents through SAP Cloud Application Programming Model development workflows, project structure, local validation, and deployment preparation.
```

Only list skills that already exist in the public repository.

---

## 9. Complete the Readiness Checklist

Select all checklist items only after confirming them.

```text
[x] The repository is public on github.com

[x] Each skill has a skills/<slug>/SKILL.md file with name and description frontmatter

[x] Author information is available, for example in README or package.json

[x] License information is available, for example a LICENSE file or package.json
```

### Sample evidence

```text
Public repository:
https://github.com/leotrinh/agent-skills-for-sap

Skill definition:
skills/sap-adt-commands/SKILL.md

Author information:
README.md
skills/sap-adt-commands/README.md
SKILL.md metadata

License:
LICENSE
Apache-2.0
```

---

## 10. Fill in “Additional Context”

Use this section to help maintainers understand:

- Target audience.
- Purpose and scope.
- Main capabilities.
- Installation command.
- Security model.
- Limitations.
- Project ownership and disclaimer.

### Reusable template

````markdown
## Target audience

<Describe the developers, architects, consultants, or agent users who would benefit from the skill.>

## Purpose

`<skill-slug>` helps agents <describe the main capability and when it should be used>.

The skill covers:

- <Capability 1>
- <Capability 2>
- <Capability 3>

## Installation

```bash
npx skills add <owner>/<repository> --skill <skill-slug>
```

The repository and skill have been successfully discovered and installed using the Skills CLI.

## Security and safety

- <Describe credential handling.>
- <Describe TLS or network security behavior.>
- <Describe approval requirements for sensitive operations.>
- <Describe whether prebuilt executables are distributed.>

## Limitations

- <System-version or platform limitations.>
- <Authorization requirements.>
- <Operational or governance limitations.>

## Project status

This is an independent community project maintained by <author or organization>.

Repository:
https://github.com/<owner>/<repository>

Skill:
https://github.com/<owner>/<repository>/tree/main/skills/<skill-slug>

This project is not affiliated with, sponsored by, or endorsed by SAP SE.
````

### Completed sample for `sap-adt-commands`

````markdown
## Target audience

SAP ABAP developers, SAP technical consultants, solution architects, and users of AI coding agents working with SAP ADT-enabled systems.

## Purpose

`sap-adt-commands` supplements existing SAP ADT MCP tooling by providing direct access to ADT REST operations that may not be exposed by the user's currently configured MCP tools.

The skill covers:

- ABAP object discovery and inspection
- Source-code reading and updates
- Object creation and activation
- Message classes and text elements
- ATC checks and ABAP Unit tests
- Transport inspection and lifecycle operations
- Object history, diff, and where-used analysis

The skill instructs agents to prefer an appropriate existing MCP tool whenever it fully supports the requested operation, and to use the direct ADT client only when the required capability is unavailable.

## Installation

```bash
npx skills add leotrinh/agent-skills-for-sap --skill sap-adt-commands
```

The repository and skill have been successfully discovered and installed using the Skills CLI.

## Security and safety

- TLS certificate verification is enabled by default.
- Corporate CA bundles are supported for SAP systems using private certificate authorities.
- Insecure TLS requires explicit opt-in and is never used as an automatic fallback.
- Credentials are resolved through environment variables or explicit local configuration.
- Users are instructed not to paste SAP passwords, tokens, cookies, or private certificates into AI conversations.
- Sensitive operations such as source updates, deletion, activation, unlocking, transport release, transport deletion, and object movement require explicit human authorization.
- The default branch distributes inspectable Python source and does not include a prebuilt executable.

## Limitations

- Available ADT endpoints depend on the SAP system version, installed components, and system configuration.
- Users must have the required SAP development and transport authorizations.
- The skill does not bypass SAP authorization, locking, transport, or governance controls.
- Users remain responsible for validating changes in an appropriate non-production environment.

## Project status

This is an independent community project maintained by Leo Trinh.

Repository:
https://github.com/leotrinh/agent-skills-for-sap

Skill:
https://github.com/leotrinh/agent-skills-for-sap/tree/main/skills/sap-adt-commands

This project is not affiliated with, sponsored by, or endorsed by SAP SE.
````

---

## 11. Final Form Review

Before submitting, confirm that the form contains the following.

### Title

```text
Register skills from leotrinh/agent-skills-for-sap
```

### Repository URL

```text
https://github.com/leotrinh/agent-skills-for-sap
```

### Skills in this repository

```text
sap-adt-commands — Executes SAP ADT REST API operations for ABAP development workflows, including object discovery, source management, object creation, activation, testing, transport handling, history, diff, and where-used analysis, especially when the required operation is unavailable through the currently configured MCP tools.
```

### Readiness checklist

```text
All four checkboxes selected
```

### Additional context

```text
Target audience
Purpose
Capabilities
Installation
Security and safety
Limitations
Project status and disclaimer
```

Click:

```text
Create
```

---

## 12. After Submission

Save the created issue URL and monitor it for feedback.

SAP maintainers may ask for:

- Changes to `SKILL.md` frontmatter.
- A clearer one-line description.
- License clarification.
- Security changes.
- Repository structure updates.
- Documentation improvements.
- Removal or explanation of scripts or executables.

Respond in the same issue after applying changes.

### Sample maintainer-response comment

```markdown
Thank you for the review.

I have applied the requested changes:

- Updated: `<brief description>`
- Commit: `<commit URL or short hash>`
- Validation: `npx skills add <owner>/<repository> --list`

Please let me know if any additional changes are required.
```

Do not open a duplicate registration issue while the first one is under review.

---

## 13. Verify the Published Listing

After maintainers confirm onboarding, open:

```text
https://skills.cloud.sap
```

Search for the skill slug:

```text
sap-adt-commands
```

Verify:

- Skill name.
- Description.
- Author or source repository.
- Community classification.
- Repository link.
- Installation command.

Run the installation test again:

```bash
npx skills add leotrinh/agent-skills-for-sap --skill sap-adt-commands
```

---

## Quick Submission Reference

```text
Issue title:
Register skills from leotrinh/agent-skills-for-sap

Repository URL:
https://github.com/leotrinh/agent-skills-for-sap

Skill:
sap-adt-commands

Skill path:
skills/sap-adt-commands/SKILL.md

Install:
npx skills add leotrinh/agent-skills-for-sap --skill sap-adt-commands

Registration form:
https://github.com/SAP/ai-skills-library/issues/new?template=new-skill.yml
```
