# Cancel-vs-Update decision guide

Some S/4HANA entities reject PATCH entirely (`405 CX_SADL_ENTITY_CUD_DISABLED`). For those, the proper workflow is **cancel-and-recreate** instead of update. This doc explains when to do which.

## Entities that need cancel-recreate

### Supplier Invoice (`A_SupplierInvoice`)

PATCH returns:
```
HTTP 405
CX_SADL_ENTITY_CUD_DISABLED: Updating operations are disabled for entity 'API_SUPPLIERINVOICE_PROCESS~A_SUPPLIERINVOICE'
```

**Why**: Posted invoices are immutable for audit/compliance.

**To "change" an invoice**:
1. Cancel via the `Cancel_SupplierInvoice` OData action:
   ```
   POST /sap/opu/odata/sap/API_SUPPLIERINVOICE_PROCESS_SRV/A_SupplierInvoice/Cancel_SupplierInvoice
   {"SupplierInvoice": "<id>", "FiscalYear": "<yr>", "ReversalReason": "01", "PostingDate": "/Date(<ms>)/"}
   ```
2. Create a fresh invoice with corrected data via the `s4hana-create-invoice` skill.

Cancellation creates a reversing FI document, preserving the audit trail.

### Material Document / Goods Receipt (`A_MaterialDocumentHeader`)

PATCH returns same `CX_SADL_ENTITY_CUD_DISABLED`.

**Why**: Material movements affect inventory; mutations would corrupt stock levels.

**To "change" a GR**:
1. Reverse via movement type **102** (Reversal of GR for PO):
   ```
   POST /sap/opu/odata/sap/API_MATERIAL_DOCUMENT_SRV/A_MaterialDocumentHeader
   { ...header,
     "to_MaterialDocumentItem": [{
       "GoodsMovementType": "102",
       "GoodsMovementRefDocType": "W",            // W = Material Document (not B = PO)
       "PurchaseOrder": "<po>", "PurchaseOrderItem": "<item>",
       "Material": "<mat>", "Plant": "<plant>",
       "QuantityInEntryUnit": "<qty>",
       "EntryUnit": "<unit>",
       ...identify original via reference
     }]}
   ```
2. If a corrected receipt is needed, create a fresh GR with movement type 101.

The reversal creates a NEGATIVE-quantity material document, preserving inventory history.

### Product Master (`A_Product`)

PATCH header rejected: `API_PRD_MSG/009: Create operation not allowed on entity` (and similarly for update). Cloud Public locks Product master under MDG.

**To "change" a product**:
- **Description**: `A_ProductDescription` PATCH works ✅ (use this skill normally)
- **Plant data**: `A_ProductPlant` PATCH for some fields
- **Master data fields** (Type, BaseUnit, ProductGroup, etc.): need MDG / Fiori "Manage Product Master" app — no API path

## How to choose

| User says... | Do this |
|---|---|
| "Update PO 4500..." | PATCH `A_PurchaseOrder` |
| "Change BP name" | PATCH `A_BusinessPartner` |
| "Backdate this invoice" | ❌ Can't — invoices are immutable. Tell user: cancel + create new |
| "Reverse this GR" | Use the reversal pattern above (movement type 102) |
| "Fix the wrong product description" | PATCH `A_ProductDescription` |
| "Change the material on PO line" | ❌ Can't — Material is write-once on `A_PurchaseOrderItem`. Tell user: delete the PO line and create a new one (or new PO) |

## Edge case — partial updates that need recreation

Sometimes a field change cascades to dependent records that can't be updated:

- **Change PO line `OrderQuantity` after GR posted** → may need to first reverse the GR
- **Change PIR `Material`** → write-once, must create new PIR
- **Change BP `BusinessPartnerCategory`** → write-once, must create new BP

When this happens, the skill should detect the write-once error and explain to the user that the field is locked, and what the workaround is.
