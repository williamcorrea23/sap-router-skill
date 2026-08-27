# SAP Router Skill for Codex

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
- skills: 164 sha256:b81f1b68450b0f1c3b5c3428c4b0a7c5dbe3b163d88febd589b47056e3474acb
- profiles: 38 sha256:1f96a9a25baec0d70da537110ab3aa8793a8a5c882d609477f76f21c0daad813
- registries: 10 sha256:d0f5012e25a62f2c5720ae7ef9e0c7e4a35e1c865e66dc8b3481943c06af2386

Run:
`python scripts/generate_ide_assets.py check`
