# SAP Transport Field Reference

All tools in this server use business-friendly names. This table maps them to SAP technical fields.

## Transport Header Fields

| Business Name | SAP Field | Example Value |
|---------------|-----------|---------------|
| `transportNumber` | TRKORR | DEVK900123 |
| `description` | AS4TEXT | Add plant 1000 config |
| `status` | TRSTATUS | see status codes below |
| `type` | CATEGORY | see type codes below |
| `owner` | AS4USER | JSMITH |
| `targetSystem` | TARSYSTEM | QA1 |
| `createdAt` | AS4DATE + AS4TIME | 2026-05-26T09:00:00Z |

## Transport Object Fields

| Business Name | SAP Field | Example Value |
|---------------|-----------|---------------|
| `objectType` | OBJECT | PROG, TABL, FUGR, DOMA |
| `objectName` | OBJ_NAME | ZMY_PROGRAM |
| `programId` | PGMID | R3TR, LIMU |

## Status Codes (TRSTATUS)

| Code | Business Label | Meaning |
|------|---------------|---------|
| D | Modifiable | Open for changes — objects can be added |
| L | Released | Exported — ready for import into target |
| R | Release Started | Release in progress |
| N | Locked | Locked by system process |

## Transport Type Codes (CATEGORY)

| Code | Business Label | Meaning |
|------|---------------|---------|
| K | Workbench | ABAP development objects (programs, tables, etc.) |
| W | Customizing | IMG configuration settings |
| C | Transport of Copies | Copy of objects — not linked to original |

## Common ABAP Object Types (OBJECT field)

| Code | Meaning |
|------|---------|
| PROG | ABAP Program |
| TABL | Database Table |
| FUGR | Function Group |
| DOMA | Domain |
| DTEL | Data Element |
| VIEW | View |
| CLAS | ABAP Class |
| INTF | Interface |
| DEVC | Package |
| TTYP | Table Type |
| MSAG | Message Class |

## Transport Number Format

```
[SID][K][######]
 DEV  K  900123
```
- 3 chars: System SID (DEV, QAS, PRD)
- K: transport request type marker
- 6 digits: sequential number assigned by SAP CTS
