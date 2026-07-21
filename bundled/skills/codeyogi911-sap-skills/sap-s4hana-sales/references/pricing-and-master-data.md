# Pricing & Master Data APIs

APIs for managing sales master data (customer materials, incoterms, sales areas, org unit replication) and pricing condition records.

**SAP Help Section:** [APIs for Order and Contract Management](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/f67705a25e2b440f90a25faaffa5ffef.html)

---

## Table of Contents

1. [Customer Material](#customer-material)
2. [Incoterms (Read-Only)](#incoterms-read-only)
3. [Sales Area (Read-Only)](#sales-area-read-only)
4. [Replication of Org Units in Sales (SOAP)](#replication-of-org-units-in-sales-soap)
5. [Condition Record for Pricing](#condition-record-for-pricing)
6. [Other Pricing APIs (Read-Only)](#other-pricing-apis-read-only)

---

## Customer Material

| Property | Value |
|----------|-------|
| **Technical Name** | `API_CUSTOMER_MATERIAL_SRV` |
| **Service URL** | `/sap/opu/odata/SAP/API_CUSTOMER_MATERIAL_SRV` |
| **Metadata** | `/sap/opu/odata/SAP/API_CUSTOMER_MATERIAL_SRV/$metadata` |
| **Protocol** | OData (A2X, Synchronous) |
| **Doc URL** | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/529318c3a0014f1bb1911541546569a2.html) |

**Entity:** `A_CustomerMaterial`

**Operations:** Create, Read, Update, Delete

**Authorization Objects:** `B_BUP_PCPT`, `F_BKPF_BED`, `F_KNA1_BED`, `S_SERVICE`, `V_KNA1_VKO`

**Constraints:** Cannot CRUD multiple customer materials in a single `$batch` changeset.

**Event API:** [Customer Material Events](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/df799851fec8495aa91a25e534ab7ca4.html)

---

## Incoterms (Read-Only)

| Property | Value |
|----------|-------|
| **Protocol** | OData (A2X, Read-only) |
| **Doc URL** | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/f68abfe593df4415bfc3555f51c1bfd3.html) |

---

## Sales Area (Read-Only)

| Property | Value |
|----------|-------|
| **Protocol** | OData (A2X, Read-only) |
| **Doc URL** | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/f4ff6b854cc34b3ebd80b97e62048711.html) |

---

## Replication of Org Units in Sales (SOAP)

All use the **Data Replication Framework (DRF)** for asynchronous outbound replication.

| API Name | Technical Name | Doc URL |
|----------|---------------|---------|
| Configuration: Replication of Org Units | -- | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/11971c5c68a347269fc5839c3cd6b56c.html) |
| Sales Area - Replicate | `SalesAreaBulkReplication_Out` | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/be405ca47a0a4ef0b7f603798e5b1053.html) |
| Sales Organization - Replicate | -- | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/62105a5aca1f49e7bb26ddf9fc14bfe3.html) |
| Sales Office - Replicate | -- | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/e81e2db9da5043f69d23568550e73a4a.html) |
| Sales Group - Replicate | -- | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/5e34f78002da40239d00ff94ae69e584.html) |
| Sales Division - Replicate | -- | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/6df93fb722c844c38d159058182cbf4d.html) |
| Distribution Chain - Replicate | -- | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/48d9c93e9f364faead8d8beaa62d3173.html) |
| Distribution Channel - Replicate | -- | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/ea51db4c82cc4dc398fd0682d8c9add4.html) |
| Divisions Per Sales Org - Replicate | -- | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/1befa02f2a1c4c2ba0dcb653848d31b7.html) |

---

## Condition Record for Pricing

| Property | Value |
|----------|-------|
| **Technical Name** | `API_SLSPRICINGCONDITIONRECORD_SRV` |
| **Service URL** | `/sap/opu/odata/sap/API_SLSPRICINGCONDITIONRECORD_SRV` |
| **Batch** | `<host>/sap/opu/odata/sap/API_SLSPRICINGCONDITIONRECORD_SRV/$batch` |
| **Protocol** | OData (A2X, Synchronous) |
| **Doc URL** | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/7916962329ee49b293156fffddfb7dd8.html) |

### Entity Types

| Entity | Type Name | Description |
|--------|-----------|-------------|
| Condition Record | `A_SlsPrcgConditionRecord` | Pricing condition records |
| Condition Record Validity | `A_SlsPrcgCndnRecdValidity` | Validity periods for condition records |
| Pricing Scale | `A_SlsPrcgCndnRecordScale` | Pricing scales for records and supplements |
| Condition Supplement | `A_SlsPrcgCndnRecdSuplmnt` | Condition supplements |

### Operations

| Operation | Method | Notes |
|-----------|--------|-------|
| Create | POST | Deep insert required (Condition Record + Validity) |
| Read | GET | All data or filtered by properties |
| Update | PUT/PATCH | Use `ConditionIsDeleted` flag for logical delete |
| Delete | DELETE | Condition records, pricing scales, supplements |
| Batch | POST to `$batch` | Change sets required for CUD operations |

### Key Properties

- `ConditionValidityEndDate` (read-only)
- `ConditionValidityStartDate` (read-only)
- `ConditionIsDeleted` (deletion flag for update)
- ETag (in every entity, required for update/delete via `If-Match` header)

**Authorization Objects:** `S_SERVICE`, `V_KONH_VKO`, `V_KONH_VKS`, `V_VBAK_VKO`

### Constraints

- Condition tables without valid-from/valid-to date fields not supported
- Cannot create/process tax rates for Brazil
- Cannot combine Condition Records + Condition Record Validity filters with `$expand`
- Must use deep insert (Condition Record + Validity) for create
- Pricing scales for condition supplements cannot be created in deep insert
- Overlapping validity: existing records updated/replaced/deleted

### Response Codes

| Operation | Success | Response |
|-----------|---------|----------|
| Create | 201 Created | Created entities |
| Update/Delete | 204 No Content | Empty |
| Failure | 400 Bad Request | System messages + details |

---

## Other Pricing APIs (Read-Only)

| API Name | Technical Name | Doc URL |
|----------|---------------|---------|
| Field Catalog for Pricing in Sales | -- | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/aafab45b9aec4445b1be3a6effc683a9.html) |
| Condition Type for Pricing in Sales | -- | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/fcc6f65362484413bfbb0f7cae3652d3.html) |
| Condition Table for Pricing in Sales | -- | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/d2b2bc4e35e648e6aba617609aba9f37.html) |
| Condition Record - Replicate | -- | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/e2500c848c264417a9380ad6407dd5a4.html) |
| Access Sequence for Pricing in Sales | -- | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/df34f53fa1bc4d0ca0bb7dd8b25c7aec.html) |
| Pricing Procedure in Sales | -- | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/61b32450f3ce465cba4cacbb971dcfb4.html) |
| Condition Exclusion for Pricing in Sales | -- | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/0c49fca365e04450b69de48e253268dc.html) |

### Event APIs

- [Sales Pricing Condition Record Events](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/71703bca89464fa0a164163979327bf4.html)
- [Purchasing Pricing Condition Record Events](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/818f410d690147a08b55df0f7c388ae6.html)
