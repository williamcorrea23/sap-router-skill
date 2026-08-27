---
name: sap-incident-resolution
description: >-
  SAP intelligent incident resolution and self-healing engine. Use when investigating
  system dumps (ST22), analyzing lock entries (SM12), triaging failed background jobs (SM37),
  diagnosing update errors (SM13), resolving CPI/RFC communication breakdowns, or triggering
  automated self-healing remediation plans under fail-closed approval gates.
trigger:
  - sap incident
  - st22 dump analysis
  - sm12 lock triage
  - sap self-healing
  - incident resolution
  - background job failure
  - sap sm37 error
---

# SAP Intelligent Incident Resolution & Self-Healing Agent

Automated triage, root-cause analysis, and remediative self-healing for SAP landscapes (ABAP, CPI, S/4HANA, NetWeaver).

## Incident Domains Covered

| Domain | Detection Tool | Diagnostic Action | Remediation / Self-Healing |
|---|---|---|---|
| **ABAP Short Dumps** | ST22 / SNAP table | Parse error class, line number, termination point | Generate patch via ADT/ZROUTER or suggest OSS note |
| **Lock Collisions** | SM12 | Inspect lock arguments, user, duration | Suggest enqueue dequeue with safety checks |
| **CPI Message Failures** | MPL / Trace | Error step isolation, payload inspection | Automated re-trigger, error subprocess routing |
| **Background Jobs** | SM37 / TBTCO | Job log analysis, step variant verification | Reschedule with corrected parameters |
| **RFC / Communication** | SM59 / SM21 | Ping RFC destination, check gateway buffer | Reconnect destination, verify SNC / credentials |

## Autonomous Execution Rules

1. **Diagnosis is Always Read-Only**: Diagnostics through `sap.incident.resolution.diagnose` or `arc-1` / `ST22_SCAN` never modify system state.
2. **Remediation Requires Explicit Approval**: Any write, cancellation, or restart must go through `approval_broker.py` plan-and-commit.
3. **Audit Trail**: Every incident step, diagnostic hypothesis, and resolution outcome is logged in `MEMORY.md`.

## Harness Integration

Run automated incident triage directly through the harness:

```bash
# Run incident triage on latest dumps
python scripts/sap_harness.py run --agent sre --task "diagnose recent ST22 dumps and lock conflicts"

# Evaluate incident resolution capability in sandbox
python scripts/sap_harness.py eval --scenario incident_triage
```
