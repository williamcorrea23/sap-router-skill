# PO write quirks — `API_PURCHASEORDER_PROCESS_SRV`

**Verified by hand against SAP S/4HANA Cloud Public Edition. 88 goods POs + 3 service POs created via this pattern.**

## 1. CSRF flow is required
GET service root with `X-CSRF-Token: Fetch` + `Authorization`. Capture both the `x-csrf-token` response header AND every `Set-Cookie` (use `res.headers.getSetCookie()` in Node — the regular header iter merges them). POST with both `X-CSRF-Token: <captured>` and `Cookie: <name=value; ...>`.

See `csrf-flow.md` for the exact code pattern.

## 2. No `$format=json` on POST URLs
SAP rejects with:
```
/IWBEP/CM_MGW_RT/022 — The Data Services Request contains SystemQueryOptions that are not allowed for this Request Type
```
Use `Accept: application/json` header instead. `sap-client=NNN` query param is fine (not a system query option). Keep `$format=json` only on GETs.

## 3. System fields are read-only on POST
`CreationDate`, `LastChangeDateTime`, `CreatedByUser` are stamped by SAP at POST time. Any value sent is silently ignored.

To backdate documents, set `PurchaseOrderDate` — that's the legal/business date and IS settable. The system-stamped audit date will still reflect today.

## 4. Quantity unit must match target master data
On `<your-tenant>`, the FERT product pool is uniformly `BaseUnit=PC`, the SERV pool is `BaseUnit=AU`. Sending mismatched units returns:
```
400 — The input of field PURCHASEORDERQUANTITYUNIT on A_PurchaseOrderItemType level cannot be processed
```
Solution: align `PurchaseOrderQuantityUnit` with the material's BaseUnit.

## 5. Item categories — limited dropdown on Cloud Public
Fiori shows only: **Standard**, **Consignment (K)**, **Subcontracting (L)**, **Third-party (S)**. The API enforces the same — cats `D` (service) and `9` (limit) return:
```
APPL_MM_PUR_PO/065: Use a supported purchase order item category
```

For services, use cat `0` (Standard) with a SERV-type material — see "Service PO recipe" below. For limit items in lean services, category `A` is system-generated (not user-selectable in Fiori) but DOES work via API.

## 6. Account-assignment deep-insert WORKS — but the nav name is `to_AccountAssignment`
**Critical correction:** earlier memory documented `to_PurchaseOrderAccountAssignment` as the nav. That's wrong — SAP rejects with `Property 'to_PurchaseOrderAccountAssignment' is invalid`.

The correct nav is `to_AccountAssignment`. With the right name, deep-insert works first-try:

```json
"to_PurchaseOrderItem": [
 {
 "PurchaseOrderItem": "10",
 "PurchaseOrderItemCategory": "0",
 "AccountAssignmentCategory": "K",
 "Material": "A001",
 "Plant": "1010",
 "OrderQuantity": "40",
 "PurchaseOrderQuantityUnit": "AU",
 "NetPriceAmount": "120.00",
 "DocumentCurrency": "EUR",
 "PurchaseOrderItemText": "...",
 "to_AccountAssignment": [
 { "AccountAssignmentNumber": "1", "CostCenter": "10101101", "GLAccount": "11001040" }
 ]
 }
]
```

This unlocks service-PO creation and any other AAC-required scenario via the API.

## 7. Multi-item deep-insert works
`to_PurchaseOrderItem: [...]` accepts multiple items in a single POST. Including limit items (cat A) alongside standard items (cat 0) — see service-PO recipe.

## 8. Service PO recipe (Cloud Public Lean Services)

Lean services on Cloud Public does NOT use item category D. Instead:

**Item 10 (the service line):**
- `PurchaseOrderItemCategory: "0"` (Standard)
- `Material`: a SERV-type product (e.g. `A001`, BaseUnit `AU`)
- `PurchaseOrderQuantityUnit: "AU"` (Activity Unit — match material's BaseUnit)
- `AccountAssignmentCategory: "K"` (Cost Center; required for service materials)
- `to_AccountAssignment`: with `CostCenter` + `GLAccount`

**Item 20 (optional — limit item, what Fiori shows in "Limit Items" tab):**
- `PurchaseOrderItemCategory: "A"` (Limit — system-generated category, not in Fiori dropdown)
- `AccountAssignmentCategory: "K"`
- No `Material`, no `OrderQuantity`
- `OverallLimitAmount` + `ExpectedOverallLimitAmount`
- `to_AccountAssignment` (same shape)

Item 20 is OPTIONAL — a minimal service PO works with just item 10. See `service-po-recipe.md` for the full payload.

## 9. Idempotency pattern survives partial failures
Use `migration-log.jsonl` + `loadDoneFromLog()`:
- Append one JSON-line per attempt: `{ok: true|false, sourceKey, targetId, ts, error?}`
- On rerun, skip any source key with a prior `ok=true`
- Survives partial failure (e.g., 5 UoM-related rejects out of 50) and lets the rerun cleanly POST only the missing ones without touching the ones already done

## Reference payload (goods PO, verified)

```json
{
 "PurchaseOrderType": "NB",
 "CompanyCode": "1010",
 "PurchasingOrganization": "1010",
 "PurchasingGroup": "001",
 "Supplier": "10100088",
 "DocumentCurrency": "EUR",
 "PaymentTerms": "0004",
 "PurchaseOrderDate": "/Date(1714694400000)/",
 "to_PurchaseOrderItem": [
 {
 "PurchaseOrderItem": "10",
 "PurchaseOrderItemCategory": "0",
 "Material": "FG011",
 "Plant": "1010",
 "OrderQuantity": "39",
 "PurchaseOrderQuantityUnit": "PC",
 "NetPriceAmount": "61.05",
 "DocumentCurrency": "EUR",
 "PurchaseOrderItemText": "Test demo line"
 }
 ]
}
```
