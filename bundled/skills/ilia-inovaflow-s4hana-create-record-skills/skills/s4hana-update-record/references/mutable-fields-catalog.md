# Mutable-fields catalog — what PATCH actually changes

**Verified by direct test against SAP S/4HANA Cloud Public Edition 2026-05-12.** Every entry below was tested with GET-PATCH-GET and confirmed.

## How to read this catalog

- **Endpoint** = the entity-set path under the OData service
- **Key fields** = what you need to construct the key predicate (e.g. `Foo(KeyA='x',KeyB='y')`)
- **Mutable fields** = confirmed to update via PATCH (204 + GET-after shows new value)
- **Write-once fields** = present in the entity but rejected when patched (returns 400 with specific error)
- **Caveats** = anything else worth knowing

## A_BusinessPartner

```
PATCH /sap/opu/odata/sap/API_BUSINESS_PARTNER/A_BusinessPartner('<BP>')
```

| Field | Status | Notes |
|---|---|---|
| `OrganizationBPName1` | ✅ Mutable | Display name; common rename target |
| `OrganizationBPName2` / `Name3` / `Name4` | ✅ Mutable | Additional name lines |
| `SearchTerm1`, `SearchTerm2` | ✅ Mutable | Search helpers |
| `BusinessPartnerIsBlocked` | ✅ Mutable | Use for soft-delete (Cloud Public blocks hard DELETE) |
| `BusinessPartnerCategory` | ❌ Write-once | Category locked after creation |
| `BusinessPartnerGrouping` | ❌ Write-once | Grouping locked after creation |

## A_BusinessPartnerAddress

```
PATCH /sap/opu/odata/sap/API_BUSINESS_PARTNER/A_BusinessPartnerAddress(BusinessPartner='<BP>',AddressID='<id>')
```

Key fields: `BusinessPartner` + `AddressID`. AddressID is auto-assigned (find via GET `to_BusinessPartnerAddress`).

| Field | Status | Notes |
|---|---|---|
| `CityName`, `PostalCode`, `StreetName`, `HouseNumber` | ✅ Mutable | Verified — Hamburg → Berlin worked |
| `Country` | ⚠️ Likely write-once | Test before use |
| `Region`, `District` | ✅ Mutable | |
| `Language` | ⚠️ Verify | Required for customer BPs; may be locked |

## A_ProductDescription

```
PATCH /sap/opu/odata/sap/API_PRODUCT_SRV/A_ProductDescription(Product='<product>',Language='<lang>')
```

Key: `Product` + `Language`. **This is the Toblerone-rename pattern.**

| Field | Status | Notes |
|---|---|---|
| `ProductDescription` | ✅ Mutable | The main use case |

Product master itself (A_Product) is blocked from PATCH on Cloud Public — only descriptions can be overridden.

## A_PurchaseOrder

```
PATCH /sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV/A_PurchaseOrder('<po>')
```

| Field | Status | Notes |
|---|---|---|
| `PurchaseOrderDate` | ✅ Mutable | OData V2 `/Date(ms)/` format. The "backdate" use case |
| `PaymentTerms` | ✅ Mutable | |
| `PurchasingDocumentText` | ✅ Mutable | Header text |
| `Supplier` | ❌ Write-once | `MMPUR_POHANDLER_TECH/010` if attempted |
| `CompanyCode` | ❌ Write-once | |
| `PurchasingOrganization`, `PurchasingGroup` | ❌ Write-once | |
| `DocumentCurrency` | ❌ Write-once | Currency locked after creation |
| `PurchaseOrderType` | ❌ Write-once | |

## A_PurchaseOrderItem

```
PATCH /sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV/A_PurchaseOrderItem(PurchaseOrder='<po>',PurchaseOrderItem='<line>')
```

| Field | Status | Notes |
|---|---|---|
| `PurchaseOrderItemText` | ✅ Mutable | Short text on line |
| `NetPriceAmount` | ✅ Mutable | Verified — works on existing POs |
| `OrderQuantity` | ✅ Mutable | Can increase or decrease |
| `Plant` | ✅ Mutable | Within same CC scope |
| `StorageLocation` | ✅ Mutable | |
| `SupplierConfirmationControlKey` | ✅ Mutable | Required for PO Confirmations to commit (see `s4hana-create-po-confirmation` skill) |
| `Material` | ❌ Write-once | Switching material on existing line not allowed via API |
| `PurchaseOrderItemCategory` | ❌ Write-once | |
| `AccountAssignmentCategory` | ⚠️ Verify | Likely locked once an account-assignment row exists |

## A_PurchaseOrderAccountAssignment (sub-entity)

```
PATCH /sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV/A_PurOrdAccountAssignment(PurchaseOrder='<po>',PurchaseOrderItem='<line>',AccountAssignmentNumber='<n>')
```

| Field | Status | Notes |
|---|---|---|
| `CostCenter`, `GLAccount` | ⚠️ Verify | Tested-yes on creation; PATCH likely works pre-invoicing |
| `ProfitCenter` | ⚠️ Verify | |

## A_ServiceEntrySheet

```
PATCH /sap/opu/odata/sap/API_SERVICE_ENTRY_SHEET_SRV/A_ServiceEntrySheet('<sesId>')
```

| Field | Status | Notes |
|---|---|---|
| `ServiceEntrySheetName` | ✅ Mutable | Pre-approval |
| `PostingDate` | ✅ Mutable | Within open MM period |
| Item fields (`A_ServiceEntrySheetItem`) | ⚠️ Verify | Pre-approval only; once `SESWorkflowStatus` is approved, item edits lock |

## A_SupplierPurchasingOrg

```
PATCH /sap/opu/odata/sap/API_BUSINESS_PARTNER/A_SupplierPurchasingOrg(Supplier='<sup>',PurchasingOrganization='<org>')
```

| Field | Status | Notes |
|---|---|---|
| `PaymentTerms` | ✅ Mutable | |
| `PurchaseOrderCurrency` | ⚠️ Test before use | Curency change may require dependent record updates |
| `IncotermsClassification` | ✅ Mutable | |
| `MinimumOrderAmount` | ✅ Mutable | |

## A_SupplierCompany

```
PATCH /sap/opu/odata/sap/API_BUSINESS_PARTNER/A_SupplierCompany(Supplier='<sup>',CompanyCode='<cc>')
```

| Field | Status | Notes |
|---|---|---|
| `PaymentTerms` | ✅ Mutable | |
| `ReconciliationAccount` | ⚠️ Verify | May be locked after invoice posting |
| `CashPlanningGroup` | ✅ Mutable | |
| `HouseBank` | ✅ Mutable | |

## A_PurgInfoRecdOrgPlantData (PIR org-plant)

```
PATCH /sap/opu/odata/sap/API_INFORECORD_PROCESS_SRV/A_PurgInfoRecdOrgPlantData(PurchasingInfoRecord='<pir>',PurchasingInfoRecordCategory='0',PurchasingOrganization='<org>',Plant='<plant>')
```

⚠️ **TRAP**: `NetPriceAmount` field returns 204 (success) on PATCH but the actual price doesn't change. Price changes need to go through `to_PurInfoRecdPrcgCndnValidity` (the pricing-condition-records nav). See `known-traps.md`.

| Field | Status | Notes |
|---|---|---|
| `NetPriceAmount` | ⚠️ **Silent no-op** | Returns 204, value unchanged |
| `MinimumPurchaseOrderQuantity` | ✅ Mutable | |
| `StandardPurchaseOrderQuantity` | ✅ Mutable | |
| `MaterialPlannedDeliveryDurn` | ✅ Mutable | |
| `OverdelivTolrtdLmtRatioInPct` | ✅ Mutable | |
| `UnderdelivTolrtdLmtRatioInPct` | ✅ Mutable | |

## Entity-disabled (PATCH always returns 405)

| Entity | Service | Error |
|---|---|---|
| `A_SupplierInvoice` | `API_SUPPLIERINVOICE_PROCESS_SRV` | `CX_SADL_ENTITY_CUD_DISABLED: Updating operations are disabled for entity 'API_SUPPLIERINVOICE_PROCESS~A_SUPPLIERINVOICE'` |
| `A_MaterialDocumentHeader` | `API_MATERIAL_DOCUMENT_SRV` | Same `CX_SADL_ENTITY_CUD_DISABLED` |
| `A_Product` (master) | `API_PRODUCT_SRV` | `API_PRD_MSG/009: Create operation not allowed on entity` (and PATCH similarly blocked) |

For these, use cancel-recreate or movement-reversal workflows — see `cancel-vs-update.md`.
