# Feature Specification: Controlled Agent Execution and Catalog Harness

**Feature Branch**: `001-controlled-agent-execution`  
**Created**: 2026-10-01  
**Status**: Local implementation complete; selected SAP DEV validation is blocked by missing target prerequisites  
**Input**: Implement the reviewed SAP Router consistency plan. Support controlled Codex CLI and Claude CLI execution, skill-agent loops and verification, and retain the nine initially reviewed repositories as disabled harness candidates. The follow-up review covers seven more projects: ABAPilot is selected for a blocked DEV profile; OData Go/Python, SAP GUI, and SuccessFactors alternatives remain disabled; OData CLI and Basis are guidance-only skill imports.

## User Scenarios & Testing

### User Story 1 - Run a bounded agent task (Priority: P1)

An operator selects a task, agent profile, and Codex or Claude backend. Harness resolves local skills and capability, asks the selected CLI for one structured operation proposal at a time, and runs only a reviewed operation allowed by that profile and route.

**Why this priority**: The current harness only prints plans; controlled execution is the requested primary outcome.

**Independent Test**: Fake both CLIs and a local stdio MCP server; run an allowed read task and observe a verified tool call and terminal report without a SAP connection.

**Acceptance Scenarios**:

1. **Given** a routable read request and approved tool contract, **When** operator uses `run --execute --backend codex`, **Then** Codex proposes one call, independent checks pass, the tool runs, and result is verified.
2. **Given** the same request with `--backend claude`, **When** run executes, **Then** Claude follows the same envelope and safety gates with no fallback to Codex.
3. **Given** an unavailable CLI, malformed proposal, unknown tool, or profile mismatch, **When** execution starts, **Then** harness stores a terminal blocked state and performs no MCP call.
4. **Given** no `--execute`, **When** operator requests a task, **Then** harness only plans and does not invoke a model or MCP tool.

### User Story 2 - Gate mutations and resume safely (Priority: P1)

An agent proposes a mutating operation. Harness binds exact capability, target, tool, arguments, and preconditions into the approval broker plan, stops, and resumes only after a valid one-time approval.

**Independent Test**: Use a temporary state directory and mock broker. Assert pending approval makes zero tool calls, changed arguments/target and replay fail, and one matching approval runs at most once.

**Acceptance Scenarios**:

1. **Given** a mutating operation, **When** first proposed, **Then** run ends `PENDING_APPROVAL` with plan identifiers and no mutation.
2. **Given** an approved unchanged plan, **When** operator resumes, **Then** broker reserves approval before call and consumes it only after a confirmed result.
3. **Given** expired approval, modified input, ambiguous tool outcome, or resumed run with incompatible version, **When** resumed, **Then** execution fails closed and never retries the mutation automatically.

### User Story 3 - Verify loops and preserve durable state (Priority: P1)

Each run has named skills, a verifiable goal, maker/checker separation, deterministic constraints before model review, bounded iteration/time/call budgets, durable sanitized state, and a named terminal state.

**Independent Test**: Fake CLI responses for success, no-op, failed checker, repeated proposal, timeout, interruption, and exhausted limits. Assert state and stopping reason survive process restart.

**Acceptance Scenarios**:

1. **Given** a successful field result, **When** deterministic and independent verification pass, **Then** run ends `Success` with evidence level and output reference.
2. **Given** no change is needed, **When** checker confirms the goal already holds, **Then** run ends `No-Op`.
3. **Given** verifier failure, repeated proposal, backend timeout, unavailable SAP, or hard budget cap, **When** condition occurs, **Then** run ends `Blocked`, `Stalled`, or `Exhausted` with reason and resumable state where safe.
4. **Given** model response includes shell instructions, secrets, or unsupported capability, **When** harness validates it, **Then** response cannot expand tool permissions or inject credentials into prompt.

### User Story 4 - Search reviewed external harness candidates (Priority: P2)

An operator can inspect the nine requested GitHub projects by immutable revision, license status, usefulness, and review constraints. Each stays a disabled candidate until explicitly promoted through repository review.

**Independent Test**: Validate registry and source catalog search; assert all nine are discoverable, have immutable commit identifiers and licensing notes, and none route or launch.

**Acceptance Scenarios**:

1. **Given** a source search, **When** one candidate is relevant, **Then** results identify it as disabled and show its reviewed revision.
2. **Given** a candidate ID passed as an agent/profile/MCP, **When** a run resolves it, **Then** route selection rejects it.
3. **Given** a candidate with absent or ambiguous licensing, **When** displayed, **Then** it stays disabled with an explicit blocker.

### User Story 5 - Prepare a selected external candidate safely (Priority: P2)

An operator selects a candidate and environment before activation. If backend, target identity, runtime, schemas, or authorization evidence is incomplete, the Router records a target-specific blocked profile and keeps the candidate disabled and non-routable.

**Independent Test**: Validate an ABAPilot DEV profile offline; assert an immutable source/package pin, HTTPS/TLS requirements, read-only allowlist, denied mutation tools, explicit blockers, no installed runtime, no active MCP registration, and rejection of policy drift.

**Acceptance Scenarios**:

1. **Given** ABAPilot MCP is selected for DEV but exact system/backend details are absent, **When** the profile is validated, **Then** it remains blocked and cannot route or start a package installer.
2. **Given** the local connector allowlist includes a mutation or TLS verification is disabled, **When** strict validation runs, **Then** the catalog rejects the profile.
3. **Given** a repository contributes skill guidance without an executable runtime, **When** imported, **Then** provenance/license are pinned and the skill registry does not imply CLI installation or MCP registration; the selected OData CLI and Basis guidance follows this rule.
4. **Given** an OData, SAP GUI, or SuccessFactors MCP alternative was not selected for the DEV trial, **When** the selected ABAPilot profile is prepared, **Then** those alternatives stay disabled and no runtime is enabled or launched for them by this feature.

### Edge Cases

- CLI missing, wrong version, invalid output schema, truncated output, timeout, interruption, or non-zero exit.
- MCP initialize/list/call timeout, oversized message, error result, duplicate JSON-RPC IDs, or subprocess crash.
- Capability absent from MCP specs, effect mismatch across registries, profile missing permission, unknown profile/skill, or stale server contract.
- Approval expiry, target drift, argument drift, interruption during mutation, or unknown outcome after network failure.
- State corruption, symlink/path escape, run ID traversal, sensitive argument keys, or oversized task/tool payload.
- Upstream candidate revisions change after review; stored evidence continues pointing at the audited commit.

## Requirements

### Functional Requirements

- **FR-001**: Planning remains default. Real execution requires explicit `--execute` and backend `codex` or `claude`.
- **FR-002**: Backend stays pinned per run; no implicit fallback or model change.
- **FR-003**: Agent and skill aliases resolve to existing canonical profiles, skills, and capabilities before model invocation.
- **FR-004**: Both CLIs receive structured schemas, isolated temporary working directories, bounded timeouts, and no native shell, browser, computer, plugin, or MCP access.
- **FR-005**: Harness strips SAP/MCP credentials from model subprocess environments and never places credentials in prompts, run logs, or candidate metadata.
- **FR-006**: Harness executes only a reviewed `(server, capability, tool, effect)` contract whose schema fingerprint matches MCP `tools/list`.
- **FR-007**: Harness validates routed capability, server status, route/profile permissions, declared effects, argument schema, and target before a tool call.
- **FR-008**: Read operations execute without approval only when canonical capability and reviewed tool contract both declare `read`.
- **FR-009**: Mutations require broker plan bound to exact arguments, target, and preconditions; a pending plan never calls MCP.
- **FR-010**: Approval is one-time. Harness begins through broker before mutation and consumes after confirmed completion. Uncertain outcomes block replay.
- **FR-011**: Independent checker uses a fresh CLI process and receives task, profile permissions, contract, and proposal, without maker reasoning. Model approval cannot override deterministic rejection.
- **FR-012**: Every run implements terminal states `Success`, `No-Op`, `Blocked`, `Stalled`, and `Exhausted`; hard limits: 8 iterations, 15 minutes/run, 120 seconds/model call, and 3 repeated non-progress proposals. Operators may lower limits only.
- **FR-013**: Run state persists below `SAP_ROUTER_STATE_DIR` (or `.sap-router/`) with local permissions, size caps, sanitized observations, backend, checkpoint, verifier evidence, and terminal state.
- **FR-014**: `status` and `resume` address opaque run IDs; unsafe, expired, corrupt, or version-incompatible state fails closed.
- **FR-015**: Skill execution loads canonical Karpathy plus named domain skills, loop specification, and verification procedure. Mirrors regenerate from `.agents/`.
- **FR-016**: Validation records command, outcome, output summary, and evidence level 1-5. Unavailable checks cannot be reported as passed.
- **FR-017**: Capability, MCP effect, approval, profile permission, route, and tool-contract inconsistencies fail strict validation; unknown capability returns a structured error.
- **FR-018**: Active `.mcp.json` entries cannot invoke package installers; local launcher requires an installed pinned runtime and canonical enabled server.
- **FR-019**: ZIP validation rejects duplicate or traversal entries. Secret audit distinguishes static XML policy templates from credentials while detecting synthetic token samples.
- **FR-020**: All nine repositories are in an immutable-revision candidate registry, searchable, disabled, non-routable, and never fetched at runtime.
- **FR-021**: Existing aliases map to canonical installed profiles and skills or fail clearly; no silent profile substitution.
- **FR-022**: Fake CLI/MCP processes cover safety and contract behavior. Live SAP verification is `NOT_RUN` without field evidence.
- **FR-023**: Nonterminal run records expire 24 hours after their UTC `created_at` timestamp; the exact 24-hour boundary is expired. `status` changes an expired nonterminal record to `Blocked` with reason `run-state-expired` and persists that local transition. `resume` never starts MCP or approval-broker actions for an expired record. Terminal records remain queryable. Run-state expiry is independent of approval expiry and the execution-time budget.
- **FR-024**: A selected external MCP candidate with incomplete backend, target, runtime, schema, or authorization evidence has a target-specific profile that records immutable source/runtime references, target facts, environment-variable names only, default-deny tool policy, and blockers; it remains disabled and non-routable until the gates are reviewed.
- **FR-025**: External skill/documentation imports record immutable source and license evidence and an explicit skill-only classification; importing guidance cannot install or register a CLI/MCP runtime.

### Key Entities

- **Run**: Opaque ID, task digest, profile, backend, capability, budgets, checkpoint, evidence, terminal state.
- **Proposal**: One contract-bound MCP call or completion claim, exact arguments, target, goal, and verification criteria.
- **Tool contract**: Reviewed server/capability/tool/effect tuple, pinned input-schema digest, constraints, verifier policy.
- **Approval plan**: Existing broker record bound to one-time approval, exact operation, and preconditions.
- **Harness candidate**: Repository URL, audited SHA, license evidence, usefulness, blockers, disabled status.
- **Loop specification**: Trigger, verifiable goal, named skills, execution step, verifier, stopping rules, durable state.

## Success Criteria

- **SC-001**: Codex and Claude fake backends complete the same read-only fixture through one verified local MCP call.
- **SC-002**: Negative tests for missing backend, schema mismatch, denied profile, unknown tool, checker failure, expired approval, and replay make zero unauthorized calls.
- **SC-003**: Mutating fixture completes only after one matching approval and cannot run twice.
- **SC-004**: All 38 canonical profiles expose loop and verification procedures; IDE check reports no mirror drift.
- **SC-005**: All nine external repositories appear in search with audited SHA and disabled status; candidates do not count as enabled servers.
- **SC-006**: Strict catalog, repository tests, packaging, ZIP checks, and offline harness eval pass. SAP live checks remain `NOT_RUN` without real target evidence.
- **SC-007**: The selected ABAPilot DEV profile passes strict local validation only while its source/package pins, HTTPS/TLS policy, read-only allowlist, server-side authorization requirement, disabled status, and missing-runtime state are intact; regression tests reject mutating tools and installer drift. SAP validation remains `NOT_RUN` until field evidence exists.
- **SC-008**: The OData CLI skill-only import and Basis source refresh pass source/license/hash validation and IDE parity without registering or installing executable runtimes; the final report records which operational checks remain `NOT_RUN`.

## Assumptions

- Operator already authenticated the chosen CLI. Harness uses that backend only and does not install, update, or configure global state.
- SAP/MCP calls require enabled local servers and reviewed tool contracts.
- Existing broker remains authority for mutation approval; transport controls stay separate.
- Repo root is trusted local project; run records contain no credentials.
- Upstream candidate repos are references, not executable dependencies; licensing is recorded at inspected revisions.
