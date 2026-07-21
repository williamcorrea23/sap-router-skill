# SES envelope template — A_ServiceEntrySheet deep-insert

**Verified against SAP S/4HANA Cloud Public Edition 2026-05-12** (SES 1, 2, 3 created via API).

## Endpoint
```
POST https://<host>/sap/opu/odata/sap/API_SERVICE_ENTRY_SHEET_SRV/A_ServiceEntrySheet?sap-client=<n>
Authorization: Basic <base64(user:pass)>
X-CSRF-Token: <captured>
Cookie: <captured>
Content-Type: application/json
Accept: application/json
```

## Minimal working envelope (one PO-referenced item)

```json
{
 "ServiceEntrySheetName": "{{40-char free text label}}",
 "PurchaseOrder": "{{po number}}",
 "PostingDate": "/Date({{ms since epoch}})/",
 "Currency": "{{currency code, e.g. EUR}}",
 "to_ServiceEntrySheetItem": [
 {
 "ServiceEntrySheetItem": "10",
 "PurchaseOrder": "{{same po}}",
 "PurchaseOrderItem": "{{service-line item number, e.g. 10}}",
 "ConfirmedQuantity": "{{qty performed}}",
 "QuantityUnit": "{{match PO unit, e.g. AU}}",
 "NetPriceAmount": "{{match PO price}}",
 "Currency": "{{currency}}",
 "Plant": "{{plant from PO line}}",
 "ServiceEntrySheetItemDesc": "{{40-char description}}",
 "ServicePerformanceDate": "/Date({{ms}})/",
 "ServicePerformanceEndDate": "/Date({{ms}})/"
 }
 ]
}
```

## Multi-item SES
Repeat the `to_ServiceEntrySheetItem` array. Each gets its own ServiceEntrySheetItem (10, 20, 30, ...) and can reference a different PO line on the same PO.

## What NOT to include

- **`to_AccountAssignment` on the item** — SES auto-inherits AAC/CostCenter/GLAccount from the PO line. Explicit deep-insert often triggers `MM_PUR_SES/128: accounting lines not numbered consecutively`. Only include if you need to OVERRIDE the inherited assignment.
- **`AccountAssignmentCategory` on the item** — also auto-inherited.
- **`ServiceEntrySheet` (header key)** — auto-assigned by SAP starting at "1".
- **`Supplier` (header)** — auto-derived from referenced PO.
- **`SESWorkflowStatus`, `ApprovalStatus`** — system-managed; new SES enters "draft/in-process" automatically.

## Response

Success returns:
```json
{
 "d": {
 "ServiceEntrySheet": "3",
 "ServiceEntrySheetUUID": "3783ac1e-246e-1fd1-...",
 "ServiceEntrySheetName": "...",
 "PurchaseOrder": "4500000093",
 "Supplier": "1000080",
 "Currency": "EUR",
 ...
 }
}
```

The new SES ID is short (1, 2, 3, ... — not zero-padded like POs).

## Field reference (header)

| Field | Required | Notes |
|---|---|---|
| `ServiceEntrySheet` | system-assigned | leave empty |
| `ServiceEntrySheetName` | yes | 40 chars |
| `PurchaseOrder` | yes | the service PO to reference |
| `PostingDate` | yes | OData V2 `/Date(ms)/` format. Must be in open MM period |
| `Currency` | yes | match PO currency |
| `PurchasingOrganization`, `PurchasingGroup` | auto | inherited from PO |
| `Supplier` | auto | inherited from PO |
| `OriginObjectType`, `OriginObject` | optional | for external-reference workflows |
| `PurgDocExternalSystem`, `PurgDocExternalReference` | optional | for IDoc/SOAP integrations |
| `ApprovalStatus`, `SESWorkflowStatus` | system-managed | don't set |

## Field reference (item)

| Field | Required | Notes |
|---|---|---|
| `ServiceEntrySheetItem` | yes | 10, 20, 30 ... |
| `PurchaseOrder`, `PurchaseOrderItem` | yes | the cat-0 SERVICE LINE on the PO (NOT cat-A limit line) |
| `ConfirmedQuantity` | yes | how much was performed |
| `QuantityUnit` | yes | match PO line unit |
| `NetPriceAmount` | yes | per-unit price (match PO) |
| `Currency`, `Plant` | yes | match PO |
| `ServiceEntrySheetItemDesc` | recommended | 40-char description |
| `ServicePerformanceDate`, `ServicePerformanceEndDate` | yes | both required. Must fall within PO line's allowed window (typically PO-date or later) |
| `AccountAssignmentCategory` | auto | inherited from PO |
| `MaterialGroup` | auto | inherited from PO line |
| `Service` | auto | the SERV material from PO line |
| `TaxCode`, `TaxCountry` | auto | inherited unless overriding |
| `ServicePerformer` | optional | text — who did the work |
| `WorkItem` | optional | work-item ID for workflow link |

## Account-assignment override (rarely needed)

If you actually need to split the cost across multiple cost centers or change the inherited one, add `to_AccountAssignment` carefully — the account-assignment numbers MUST be consecutively numbered starting at "01" or you'll get `MM_PUR_SES/128`.

```json
"to_AccountAssignment": [
 { "AccountAssignment": "01", "CostCenter": "10101101", "GLAccount": "11001040", "ControllingArea": "A000" },
 { "AccountAssignment": "02", "CostCenter": "10101102", "GLAccount": "11001040", "ControllingArea": "A000", "MultipleAcctAssgmtDistrPercent": "50.0" }
]
```

Skip this entirely for typical use.
