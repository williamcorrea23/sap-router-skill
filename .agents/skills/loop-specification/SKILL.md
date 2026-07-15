---
name: loop-specification
description: Framework for designing, verifying, and executing autonomous loop specifications for SAP tasks (arXiv:2607.00038)
trigger:
  keywords: [loop engineering, loop specification, autonomous agent loop, agent verification ladder, maker-checker loop, ralph loop, sandeco-loop]
  intent: Designing or running autonomous reasoning/execution loops with verification and stopping rules.
---
# Loop Specification — Engineering Autonomous Loops

Adapts the loop engineering methodology from **arXiv:2607.00038** ("Stop Hand-Holding Your Coding Agent: Engineering the Loops that Replace Step-by-Step Prompting") for SAP development pipelines (ABAP, CPI, BTP, SAP GUI).

Instead of prompting the agent at every step, design a bounded, reusable **Loop Specification** that allows the agent to pursue a goal autonomously while ensuring correctness and preventing runaway execution.

## The Loop Specification Anatomy

Every loop specification must compile five core pieces and a persistent memory structure:

```
                  ┌────────────────────────┐
                  │        TRIGGER         │
                  └───────────┬────────────┘
                              ▼
                  ┌────────────────────────┐
                  │    GOAL & MEMORY       │◄────────┐
                  └───────────┬────────────┘         │
                              ▼                      │
                  ┌────────────────────────┐         │
                  │   EXECUTION (SKILLS)   │         │
                  └───────────┬────────────┘         │
                              ▼                      │
                  ┌────────────────────────┐         │ Iteration
                  │      VERIFICATION      │         │
                  └───────────┬────────────┘         │
                              ├──────────────────────┘
                              ▼
                  ┌────────────────────────┐
                  │   STOPPING RULE        │
                  │ (Named Terminal State) │
                  └────────────────────────┘
```

1. **Trigger**: When the loop starts (Manual, Scheduled, or Event-driven like a PR).
2. **Goal**: The desired target condition (must be verifiable).
3. **Execution**: The action phase. The agent must execute named, tested skills (e.g. `sap-crew-analysis`, `sap-transport-gate`, `abap-unit-testing`) rather than raw unbounded generation.
4. **Verification**: A strict check that validates the turn output.
5. **Stopping Rule**: Conditions that force loop exit into a **named terminal state** (Success, No-Op, Blocked, Stalled, Exhausted).
6. **Memory**: Durable state stored on disk (e.g. in `MEMORY.md` or a JSON file) to persist plan and decisions across turns without bloating the prompt context.

---

## The 5-Level Verification Ladder

Align your verification checks strictly against the ladder. Be honest about the level of verification.

| Level | Type | SAP Context Example | Autonomy / Trust |
|---|---|---|---|
| **Level 1** | Deterministic | Exit codes, `abaplint` JSON validation, signature matches | **Autonomous** / Absolute trust |
| **Level 2** | Text Rule / Constraint | Regular expression policy check, schema validation | **Autonomous** / High trust |
| **Level 3** | Delayed Field Truth | Automated ABAP Unit tests green, CPI message status | **Autonomous** / High trust (Slow) |
| **Level 4** | Model-as-Judge | Rubric-based LLM rating of custom logic, code review | **Assisted** / Moderate trust |
| **Level 5** | Human Checkpoint | Release Transport Request, production deploy | **Assisted** / Human gate |

> [!IMPORTANT]
> **The Golden Rule:** A loop is only as autonomous as its verification level. Avoid using Level 4 verification as if it were Level 1.

---

## Design Principles for SAP Loops

### 1. Maker-Checker Separation
Never let the same agent session or prompt generate code and also judge its correctness.
*   *Action:* Use a separate checker agent, or use deterministic checks (Level 1/2/3) for validation. If using a model-as-judge (Level 4), break the prompt context between the maker and the checker.

### 2. Surgical Turn Scope (One Change per Turn)
Do not let the agent rewrite multiple objects or methods in a single loop step.
*   *Action:* Prohibit the agent from touching adjacent code. Ensure a single modification, execute checks, record state, and verify.

### 3. Proven Verifier (Red-Before, Green-After)
Ensure tests or checks can fail. A test that always passes is a silent failure.
*   *Action:* Write the test/linter check first, verify it fails, then execute the fix and verify it passes.

### 4. Cost Per Accepted Change
Measure efficiency. Keep track of token spend divided by the number of changes that survived verification.
*   *Action:* Track execution costs and log stagnation if token budget is burning without approved changes.

---

## Anti-Patterns to Avoid

*   **While-True Around a Stranger:** Wrapping a raw LLM call in a retry loop with no real verifier or named skills. The model will just repeat its errors or agree with itself.
*   **Self-Approving Loop (Reward Hacking):** Generator model grades its own work. The grade drifts to 100% while actual quality decreases.
*   **Specification Gaming:** The agent changes the test or linter configuration to pass instead of resolving the bug in the code.
*   **Unattended Runaway:** A loop with no token/iteration limit or stagnation detector, executing loops endlessly.

---

## Loop Specification Template (`<name>-loop.md`)

Use this skeleton when authoring loop specifications:

```markdown
# [Name] Loop Specification

## 1. Metadata
- **Trigger:** [Manual | Schedule | Event]
- **Goal:** [Verifiable description]
- **Verification Level:** Level [1-5]

## 2. Anatomy
### Execution (Skills called)
- Skill 1
- Skill 2

### Verification Command
- `[Command to execute for verification]`

### Stopping Rules & Terminal States
- **Success:** [Criteria]
- **No-Op:** [Criteria]
- **Blocked:** [Criteria]
- **Exhausted:** [Iteration/budget cap]

### Durable Memory
- State stored in: `[Path to file]`
- Schema/Format: `[Format details]`

## 3. Surgical Run Turn Steps
1. Read current state from memory.
2. Verify baseline (Red-before check).
3. Execute modification (surgical scope).
4. Run verification command.
5. Record outcome to memory.

## 4. Guardrails & Human Approvals
- Require human gate before executing: `[Irreversible action]`
```

---

## Actuation Patterns

### 1. Context-Bounded Loop (`/goal` command)
If the task context fits in a single window, pass the Loop Specification markdown document to the agent harness with a `/goal` prefix.

### 2. Context-Refreshed Loop (Ralph Pattern)
For long-horizon tasks (e.g. multi-object SAP refactoring):
*   Write a runner shell script that calls the agent harness.
*   Each turn runs in a fresh process with a clean context.
*   All state (plan, file changes, test outputs) is read from and written to files on disk.

---

## Verification Checklist for new loops

- [ ] Loop specification triage completed (iteration changes next action)
- [ ] Goal is verifiable (Levels 1-3 preferred)
- [ ] Maker role separated from Checker role
- [ ] Named terminal states defined (Success, Blocked, Stalled, Exhausted)
- [ ] Maximum iteration and budget limit defined
- [ ] Durable memory located on disk, not in context history
- [ ] Human gate added to any destructive actions (e.g. releasing transport requests)
