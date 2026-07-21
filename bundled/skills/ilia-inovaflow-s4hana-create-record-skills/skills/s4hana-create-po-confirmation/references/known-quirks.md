# Known quirks — Supplier Confirmation Request SOAP service

Three things that wasted hours of debugging without WSDL-level visibility. All baked into the skill but documented here for context.

## 1. WS-Addressing headers are mandatory (no fault on missing)

The WSDL has `<wsaw:UsingAddressing/>` (WITHOUT `wsp:Optional="true"`). At runtime, the service silently rejects messages without WS-A headers with a generic fault:

```
Web service processing error; more details in the web service error log on provider side
```

That fault gives you ZERO clue what's wrong. The fix is to include all four standard WS-A header elements:

```xml
<soap:Header>
 <wsa:Action soap:mustUnderstand="1">{{soap action URI}}</wsa:Action>
 <wsa:To soap:mustUnderstand="1">{{full endpoint URL}}</wsa:To>
 <wsa:MessageID>urn:uuid:{{generated guid}}</wsa:MessageID>
 <wsa:ReplyTo><wsa:Address>http://www.w3.org/2005/08/addressing/anonymous</wsa:Address></wsa:ReplyTo>
</soap:Header>
```

Use namespace `http://www.w3.org/2005/08/addressing` (the 2005 spec, not the older 2004/08 one).

Other SAP A2X services on the same tenant (e.g. `ecc_suplrinvcerpcrtrc` for supplier invoices) have WS-A as **optional** — that's why they work without these headers. Per-service policy.

## 2. PO line `SupplierConfirmationControlKey` must be non-empty

On this tenant (and likely most Cloud Public tenants without explicit defaulting config), `SupplierConfirmationControlKey` on `A_PurchaseOrderItem` defaults to empty (`""`). Confirmations sent against an empty-CCK line are:
- **Accepted as 202** (the SOAP message is queued)
- **Silently discarded** during async processing (no error, no commit)

The fix is to PATCH the PO line BEFORE posting the confirmation:

```http
PATCH /sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV/A_PurchaseOrderItem(PurchaseOrder='<po>',PurchaseOrderItem='<line>')?sap-client=<n>
Content-Type: application/json
{"SupplierConfirmationControlKey": "0001"}
```

Valid key on a Cloud Public tenant: `0001`. Other tenants may have `Z001`, `0002`, etc. — query existing PO items to find values in use.

**No public OData entity exposes the list of valid confirmation control keys.** The values are defined in tenant customizing (CBC config activity "Confirmation Control Keys"). If `0001` doesn't work on a different tenant, ask the user or default to whatever the tenant's existing POs use.

## 3. One-way async — 202 doesn't mean success

The WSDL declares this operation with `<wsdl:input/>` but **NO `<wsdl:output/>`**. That means the service returns HTTP 202 (Accepted) immediately after the SOAP message is queued — processing happens in background.

Implications:
- HTTP 202 doesn't guarantee the confirmation committed
- No structured success/failure response is returned
- Errors during async processing land in the SAP web service error log (transaction `SRT_UTIL` in old SAP, or Fiori app "Display Web Service Error Logs" on Cloud Public)
- The only reliable verification is to fetch the PO's confirmations afterwards — via Fiori UI in this case, since the API doesn't expose them

Practical implication: after bulk posting, **spot-check 2-3 confirmations in Fiori** ("Manage Purchase Orders" → item → Supplier Confirmation tab) to confirm they actually committed.

## ActionCode enum (only 3 valid values)

The WSDL enumerates only 3 ActionCode values (others are rejected with WSP/generic processing fault):

| Code | Meaning | Required additional fields |
|---|---|---|
| `01` | Create (Add) | None — system auto-assigns `SupplierConfirmation` sequential number |
| `02` | Update (Change) | `SupplierConfirmation` (the existing sequential number to update) |
| `03` | Delete (Remove) | `SupplierConfirmation` (the sequential number to remove) |

Common mistake: trying `04` (create) like in some other SAP services — rejected by enum validation, results in generic 500.

## Confirmation Categories on the resulting record

The "Confirm. Category" you see in Fiori is auto-assigned by SAP based on the SOAP message content:

| Cat | Source | When |
|---|---|---|
| `AB` | Order Acknowledgement (Auftragsbestätigung) | Default — when sending a basic confirmation with delivery date + qty |
| `LA` | Shipping Notification (Lieferavis) | Requires inbound delivery / shipping fields (this skill doesn't generate these) |
| `WA` | Shipping Notification - Service | For service-based confirmations |

For typical demos, `AB` is what you want — supplier acknowledging the PO with promised delivery date + qty. The skill generates AB by default.

## Tenant config gates we've documented

If the SOAP endpoint is wholly unreachable:
- Returns HTTP 403 HTML → comm arrangement `SAP_COM_0827` not added to the user. Add it via Fiori → Communication Arrangements → New → SAP_COM_0827.

If the endpoint is reachable but messages don't commit:
- See gotcha #2 above (CCKey)
- Check the web service error log for the actual backend error (only the user can view this)
