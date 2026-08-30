# SAP Router Skill for Kiro

Canonical source: `.agents/`.
Karpathy wrapper: mandatory. Caveman compression: default.
Do not copy or fork skill bodies here; regenerate from canonical source.

Runtime root:
- `SAP_ROUTER_ROOT` must point to the canonical sap-router-skill repository.
- change the working directory to `SAP_ROUTER_ROOT` before relative commands.
- fail closed if `scripts/source_catalog.py` is not present there.

Dynamic local discovery:
- search skills: `python scripts/source_catalog.py search "task description"`
- search MCPs: `python scripts/mcp_launcher.py search --query "task description"`
- bundled MCPs are disabled candidates until reviewed; no runtime GitHub lookup.

Local optimization:
- prefer `rtk` for supported verbose CLI commands.
- use Context Mode for large outputs, indexed fetches, and session checkpoints.

Parity proof:
- skills: 165 sha256:df88df6d47623b2cb8519c0291287107146b84864ec9d21b117422f9c355d51e
- profiles: 38 sha256:1f96a9a25baec0d70da537110ab3aa8793a8a5c882d609477f76f21c0daad813
- registries: 10 sha256:9b826019b85b0ad744827bd43b029581624f31f774edfb070223567def530344

Run:
`python scripts/generate_ide_assets.py check`
