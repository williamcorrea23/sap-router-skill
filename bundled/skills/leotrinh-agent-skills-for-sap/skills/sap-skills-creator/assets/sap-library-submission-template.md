# SAP AI Skills Library Submission Draft

Reusable placeholders for the SAP AI Skills Library "Register a New
Skill" issue. Fill each field with concrete values, then hand the draft
to a human maintainer for review and submission.

The creator skill does not submit this issue. It only prepares the
content.

## Issue Title

```text
Register skills from <owner>/<repository>
```

For a single-skill submission the following title is also acceptable:

```text
Register <skill-slug>
```

## Repository URL

```text
https://github.com/<owner>/<repository>
```

Use the repository root URL. Do not link to a raw file, a subdirectory,
or a private mirror.

## Skills in This Repository

One line per skill, using the pattern:

```text
<skill-slug> — <one-line description covering capability, activation, and
important exclusion when useful>
```

Example:

```text
sap-adt-commands — Executes SAP ADT REST API operations for ABAP
development workflows, including object discovery, source management,
object creation, activation, testing, transport handling, history,
diff, and where-used analysis, especially when the required operation
is unavailable through the currently configured MCP tools.
```

For multi-skill repositories, list each skill on its own line.

## Readiness Checklist

Confirm all four items before submission:

- [ ] The repository is public on `github.com`.
- [ ] Each skill has a `skills/<slug>/SKILL.md` with valid `name` and
      `description` frontmatter.
- [ ] Author information is available (root `README.md`, skill
      `README.md`, or skill metadata).
- [ ] License information is available (root `LICENSE` or package
      metadata).

Include short evidence links or paths in the issue body when the
template requests them.

## Additional Context

Use the following template. Replace every placeholder before submission.

````markdown
## Target audience

<Describe the developers, architects, consultants, or agent users who
would benefit from the skill.>

## Purpose

`<skill-slug>` helps agents <describe the primary capability and when it
should be used>.

The skill covers:

- <Capability 1>
- <Capability 2>
- <Capability 3>

## Installation

```bash
npx skills add <owner>/<repository> --skill <skill-slug>
```

The repository and skill have been successfully discovered and installed
using the Skills CLI.

## Security and safety

- <Credential handling summary>
- <TLS or network security summary>
- <Approval requirements for sensitive operations>
- <Prebuilt executable policy>

## Limitations

- <SAP release scope and versioning>
- <Authorization requirements>
- <Operational or governance constraints>

## Project status

This is an independent community project maintained by <author or
organization>.

Repository:
https://github.com/<owner>/<repository>

Skill:
https://github.com/<owner>/<repository>/tree/main/skills/<skill-slug>

This project is not affiliated with, sponsored by, or endorsed by SAP SE.
````

## Pre-Submission Verification

Before sharing the draft with the maintainer, confirm:

- Every placeholder above has been replaced.
- The skill discovery command succeeds against the public URL:

  ```bash
  npx skills add <owner>/<repository> --list
  ```

- The structural validator returns no `FAIL` for every skill listed.
- No secrets, real hostnames, SIDs, or customer identifiers appear
  anywhere in the draft.
- The non-affiliation disclaimer is present.

## Post-Submission Notes

- Save the created issue URL alongside the repository documentation
  (do not commit customer-specific issue metadata).
- Monitor the issue for maintainer feedback.
- When applying requested changes, respond in the same issue rather than
  opening a new registration issue.
