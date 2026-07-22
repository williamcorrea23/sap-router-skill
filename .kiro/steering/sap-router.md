# SAP Router Skill for Kiro

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
- skills: 93 sha256:e214818a8e31601b2af3b7811180d8e9a3af5ebae70fdf670627006d7a88bd10
- profiles: 38 sha256:6f0e2c46679d2daebcfeda21f126dd8aea758e20dbe29f23b3669d4ed3293144
- registries: 10 sha256:33fd85be432e599592eb92960cd4147c284bc5d808b097a0750f9c1f3344c109

Run:
`python scripts/generate_ide_assets.py check`
