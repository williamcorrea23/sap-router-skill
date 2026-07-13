---
name: sap-api-style
description: SAP API documentation standards — OData API documentation guidelines, REST API style guide, OpenAPI/Swagger specs for SAP services, API naming conventions, SAP API Business Hub documentation requirements. Use when documenting SAP APIs, creating OpenAPI specs for SAP services, or reviewing API documentation against SAP standards.
trigger:
  keywords: [api, odata, rest, openapi, swagger, documentation, style, naming, business-hub, specs]
  intent: >-
    Document SAP APIs following OData and REST style guide standards, including OpenAPI/Swagger specs and API Business Hub requirements.
---

# SAP API Style Guide

API documentation standards following SAP guidelines.

## OData API Naming

| Entity | Convention | Example |
|---|---|---|
| Entity Set | Plural Noun | Products, SalesOrders |
| Entity Type | Singular Noun | Product, SalesOrder |
| Property | PascalCase | MaterialNumber, CreatedAt |
| Navigation Property | Prefix "to_" | to_ProductText, to_Supplier |
| Function Import | Verb-Noun | GetTopCustomers, ValidateOrder |

## OpenAPI Document Structure

```yaml
openapi: 3.0.3
info:
  title: Product Management API
  version: "1.0.0"
  description: |
    Manages product master data in SAP S/4HANA.
    Scope: MM module, product lifecycle from creation to archival.
servers:
  - url: https://my-s4hana.sap.com/sap/opu/odata/sap/Z_PRODUCT_API
paths:
  /Products:
    get:
      summary: List products
      parameters:
        - name: $filter
          in: query
          description: OData filter (e.g. MaterialType eq 'FERT')
          schema: { type: string }
      responses:
        '200':
          description: Product list
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ProductsList'
    post:
      summary: Create product
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ProductCreate'
```

## Documentation Checklist

1. API title and version
2. Authentication method (Basic Auth, OAuth2, API Key)
3. Rate limits
4. Error response format (use BAPIRET2 structure)
5. All HTTP methods documented (GET, POST, PUT, PATCH, DELETE)
6. Query parameters: $filter, $expand, $top, $skip, $orderby, $select
7. Example request and response for each endpoint
8. CSRF token requirement (for write operations against SAP Gateway)

## SAP API Business Hub

Publish APIs to: https://api.sap.com
Requirements: OpenAPI 3.0 spec + SAP API Business Hub account.

## Gotchas
- OData $filter syntax differs from REST query parameters
- SAP Gateway requires X-CSRF-Token header for POST/PUT/PATCH/DELETE
- Error responses use sap-message format, not RFC 7807 Problem Details
