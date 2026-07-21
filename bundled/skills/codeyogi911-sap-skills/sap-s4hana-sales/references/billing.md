# Billing APIs

APIs for managing billing documents, billing requests, self-billing, and subscription billing integration in SAP S/4HANA.

---

## Table of Contents

1. [Billing Document (OData)](#billing-document-odata)
2. [Other Billing APIs](#other-billing-apis)

---

## Billing Document (OData)

| Property | Value |
|----------|-------|
| **Technical Name** | `API_BILLING_DOCUMENT_SRV` |
| **Service URL** | `/sap/opu/odata/SAP/API_BILLING_DOCUMENT_SRV` |
| **Metadata** | `/sap/API_BILLING_DOCUMENT_SRV/$metadata` |
| **Protocol** | OData (A2X, Synchronous) |
| **Doc URL** | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/fe6f3eda2f914d81b512493fd79e9769.html) |

### Entity Types

| Entity | Description |
|--------|-------------|
| Billing Document Header | Header fields valid for all items |
| Header Partner | Header-level partners |
| Header Pricing Element | Header pricing elements |
| Header Text | Header-level texts |
| Billing Document Item | Billing document items |
| Item Partner | Item-level partners |
| Item Pricing Element | Item pricing elements |
| Item Text | Item-level texts |

### Operations

- Read billing document data
- Cancel billing documents
- Get PDF of billing documents
- Complete pro forma invoice (single by number; multiple via `$batch`)

**Authorization Objects:** `V_VBRK_FKA`, `V_VBRK_VKO`, `S_SERVICE`

---

## Other Billing APIs

| API Name | Type | Protocol | Doc URL |
|----------|------|----------|---------|
| Billing Document - Create | A2A | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/3ddf092469f8410f9186c0aaab1ec56e.html) |
| Billing Document - Send Creation Confirmation | A2A | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/f363219973f94b969fe8d47c0cdd6dcf.html) |
| Billing Document - Create with SD Doc Reference | A2A | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/63effdc0e14b4719bc72707672cac1cb.html) |
| Billing Document - Confirm Creation with SD Doc Ref | A2A | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/bffcc5e4b708410d8a232a9b2de7713a.html) |
| Billing Document Request - Create | A2A | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/85faa648ad684764a5b2361b88ca074a.html) |
| Billing Document Request - Send Creation Confirmation | A2A | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/ab19ef0c4112472fbc7719fad8427c3a.html) |
| Billing Document Request - Read, Reject, Delete | A2X | OData | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/ddcccb0282774476869bc499812cf793.html) |
| Customer Invoice - Send (B2B) | B2B | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/a95e8586cf87415890c74127e9c7ae52.html) |
| Manage Attachments in Billing Documents | A2X | OData | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/8f4dd26933404a89abc1829cdb7fd945.html) |
| APIs for Integration with SAP Self-Billing Cockpit | A2X | OData | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/a1830442ce474d46b4e7b17bb32411aa.html) |
| APIs for Integration with SAP Subscription Billing | A2X | OData | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/5538696693744a4492f27e178e72a92b.html) |

### Event APIs

- [Billing Document Events](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/28ff5a6e242249e0b82645ca26d46043.html)
- [Billing Document Request Events](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/623cd898daf54d0c936a19ea8db9cd48.html)
