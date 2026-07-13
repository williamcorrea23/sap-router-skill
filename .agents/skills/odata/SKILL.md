---
name: odata
description: SAP OData service development — OData V2 and V4 protocol patterns, $metadata structure, entity sets, navigation properties, function imports, $filter/$expand/$select/$top/$skip query options, deep insert, batch requests, ETag optimistic locking, OData annotations, SAP Gateway error handling, OData security (CSRF, SAML, OAuth2). Use when building OData services, consuming SAP OData APIs, troubleshooting OData errors, or designing OData-based integrations.
trigger:
  keywords: [odata, service, metadata, entity, navigation, gateway, v2, v4, crud, sap]
  intent: >-
    Use when building, consuming, troubleshooting, or designing SAP OData services (V2/V4) with Gateway, S/4HANA, or BTP.
---

# SAP OData Development

OData V2/V4 protocol patterns for SAP Gateway, S/4HANA, and BTP.

## OData URL Structure

```
https://<host>:<port>/sap/opu/odata/sap/<SERVICE_NAME_SRV>/<EntitySet>
  ?$format=json
  &$filter=MaterialType eq 'FERT'
  &$expand=to_ProductText
  &$select=Material,Description,Plant
  &$orderby=CreatedAt desc
  &$top=10
  &$skip=20
  &$count=true
```

## OData V2 vs V4

| Feature | V2 | V4 |
|---|---|---|
| Metadata path | `/$metadata` | `/$metadata` |
| Entity key access | `/Product('MAT001')` | `/Product('MAT001')` |
| Count | `$inlinecount=allpages` | `$count=true` |
| Batch | `/$batch` | `/$batch` |
| Null values | Omitted by default | `null` returned |
| Enum types | String-based | Typed enums |
| Containment | Not supported | Navigation via containment |

## $filter Examples

```
# V2/V4 equality
$filter=MaterialType eq 'FERT'

# Numeric comparison
$filter=NetPrice gt 100 and NetPrice lt 500

# Date filter
$filter=CreatedAt ge datetime'2026-01-01T00:00:00'

# String functions
$filter=startswith(Material,'MAT')
$filter=substringof('WIDGET',Description)

# Null check
$filter=Plant eq null
$filter=Plant ne null

# Logical OR
$filter=MaterialType eq 'FERT' or MaterialType eq 'HAWA'
```

## $expand (Navigation Properties)

```
# Single-level expand
$expand=to_ProductText

# Multi-level expand (V4 only)
$expand=to_Items($expand=to_Material)

# Expand with filter
$expand=to_Items($filter=Quantity gt 10;$top=5)
```

## Deep Insert (Parent + Children)

```http
POST /sap/opu/odata/sap/Z_PRODUCT_SRV/ProductSet HTTP/1.1
Content-Type: application/json
Accept: application/json

{
  "Material": "MAT001",
  "MaterialType": "FERT",
  "Description": "Test Widget",
  "to_ProductText": [{
    "Language": "EN",
    "Description": "English description"
  }, {
    "Language": "DE",
    "Description": "German description"
  }]
}
```

## Batch Operations

```http
POST /sap/opu/odata/sap/Z_PRODUCT_SRV/$batch HTTP/1.1
Content-Type: multipart/mixed; boundary=batch_123

--batch_123
Content-Type: application/http
Content-Transfer-Encoding: binary

GET ProductSet('MAT001') HTTP/1.1

--batch_123
Content-Type: application/http
Content-Transfer-Encoding: binary

POST ProductSet HTTP/1.1
Content-Type: application/json

{"Material":"MAT002","Description":"Batch created"}

--batch_123--
```

## ETag (Optimistic Locking)

```http
# Server returns ETag header:
# ETag: W/"datetime'2026-01-15T10%3A30%3A00'"

# Client sends If-Match for updates:
PUT /ProductSet('MAT001') HTTP/1.1
If-Match: W/"datetime'2026-01-15T10%3A30%3A00'"

# Server returns 412 Precondition Failed if record changed
```

## Error Handling

### SAP Gateway Error Format (V2)

```json
{
  "error": {
    "code": "SY/530",
    "message": {
      "lang": "en",
      "value": "Material MAT001 already exists"
    },
    "innererror": {
      "application": {
        "component_id": "MM",
        "service_namespace": "/SAP/",
        "service_id": "Z_PRODUCT_SRV",
        "service_version": "0001"
      },
      "transactionid": "ABC123..."
    }
  }
}
```

## CSRF Token (required for write operations)

```http
# Step 1: GET with X-CSRF-Token: Fetch
GET /sap/opu/odata/sap/Z_PRODUCT_SRV/ HTTP/1.1
X-CSRF-Token: Fetch

# Response header: x-csrf-token: abc123...

# Step 2: POST/PUT/PATCH/DELETE with token
POST /sap/opu/odata/sap/Z_PRODUCT_SRV/ProductSet HTTP/1.1
x-csrf-token: abc123...
Content-Type: application/json
```

## Consuming OData from Python

```python
import requests

# SAP OData client pattern
session = requests.Session()
session.auth = ('USER', 'PASSWORD')

# Fetch CSRF token
headers = {'X-CSRF-Token': 'Fetch'}
r = session.get(f'{base_url}/', headers=headers, params={'$format': 'json'})
token = r.headers.get('x-csrf-token', '')

# Query
headers['x-csrf-token'] = token
headers['Accept'] = 'application/json'
r = session.get(
    f'{base_url}/ProductSet',
    headers=headers,
    params={
        '$filter': "MaterialType eq 'FERT'",
        '$top': '50',
        '$format': 'json'
    }
)
products = r.json()['d']['results']
```

## Consuming OData from Node.js

```javascript
const axios = require('axios');

async function getProducts() {
  const client = axios.create({
    baseURL: 'https://s4hana.company.com:443/sap/opu/odata/sap/Z_PRODUCT_SRV',
    auth: { username: 'USER', password: 'PASSWORD' }
  });

  // Fetch CSRF
  const tokenResp = await client.get('/', { headers: { 'X-CSRF-Token': 'Fetch' } });
  const csrf = tokenResp.headers['x-csrf-token'];

  // Query
  const { data } = await client.get('/ProductSet', {
    headers: { 'x-csrf-token': csrf },
    params: { $filter: "MaterialType eq 'FERT'", $top: 50, $format: 'json' }
  });
  return data.d.results;
}
```

## SAP Gateway Service Registration

```bash
# Transaction: /IWFND/MAINT_SERVICE
# 1. Add Service
# 2. System Alias: LOCAL
# 3. Technical Service Name: Z_PRODUCT_SRV
# 4. Service Version: 0001
# 5. Click "Load Metadata" to verify

# Gateway Client test: /IWFND/GW_CLIENT
# Test URL: /sap/opu/odata/sap/Z_PRODUCT_SRV/ProductSet
```

## Gotchas

- **CSRF token required** for POST/PUT/PATCH/DELETE — GET "Fetch" first
- **$filter on Edm.Guid**: use `guid'...'` not plain string
- **V2 batch**: Content-Transfer-Encoding MUST be `binary`
- **V4 containment**: child resources accessed via parent navigation, not direct
- **SAP Gateway error** common causes: wrong system alias, inactive service, missing role
- **/IWFND/CACHE_CLEANUP** — run after service metadata changes
