# SAP Router Skill for Cursor

Canonical source: `.agents/`.
Karpathy wrapper: mandatory. Caveman compression: default.
Spec Kit background workflow: automatic for broad changes; `python scripts/sap_router.py spec-kit --task "..."`.
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
- skills: 203 sha256:046f6d52886520160ec0c76373806fd76f42ea8b489ebbe57b54e61fd29919fd
- profiles: 38 sha256:e746d5f5374f567c00e178b16645e378521476723efc61383bdc562f25d9c827
- registries: 14 sha256:e98ac633c7685dfb67cb878c1ae16833b0dcfccac5865035f5862c5fde42caf5

Run:
`python scripts/generate_ide_assets.py check`
