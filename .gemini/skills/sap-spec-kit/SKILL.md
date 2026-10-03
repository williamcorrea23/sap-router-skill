---
name: sap-spec-kit
description: >-
  Apply GitHub Spec Kit 1.0.6 to SAP Router work. Use automatically for new
  features, contract or data-model changes, integrations, and multi-component
  SAP changes; use when the user explicitly requests Spec Kit or
  specification-driven development. Keep localized fixes and read-only work on
  the lightweight Karpathy path.
license: MIT
trigger:
  keywords: [spec kit, spec-kit, specification-driven, new feature, contract change, data model, integration, multi-component]
  intent: >-
    Create and converge Spec Kit artifacts while routing implementation through
    the SAP Router and its approval controls.
---

# SAP Spec Kit — Karpathy Background Workflow

Use GitHub Spec Kit **v1.0.6** as a background workflow. Keep it inside the
current task: do not create a resident service and do not require the caller to
manually invoke every Spec Kit command.

## Prerequisites

Run `specify version` before using the workflow. Require version `1.0.6`.
Install or repair it with:

```powershell
uv tool install --force specify-cli --from git+https://github.com/github/spec-kit.git@v1.0.6
specify version
```

Use the repository's `.specify/` infrastructure, initialized with the Codex
integration and PowerShell scripts. Do not re-run `specify init . --force` in a
configured repository: it can merge or overwrite project artifacts. Initialize
only a fresh project with:

```powershell
specify init . --integration codex --script ps --non-interactive --ignore-agent-tools
```

Read [upstream.md](references/upstream.md) when checking source provenance,
versions, or the exact upstream files included in this package.

## Scope decision

Run `python scripts/sap_router.py spec-kit --task "<request>"` before starting
work that may change code or configuration.

Use `full` when the task is a new feature, changes a public contract or data
model, adds an integration, or affects several components. Use `light` for a
localized fix: state the Karpathy goal and verification only. Use `none` for
questions, discovery, and other read-only work. An explicit request to execute
Spec Kit selects `full`; a question about Spec Kit remains `none`.

## Full workflow

1. Apply Karpathy: record assumptions, choose the minimum SAP route, and define
   verifiable success criteria.
2. Establish or update the constitution with `$speckit-constitution` only when
   project principles need changing.
3. Run `$speckit-specify`, then `$speckit-clarify` when the feature contains a
   material ambiguity.
4. Run `$speckit-plan`, `$speckit-checklist`, `$speckit-tasks`, and
   `$speckit-analyze`. Resolve inconsistencies before implementation.
5. Run `$speckit-implement`. Route every SAP operation through SAP Router;
   preserve functional-context, approval, deployment, and transport gates.
6. Run `$speckit-converge`. Address newly appended tasks until it reports
   convergence or records a concrete external blocker.

Keep the active feature in `.specify/feature.json`. Store feature artifacts in
its directory: `spec.md`, `plan.md`, and `tasks.md`. Resume that directory on
later work; do not infer it from the Git branch.

## SAP controls

Spec Kit creates requirements artifacts. It does not authorize SAP mutations.
Require the existing Router functional context for BAPI or business writes and
the existing plan/approval/commit gate for deployments and transports. Never
claim convergence when an SAP verification step was not performed.

## Verification

```powershell
specify version
python scripts/sap_router.py spec-kit --task "fix typo in one ABAP method"
python scripts/sap_router.py spec-kit --task "add CAP service with new API contract and CPI integration"
python scripts/sap_router.py spec-kit --task "use Spec Kit to implement this"
python scripts/sap_router.py spec-kit --task "where is BAPI_MATERIAL_SAVEDATA used"
```

Expect `light`, `full`, `full`, and `none`, respectively. Validate this skill
with `python scripts/skill_packager.py validate --skill sap-spec-kit`.
