---
name: sap-s4hana-sales
description: >
  SAP S/4HANA On-Premise Sales API integration guide covering ~119 APIs across OData V2, OData V4,
  and SOAP protocols. Use when building integrations with SAP S/4HANA Sales — including sales orders,
  sales quotations, sales contracts, scheduling agreements, billing documents, customer returns,
  credit/debit memo requests, leads, opportunities, appointments, phone calls, tasks, pricing
  condition records, customer materials, and solution quotations. Triggers on: "SAP", "S/4HANA",
  "S4HANA", "OData", "SOAP A2A", "sales order", "sales quotation", "billing document",
  "customer return", "credit memo", "debit memo", "lead API", "opportunity API", "pricing condition",
  "scheduling agreement", "sales contract", "deep insert", "SAP API", "SAP integration",
  "API_SalesOrder", "API_LEAD", "API_OPPORTUNITY", "API_BILLING_DOCUMENT_SRV".
---

# SAP S/4HANA Sales APIs

**Source:** [SAP Help Portal — APIs for Sales](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/3bac8c01d7024ae1b15cf848ce12544e.html)
**Version:** SAP S/4HANA 2025 FPS01 (Feb 2026)

## Protocol Quick Reference

| Protocol | Version | Communication | Use Case |
|----------|---------|---------------|----------|
| **OData** | V2 | Synchronous | Standard CRUD, real-time integration |
| **OData** | V4 | Synchronous + Async | Next-gen APIs (RAP), lightweight JSON, deep insert with full response |
| **SOAP** | — | Asynchronous | Bulk processing, A2A/B2B integration, reliable messaging |

### Communication Types

| Type | Protocol | Execution | Use Case |
|------|----------|-----------|----------|
| **A2X** | OData | Synchronous | Connect SAP with external systems via HTTP |
| **A2A** | SOAP | Asynchronous | Internal system-to-system. Monitor via AIF (`/AIF/ERR`) or `SRT_MONI` |
| **B2B** | SOAP | Asynchronous | Cross-company/external landscape connectivity |

### OData V2 vs V4

| Feature | OData V2 | OData V4 |
|---------|----------|----------|
| Response format | XML/JSON | Lightweight JSON |
| Async mode | No | Yes (`prefer: respond-async`) |
| Minimal response | No | Yes (`prefer: return=minimal`) |
| Deep insert response | Key only | Full entity tree |
| Subentity filtering | Limited | Supported |
| Pricing in response | Limited | Complete (incl. subtotals) |
| ETag | Varies | Consistent (`If-Match` header) |
| Architecture | Classic SAP Gateway | RAP (ABAP RESTful Application Programming Model) |

Only 3 APIs have V4 versions: **Sales Order**, **Sales Contract**, **Customer Return**. Prefer V4 when available.

## API Selection Guide

### By Task

| Task | API | Protocol | Reference File |
|------|-----|----------|----------------|
| Create/manage sales orders | `API_SalesOrder` (V4) | OData V4 | [order-contract-management.md](references/order-contract-management.md) |
| Bulk create sales orders | `SalesOrderBulkRequest_In` | SOAP A2A | [order-contract-management.md](references/order-contract-management.md) |
| Simulate sales order (pricing/ATP/credit) | `API_SALES_ORDER_SIMULATION_SRV` | OData | [order-contract-management.md](references/order-contract-management.md) |
| Create/manage sales quotations | `API_SALES_QUOTATION_SRV` | OData | [order-contract-management.md](references/order-contract-management.md) |
| Create/manage sales contracts | `API_SalesContract` (V4) | OData V4 | [order-contract-management.md](references/order-contract-management.md) |
| Manage scheduling agreements | `API_SALES_SCHEDULING_AGREEMENT` | OData | [order-contract-management.md](references/order-contract-management.md) |
| Read/cancel billing documents | `API_BILLING_DOCUMENT_SRV` | OData | [billing.md](references/billing.md) |
| Create billing documents | SOAP A2A | SOAP | [billing.md](references/billing.md) |
| Create/manage customer returns | `API_CUSTOMER_RETURN_SRV` (V2) | OData V2 | [returns-and-claims.md](references/returns-and-claims.md) |
| Create credit memo requests | `API_CREDIT_MEMO_REQUEST_SRV` | OData | [returns-and-claims.md](references/returns-and-claims.md) |
| Manage leads | `API_LEAD` | OData | [sales-force-support.md](references/sales-force-support.md) |
| Manage opportunities | `API_OPPORTUNITY` | OData | [sales-force-support.md](references/sales-force-support.md) |
| Manage pricing conditions | `API_SLSPRICINGCONDITIONRECORD_SRV` | OData | [pricing-and-master-data.md](references/pricing-and-master-data.md) |
| Manage customer materials | `API_CUSTOMER_MATERIAL_SRV` | OData | [pricing-and-master-data.md](references/pricing-and-master-data.md) |
| Solution quotations | OData A2X | OData | [solution-business-and-index.md](references/solution-business-and-index.md) |

### By Protocol Choice

- **Real-time CRUD on single documents** → OData (V4 preferred if available)
- **Bulk/batch processing** → SOAP A2A
- **Cross-company B2B** → SOAP B2B
- **Simulation (no save)** → OData Simulation APIs
- **Read-only master data** → OData A2X (Read)

## Authentication

| Method | OData V2 | OData V4 | SOAP |
|--------|----------|----------|------|
| Basic (User ID/Password) | Yes | Yes | Yes (Username Token) |
| X.509 Certificate | — | Yes | Yes (X509 Token) |
| OAuth 2.0 | — | Yes | — |

### Common Authorization Objects

| Object | Description |
|--------|-------------|
| `S_SERVICE` | Check at Start of External Services (required by all APIs) |
| `V_VBAK_AAT` | Sales Document: Authorization for Sales Document Types |
| `V_VBAK_VKO` | Sales Document: Authorization for Sales Areas |
| `V_VBAK_APM` | Sales Document: Approval Management |
| `V_VBRK_FKA` | Billing: Authorization for Billing Types |
| `V_VBRK_VKO` | Billing: Authorization for Sales Organizations |
| `V_KONH_VKO` | Condition: Authorization for Sales Organizations |
| `/AIF/PROC` | AIF Interface Processing (SOAP A2A APIs) |

## Common Implementation Patterns

### Service Activation

**OData APIs:** Activate via transaction for maintaining services on SAP Gateway hub system.

**SOAP A2A APIs:** ICF service is **inactive by default**. Activate via `SICF`: Select service → Menu Service/Host → Activate.

### Deep Insert (Required by Most Sales APIs)

```
POST /sap/opu/odata/SAP/<SERVICE>/<HeaderEntity>
Content-Type: application/json

{
  "HeaderField1": "value",
  "to_Item": [
    {
      "ItemField1": "value",
      "to_Partner": [...]
    }
  ],
  "to_Partner": [...],
  "to_PricingElement": [...],
  "to_Text": [...]
}
```

### $batch Request Pattern

```
POST /sap/opu/odata/SAP/<SERVICE>/$batch
Content-Type: multipart/mixed; boundary=batch

--batch
Content-Type: multipart/mixed; boundary=changeset

--changeset
Content-Type: application/http
Content-Transfer-Encoding: binary

<individual request>
--changeset--
--batch--
```

**Universal constraint:** No multiple documents in a single changeset.

### ETag Handling (Optimistic Concurrency)

**OData V4** (Sales Order, Sales Contract): `If-Match` header required for all change operations. ETag = `LastChangeDateTime`.

**OData V2** (Customer Return): GET → retrieve `LastChangeDateTime` → `$batch` changeset with MERGE (If-Match) as first op, then payload.

**Pricing APIs:** ETag in every entity; retrieve via GET, include in `If-Match`.

### Async Mode (OData V4 Only)

Set `prefer: respond-async` header. Response returns `202 Accepted` with `location` header containing a polling URL.

### Error Monitoring

| Protocol | Tool | Transaction |
|----------|------|-------------|
| OData | SAP Gateway Error Log | — |
| SOAP A2A | SAP Application Interface Framework (AIF) | `/AIF/ERR` |
| SOAP A2A | SOAP Monitoring | `SRT_MONI` |

### BAdI Integration Points

Available for Sales Orders, Customer Returns, Scheduling Agreements, Credit/Debit Memos:

- **Sales Document Check Before Save BAdI** — Cancel without saving on error
- **Sales Header Check BAdI** — Continue and save
- **Sales Item Check BAdI** — Continue and save

## Reference Files

Read the relevant reference file when working with a specific API domain:

| File | When to Read |
|------|-------------|
| [sales-force-support.md](references/sales-force-support.md) | Working with Lead, Opportunity, Appointment, Phone Call, or Task APIs |
| [order-contract-management.md](references/order-contract-management.md) | Working with Sales Orders, Quotations, Contracts, or Scheduling Agreements |
| [pricing-and-master-data.md](references/pricing-and-master-data.md) | Working with Pricing Condition Records, Customer Materials, or Sales Org master data |
| [billing.md](references/billing.md) | Working with Billing Documents or Billing Requests |
| [returns-and-claims.md](references/returns-and-claims.md) | Working with Customer Returns, Credit/Debit Memos, or Sales Orders Without Charge |
| [solution-business-and-index.md](references/solution-business-and-index.md) | Working with Solution Quotations, or looking up an API by technical name |
