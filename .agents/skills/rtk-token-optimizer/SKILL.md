---
name: rtk-token-optimizer
description: |
  RTK CLI proxy that reduces LLM token consumption by 60-90% on common dev commands.
  Use when running git, cargo, npm, pytest, or any CLI tool inside an AI coding session.
  Rewrites verbose command outputs to compact summaries before they reach the context window.
  Supports Antigravity (Gemini), Claude Code, Cursor, Codex, Copilot, and 10+ other agents.
  Source: https://github.com/rtk-ai/rtk — offline-capable single Rust binary, zero deps.
triggers:
  - rtk
  - token savings
  - context reduction
  - LLM token
  - git log verbose
  - cargo test output
  - npm install output
  - reduce output
  - compress tool output
---

# RTK Token Optimizer Skill

**RTK** is a CLI proxy that intercepts shell commands and returns compact, LLM-optimized summaries instead of raw verbose output — saving 60-90% of token consumption.

## Local Reference
```
C:\Users\William Correa\tools\rtk\
sap-router-skill\references\rtk\
```

## What RTK Does

RTK wraps common dev commands and returns only what matters to the LLM:

| Command | Without RTK | With RTK |
|---------|------------|----------|
| `git log --oneline -50` | 50 lines of SHAs + messages | 10-line summary |
| `cargo test` | 200+ lines of test output | `PASSED: 47/47` or compact failure |
| `npm install` | 300+ lines of progress | `installed 142 packages` |
| `pytest -v` | Full verbose output | Summary table |

## Installation (Antigravity / Gemini)

RTK supports **Google Antigravity** via `.agents/rules/antigravity-rtk-rules.md`:

```bash
# Install RTK binary (Windows - via cargo)
cargo install rtk

# Or download pre-built binary
# https://github.com/rtk-ai/rtk/releases

# Initialize for Antigravity
rtk init --agent antigravity
```

This creates `.agents/rules/antigravity-rtk-rules.md` in your project, which instructs Antigravity to route shell commands through `rtk`.

## Initialization for All Supported Agents

```bash
rtk init -g                    # Claude Code (global)
rtk init -g --gemini           # Gemini CLI (global)
rtk init -g --copilot          # GitHub Copilot (global)
rtk init -g --agent cursor     # Cursor (global)
rtk init -g --codex            # Codex (global)
rtk init --agent antigravity   # Antigravity (project-scoped)
rtk init --agent kilocode      # Kilo Code (project-scoped)
rtk init --agent cline         # Cline / Roo Code (project-scoped)
```

## RTK Usage in Sessions

```bash
# RTK transparently intercepts these:
rtk git log --oneline -20
rtk cargo test
rtk npm install
rtk pytest tests/

# Analytics
rtk gain          # Token savings summary for current session
rtk gain --30d    # 30-day savings report

# Discovery
rtk discover      # Show which commands RTK optimizes in your project
rtk verify        # Verify hook is active for current agent

# Telemetry (opt-in only)
rtk telemetry status
rtk telemetry enable   # explicit opt-in
rtk telemetry disable
```

## Config (~/.config/rtk/config.toml)

```toml
[hooks]
exclude_commands = ["curl", "playwright"]  # skip rewrite for these

[tee]
enabled = true          # save raw output on failure
mode = "failures"       # "failures" | "always" | "never"
```

## Integration with SAP Router Skill

In the SAP Router context, RTK is especially useful for:

- **`git log`** when reviewing transport histories
- **`abaplint`** output compression (ABAP linting runs)
- **`pytest`** for SAP skill test runner output (`driver.py`)
- **Healthcheck output**: `python scripts/healthcheck.py` — RTK can compress the 35-MCP probe output

### SAP Router + RTK pattern:
```bash
# Instead of:
python scripts/healthcheck.py  # → verbose 35-MCP output

# Via RTK:
rtk python scripts/healthcheck.py  # → compact summary
```

## Token Saving Estimates

| Tool | Avg Savings |
|------|------------|
| git log/status/diff | 65-85% |
| cargo/rust | 70-90% |
| npm/yarn/pnpm | 60-75% |
| pytest/unittest | 70-85% |
| make/gradle | 55-70% |

## Uninstall

```bash
rtk init -g --uninstall    # Remove hooks
cargo uninstall rtk
```

## References
- Full guide: https://www.rtk-ai.app/guide
- Supported agents: https://www.rtk-ai.app/guide/getting-started/supported-agents
- Architecture: `references/rtk/docs/contributing/ARCHITECTURE.md`
- Hooks source: `references/rtk/hooks/`
