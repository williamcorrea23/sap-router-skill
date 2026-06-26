---
name: sap-api-policy
description: >-
  SAP API Management policy design and governance — API proxy configuration,
  security policies (OAuth, API Key, Basic Auth), traffic management (rate
  limiting, spike arrest), mediation policies (JSON→XML, XSLT), SAP API
  Business Hub publication, API lifecycle management, OpenAPI/Swagger spec
  generation for SAP services. Use when designing API policies, managing
  API proxies on SAP BTP, securing OData endpoints, or publishing APIs
  to SAP API Business Hub. Triggers on: "API policy", "API management",
  "API proxy", "rate limiting", "API security", "API key", "API Business Hub",
  "OpenAPI spec SAP", "API gateway", "API lifecycle".
---

# SAP API Policy — API Management & Governance

Design and manage API policies for SAP BTP API Management / Integration Suite.
Covers security, traffic, mediation, and lifecycle policies.

## Architecture

```
Client → API Gateway (API Management) → Backend (SAP S/4HANA / BTP)
         │
         ├─ Security: OAuth2, API Key, Basic Auth
         ├─ Traffic: Rate Limit, Spike Arrest, Caching
         ├─ Mediation: JSON↔XML, XSLT, URL Rewrite
         └─ Monitoring: Analytics, Alerts, Logging
```

## Security Policies

### OAuth2 Client Credentials

```xml
<!-- oauth2-policy.xml -->
<AssignMessage async="false" continueOnError="false" enabled="true"
    xmlns="http://sap.com/apimgmt/policies">
    <Add>
        <Headers>
            <Header name="Authorization">Bearer {oauth.token}</Header>
        </Headers>
    </Add>
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
</AssignMessage>
```

### API Key Validation

```javascript
// ValidateAPIKey.js — JavaScript policy for API key validation
var apiKey = context.getVariable("request.header.X-API-Key");
var validKeys = context.getVariable("api.keys").split(",");

if (!apiKey || validKeys.indexOf(apiKey) === -1) {
    context.setVariable("response.status.code", 401);
    context.setVariable("response.header.Content-Type", "application/json");
    context.setVariable("response.content", JSON.stringify({
        error: "Unauthorized",
        message: "Invalid or missing API key"
    }));
    throw new Error("API Key validation failed");
}

// Log access for audit
context.setVariable("api.requester", apiKey);
```

### Threat Protection (JSON/XML)

```xml
<!-- threat-protection-policy.xml -->
<JSONThreatProtection async="false" continueOnError="false" enabled="true">
    <ArrayElementCount>100</ArrayElementCount>
    <ContainerDepth>10</ContainerDepth>
    <ObjectEntryCount>1000</ObjectEntryCount>
    <ObjectEntryNameLength>128</ObjectEntryNameLength>
    <StringValueLength>50000</StringValueLength>
</JSONThreatProtection>
```

## Traffic Management Policies

### Spike Arrest

```xml
<!-- spike-arrest-policy.xml -->
<SpikeArrest async="false" continueOnError="false" enabled="true">
    <Rate>100ps</Rate>  <!-- 100 requests per second -->
    <Identifier ref="request.header.X-Forwarded-For"/>
    <MessageWeight ref="request.header.Content-Length"/>
</SpikeArrest>
```

### Quota / Rate Limiting

```xml
<!-- quota-policy.xml -->
<Quota async="false" continueOnError="false" enabled="true" type="calendar">
    <Allow count="10000"/>  <!-- 10K requests -->
    <Interval>1</Interval>
    <TimeUnit>month</TimeUnit>
    <Distributed>true</Distributed>
    <Synchronous>true</Synchronous>
    <AsynchronousConfiguration>
        <SyncIntervalInSeconds>60</SyncIntervalInSeconds>
    </AsynchronousConfiguration>
</Quota>
```

### Response Caching

```xml
<!-- response-cache-policy.xml -->
<ResponseCache async="false" continueOnError="false" enabled="true">
    <CacheKey>
        <Prefix>odata-api</Prefix>
        <KeyFragment ref="request.uri"/>
    </CacheKey>
    <ExpirySettings>
        <TimeoutInSec>300</TimeoutInSec>  <!-- 5 min cache -->
    </ExpirySettings>
</ResponseCache>
```

## Mediation Policies

### JSON ↔ XML Conversion

```javascript
// ConvertSOAPtoREST.js — Transform SOAP backend to REST API
var soapPayload = context.getVariable("response.content");
var jsonPayload = XMLtoJSON(soapPayload);

// Flatten SAP namespace prefixes
jsonPayload = jsonPayload.replace(/:ns[0-9]/g, "");

context.setVariable("response.content", jsonPayload);
context.setVariable("response.header.Content-Type", "application/json");
```

### URL Rewrite for OData

```xml
<!-- url-rewrite-odata.xml -->
<AssignMessage async="false" continueOnError="false" enabled="true">
    <AssignTo createNew="false" type="request"/>
    <Set>
        <Path>/sap/opu/odata/sap/{odata_service}/</Path>
        <QueryParams>
            <QueryParam name="sap-client">100</QueryParam>
        </QueryParams>
    </Set>
</AssignMessage>
```

## SAP API Business Hub Integration

### OpenAPI Spec Template

```yaml
# sap-api-spec.yaml
openapi: 3.0.3
info:
  title: Material Management API
  description: OData V2 API for SAP S/4HANA Material Master
  version: "1.0.0"
  contact:
    name: SAP Integration Team
servers:
  - url: https://{host}:{port}/sap/opu/odata/sap/ZMATERIAL_SRV
    variables:
      host:
        default: my-s4hana.example.com
      port:
        default: "443"
paths:
  /MaterialSet:
    get:
      summary: Get list of materials
      parameters:
        - name: $filter
          in: query
          schema:
            type: string
          description: OData filter expression
        - name: $top
          in: query
          schema:
            type: integer
          description: Max number of results
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MaterialCollection'
    post:
      summary: Create material
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Material'
      responses:
        '201':
          description: Created
        '400':
          description: Bad Request

components:
  schemas:
    Material:
      type: object
      properties:
        Material:
          type: string
          maxLength: 18
          description: Material number
        MaterialType:
          type: string
          maxLength: 4
          description: Material type (FERT, HAWA, ROH, etc.)
        IndustrySector:
          type: string
          maxLength: 1
        MaterialDescription:
          type: string
          maxLength: 40
        BaseUnitOfMeasure:
          type: string
          maxLength: 3
    MaterialCollection:
      type: object
      properties:
        d:
          type: object
          properties:
            results:
              type: array
              items:
                $ref: '#/components/schemas/Material'
```

## API Lifecycle Management

| Phase | Activity | Tool |
|---|---|---|
| Design | Define OpenAPI spec, review | SAP API Business Hub |
| Develop | Implement backend (ABAP/CAP) | ADT / BAS |
| Secure | Apply policies, test | API Management |
| Publish | Deploy proxy, expose endpoint | API Portal |
| Monitor | Analytics, alerts, errors | API Analytics |
| Deprecate | Sunset old versions, redirect | API Portal |
| Retire | Remove proxy, archive docs | API Management |

## Policy Template Library

```bash
# Generate policy templates via CLI
python scripts/api_policy_gen.py template --type oauth2 --output oauth2-policy.xml
python scripts/api_policy_gen.py template --type rate-limit --rate 100pm
python scripts/api_policy_gen.py template --type cors --origins "*.sap.com"
python scripts/api_policy_gen.py template --type json-threat --max-depth 10
```

## Integration with sap_router.py

```python
# Added to ROUTING_TABLE:
API_POLICY_ACTIONS = {
    'api_proxy_create': 'sap-api-policy → generate proxy config',
    'api_policy_apply': 'sap-api-policy → apply security/traffic policy',
    'api_spec_generate': 'sap-api-policy → generate OpenAPI spec',
    'api_publish': 'sap-api-policy → publish to API Business Hub',
}
```

## Gotchas

- **SAP API Management vs Integration Suite API Management**: Different products; policies mostly compatible
- **Policy execution order**: ProxyEndpoint PreFlow → TargetEndpoint PreFlow → backend → TargetEndpoint PostFlow → ProxyEndpoint PostFlow
- **OData $metadata caching**: Cache metadata response; it's large and changes rarely
- **CSRF tokens for write**: OData POST/PUT/PATCH require X-CSRF-Token from GET with `x-csrf-token: Fetch` header
- **SAML vs OAuth2 for SAP**: Use OAuth2 (XSUAA) for BTP apps, SAML for on-premise Gateway
- **Rate limit headers**: Return X-RateLimit-Remaining, X-RateLimit-Reset headers for client awareness
- **Policy variables**: Use `context.getVariable()` not direct access; policy variables are scoped
