---
name: sap-code-search
description: Search ABAP source code using ADT REST API, abap-code-search-tools (DevEpos), or RS_ABAP_SOURCE_SCAN
trigger:
  keywords: [code search, where used, find abap, scan source, impact analysis, rs_abap_source_scan, code_search]
  intent: Searching ABAP code, finding references, or scanning source code across SAP systems
---
# SAP Code Search

## Mental Model

You have three search engines, each with a different tradeoff:

- **ADT REST API** — fast, indexed, built-in. Best for object lookup and quick searches.
- **abap-code-search-tools (DevEpos)** — full-text, regex, 12 object types. Best for deep scanning.
- **RS_ABAP_SOURCE_SCAN** — standard report, no add-ons. Best for quick one-off scans in GUI.

Pick based on what you need: speed → ADT, depth → DevEpos, zero-install → RS_ABAP_SOURCE_SCAN.

## Prerequisites

```bash
# 1. ADT path — verify ADT REST endpoint is reachable
curl -s -u "$SAP_USER:$SAP_PASS" \
  "$SAP_HOST/sap/bc/adt/repository/informationsystem/search?operation=quickSearch&query=Z*" \
  | head -20

# 2. DevEpos path — verify abap-code-search-tools installed
#    SE24 → ZCL_ADCOSET_SEARCH_ENGINE exists
#    SE38 → ZADCOSET_SEARCH executable
#    abapGit repo: https://github.com/DevEpos/abap-code-search-tools

# 3. RS_ABAP_SOURCE_SCAN — zero install, available on all NW ≥ 7.00
#    SE38 → RS_ABAP_SOURCE_SCAN → execute

# 4. Authorizations
#    ADT:     S_ADT_RES with URI = '/devepos/adt/cst/*'
#    ZROUTER: ZROUTER with ACTIVITY = 'ZROUTER_BASIS_CODE_SEARCH'
```

## Search via ADT (Quick Object Lookup)

```bash
# Quick search — returns object names + ADT URIs
curl -s -u "$SAP_USER:$SAP_PASS" \
  "$SAP_HOST/sap/bc/adt/repository/informationsystem/search?operation=quickSearch&query=ZCL_FOO*"

# Read source of a program
curl -s -u "$SAP_USER:$SAP_PASS" \
  "$SAP_HOST/sap/bc/adt/programs/programs/ZMYPROG/source/main"

# Read source of a class
curl -s -u "$SAP_USER:$SAP_PASS" \
  "$SAP_HOST/sap/bc/adt/oo/classes/ZCL_FOO/source/main"

# Where-used list (ADT)
curl -s -u "$SAP_USER:$SAP_PASS" \
  "$SAP_HOST/sap/bc/adt/repository/informationsystem/whereused?objectName=BAPI_MATERIAL_SAVEDATA&objectType=FUGR"
```

## Search via DevEpos Engine (Full-Text + Regex)

```bash
# Route to ZROUTER RFC handler
python scripts/sap_router.py route --action BASIS_CODE_SEARCH

# CSV template for batch searches
python scripts/xls_to_bapi.py template --output cs.csv --module BASIS --action CODE_SEARCH
# Fields: query, mode, object_type, package, owner, max_results, ignore_case, parallel

# Example CSV rows (search all types — omit object_type):
# BAPI_TRANSACTION_COMMIT,STRING,,ZMY_PKG,200
# CALL_FUNCTION\s+'BAPI_\w+',REGEX,PROG,ZMY_PKG,500
# (?i)select.*from\s+mara,PCRE,,ZMY_PKG,100
python scripts/xls_to_bapi.py convert --input cs.csv --module BASIS --action CODE_SEARCH

# Stats per package/owner
python scripts/sap_router.py route --action BASIS_CODE_SEARCH_STATS
```

### Search Modes

| Mode | Syntax | When to use |
|------|--------|-------------|
| `STRING` | Plain text | Exact phrase matching |
| `REGEX` | POSIX regex | Pattern matching (`BAPI_\w+_CREATE`) |
| `PCRE` | Perl regex | Advanced (`(?i)select.*from\s+\w+`) |

### Searchable Object Types (12)

`CLAS` `INTF` `PROG` `TYPE` `FUGR` `DDLS` `DDLX` `DCLS` `BDEV` `XSLT` `STRU`(7.50+) `DTAB`(7.52+)

## Search via RS_ABAP_SOURCE_SCAN (Zero Install)

```abap
" SE38 → RS_ABAP_SOURCE_SCAN
" Fill parameters:
"   Pattern:           CALL FUNCTION 'BAPI_MATERIAL_SAVEDATA'
"   Program range:     Z*
"   Find pattern in:   Reports + Includes
" This scans source line-by-line. No add-on required.
```

```bash
# Via RFC (if ZROUTER not installed)
python scripts/sap_router.py route --action code_search
# Routes to ADT quickSearch — lighter but no regex
```

## Pitfalls

1. **ADT search ≠ full-text** — ADT `quickSearch` finds object names, not source content. Use DevEpos engine for body search.
2. **RS_ABAP_SOURCE_SCAN is slow** on large systems — always filter by package or program name range.
3. **PCRE mode depends on kernel** — verify `cl_abap_regex` supports PCRE on your NW release before using.
4. **Where-used via ADT requires `S_ADT_RES`** — the standard `S_DEVELOP` authorization is not enough.
5. **DevEpos branch matters** — use `main` for NW ≥ 7.51, `nw-740` for 7.40–7.50. Wrong branch = syntax errors.
6. **Parallel search** — set `parallel=true` only on systems with ≥ 4 dialog WP; otherwise it degrades.
7. **Case sensitivity** — DevEpos `ignore_case=true` is off by default. Most BAPI searches need it on.
8. **DTAB/STRU types** — only available on NW 7.52+/7.50+ respectively. Older systems silently skip them.

## Verification

```bash
# 1. ADT path — expect HTTP 200 + XML
curl -s -o /dev/null -w "%{http_code}" -u "$SAP_USER:$SAP_PASS" \
  "$SAP_HOST/sap/bc/adt/repository/informationsystem/search?operation=quickSearch&query=Z*"
# Expected: 200

# 2. DevEpos path — expect ZCL_ADCOSET_SEARCH_ENGINE in SE24
#    Run: SE24 → ZCL_ADCOSET_SEARCH_ENGINE → Display → no errors

# 3. RS_ABAP_SOURCE_SCAN — SE38 → execute with pattern "REPORT"
#    Expect: list of programs containing "REPORT" statement

# 4. ZROUTER handler — run driver
python scripts/sap_router.py route --action BASIS_CODE_SEARCH
# Expected: "ZROUTER RFC"

# 5. CSV round-trip
python scripts/xls_to_bapi.py template --output /tmp/cs_test.csv --module BASIS --action CODE_SEARCH
python scripts/xls_to_bapi.py convert --input /tmp/cs_test.csv --module BASIS --action CODE_SEARCH
# Expected: valid JSON payload with search parameters
```

## Decision Tree

```
Need to search ABAP source code?
├─ Just find an object by name? → ADT quickSearch
├─ Search source body with regex? → DevEpos engine (BASIS_CODE_SEARCH)
├─ No add-on installed? → RS_ABAP_SOURCE_SCAN (SE38)
├─ Need where-used for a specific object? → ADT where-used endpoint
└─ Batch search across packages? → CSV + xls_to_bapi.py → BASIS_CODE_SEARCH
```
