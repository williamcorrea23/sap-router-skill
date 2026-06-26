---
name: sap-transport-management
description: >-
  SAP Transport Request management — CTS transport lifecycle, TR release
  gates, abapGit integration, code review before transport, STMS import
  status, and ZROUTER BASIS handler integration. Use when creating,
  releasing, or auditing transport requests; when performing pre-release
  code review; when managing transport landscapes via ABAP or MCP.
---

# SAP Transport Management

Transport request management for SAP ABAP changes. Covers both manual
(SE09/SE10) and automated (ZROUTER_BASIS handler, MCP) workflows.

## Transport Lifecycle

```
CREATE → ADD OBJECTS → RELEASE TASK → RELEASE REQUEST → IMPORT (STMS)
```

## ZROUTER BASIS Actions

| Action | FM | Description |
|---|---|---|
| CREATE_REQUEST | TR_INSERT_REQUEST_WITH_TASKS | Create new TR with tasks |
| RELEASE_REQUEST | TR_RELEASE_REQUEST | Release TR/task |
| CODE_ANALYSIS | TRINT_INSPECT_OBJECTS | Inspect objects before release |

## ABAP Patterns

```abap
" Create transport request
CALL FUNCTION 'TR_INSERT_REQUEST_WITH_TASKS'
  EXPORTING
    iv_type  = 'K'       " K=Workbench, W=Customizing
    iv_text  = lv_description
  IMPORTING
    ev_request = lv_trkorr
  EXCEPTIONS
    OTHERS   = 99.

" Release transport
CALL FUNCTION 'TR_RELEASE_REQUEST'
  EXPORTING
    iv_trkorr = lv_trkorr
  EXCEPTIONS
    OTHERS    = 99.

" Add object to transport
" Use TR_APPEND_TO_TRANSPORT or ADT API
```

## Pre-Release Gate (sap-transport-gate skill)

```bash
# Hermes MCP transport gate — 10-dimension risk review
# Dimensions: SEC, AUTH, DATA, PERF, STD, INTERFACE, CHANGE, COMP, FUNC
# Generates: GO / CONDITIONAL_GO / NO_GO / NEED_MORE_EVIDENCE
```

## abapGit Integration

```bash
# Serialize for abapGit
python scripts/abap_serializer.py generate \
  --source templates/ZROUTER_DISPATCH.abap \
  --name ZCL_ZROUTER_DISPATCH \
  --type CLAS \
  --format abapgit \
  --output exports/

# Package in all 3 formats
python scripts/abap_serializer.py package \
  --source templates/ZROUTER_DISPATCH.abap \
  --name ZCL_ZROUTER_DISPATCH \
  --type CLAS \
  --output exports/
```

## Transport Objects CSV

```bash
# CSV template for transport management
python scripts/xls_to_bapi.py template --output tr.csv --module BASIS --action CREATE_REQUEST

# Fields: request_type, owner_text, target_system
# Convert: K, "Bugfix for material creation", DEV
```

## DDIC Transport Tables

```abap
" E070 — Transport Request Header
SELECT trkorr, trfunction, trstatus, as4user, as4date
  FROM e070
  WHERE trkorr LIKE 'S4HK%'
  ORDER BY as4date DESCENDING.

" E071 — Transport Request Objects
SELECT trkorr, pgmid, object, obj_name
  FROM e071
  WHERE trkorr = @lv_trkorr.
```

## CSA Notes

- **Never skip transport recording** — objects modified without TR are local only
- **TR_INSERT_REQUEST_WITH_TASKS** creates request + task — guaranteed atomic
- **TR_RELEASE_REQUEST** on a request releases it AND all open tasks
- **For production transports**: use sap-transport-gate skill for 10-dimension risk review
- **abapGit transport**: use `scripts/abap_serializer.py` for offline packaging
