# SAP Router Skill for Cursor

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
- skills: 162 sha256:5d200a4cc96e7b35ecfb1b4a6f4675296dc84ecd5672aa795cace41d0233b245
- profiles: 38 sha256:1f96a9a25baec0d70da537110ab3aa8793a8a5c882d609477f76f21c0daad813
- registries: 10 sha256:63e64157ed445e7251fc0d72f6ad6c57c70ad535dcae2f87301fd2ec7d4fe30c

Run:
`python scripts/generate_ide_assets.py check`
