# PIR known quirks — `API_INFORECORD_PROCESS_SRV`

Lessons collected from real PIR creation runs against SAP S/4HANA Cloud Public Edition.

## Header vs org-plant field placement

The single biggest source of confusion. Many fields LOOK like they belong on the header but actually live on the **`to_PurgInfoRecdOrgPlantData`** child entity. Putting them on the header gets rejected.

| Field | Where it lives | Common mistake |
|---|---|---|
| `Supplier`, `Material`, `BaseUnit`, `PurgDocOrderQuantityUnit` | **Header** | These ARE on header — easy ones |
| `PurchasingOrganization` | **Org-plant child** | Easy to assume header |
| `PurchasingInfoRecordCategory` | **Org-plant child** | Header gets `Property 'PurchasingInfoRecordCategory' is invalid` |
| `PurchasingInfoRecordType` | **Org-plant child** | Same — must be on org-plant |
| `Plant`, `PurchasingGroup`, `Currency` | **Org-plant child** | |
| `NetPriceAmount`, `MinimumPurchaseOrderQuantity`, `StandardPurchaseOrderQuantity` | **Org-plant child** | |

The general rule: anything that varies by (PurchOrg, Plant) combination lives on the child. Anything that's intrinsic to the (Supplier, Material) pair lives on the header.

## ProcurementType filter — F only

PIRs only work for materials with `ProcurementType=F` (external procurement). Materials with `ProcurementType=E` (in-house produced) fail with `ME/092`.

When picking eligible materials for bulk PIR creation:

```
GET /sap/opu/odata/sap/API_PRODUCT_SRV/A_ProductPlant?$filter=Plant eq '<plant>' and ProcurementType eq 'F'
```

FERT (finished product) and SEMI (semi-finished) materials are often `E` (in-house). HAWA (trading) and ROH (raw) are typically `F`. Check before bulk.

## Supplier-PurchOrg assignment is a prerequisite

The supplier must have an `A_SupplierPurchasingOrg` row for the target PurchOrg, or PIR creation fails with `06/321: Supplier does not exist in purchasing organization`.

To check beforehand:

```
GET /sap/opu/odata/sap/API_BUSINESS_PARTNER/A_SupplierPurchasingOrg?$filter=Supplier eq '<sup>' and PurchasingOrganization eq '<org>'
```

If the supplier exists without that row, extend the supplier first by PATCHing or via the `s4hana-create-business-partner` skill's update flow.

## Field naming pitfalls — `Currency` vs `PurchaseOrderCurrency`

| Entity | Currency field name |
|---|---|
| `A_PurgInfoRecdOrgPlantData` (PIR org-plant) | **`Currency`** |
| `A_SupplierPurchasingOrg` (supplier purch org) | **`PurchaseOrderCurrency`** |

These sibling entities use confusingly different field names for the same concept. Easy to copy-paste from the supplier skill and end up with `PurchaseOrderCurrency` on a PIR (rejected as `Property invalid`). Use the right name per entity.

## `StandardPurchaseOrderQuantity` is required

SAP API Hub docs sometimes list it as optional. In practice, omitting it returns `ME/083: Enter Standard Order Quantity`. Always include it — typical default is `10`.

## PIR creation auto-generates pricing condition records

After a PIR is created, SAP automatically generates pricing condition records in the related condition tables. This is a useful side-effect for demos:

- `search_pricing_conditions` MCP tools start returning data
- `get_pricing_condition` works against the auto-generated records
- `get_product_pricing` returns the PIR-driven prices

So you typically don't need a separate "create pricing condition" skill — bulk PIR creation populates pricing data as a side-effect.

## `NetPriceAmount` on org-plant is display-only for UPDATES

⚠️ For CREATE: `NetPriceAmount` on `to_PurgInfoRecdOrgPlantData` works (the price is recorded).

⚠️ For UPDATE: PATCHing `NetPriceAmount` on `A_PurgInfoRecdOrgPlantData` returns 204 (success) but the value doesn't actually change. The editable price for updates lives in the `to_PurInfoRecdPrcgCndnValidity` nav (Pricing Condition Validity records).

See `s4hana-update-record/references/known-traps.md` for the "silent failure" pattern.

## PIR categories — only `0` is verified

`PurchasingInfoRecordCategory` values on this tenant family:
- ✅ `"0"` = Standard (external procurement) — fully tested
- ⚠️ `"1"` = Subcontracting — untested
- ⚠️ `"2"` = Consignment — untested
- ⚠️ `"3"` = Pipeline — untested

For cat 1/2/3, treat as research-mode — probe via `s4hana-create-record` generic skill first.

## Multi-org-plant PIRs

A single PIR can have rows for multiple (PurchOrg, Plant) combos — pass multiple objects in the `to_PurgInfoRecdOrgPlantData` array:

```json
"to_PurgInfoRecdOrgPlantData": [
  { "PurchasingOrganization": "1010", "Plant": "1010", ... },
  { "PurchasingOrganization": "1010", "Plant": "1110", ... },
  { "PurchasingOrganization": "1010", "Plant": "1710", ... }
]
```

Rarer than single-org/single-plant in practice but supported.
