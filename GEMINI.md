# SAP Router Skill

Canonical skills live in `.agents/skills`. Gemini/Antigravity may mirror skills into `.gemini/skills` only when the client requires a local skill tree.

Run the offline gate before release:

```bash
python .claude/skills/run-sap-router-skill/driver.py
```

Use `scripts/sap_router.py` for routing, `scripts/mcp_launcher.py` for MCP capability resolution, and `.agents/registries/mcp-capabilities.json` as the source of truth.
