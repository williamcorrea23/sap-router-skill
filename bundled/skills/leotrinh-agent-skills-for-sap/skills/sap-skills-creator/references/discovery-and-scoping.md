# Discovery and Scoping

Load this file at the beginning of any Create, Refactor, or Audit run.

A skill is worth building only when there is a real, repeatable, verifiable
task behind it. This document describes how to find that task and how to
narrow the scope until the resulting skill is a coherent unit.

## Valid Sources of Expertise

Prefer these over generic LLM knowledge:

- A successfully completed engineering task, with commits, logs, or a
  changelog entry.
- A runbook that a team already follows manually.
- Existing source code or configuration that captures the working
  procedure.
- An API specification (OpenAPI, WSDL, EDMX, gRPC, ADT REST) plus a
  concrete usage example.
- Post-incident reviews and remediation notes.
- Documented review feedback that keeps repeating.
- A named team convention that survives across projects.
- Verified official SAP documentation with a specific version or release.

## Invalid Sources of Expertise

Refuse to proceed when the only source is one of the following:

- A vague personal recollection with no artefact.
- General LLM knowledge without a verifiable reference.
- Copy-pasted marketing content from an SAP product page.
- A single conversation in which the workflow was invented on the spot.
- An outdated blog post without a version reference.

Ask the user to point to an artefact (runbook, code, ticket, diff, report)
or record the artefact together during the discovery phase.

## Deciding Whether a Skill Is Warranted

A workflow is worth packaging as a skill when at least three of the
following are true:

- It repeats often enough that automation saves noticeable time.
- The steps are stable across similar tasks.
- Skipping or reordering steps causes real risk (data loss, wrong
  transport, wrong system).
- Onboarding a new person to the workflow is currently painful.
- The workflow benefits from a consistent output format.
- Existing MCP tooling does not already cover the workflow.

If only one or two are true, capture the workflow as a checklist or a
runbook first, and revisit the skill decision later.

## Narrowing SAP Domains

SAP is very large. A skill should never cover an entire product family.
Use these narrowing questions:

- Which product? (For example: SAP S/4HANA on-premise, SAP S/4HANA Cloud,
  SAP BTP ABAP Environment, SAP CAP, SAP Fiori elements, SAP Integration
  Suite, SAP HANA Cloud, SAP Analytics Cloud.)
- Which release or edition matters?
- Which persona is the primary user? (Developer, integration engineer,
  SAP Basis, ABAP consultant, functional consultant, data engineer.)
- Which environment layer? (Development, quality assurance, production.)
- Which layer of the stack? (Data model, service, UI, deployment,
  monitoring.)
- Which one repeatable task inside that layer?

Combine the answers into a scope statement and stop there.

## Scope Statement Template

```text
This skill helps <target user or agent> perform <repeatable task> on
<SAP product / component> in <environment / persona context>, especially
when <trigger condition or existing gap>.
```

Examples that pass the coherence test:

```text
This skill helps SAP ABAP developers create and activate a new ABAP CDS
view in a tracked transport on an SAP S/4HANA on-premise system,
especially when the local MCP tools do not expose ADT object creation.
```

```text
This skill helps SAP CAP developers scaffold a new service module with
role-based access checks and unit tests, especially when the team's
standard project layout requires a specific folder structure and mock
data.
```

Examples that fail the coherence test:

- "Everything about SAP BTP."
- "SAP integration best practices."
- "Complete guide to SAP HANA performance."

## Input and Output Contract

For every candidate skill, capture:

- **Inputs**: user intent, source materials, existing files, credentials
  (only by reference), external services.
- **Outputs**: created files, edited files, external calls made, reports
  produced, user-visible confirmations.
- **Preconditions**: environment variables, MCP tools, project layout,
  network access.
- **Postconditions**: what must be true when the skill reports success.
- **Idempotency**: whether running the skill twice is safe.

Anything the skill needs but the user did not provide belongs in the
required-inputs section of the resulting `SKILL.md`.

## Definition of Done

The scope is complete when:

- The problem statement fits in one paragraph and passes the coherence
  test.
- The requirements template (see
  [`../assets/skill-requirements-template.md`](../assets/skill-requirements-template.md))
  is filled in, including risk classification and distribution target.
- Positive and negative activation triggers are drafted.
- Preconditions are documented, including which credentials the user must
  configure outside the AI conversation.

## Discovery Interview

Do not ask twenty questions at once. Ask up to five clarifying questions
per round, ordered by priority:

1. Objective and workflow.
2. Source expertise.
3. Risk and credentials.
4. Inputs and outputs.
5. Distribution target.
6. Validation.

Skip a question when the answer is already in the source artefact.

Example first-round questions:

- "Which specific SAP product and release does this workflow target?"
- "Do you already have a runbook, code, or ticket that shows the current
  procedure?"
- "Who is the primary user of the finished skill — a human developer, an
  AI agent, or both?"
- "Which parts of the workflow are read-only, and which parts change SAP
  state?"
- "Is this skill for your internal team only, or is it intended for
  public release?"

## Scope Anti-Patterns

Reject these patterns and reshape the scope before continuing:

- **The encyclopedia**: "Cover everything about SAP Integration Suite."
- **The mega-skill**: One skill that handles CAP, Fiori, BTP CF, and
  transports at the same time.
- **The single-shot fix**: A skill that is really a one-time script to
  clean up a bad state.
- **The bypass**: A skill designed to skip transports, approvals, or
  authorization checks.
- **The mirror**: A skill that only repeats what an existing MCP tool
  already does well.
- **The oracle**: A skill that promises to answer any SAP question from
  general model knowledge.

For each anti-pattern, explain the reason and propose a narrower
alternative before writing files.
