# PIR envelope template — A_PurchasingInfoRecord deep-insert

**Verified against SAP S/4HANA Cloud Public Edition — 120 PIRs created via this pattern.**

## Endpoint
```
POST https://<host>/sap/opu/odata/sap/API_INFORECORD_PROCESS_SRV/A_PurchasingInfoRecord?sap-client=<n>
Authorization: Basic <base64(user:pass)>
X-CSRF-Token: <captured>
Cookie: <captured>
Content-Type: application/json
Accept: application/json
```

## Minimal working envelope

```json
{
 "Supplier": "{{supplier id}}",
 "Material": "{{material code with ProcurementType=F}}",
 "BaseUnit": "{{material's BaseUnit, e.g. PC}}",
 "PurgDocOrderQuantityUnit": "{{same as BaseUnit usually}}",
 "to_PurgInfoRecdOrgPlantData": [
 {
 "PurchasingOrganization": "{{e.g. 1010}}",
 "Plant": "{{e.g. 1010}}",
 "PurchasingInfoRecordCategory": "0",
 "PurchasingGroup": "{{e.g. 001}}",
 "Currency": "{{e.g. EUR}}",
 "NetPriceAmount": "{{price}}",
 "MinimumPurchaseOrderQuantity": "{{e.g. 1}}",
 "StandardPurchaseOrderQuantity": "{{e.g. 10 — REQUIRED}}",
 "MaterialPlannedDeliveryDurn": "{{days, e.g. 7}}"
 }
 ]
}
```

## Header field reference

| Field | Required | Where | Notes |
|---|---|---|---|
| `PurchasingInfoRecord` | auto | header | System-assigned in `5300000xxx` range |
| `Supplier` | yes | header | Must have an `A_SupplierPurchasingOrg` row for the target PurchOrg |
| `Material` | yes | header | Must have `ProcurementType=F` at the target plant |
| `BaseUnit` | yes | header | The material's base unit of measure |
| `PurgDocOrderQuantityUnit` | yes | header | Usually equals BaseUnit |
| `PurchasingOrganization` | NO | header | **Lives on org-plant child entity, NOT here** |
| `PurchasingInfoRecordCategory` | NO | header | **Lives on org-plant child entity, NOT here** |
| `PurchasingInfoRecordType` | NO | header | **Lives on org-plant child entity, NOT here** |

## Org-plant entity (`to_PurgInfoRecdOrgPlantData`) field reference

| Field | Required | Notes |
|---|---|---|
| `PurchasingOrganization` | yes | Target PurchOrg |
| `Plant` | yes | Target Plant |
| `PurchasingInfoRecordCategory` | yes | `0` = standard external. Others untested. |
| `PurchasingGroup` | yes | Target PurchGroup |
| `Currency` | yes | **NOT `PurchaseOrderCurrency` — that's a different entity's field** |
| `NetPriceAmount` | yes | Per-unit price |
| `MinimumPurchaseOrderQuantity` | recommended | Minimum order qty (defaults to 1) |
| `StandardPurchaseOrderQuantity` | **yes** | Standard order qty — `ME/083` fires if missing |
| `MaterialPlannedDeliveryDurn` | recommended | Planned delivery time in days |
| `PriceValidityStartDate` | optional | `/Date(ms)/` format. Defaults to today |
| `PriceValidityEndDate` | optional | Defaults to `9999-12-31` |
| `TaxCode` | optional | If supplier-specific tax applies |
| `IsRegularSupplier` | optional | `true` marks this supplier as regular for the material |
| `OverdelivTolrtdLmtRatioInPct` | optional | Tolerance % |
| `UnderdelivTolrtdLmtRatioInPct` | optional | Tolerance % |
| `MaximumPurchaseOrderQuantity` | optional | Cap on order qty |

## Multi-org-plant PIRs

A single PIR can have rows for multiple `(PurchOrg, Plant)` combos — pass multiple objects in `to_PurgInfoRecdOrgPlantData`:

```json
"to_PurgInfoRecdOrgPlantData": [
 { "PurchasingOrganization": "1010", "Plant": "1010", ... },
 { "PurchasingOrganization": "1010", "Plant": "1110", ... },
 { "PurchasingOrganization": "1010", "Plant": "1710", ... }
]
```

This is rarer than single-org/single-plant in practice.

## Response

Success:
```json
{
 "d": {
 "PurchasingInfoRecord": "5300000130",
 "PurchasingInfoRecordUUID": "...",
 "Supplier": "10100088",
 "Material": "HB01",
 "BaseUnit": "PC",
 "to_PurgInfoRecdOrgPlantData": { "results": [...] }
 }
}
```

## Side-effects

PIR creation triggers SAP to auto-generate **pricing condition records** in the condition tables. After bulk PIR creation, the following MCP tools start returning rows:
- `search_pricing_conditions`
- `get_pricing_condition`
- `get_product_pricing`

This is useful for demos that need pricing data — bulk PIR creation populates pricing as a side-effect.
