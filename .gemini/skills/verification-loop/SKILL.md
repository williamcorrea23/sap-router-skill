---
name: verification-loop
description: >-
  Verify SAP Router changes and agent outcomes with bounded loops, independent
  checks, PASS/FAIL/NOT_RUN evidence, and explicit separation of offline results
  from observed SAP field responses.
trigger:
  keywords: [verification loop, verification report, quality gate, agent verification, verify implementation]
  intent: Verify a change, agent result, or integration outcome before declaring success.
---

# Verification Loop — SAP Router

Required for every routed profile and delegated agent, together with
`karpathy-guidelines` and `loop-specification`. Read the selected canonical
profile's `execution_protocols` before work. These instructions define checks;
they do not prove a CLI, MCP, or SAP operation has executed.

## Start with an observable goal

Resolve `SAP_ROUTER_ROOT`, change into it, and require
`scripts/source_catalog.py`. Discover domain skills and enabled MCP providers
through the local catalog. Define acceptance criteria, the requested target,
changed objects, relevant checks, and evidence needed before execution.
Use existing authorization and canonical capability policy. A skill, model
review, or successful healthcheck cannot grant a capability or approve a write.

For a defect, reproduce the failing behavior before its fix where practical.
For a new verifier, show that an invalid input fails. Keep tests and their
expected result independent of the maker's proposed solution.

## Bound the loop

Use the profile's declared limits: at most eight iterations, 900 seconds total,
120 seconds per call, and three consecutive iterations without progress.
Declare any additional budget before starting. Perform one accepted change per
iteration. Record the goal, plan, iteration, remaining limits, action fingerprint,
approval reference, verification evidence, and next action in harness run state
or a named local artifact. Save checkpoints before and after external actions.
Keep credentials and raw secret values out of the durable state and report.

Maker and checker run in fresh, separate processes when model judgment is used.
Give the checker the goal, rubric, relevant artifact, and observed evidence;
exclude the maker's private reasoning. Independent deterministic checks remain
required for schema, policy, and tool results. Level 4 review cannot replace a
failed deterministic check or an unobserved SAP response.

An approved write remains bound to its exact target and arguments. An uncertain
mutation requires reconciliation before retry or fallback. `PENDING_APPROVAL`
is a saved checkpoint: stop external execution, expose the concrete action for
approval, and resume only after the approval broker verifies it.

Terminal states:

| State | Required condition |
|---|---|
| `Success` | Goal evidence exists and every required acceptance check is `PASS`. |
| `No-Op` | A read or deterministic comparison proves the requested condition already holds. |
| `Blocked` | A required capability, authorization, contract, dependency, or field check is unavailable. |
| `Stalled` | Three consecutive iterations produce no accepted progress. |
| `Exhausted` | An iteration, elapsed time, call, or declared budget limit prevents further work. |

Save the terminal reason and remaining checks. A stopped process, generated
plan, model approval, or zero exit code alone cannot establish `Success`.

## Choose the verification level

| Level | Evidence | Use |
|---|---|---|
| 1 | Deterministic command result, artifact integrity, exact comparison | Local mechanical correctness |
| 2 | Schema, permission, argument, or text constraint validation | Contract and policy correctness |
| 3 | Observed SAP result: ABAP Unit result, persisted object read, CPI message payload/status | Requested target behavior |
| 4 | Independent model judgment against a stated rubric | Assisted review with stated limits |
| 5 | Human authorization or acceptance recorded for the concrete action | Required human checkpoint |

Label each check honestly. CLI initialization and `tools/list` establish
transport availability only. A configured URL, OAuth token, successful build,
offline fixture, or healthy server does not establish Level 3 field truth.
Level 5 approval permits a guarded action; it does not prove that action worked.

## Run applicable phases

Use repository commands that actually exist. Prefer RTK for supported verbose
commands and Context Mode for large evidence. Preserve exit codes and complete
diagnostics needed for review. Avoid truncation that hides a failure.

| Phase | Repository checks | Evidence boundary |
|---|---|---|
| Build/artifact | `python scripts/generate_ide_assets.py check`; `npm run zrouter:artifacts:check` for ZROUTER changes | Mirror and generated artifact parity; report a general build as `NOT_RUN` if no target exists. |
| Types/syntax | Existing language checks for changed code | Report `NOT_RUN` with reason when a type-check target is absent. Do not install a tool implicitly. |
| Catalog/lint | `python scripts/validate_catalog.py --strict`; `npm run abap:review` for ABAP templates | Canonical catalog, policy, and relevant static review. |
| Tests | Focused regression first; `python -m unittest discover -s tests -q` when affected scope requires the repository suite | State passed/failed counts. Coverage is `NOT_RUN` unless measured. |
| Security | `python scripts/secret_audit.py --strict --json`; inspect changed argument and permission handling | Report findings by location/type; never expose secret values. |
| Diff | `git diff --stat` and relevant `git diff -- <paths>` | Requested scope, edge cases, missing error handling, preserved concurrent edits. |
| SAP field outcome | Authorized readback or test in the requested target | Observe the operation's actual output and expected business/development state. |

Stop a failing dependency chain, diagnose the cause, make the smallest relevant
fix, and rerun the affected check. Repeat broader checks only when another change
or unresolved risk justifies them. A phase that has not run remains `NOT_RUN`.

SAP outcome examples:

- ABAP: inspect returned syntax/ATC/ABAP Unit results for the requested object
  and target. Local template lint does not prove SAP activation.
- BAPI: inspect all returned errors, approved commit outcome when required, and
  read back the resulting object in the same target. A dispatch plan or request
  identifier does not prove persistence.
- CPI: validate the ZIP locally, then observe approved deployment and a test
  message's MPL status plus expected payload when those actions are in scope.
- SAP GUI: capture the requested screen or result, transaction status, and
  readback after any approved write. An attached session proves attachment only.
- MCP: validate the selected tool contract, argument schema, effect, and returned
  result. Mock transport tests prove the harness contract, not a live SAP call.

## Report evidence

Each check records `check`, `status`, `verification_level`, `command_or_tool`,
`target`, `observed_result`, and `artifact_or_reference`. Add `reason` for
`NOT_RUN`; keep references to sanitized evidence. Use `PASS`, `FAIL`, or
`NOT_RUN` only. Include the run state and next action when incomplete.

```text
VERIFICATION REPORT
Goal: <observable requested condition>
Target: <local/offline or exact SAP target>
Build: PASS / FAIL / NOT_RUN — evidence or reason
Types: PASS / FAIL / NOT_RUN — evidence or reason
Catalog/lint: PASS / FAIL / NOT_RUN — evidence or reason
Tests: PASS / FAIL / NOT_RUN — counts and evidence
Security: PASS / FAIL / NOT_RUN — sanitized evidence
Diff: PASS / FAIL / NOT_RUN — reviewed scope
SAP field outcome: PASS / FAIL / NOT_RUN — level and observed response
Run state: Success / No-Op / Blocked / Stalled / Exhausted / PENDING_APPROVAL
Remaining checks: <items or none>
```

Readiness is scoped to the verified goal. If live SAP acceptance is required and
has not run, local gates may pass while the run remains `Blocked` with that
missing evidence recorded. The report must retain this boundary.
