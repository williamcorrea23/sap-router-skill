---
name: sap-code-search
description: >-
  Search ABAP source code using abap-code-search-tools (DevEpos) or ADT.
  Supports full-text search across 12 object types (CLAS, INTF, PROG, FUGR,
  DDLS, BDEV, XSLT, DTAB, etc.) with STRING, REGEX, and PCRE modes.
  Use when searching ABAP code, finding references, auditing codebases,
  scanning for patterns, or performing impact analysis across SAP systems.
---

# SAP Code Search

Code search across ABAP systems using two search paths:

| Path | Engine | Best for |
|---|---|---|
| `code_search` → ARC-1 ADT | ADT REST API | Object lookup, source read, navigation |
| ZROUTER RFC → BASIS handler | ZCL_ADCOSET_SEARCH_ENGINE | Full-text search, regex, bulk scanning |

## Quick Start

```bash
# Route code search actions
python scripts/sap_router.py route --action BASIS_CODE_SEARCH
# → "ZROUTER RFC" (uses abap-code-search-tools engine)

python scripts/sap_router.py route --action code_search
# → "ARC-1 (ADT)" (uses built-in ADT search)
```

## Searchable Object Types (12)

| Type | Code | ABAP Version |
|---|---|---|
| Classes | CLAS | 7.40+ |
| Interfaces | INTF | 7.40+ |
| Programs | PROG | 7.40+ |
| Type Groups | TYPE | 7.40+ |
| Function Groups | FUGR | 7.40+ |
| Data Definitions | DDLS | 7.40+ |
| Metadata Extensions | DDLX | 7.40+ |
| Access Controls | DCLS | 7.40+ |
| Behavior Definitions | BDEV | 7.40+ |
| Simple Transformations | XSLT | 7.40+ |
| Structures | STRU | 7.50+ |
| Database Tables | DTAB | 7.52+ |

## Search Modes

| Mode | Description | Example |
|---|---|---|
| STRING | Plain text search | `CALL FUNCTION 'BAPI_MATERIAL` |
| REGEX | POSIX regular expression | `BAPI_\w+_CREATE` |
| PCRE | Perl Compatible Regex (system-dependent) | `(?i)bapi.*material` |

## Installation

```bash
# 1. Install abap-code-search-tools via abapGit
#    Repo: https://github.com/DevEpos/abap-code-search-tools
#    Branch: main (NW ≥ 7.51) or nw-740 (NW 7.40–7.50)

# 2. Verify
#    SE24 → ZCL_ADCOSET_SEARCH_ENGINE → exists
#    SE38 → ZADCOSET_SEARCH → executable

# 3. Import ZROUTER_CODE_SEARCH.abap from templates/
#    Adds BASIS handler methods: CODE_SEARCH, CODE_SEARCH_STATS, CODE_SEARCH_ADT
```

## CSV/XLS Usage

```bash
# Generate template for code search
python scripts/xls_to_bapi.py template --output cs.csv --module BASIS --action CODE_SEARCH

# Fields: query, mode, object_type, package, owner, max_results, ignore_case, parallel

# Convert
python scripts/xls_to_bapi.py convert --input searches.csv --module BASIS --action CODE_SEARCH

# Search all 12 types at once (omit object_type):
# query,mode,object_type,package,max_results
# BAPI_TRANSACTION,STRING,,ZFOO,200
```

## ADT vs Engine Tradeoffs

| Feature | ADT Search | Engine Search |
|---|---|---|
| Scope | Current system | Current system |
| Speed | Fast (indexed) | Slower (line-by-line) |
| Regex | No | Yes (REGEX + PCRE) |
| Parallel | N/A | Yes (optional) |
| Object types | All ADT types | 12 ABAP source types |
| ADT URI navigation | Built-in | Via build_adt_uri() |
| GUI report | N/A | ZADCOSET_SEARCH |

## CSA Authorization

```abap
" For ADT search path:
AUTHORITY-CHECK OBJECT 'S_ADT_RES'
  ID 'URI' FIELD '/devepos/adt/cst/*'.

" For ZROUTER handler:
AUTHORITY-CHECK OBJECT 'ZROUTER'
  ID 'ACTIVITY' FIELD 'ZROUTER_BASIS_CODE_SEARCH'.
```
