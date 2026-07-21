# Skill Review Report

Use this template for every Audit run and at the end of Create and
Refactor runs.

## Executive Result

- **Skill:** _<slug>_
- **Mode:** _Create | Refactor | Audit | Repository integration |
  Submission preparation_
- **Reviewed by:** _<name or agent identifier>_
- **Review date:** _<YYYY-MM-DD>_
- **Overall status:** _Ready | Ready with recommendations | Blocked_

Short paragraph describing the outcome and the top three findings.

## Scope

- **Repository:** _<owner/repo>_
- **Skill path:** _`skills/<slug>/`_
- **Files reviewed:** _<count and list>_
- **Files out of scope:** _<list with reason>_

## Structure

- **Frontmatter valid:** _yes | no_
- **`SKILL.md` line count:** _<n>_
- **References linked from `SKILL.md` or a linked file:** _yes | no_
- **Empty directories:** _none | list_
- **Broken relative links:** _none | list_

## Frontmatter

- **`name`:** _<value>_ — matches directory: _yes | no_
- **`description` length:** _<n> characters_
- **`compatibility` length:** _<n> characters_
- **`metadata` keys:** _<list>_
- **Unsupported top-level fields:** _none | list_

## Trigger Quality

- **Positive triggers tested:** _<count>_ — _<pass rate>_
- **Negative triggers tested:** _<count>_ — _<pass rate>_
- **Ambiguous prompts:** _<count>_ — _<behaviour summary>_
- **Safety prompts:** _<count>_ — _<behaviour summary>_
- **Notable false positives:** _<list>_
- **Notable false negatives:** _<list>_

## Progressive Disclosure

- **Metadata tier concise:** _yes | no_
- **Main instructions focused:** _yes | no_
- **References loaded on demand:** _yes | no_
- **Nested reference chains detected:** _none | list_
- **Duplicated safety rules across files:** _none | list_

## Security

Summarise each category from
[`../references/security-review.md`](../references/security-review.md).

| Category | Findings | Severity | Status |
|----------|----------|----------|--------|
| Credentials and secrets | _<n>_ | _<max severity>_ | _<open / fixed / accepted>_ |
| Network behaviour | _<n>_ | _<max severity>_ | _<...>_ |
| Filesystem behaviour | _<n>_ | _<max severity>_ | _<...>_ |
| Shell and subprocess | _<n>_ | _<max severity>_ | _<...>_ |
| SAP-specific operational risks | _<n>_ | _<max severity>_ | _<...>_ |
| Dependency and supply-chain | _<n>_ | _<max severity>_ | _<...>_ |
| Public-release | _<n>_ | _<max severity>_ | _<...>_ |

## Scripts

- **Scripts inspected:** _<list>_
- **Documentation completeness:** _pass | partial | fail_
- **Dependency justification:** _pass | partial | fail_
- **Unit tests present and passing:** _yes | partial | no_
- **Network calls documented and safe:** _yes | partial | no_
- **Secrets redacted from output:** _yes | partial | no_

## Documentation

- **`README.md` for the skill:** _present | missing_
- **Human onboarding readable:** _yes | partial | no_
- **Licence disclaimer present:** _yes | no_
- **SAP non-affiliation disclaimer present (public releases):** _yes | no
  | not applicable_

## Validation

- **Structural validator command:** _<command line used>_
- **Structural validator result:** _PASS/WARN/FAIL counts_
- **Blockers reported:** _none | list_
- **Warnings accepted with reason:** _list_

## Behavioural Evaluation

Attach or link the transcript notes. Summarise:

- **Cycles executed:** _<n>_
- **Trigger precision:** _<summary>_
- **Instruction adherence:** _<summary>_
- **Tool selection:** _<summary>_
- **Safety behaviour:** _<summary>_
- **Output correctness:** _<summary>_
- **Failure reporting:** _<summary>_
- **Context efficiency:** _<summary>_

## Repository Readiness

- **Skill catalog entry updated:** _yes | no | not applicable_
- **Root `LICENSE`, `SECURITY.md`, `CONTRIBUTING.md` present:** _yes | no_
- **Tests pass locally:** _yes | no_
- **Local skill discovery succeeds:** _yes | no_

## SAP AI Skills Library Readiness

- **Public repository:** _yes | no | not applicable_
- **Readiness checklist confirmed:** _yes | no_
- **Additional context template drafted:** _yes | no_
- **Outstanding blockers for submission:** _list_

## Findings

| ID | Severity | Category | Location | Description | Remediation | Status |
|----|----------|----------|----------|-------------|-------------|--------|
| F-001 | Critical | _<category>_ | _<file[:line]>_ | _<what and why>_ | _<how to fix>_ | Open |
| F-002 | High | _<category>_ | _<file[:line]>_ | _<what and why>_ | _<how to fix>_ | Fixed |

Severity ladder: **Critical**, **High**, **Medium**, **Low**,
**Informational**.

## Recommendations

Ordered list of the next actions, tagged by phase:

1. _<action>_ — _<phase>_
2. _<action>_ — _<phase>_
3. _<action>_ — _<phase>_

## Blockers Summary

- **Blockers:** _<list or "none">_
- **Warnings requiring decision:** _<list or "none">_
- **Informational findings:** _<list or "none">_

Do not label safe documented placeholders as confirmed secrets. Do not
claim readiness in categories that were not walked.
