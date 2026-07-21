# SAP AI Skills Library Submission

Load this file during the Prepare Submission phase. The skill helps the
user draft a registration issue; it never submits the form.

## Current Registration Model

At the time of writing, the SAP AI Skills Library uses a
**bring-your-own-repository** model:

- The skill source stays in the maintainer's public GitHub repository.
- Registration is performed by opening an issue on the SAP AI Skills
  Library GitHub repository, using the "Register a New Skill" template.
- SAP maintainers review the issue and, if approved, onboard the
  repository so that its skills appear on the SAP AI Skills Library.

Before any submission, verify that this model is still in use by
consulting the SAP AI Skills Library repository directly. Confirm the
current form fields, checklist items, and any additional constraints
before drafting the issue.

## Prerequisites for a Ready Repository

Confirm the repository meets every item below before drafting the
submission:

- Public GitHub repository.
- Each skill under `skills/<slug>/SKILL.md`.
- Every `SKILL.md` frontmatter includes at least `name` and
  `description`, and the directory name matches `name`.
- Author information available (root `README.md`, skill `README.md`, or
  skill metadata).
- License information available in a root `LICENSE` file or in package
  metadata.
- Skill discovery works against the public URL:

  ```bash
  npx skills add <owner>/<repository> --list
  ```

- No secrets, real customer hostnames, or proprietary code are present.

## Registration Content

The registration issue typically requires:

- **Issue title.** A reusable pattern:
  `Register skills from <owner>/<repository>`.
- **Repository URL.** The root URL of the public repository. Do not use
  a raw file URL.
- **Skills in this repository.** One line per skill:
  `<skill-slug> — <one-line description>`.
- **Readiness checklist.** Confirms public repository, `SKILL.md`
  presence, author information, and license information.
- **Additional context.** Target audience, purpose, capabilities,
  installation command, security posture, limitations, and project
  status.

Populate the reusable draft in
[`../assets/sap-library-submission-template.md`](../assets/sap-library-submission-template.md).

## What the Creator Skill Does and Does Not Do

The creator skill:

- Verifies the readiness checklist locally.
- Drafts the issue body from the template.
- Confirms discovery commands succeed against the public URL.
- Reports the exact next steps a human maintainer should perform.

The creator skill does not:

- Open the SAP AI Skills Library issue automatically.
- Claim SAP approval, certification, or endorsement.
- Modify the SAP AI Skills Library repository in any way.
- Promise a specific onboarding timeline.

## Sample One-Line Description

```text
<skill-slug> — <primary capability sentence>. Use when <activation
condition>.
```

Keep the sentence self-contained. Do not rely on the reader having read
the `SKILL.md`.

## Additional Context Guidance

Cover the following sections in the additional context:

- **Target audience.** Developers, architects, consultants, or agent
  users who benefit from the skill.
- **Purpose.** Primary capabilities and the gap the skill fills.
- **Installation.** The `npx skills add ...` command that installs the
  skill.
- **Security and safety.** Credential handling, TLS behaviour, human
  authorization requirements, and prebuilt executable policy.
- **Limitations.** SAP release scope, authorization requirements, and
  operational constraints.
- **Project status.** Community project, independent maintainer, and the
  non-affiliation disclaimer with SAP SE.

## Post-Submission Handling

After the issue is submitted (by the human maintainer):

- Save the issue URL.
- Monitor the issue for maintainer feedback.
- Respond in the same issue after applying requested changes.
- Do not open a duplicate registration issue while the first one is
  under review.

## Maintainer-Response Draft

```markdown
Thank you for the review.

I have applied the requested changes:

- Updated: <brief description>
- Commit: <commit URL or short hash>
- Validation: `npx skills add <owner>/<repository> --list`

Please let me know if any additional changes are required.
```

## Submission Blockers

Stop the workflow and report when:

- The repository is not public.
- One or more skills fail the readiness checklist.
- The validator returns `FAIL` on any skill in scope.
- A skill references real customer data, secrets, or hostnames.
- The maintainer cannot confirm license compatibility for embedded
  content.

Never claim readiness on the maintainer's behalf. The final decision to
submit must be made by a human.
