---
name: s4hana-create-invoice
description: Create supplier (AP) invoices in SAP S/4HANA Cloud Public or on-prem private edition via the SOAP A2X "Supplier Invoice ERP Create Request" service. Use whenever the user wants to post, create, add, generate, seed, or backdate supplier/vendor/AP invoices on S/4HANA — including phrases like "make me a few invoices", "post 20 supplier invoices", "seed invoice demo data", "invoice these POs", "create supplier invoice for PO 4500...". Handles full SOAP envelope construction, CSRF-equivalent (none required for this service), tenant-ledger preflight, master-data lookup (material/qty/price from PO), partial vs full invoicing, idempotent bulk batches with per-record logging, and the FINS_ACDOC_CUST/201 ledger-config diagnosis path. Do NOT use for non-PO-based invoice creation, credit memos, or invoice cancellation — those need different envelope shapes (track them under generic skill until verified).
---

# s4hana-create-invoice

Create AP supplier invoices on SAP S/4HANA. **Verified production-ready against SAP S/4HANA Cloud Public Edition — 52 invoices posted 2026-05-11 with zero failures.**

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
Verbs: create / post / add / generate / seed / make / backdate / invoice
Objects: invoice(s), supplier invoice(s), vendor invoice(s), AP invoice(s)
Counts: 1 to ~200 records.

## Hard rules (never violate)
1. Always do a 1-record live POST as a probe before bulk (≥3 records).
2. Never invent master-data IDs — fetch Material/Plant/Currency/Supplier from the source PO line via OData GET.
3. If a required field has no sensible default and the user didn't specify → **ask once**, then auto-pick.
4. Scripts go in `<cwd>/.s4hana-tmp/create-invoices-<YYYYMMDD-HHMM>/`. Never commit, never modify `.env`.
5. POSTs are sequential with 200ms delay; halt on 3 consecutive failures.
6. SOAP A2X is the canonical create path on Cloud Public — the OData V2 `A_SupplierInvoice` POST works after ledger config is fixed but has stricter line-item field shape (`M8/375` requires `ReferenceDocument/-FiscalYear/-Item`). Use SOAP A2X.

## Endpoint
- Service path: `/sap/bc/srt/scs_ext/sap/ecc_suplrinvcerpcrtrc`
- SOAP action: `http://sap.com/xi/APPL/Global2/SupplierInvoiceERPCreateRequestConfirmation_In/SupplierInvoiceERPCreateRequestConfirmation_InRequest`
- Communication scenario: `SAP_COM_0057` — "Supplier Invoice Integration"

The arrangement must be active with the inbound service "Supplier Invoice - Create (A2X, Inbound, Synchronous)" listed. Verify in Fiori → Communication Arrangements.

## Auth & target
Pick **one** target up-front and use that mode for the whole run. Skill supports the same three modes as the parent collection — see `../../shared/auth-modes.md`.

For Cloud Public Edition with comm user (e.g. `<comm-user>`):
- Header: `Authorization: Basic <base64(user:pass)>` (no CSRF for SOAP)
- `Content-Type: text/xml; charset=utf-8`
- `SOAPAction: "<soap action above>"`
- `Accept: text/xml`
- `?sap-client=<n>` query param

## Phases

### Phase 1 — Parse & gather input
Detect count and target. Decide:

| Question | Default | When to ask |
|---|---|---|
| How many invoices? | 1 | If ambiguous |
| Which POs? | Auto-pick uninvoiced EUR PO lines on CC 1010 | If user didn't say |
| Full or partial quantity? | 50% of order qty (keeps PO not fully invoiced) | Always show before bulk |
| Backdate? | Today, unless current period is closed | If user mentioned "backdate" or current period is closed |

### Phase 2 — Tenant preflight (CRITICAL — do this once per tenant)
Before posting, verify ledger config is healthy. The `FINS_ACDOC_CUST/201` "Configuration settings need to be corrected" error blocks ALL FI postings until ledger accounting principles are assigned correctly. See `references/ledger-config-preflight.md` for the diagnosis flow and CBC fix path.

Quick probe to detect the issue:
```bash
node references/preflight-probe.mjs
```
If the probe returns `FINS_ACDOC_CUST/201` → STOP and surface the ledger-config issue to the user. Posting will not work until CBC config is fixed.

Also verify open posting periods. Tenants commonly have only a few months open; backdate accordingly.

### Phase 3 — Master-data resolution
For each target (PO, line):
1. `GET /A_PurchaseOrderItem(PurchaseOrder='<po>',PurchaseOrderItem='<line>')?$select=Material,Plant,OrderQuantity,PurchaseOrderQuantityUnit,NetPriceAmount,IsCompletelyInvoiced,PurchaseOrderItemCategory&$format=json&sap-client=<n>`
2. Get the parent PO for `Supplier`, `DocumentCurrency`, `CompanyCode`.
3. Skip if `IsCompletelyInvoiced=true` or `PurchaseOrderItemCategory` ≠ `0` (services D/9 don't post cleanly).

For bulk runs, do this in ONE fetch via `A_PurchaseOrderItem?$top=500` and `A_PurchaseOrder?$top=200`, build a Map, then iterate.

### Phase 4 — Build SOAP envelope
Use the verified shape in `references/soap-envelope-template.md`. Key field values that took experimentation to find:

| Field | Verified value | Notes |
|---|---|---|
| Header `TypeCode` | `004` | Vendor Invoice (= OData "RE") |
| Header `CompletenessAndValidationStatusCode` | `5` (post) or `A` (parked) | Status codes are alphanumeric — `1/2/3` were rejected |
| Header `BillFromID` | supplier's invoice ref | This is the "Reference" field required for doc type RE. NOT `SupplierInvoiceReference` (that's for credit-memo references) |
| Header `BillFromParty/InternalID` | Supplier ID | |
| Header `CashDiscountTerms/Code` | `0004` | or whatever the supplier's payment terms map to |
| Header `TaxCalculation/AutomaticIndicator` | `false` | When supplying explicit item ProductTaxDetails |
| Item `TypeCode` | `002` | Material item |
| Item `ProcessingTypeCode` | `M` | Material — `001/01/1/002` all rejected |
| Item `Quantity unitCode` | `PCE` | ISO code, NOT SAP-internal `PC` |
| Item `Product/InternalID` | Material from PO | Required even for PO-referenced items |
| Item `TaxCalculation/ProductTaxDetails/TaxationCharacteristicsCode` | `V0` | OData tax code passes through directly |
| Item `TaxCalculation/ProductTaxDetails/TaxAmount` | `0.00` (V0=0%) | Required field. Currency attribute too |
| Item `TaxCalculation/ProductTaxDetails/TaxBaseAmount` | = item NetAmount | |
| `HeaderReferences` | **do NOT include** | Only valid for status `A` (parked) or `D` — for status `5` (post), SAP rejects it |

`Amount` elements need `currencyCode` attribute; `Quantity` elements need `unitCode` attribute.

### Phase 5 — POST
Sequential, 200ms delay. Capture `<SupplierInvoice><ID>...<Year>...</...>` from the response. Halt on 3 consecutive failures.

Result codes:
- `BusinessDocumentProcessingResultCode = 1` → success
- `= 3` → success with warnings (e.g. "Net due date in past" for backdated invoices) — still posts, treat as success
- `= 5` → failure (read `<Note>` for reason)

### Phase 6 — Verify & report
After all POSTs, `$expand` 2–3 random target invoices to confirm structure:
```
GET /sap/opu/odata/sap/API_SUPPLIERINVOICE_PROCESS_SRV/A_SupplierInvoice(SupplierInvoice='<id>',FiscalYear='<yr>')?$expand=to_SupplierInvoiceItemPurOrdRef
```

Show user: total created, invoice ID range, supplier/PO distribution, any failures.

## Output structure
```
<cwd>/.s4hana-tmp/create-invoices-<YYYYMMDD-HHMM>/
├── candidates.json # POs eligible for invoicing
├── payloads/ # one envelope per record (debug)
├── create-log.jsonl # one line per attempt (idempotent)
├── results.json # final summary
└── verify-sample.json # spot-check of 2-3 created invoices
```

`create-log.jsonl` format (one JSON object per line):
```json
{"ts":"2026-05-11T19:14:33Z","po":"4500000000","item":"10","supplier":"10300010","date":"2025-08-01","refId":"INV-4500000000-10","ok":true,"invoiceId":"5105600103","year":"2025","result":"1","status":200}
```

On rerun, load this log first and skip any `po/item` with prior `ok=true`. Survives partial failures cleanly.

## Reference files
Read these on demand — do not load eagerly:
- `references/soap-envelope-template.md` — full XML template with placeholders
- `references/ledger-config-preflight.md` — FINS_ACDOC_CUST/201 diagnosis + CBC fix path
- `references/known-error-codes.md` — error catalog with fixes (IVE_E_INVOICE/052, M8_2/057, M8/375, F5/480, FINS_ACDOC_CUST/201, etc.)
- `references/preflight-probe.mjs` — runnable script to check tenant readiness
- `scripts/bulk-invoice-poster.mjs` — reference implementation, 50-invoice batch
