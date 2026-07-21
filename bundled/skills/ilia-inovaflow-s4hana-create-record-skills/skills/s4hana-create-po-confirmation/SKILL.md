---
name: s4hana-create-po-confirmation
description: Create supplier (PO) confirmations in SAP S/4HANA Cloud Public or on-prem private edition via the SOAP A2X "SupplierConfirmationRequest" service. Use whenever the user wants to create, post, add, generate, seed, simulate, or record supplier acknowledgements / order confirmations / vendor confirmations on S/4HANA — phrases like "confirm these POs", "acknowledge order receipt", "post a supplier confirmation", "seed PO confirmation demo data", "simulate supplier accepting PO", "vendor confirmed delivery". Handles the WS-Addressing-required SOAP envelope, the SupplierConfirmationControlKey prerequisite (PATCHes PO lines that don't have it), the one-way async response model (202 Accepted), and idempotent bulk batches. Do NOT use for goods receipts (use s4hana-create-goods-receipt instead), inbound delivery / ASN, or service confirmations (those use different SOAP services).
---

# s4hana-create-po-confirmation

Create supplier order confirmations on SAP S/4HANA Cloud Public via the SOAP A2X service. **Verified end-to-end against SAP S/4HANA Cloud Public Edition 2026-05-12 — confirmation visible in Fiori "Supplier Confirmation" tab on PO 4500000020/10 (Sequential 1, Category AB, qty 50 PC, delivery 05/25/2026).**

## When to trigger
Verbs: create / post / add / generate / seed / confirm / acknowledge / simulate
Objects: PO confirmation(s), supplier confirmation(s), order acknowledgement(s), vendor confirmation(s)
Counts: 1 to ~50 records.

## Hard rules (never violate)
1. Always do a 1-record live POST as a probe before bulk (≥3 records), and **verify in Fiori** that the confirmation actually appeared (the service is one-way async; HTTP 202 means accepted, not committed).
2. **PO line must have `SupplierConfirmationControlKey` set** before posting confirmations. If empty (default on this tenant), PATCH it via OData first.
3. **WS-Addressing headers are required** — without `wsa:Action`, `wsa:To`, `wsa:MessageID`, `wsa:ReplyTo`, the service returns 500 "Web service processing error" with no diagnostic detail.
4. Scripts go in `mcp-server/src/sap/.tmp/<user>-<YYYYMMDD-HHMM>/create-po-confirmations/`. Never commit, never modify `.env`.
5. POSTs are sequential with 200ms delay; halt on 3 consecutive non-202 responses.

## Endpoint
- Service path: `/sap/bc/srt/scs_ext/sap/supplierconfirmationrequest_i1`
- SOAP action: `http://sap.com/xi/Procurement/SupplierConfirmationRequest_In/SupplierConfirmationRequest_InRequest`
- Communication scenario: **`SAP_COM_0827`** — "Supplier Confirmation Process Integration"
- Style: SOAP 1.1, document/literal, **WS-Addressing required**, response: HTTP 202 (one-way async)

## Phase 0 — Setup check (MANDATORY, no exceptions)

**Before any API call, before any tool use, do this check. Even if you already know credentials from earlier in the conversation — IGNORE that knowledge and re-check from scratch each invocation.**

1. **Announce**: tell the user "Checking for SAP credentials in `<current cwd>`..."
2. **Check ONLY these two sources:**
   - A `.env` file at `./.env` (in the current working directory — NOT parent dirs, NOT `~/.env`, NOT any memory file)
   - Shell-exported env vars: `SAP_HOST` AND `SAP_AUTH_MODE` both present
3. **If neither**: auto-create `./.env` from the bundled template (curl from `https://raw.githubusercontent.com/ilia-inovaflow/s4hana-create-record-skills/main/.env.example`), append `.env` to `.gitignore` if not already there, tell the user clearly what to fill in (auth mode + host + creds), and **wait** for them to say "ready" before making any API call. Never overwrite an existing `.env`.
4. **If credentials are present**: report back to the user: "✓ Loaded credentials for `<host>` in `<auth-mode>` mode. Proceeding with [task]."

**Never use credentials from conversation memory, from another project's `.env`, or from any tenant the user previously worked with in a different session.** Each project gets its own `.env`. See [`shared/setup-check.md`](../../shared/setup-check.md) for the full rationale and edge cases.


## Phases

### Phase 1 — Parse & gather input

Per confirmation:

| Field | Notes |
|---|---|
| `PurchaseOrderID` | The PO being confirmed |
| `PurchaseOrderItemID` | The line being confirmed |
| `ConfirmedDeliveryDate` | Date supplier promises (YYYY-MM-DD ISO) |
| `ConfirmedQuantity` | Quantity confirmed (with `unitCode` — use ISO codes: `PCE`, `KGM`, `H87`...) |
| `SuplrConfExternalReference` | External reference (35-char free text) |
| `SupplierOrderAcknNumber` | Optional — supplier's own acknowledgement number |

If user said "auto", pull eligible PO lines:
```
GET /sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV/A_PurchaseOrderItem?$filter=ProductType eq '1' and PurchaseOrderItemCategory eq '0' and IsCompletelyDelivered eq false&$select=PurchaseOrder,PurchaseOrderItem,Material,Plant,OrderQuantity,PurchaseOrderQuantityUnit,SupplierConfirmationControlKey
```

### Phase 2 — Prerequisite check: PO line must have a Confirmation Control Key

This tenant defaults `SupplierConfirmationControlKey` to empty on all PO lines. Confirmations sent against an empty-CCK line are silently accepted (HTTP 202) but never commit. Set it via OData PATCH before posting:

```http
PATCH /sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV/A_PurchaseOrderItem(PurchaseOrder='<po>',PurchaseOrderItem='<line>')?sap-client=<n>
X-CSRF-Token: <captured>
Cookie: <captured>
Content-Type: application/json

{"SupplierConfirmationControlKey": "0001"}
```

Valid key on a Cloud Public tenant: **`0001`**. Returns HTTP 204 on success. After this, confirmations against that PO line will commit.

If you're seeding many confirmations: PATCH all eligible PO lines first (one OData call each), then start posting confirmations.

### Phase 3 — Build SOAP envelope

**Verified working envelope:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
 xmlns:wsa="http://www.w3.org/2005/08/addressing"
 xmlns:n0="http://sap.com/xi/Procurement">
 <soap:Header>
 <wsa:Action soap:mustUnderstand="1">http://sap.com/xi/Procurement/SupplierConfirmationRequest_In/SupplierConfirmationRequest_InRequest</wsa:Action>
 <wsa:To soap:mustUnderstand="1">{{full endpoint url}}</wsa:To>
 <wsa:MessageID>urn:uuid:{{guid}}</wsa:MessageID>
 <wsa:ReplyTo><wsa:Address>http://www.w3.org/2005/08/addressing/anonymous</wsa:Address></wsa:ReplyTo>
 </soap:Header>
 <soap:Body>
 <n0:SupplierConfirmationRequest>
 <MessageHeader>
 <CreationDateTime>{{ISO datetime}}</CreationDateTime>
 </MessageHeader>
 <SupplierConfirmation>
 <ActionCode>01</ActionCode>
 <SuplrConfExternalReference>{{free text, max 35 chars}}</SuplrConfExternalReference>
 <PurchaseOrderID>{{po number}}</PurchaseOrderID>
 <SupplierConfirmationItem>
 <PurchaseOrderItemID>{{po item, e.g. 10}}</PurchaseOrderItemID>
 <SupplierConfirmationLine>
 <ConfirmedDeliveryDate>{{YYYY-MM-DD}}</ConfirmedDeliveryDate>
 <ConfirmedQuantity unitCode="{{ISO unit, e.g. PCE}}">{{qty}}</ConfirmedQuantity>
 </SupplierConfirmationLine>
 </SupplierConfirmationItem>
 </SupplierConfirmation>
 </n0:SupplierConfirmationRequest>
 </soap:Body>
</soap:Envelope>
```

**ActionCode enum (from WSDL — only 3 values allowed):**

| Code | Meaning | Verification |
|---|---|---|
| `01` | Create | ✅ Verified end-to-end — creates category AB (Order Acknowledgement) |
| `02` | Update | ⚠️ Accepted (202) but outcome requires Fiori verification — likely requires `SupplierConfirmation` ID to identify which existing one to update |
| `03` | Delete | ⚠️ Accepted (202) but outcome requires Fiori verification — likely requires `SupplierConfirmation` ID |

Skill default: use ActionCode `01`. Update/delete are exposed but treated as advanced — confirm with user before using them and require user to verify in Fiori after.

### Phase 4 — POST
```http
POST /sap/bc/srt/scs_ext/sap/supplierconfirmationrequest_i1?sap-client=<n>
Authorization: Basic <base64(user:pass)>
Content-Type: text/xml; charset=utf-8
SOAPAction: "http://sap.com/xi/Procurement/SupplierConfirmationRequest_In/SupplierConfirmationRequest_InRequest"
Accept: text/xml
```

Expected response: **HTTP 202** (Accepted, no body). This is normal for one-way async services.

If response is HTTP 500 with fault `Wrong SOAP Version` → you used `application/soap+xml` Content-Type. Switch to `text/xml`.

If response is HTTP 500 with fault `Web service processing error... details in the web service error log on provider side` → WS-Addressing headers missing OR malformed. Re-check `wsa:Action`, `wsa:To`, `wsa:MessageID`, `wsa:ReplyTo`.

### Phase 5 — Verify (manual)

The service is one-way async. **HTTP 202 doesn't guarantee commit.** To verify:

**Via Fiori**: Open PO in "Manage Purchase Orders" → item → **Supplier Confirmation tab**. The confirmation should appear with:
- Confirm. Category = `AB` (Order Acknowledgement) for ActionCode 01
- Delivery Date / Time / Quantity matching what you sent
- Sequential number assigned automatically (1, 2, 3, ...)

**Via API**: Not possible on this tenant — `to_ScheduleLine` shows the original PO schedule, not confirmations. The confirmation data lives in `EKES` (table) which isn't exposed via OData V2 in the standard PO service.

For bulk runs: spot-check 2–3 records in Fiori after the batch completes.

## Output structure
```
mcp-server/src/sap/.tmp/<user>-<YYYYMMDD-HHMM>/create-po-confirmations/
├── eligible-po-lines.json
├── cck-patches.jsonl # log of which PO lines we PATCHed with confirmation control key
├── create-log.jsonl # one line per SOAP attempt
├── results.json # summary
└── verify-checklist.md # printable list of POs to spot-check in Fiori
```

## Reference files
- `references/soap-envelope-template.md` — full XML template with WS-A headers + ActionCode notes
- `references/known-quirks.md` — the 3 gotchas (WS-A required, CCKey prerequisite, async-202-doesn't-mean-success)
- `scripts/bulk-poc-poster.mjs` — reference implementation with PATCH-then-POST flow
