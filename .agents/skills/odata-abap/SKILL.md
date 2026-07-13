---
name: odata-abap
description: >-
  OData service development in ABAP — CDS-exposed OData, SADL service
  definitions, RAP service bindings, SEGW legacy, OData V2/V4, query
  options, deep insert, ETag, batch, service registration. Use when
  creating OData services, exposing CDS views, or troubleshooting
  SAP Gateway errors.
trigger: odata abap, @OData.publish, service binding, service definition, /IWFND/MAINT_SERVICE, SEGW, SADL, OData V4 ABAP, RAP unmanaged, DPC_EXT, $metadata, deep insert, ETag
---

# OData Service Development in ABAP

Three approaches: CDS-exposed (simplest), Service Definition + Binding (RAP, recommended), SEGW (legacy).

## Prerequisites

- SAP system with SAP Gateway (SAP_GWFND) or S/4HANA
- ABAP Development Tools (ADT) in Eclipse
- Development package and transport request
- Authorization for `/IWFND/MAINT_SERVICE`

## 1. CDS-Exposed OData (Simplest)

```cds
@OData.publish: true
@EndUserText.label: 'Product API'
define view entity Z_C_PRODUCT_API
  as select from zproduct
{
  key product_guid  as ProductGuid,
      material      as Material,
      material_type as MaterialType,
      description   as Description,
      created_at    as CreatedAt,

      @Consumption.filter: { mandatory: false }
      plant          as Plant
}
```

1. Activate the CDS view in ADT
2. OData service auto-registers as `Z_C_PRODUCT_API_CDS`
3. Register in Gateway: `/IWFND/MAINT_SERVICE` → Add Service
4. Test via SAP Gateway Client (`/IWFND/GW_CLIENT`)

## 2. Service Definition + Binding (RAP — Recommended)

**Service Definition (SRVD):**
```abap
@EndUserText.label: 'Product Service'
define service Z_PRODUCT_SRV {
  expose Z_C_PRODUCT_API      as Product;
  expose Z_C_PRODUCT_TEXT_API as ProductText;
}
```

**Service Binding (SRVB) in ADT:**
1. Right-click service definition → New → Service Binding
2. Binding type: **OData V4 (UI)**
3. Select service definition: `Z_PRODUCT_SRV`
4. Activate → click **Preview** to test

## 3. SEGW Manual OData (Legacy)

```
SEGW → Create Project → Data Model
  Entity: Product
    Properties: ProductGuid (Edm.Guid, Key), Material (Edm.String)
  Generate runtime artifacts → DPC_EXT class
```

**DPC_EXT implementation:**
```abap
METHOD products_get_entity.
  DATA(lv_guid) = io_tech_request_context->get_converted_keys(
    )->get_value( 'PRODUCTGUID' ).
  SELECT SINGLE * FROM zproduct
    WHERE product_guid = @lv_guid
    INTO CORRESPONDING FIELDS OF @er_entity.
ENDMETHOD.
```

## 4. Query Options

- **$filter**: `Material eq 'MAT001'`
- **$expand**: `$expand=ProductText`
- **$orderby**: `$orderby=CreatedAt desc`
- **$top/$skip**: `$top=10&$skip=20`
- **$select**: `$select=Material,Description`
- **$count**: `$count=true` (V2) / `$count` path segment (V4)

## 5. Deep Insert (Parent + Children)

```http
POST /sap/opu/odata/sap/Z_PRODUCT_SRV/Product
Content-Type: application/json

{
  "Material": "MAT001",
  "Description": "Test Product",
  "to_ProductText": [
    { "Language": "EN", "Description": "English text" },
    { "Language": "DE", "Description": "German text" }
  ]
}
```

## 6. ETag (Optimistic Locking)

```cds
@Semantics.systemDate.lastChangedAt: true
created_at as LastChangedAt
```
Client sends `If-Match: <etag>` header. Server returns `412 Precondition Failed` if record changed.

## 7. Batch Operations

```http
POST /sap/opu/odata/sap/Z_PRODUCT_SRV/$batch
Content-Type: multipart/mixed; boundary=batch_boundary

--batch_boundary
Content-Type: application/http

GET Product('ABC123') HTTP/1.1

--batch_boundary
Content-Type: application/http

POST Product HTTP/1.1
Content-Type: application/json

{"Material":"MAT002","Description":"Batch created"}

--batch_boundary--
```

## 8. Service Registration (/IWFND/MAINT_SERVICE)

1. Transaction `/IWFND/MAINT_SERVICE`
2. Add Service → System Alias: `LOCAL`
3. Technical Service Name: `Z_PRODUCT_SRV` (or `Z_C_PRODUCT_API_CDS`)
4. Service Version: `0001`
5. Add → OK → Back → Load Metadata

## Pitfalls

- **$filter on Edm.Guid fails** — *Cause:* GUIDs need special syntax. *Solution:* use `ProductGuid eq guid'xxxx-xxxx-...'` (V2) or `ProductGuid eq xxxxxxxx-xxxx-...` without quotes (V4).

- **Service not visible after activation** — *Cause:* CDS view activated but Gateway cache stale. *Solution:* run `/IWFND/CACHE_CLEANUP` or `/IWFND/MED_CLEANUP` to clear metadata cache.

- **$expand returns empty** — *Cause:* navigation property not defined or association cardinality mismatch. *Solution:* verify association in CDS view and that the target entity is also exposed in the same service.

- **SEGW generates code but 500 error** — *Cause:* DPC_EXT method not redefined or `super->` call missing. *Solution:* redefine method in Z-class, not base class; call `super->` for unhandled entities.

- **OData V2 vs V4 mismatch** — *Cause:* V4 uses different query syntax (`$count` path vs `$count=true`). *Solution:* check service binding type; V4 doesn't support `$inlinecount`.

- **Draft-enabled entity not editable** — *Cause:* draft actions not exposed or `@ObjectModel.draftEnabled: true` missing. *Solution:* add `@ObjectModel.draftEnabled: true` to CDS view and activate.

## Verification

```bash
# 1. Check $metadata loads
curl -u <user>:<pass> \
  "https://<host>/sap/opu/odata/sap/Z_PRODUCT_SRV/\$metadata"

# 2. Query entity set
curl -u <user>:<pass> \
  "https://<host>/sap/opu/odata/sap/Z_PRODUCT_SRV/Product?\$top=5"

# 3. Verify in SAP Gateway Client (/IWFND/GW_CLIENT)
#    GET /sap/opu/odata/sap/Z_PRODUCT_SRV/$metadata  → expect 200

# 4. Check service is registered
#    /IWFND/MAINT_SERVICE → search Z_PRODUCT_SRV → Status: green

# 5. Test deep insert
curl -X POST -H "Content-Type: application/json" \
  -d '{"Material":"TEST","to_ProductText":[]}' \
  "https://<host>/sap/opu/odata/sap/Z_PRODUCT_SRV/Product"
```
