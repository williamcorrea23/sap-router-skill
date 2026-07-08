# Peer Review — ZROUTER v5 (12 Dimensions)
**Date**: 2026-07-05 | **Reviewer**: sap-code-reviewer v3.0 | **Objects**: 7 files

## Scores by Dimension

| # | Dim | W | Score | C/H/M/L | Status |
|---|-----|---|-------|----------|--------|
| 1 | SEC | 2.0 | 75 | 0/1/1/0 | COND |
| 2 | AUTH | 1.5 | 85 | 0/1/0/0 | COND |
| 3 | DATA | 1.5 | 70 | 0/1/2/0 | COND |
| 4 | PERF | 1.0 | 85 | 0/0/3/0 | PASS |
| 5 | STD | 1.0 | 80 | 0/0/4/0 | PASS |
| 6 | INTERFACE | 1.0 | 90 | 0/0/1/0 | PASS |
| 7 | CHANGE | 1.5 | 100 | 0/0/0/0 | PASS |
| 8 | COMP | 1.0 | 60 | 0/2/1/0 | FAIL |
| 9 | FUNC | 1.0 | 85 | 0/0/2/0 | PASS |
| 10 | HTTP | 1.5 | 80 | 0/0/2/0 | PASS |
| 11 | BDC | 1.0 | 80 | 0/0/2/0 | PASS |
| 12 | RFC | 1.5 | 90 | 0/0/1/0 | PASS |

**Weighted Score**: 79/100 → **GO (Conditional)**

## Findings

### COMP-1 [HIGH] — cl_abap_authorization may not exist on NW 7.40
**File**: `zcl_zrouter_authority.clas.abap:21`
**Problem**: Uses `cl_abap_authorization=>check_authorization()` which is an ABAP Cloud class. On NW 7.40, this class may not exist.
**Fix**: Replace with classic `AUTHORITY-CHECK OBJECT 'ZROUTER' ID 'ACTIVITY' FIELD lv_activity.`

### COMP-2 [HIGH] — ZROUTER_ACTIVATE: `&& lv_subrc &&` integer concatenation
**File**: ZROUTER_ACTIVATE line 31 (FIXED)
**Problem**: `lv_subrc TYPE sy-subrc` (integer) used with `&&` string concatenation operator.
**Fix**: Use `|FAILED (subrc={ sy-subrc }): { lv_name }|` string template. ✅ FIXED

### SEC-1 [HIGH] — GENERATE SUBROUTINE POOL still present
**File**: `zcl_zrouter_handler_abstract.clas.abap:130`
**Problem**: `GENERATE SUBROUTINE POOL` with allowlist. Allowlist reduces risk but doesn't eliminate it — eval still has code execution capability.
**Fix**: Consider removing `evaluate_expression()` entirely if not used by any handler. If needed, restrict to pure math/string expressions only.

### DATA-1 [HIGH] — Logger COMMIT WORK inside LUW
**File**: `zcl_zrouter_logger.clas.abap:38`
**Problem**: `COMMIT WORK AND WAIT` after every log INSERT. If a handler rolls back its BAPI but the logger already committed, the audit trail is misleading. Additionally, this commits any pending LUW.
**Fix**: Remove COMMIT WORK from logger. Let the caller (handler) control the LUW. Use `COMMIT WORK AND WAIT` only at the top level (RFC FM).

### AUTH-1 [HIGH] — No ICF authorization for HTTP handler
**File**: `zcl_zrouter_http.clas.abap:95` (handle_request)
**Problem**: HTTP handler has no authorization check. Anyone with HTTP access can dispatch any ZROUTER action.
**Fix**: Add `AUTHORITY-CHECK OBJECT 'ZROUTER' ID 'ACTIVITY' FIELD lv_activity` in handle_request before dispatch.

### PERF-1 [MEDIUM] — SELECT * in YFG_SBDC
**File**: `yfg_sbdc.fugr.abap:217,222`
**Problem**: `SELECT * FROM ysbdc_session` fetches all columns including `bdcdata_json` (STRING, large). Unnecessary for list operations.
**Fix**: `SELECT session_id, tcode, recording_name, created_by, created_at FROM ysbdc_session`

### PERF-2 [MEDIUM] — SELECT * FROM SAP customizing tables
**File**: `zcl_zrouter_handler_mm.clas.abap:154-156`, `zcl_zrouter_handler_sd.clas.abap:124-126`
**Problem**: `SELECT * FROM t161/t024/t001w/tvak/tvko/tvfk` reads all columns.
**Fix**: Select only needed columns. Apply WHERE clause if possible.

### PERF-3 [MEDIUM] — No HTTP timeout in REST handler
**File**: `zcl_zrouter_http.clas.abap:95`
**Problem**: No timeout set for dispatch operations. A slow BAPI could hang the HTTP connection indefinitely.
**Fix**: Set `rv_timeout = 30` in `dispatch_action`, check elapsed time, abort if exceeded.

### DATA-2 [MEDIUM] — Multiple COMMIT WORK in YFG_SBDC
**File**: `yfg_sbdc.fugr.abap:65,173,180,198`
**Problem**: Each FM (RECORD, REPLAY, DELETE) does its own `COMMIT WORK AND WAIT`. This fragments the LUW and is unnecessary for independent operations.
**Fix**: Consolidate COMMIT to the caller level. Or document that each operation is intentionally independent.

### DATA-3 [MEDIUM] — Y_SBDC_REPLAY error handling incomplete
**File**: `yfg_sbdc.fugr.abap:140-160`
**Problem**: Only checks `msgtyp = 'E'` and `msgtyp = 'A'`. Doesn't check for `msgtyp = 'W'` (warnings) or `msgtyp = 'X'` (exit).
**Fix**: Add checks for W (warning) and X (exit) message types.

### STD-1 [MEDIUM] — Y_SBDC_EXPORT unused variable
**File**: `yfg_sbdc.fugr.abap:233`
**Problem**: `lt_bdcdata` deserialized but never used in export structure validation.
**Fix**: Validate that lt_bdcdata is not empty before building export.

### STD-2 [MEDIUM] — ZREQ: P_DSTTXT initialization overwrites user input
**File**: `zreq.prog.abap:20`
**Problem**: `INITIALIZATION` concatenates `p_dsttxt` with date/time, overwriting user's description text.
**Fix**: Append date/time instead of replacing: `CONCATENATE p_dsttxt 'Copy' sy-datum sy-uzeit INTO lv_dsttxt SEPARATED BY space.`

### HTTP-1 [MEDIUM] — CORS wildcard without validation
**File**: `zcl_zrouter_http.clas.abap:102`
**Problem**: `Access-Control-Allow-Origin: *` without origin validation. In production, this should be restricted.
**Fix**: For production: validate `Origin` header against allowlist. Keep wildcard for dev.

### HTTP-2 [MEDIUM] — No Content-Type validation
**File**: `zcl_zrouter_http.clas.abap:131`
**Problem**: `handle_post` calls `get_cdata()` without checking if Content-Type is `application/json`.
**Fix**: Validate Content-Type header before parsing as JSON.

### BDC-1 [MEDIUM] — Y_SBDC_REPLAY: BDC_OKCODE not verified
**File**: `yfg_sbdc.fugr.abap:109-130`
**Problem**: Deserialized bdcdata is replayed without verifying that each screen has BDC_OKCODE and BDC_CURSOR set.
**Fix**: Validate before replay: LOOP AT lt_bdcdata, check for BDC_OKCODE entry per screen.

### BDC-2 [MEDIUM] — Y_SBDC_RECORD: BDCDATA validation missing
**File**: `yfg_sbdc.fugr.abap:55`
**Problem**: No validation that `it_bdcdata` contains proper screen markers (dynbegin = 'X').
**Fix**: Validate at least one entry has dynbegin = 'X' before storing.

### FUNC-1 [MEDIUM] — ZREQ fallback path untested
**File**: `zreq.prog.abap:42-89`
**Problem**: Manual copy fallback (when TR_COPY_REQUEST fails) inserts objects without checking if they're already locked.
**Fix**: Add ENQUEUE before manual object insertion.

### FUNC-2 [MEDIUM] — ZROUTER_ACTIVATE tries SEO_CLIF_ACTIVATE for all objects
**File**: ZROUTER_ACTIVATE (deployed)
**Problem**: Calls `SEO_CLIF_ACTIVATE` for ZREQ (a program, not a class). Will fail and fallback to RS_PROGRAM_ACTIVATE. Inefficient but works.
**Fix**: Check object type first with `SELECT FROM tadir` before deciding which FM to call.

### STD-3 [LOW] — Inconsistent error message format
**File**: Multiple handlers
**Problem**: Some use `'Error: ' && lv_msg`, others use string templates, others use CONCATENATE.
**Fix**: Standardize on string templates: `|Error: { lv_msg }|`.

### STD-4 [LOW] — ZCL_ZROUTER_HTTP: parse_path method unused
**File**: `zcl_zrouter_http.clas.abap:95`
**Problem**: `parse_path` method declared but never called.
**Fix**: Remove or call it in handle_get/handle_post.

### RFC-1 [LOW] — ZROUTER_DISPATCH_FM: EV_RESULT length undefined
**File**: `zrouter_dispatch_fm.fugr.abap:8`
**Problem**: FM parameters typed as STRING (unlimited). RFC clients may truncate at their buffer size.
**Fix**: Document max payload size in FM description. Add length validation before export.

## Summary

| Priority | Count | Action |
|----------|-------|--------|
| CRITICAL | 0 | — |
| HIGH | 4 | COMP-1, COMP-2✅, SEC-1, DATA-1, AUTH-1 |
| MEDIUM | 14 | PERF 3x, DATA 2x, HTTP 2x, BDC 2x, STD 2x, FUNC 2x, INTERFACE 1x |
| LOW | 3 | STD 2x, RFC 1x |

### Immediate Actions (HIGH)
1. **COMP-1**: Fix `cl_abap_authorization` → `AUTHORITY-CHECK` (NW 7.40 compat)
2. **DATA-1**: Remove `COMMIT WORK AND WAIT` from logger
3. **AUTH-1**: Add AUTHORITY-CHECK to HTTP handler
4. **COMP-2**: ✅ Fixed (ZROUTER_ACTIVATE integer concat)

### Recommended Order
1. Fix COMP-1 (crash risk on NW 7.40)
2. Fix DATA-1 (data integrity)
3. Fix AUTH-1 (security gate)
4. Fix PERF MEDIUM items
5. Standardize error handling (STD)
6. Address BDC validations
