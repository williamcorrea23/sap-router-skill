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
- skills: 162 sha256:f270b087a24c30b12993c7eefa8ba82bf7699a2451f8ec9aaed6b09c4a071e41
- profiles: 38 sha256:6f0e2c46679d2daebcfeda21f126dd8aea758e20dbe29f23b3669d4ed3293144
- registries: 10 sha256:301221debf9b226df28e67754268e0756e8ea46f1fa63df54c344cd208b5c03a

Run:
`python scripts/generate_ide_assets.py check`
