---
name: sap-self-learn
description: >-
  Hermes-style self-improvement engine for SAP Router. Learns from every MCP
  interaction, tracks latency/reliability, adapts routing preferences, discovers
  SAP system features, remembers user patterns. Auto-optimizes over time —
  faster MCPs rise, unreliable paths fall. Persists learned context in MEMORY.md
  LEARN section. Use when system needs to adapt to environment, learn from
  past failures, or optimize routing based on historical data. Triggers on:
  "learn from", "adapt routing", "optimize MCP", "self improve", "track performance",
  "remember pattern", "system learning", "routing history", "MCP stats".
---

# SAP Self-Learn — Hermes-Style Environment Adaptation

Builds internal knowledge graph from every SAP interaction. Like Hermes agent
but focused on SAP development workflows — MCP performance, routing success,
system quirks, user preferences.

## Philosophy (Andrej Karpathy)

```
measure → learn → adapt → repeat
```

Never route blindly. Every decision backed by data. Track what works,
deprecate what fails, discover what's possible.

## Architecture

```
Every MCP Call
    │
    ▼ Timestamp, latency, success/fail, error
┌──────────────────────────────┐
│   Self-Learn Engine           │
│                               │
│  1. Record observation        │
│  2. Update EMA statistics     │
│  3. Adapt routing weights     │
│  4. Persist to MEMORY.md      │
│     ## LEARN section          │
└──────────┬───────────────────┘
           │
           ▼ Context injected into every prompt
┌──────────────────────────────────────────────┐
│  MCP_RELIABILITY: arc-1=98% aibap=95% ...   │
│  SYS: hana=2.0 s4h=2023 gcts=true ...        │
│  PATTERNS: material_create→ZROUTER ...        │
└──────────────────────────────────────────────┘
```

## Integration with sap_router.py

```python
# After every routing decision:
from scripts.self_learn import SelfLearnEngine

engine = SelfLearnEngine()
engine.load_history()

# Record MCP call outcome
engine.record_mcp_call(
    mcp_name='arc-1',
    latency_ms=245,
    success=True
)

# Adapt route based on history
adapted = engine.adapt_route('MM_CREATE_MATERIAL', primary_route)
if adapted.get('confidence', 0.5) < 0.3:
    # Low confidence — try alternative
    ...

# Persist learned context
engine.persist()
```

## CLI Commands

```bash
# Record MCP call outcome
python scripts/self_learn.py record-mcp --mcp arc-1 --latency 245 --success true

# Record routing outcome
python scripts/self_learn.py record-route --action MM_CREATE_MATERIAL --success true

# Get best MCP among candidates
python scripts/self_learn.py best-mcp --candidates "arc-1,aibap,mcp-abap-adt"

# Get learned context for prompt injection
python scripts/self_learn.py context

# Force persist to MEMORY.md
python scripts/self_learn.py persist

# Discover SAP system feature
python scripts/self_learn.py discover --feature hana_version --value "2.00.080.00"
```

## MEMORY.md LEARN Section Format

```markdown
## LEARN
- sys:adt_version 2.115
- sys:basis_release 757
- sys:gcts true
- sys:hana_version 2.00.080.00
- sys:rap_version managed
- mcp:aibap latency:180ms success:0.92 last:2026-06-26T14:30:00
- mcp:arc-1 latency:245ms success:0.98 last:2026-06-26T14:35:00
- mcp:mcp-abap-adt latency:350ms success:0.85 last:2026-06-26T14:20:00
- mcp:mcp-sap-gui latency:1200ms success:0.75 last:2026-06-26T12:00:00
- route:MM_CREATE_MATERIAL total:45 ok:43 fail:2
- route:BASIS_CODE_SEARCH total:30 ok:28 fail:2
- pattern:mass_material_create ZROUTER prefer_batch_for_50plus
- pattern:quick_source_read ADT prefer_direct_for_single_classes
```

## Auto-Discovery

Self-learn engine automatically discovers:

| Feature | Detection Method |
|---|---|
| ADT version | Parse `arc-1 SAPDiagnose` output |
| Basis release | Parse `aibap system_info` output |
| HANA version | Parse `sap_hana_query SELECT * FROM M_DATABASE` |
| gCTS available | Probe `aibap gcts_list` success |
| RAP version | Probe CDS view with managed scenario |
| BTP subaccount | Parse `btp-mcp list_subaccounts` |
| CPI tenant | Probe `sap-cpi list_packages` |

## Routing Adaptation

When confidence drops below threshold, self-learn suggests alternatives:

```
Primary route confidence: 0.25 (5 failures in 20 attempts)
Alternatives:
  1. ADT direct (confidence: 0.92) — recommended
  2. GUI fallback (confidence: 0.85)
  3. ZROUTER RFC (confidence: 0.45) — same failure pattern
```

## Gotchas

- **Cold start**: No history → neutral routing (no bias). Confidence stays 0.5 until 3+ observations.
- **Decay**: Stats decay over 24h half-life. Recent performance matters more.
- **No persistence on error**: Failed calls recorded but don't corrupt stats. 30% EMA weighting.
- **Context injection**: Learned context auto-injected into every LLM prompt for routing decisions. ~50 tokens overhead.
- **Memory budget**: LEARN section capped at 50 lines. Older stats archived as ARCHIVE_LEARN.
