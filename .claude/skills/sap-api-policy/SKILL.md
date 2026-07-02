---
name: sap-api-policy
description: SAP API Management policy design and governance — security, traffic, mediation, lifecycle
trigger:
  keywords: [api policy, api management, api proxy, rate limiting, api security, api key, api business hub, openapi spec sap, api gateway, api lifecycle]
  intent: Designing and managing API policies on SAP BTP API Management / Integration Suite
prerequisites:
  - SAP BTP API Management or Integration Suite entitlement
  - API Portal access (https://<subaccount>.apim.cfapps.<region>.hana.ondemand.com)
  - Postman or curl for testing
  - Backend API endpoint (SAP Gateway, CAP, or external)
---

# SAP API Policy — API Management & Governance

## 1. Architecture

```
Client → API Gateway (SAP API Management)
         ├─ Security: OAuth2, API Key, Basic Auth
         ├─ Traffic: Rate Limit, Spike Arrest, Caching
         ├─ Mediation: JSON↔XML, XSLT, URL Rewrite
         └─ Monitoring: Analytics, Alerts
```

## 2. Security Policies

```xml
<!-- OAuth2: validate XSUAA token -->
<OAuthV2 async="false" continueOnError="false" enabled="true">
    <ExternalAuthorization>false</ExternalAuthorization>
    <Operation>VerifyAccessToken</Operation>
    <SupportedGrantTypes>
        <GrantType>client_credentials</GrantType>
    </SupportedGrantTypes>
</OAuthV2>

<!-- JSON Threat Protection -->
<JSONThreatProtection>
    <ArrayElementCount>100</ArrayElementCount>
    <ContainerDepth>10</ContainerDepth>
    <StringValueLength>50000</StringValueLength>
</JSONThreatProtection>
```

## 3. Traffic Management

```xml
<!-- Spike Arrest: 100 req/s -->
<SpikeArrest><Rate>100ps</Rate>
    <Identifier ref="request.header.X-Forwarded-For"/></SpikeArrest>

<!-- Monthly Quota: 10K requests -->
<Quota type="calendar"><Allow count="10000"/>
    <Interval>1</Interval><TimeUnit>month</TimeUnit>
    <Distributed>true</Distributed></Quota>
```

## 4. Mediation & URL Rewrite

```xml
<!-- Rewrite OData path + inject client -->
<AssignMessage>
    <Set><Path>/sap/opu/odata/sap/ZMATERIAL_SRV/</Path>
        <QueryParams><QueryParam name="sap-client">100</QueryParam></QueryParams>
    </Set>
</AssignMessage>
```

## 5. API Lifecycle

| Phase | Activity |
|---|---|
| Design | OpenAPI spec → review in API Business Hub |
| Develop | Implement backend (CAP/ABAP) |
| Secure | Apply OAuth2 + threat + rate limit policies |
| Publish | Deploy proxy → expose endpoint |
| Monitor | Analytics dashboard |
| Deprecate | Sunset old versions → redirect |
| Retire | Remove proxy |

## 6. Policy Execution Order

```
ProxyEndpoint PreFlow → TargetEndpoint PreFlow → backend →
TargetEndpoint PostFlow → ProxyEndpoint PostFlow
```

## Pitfalls

- **Policy not applying** → Cause: wrong flow step. Solution: verify policy is attached to correct flow (PreFlow vs PostFlow) in API Portal.
- **OData $metadata timeout** → Cause: un-cached metadata response. Solution: add ResponseCache to proxy PreFlow, TTL=600s.
- **CSRF token missing** → Cause: OData writes need token. Solution: GET `x-csrf-token: Fetch` first, then POST/PUT with `x-csrf-token: <token>`.
- **Rate limit not enforced** → Cause: quota not distributed. Solution: set `<Distributed>true</Distributed>` on Quota policy.
- **SAML vs OAuth confusion** → Solution: use OAuth2 (XSUAA) for BTP apps, SAML bearer for SAP Gateway on-premise.

## Verification

```bash
# Test proxy health
curl -s -o /dev/null -w "%{http_code}" https://<proxy>.apim.cfapps.<region>.hana.ondemand.com/health
# Expect: 200

# Check OAuth is working
curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $TOKEN" \
  https://<proxy>/sap/opu/odata/sap/ZMATERIAL_SRV/MaterialSet?\$top=1
# Expect: 200

# Check rate limit headers
curl -sI -H "Authorization: Bearer $TOKEN" https://<proxy>/api/v1/test \
  | grep -i x-ratelimit
```