# Sales Force Support APIs

APIs for managing leads, opportunities, appointments, phone calls, and tasks in SAP S/4HANA Sales.

**SAP Help Section:** [APIs for Sales Force Support](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/04d285a13aa840058928fc96196aec73.html)

---

## Table of Contents

1. [Lead (OData)](#lead-odata)
2. [Lead (SOAP)](#lead-soap)
3. [Opportunity (OData)](#opportunity-odata)
4. [Opportunity (SOAP)](#opportunity-soap)
5. [Appointment](#appointment)
6. [Phone Call](#phone-call)
7. [Task](#task)

---

## Lead (OData)

| Property | Value |
|----------|-------|
| **Technical Name** | `API_LEAD` |
| **Service URL** | `/sap/opu/odata/SAP/API_LEAD_SRV` |
| **Metadata** | `/sap/opu/odata/SAP/API_LEAD_SRV/$metadata` |
| **Batch** | `/sap/opu/odata/SAP/API_LEAD_SRV/$batch` |
| **Protocol** | OData (A2X, Synchronous) |
| **PFCG Role** | `SAP_S4C_SLS_LEAD` |
| **Auth Method** | User ID/password (Username Token) |
| **ETag Support** | Not supported in current release |
| **Doc URL** | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/c1f74f927c6641039093d7210078e70f.html) |

### Entity Types

| Entity | Type Name | Description |
|--------|-----------|-------------|
| Lead Header | `A_LeadType` | Lead header data |
| Lead Item | `A_LeadItemType` | Lead item (product/service) |
| Person Responsible | `A_LeadPersonRespType` | Person responsible for lead |
| Lead Text | `A_LeadTextType` | Free-text notes on lead |

### Navigation Properties

| Source | Target | Navigation Property | Cardinality |
|--------|--------|---------------------|-------------|
| A_Lead | A_LeadItem | `to_Item` | 0..* |
| A_Lead | A_LeadPersonResp | `to_PersonResponsible` | 0..* |
| A_Lead | A_LeadText | `to_Text` | 0..* |

### Operations

| Entity | Read | Create | Update | Delete |
|--------|------|--------|--------|--------|
| A_LeadType | Yes | Yes (deep + single) | Yes | **No** (lead deletion not supported) |
| A_LeadItemType | Yes | Yes | Yes | Yes |
| A_LeadPersonRespType | Yes | Yes | Yes | Yes |
| A_LeadTextType | Yes | Yes | Yes | Yes |

### Constraints

- Only one lead processed at a time (except with `$batch`)
- Deletion of the lead header is **not** supported
- Deep entity creation only with `A_LeadType` (Header)
- Parent entity must be created before child entities
- On create: Lead ID = `0000000000`, Lead UUID = `00000000-0000-0000-0000-000000000000`

### Response Codes

| Code | Meaning |
|------|---------|
| 200 OK | GET successful |
| 201 Created | POST successful |
| 202 Accepted | Request received |
| 204 No Content | PATCH/DELETE successful |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Business/technical error |

---

## Lead (SOAP)

| API Name | Technical Type | Protocol | Doc URL |
|----------|---------------|----------|---------|
| Lead (Asynchronous) | A2A | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/518e6d0a41e44778a7578a3abe38c816.html) |
| Lead - Confirm Processing | A2A | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/ee94eab425ab45caba0fbdaac727559c.html) |
| Lead (Bulk, Asynchronous) | A2A | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/ed60237f961349758bd5782c7b51a40a.html) |
| Lead (Bulk) - Confirm Processing | A2A | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/f16af3b65c934d4185f3c7f62d8b925a.html) |

---

## Opportunity (OData)

| Property | Value |
|----------|-------|
| **Technical Name** | `API_OPPORTUNITY` |
| **Service URL** | `/sap/opu/odata/SAP/API_OPPORTUNITY_SRV` |
| **Metadata** | `/sap/opu/odata/SAP/API_OPPORTUNITY_SRV/$metadata` |
| **Protocol** | OData (A2X, Synchronous) |
| **PFCG Role** | `SAP_S4C_SLS_OPPT` |
| **Auth Method** | User ID/password (Username Token) |
| **ETag Support** | Not supported in current release |
| **Doc URL** | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/c9fe1f949d5c4c5a93f5382dd49fc45f.html) |

### Entity Types

| Entity | Type Name | Description |
|--------|-----------|-------------|
| Opportunity Header | `A_OpportunityType` | Opportunity header |
| Opportunity Item | `A_OpportunityItemType` | Opportunity item |
| Person Responsible | `A_OpportunityPersonRespType` | Person responsible |
| Sales Representative | `A_OpportunitySalesRepType` | Sales representative |
| Opportunity Text | `A_OpportunityTextType` | Free-text notes |
| Follow-Up Sales Order | `A_OpportunityFUPSalesOrderType` | Follow-up to Sales Order (Read-only) |
| Follow-Up Sales Quotation | `A_OpportunityFUPSalesQuotationType` | Follow-up to Sales Quotation (Read-only) |
| Follow-Up Service Order | `A_OpportunityFUPServiceOrderType` | Follow-up to Service Order (Read-only) |
| Item Person Responsible | `A_OpportunityItemPersonRespType` | Item-level person responsible |
| Item Sales Representative | `A_OpportunityItemSalesRepType` | Item-level sales representative |
| Item Text | `A_ServiceOrderItemTextType` | Item-level text |
| Item Follow-Up Sales Order | `A_OpptyItmFUPSalesOrderType` | Item follow-up to Sales Order (Read-only) |
| Item Follow-Up Quotation | `A_OpptyItmFUPSalesQuotationType` | Item follow-up to Quotation (Read-only) |
| Item Follow-Up Service Order | `A_OpptyItmFUPServiceOrderType` | Item follow-up to Service Order (Read-only) |

### Navigation Properties

| Source | Target | Navigation Property | Cardinality |
|--------|--------|---------------------|-------------|
| A_Opportunity | A_OpportunityItem | `to_Item` | 0..* |
| A_Opportunity | A_OpportunityPersonResp | `to_PersonResponsible` | 0..* |
| A_Opportunity | A_OpportunityText | `to_Text` | 0..* |
| A_Opportunity | A_OpportunitySalesRep | `to_PersonResponsible` | 0..* |
| A_Opportunity | A_OpportunityFUPSalesOrder | `to_SalesOrder` | 0..* |
| A_Opportunity | A_OpportunityFUPSalesQuotation | `to_SalesQuotation` | 0..* |
| A_Opportunity | A_OpportunityFUPServiceOrder | `to_ServiceOrder` | 0..* |
| A_OpportunityItem | A_OpportunityItemPersonResp | `to_PersonResponsible` | 0..* |
| A_OpportunityItem | A_OpportunityItemText | `to_Text` | 0..* |
| A_OpportunityItem | A_OpportunityItemSalesRep | `to_SalesRepresentative` | 0..* |
| A_OpportunityItem | A_OpptyItmFUPSalesOrder | `to_OpportunityItemSalesOrder` | 0..* |
| A_OpportunityItem | A_OpptyItmFUPServiceOrder | `to_OpportunityItemServiceOrder` | 0..* |
| A_OpportunityItem | A_OpptyItmFUPSalesQuotation | `to_OpportunityItemSalesQuotation` | 0..* |

### Operations

| Entity | Read | Create | Update | Delete |
|--------|------|--------|--------|--------|
| A_OpportunityType | Yes | Yes (deep + single) | Yes | **No** |
| A_OpportunityItemType | Yes | Yes | Yes | Yes |
| A_OpportunityPersonRespType | Yes | Yes | Yes | Yes |
| A_OpportunitySalesRepType | Yes | Yes | Yes | Yes |
| A_OpportunityTextType | Yes | Yes | Yes | Yes |
| Follow-Up entities (all) | Yes | No | No | No |
| Item sub-entities | Yes | Yes | Yes | Yes |

### Constraints

- Deep entity creation restricted to `A_OpportunityType` (Header)
- Only one opportunity at a time (except `$batch`)
- Deletion of opportunity header not supported
- On create: Opportunity = `0000000000`, OpportunityUUID = `00000000-0000-0000-0000-000000000000`

---

## Opportunity (SOAP)

| API Name | Technical Type | Protocol | Doc URL |
|----------|---------------|----------|---------|
| Opportunity (Asynchronous) | A2A | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/de8d0a762bf743f1ae0c6708cf72a4e9.html) |
| Opportunity - Confirm Processing | A2A | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/a8aa123919454e0883e77a384332ba56.html) |
| Opportunity (Bulk, Asynchronous) | A2A | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/9df28a134700467db2d40be38b8ecf3b.html) |
| Opportunity (Bulk) - Confirm Processing | A2A | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/d6bdfaa1c47c483f8ed22019ba675f59.html) |

---

## Appointment

| Property | Value |
|----------|-------|
| **Protocol** | OData (A2X, Synchronous) |
| **Doc URL** | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/75359c8918234d47ad17d157e723b45b.html) |

### SOAP APIs

| API Name | Type | Doc URL |
|----------|------|---------|
| Appointment Activity (Async) | A2A | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/e20ebd051985420daf0192dee13f275f.html) |
| Appointment Activity - Confirm Processing | A2A | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/431b89f74ee841f4bab111bb550bcc3d.html) |
| Appointment Activity (Bulk, Async) | A2A | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/1e87fc2b2df948009b07f5d08420c958.html) |
| Appointment Activity (Bulk) - Confirm Processing | A2A | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/c4ced7c2e86745718605828c95ca5c74.html) |

---

## Phone Call

| Property | Value |
|----------|-------|
| **Protocol** | OData (A2X, Synchronous) |
| **Doc URL** | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/96226d442fd649b182be3a8bd94c88c8.html) |

### SOAP APIs

| API Name | Type | Doc URL |
|----------|------|---------|
| Phone Call Activity (Async) | A2A | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/f72307193a314c2e8811e86f745b967f.html) |
| Phone Call Activity - Confirm Processing | A2A | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/b36a4dddbad146cfa9c38c15af8a519b.html) |
| Phone Call Activity (Bulk, Async) | A2A | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/4cfc24162b624c12ac41b9d19b3683a1.html) |
| Phone Call Activity (Bulk) - Confirm Processing | A2A | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/e8ebc6334bb3454f91252d9f90a6813c.html) |

---

## Task

| Property | Value |
|----------|-------|
| **Protocol** | OData (A2X, Synchronous) |
| **Doc URL** | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/b093d125e226429fa2d4a9b138e410d6.html) |

### SOAP APIs

| API Name | Type | Doc URL |
|----------|------|---------|
| Task Activity (Async) | A2A | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/52860bca1ae6443b96878f04fc0f81f4.html) |
| Task Activity - Confirm Processing | A2A | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/46e9236bc86b487ea09d66dbe3164463.html) |
| Task Activity (Bulk, Async) | A2A | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/c57892c7021540a985d952184376b9ae.html) |
| Task Activity (Bulk) - Confirm Processing | A2A | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/74192b5ee80b4eac9f34f2f2470c1536.html) |
