# SAP Router Skill for Codex

Canonical source: `.agents/`.
Karpathy wrapper: mandatory. Caveman compression: default.
Do not copy or fork skill bodies here; regenerate from canonical source.

Dynamic local discovery:
- search skills: `python scripts/source_catalog.py search "task description"`
- search MCPs: `python scripts/mcp_launcher.py search --query "task description"`
- bundled MCPs are disabled candidates until reviewed; no runtime GitHub lookup.

Local optimization:
- prefer `rtk` for supported verbose CLI commands.
- use Context Mode for large outputs, indexed fetches, and session checkpoints.

Parity proof:
- skills: 89 sha256:25038c1b3f9cbf4307196ba18d45c2f1ae0ccbd1ba8e7658b416dccdfc7d0cd7
- profiles: 38 sha256:6f0e2c46679d2daebcfeda21f126dd8aea758e20dbe29f23b3669d4ed3293144
- registries: 10 sha256:2aae846c8806c75ad9724df29b9b20d5c8dbc339f3723448317da067bc0525ee

Run:
`python scripts/generate_ide_assets.py check`
