---
name: claude-mem
description: "Persistent cross-session memory architecture for AI coding agents. Captures session activity, generates AI-compressed observations, maintains searchable timeline indexes, and provides progressive 3-layer context retrieval across restarts."
license: MIT
trigger:
  keywords: [claude-mem, persistent memory, cross-session context, memory search, session observations, timeline anchor, context preservation, session continuity]
  intent: >-
    Search, recover, and manage persistent agent memory across sessions, using progressive token-optimized filtering (search -> timeline -> fetch).
---

# Claude-Mem — Persistent Cross-Session Memory Architecture

Persistent context and cognitive cache across sessions for AI coding assistants (Claude Code, Gemini Antigravity, Cursor, Codex).

## Overview

Claude-Mem captures session workflows, extracts key decisions, discoveries, and bugfixes into structured observations, indexes them chronologically, and provides progressive 3-layer retrieval to recover past context with minimum token overhead.

For full reference documentation, see:
- [Memory Search Guide](references/mem-search.md)
- [How Claude-Mem Works](references/how-it-works.md)
- [Learn Codebase Workflow](references/learn-codebase.md)
- [Context Injection Rules](references/claude-mem-context.md)

---

## 3-Layer Progressive Retrieval Workflow (MANDATORY)

**Never fetch full observation details without filtering first. This ensures up to 10x token savings.**

### Layer 1: Search — Index with IDs
Query the memory index using targeted search terms and type filters:
```bash
search(query="<topic>", limit=20, project="<project-name>")
```
**Output:** Lightweight index table (~50-100 tokens per result) containing ID, timestamp, type, and title:
| ID | Time | T | Title | Tokens |
|----|------|---|-------|--------|
| #1042 | 10:15 AM | 🟣 | Configured ADT REST endpoints | ~65 |
| #1088 | 02:30 PM | 🔴 | Fixed CSRF token expiration | ~50 |

Supported observation types (`obs_type`):
- `bugfix`: Defect resolution and root cause
- `feature`: Newly created capabilities and tools
- `decision`: Architectural decisions and design rationales
- `discovery`: Environment findings, ports, endpoints, credentials
- `change`: Refactorings, file moves, and dependency upgrades

### Layer 2: Timeline — Local Context Around Anchor
When an interesting observation is identified from Layer 1, inspect its chronological neighbors to understand preceding context and subsequent effects:
```bash
timeline(anchor=1088, depth_before=3, depth_after=3, project="<project-name>")
```

### Layer 3: Fetch — Read Selected Observations
Only fetch full markdown content for the specific observation IDs that are confirmed relevant:
```bash
get_observations(ids=[1088, 1042])
```

---

## Cognitive Priming (`learn-codebase`)

When onboarding onto a new or unfamiliar repository, systematically prime the cognitive cache:
1. Scan directory structure and package manifests.
2. Read foundational architecture specifications and entry points.
3. Record high-level structural notes into the persistent memory store.
4. Subsequent sessions query the cache via `search` instead of re-reading raw files.

---

## Session Continuity & Memory Gating

In this repository, Claude-Mem integrates with `scripts/memory_manager.py` and `MEMORY.md`:
- Active session context is maintained under 20 blocks / 100 lines total.
- Archived decisions and milestones are indexed into long-term storage.
- When an agent session restarts, verify memory state:
  ```bash
  python scripts/memory_manager.py verify --input MEMORY.md
  ```
