# Severity Rubric

The skill MUST classify every finding into exactly one of the four severities below, using exactly one category. If a finding doesn't match any category in this rubric, **do not emit it**.

---

## Critical

Reserved for issues that can cause data leakage, unauthorized access, data corruption from race conditions, or production outage. A Critical finding blocks the PR.

| Category | Where defined | Example one-liner |
|---|---|---|
| Security | `security-checklist.md` | Raw SQL with user input → SQL injection |
| Concurrency | `concurrency-checklist.md` | UPDATE without WHERE inside a parallel loop → lost updates |

## High

Reserved for issues that will produce runtime exceptions on the happy/sad path, or measurable performance regression at production scale. A High finding should block the PR unless the team explicitly accepts the risk.

| Category | Where defined | Example one-liner |
|---|---|---|
| Runtime exception risk | `runtime-exceptions.md` | `await SELECT.one(...).field` without null guard → TypeError on no-row |
| Performance | `performance-checklist.md` | N+1 SELECT inside `for` loop → linear DB round-trips |
| Dependency hygiene | `dependency-hygiene.md` | Use of deprecated API; private/internal symbol; external lib for built-in feature |

## Medium

Reserved for documentation/i18n gaps that hurt maintainability of public service contracts. Medium findings shouldn't block a PR but should produce a follow-up task.

| Category | Where defined | Example one-liner |
|---|---|---|
| Missing/incorrect JSDoc | `jsdoc-conventions.md` | Public action handler without JSDoc — params, returns, errors |
| Hardcoded user-facing messages | `i18n-conventions.md` | `req.error(400, 'Title required')` instead of `req.error(400, '{i18n>TITLE_REQUIRED}')` |

## Low

Cosmetic / hygiene findings. Low findings are advisory.

| Category | Where defined | Example one-liner |
|---|---|---|
| Dead code | `code-quality-checklist.md#dead-code` | `if (false) { ... }` block |
| Unnecessary comments | `code-quality-checklist.md#unnecessary-comments` | `// increments stock by 1` next to `stock++` |
| Unused code | `code-quality-checklist.md#unused-code` | Imported `Authors` never referenced |

---

## Anti-rubric — what NOT to flag

- **Style preferences** (single vs double quotes, trailing commas, indent width). Use ESLint/Prettier separately.
- **TypeScript strict-mode hints** in JS files (the IDE shows them; not part of this skill).
- **Architectural choices** (CQRS, hex, DDD). The skill reviews implementation, not architecture.
- **Existing patterns in unchanged code.** If a smell already exists in code that was NOT modified by the PR, do not flag it. Out of scope.
- **Anything not justified by a capire reference under `references/`.** No "common best practice from elsewhere" — the rubric is anchored to capire.

---

## Mapping table (quick reference for the skill loop)

```
Critical → security-checklist.md       (any rule)
Critical → concurrency-checklist.md    (any rule)
High     → performance-checklist.md    (any rule)
High     → runtime-exceptions.md       (any rule)
High     → dependency-hygiene.md       (any rule)
Medium   → jsdoc-conventions.md        (any rule)
Medium   → i18n-conventions.md         (any rule)
Low      → code-quality-checklist.md   (any subsection)
```

Each rule in those files has a `Rule ID` (e.g. `SEC-001`, `PERF-002`). The Rule ID goes into the report's "Capire reference" field along with the file:section anchor.
