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
- skills: 168 sha256:f872def69220396279ccdde014152a88cd292cd2f003970bbc9f12355dcf77b8
- profiles: 38 sha256:1f96a9a25baec0d70da537110ab3aa8793a8a5c882d609477f76f21c0daad813
- registries: 10 sha256:85037785d6bb5ad91860b2fe92047f9d1079f09b4b0e3739ca99513f93c1038e

Run:
`python scripts/generate_ide_assets.py check`
