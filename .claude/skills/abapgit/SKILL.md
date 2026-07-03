---
name: abapgit
description: abapGit workflows — install from GitHub repos, branch selection (main vs nw-740), offline serialization, repo management, object serialization (.abap + .xml formats), transport integration, CI/CD with abapGit, mass object handling. Use when installing ABAP code from Git, serializing ABAP objects to files, or setting up ABAP CI/CD with abapGit.
trigger:
  keywords: [abapgit, git, serialization, repository, branch, transport, offline, ci-cd, abap-objects, mass-handling]
  intent: >-
    Manage ABAP code with Git via abapGit for version control, serialization, and CI/CD integration.
---

# abapGit

Git-based version control for ABAP development.

## Installation

### Via abapGit itself
```
SE38 → ZABAPGIT_STANDALONE → New → Clone from URL
  URL: https://github.com/abapGit/abapGit.git
  Branch: main (NW ≥ 7.51) or nw-740 (NW 7.40-7.50)
  Package: $ABAPGIT
```

### Via SAPTransport
Download from https://abapgit.org — transport request for import.

## Cloning a Repository

```
Repository → Clone → Online
  Git Repository URL: https://github.com/DevEpos/abap-code-search-tools
  Branch: main
  Target Package: ZCODE_SEARCH
  Folder Logic: Full
```

## Branch Selection by NetWeaver

| NW Version | Branch |
|---|---|
| ≥ 7.51 | main |
| 7.40 – 7.50 | nw-740 (ADBC-based, Oracle/HANA/MSSQL only) |
| < 7.40 | Not supported |

## Object Serialization Format

```
zcl_material_handler.clas.abap     ← ABAP source
zcl_material_handler.clas.xml      ← Metadata (VSEOCLASS-like)
zcl_material_handler.clas.loc.html  ← Language overlay (optional)
```

## Offline Workflow

```bash
# Export ABAP objects to files (via abap_serializer.py)
python scripts/abap_serializer.py package   --source templates/ZROUTER_DISPATCH.abap   --name ZCL_ZROUTER_DISPATCH   --type CLAS   --output exports/

# Creates:
# exports/nugg/zcl_zrouter_dispatch.nugg
# exports/abapgit/zcl_zrouter_dispatch.clas.xml + .abap
# exports/xml/zcl_zrouter_dispatch_zdload.xml
```

## Transport Integration

```abap
" abapGit can integrate with CTS
" Objects pulled via abapGit → recorded in Transport Request
" Settings → Advanced → Enable "Transport Recording"
```

## Stage / Commit / Push

```
abapGit Workflow:
  1. Stage objects (select which to include)
  2. Write commit message
  3. Commit (local) → Push (remote)

  Or: Pull → Stage → Commit → Push (full Git cycle)
```

## CI/CD with abapGit

```yaml
# GitHub Actions workflow
name: ABAP CI
on: [push]
jobs:
  abap-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install -g abaplint
      - run: abaplint **/*.abap
```

## Gotchas

- **Full folder logic** downloads all objects in package — unintended pulls possible
- **Transport recording must be ON** for objects to appear in TR
- **Serialized files are UTF-8** — SAP system uses codepage (1100 for Latin-1)
- **Large repos** (> 500 objects) may timeout on push — split into smaller repos
