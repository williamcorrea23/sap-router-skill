# Skill Requirements Worksheet

Fill this worksheet during Discover and Scope. Keep answers concrete.
Every empty section is a stop condition until it is completed.

## Identification

- **Working title:** _<short human name>_
- **Proposed slug:** _<kebab-case, ≤ 64 chars, matches directory name>_
- **Maintainer:** _<name, GitHub handle, or team>_
- **Distribution target:** _internal team | public repository | SAP AI
  Skills Library submission_

## Problem Statement

_One paragraph, using the scope template:_

> This skill helps <target user or agent> perform <repeatable task> on
> <SAP product / component> in <environment / persona context>,
> especially when <trigger condition or existing gap>.

## Users

- **Target users:** _<personas>_
- **Target agents or clients:** _<Claude Code, Codex, Cursor, OpenCode,
  Copilot-compatible, ...>_
- **Existing MCP tools relevant to the scope:** _<list or "none">_

## SAP Scope

- **Product family:** _<SAP S/4HANA, SAP BTP ABAP Environment, SAP CAP,
  SAP Fiori, SAP Integration Suite, SAP HANA Cloud, ...>_
- **Release or edition:** _<e.g., "2023 on-premise", "BTP CF">_
- **Environment layer:** _<development | quality | production>_
- **Stack layer:** _<data model | service | UI | deployment | monitoring
  | integration>_

## Repeatable Workflow

_Numbered steps of the current procedure, referencing artefacts._

1. _Step..._
2. _Step..._
3. _Step..._

Source materials (link or path per bullet):

- _<runbook path>_
- _<code file>_
- _<ticket ID>_
- _<official documentation URL>_

## Triggers

- **Positive triggers (3+):**
  1. _..._
  2. _..._
  3. _..._

- **Negative triggers (3+):**
  1. _..._
  2. _..._
  3. _..._

- **Ambiguous prompts (2):**
  1. _..._
  2. _..._

- **Safety prompts (2):**
  1. _..._
  2. _..._

## Contracts

- **Inputs:** _<user intent, files, credentials by reference, external
  services>_
- **Outputs:** _<created files, edited files, external calls, reports>_
- **Preconditions:** _<env vars, tools, project layout, network access>_
- **Postconditions:** _<must be true on success>_
- **Idempotency:** _<safe to run twice? yes / no / conditional>_

## Tools and Access

- **Required tools:** _<CLI, SDK, MCP tool, IDE integration>_
- **Required network access:** _<hosts, protocols, offline capability>_
- **Required credentials:** _<by reference only>_
- **Read operations:** _<list>_
- **Write operations:** _<list>_
- **Destructive operations:** _<list, with pre-execution controls>_

## Risk Classification

Mark all that apply:

- [ ] Read-only informational
- [ ] Read-only operational
- [ ] Write-capable
- [ ] Destructive or difficult-to-reverse
- [ ] Credential-sensitive
- [ ] Production-impacting

Notes: _<explain each checked box>_

## Known Failure Modes

_List real failures observed or expected, and how the skill should respond._

- _<failure> → <expected behaviour>_
- _<failure> → <expected behaviour>_

## Validation Strategy

- **Structural validator command:** _<default or overridden>_
- **Behavioural evaluation prompts:** _<link to the prompt set>_
- **Regression watch:** _<how the prompts will be re-run>_
- **Unit tests for scripts:** _<paths under tests/>_

## License and Attribution

- **License:** _<Apache-2.0, MIT, ...>_
- **Attribution constraints:** _<none | list them>_
- **Third-party content:** _<none | list with license>_

## Open Questions

_List every unresolved question. Do not proceed to Generate until each
question has an owner and a target answer date, or is explicitly
deferred._

- _<question>_
- _<question>_
