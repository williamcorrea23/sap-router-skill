# Repository Integration

Load this file during the Integrate phase and when adding a new skill to
an existing multi-skill repository.

## Target Layout

Every skill lives at:

```text
skills/<slug>/SKILL.md
```

A healthy repository layout looks like this:

```text
<repository>/
├── README.md
├── LICENSE
├── SECURITY.md
├── CONTRIBUTING.md
├── .gitignore
├── skills/
│   ├── <slug-a>/
│   │   ├── SKILL.md
│   │   ├── README.md
│   │   ├── references/
│   │   ├── assets/
│   │   └── scripts/
│   └── <slug-b>/
│       └── ...
└── tests/
    └── test_<slug>_<scope>.py
```

Do not add a second copy of a skill outside `skills/`. Do not create
empty placeholder directories.

## Root README Catalog

Every multi-skill repository must maintain a skill catalog table in the
root `README.md`. Add one row per skill using the existing style. Keep
the description concise and mention the primary activation condition.

Example row (see the current root README for the style in use):

```text
| [`sap-skills-creator`](skills/sap-skills-creator/) | Creates, refactors, audits, and validates SAP-related Agent Skills that follow the Agent Skills specification and SAP AI Skills Library readiness requirements. | Available |
```

Do not duplicate long explanations from the skill's own `README.md` into
the root README.

## Repository Files to Check

Confirm the following exist and are current:

- **`README.md`** — includes the skill catalog row.
- **`LICENSE`** — matches the license declared in each skill.
- **`SECURITY.md`** — describes vulnerability reporting and safety
  posture.
- **`CONTRIBUTING.md`** — documents layout, frontmatter, and quality
  gates for new skills.
- **`.gitignore`** — excludes virtual environments, build output,
  compiled artefacts, dotenv files, and private keys.

If any file is missing or out of date, propose an update as part of the
integration, but do not commit or push.

## Tests

Skills that ship scripts must include unit tests. Place them at:

```text
tests/test_<slug>_<scope>.py
```

Use the existing test framework in the repository. Follow the loader
pattern established by other tests when the script has a hyphenated file
name.

Confirm tests pass locally:

```powershell
python -m unittest discover -s .\tests -v
```

Report failures immediately. Do not weaken the test to make it pass.

## Discovery Commands

Verify that the Skills CLI (or the equivalent tool used by the target AI
client) can discover the skill locally:

```powershell
npx skills add . --list
```

Expect the new slug to appear alongside existing skills. Ordering does
not matter.

Verify remote discovery only after the repository has been pushed by a
human. Do not push automatically.

## Git Workflow

- Confirm `git status` shows only the intended changes.
- Confirm `git diff --check` reports no whitespace errors.
- Prepare a conventional-style commit message.
- Do not run `git commit`, `git push`, `git tag`, `gh release`, `gh
  issue create`, or `gh pr create` automatically.

Explicitly hand the commit and push steps back to the human maintainer
in the final report.

## Coexistence with Other Skills

- Ensure the new skill does not overlap with an existing skill without a
  clear reason.
- Ensure the description does not accidentally activate on prompts
  already handled by another skill.
- Ensure shared references (for example, credential-handling patterns)
  point to a single source of truth rather than duplicating text.

## Repository Metadata

- Confirm the repository is public (or intentionally private) matching
  the skill's distribution target.
- Confirm the license badge and description in the repository metadata
  are current.
- Confirm the repository does not commit prebuilt executables.
- Confirm the repository does not commit environment files with values.

## Integration Checklist

- [ ] Skill directory is at `skills/<slug>/` with the required layout.
- [ ] Root `README.md` catalog is updated.
- [ ] `LICENSE`, `SECURITY.md`, and `CONTRIBUTING.md` exist and are
      current.
- [ ] Tests for any new script exist under `tests/` and pass.
- [ ] Local skill discovery works.
- [ ] No secrets, customer data, or proprietary code are staged.
- [ ] No automatic commit, push, tag, or issue creation was performed.
- [ ] The final report tells the human maintainer exactly which files
      to commit and push.
