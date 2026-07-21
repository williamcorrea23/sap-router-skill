# Product entity — field reference

Endpoint: `/sap/opu/odata4/sap/api_product/srvd_a2x/sap/product/0002/Product`

## Required fields for create (per SAP runtime, not all WSDL-required)

| Field | Type / Max | Notes |
|---|---|---|
| `Product` | String / 18 chars | External ID. No API-side auto-numbering — you must supply. Uppercase. |
| `ProductType` | String / 4 chars | `HAWA` (trading goods), `FERT` (finished), `SERV` (service), `ROH` (raw), `HALB` (semi-finished), `MAT`, `HIBE`, `NLAG`, `PIPE`, `VERP` — depends on tenant. |
| `BaseUnit` | String / 3 chars | **Internal SAP code** — discover via GET. Common: `ST` (Stück / piece), `LE` (Leistungseinheit / service unit), `KG`, `L`, `M`. **Not** the ISO codes (`PC`, `EA`) that V2 returns. |
| `ProductGroup` | String / 9 chars | Tenant-specific. Discover via GET. Common demo values: `A001`, `L001`, `L002`, `L004`. |
| `IndustrySector` | String / 1 char | Required even though Fiori's manual create dialog doesn't ask for it. Most demo tenants: `M` (Mechanical Engineering). Other values: `A`, `C`, `P`, etc. |

## Deep-insert children at create time

Only `_ProductDescription` is required at create. Other extension entities (`_ProductPlant`, `_ProductSales`, `_ProductValuation`) can be POSTed in separate calls after the header exists.

### `_ProductDescription` (collection — at least one entry required)

```json
"_ProductDescription": [
  { "Product": "<SAME parent ID>", "Language": "EN", "ProductDescription": "..." }
]
```

**Critical:** child must repeat the parent's `Product` key. Without it: `CMD_PROD_RAP/003 "Property PRODUCT is a key and cannot be initial"`.

| Field | Type | Notes |
|---|---|---|
| `Product` | String / 18 | Must equal parent. |
| `Language` | String / 2 | Language ISO code (`EN`, `DE`, `FR`...). |
| `ProductDescription` | String / 40 | Free text. |

## Optional but commonly populated header fields

| Field | Type / Max | When to populate |
|---|---|---|
| `GrossWeight` | Decimal(13,3) | If shipping logistics matter |
| `NetWeight` | Decimal(13,3) | If shipping logistics matter |
| `WeightUnit` | String / 3 | Required if any weight set |
| `ProductVolume` | Decimal(13,3) | If volumetric pricing |
| `VolumeUnit` | String / 3 | Required if volume set |
| `Division` | String / 2 | Sales org division |
| `IsBatchManagementRequired` | Boolean | Pharma / food / chemicals |
| `IsPilferable` | Boolean | High-value items |
| `ItemCategoryGroup` | String / 4 | Sales item category trigger |

## Read-only system fields (do NOT include in POST)

`CreationDate`, `CreationTime`, `CreationDateTime`, `CreatedByUser`, `LastChangeDate`, `LastChangedByUser`, `LastChangeDateTime`, `LastChangeTime`, `BaseISOUnit` (auto-derived from `BaseUnit`), `WeightISOUnit`, `VolumeISOUnit`, `QuarantinePeriodISOUnit`, `ProductMeasurementISOUnit`, `MaxPackggDimensionISOUnit`.

## Navigation properties (for `$expand` reads or post-create POSTs)

| Nav property | Target entity | Cardinality | Purpose |
|---|---|---|---|
| `_ProductDescription` | `ProductDescription` | many | Multi-language descriptions |
| `_ProductBasicText` | `ProductBasicTexts` | many | Long text on Basic Data tab |
| `_ProductInternalComment` | `ProductInternalNoteTexts` | many | Internal notes |
| `_ProductPurchaseOrderText` | `ProductPurchaseOrderText` | many | PO text printed on POs |
| `_ProductInspectionText` | `ProductInspectionTexts` | many | QM inspection text |
| `_ProductPlant` | `ProductPlant` | many | Plant-level extension (one row per plant) |
| `_ProductSales` | `ProductSales` | one | Sales org extension |
| `_ProductSalesDelivery` | `ProductSalesDelivery` | many | Sales/delivery tab data |
| `_ProductStorage` | `ProductStorage` | one | Storage tab |
| `_ProductProcurement` | `ProductProcurement` | one | Procurement tab |
| `_ProductValuation` | `ProductValuation` | many | Valuation area pricing |
| `_ProductQualityManagement` | `ProductQualityManagement` | one | QM extension |
| `_ProductEWMWarehouse` | `ProductEWMWarehouse` | many | EWM warehouse extension |
| `_ProductUnitOfMeasure` | `ProductUnitOfMeasure` | many | Alternative units of measure |
| `_ProductChangeMaster` | `ProductChangeMaster` | many | ECM change number link |

## Reads — useful query patterns

```http
# All products by type
GET /Product?$filter=ProductType eq 'HAWA'&$top=50&$select=Product,BaseUnit,ProductGroup

# Specific product with descriptions
GET /Product('11')?$expand=_ProductDescription

# Recent creates
GET /Product?$top=10&$orderby=CreationDateTime desc&$select=Product,ProductType,CreationDateTime,CreatedByUser

# Discover tenant unit/group/sector pools (use for Phase 2)
GET /Product?$top=20&$select=ProductType,BaseUnit,ProductGroup,IndustrySector
```
