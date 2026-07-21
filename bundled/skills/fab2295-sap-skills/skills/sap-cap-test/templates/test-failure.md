# CAP Test Failure Report

> One or more tests failed. This file is written by **sap-cap-test**
> in addition to `CAP-TEST-REPORT.md` so you have a focused failure
> view without scrolling through the full report.
>
> ⚠️ The skill did NOT modify any production code. Fixing the bug is
> your call.

| Field | Value |
|---|---|
| Generated | `<ISO_TIMESTAMP>` |
| Runner | `<cds test \| vitest \| mocha \| jest>` |
| Exit code | `<non-zero>` |
| Failed tests | `<n>` of `<total>` |

---

## Reproduce

```sh
<exact command that was executed>
```

---

## Failures

### 1. `<suite> > <test name>`

- **File:** `<test/foo.test.js:42>`
- **Assertion:**

```
<assertion message verbatim from runner output>
```

- **Stack (excerpt):**

```
<≤ 15 lines of stack, trimmed to user code>
```

- **Probable cause** (from runner output, NOT invented):

> `<one-line probable cause, or "Unknown — not visible in runner output">`

---

### 2. `<suite> > <test name>`

…

---

## What this skill will NOT do

- Fix the failing test by changing `srv/`, `db/`, or `app/` files.
- Comment out or skip the failing assertion.
- Lower coverage thresholds to make the run green.
- Commit anything.

If the failure is in the test file itself (typo, wrong fixture, wrong
expectation), ask the skill to **re-scaffold** that specific test.
If the failure exposes a real bug in production code, fix it yourself
or invoke a code-modifying skill — `sap-cap-test` deliberately stops
at the failure boundary.

---

## Method

Failures were collected verbatim from the runner's stderr/stdout. No
heuristic re-interpretation, no synthesized assertions. If the runner
did not surface a "probable cause" line, the field reads `Unknown`.
