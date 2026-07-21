# Frontmatter and Triggering

Load this file when writing or reviewing the YAML frontmatter of a skill.
The frontmatter and the description control when the skill activates, so
their quality determines whether the skill is actually used.

## Frontmatter Field Reference

```yaml
---
name: <slug>
description: >-
  <capability sentence>. Use when <activation conditions>. Do not use for
  <important exclusions>.
license: <license>
compatibility: <runtime prerequisites>
metadata:
  author: <name>
  version: "<version>"
  category: <category>
  repository: <owner/repo>
allowed-tools: <optional tool constraint>
---
```

### `name`

- Required.
- Maximum 64 characters.
- Lowercase ASCII letters, digits, and single hyphens.
- No leading or trailing hyphen.
- No consecutive hyphens.
- Must exactly match the parent directory name.

Good examples: `sap-adt-commands`, `sap-cap-service-scaffold`,
`sap-btp-destination-helper`.

Bad examples: `SAP_ADT_Commands`, `sap--cap-scaffold`, `-sap-cap`,
`sap-cap-`.

### `description`

- Required.
- Maximum 1024 characters.
- Loaded before the body of `SKILL.md`, so it controls activation.
- Must state both what the skill does and when to use it.
- Should mention SAP product or workflow context.
- Should include important exclusions when likely to prevent misuse.

Avoid vague filler phrases such as "follow best practices", "handle errors
appropriately", "use as needed", "comprehensive solution". The included
validator flags these as warnings.

### `license`

- Optional but recommended.
- Must be a string, for example `Apache-2.0` or `MIT`.
- Should match the repository license unless a specific file overrides it.

### `compatibility`

- Optional but recommended for SAP skills.
- Maximum 500 characters.
- Describe runtime prerequisites, network requirements, and required
  tooling.
- Do not embed instructions that should live in the body.

### `metadata`

- Optional mapping.
- Values must be strings. Quote version numbers explicitly (`"1.0.0"`).
- Typical keys: `author`, `version`, `category`, `repository`.
- Do not embed secrets, personal contact information, or customer data.

### `allowed-tools`

- Optional and experimental across AI clients.
- When used, must be a string.
- Do not add this field unless there is a portable, justified need.

## Description-Writing Formula

Use this three-part structure:

```text
<Primary actions>. Use when <user intents, workflow, system context, or
capability gap>. Do not use for <important exclusions>.
```

### Example: strong SAP description

```text
Executes SAP ADT REST operations for object discovery, source management,
object creation, activation, testing, transport handling, history,
where-used analysis, message classes, and text elements. Use when working
with an SAP ABAP system and the required ADT operation is unavailable
through the currently configured MCP tools. Do not use for SAP GUI-only
capabilities such as ATC baseline management, interactive debugging, or
production changes without explicit human authorization.
```

Why it works:

- Verb-first sentence names the concrete capabilities.
- The "Use when" clause names the trigger and the missing-tool gap.
- The "Do not use" clause protects against misactivation.

### Example: weak SAP description

```text
A comprehensive skill for handling SAP tasks with best practices and
robust error handling.
```

Why it fails:

- No verb names the capability.
- No trigger states when to activate.
- No exclusion protects against misuse.
- Vague filler phrases pollute the description.

## Trigger Design

Every skill needs at least three positive triggers and three negative
triggers documented during design.

### Positive triggers

Real user intents that should activate the skill.

Examples for `sap-skills-creator`:

- "Create a reusable Agent Skill from this SAP CAP deployment runbook."
- "Audit this SAP ABAP skill before we share it with the team."
- "Refactor this oversized SAP Integration Suite skill into progressive
  disclosure."

### Negative triggers

Adjacent intents that should not activate the skill.

Examples for `sap-skills-creator`:

- "Explain what SAP BTP is."
- "Fix this single Java syntax error."
- "Give me a generic summary of SAP Integration Suite."

## False Positive and False Negative Risks

Inspect the description for two failure modes:

- **False positive**: the description accidentally activates the skill on
  unrelated SAP prompts. Fix by adding an explicit exclusion.
- **False negative**: the description misses a real user intent. Fix by
  adding a matching verb or trigger keyword.

Iterate on the description while running a small set of test prompts
through the target AI client. Aim for at least one execute-review-revise
cycle before shipping.

## Description Anti-Patterns

- Restating the skill name in the description without adding meaning.
- Listing every SAP product covered by the parent repository.
- Using marketing language ("state-of-the-art", "seamless", "robust").
- Padding with keywords for the sake of trigger coverage.
- Mixing tone (some sentences imperative, some passive) inside one
  description.
- Including internal ticket IDs or customer names.

## Frontmatter Structural Rules

- Frontmatter must start on line 1.
- Opening and closing `---` markers must be on their own lines.
- Nested mappings should be indented consistently (two spaces).
- Quoted values are preferred for anything that could be misinterpreted
  as a boolean, number, or null.
- Do not add unsupported top-level fields (the validator warns on them).

## Validator Behaviour

The included validator (`scripts/validate_skill.py`) checks:

- Presence and shape of `name`, `description`, `license`, `compatibility`,
  and `metadata`.
- Directory-name / `name` match.
- Description length and vague-phrase warnings.
- Compatibility length.
- Metadata value types.
- Unsupported top-level fields.

Fix every `FAIL`. Triage every `WARN` explicitly.
