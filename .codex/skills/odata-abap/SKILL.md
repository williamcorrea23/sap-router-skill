---
name: odata-abap
description: OData service development in ABAP — SADL-based OData, CDS-exposed OData, @OData.publish annotation, SEGW vs CDS approach, OData V4 in SAP Gateway, $metadata, entity sets, function imports, $expand/$filter/$top/$skip, batch operations, deep insert, ETag, service registration (/IWFND/MAINT_SERVICE). Use when creating OData services, exposing CDS views as OData, or troubleshooting OData errors in SAP Gateway.
---

# OData Service Development in ABAP

Creating OData V2/V4 services from ABAP — CDS-exposed, SADL-based, and manual approaches.

## CDS-Exposed OData (Recommended)

```cds
@OData.publish: true
define view entity Z_C_PRODUCT_API
  as select from zproduct
{
  key product_guid as ProductGuid,
      material     as Material,
      material_type as MaterialType,
      description  as Description,
      created_at   as CreatedAt,

      @Consumption.filter: { mandatory: false }
      plant as Plant
}
```

### Service Registration
```
1. Activate CDS view → OData service auto-registered
2. /IWFND/MAINT_SERVICE → service name: Z_C_PRODUCT_API_CDS
3. Add to /IWFND/MAINT_SERVICE → SAP Gateway Client → Test
```

## SADL-Based OData (Service Definition)

```abap
" Service Definition (SRVD)
DEFINE SERVICE z_product_srv {
  EXPOSE z_c_product_api AS Product;
  EXPOSE z_c_product_text AS ProductText;
}

" Service Binding (SRVB)
" ADT → New → Service Binding
"   Binding Type: OData V4 (UI)
"   Service Definition: Z_PRODUCT_SRV
" → generates OData V4 endpoint
```

## Manual OData via SEGW (Legacy)

```abap
" SEGW project → Data Model → Entity Types
" Entity: Product
"   Properties: ProductGuid (Edm.Guid, Key), Material (Edm.String)
"
" Runtime: DPC_EXT class
METHOD products_get_entity.
  DATA(lv_guid) = io_tech_request_context->get_converted_source_keys(
    )->get_value( 'PRODUCTGUID' ).
  SELECT SINGLE * FROM zproduct
    WHERE product_guid = @lv_guid
    INTO CORRESPONDING FIELDS OF @er_entity.
ENDMETHOD.
```

## OData Query Options

| Option | Syntax | Example |
|---|---|---|
| $filter | `Property eq value` | `Material eq 'MAT001'` |
| $expand | `NavigationProperty` | `$expand=ProductText` |
| $orderby | `Property asc/desc` | `$orderby=CreatedAt desc` |
| $top / $skip | `$top=N&$skip=M` | `$top=10&$skip=20` |
| $select | `Property1,Property2` | `$select=Material,Description` |
| $count | `$count=true` | Returns total count with results |

## Deep Insert (Parent + Children)

```json
// POST /sap/opu/odata/sap/Z_PRODUCT_SRV/Product
{
  "Material": "MAT001",
  "Description": "Test Product",
  "to_ProductText": [{
    "Language": "EN",
    "Description": "English text"
  }, {
    "Language": "DE",
    "Description": "German text"
  }]
}
```

## ETag (Optimistic Locking)

```abap
" CDS annotation for ETag
@Semantics.systemDate.lastChangedAt: true
created_at as LastChangedAt

" Client sends If-Match header with ETag value
" Server returns 412 if record changed by another user
```

## Batch Operations

```http
POST /sap/opu/odata/sap/Z_PRODUCT_SRV/$batch
Content-Type: multipart/mixed; boundary=batch_boundary

--batch_boundary
Content-Type: application/http
Content-Transfer-Encoding: binary

GET Product('ABC123') HTTP/1.1

--batch_boundary
Content-Type: application/http
Content-Transfer-Encoding: binary

POST Product HTTP/1.1
Content-Type: application/json

{"Material":"MAT002","Description":"Batch created"}

--batch_boundary--
```

## Service Registration

```
Transaction /IWFND/MAINT_SERVICE:
  1. Add Service
  2. System Alias: LOCAL
  3. Technical Service Name: Z_PRODUCT_SRV
  4. Service Version: 0001
  5. Add → OK → Back → Load Metadata
```

## Gotchas

- **CDS OData auto-exposure** uses @OData.publish: true — simplest approach
- **$filter on Edm.Guid**: use `ProductGuid eq guid'...'` not `ProductGuid eq '...'`
- **SEGW is legacy** — prefer CDS-exposed or Service Definition approaches
- **OData V2 vs V4**: V4 is the future but V2 still more widely supported
