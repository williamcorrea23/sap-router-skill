# CAP Code Review

> ⚠️ **Suggestions in this report require human validation before being applied.** The sap-cap-code-review skill is read-only static analysis — it does not edit code, it does not commit, and it does not push. Treat every "Suggested fix" as a pointer, not a verdict.
>
> 🔒 **Evidence excerpts are redacted.** All code blocks below were passed through the redaction filter at `references/secret-redaction.md` before being written. Values that matched a credential / token / private-key / URL-with-creds pattern were replaced with `[REDACTED:<kind>]`. Excerpts from `xs-security.json`, `manifest.yaml`, `mta.yaml`, `default-services.json`, `default-env.json`, or `.env*` were replaced wholesale when any redaction trigger matched. If a finding's Evidence ended up empty after redaction, the code block was omitted and a `<path>:<line>` pointer was used instead. **The original files on disk were not modified** — redaction applies only to this report.

| Field | Value |
|---|---|
| Generated | `<ISO_TIMESTAMP>` |
| Mode | `<A: branch compare \| B: explicit files \| C: default diff>` |
| Base ref | `<base-ref-or-NA>` |
| Head ref | `<head-ref-or-NA>` |
| Files analyzed | `<N>` |
| Files skipped | `<M>` |
| CAP runtime detected | `<@sap/cds version from package.json>` |
| Redaction filter | `references/secret-redaction.md` (fail-closed) |
| Redactions applied | `<count of lines/excerpts modified>` |

## Summary

| Severity | Count |
|---|---|
| 🔴 Critical | `<n>` |
| 🟠 High | `<n>` |
| 🟡 Medium | `<n>` |
| 🟢 Low | `<n>` |
| **Total** | `<n>` |

---

## 🔴 Critical findings

> Blocks the PR. Security or concurrency issues that can lead to data leakage, unauthorized access, or data corruption.

### `<N>`. `<short title>` — `<rule-id>`

- **Category:** `<Security \| Concurrency>`
- **Location:** [`<file>:<line>`](<file>#L<line>) (or `<file>:<start>-<end>`)
- **Symbol:** `<function/method/class/action/entity name>` (or `<module>`)
- **Capire reference:** [`<reference>.md#<anchor>`](../.claude/skills/sap-cap-code-review/references/<reference>.md#<anchor>) — Rule `<RULE-ID>`

**Evidence**

```js
<offending excerpt — ≤ 10 lines>
```

`<one-sentence description of why this triggers the rule>`

**Suggested fix**

> ⚠️ Suggestion — needs human validation before applying.

```js
<illustrative replacement — ≤ 5 lines, anchored to capire>
```

`<one-sentence description of the proposed change>`

---

## 🟠 High findings

> Should block the PR unless the team explicitly accepts the risk. Runtime errors, performance regressions, or use of deprecated/private APIs / external libs that duplicate CAP capabilities.

### `<N>`. `<short title>` — `<rule-id>`

- **Category:** `<Runtime exception risk \| Performance \| Dependency hygiene>`
- **Location:** [`<file>:<line>`](<file>#L<line>)
- **Symbol:** `<...>`
- **Capire reference:** [`<reference>.md#<anchor>`](...) — Rule `<RULE-ID>`

**Evidence**

```js
<offending excerpt>
```

`<description>`

**Suggested fix**

> ⚠️ Suggestion — needs human validation before applying.

```js
<illustrative replacement>
```

`<description>`

---

## 🟡 Medium findings

> Should produce a follow-up task but should not block the PR. Documentation/i18n gaps that hurt maintainability of the public service contract.

### `<N>`. `<short title>` — `<rule-id>`

- **Category:** `<Missing/incorrect JSDoc \| Hardcoded user-facing messages (i18n)>`
- **Location:** [`<file>:<line>`](<file>#L<line>)
- **Symbol:** `<...>`
- **Capire reference:** [`<reference>.md#<anchor>`](...) — Rule `<RULE-ID>`

**Evidence**

```js
<offending excerpt>
```

`<description>`

**Suggested fix**

> ⚠️ Suggestion — needs human validation before applying.

```js
<illustrative replacement>
```

`<description>`

---

## 🟢 Low findings

> Cosmetic / hygiene findings. Advisory only.

### `<N>`. `<short title>` — `<rule-id>`

- **Category:** `<Dead code \| Unnecessary comments \| Unused code \| Magic literal \| console.log \| TODO without owner>`
- **Location:** [`<file>:<line>`](<file>#L<line>)
- **Symbol:** `<...>`
- **Capire reference:** [`<reference>.md#<anchor>`](...) — Rule `<RULE-ID>`

**Evidence**

```js
<offending excerpt>
```

`<description>`

**Suggested fix**

> ⚠️ Suggestion — needs human validation before applying.

```js
<illustrative replacement>
```

`<description>`

---

## Files in scope

| Path | LOC analyzed | Findings |
|---|---|---|
| `<file>` | `<n>` | C:`<n>` H:`<n>` M:`<n>` L:`<n>` |

## Files skipped

| Path | Reason |
|---|---|
| `<file>` | `<reason — e.g. "binary blob, not analyzed", "not in relevance filter">` |

## Out-of-rubric (considered but not flagged)

> Optional appendix. Things the analyzer noticed that don't map to any Rule ID. Listed here only if the operator passes `--include-considered`. Empty by default.

| Path:line | Note |
|---|---|

---

## Method

The sap-cap-code-review skill applies the rules under `~/.claude/skills/sap-cap-code-review/references/`:

- `severity-rubric.md` — classification map
- `security-checklist.md` — Critical / Security
- `concurrency-checklist.md` — Critical / Concurrency
- `performance-checklist.md` — High / Performance
- `runtime-exceptions.md` — High / Runtime exception risk
- `dependency-hygiene.md` — High / Dependency hygiene
- `jsdoc-conventions.md` — Medium / Missing or incorrect JSDoc
- `i18n-conventions.md` — Medium / Hardcoded user-facing messages
- `code-quality-checklist.md` — Low / Hygiene

Findings without a Rule ID anchor are not emitted.

The skill does not run code, does not edit files, does not commit. It only writes this report.
