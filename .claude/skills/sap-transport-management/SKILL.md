---
name: sap-transport-management
description: SAP Transport Request lifecycle management — SE09/SE10, TR release, STMS import, abapGit, ZROUTER BASIS handler
trigger:
  keywords: [transport request, se09, se10, tr release, stms, tr import, transport route, tr_add_to_transport, abapgit transport, e070, e071]
  intent: Creating, releasing, importing, and auditing SAP transport requests
prerequisites:
  - SAP system access with authorizations for SE09/SE10 or STMS
  - RFC user with TR_INSERT_REQUEST_WITH_TASKS / TR_RELEASE_REQUEST authority
  - STMS configuration for target system (DEV → QAS → PRD route)
  - (Optional) abapGit repo for serialized transport
---

# SAP Transport Management

## 1. Transport Lifecycle

```
CREATE (SE01/SE09) → ADD OBJECTS (SE80/SETDT) → RELEASE TASK → RELEASE REQUEST → IMPORT (STMS)
                       ↑ Code Review Gate (sap-transport-gate)
```

## 2. Create & Release (ABAP)

```abap
" Create Workbench transport request
CALL FUNCTION 'TR_INSERT_REQUEST_WITH_TASKS'
  EXPORTING
    iv_type    = 'K'          " K=Workbench, W=Customizing
    iv_text    = 'Bugfix: material creation validation'
  IMPORTING
    ev_request = lv_trkorr
  EXCEPTIONS
    OTHERS     = 99.

" Release transport (auto-releases all open tasks)
CALL FUNCTION 'TR_RELEASE_REQUEST'
  EXPORTING
    iv_trkorr = lv_trkorr
  EXCEPTIONS
    OTHERS    = 99.
```

## 3. Query Transport Tables

```abap
" E070 — Transport Request Header
SELECT trkorr, trfunction, trstatus, as4user, as4date
  FROM e070 WHERE trkorr LIKE 'S4HK%'
  ORDER BY as4date DESCENDING.

" E071 — Transport Objects
SELECT trkorr, pgmid, object, obj_name
  FROM e071 WHERE trkorr = @lv_trkorr.
```

## 4. STMS Import (via CLI)

```bash
# Import request to target
tp import S4HK123456 QAS U1

# Check import queue
tp show queue QAS

# Monitor import status (SE03 → Transport Log)
# Or via table: SELECT trkorr, trstatus FROM e070
```

## 5. abapGit Transport (Offline)

```bash
# Serialize ABAP object for transport
python scripts/abap_serializer.py generate \
  --source templates/ZROUTER_DISPATCH.abap \
  --name ZCL_ZROUTER_DISPATCH --type CLAS \
  --format abapgit --output exports/
```

## Pitfalls

- **Objects modified without TR** → Cause: forgot to record. Solution: all changes MUST be recorded in transport request; unreleased changes are local only.
- **TR_RELEASE_REQUEST on task** → Cause: releasing task instead of request. Solution: releasing the request auto-releases all open tasks.
- **Import fails with "object not found"** → Cause: dependent objects missing. Solution: check E071 for object type; include all dependent objects.
- **STMS import queue blocked** → Cause: previous transport still importing. Solution: use `tp checkqueue QAS` to view blocking request.
- **abapGit package mismatch** → Cause: repository dev class ≠ transport package. Solution: ensure dev class matches transport package in SE03.
- **Transport not in correct layer** → Cause: wrong development class layer. Solution: assign objects to correct package (developments in DEV layer, customizing in CUS layer).

## Verification

```bash
# Check transport status via E070
python scripts/sap_router.py adt list --table E070 --fields "trkorr,trstatus,as4date" --where "trkorr='S4HK123456'"

# Or via SE03 (transport log)
# tp show queue QAS
# tp import S4HK123456 QAS U1

# Verify import: check object in target system
python scripts/sap_router.py adt read --object ZCL_ZROUTER_DISPATCH
```