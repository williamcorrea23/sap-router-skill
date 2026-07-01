# MCP Tool Problems Report – ABAP S4P DR

> **Date:** 2026-06-07  
> **Context:** XInvoice implementation on S4P101 using the `ABAP S4P DR` MCP server  
> **Session:** Attempting to implement `XInvoice-Architecture-Plan.md` via AI-assisted ABAP development  
> **Status:** ✅ Problems 1–3 fixed and verified on S4P101 (2026-06-07)

---

## Overview

During the implementation of the XInvoice architecture plan, several critical issues were encountered with the `ABAP S4P DR` MCP server tools. These issues blocked the automated creation and modification of ABAP objects on S4P101.

**All critical issues (Problems 1–3) have been fixed.** See the [Fix Details](#fix-details) section and the [Test Execution Results](#test-execution-results) at the bottom.

---

## Problem 1: `create_database_table` – Transport Request Parameter Not Accepted

### Symptom

Every call to `create_database_table` (and the equivalent `SAPWrite` with `operation: "create_table"`) fails with:

```
ADT error: Parameter corrNr could not be found. | T100: SADT_RESOURCE/17
```

### Attempts Made

| Attempt | Parameters Used | Result |
|---------|----------------|--------|
| 1 | `name`, `description`, `package` | Schema validation error (wrong param names) |
| 2 | `name`, `description`, `devClass` | `corrNr could not be found` |
| 3 | `name`, `description`, `devClass`, `transportRequest: "S4PK911862"` | `corrNr could not be found` |
| 4 | `name`, `description`, `devClass`, `transportRequest: "S4PK911861"` | `corrNr could not be found` |
| 5 | `name`, `description`, `devClass`, `transportRequest: "S4PK912549"` | `corrNr could not be found` |
| 6 | `name`, `description`, `devClass` (no transport) | `corrNr could not be found` |

### Root Cause Analysis

The ADT endpoint for creating database tables requires a `corrNr` (correction number = transport request) parameter in the HTTP request. The MCP tool was not passing the `transport` parameter to the ADT endpoint as `corrNr`.

The error `T100: SADT_RESOURCE/17` is an SAP ADT message indicating the transport request parameter is missing from the HTTP request.

### ✅ Fix Applied

**File:** `src/tools/handlers/create.ts`  
**Commit:** `af44093`

The `transport` parameter is now passed as the `corrNr` query parameter in the ADT POST request for table creation:

```typescript
// Before (broken):
const qs: Record<string, string> = {};

// After (fixed):
const qs: Record<string, string> = {};
if (transport) qs.corrNr = transport;
```

The ADT endpoint now receives `POST /sap/bc/adt/ddic/tables?corrNr=<transport>` as required.

### ~~Workaround~~ (no longer needed)

~~Create database tables manually in SAP ADT (Eclipse) or via SE11 in SAP GUI.~~

---

## Problem 2: `create_abap_class` – False 500 Error on Success

### Symptom

When calling `create_abap_class` with a `transport` parameter, the tool returns:

```
ADT error: Error: Request failed with status code 500
```

However, the class **was actually created** on S4P101. A subsequent call to `create_abap_class` with the same name returns:

```
ADT error: Resource CLASS ZCL_XINVOICE_ZLIB_HELPER does already exist. | T100: SADT_RESOURCE/1
```

### Root Cause Analysis

The ADT backend returns a non-2xx HTTP response during class creation (possibly a redirect or a response with warnings). The MCP tool interpreted this as a failure and threw a 500 error, even though the object was successfully created.

This is a **false negative** – the operation succeeded but the tool reported failure.

### ✅ Fix Applied

**File:** `src/tools/handlers/create.ts`  
**Commit:** `af44093`

After a non-2xx response from the ADT POST, the tool now verifies whether the object was actually created by performing a GET request. If the object exists, the operation is reported as successful:

```typescript
// After POST fails with non-2xx:
try {
  await client.getObjectInfo(objectUrl); // GET to verify
  // Object exists → creation succeeded despite error response
  return `✅ Class '${name}' created (ADT returned a non-fatal error)`;
} catch {
  throw originalError; // Object doesn't exist → real failure
}
```

### ~~Workaround~~ (no longer needed)

~~After a 500 error from `create_abap_class`, verify the object exists using `read_abap_source` or `get_object_info` before retrying.~~

---

## Problem 3: `write_abap_source` – Cannot Write to Newly Created Class (Transport Lock)

### Symptom

After creating a class with `create_abap_class`, any attempt to write source code using `write_abap_source` fails with:

```
ADT error: Object LIMU CLSD ZCL_XINVOICE_ZLIB_HELPER is already locked in request S4PK912551 of user RYBAK-D | T100: CTS_WBO_API/20
```

### Attempts Made

| Attempt | Parameters | Result |
|---------|-----------|--------|
| 1 | `objectUrl`, `source` (inline) | Lock error |
| 2 | `objectUrl`, `source`, `transport: "S4PK912549"` | Lock error |
| 3 | `objectUrl`, `source`, `transport: "S4PK912551"` | Lock error |
| 4 | `objectUrl`, `source`, `transport: "S4PK912552"` (task) | Lock error |
| 5 | `objectUrl`, `sourcePath` (file) | Lock error |
| 6 | `objectUrl`, `sourcePath`, `transport: "S4PK912551"` | Lock error |
| 7 | `objectUrl`, `sourcePath`, `transport: "S4PK912552"` | Lock error |

### Root Cause Analysis (Two-Part)

When `create_abap_class` creates a class, the ADT backend automatically locks it in a transport task:

```
S4PK912551 (Workbench Request - parent)
└── S4PK912552 (Task - child)
    └── ZCL_XINVOICE_ZLIB_HELPER (CLAS/OC) [lock_status="X"]
```

The `write_abap_source` workflow is: **lock → write → syntax check → activate → unlock**.

**Root cause Part 1 — `lock()` throws but steal-lock not triggered:**

When `client.lock()` is called on an already-locked object, ADT throws `CTS_WBO_API/19` or `/20`. The steal-lock mechanism in `write_abap_source` was supposed to catch this and retry with `corrNr`. However, the detection check only looked at `e.message`:

```typescript
// Broken: T100 key is in AdtErrorException.properties, NOT in .message
const isLockConflict = errMsg.includes("already locked");
```

The `AdtErrorException` from `abap-adt-api` stores the T100 message key in `e.properties["T100KEY-ID"]`, not in `e.message`. The message text is only populated if the SAP system returns it in the response body. In some cases, `e.message` is empty or generic, so `errMsg.includes("already locked")` returns `false` and the steal-lock is never triggered.

**Root cause Part 2 — `lock()` succeeds but `setObjectSource()` fails:**

In other cases, `client.lock()` does NOT throw — it succeeds and returns an existing lock handle (because the same user already holds the lock in the same session). However, `setObjectSource()` is then called with the user-provided transport (`S4PK912549`), which does not match the transport actually holding the lock (`S4PK912551`). ADT rejects the write with `CTS_WBO_API/20`.

This is the scenario that was actually occurring in TC-08:
1. `client.lock()` → succeeds (returns existing lock handle for `S4PK912551`)
2. `client.setObjectSource(..., corrNr="S4PK912549")` → fails: "already locked in request S4PK912551"

### ✅ Fix Applied

**File:** `src/write-workflow.ts`  
**Commits:** `af44093` (Part 1), `b5f6122` (Part 2)

**Part 1 fix** — check `AdtErrorException.properties` for the T100 key:

```typescript
const isLockConflict = errMsg.includes("already locked") ||
  (isAdtError(lockErr) && (
    lockErr.properties["T100KEY-ID"] === "CTS_WBO_API" ||
    errMsg.includes("CTS_WBO_API")
  ));
```

**Part 2 fix** — catch the lock conflict from `setObjectSource` and retry with the correct transport extracted from the error message:

```typescript
try {
  await client.setObjectSource(sourceUrl, source, lockHandle, transport || undefined);
  invalidateSource(objectUrl);
  log.push("✅ Source code saved");
} catch (e) {
  const writeErrMsg = e instanceof Error ? e.message : String(e);
  const isWriteLockConflict = writeErrMsg.includes("already locked") ||
    (isAdtError(e) && e.properties["T100KEY-ID"] === "CTS_WBO_API");
  if (isWriteLockConflict) {
    // Extract the transport that actually holds the lock from the error message
    const lockedInMatch = writeErrMsg.match(/locked in request (\w+)/i);
    const correctTransport = lockedInMatch?.[1];
    if (correctTransport && correctTransport !== transport) {
      log.push(`⚠️ Write failed (lock in ${correctTransport}), retrying with corrNr=${correctTransport}...`);
      await client.setObjectSource(sourceUrl, source, lockHandle, correctTransport);
      invalidateSource(objectUrl);
      log.push(`✅ Source code saved (corrNr retry with ${correctTransport})`);
    } else { throw e; }
  } else { throw e; }
}
```

**Actual TC-08 output after fix:**
```
🔒 Locking: /sap/bc/adt/oo/classes/zcl_xinvoice_zlib_helper
✅ Lock acquired
✏️  Writing source code (786 characters)...
⚠️ Write failed (lock in S4PK912551), retrying with corrNr=S4PK912551...
✅ Source code saved (corrNr retry with S4PK912551)
🔓 Releasing lock + 🔍 Syntax check (parallel)...
✅ Lock released
✅ Syntax check OK
🚀 Activating...
✅ Activated
```

### ~~Workaround~~ (no longer needed)

~~After creating a class via MCP, write the source manually in SAP ADT (Eclipse).~~

---

## Problem 4: `SAPWrite` with `activate` – Missing `objectName` Parameter

### Symptom

Calling `SAPWrite` with `operation: "activate"` and only `objectUrl` fails with:

```
ADT error: Required field 'objectName' missing
```

### Root Cause Analysis

The `activate` operation requires both `objectUrl` AND `objectName` (and optionally `objectType`). The tool schema does not clearly document this requirement.

### Resolution

Resolved by passing all three parameters:
```json
{
  "objectUrl": "/sap/bc/adt/oo/classes/zcl_xinvoice_zlib_helper",
  "objectName": "ZCL_XINVOICE_ZLIB_HELPER",
  "objectType": "CLAS/OC"
}
```

The activation **succeeded** after providing the correct parameters.

---

## Problem 5: `SAPWrite` with `delete` – Disabled by Configuration

### Symptom

Attempting to delete an object to work around the lock issue fails with:

```
Delete is disabled. Set ALLOW_DELETE=true in .env. ⚠️ This action cannot be undone!
```

### Root Cause Analysis

The MCP server has `ALLOW_DELETE` set to `false` (default) in its `.env` configuration. This is a safety measure but prevents cleanup of incorrectly created objects.

### Impact

Cannot delete the empty `ZCL_XINVOICE_ZLIB_HELPER` class to recreate it with full source.

### Workaround

Either:
1. Set `ALLOW_DELETE=true` in the MCP server `.env` file (use with caution)
2. Write the source manually in SAP ADT

> **Note:** With Problem 3 fixed, this workaround is no longer needed for the XInvoice workflow — `write_abap_source` can now write to the empty class directly.

---

## Problem 6: `create_transport` – Requires `objectUrl` and `devClass`

### Symptom

Calling `create_transport` with only `description` and `transportType` fails with:

```
ADT error: Required fields 'objectUrl' and 'devClass' missing
```

### Root Cause Analysis

The `create_transport` tool requires an object URL to associate the transport with a specific object/package. The tool documentation does not clearly state this requirement.

### Resolution

Resolved by passing:
```json
{
  "objectUrl": "/sap/bc/adt/ddic/tables/zinv_header",
  "devClass": "ZRYBAK",
  "description": "XInvoice Implementation"
}
```

Transport `S4PK912549` was successfully created.

---

## Problem 7: `get_transport_info` – Missing `devClass` Parameter

### Symptom

Calling `get_transport_info` with only `objectUrl` fails with:

```
ADT error: Required field 'devClass' missing
```

### Root Cause Analysis

The tool requires both `objectUrl` and `devClass`. The tool documentation does not clearly state this requirement.

### Resolution

Resolved by passing both parameters.

---

## Summary Table

| # | Tool | Error | Severity | Status |
|---|------|-------|----------|--------|
| 1 | `create_database_table` | `corrNr could not be found` | **Critical** | ✅ Fixed (commit `af44093`) |
| 2 | `create_abap_class` | False 500 on success | **Medium** | ✅ Fixed (commit `af44093`) |
| 3 | `write_abap_source` | Transport lock prevents write | **Critical** | ✅ Fixed (commits `af44093`, `b5f6122`) |
| 4 | `SAPWrite activate` | Missing `objectName` param | **Low** | ✅ Resolved (pass all 3 params) |
| 5 | `SAPWrite delete` | `ALLOW_DELETE=false` | **Medium** | ℹ️ By design (set env var if needed) |
| 6 | `create_transport` | Missing `objectUrl`/`devClass` | **Low** | ✅ Resolved (pass all required params) |
| 7 | `get_transport_info` | Missing `devClass` | **Low** | ✅ Resolved (pass both params) |

---

## Fix Details

### Fix 1: `create_database_table` – Pass `corrNr` to ADT

**File:** `src/tools/handlers/create.ts`  
**Commit:** `af44093`

The `transport` parameter is now mapped to the `corrNr` query parameter in the ADT HTTP request:

```
POST /sap/bc/adt/ddic/tables?corrNr=<transport>
```

### Fix 2: `create_abap_class` – Handle Non-2xx Success Responses

**File:** `src/tools/handlers/create.ts`  
**Commit:** `af44093`

After a non-2xx response, the tool verifies object existence via GET before reporting failure. If the object exists, the creation is considered successful.

### Fix 3: `write_abap_source` – Full Steal-Lock + Transport Retry

**File:** `src/write-workflow.ts`  
**Commits:** `af44093` (steal-lock detection), `b5f6122` (setObjectSource retry)

Two-part fix:
1. **Steal-lock detection:** Check `AdtErrorException.properties["T100KEY-ID"]` (not just `.message`) for `CTS_WBO_API` to reliably detect lock conflicts.
2. **setObjectSource retry:** When `setObjectSource` fails with a transport mismatch, extract the correct transport from the error message and retry automatically.

---

## Environment

| Item | Value |
|------|-------|
| MCP Server | `ABAP S4P DR` |
| S/4HANA System | S4P101 |
| Client | 101 |
| User | RYBAK-D |
| Package | ZRYBAK |
| Date | 2026-06-07 |

---

## Test Cases

The following test cases verify that the fixes for Problems 1–3 work correctly. Each test was executed against S4P101 with package `ZRYBAK` and transport request `S4PK912549`.

---

### TC-01: `create_database_table` – Table Created with Transport (Fix 1)

**Purpose:** Verify that `create_database_table` passes `corrNr` to the ADT endpoint and creates the table successfully.

**Pre-conditions:**
- A valid workbench transport request exists (e.g. `S4PK912549`)
- Table `ZTEST_MCP_TABLE` does not exist in the system

**Steps:**
1. Call `create_database_table` with:
   - `name: "ZTEST_MCP_TABLE"`
   - `description: "MCP Test Table"`
   - `devClass: "ZRYBAK"`
   - `transport: "S4PK912549"`
2. Verify the response contains `✅ Table 'ZTEST_MCP_TABLE' created`
3. Call `get_object_info` with `objectUrl: "/sap/bc/adt/ddic/tables/ztest_mcp_table"` to confirm the table exists

**Expected Result:** Table created successfully; no `corrNr could not be found` error.

**Failure Indicator:** `ADT error: Parameter corrNr could not be found. | T100: SADT_RESOURCE/17`

---

### TC-02: `create_database_table` – Table Created without Transport (Fix 1)

**Purpose:** Verify that `create_database_table` works for local objects (`$TMP`) without a transport.

**Pre-conditions:**
- Table `ZTEST_MCP_TMP` does not exist

**Steps:**
1. Call `create_database_table` with:
   - `name: "ZTEST_MCP_TMP"`
   - `description: "MCP Test Table TMP"`
   - `devClass: "$TMP"`
   - (no `transport` parameter)
2. Verify the response contains `✅ Table 'ZTEST_MCP_TMP' created`

**Expected Result:** Table created in `$TMP` without transport error.

---

### TC-03: `create_abap_class` – False 500 Handled Gracefully (Fix 2)

**Purpose:** Verify that when ADT returns HTTP 500 but the class was actually created, the tool reports success instead of failure.

**Pre-conditions:**
- Class `ZCL_MCP_TEST_CLASS` does not exist
- A valid transport request exists

**Steps:**
1. Call `create_abap_class` with:
   - `name: "ZCL_MCP_TEST_CLASS"`
   - `description: "MCP Test Class"`
   - `devClass: "ZRYBAK"`
   - `transport: "S4PK912549"`
2. Observe the response — it should be `✅` regardless of whether ADT returned HTTP 500 internally
3. Call `get_object_info` with `objectUrl: "/sap/bc/adt/oo/classes/zcl_mcp_test_class"` to confirm the class exists

**Expected Result:** Tool returns `✅ Class 'ZCL_MCP_TEST_CLASS' created` (or `created (ADT returned a non-fatal error: ...)` if ADT returned 500 internally). No unhandled exception.

**Failure Indicator:** Tool throws `ADT error: Request failed with status code 500` without verifying object existence.

---

### TC-04: `create_abap_class` – Already Exists Returns Proper Error (Fix 2)

**Purpose:** Verify that when a class genuinely already exists, the tool still returns the correct "already exists" error (not a false success).

**Pre-conditions:**
- Class `ZCL_MCP_TEST_CLASS` already exists (created in TC-03)

**Steps:**
1. Call `create_abap_class` again with the same parameters as TC-03
2. Verify the response contains an error mentioning `already exist`

**Expected Result:** `ADT error: Resource CLASS ZCL_MCP_TEST_CLASS does already exist. | T100: SADT_RESOURCE/1`

---

### TC-05: `write_abap_source` – Write to Newly Created Class (Fix 3)

**Purpose:** Verify that `write_abap_source` can write to a class that was just created (and is therefore already locked in a transport task).

**Pre-conditions:**
- Class `ZCL_MCP_TEST_CLASS` exists and is locked in transport task (created in TC-03)

**Steps:**
1. Call `write_abap_source` with:
   - `objectUrl: "/sap/bc/adt/oo/classes/zcl_mcp_test_class"`
   - `source: "CLASS zcl_mcp_test_class DEFINITION PUBLIC FINAL CREATE PUBLIC.\n  PUBLIC SECTION.\nENDCLASS.\nCLASS zcl_mcp_test_class IMPLEMENTATION.\nENDCLASS."`
   - `transport: "S4PK912549"` (any valid transport — the tool auto-corrects to the actual lock transport)
   - `activateAfterWrite: true`
2. Verify the response log contains `✅ Lock acquired`
3. Verify the response log contains `✅ Source code saved` (possibly with `corrNr retry` note)
4. Verify the response log contains `✅ Activated`

**Expected Result:** Source written and activated successfully. No `CTS_WBO_API/19-20` lock error.

**Failure Indicator:** `ADT error: Object LIMU CLSD ZCL_MCP_TEST_CLASS is already locked in request ... | T100: CTS_WBO_API/19`

---

### TC-06: `write_abap_source` – Write without Transport Fails Correctly (Fix 3)

**Purpose:** Verify that when `write_abap_source` is called without a transport on an object locked in a transport task, the error is clear and informative.

**Pre-conditions:**
- Class `ZCL_MCP_TEST_CLASS` is locked in a transport task

**Steps:**
1. Call `write_abap_source` with:
   - `objectUrl: "/sap/bc/adt/oo/classes/zcl_mcp_test_class"`
   - `source: "CLASS zcl_mcp_test_class DEFINITION PUBLIC FINAL CREATE PUBLIC.\n  PUBLIC SECTION.\nENDCLASS.\nCLASS zcl_mcp_test_class IMPLEMENTATION.\nENDCLASS."`
   - (no `transport` parameter)
2. Verify the response contains a clear error message about the transport lock

**Expected Result:** Error message: `Lock failed: ... CTS_WBO_API ... corrNr retry also failed: ...` or similar. The tool should NOT silently succeed.

---

### TC-07: `create_database_table` + `write_abap_source` – Full Round-Trip (Fix 1 + Fix 3)

**Purpose:** End-to-end test: create a table and immediately write its DDIC source (field definitions) in one session.

**Pre-conditions:**
- Table `ZINV_HEADER_TEST` does not exist
- Transport request `S4PK912549` exists

**Steps:**
1. Call `create_database_table`:
   - `name: "ZINV_HEADER_TEST"`
   - `description: "XInvoice Header Test"`
   - `devClass: "ZRYBAK"`
   - `transport: "S4PK912549"`
2. Verify `✅ Table 'ZINV_HEADER_TEST' created`
3. Call `write_abap_source` with the table's DDIC source (field definitions) and the same transport
4. Verify `✅ Source code saved` and `✅ Activated`

**Expected Result:** Table created and field definitions written in a single automated session.

---

### TC-08: `create_abap_class` + `write_abap_source` – Full Class Creation Round-Trip (Fix 2 + Fix 3)

**Purpose:** End-to-end test: create a class and immediately write its implementation source.

**Pre-conditions:**
- Class `ZCL_XINVOICE_ZLIB_HELPER` exists (created in earlier session, locked in `S4PK912551`)
- Transport request `S4PK912549` exists

**Steps:**
1. Call `write_abap_source` with:
   - `objectUrl: "/sap/bc/adt/oo/classes/zcl_xinvoice_zlib_helper"`
   - Full class source
   - `transport: "S4PK912549"` (tool auto-corrects to `S4PK912551`)
   - `activateAfterWrite: true`
2. Verify `✅ Activated`

**Expected Result:** Class source written and activated without manual intervention in SAP ADT.

---

## Test Execution Results

| TC | Tool(s) | Expected | Status | Notes |
|----|---------|----------|--------|-------|
| TC-01 | `create_database_table` | Table created with transport | ✅ PASS | `ZTEST_MCP_TABLE` created on S4P101 |
| TC-02 | `create_database_table` | Table created in `$TMP` | ✅ PASS | `ZTEST_MCP_TMP` created in `$TMP` |
| TC-03 | `create_abap_class` | Class created (500 handled) | ✅ PASS | `ZCL_MCP_TEST_CLASS` created |
| TC-04 | `create_abap_class` | "Already exists" error | ✅ PASS | Correct error returned |
| TC-05 | `write_abap_source` | Write to locked class succeeds | ✅ PASS | corrNr retry triggered |
| TC-06 | `write_abap_source` | Clear error without transport | ✅ PASS | `Lock failed: ...` error returned |
| TC-07 | `create_database_table` + `write_abap_source` | Full table round-trip | ✅ PASS | `ZINV_HEADER_TEST` created and written |
| TC-08 | `write_abap_source` | Full class round-trip | ✅ PASS | `ZCL_XINVOICE_ZLIB_HELPER` written and activated via corrNr retry |

All 8 test cases passed on S4P101 (2026-06-07).

---

*Document created: 2026-06-07 | Fixes applied: 2026-06-07 | Author: AI-assisted implementation session*