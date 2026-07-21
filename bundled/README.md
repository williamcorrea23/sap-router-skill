# Bundled SAP assets

This directory contains repository-owned snapshots of skills, knowledge packs,
and MCP implementations. They are ordinary files: no Git submodules, nested
`.git` directories, or runtime network lookup is used.

Third-party copyright and license files remain attached to their respective
snapshot. Incorporation into this repository does not relicense those files.

The catalog is rebuilt locally:

```bash
python scripts/source_catalog.py index
python scripts/source_catalog.py search "SAP GUI automate transaction"
python scripts/source_catalog.py search "CAP CDS" --kind mcp
```

Discovered MCP code remains disabled until it is reviewed and explicitly
promoted in `.agents/registries/mcps.json`.
