# Tasks: Controlled Agent Execution and Catalog Harness

**Input**: [spec.md](spec.md), [plan.md](plan.md)  
**Organization**: Test first for each source behavior; each regression test must fail before its fix.

## Phase 1: Specification and baseline

- [x] T001 Run repository Spec Kit classifier and create feature state in `.specify/feature.json`.
- [x] T002 Write requirements, design, and acceptance gates in this directory.
- [x] T003 Run `$speckit-analyze` prerequisites with this active feature and resolve inconsistencies. Analysis mapped the 22 requirements and 6 success criteria; Python floor aligned with the existing UTC APIs.
- [x] T004 Record starting status/diff; preserve unrelated local changes.

## Phase 2: Catalog and route consistency

- [x] T005 [P] Add failing regressions for missing capability, profile rights, effect mismatch, invalid aliases in `tests/test_consistency_regressions.py`.
- [x] T006 Repair cross-registry validation and structured unknown-capability result in `scripts/mcp_launcher.py`, `scripts/validate_catalog.py`, and `python/sap_router_core/registry.py`.
- [x] T007 Add required read permissions to BTP, HCM, Basis profiles; resolve aliases to canonical installed profiles and skills in `scripts/sap_harness.py`.
- [x] T008 Add failing regression for active `.mcp.json` installer bypass.
- [x] T009 Route active server startup through `mcp_launcher.py run`; preserve exact local pins and block installers.

## Phase 3: Candidate harness catalog

- [x] T010 Add tests proving all nine candidates searchable, SHA-pinned, disabled, non-routable.
- [x] T011 Add `.agents/registries/harness-candidates.json` with revision, license evidence, utility, and blockers.
- [x] T012 Add candidate search in `scripts/source_catalog.py` and strict schema checks in `scripts/validate_catalog.py`.
- [x] T013 Document promotion/review procedure in `docs/HARNESS_CANDIDATES.md`; forbid runtime fetching/execution.

## Phase 4: Agent loop and verifier procedure

- [x] T014 Add canonical `.agents/skills/verification-loop/SKILL.md` covering relevant checks and truthful `NOT_RUN`/blocked evidence.
- [x] T015 Add shared `execution_protocols` metadata to all 38 canonical JSON profiles; validate it.
- [x] T016 Update canonical router wrapper so each selected skill agent receives Karpathy, loop, verifier, named skills, strict checks, and terminal states.
- [x] T017 Regenerate Claude/Gemini mirrors; verify Codex/Cursor use canonical instructions. Generator parity check passed for all IDE targets.

## Phase 5: Controlled executor

- [x] T018 Add failing tests for backend, malformed output, forbidden tools, timeout, budgets, stagnation, terminal states in `tests/test_harness_executor.py`.
- [x] T019 Add deterministic capability/server/tool/effect/schema validation and fake MCP test support in `scripts/harness_contracts.py` and `scripts/harness_mcp_client.py`.
- [x] T020 Add Codex/Claude adapters using temp cwd, strict output schema, disabled native tools/MCP, and scrubbed environment.
- [x] T021 Add opaque durable run records, evidence, sanitization, atomic writes, `status`, and `resume`.
- [x] T022 Add deterministic verifier and fresh-process checker; model cannot override local rejection.
- [x] T023 Add explicit `--execute --backend` and keep plan-only default in `scripts/sap_harness.py`.
- [x] T024 Bind mutations to broker; pause for approval, reserve one-time plan, consume after success, quarantine uncertain outcomes.
- [x] T025 Define reviewed read contracts and a broker-only mutating fixture contract; other real tools stay blocked.

## Phase 6: Audit corrections

- [x] T026 Add red tests for duplicate/traversal ZIP entries; fix `scripts/cpi_iflow_packager.py`.
- [x] T027 Add red tests for static XML policy template; fix `scripts/secret_audit.py` without weakening token detection.
- [x] T028 Correct CPI Groovy/JavaScript runtime guidance in canonical skill.
- [x] T029 Correct run-skill driver path, stale registry counts, and pipeline state/reporting inconsistencies.
- [x] T030 Fix live ZROUTER eval; an environment variable alone cannot prove live domain success.

## Phase 7: Verification and convergence

- [x] T031 Run new regressions red-before-green; run focused suite after each layer and the full unit suite.
- [x] T032 Run strict catalog, IDE mirror, packaging, ABAP static review, offline harness evaluation, and secret-audit gates.
- [x] T033 Run fake Codex and Claude MCP paths, verified no-op, checker rejection, approval/resume/replay, target drift, expired approval, missing CLI, malformed/native-tool CLI responses, incompatible run state, schema mismatch, timeout, interruption, and exhausted-loop cases.
- [x] T034 Run final diff/security review and `$speckit-converge`; label live SAP verification `NOT_RUN` without field evidence.

## Phase 8: Peer-review remediation

- [x] T035 [C1] Add a red regression for nested credentials in structured and textual MCP results, including escaped values absent from the environment.
- [x] T036 [C1] Redact parsed credential fields before checker input and persistence; hash only sanitized observations.
- [x] T037 [C2] Add a red fake MCP regression that negotiates and then stops consuming stdin during a large request.
- [x] T038 [C2] Bound request writes and response waits by one deadline and terminate the blocked transport on expiry.
- [x] T039 [C3] Add red strict-catalog regressions for schema hash, effect, capability/server binding, duplicate contracts, and policy violations.
- [x] T040 [C3] Validate every reviewed harness tool contract against canonical registries during strict catalog validation.
- [x] T041 [C4] Add a red regression where initialization and `tools/list` consume the run budget; assert zero approval reservations and tool calls.
- [x] T042 [C4] Recheck the total run budget after model and MCP phases and immediately before broker or tool actions.
- [x] T043 [C5] Add a red executor regression for an unknown capability and assert a structured `Blocked` record with zero calls.
- [x] T044 [C5] Reject unknown capabilities before dereferencing them and persist the terminal blocked result.
- [x] T045 [U1] Define 24-hour run-state expiry and add controlled-clock regressions for the exact boundary, pending approval, terminal history, and resume.
- [x] T046 [U1] Persist the expired-state transition locally and prevent all broker/MCP activity on expired resumes.
- [x] T047 [D1] Add a failing documentation-floor check and probe availability of Python 3.11.
- [x] T048 [D1] Align the user-facing Python minimum with the harness plan and regenerate affected IDE instruction assets.

## Phase 9: External candidate implementation

- [x] T049 [FR-006, FR-007, FR-018, FR-020, FR-024, SC-007] Add a blocked ABAPilot DEV target profile with an immutable package/source pin, HTTPS/TLS policy, default-deny read allowlist, explicit denied tools, and no active runtime route.
- [x] T050 [FR-017, FR-022, FR-024, SC-007] Add strict catalog validation and regressions for target-profile consistency and rejection of write/installer policy drift.
- [x] T051 [FR-015, FR-020, FR-025, SC-008] Import the pinned SAP OData CLI skill and license as guidance-only; validate source hash and ensure no CLI/MCP runtime is implied.
- [x] T052 [FR-015, FR-016, FR-020, FR-025, SC-008] Refresh the SAP Basis bundle and canonical skills from the exact upstream revision; preserve the 21 new and 12 refreshed skills with license notices.
- [x] T053 [FR-016, FR-022, SC-004, SC-006, SC-007, SC-008] Update skill counts and integration docs, regenerate all IDE assets, and run the final offline verification gates; retain ABAPilot DEV execution and independent checklist review as open gates.
