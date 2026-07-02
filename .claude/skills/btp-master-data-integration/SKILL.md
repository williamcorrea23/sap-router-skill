---
name: btp-master-data-integration
description: SAP Master Data Integration (MDI) — BP/Material replication, distribution models, CPI iFlow integration
trigger:
  keywords: [mdi, master data, business partner replication, material master sync, distribution model, master data hub]
  intent: Replicating master data between SAP systems via BTP MDI
prerequisites:
  - BTP subaccount with MDI entitlement (Enterprise Messaging + MDI service)
  - S/4HANA system (source or target) with MDI-compatible APIs
  - CPI tenant for iFlow-based replication (optional but recommended)
  - Postman or curl for API testing
---

# SAP Master Data Integration (MDI)

Central hub for master data harmonization — Business Partner, Material, Cost Center, etc.

## 1. Enable MDI

```bash
# Create service instance
cf create-service master-data-integration standard mdi-instance
cf create-service-key mdi-instance mdi-key
cf service-key mdi-instance mdi-key
# → Save the `url` and `clientid`/`clientsecret`
```

## 2. Define Distribution Model

```json
{
  "sourceSystem": "S4H_100",
  "entityType": "BusinessPartner",
  "targetSystems": ["SFSF_worker", "COM_Cloud_customer"]
}
```

Entities: `BusinessPartner`, `Material`, `CostCenter`, `ProfitCenter`, `CompanyCode`.

## 3. Push Master Data via API

```bash
# Get OAuth token
TOKEN=$(curl -s -X POST "$AUTH_URL/oauth/token" \
  -d "grant_type=client_credentials&client_id=$CLIENT_ID&client_secret=$CLIENT_SECRET" \
  | jq -r '.access_token')

# Send Business Partner
curl -X POST "$MDI_URL/api/v1/BusinessPartner" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"BusinessPartner":"1000001","BusinessPartnerName":"ACME Corp"}'
```

## 4. CPI iFlow Integration

```
S/4HANA → CPI iFlow (BAPI_MATERIAL_GETLIST → MDI API map) → MDI Service → Targets
```

Key CPI patterns: idempotency check (avoid duplicate BP), field mapping (S/4 field → MDI field), error logging to Cloud Logging.

## 5. Monitoring

MDI dashboard → Distribution run status, record-level errors, queue depth, processing time per entity.

## Pitfalls

- **7-day message retention** → Cause: default retention is 7 days. Solution: configure retention on Enterprise Messaging if longer replay needed.
- **One source of truth per entity** → Cause: multiple systems pushing BP/Material. Solution: designate one source system per entity type on the distribution model.
- **Field name mismatch** → Cause: source field doesn't match MDI entity attribute. Solution: check MDI entity schema via `GET $MDI_URL/api/v1/$metadata`, map fields in CPI iFlow.
- **Duplicate Business Partner** → Cause: MDI receives same BP from multiple sources. Solution: set up dedup rules in distribution model (priority order by source).
- **MDI instance not provisioning** → Cause: missing Enterprise Messaging prerequisite. Solution: first create Enterprise Messaging instance, then MDI.

## Verification

```bash
# Check MDI service health
curl -s -o /dev/null -w "%{http_code}" "$MDI_URL/health/v1"
# Expect: 200

# List distribution models
curl -s -H "Authorization: Bearer $TOKEN" "$MDI_URL/api/v1/DistributionModel" | jq

# Check replication log
curl -s -H "Authorization: Bearer $TOKEN" "$MDI_URL/api/v1/DistributionLog?$top=5" | jq
```