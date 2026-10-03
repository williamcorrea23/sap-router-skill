# Implementation Plan: Controlled Agent Execution and Catalog Harness

**Branch**: `001-controlled-agent-execution` | **Date**: 2026-10-01 | **Spec**: [spec.md](spec.md)

## Summary

Add a bounded executor to `sap_harness.py` for Codex and Claude. Each backend returns one typed proposal; deterministic registry/schema checks plus a fresh-process checker run before the Router invokes a pinned local MCP tool contract. Mutations use the existing approval broker and resumable run state. Add canonical loop/verifier procedure, synchronize generated mirrors, repair registry mismatches, and register audited repositories as disabled candidates. The follow-up implementation adds a blocked ABAPilot DEV target profile, retains unselected OData/SAP GUI/SuccessFactors alternatives as disabled, imports SAP OData CLI guidance without its runtime, and refreshes the pinned SAP Basis skill source.

## Technical Context

**Language/Version**: Python 3.11+; installed Codex and Claude CLIs are capability-checked at runtime.  
**Primary Dependencies**: Python standard library; existing Router registry, MCP launcher, approval broker, source catalog, Spec Kit, IDE asset generator.  
**Storage**: Atomic JSON run records below `SAP_ROUTER_STATE_DIR/harness-runs`; approval records remain owned by `approval_broker.py`.  
**Testing**: `unittest`; temporary state; fake CLI/MCP processes; strict catalog, IDE asset, packaging, ABAP review, and offline evaluation gates.  
**Target Platform**: Windows and POSIX hosts supported by current scripts; Codex and Claude CLI only.  
**Project Type**: Python CLI with generated skill mirrors and JSON registries.  
**Performance Goals**: One maker and one independent checker model call per proposed operation; caps of 8 iterations, 15 minutes/run, and 120 seconds/call.  
**Constraints**: No native tools or model-managed MCP; no package installs; no backend fallback; no credentials in model prompt; no mutation before approval; no unreviewed tool calls.  
**Scale/Scope**: 38 profiles, 203 canonical skills, current capability/server registries, and external candidates that remain fail-closed unless explicitly promoted.

## Constitution Check

- Karpathy: assumptions, minimum route, and measurable outcomes recorded; changes stay at responsible ownership boundaries.
- Specification: active feature, plan, tasks, and analyzer run precede implementation.
- SAP controls: broker remains mutation authority; capability/profile/transport gates remain independent.
- Verifiable delivery: fake process tests prove executor behavior; no live SAP claim without field evidence.

## Design

1. **Canonical policy**: Add local verification-loop skill and shared profile protocol metadata. Executor composes Karpathy, domain skill, loop and verifier procedures. Generated Claude/Gemini trees use current generator.
2. **Registry contract**: Add `harness-tool-contracts.json`; pin tool schema digest and effect. Resolve enabled server, exact profile permission, capability effect, route, and MCP capability in one deterministic check. Missing or inconsistent contract blocks.
3. **CLI adapters**: One adapter per backend. Use selected CLI only, disable native tools/MCP, temp cwd, structured output, bounded timeout, credential-scrubbed subprocess environment, and sanitized logs.
4. **Execution loop**: Deterministic precheck, maker proposal, schema/policy validation, fresh-process checker, MCP call, deterministic result check, durable checkpoint, bounded next iteration. Checker cannot broaden permissions.
5. **Approval/resume**: Bind exact arguments/target/preconditions in existing broker; return `PENDING_APPROVAL`; resume by opaque run ID. Reserve before mutation; consume after confirmed result. Unknown outcome quarantines run.
6. **Catalog and audit corrections**: Record nine SHAs and review notes as disabled candidates. Repair missing capability lookup/profile grants, installer bypass, effect mismatch, aliases, ZIP duplicate validation, secret false positive, driver path, CPI runtime text, pipeline state reporting, and live-eval false positive.
7. **Review**: Run Spec Kit analyzer after artifacts; apply TDD red/green for behavioral corrections; review final diff and run verification gates.
8. **External candidate implementation**: Keep ABAPilot disabled behind a DEV-specific target profile and strict local consistency validators; import OData CLI as skill-only; refresh the Basis snapshot from its pinned upstream revision; regenerate IDE mirrors and retain SAP-side verification as an explicit blocked gate.

## Project Structure

```text
scripts/harness_executor.py
scripts/harness_mcp_client.py
scripts/harness_contracts.py
scripts/sap_harness.py
scripts/source_catalog.py
scripts/validate_catalog.py
scripts/cpi_iflow_packager.py
scripts/secret_audit.py
.agents/registries/harness-tool-contracts.json
.agents/registries/harness-candidates.json
.agents/skills/verification-loop/SKILL.md
.agents/profiles/*.json
tests/test_harness_executor.py
tests/test_harness_contracts.py
tests/test_consistency_regressions.py
specs/001-controlled-agent-execution/
```

## Risks and Decisions

- MCP tools lack a universal effect field. Static contracts and schema fingerprints define execution boundary; absent contract means blocked.
- Remote mutation can have uncertain outcome after timeout. Quarantine for reconciliation; never retry automatically.
- Nonterminal run state expires 24 hours after its UTC creation timestamp; `status` persists a local `Blocked` transition at the exact boundary. Approval expiry and execution budget remain separate clocks.
- Model cost/provider access depends on operator account. Fail explicitly; never switch backend.
- SAP credentials stay available to MCP subprocess where authentication needs them, but are excluded from model subprocesses, prompts, and run records.
- `shrek-abaper/sap-functional-skill` overlaps existing locked bundle; record new SHA without replacing prior snapshot.
- `manoj-iflowdev/...` declares MIT in package metadata without repository license file; `aztun-neru/hermes-pm-skill` has no license. Keep both blocked.

## Verification

1. Add red regressions for each repaired behavior and safety boundary.
2. Confirm each fails for the expected reason, implement minimum fix, then verify green.
3. Run focused suite after each layer; run full offline suite at convergence.
4. Run strict catalog, IDE mirror, packaging, ZIP, secret audit, and ABAP gates.
5. Run offline harness evaluation.
6. Run both fake CLIs against fake MCP, covering reads and brokered resume/replay.
7. Label SAP checks `NOT_RUN` unless real target evidence is collected.
