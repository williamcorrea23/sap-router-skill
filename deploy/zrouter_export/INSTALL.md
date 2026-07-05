# ZROUTER Installation Guide v4.2.0

## Overview

ZROUTER is an RFC accelerator for SAP — dispatches functional actions (BAPI calls) through a single RFC-enabled function module, with config-based allowlisting, audit logging, and 9 module handlers.

**23 objects total** — 16 classes, 3 interfaces, 2 DDIC tables, 1 function group, 1 function module.

## Prerequisites

- SAP NetWeaver 7.40+ / S/4HANA
- Developer authorization (S_DEVELOP with ACTVT 01/02)
- RFC destination configured (for external RFC calls)
- Package ZROUTER created (SE80 → create package)

## Files in `deploy/zrouter_export/`

```
zrouter_export/
├── *.clas.abap + *.clas.xml        # 16 classes (DEF + IMPL)
├── *.intf.abap + *.intf.xml        # 3 interfaces
├── zrouter_dispatch_fm.fugr.*      # Function Module source
├── zrouter_ddic_tables.abap        # DDIC table creation report
├── zrouter_seed_data.abap          # Config seed data report
├── zrouter_test_report.abap        # Post-install test report
└── INSTALL.md                      # This file
```

## Installation Steps

### Phase 1 — Package + DDIC (5 min)

**1.1 Create Package**
- SE80 → Repository Browser → Create → Package
- Name: `ZROUTER`
- Short Description: `ZROUTER RFC Accelerator`
- Software Component: `HOME` (or `LOCAL` for sandbox)

**1.2 Create DDIC Tables**
- Execute report `ZROUTER_DDIC_SETUP` via SE38 (create from `zrouter_ddic_tables.abap`)
- Tables created: ZROUTER_CONFIG, ZROUTER_LOG, ZROUTER_BATCH_RESULT
- For each table: SE11 → add fields (see table specs below), then activate

#### ZROUTER_CONFIG Fields
| Field | Data Element | Type | Len | Key | Description |
|-------|-------------|------|-----|-----|-------------|
| MANDT | MANDT | CLNT | 3 | X | Client |
| MODULE | ZROUTER_MODULE | CHAR | 10 | X | SAP Module |
| ACTION | ZROUTER_ACTION | CHAR | 30 | X | Action name |
| ACTIVE | ZROUTER_BOOL | CHAR | 1 | | Active flag (X) |
| BATCHABLE | ZROUTER_BOOL | CHAR | 1 | | Batchable flag |
| TIMEOUT | INT4 | INT4 | 10 | | Timeout (seconds) |

#### ZROUTER_LOG Fields
| Field | Data Element | Type | Len | Key | Description |
|-------|-------------|------|-----|-----|-------------|
| MANDT | MANDT | CLNT | 3 | X | Client |
| GUID | SYSUUID_C32 | CHAR | 32 | X | Log GUID |
| MODULE | ZROUTER_MODULE | CHAR | 10 | | Module |
| ACTION | ZROUTER_ACTION | CHAR | 30 | | Action |
| STATUS | CHAR10 | CHAR | 10 | | SUCCESS/ERROR |
| MESSAGE | CHAR200 | CHAR | 200 | | Message text |
| PAYLOAD | STRING | STRING | | | JSON payload |
| RESULT | STRING | STRING | | | JSON result |
| USERNAME | SYUNAME | CHAR | 12 | | SAP user |
| TIMESTAMP | TIMESTAMPL | DEC | 21/7 | | UTC timestamp |

#### ZROUTER_BATCH_RESULT Fields
| Field | Data Element | Type | Len | Key | Description |
|-------|-------------|------|-----|-----|-------------|
| MANDT | MANDT | CLNT | 3 | X | Client |
| BATCH_GUID | SYSUUID_C32 | CHAR | 32 | X | Batch GUID |
| SEQNR | INT4 | INT4 | 10 | X | Seq number |
| MODULE | ZROUTER_MODULE | CHAR | 10 | | Module |
| ACTION | ZROUTER_ACTION | CHAR | 30 | | Action |
| STATUS | CHAR10 | CHAR | 10 | | Status |
| MESSAGE | CHAR200 | CHAR | 200 | | Message |
| PAYLOAD | STRING | STRING | | | JSON payload |
| RESULT | STRING | STRING | | | JSON result |
| TIMESTAMP | TIMESTAMPL | DEC | 21/7 | | UTC timestamp |

**1.3 Create Data Elements**
- SE11 → Data Type → Create
- ZROUTER_MODULE: CHAR 10 — SAP Module name
- ZROUTER_ACTION: CHAR 30 — Action name
- ZROUTER_BOOL: CHAR 1 — Boolean flag (X/space)

### Phase 2 — Interfaces (2 min)

Import in dependency order (SE24 → Create → Interface):

```
1. CX_ZROUTER          (Exception class — SE24 → Class)
2. ZIF_ZROUTER_HANDLER  (depends on: CX_ZROUTER)
3. ZIF_ZROUTER_CONFIG   (independent)
4. ZIF_ZROUTER_LOGGER   (independent)
```

For each:
- SE24 → enter interface name → Create
- Paste source from `*.intf.abap`
- Save + Activate (Ctrl+S, Ctrl+F3)

### Phase 3 — Infrastructure Classes (3 min)

```
5.  ZCL_ZROUTER_CONFIG    (depends: ZIF_ZROUTER_CONFIG, ZROUTER_CONFIG table)
6.  ZCL_ZROUTER_LOGGER     (depends: ZIF_ZROUTER_LOGGER, ZROUTER_LOG table)
7.  ZCL_ZROUTER_AUTHORITY  (independent)
8.  ZCL_ZROUTER_HANDLER_ABSTRACT (depends: ZIF_ZROUTER_HANDLER, _CONFIG, _LOGGER)
```

For each:
- SE24 → enter class name → Create
- Paste source from `*.clas.abap` (contains DEFINITION + IMPLEMENTATION)
- Save + Activate

### Phase 4 — Module Handlers (5 min)

```
9.  ZCL_ZROUTER_HANDLER_MM    (depends: ZCL_ZROUTER_HANDLER_ABSTRACT)
10. ZCL_ZROUTER_HANDLER_SD    (depends: ZCL_ZROUTER_HANDLER_ABSTRACT)
11. ZCL_ZROUTER_HANDLER_FI    (depends: ZCL_ZROUTER_HANDLER_ABSTRACT)
12. ZCL_ZROUTER_HANDLER_QM    (depends: ZCL_ZROUTER_HANDLER_ABSTRACT)
13. ZCL_ZROUTER_HANDLER_PP    (depends: ZCL_ZROUTER_HANDLER_ABSTRACT)
14. ZCL_ZROUTER_HANDLER_WM    (depends: ZCL_ZROUTER_HANDLER_ABSTRACT)
15. ZCL_ZROUTER_HANDLER_CO    (depends: ZCL_ZROUTER_HANDLER_ABSTRACT)
16. ZCL_ZROUTER_HANDLER_HCM   (depends: ZCL_ZROUTER_HANDLER_ABSTRACT)
17. ZCL_ZROUTER_HANDLER_BASIS (depends: ZCL_ZROUTER_HANDLER_ABSTRACT)
```

### Phase 5 — Core + Function Module (3 min)

```
18. ZCL_ZROUTER_DISPATCH     (depends: all handlers + infrastructure)
19. ZCL_ZROUTER_BATCH        (depends: ZCL_ZROUTER_DISPATCH)
```

**Create Function Group:**
- SE80 → Function Groups → Create → `ZROUTER`

**Create Function Module:**
- SE37 → `ZROUTER_DISPATCH_FM` → Create → Function Group: `ZROUTER`
- Attributes tab → Processing Type: `Remote-Enabled Module`
- Import tab: IV_MODULE (TYPE STRING), IV_ACTION (TYPE STRING), IV_PAYLOAD (TYPE STRING)
- Export tab: EV_RESULT (TYPE STRING), EV_STATUS (TYPE STRING), EV_RETURN_MESSAGE (TYPE STRING)
- Source Code tab → paste from `zrouter_dispatch_fm.fugr.abap`
- Save + Activate

### Phase 6 — Seed + Test (2 min)

**Seed Config Data:**
- SE38 → ZROUTER_SEED_DATA → Execute
- Registers 28 actions across 9 modules in ZROUTER_CONFIG

**Run Test Report:**
- SE38 → ZROUTER_TEST → Execute
- Tests: ping (all modules), config check (MM/SD), PING via RFC FM

## Verification Checklist

```
[ ] Package ZROUTER exists
[ ] 2 DDIC tables active (ZROUTER_CONFIG, ZROUTER_LOG)
[ ] 3 interfaces active (ZIF_ZROUTER_HANDLER, _CONFIG, _LOGGER)
[ ] 16 classes active (no syntax errors)
[ ] Function group ZROUTER + FM ZROUTER_DISPATCH_FM active
[ ] ZROUTER_CONFIG has 28 seed rows
[ ] ZROUTER_TEST passes all tests
[ ] RFC call: ZROUTER_DISPATCH_FM returns pong for any module PING
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Table ZROUTER_CONFIG not found" | Activate DDIC table first |
| "Interface ZIF_ZROUTER_HANDLER not found" | Import interfaces before classes |
| "CX_ZROUTER not active" | Activate exception class first |
| "Function group ZROUTER not found" | Create FUGR in SE80 first |
| "RFC destination error" | SM59 → create TCP/IP destination |
| Syntax error in handler | Check BAPI names against SAP system version |

## Optional: abapGit Import

Alternative to manual SE24/SE37: use abapGit to import all `*.xml` + `*.abap` files at once.
1. Clone repo with abapGit
2. Select all ZROUTER objects
3. Pull into SAP
4. Activate all
