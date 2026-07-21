# Code quality checklist (Low)

Anchored in capire's general best-practices guidance and standard JS hygiene. The rules here are advisory — Low severity. If a finding doesn't match a Rule ID below, do not classify it as Low.

The skill flags only what's INSIDE THE PR'S DIFF. Pre-existing dead code in unchanged files is out of scope.

---

## QUAL-001 — Dead code (`if (false)` / `while (false)` / unreachable after `return`)

**Trigger.** Inside changed files, any of:
- `if (false) { ... }` or `if (true) { ... } else { ... }`
- A statement that follows an unconditional `return`, `throw`, or `process.exit` in the same block
- A `try { ... } catch { ... } finally { return X; throw Y }` — code after the early-exit
- Commented-out blocks > 5 lines that look like JS code (heuristic: contains `;`, `=>`, or `function`)

**Reference.** capire / general — *"Remove dead code; rely on git history if you need to recover it."*

**Why.** Confuses readers, hides intent, expands review surface.

**Suggested fix anchor.** Delete it. If the block is intentionally retained as documentation, convert to a JSDoc comment with explanation.

---

## QUAL-002 — Unnecessary comments (restating the next line)

**Trigger.** A single-line comment whose normalized text (lowercased, stop-words removed) is a near-duplicate of the next non-empty line of code. Examples:
- `// increment counter` followed by `counter++`
- `// loop over books` followed by `for (const book of books) { ... }`
- `// return result` followed by `return result`

**Reference.** capire / general — *"Code comments should explain WHY, not WHAT. The identifier already says what."*

**Why.** Adds noise without information; rots when the code changes; trains readers to skim past comments.

**Suggested fix anchor.** Remove the comment. If a clarification is genuinely needed, rewrite to explain the WHY (a constraint, an invariant, a non-obvious decision).

---

## QUAL-003 — Unused code (imports, variables, parameters)

**Trigger.** In a changed file, ONE OF:
- A `require(...)` whose result is bound to a name that is never referenced in the file.
- A top-level `const`/`let` whose name is never used.
- A function parameter that's never read AND has no `_` prefix indicating intentional unused.
- A function declared in the file but never called and not exported.

**Reference.** capire / general — *"Remove unused symbols; ESLint's `no-unused-vars` is the canonical check."*

**Why.** Dead surface; readers ask "what's this for?" and find nothing.

**Suggested fix anchor.** Delete the unused name. For required-but-unused parameters (e.g. middleware signature), prefix with `_` (`_req, _res, next`).

---

## QUAL-004 — Magic literal that should be a named constant

**Trigger.** A numeric or string literal repeated ≥ 3 times within the same file (excluding `0`, `1`, `-1`, empty string, and obvious singletons like `'GET'`, `'POST'`).

**Reference.** capire / general — *"Extract magic numbers to named constants for searchability and intent."*

**Why.** Three occurrences signal a single concept; a name documents it.

**Suggested fix anchor.** Extract to a `const PAGE_SIZE = 50;` at the top of the file and replace each call site.

---

## QUAL-005 — `console.log` in production code

**Trigger.** `console.log(...)`, `console.warn(...)`, `console.error(...)`, `console.debug(...)` inside `srv/`, `db/`, or `app/` (not under `test/`).

**Reference.** capire — *"Use `cds.log('namespace')` for logging; CAP routes it to the configured sink (otel/winston/console) and respects log-level config."*

**Why.** Direct console calls bypass CAP's log infrastructure: no log level, no namespace, no telemetry export.

**Suggested fix anchor.** Replace `console.log(...)` with `LOG.info(...)` / `LOG.debug(...)` from `const LOG = cds.log('catalog')` declared at module top.

---

## QUAL-006 — TODO / FIXME / HACK without a tracking link

**Trigger.** A comment with `TODO`, `FIXME`, `XXX`, or `HACK` (case-insensitive) introduced in this PR's diff, without a JIRA/GitHub issue link or owner tag (`@username`).

**Reference.** capire / general — *"Annotate TODOs with an owner or ticket so they don't rot in the codebase."*

**Why.** Anonymous TODOs accumulate forever and never get done.

**Suggested fix anchor.** Either resolve the TODO before merging, or add `// TODO(@user, ISSUE-123): explain` so it's traceable.

---

## What this section is NOT

- It does NOT replace ESLint/Prettier. Most of these rules can be enforced by lint config — prefer that.
- It does NOT flag style preferences (tab vs space, single vs double quote).
- It does NOT flag long functions, deep nesting, or complexity metrics. Those are subjective and out of scope.
- It does NOT flag pre-existing issues in unchanged files.
