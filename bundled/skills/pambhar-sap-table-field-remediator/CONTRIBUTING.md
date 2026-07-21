# Contributing

## Branching & PRs

- Branch from `main`. Names: `feat/<short-desc>`, `fix/<short-desc>`, `docs/<short-desc>`.
- Open PRs against `main`. **One peer review required** before merge — branch protection enforced.
- Use the PR template (`.github/PULL_REQUEST_TEMPLATE.md`). It's there for a reason.

## Using AI assistance

We use AI aggressively but consciously. Two non-negotiables:

1. **Disclose.** Every PR declares AI usage via the template checkbox.
2. **Verify.** If AI generated anything, the "What I verified" field must be filled with specifics — what you read, what you tested, what you cross-checked against external sources.

Read `CLAUDE.md` before generating code here.

## Test cases

- Add or update a test when changing skill behavior.
- Every test case has an expected output. **If a test fails, fix the skill — never edit the expected output to make it pass.**

## Questions

Open an issue or ask on the relevant PR.
