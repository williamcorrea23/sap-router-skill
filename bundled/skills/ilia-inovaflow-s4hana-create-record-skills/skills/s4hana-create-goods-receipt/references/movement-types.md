# Goods Movement Types — common codes for SAP S/4HANA Cloud

SAP movement types are the canonical 3-digit codes that classify what kind of stock movement a Material Document represents. This skill's primary focus is **receipts (1xx series)**, but other types are documented here for awareness.

## Receipts (1xx) — relevant to this skill

| Type | Meaning | Reference | Common use |
|---|---|---|---|
| **`101`** | Goods receipt for purchase order to warehouse | PO (B) | Standard GR — what `s4hana-create-goods-receipt` defaults to |
| `102` | Reversal of GR for PO | Material Document | Cancellation/reversal of a prior 101 |
| `103` | Receipt to stock-in-quality-inspection | PO | When inbound goods need QM before usable |
| `105` | Release from quality stock | PO | Pair with 103 — releases to unrestricted stock |
| `106` | Reversal of 105 | Material Document | |
| `122` | Return delivery to supplier | PO (B) | Returning rejected goods. Negative effective qty |
| `123` | Cancellation of return delivery | Material Document | Reverse a 122 |
| `161` | Returns delivery for purchase order | PO (B) | Similar to 122 but different flow context |

## Issues (2xx) — NOT in scope for this skill
Used for goods issues (consumption, sales, scrapping). Use a different skill if needed.

## Transfers (3xx / 4xx) — NOT in scope
Stock transfers between storage locations, plants, etc.

## Stock Type combinations

The `InventoryStockType` field on items further classifies the receipt:

| Code | Meaning |
|---|---|
| `F` | Unrestricted-use stock (most common GR result) |
| `S` | Blocked stock |
| `Q` | Quality-inspection stock (paired with type 103) |
| `Z` | Customs / external stock |

For typical receipts, leave `InventoryStockType` unset → defaults to `F`.

## GoodsMovementRefDocType — reference type codes

This is the field you MUST include alongside `PurchaseOrder` for receipt types. Common values:

| Code | Meaning | When to use |
|---|---|---|
| **`B`** | Purchase Order | **Standard for type 101 receipts** |
| `L` | Inbound Delivery (ASN) | When GR comes from a delivery doc |
| `Q` | Project / WBS Element | Project-driven receipts |
| `R` | Material Reservation | Pre-reserved stock |

For PO-based receipts (the common case), always use `"B"`.

## Special-case quirks

### Serialized materials (`M7/175`)
If the material has serial-number management enabled, GR requires a `to_SerialNumber` deep-insert with one serial number per unit:

```json
"to_MaterialDocumentItem": [{
  ...
  "to_SerialNumber": { "results": [{ "SerialNumber": "SN001" }, { "SerialNumber": "SN002" }] }
}]
```

Out of scope for the default skill — filter these materials out of bulk runs.

### Batch-managed materials
If the material has batch management, `Batch` field is required on the item. Some tenants auto-assign batch numbers; on others you need to pre-create the batch via `A_Batch` POST first.

### Returns (type 122/123)
Returns delivery (type 122) creates a negative-quantity material document. Requires:
- Same Material + PurchaseOrder/Item as the original GR
- `GoodsMovementType="122"` instead of `101`
- Cumulative return qty cannot exceed original GR qty (else `M7/021`)

### Reversal of GR (type 102)
To reverse a specific Material Document:
- `GoodsMovementType="102"`
- `GoodsMovementRefDocType="W"` (Material Document)
- Reference the original `MaterialDocument` + `MaterialDocumentYear` + `MaterialDocumentItem`
- Quantity must match exactly

Not in scope for the create-goods-receipt skill (creation only).
