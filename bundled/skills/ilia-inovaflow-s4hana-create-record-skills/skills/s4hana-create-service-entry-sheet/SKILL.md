---
name: s4hana-create-service-entry-sheet
description: Create Service Entry Sheets (SES) in SAP S/4HANA Cloud Public or on-prem private edition via OData V2 A_ServiceEntrySheet deep-insert at API_SERVICE_ENTRY_SHEET_SRV (Lean Services model). Use whenever the user wants to create, post, add, generate, seed, enter, or confirm service entry sheets on S/4HANA — phrases like "create SES for PO X", "make me a few service entries", "confirm services rendered on these POs", "seed SES demo data", "post a service entry sheet". Handles full SES header+item deep-insert (auto-inherits account assignment from referenced PO line), open-MM-period validation, PO performance-period validation, the "PO not released" transient async retry, and idempotent bulk batches with per-record logging. Requires a service PO to reference (cat 0 + SERV material + AAC=K) — if none exist, defer to s4hana-create-po with the service-PO recipe first. Do NOT use for invoice creation against SES (that's s4hana-create-invoice extended with SES reference), for SES approval workflow (separate API/PATCH), or for time-sheet entries (different entity).
---

# s4hana-create-service-entry-sheet

Create Service Entry Sheets on SAP S/4HANA Cloud Public (Lean Services). **Verified end-to-end against SAP S/4HANA Cloud Public Edition 2026-05-12 — SES 1, 2, 3 posted via API.**

## Phase 0 — Setup check (MANDATORY, no exceptions)

**Before any API call, before any tool use, do this check. Even if you already know credentials from earlier in the conversation — IGNORE that knowledge and re-check from scratch each invocation.**

1. **Announce**: tell the user "Checking for SAP credentials in `<current cwd>`..."
2. **Check ONLY these two sources:**
   - A `.env` file at `./.env` (in the current working directory — NOT parent dirs, NOT `~/.env`, NOT any memory file)
   - Shell-exported env vars: `SAP_HOST` AND `SAP_AUTH_MODE` both present
3. **If neither**: auto-create `./.env` from the bundled template (curl from `https://raw.githubusercontent.com/ilia-inovaflow/s4hana-create-record-skills/main/.env.example`), append `.env` to `.gitignore` if not already there, tell the user clearly what to fill in (auth mode + host + creds), and **wait** for them to say "ready" before making any API call. Never overwrite an existing `.env`.
4. **If credentials are present**: report back to the user: "✓ Loaded credentials for `<host>` in `<auth-mode>` mode. Proceeding with [task]."

**Never use credentials from conversation memory, from another project's `.env`, or from any tenant the user previously worked with in a different session.** Each project gets its own `.env`. See [`shared/setup-check.md`](../../shared/setup-check.md) for the full rationale and edge cases.


## When to trigger
Verbs: create / post / add / generate / seed / enter / confirm
Objects: SES, service entry sheet(s), service confirmation(s)
Counts: 1 to ~50 records.

## Hard rules (never violate)
1. Always do a 1-record live POST as a probe before bulk (≥3 records).
2. The referenced PO must be a SERVICE PO (cat `0` + SERV material + AAC=K). Use `s4hana-create-po` with the service-PO recipe first if none exist.
3. SES references the **service line (cat 0)**, NOT the limit item (cat A) if the PO has one.
4. Scripts go in `<cwd>/.s4hana-tmp/create-ses-<YYYYMMDD-HHMM>/`. Never commit, never modify `.env`.
5. POSTs are sequential with 200ms delay; halt on 3 consecutive failures (but auto-retry once on `MM_PUR_SES/119: PO not released` after a 2-second wait — transient backend async).

## Endpoint
- Service path: `/sap/opu/odata/sap/API_SERVICE_ENTRY_SHEET_SRV`
- Entity sets: `A_ServiceEntrySheet`, `A_ServiceEntrySheetItem`, `A_SrvcEntrShtAcctAssignment`
- Method: POST (deep-insert with `to_ServiceEntrySheetItem`)
- Communication scenario: **`SAP_COM_0146`** — "Service Entry Sheet Integration" (must be added to comm user — common gap on fresh tenants)

There's also an OData V4 variant at `/sap/opu/odata4/sap/api_serviceentrysheet/srvd_a2x/sap/serviceentrysheet/0001/` — same data, different protocol. Use V2 for now (this skill targets V2).

## Phases

### Phase 1 — Parse & gather input
For each SES, required:

| Field | Notes |
|---|---|
| `PurchaseOrder` (header + item) | A service PO that exists and is released |
| `PurchaseOrderItem` (item) | The cat-0 service line on that PO (NOT cat-A limit line) |
| `ConfirmedQuantity` | Amount of service performed (typically partial — 25%-100% of order qty) |
| `QuantityUnit` | Match the PO line unit (e.g. `AU`) |
| `NetPriceAmount` | Match the PO line price |
| `Plant`, `Currency` | From the PO line |
| `PostingDate` | **Must be in open MM posting period** (often different from FI periods — typically 2-3 months back) |
| `ServicePerformanceDate` / `EndDate` | **Must be within the PO line's allowed performance window** — typically must equal or follow the PO creation date |
| `ServiceEntrySheetName` | Free text, 40 char max |

If the user said "auto", pull eligible PO lines from `A_PurchaseOrderItem?$filter=ProductType eq '2' and PurchaseOrderItemCategory eq '0' and IsFinallyInvoiced eq false`.

### Phase 2 — Preflight checks
Before bulk:
1. Confirm the comm arrangement for `SAP_COM_0146` is active (probe `A_ServiceEntrySheet?$top=1` — 403 HTML = missing arrangement).
2. Find an open MM posting period via either a probe (try to post with today's date, read M7/053 error for allowed periods) or `T_T001B`-equivalent OData if accessible. Cache result.
3. For each candidate PO line, fetch performance window (`Item.NetPriceQuantity`, `Item.PurchaseOrderDate` etc.) so SES dates are valid.

### Phase 3 — Build payload

Minimal working envelope (verified):

```json
{
 "ServiceEntrySheetName": "<short label>",
 "PurchaseOrder": "<po>",
 "PostingDate": "/Date(<ms>)/",
 "Currency": "EUR",
 "to_ServiceEntrySheetItem": [
 {
 "ServiceEntrySheetItem": "10",
 "PurchaseOrder": "<po>",
 "PurchaseOrderItem": "<line>",
 "ConfirmedQuantity": "<qty>",
 "QuantityUnit": "AU",
 "NetPriceAmount": "<price>",
 "Currency": "EUR",
 "Plant": "1010",
 "ServiceEntrySheetItemDesc": "<short desc>",
 "ServicePerformanceDate": "/Date(<ms>)/",
 "ServicePerformanceEndDate": "/Date(<ms>)/"
 }
 ]
}
```

**Do NOT include `to_AccountAssignment`** unless the user explicitly wants a different cost center than what's on the PO — SES auto-inherits the PO line's AAC/CostCenter/GLAccount, and explicit deep-insert often triggers `MM_PUR_SES/128: accounting lines not numbered consecutively`.

### Phase 4 — CSRF + POST
Same CSRF flow as the other OData V2 services in this collection — see `../s4hana-create-po/references/csrf-flow.md`.

If response is `MM_PUR_SES/119: Purchase order X is not released.` for a PO created in the same session/seconds ago → **wait 2s and retry once** (transient backend async). The PO IS released; the SES backend just hasn't refreshed its cache yet.

### Phase 5 — Verify & report
After all POSTs, `$expand=to_ServiceEntrySheetItem` on 2-3 random SES to confirm. Show user: total created, SES ID range, supplier/PO distribution, any failures.

## Output structure
```
<cwd>/.s4hana-tmp/create-ses-<YYYYMMDD-HHMM>/
├── eligible-po-lines.json # candidate POs after filtering
├── create-log.jsonl # one line per attempt
├── results.json # final summary
└── verify-sample.json
```

## Reference files
- `references/envelope-template.md` — full schema with all optional fields
- `references/known-errors.md` — error catalog (MM_PUR_SES/006, /015, /119, /128, M7/053, etc.)
- `references/po-not-released-retry.md` — the transient async pattern + retry algorithm
- `scripts/bulk-ses-poster.mjs` — reference implementation
