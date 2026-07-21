# PO Confirmation SOAP envelope template

**Verified against SAP S/4HANA Cloud Public Edition.** Service: `SupplierConfirmationRequest_In` at `/sap/bc/srt/scs_ext/sap/supplierconfirmationrequest_i1`.

## Endpoint

```
POST https://<host>/sap/bc/srt/scs_ext/sap/supplierconfirmationrequest_i1?sap-client=<n>
Authorization: Basic <base64(user:pass)>
Content-Type: text/xml; charset=utf-8
SOAPAction: "http://sap.com/xi/Procurement/SupplierConfirmationRequest_In/SupplierConfirmationRequest_InRequest"
Accept: text/xml
```

Expected response: **HTTP 202 No Content** (asynchronous accept — message is queued for backend processing).

## Minimal working envelope

```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:wsa="http://www.w3.org/2005/08/addressing"
               xmlns:n0="http://sap.com/xi/Procurement">
  <soap:Header>
    <wsa:Action soap:mustUnderstand="1">http://sap.com/xi/Procurement/SupplierConfirmationRequest_In/SupplierConfirmationRequest_InRequest</wsa:Action>
    <wsa:To soap:mustUnderstand="1">{{full endpoint URL}}</wsa:To>
    <wsa:MessageID>urn:uuid:{{generated uuid v4}}</wsa:MessageID>
    <wsa:ReplyTo><wsa:Address>http://www.w3.org/2005/08/addressing/anonymous</wsa:Address></wsa:ReplyTo>
  </soap:Header>
  <soap:Body>
    <n0:SupplierConfirmationRequest>
      <MessageHeader>
        <CreationDateTime>{{ISO 8601 timestamp, e.g. 2026-05-12T13:30:00Z}}</CreationDateTime>
      </MessageHeader>
      <SupplierConfirmation>
        <ActionCode>01</ActionCode>
        <SuplrConfExternalReference>{{free text, max 35 chars}}</SuplrConfExternalReference>
        <PurchaseOrderID>{{po number, e.g. 4500000020}}</PurchaseOrderID>
        <SupplierConfirmationItem>
          <PurchaseOrderItemID>{{po item, e.g. 10}}</PurchaseOrderItemID>
          <SupplierConfirmationLine>
            <ConfirmedDeliveryDate>{{YYYY-MM-DD}}</ConfirmedDeliveryDate>
            <ConfirmedQuantity unitCode="{{ISO unit code: PCE, KGM, etc.}}">{{qty}}</ConfirmedQuantity>
          </SupplierConfirmationLine>
        </SupplierConfirmationItem>
      </SupplierConfirmation>
    </n0:SupplierConfirmationRequest>
  </soap:Body>
</soap:Envelope>
```

## Critical pieces — don't skip these

### 1. WS-Addressing headers are mandatory

The WSDL declares `<wsaw:UsingAddressing/>` without `Optional="true"`. Without all four WS-A headers, the service rejects with a generic 500 `Web service processing error` and zero diagnostic detail.

Required:
- `wsa:Action` — the SOAP action URI (matches the `SOAPAction` HTTP header)
- `wsa:To` — the full endpoint URL (including `https://...?sap-client=`)
- `wsa:MessageID` — a unique URN UUID
- `wsa:ReplyTo` — usually `http://www.w3.org/2005/08/addressing/anonymous` for one-way calls

Use namespace `http://www.w3.org/2005/08/addressing` (2005 WS-A spec). The 2004/08 namespace appears in the WSDL but the runtime expects the 2005 one.

### 2. ActionCode enum

The WSDL restricts to exactly three values:

| Code | Meaning | Required additional fields |
|---|---|---|
| `01` | Create (Add) — verified end-to-end | None — system auto-assigns `SupplierConfirmation` sequential number |
| `02` | Update (Change) — accept-only verification (Fiori check required) | `SupplierConfirmation` (existing sequential number) |
| `03` | Delete (Remove) — accept-only verification (Fiori check required) | `SupplierConfirmation` |

Other values (e.g. `04`) are silently rejected as generic 500 — the enum check fires before any diagnostic gets emitted.

### 3. PO line `SupplierConfirmationControlKey` must be set

On a fresh tenant, all PO lines default `SupplierConfirmationControlKey` to empty (`""`). Confirmations sent against an empty-CCK line are:

- **Accepted as HTTP 202** (queued)
- **Silently discarded** during async processing — no error, no commit

PATCH the field BEFORE posting the confirmation:

```http
PATCH /sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV/A_PurchaseOrderItem(PurchaseOrder='<po>',PurchaseOrderItem='<line>')
{"SupplierConfirmationControlKey": "0001"}
```

`"0001"` is the typical default value. Verify by querying existing PO items if `"0001"` doesn't work on your tenant.

### 4. SOAP version + content type combinations

| Content-Type | Envelope namespace | Behavior |
|---|---|---|
| `text/xml; charset=utf-8` | `http://schemas.xmlsoap.org/soap/envelope/` (SOAP 1.1) | ✅ Works — what this template uses |
| `application/soap+xml; charset=utf-8` | `http://www.w3.org/2003/05/soap-envelope` (SOAP 1.2) | ✅ Also works — alternative |
| Mismatch (e.g. SOAP 1.1 namespace with SOAP 1.2 Content-Type) | — | ❌ Returns `VersionMismatch` fault |

Stick to the SOAP 1.1 combination above unless you have a reason to use 1.2.

## Response handling

Successful POST returns **HTTP 202** with empty body. There's no SOAP response envelope — this is one-way async.

Errors come as SOAP fault envelopes:

```xml
<soap:Fault>
  <faultcode>soap:Server</faultcode>
  <faultstring xml:lang="en">{{error message}}</faultstring>
  <detail/>
</soap:Fault>
```

Common faults:
- `Web service processing error; more details in the web service error log on provider side` → WS-Addressing headers missing or malformed
- `Wrong SOAP Version` → namespace/content-type mismatch
- `VersionMismatch` → same as above
- HTTP 403 (HTML response, not SOAP) → comm arrangement `SAP_COM_0827` not granted

## Verification

The service is one-way async — HTTP 202 ≠ committed. To verify the confirmation actually applied:

**Fiori check** (only reliable method on this tenant): Open PO in "Manage Purchase Orders" → item → **Supplier Confirmation tab**. The confirmation should appear with:
- Sequential number (auto-assigned: 1, 2, 3...)
- Confirm. Category = `AB` (Order Acknowledgement) for ActionCode 01
- Delivery Date / Quantity matching what was sent

Spot-check 2-3 confirmations in Fiori after every bulk batch.

## Multi-line confirmations

A single SupplierConfirmation can carry multiple items + lines:

```xml
<SupplierConfirmationItem>
  <PurchaseOrderItemID>10</PurchaseOrderItemID>
  <SupplierConfirmationLine>
    <ConfirmedDeliveryDate>2026-05-20</ConfirmedDeliveryDate>
    <ConfirmedQuantity unitCode="PCE">50</ConfirmedQuantity>
  </SupplierConfirmationLine>
  <SupplierConfirmationLine>
    <ConfirmedDeliveryDate>2026-06-15</ConfirmedDeliveryDate>
    <ConfirmedQuantity unitCode="PCE">30</ConfirmedQuantity>
  </SupplierConfirmationLine>
</SupplierConfirmationItem>
```

Use this for split deliveries — supplier confirms part now, part later.
