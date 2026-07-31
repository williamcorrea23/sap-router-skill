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
- skills: 94 sha256:c5d869302c82503cb142e470f155415fffa0f53fa00156c9e29207f34a7aad3c
- profiles: 38 sha256:6f0e2c46679d2daebcfeda21f126dd8aea758e20dbe29f23b3669d4ed3293144
- registries: 10 sha256:3ac10628948a93ae4b5fa398194a83e5a1edc50b64501f5b8b21dad7567cfb48

Run:
`python scripts/generate_ide_assets.py check`
