# Returns & Claims APIs

APIs for managing customer returns, credit/debit memo requests, and sales orders without charge in SAP S/4HANA.

---

## Table of Contents

1. [Customer Return (OData V2)](#customer-return-odata-v2)
2. [Customer Return (OData V4)](#customer-return-odata-v4)
3. [Other Customer Return APIs](#other-customer-return-apis)
4. [Sales Order Without Charge](#sales-order-without-charge)
5. [Credit Memo Request](#credit-memo-request)
6. [Debit Memo Request](#debit-memo-request)
7. [Event APIs](#event-apis)

---

## Customer Return (OData V2)

| Property | Value |
|----------|-------|
| **Technical Name** | `API_CUSTOMER_RETURN_SRV` |
| **Service URL** | `/sap/opu/odata/SAP/API_CUSTOMER_RETURN_SRV` |
| **Metadata** | `/sap/opu/odata/SAP/API_CUSTOMER_RETURN_SRV/$metadata` |
| **Protocol** | OData V2 (A2X, Synchronous) |
| **Doc URL** | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/69bd2e81cb394eb0b3d8eae85d6b4517.html) |

### Entity Types

| Entity | Node | Notes |
|--------|------|-------|
| Returns Order | `A_CustomerReturn` | Header |
| Returns Order Partner | -- | -- |
| Pricing Element | -- | Manually entered |
| Header Related Object | -- | -- |
| Header Text | -- | -- |
| Returns Order Item | `A_CustomerReturnItem` | -- |
| Item Partner | -- | -- |
| Item Pricing Element | -- | Manually entered |
| Item Text | -- | -- |
| Item Related Object | -- | -- |
| Schedule Line | -- | **GET only** |
| Serial Number | -- | -- |
| Process Steps | -- | **GET only** |
| Value-Added Service | -- | -- |

### Operations

| Operation | Method | Notes |
|-----------|--------|-------|
| Read | GET | With filters or all data |
| Create (order) | POST | **Deep insert required** (header + at least one sub-entity) |
| Create (item) | POST | **Deep insert required** (item + at least one sub-entity) |
| Update | PATCH/MERGE | Header, partners, pricing, text, items |
| Delete | DELETE | All entities including header |

### ETag Handling

Implemented on `A_CustomerReturn` node with `LastChangeDateTime`:

1. GET to retrieve `LastChangeDateTime`
2. Create `$batch` with one changeset
3. First operation: MERGE `A_CustomerReturn` with `LastChangeDateTime` + `If-Match` header
4. Second operation: Desired payload (POST/MERGE item, etc.)

**Authorization Objects:** `S_SERVICE`, `M_BEST_BSA`, `M_BEST_EKG`, `M_BEST_EKO`, `M_BEST_WRK`, `M_MATE_MAN`, `M_MATE_MAR`, `M_MATE_MAT`, `M_MATE_STA`, `M_MATE_WGR`, `V_LIKP_VST`, `V_VBAK_AAT`, `V_VBAK_VKO`, `WFD_ASSGMT`, `C_STUE_BER`, `C_STUE_WRK`

### Constraints

- No one-time customers
- No single entity creation -- **deep insert only**
- No subentity filter search
- No multiple returns in single `$batch` changeset
- BAdIs: `Sales Document Check Before Save`, `Sales Header Check`, `Sales Item Check`

---

## Customer Return (OData V4)

| Property | Value |
|----------|-------|
| **Protocol** | OData V4 (A2X) |
| **Doc URL** | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/0227a02f513a452c96a0efbe848496d3.html) |

---

## Other Customer Return APIs

| API Name | Type | Protocol | Doc URL |
|----------|------|----------|---------|
| Customer Return (A2A) | A2A | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/88075b574160445a8aa3670f0edd12ed.html) |
| Customer Return - Confirm Processing (A2A) | A2A | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/782cb0425aef4c2a8aef185802d3bc33.html) |
| Customer Return - Replicate (A2A) | A2A | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/67d7dbd3a97a4603b609e97850dcfdf0.html) |
| Customer Return - Simulate (A2X) | A2X | OData | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/8b21e92ee26b4da29f0ce9654a1d587e.html) |
| Sales Order/Customer Return (B2B) | B2B | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/958f6d37ff264a9f8bec2f095628bfb6.html) |
| Returns Inspection (A2X) | A2X | OData | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/b3a6192e1f6d42e8a2e41a1aeb2538f5.html) |
| Returns Inspection (A2X) **(Deprecated)** | A2X | OData | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/ef543281000346ea990173dc872bf847.html) |

---

## Sales Order Without Charge

| Property | Value |
|----------|-------|
| **Protocol** | OData (A2X) |
| **Doc URL** | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/1eb3e97d4e314e769d614b8d5b16468d.html) |

---

## Credit Memo Request

| Property | Value |
|----------|-------|
| **Technical Name** | `API_CREDIT_MEMO_REQUEST_SRV` |
| **Service URL** | `/sap/opu/odata/SAP/API_CREDIT_MEMO_REQUEST_SRV` |
| **Metadata** | `/sap/opu/odata/SAP/API_CREDIT_MEMO_REQUEST_SRV/$metadata` |
| **Protocol** | OData (A2X, Synchronous) |
| **Doc URL** | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/191531b7e2e048d9bddffab772f1788b.html) |

### Entity Types

| Entity | Type Name |
|--------|-----------|
| Credit Memo Request Header | `A_CreditMemoRequest` |
| Header Partner | `A_CreditMemoReqPartner` |
| Header Pricing Element | `A_CreditMemoReqPrcgElmnt` |
| Header Text | `A_CreditMemoReqText` |
| Header Subsequent Process Flow | `A_CreditMemoReqSubsqntProcFlow` |
| Credit Memo Request Item | `A_CreditMemoRequestItem` |
| Item Partner | `A_CreditMemoReqItemPartner` |
| Item Pricing Element | `A_CreditMemoReqItemPrcgElmnt` |
| Item Text | `A_CreditMemoReqItemText` |
| Item Subsequent Process Flow | `A_CrdMmReqItemSubsqntProcFlow` |
| Item Value Added Service | `A_CreditMemoValAddedSrvc` |

**Operations:** Create (deep insert only), Read, Update (PATCH/MERGE), Delete

**Authorization Objects:** `S_SERVICE`, `V_VBAK_AAT`, `V_VBAK_VKO`, `V_VBAK_APM`

### Constraints

- No one-time customers
- Deep insert only (no single entity creation)
- No subentity filter search
- No multiple credit memos in single `$batch` changeset
- Max 20 non-fatal messages; first is generic, rest sorted by severity
- BAdIs: `Sales Document Check Before Save`, `Sales Header Check`, `Sales Item Check`

**Simulate API:** [Credit Memo Request - Simulate](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/c989713e57b2466dbbacde00ac7f82ae.html)

---

## Debit Memo Request

| API Name | Doc URL |
|----------|---------|
| Debit Memo Request (A2X) | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/e7f50d9ea49d49c7a428da494fce2c44.html) |
| Debit Memo Request - Simulate (A2X) | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/2b5cfb29c8f14d63b8c8b9781a5c9da0.html) |

---

## Event APIs

- [Sales Order Without Charge Events](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/38eba7d13a994fba8d0831497c88ffa1.html)
- [Credit Memo Request Events](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/2990a27adf0e450980a4196bde5f68a5.html)
- [Debit Memo Request Events](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/113b0fe0c1994d7585e179f03d2fa170.html)
- [Customer Return Events](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/3dd99b16b239476ca4764f8837ec95c9.html)
