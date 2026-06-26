---
name: btp-master-data-integration
description: SAP Master Data Integration (MDI) — master data distribution across SAP systems, harmonization models, distribution models, business partner replication, material master sync, CPI iFlow integration for MDI. Use when replicating master data between SAP systems or setting up MDI distribution models.
---

# SAP Master Data Integration (MDI)

Central hub for master data harmonization across SAP systems on BTP.

## Architecture

```
SAP S/4HANA (BP/Material) ──┐
SAP MDG ────────────────────┤
SAP SuccessFactors ─────────┤── MDI Service (BTP) ──→ Target Systems
External systems ───────────┤
```

## Distribution Model

```
Source: S/4HANA Entity: BusinessPartner
  → SuccessFactors (worker data)
  → Commerce Cloud (customer)
  → S/4HANA-CRM (sold-to party)
```

## APIs

```bash
# Inbound API (Push to MDI)
curl -X POST https://mdi.cfapps.<region>.hana.ondemand.com/api/v1/BusinessPartner \
  -H "Content-Type: application/json" \
  -d '{"BusinessPartner":"1000001","BusinessPartnerName":"ACME"}'
```

## CPI Integration

```
SAP S/4HANA → CPI iFlow (BAPI → MDI API mapping) → MDI Service → target systems
```

## Monitoring

MDI Dashboard: distribution run status, record-level errors, queue depth per target, processing time per entity type.

## Gotchas
- Message retention: 7 days default
- One source of truth per entity type
- Field names must align between source and MDI entity attributes
