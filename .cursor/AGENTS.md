# SAP Router Skill for Cursor

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
- skills: 94 sha256:ae44702217c0fda15bafd00dbf9ceb9119ff2ae7136fc3a800eb3cb72f3c300b
- profiles: 38 sha256:6f0e2c46679d2daebcfeda21f126dd8aea758e20dbe29f23b3669d4ed3293144
- registries: 10 sha256:ec6bf4c0eb60da3330ac4c6e250c93e351916b31b523c6eb22c84a05bc5c19f9

Run:
`python scripts/generate_ide_assets.py check`
