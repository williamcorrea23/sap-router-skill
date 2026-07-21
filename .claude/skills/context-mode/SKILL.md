---
name: context-mode
description: |
  Context window optimization for AI coding agents. Sandboxes tool output (98% reduction),
  persists session memory across compactions, and enforces routing across 17 platforms via
  MCP + hooks. Use when context window is filling up, tool outputs are too large, or
  session state needs to survive compaction. Works with Antigravity, Claude, Cursor,
  Codex, Copilot, OpenCode, and more.
  Source: https://github.com/mksglu/context-mode — MCP-layer sandboxing, local-only, no telemetry.
triggers:
  - context window
  - context optimization
  - session memory
  - compaction
  - ctx_execute
  - ctx_fetch
  - MCP sandbox
  - tool output size
  - 98% reduction
  - context mode
  - ctx-stats
---

# Context Mode Skill

**Context Mode** operates at the MCP protocol layer to sandbox tool outputs, persist session memory across compactions, and enforce routing across 17 AI platforms. **Nothing leaves your machine** — no telemetry, no cloud sync, all SQLite-local.

## Local Reference
```
sap-router-skill\bundled\tools\context-mode\
```

## Core Capabilities

| Problem | Context Mode Solution |
|---------|----------------------|
| Tool output too large (7 MB API response) | `ctx_fetch_and_index` → 1.8 KB indexed summary |
| Context compaction loses session state | `ctx_checkpoint` persists tasks, files, decisions |
| 20 Jira MCP calls flood context | Wrap with `ctx_execute` → compact result |
| Can't continue after compaction | `ctx_restore` rebuilds full session state |

## Installation

```bash
# Repository-owned snapshot (already bundled)
cd bundled/tools/context-mode
npm install

# Initialize for your agent (from project directory):
# Claude Code
npx context-mode init

# Antigravity (Gemini) — copies .agents plugin files
npx context-mode init --agent antigravity

# Codex
npx context-mode init --agent codex

# Cursor  
npx context-mode init --agent cursor

# Copilot
npx context-mode init --agent copilot

# OpenCode
npx context-mode init --agent opencode
```

## MCP Tools Available

### Execution Sandbox
```
ctx_execute          - Run code in isolated subprocess, return compact result
ctx_execute_file     - Run code over a file (project-boundary confined)
ctx_batch_execute    - Run multiple operations, aggregate summary only
```

### Fetch & Index
```
ctx_fetch_and_index  - Fetch URL, store raw in SQLite, return <2 KB summary
                       Blocks dangerous schemes/IPs by default
```

### Session Memory
```
ctx_checkpoint       - Save current session state (tasks, files, decisions)
ctx_restore          - Restore full session state after compaction
ctx_stats / ctx-stats - Show session event count, token savings, context health
ctx_doctor           - Diagnose storage config and environment
```

## Security Model

Context Mode enforces **your existing Claude/agent permission rules** inside the sandbox:

```json
{
  "permissions": {
    "deny": [
      "Bash(sudo *)",
      "Bash(rm -rf /*)",
      "Read(.env)",
      "Read(**/.env*)"
    ],
    "allow": [
      "Bash(git:*)",
      "Bash(npm:*)"
    ]
  }
}
```

Add to `.claude/settings.json` or `~/.claude/settings.json`. All 17 platforms read this same format.

- **`deny` always wins** over `allow`
- **Project-level rules** override global
- **`ctx_execute_file`** is confined to project root — path traversal (`../../`) blocked
- **Credentials auto-redacted**: tokens, API keys, secrets masked to `[REDACTED]` before SQLite

## Network Fetch Hardening

`ctx_fetch_and_index` blocks by default:
- `file://`, `gopher://`, `javascript:`, `data:` schemes
- Cloud metadata: `169.254.169.254` (AWS/GCP/Azure IMDS)
- Multicast, reserved IPs

```bash
# Strict mode (blocks RFC1918 too — for CI/hosted envs):
export CTX_FETCH_STRICT=1
```

## Integration with SAP Router Skill

Context Mode is critical for SAP sessions that generate large outputs:

### Large Output Handling
```
# Instead of letting healthcheck flood context:
ctx_execute("python scripts/healthcheck.py")
# → compact: "35/35 MCPs healthy | 2 warnings: mcp-sap-gui timeout"

# Large ABAP search results via ADT:
ctx_execute("python scripts/sap_router.py code_search --query ZCL_ROUTER --max 500")
# → compact summary with file list

# iFlow package analysis:
ctx_execute("python scripts/cpi_iflow_packager.py validate --input my.zip")
# → "Valid: 12/12 artifacts | 0 errors"
```

### Session Memory for SAP Tasks
```
# Before starting long SAP task:
ctx_checkpoint({"task": "Implement ZROUTER_V3", "status": "planning", 
                "pending": ["create_class", "test_bapi", "transport"]})

# After compaction, agent restores:
ctx_restore()
# → Full task state recovered, no re-prompting needed
```

### Fetch & Index SAP Documentation
```
# Fetch large SAP Help page:
ctx_fetch_and_index("https://help.sap.com/docs/SAP_NETWEAVER/...")
# → 2 KB indexed summary instead of 500 KB raw HTML

# Then query the index:
ctx_execute("query indexed content for BAPI_PO_CREATE1 parameters")
```

## Storage Environment

```bash
# Custom storage location:
export CONTEXT_MODE_DIR="C:\Users\William Correa\.context-mode"

# MCP nudge frequency (re-inject routing guidance every N tool calls):
export CONTEXT_MODE_EXTERNAL_MCP_NUDGE_EVERY=10  # default
```

## Routing Nudge Behavior

Every 10th external MCP tool call (Jira, Slack, Notion, etc.), Context Mode re-injects:
> "Wrap large external-MCP payloads in `ctx_execute` for 98% context reduction"

This prevents guidance from being lost after compaction in long sessions.

## Commands Reference

```bash
ctx stats          # Session stats (tool calls, tokens saved, context %)
ctx checkpoint     # Save session state now
ctx restore        # Restore after compaction
ctx doctor         # Diagnose storage and env config
/context-mode:ctx-stats  # In-chat command
```

## References
- Repository: `bundled/tools/context-mode/`
- Contributing: `bundled/tools/context-mode/CONTRIBUTING.md`
- Issues tracker: https://github.com/mksglu/context-mode/issues
- Security: `bundled/tools/context-mode/SECURITY.md` (if present)
- License: Elastic License 2.0 (source-available, no SaaS repackaging)
