# GR envelope template — A_MaterialDocumentHeader deep-insert

**Verified against SAP S/4HANA Cloud Public Edition 2026-05-12.**

## Endpoint
```
POST https://<host>/sap/opu/odata/sap/API_MATERIAL_DOCUMENT_SRV/A_MaterialDocumentHeader?sap-client=<n>
Authorization: Basic <base64(user:pass)>
X-CSRF-Token: <captured>
Cookie: <captured>
Content-Type: application/json
Accept: application/json
```

## Minimal working envelope (GR for PO, single item)

```json
{
 "DocumentDate": "/Date({{ms}})/",
 "PostingDate": "/Date({{ms}})/",
 "MaterialDocumentHeaderText": "{{free text, max 25 chars}}",
 "GoodsMovementCode": "01",
 "to_MaterialDocumentItem": [
 {
 "Material": "{{exact material from PO line}}",
 "Plant": "{{plant from PO line, e.g. 1010}}",
 "StorageLocation": "{{e.g. 101A}}",
 "GoodsMovementType": "101",
 "GoodsMovementRefDocType": "B",
 "PurchaseOrder": "{{po number}}",
 "PurchaseOrderItem": "{{po item, e.g. 10}}",
 "QuantityInEntryUnit": "{{qty}}",
 "EntryUnit": "{{unit from PO line, e.g. PC}}"
 }
 ]
}
```

## Field reference (header)

| Field | Required | Notes |
|---|---|---|
| `MaterialDocument`, `MaterialDocumentYear` | auto | System-assigned in `500000000x` range, paired with year |
| `DocumentDate` | yes | OData V2 `/Date(ms)/` format |
| `PostingDate` | yes | **Must be in open MM period.** Different from FI period. `M7/053` if closed |
| `MaterialDocumentHeaderText` | optional | Free text, max 25 chars |
| `GoodsMovementCode` | yes | `"01"` for GR. Header-level code that classifies the document type. |
| `ReferenceDocument` | optional | External reference number (e.g. delivery note no.) |

## Field reference (item)

| Field | Required | Notes |
|---|---|---|
| `Material` | yes | Must EXACTLY match referenced PO line's material. `M7/360` if mismatched |
| `Plant` | yes | Match PO line |
| `StorageLocation` | yes for stock | `101A` is the common default on a Cloud Public tenant |
| `GoodsMovementType` | yes | `"101"` = Receipt for PO. See movement-types.md for full list |
| `GoodsMovementRefDocType` | **yes when PO-based** | `"B"` for PO reference. Without it, the API rejects PURCHASEORDER fields |
| `PurchaseOrder` | conditional | Required when `GoodsMovementRefDocType="B"` |
| `PurchaseOrderItem` | conditional | The PO item number (not zero-padded — "10" works) |
| `QuantityInEntryUnit` | yes | Numeric, supports partial qty |
| `EntryUnit` | yes | Must match PO line's `PurchaseOrderQuantityUnit` |
| `Batch` | conditional | Required for batch-managed materials |
| `GoodsMovementReasonCode` | conditional | Required for some movement types (returns, etc.) |
| `GoodsRecipientName`, `UnloadingPointName` | optional | For delivery routing |

## Multi-item GRs

Repeat `to_MaterialDocumentItem` for multiple receipts in one document:

```json
"to_MaterialDocumentItem": [
 { "Material": "FG041", "Plant": "1010", "StorageLocation": "101A", "GoodsMovementType": "101", "GoodsMovementRefDocType": "B", "PurchaseOrder": "4500000000", "PurchaseOrderItem": "10", "QuantityInEntryUnit": "250", "EntryUnit": "PC" },
 { "Material": "FG011", "Plant": "1010", "StorageLocation": "101A", "GoodsMovementType": "101", "GoodsMovementRefDocType": "B", "PurchaseOrder": "4500000001", "PurchaseOrderItem": "20", "QuantityInEntryUnit": "100", "EntryUnit": "PC" }
]
```

Each item creates a row in the material document. Header is single.

## What NOT to include

- **`PurchaseOrder` without `GoodsMovementRefDocType="B"`** — rejected: `MM_IM_ODATA_API_MDOC/011: Property PURCHASEORDER is not supported for GoodsMovementType 101`
- **`MaterialDocument` / `MaterialDocumentYear`** in payload — system-assigned, sending values gets ignored
- **`Supplier`** on the item — auto-derived from referenced PO

## Response

Success returns:
```json
{
 "d": {
 "MaterialDocument": "5000000001",
 "MaterialDocumentYear": "2025",
 "DocumentDate": "/Date(...)/",
 "PostingDate": "/Date(...)/",
 "GoodsMovementCode": "01",
 "to_MaterialDocumentItem": { ... }
 }
}
```

## Side-effects on related records

After successful GR posting:
- The referenced PO line's `GoodsReceiptQuantity` increases by the received amount
- `IsCompletelyDelivered` flips to `true` once cumulative GR qty ≥ ordered qty
- `EnterpriseInventoryAssignment` records update (stock levels)
- For services (cat-A limit items, ProductType=2): no stock impact, but `IsCompletelyDelivered` still tracks

These side-effects mean once a GR exists on a PO line, that line can be invoiced via the supplier-invoice skill with three-way match validation.
