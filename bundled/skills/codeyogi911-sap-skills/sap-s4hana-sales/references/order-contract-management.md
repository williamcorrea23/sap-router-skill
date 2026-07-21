# Order & Contract Management APIs

APIs for managing sales quotations, sales contracts, scheduling agreements, and sales orders in SAP S/4HANA.

**SAP Help Section:** [APIs for Order and Contract Management](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/f67705a25e2b440f90a25faaffa5ffef.html)

---

## Table of Contents

1. [Sales Inquiry (Read-Only)](#sales-inquiry-read-only)
2. [Sales Quotation](#sales-quotation)
3. [Sales Contract (OData V2)](#sales-contract-odata-v2)
4. [Sales Contract (OData V4)](#sales-contract-odata-v4)
5. [Sales Scheduling Agreement](#sales-scheduling-agreement)
6. [Sales Order (OData V4)](#sales-order-odata-v4)
7. [Sales Order (OData V2)](#sales-order-odata-v2)
8. [Sales Order (SOAP A2A)](#sales-order-soap-a2a)
9. [Other Sales Order APIs](#other-sales-order-apis)
10. [Sales Order Simulation](#sales-order-simulation)
11. [Additional Sales Document APIs](#additional-sales-document-apis)

---

## Sales Inquiry (Read-Only)

| Property | Value |
|----------|-------|
| **Protocol** | OData (A2X, Read-only) |
| **Doc URL** | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/3913cc82abf14e5ca269ff691c7a2958.html) |

---

## Sales Quotation

| Property | Value |
|----------|-------|
| **Technical Name** | `API_SALES_QUOTATION_SRV` |
| **Service URL** | `/sap/opu/odata/SAP/API_SALES_QUOTATION_SRV` |
| **Metadata** | `/sap/opu/odata/SAP/API_SALES_QUOTATION_SRV/$metadata` |
| **Protocol** | OData (A2X, Synchronous) |
| **Doc URL** | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/bcfea10daf7241aea335dab3bc70ea8e.html) |

### Entity Types

- `A_SalesQuotation` -- Sales quotation header
- `A_SalesQuotationItem` -- Sales quotation item
- Partners, Pricing Elements, Texts, Related Objects, Process Flows

**Operations:** Create, Read, Update, Delete + Release/Reject (approval workflow)

**Authorization Objects:** `S_SERVICE`, `V_VBAK_AAT`, `V_VBAK_VKO`, `V_VBAK_APM`

### Constraints

- No one-time customer sales
- No subentity search with filters
- No multiple quotations in a single `$batch` changeset
- Max 20 non-fatal messages per request

### Event APIs

- [Sales Inquiry Events](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/0de95fcbb7cb464d9296442f8ae506ca.html)
- [Sales Quotation Events](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/b88e434cb6424766a0e776f18aeefcc1.html)

---

## Sales Contract (OData V2)

| Property | Value |
|----------|-------|
| **Protocol** | OData V2 (A2X, Synchronous) |
| **Doc URL** | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/bc2d6c95d98e4b96ae70e7db2de4cca1.html) |

---

## Sales Contract (OData V4)

| Property | Value |
|----------|-------|
| **Service Group** | `API_SalesContract` |
| **Repository ID** | `srvd_a2x` |
| **Service Name** | `SalesContract` |
| **Version** | `0001` |
| **Protocol** | OData V4 (A2X, Sync + Async) |
| **API Monitoring Namespace** | `/SDSLS` |
| **Recipient** | `SDSLS_CONTR_ODATA_IN_RECIPIENT` |
| **Doc URL** | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/a6aeba736a2b4a51a0b296b1e1d3dd96.html) |

### Entity Types

| Entity | Description |
|--------|-------------|
| `SalesContract` | Full sales contract data |
| `SalesContractPartner` | Header partner functions (e.g., ship-to party) |
| `SalesContractText` | Header texts/notes |
| `SlsContrPricingElement` | Header pricing (prices, discounts, surcharges, freight, taxes) |
| `SalesContractItem` | Items with quantity/product |
| `SalesContractItemPartner` | Item-level partners (specific + inherited from header) |
| `SalesContractItemText` | Item-level texts |
| `SlsContrItemPricingElement` | Item-level pricing |

**Operations:** Create, Read, Update, Delete (single entities like items)

### HTTP Headers

| Header | Value | Purpose |
|--------|-------|---------|
| `prefer` | `return=representation` | Full response (all entities/properties) |
| `prefer` | `return=minimal` | Minimal response (key only in header) |
| `prefer` | `respond-async` | Async processing; response `location` header has polling URL |
| `If-Match` | ETag value | Required for all change operations (optimistic concurrency) |

**Authentication:** Basic, OAuth 2.0, X.509

### Constraints

- Cannot delete sales contracts (full document)
- Cannot CRUD partners with function AA or AW at item level
- Cannot use variant configuration (AVC) entities
- Cannot use `SalesPriceAgreement` / `SalesPriceAgreementScale` entities
- Cannot process multiple contracts in single `$batch` changeset
- Max 1 PATCH per changeset

### Event APIs

- [Sales Contract Events](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/6656517072844177a2a724bf229b0a85.html)
- [Sales Scheduling Agreement Events](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/ec0e83cc24f14cc786f8c0a500a1b6ad.html)

---

## Sales Scheduling Agreement

| Property | Value |
|----------|-------|
| **Technical Name** | `API_SALES_SCHEDULING_AGREEMENT` |
| **Service URL** | `/sap/opu/odata/SAP/API_SALES_SCHEDULING_AGREEMENT` |
| **Metadata** | `/sap/opu/odata/SAP/API_SALES_SCHEDULING_AGREEMENT/$metadata` |
| **Protocol** | OData (A2X, Synchronous) |
| **Doc URL** | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/904b06b7cbb84ce48e7f71c58db856e0.html) |

### Entity Types

| Entity | Type Name | Operations |
|--------|-----------|------------|
| Header | `A_SalesSchedgAgrmt` | CRUD + Release/Reject |
| Header Partner | `A_SalesSchedgAgrmtPartner` | Deep insert only (create) |
| Header Pricing Element | `A_SalesSchedgAgrmtPrcgElement` | Deep insert only (create) |
| Header Text | `A_SalesSchedgAgrmtText` | Deep insert only (create) |
| Item | `A_SalesSchedgAgrmtItem` | CRUD + Create correction deliveries |
| Item Partner | `A_SalesSchedgAgrmtItemPartner` | Deep insert only (create) |
| Item Pricing Element | `A_SalesSchedgAgrmtItmPrcgElmnt` | Deep insert only (create) |
| Item Text | `A_SalesSchedgAgrmtItemText` | Deep insert only (create) |
| Delivery Schedule | `A_SalesSchedgAgrmtDeliverySchedule` | **GET only** |
| Schedule Line | `A_SalesSchedgAgrmtSchedLine` | **GET only** |

**Operations:** Create, Read, Update, Delete, Release, Reject, Create Correction Deliveries

**Authorization Objects:** `V_VBAK_AAT`, `V_VBAK_VKO`, `S_SERVICE`

### Constraints

- Header partner/pricing/text only via deep insert (no individual create)
- Cannot CUD delivery schedules or schedule lines
- No subentity filter search
- No multiple scheduling agreements in single `$batch` changeset
- BAdIs: `Sales Document Check Before Save`, `Sales Header Check`, `Sales Item Check`

### Related B2B APIs

| API Name | Doc URL |
|----------|---------|
| Delivery Schedule of Sales Scheduling Agreement - Receive, Update (B2B) | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/837a0869882f4344b121f26e0adf144f.html) |
| Consignment Issue for Sales Scheduling Agreement - Create (B2B) | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/03f667c2706f4a869d1424ea8d3ef69c.html) |
| Sold-to Party Assignment - Read (A2X) | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/19e224a14b034a4798e08bddafd2fe78.html) |

---

## Sales Order (OData V4)

| Property | Value |
|----------|-------|
| **Service Group** | `API_SalesOrder` |
| **Repository ID** | `srvd_a2x` |
| **Service Name** | `SalesOrder` |
| **Version** | `0001` |
| **Protocol** | OData V4 (A2X, Sync + Async) |
| **API Monitoring Namespace** | `/SDSLS` |
| **Recipient** | `SDSLS_SO_ODATA_IN_RECIPIENT` |
| **Architecture** | RAP (ABAP RESTful Application Programming Model) |
| **Related App** | Manage Sales Orders - Version 2 |
| **Doc URL** | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/10ec8998a151440795e797cb098321bb.html) |

### Entity Types

| Entity | Description |
|--------|-------------|
| `SalesOrder` | Header -- data for entire sales order |
| `SalesOrderPartner` | Header partner functions (e.g., ship-to party) |
| `SalesOrderPricingElement` | Header pricing (prices, discounts, surcharges, freight, taxes) |
| `SalesOrderText` | Header texts (e.g., internal notes) |
| `SalesOrderItem` | Item -- quantity of product |
| `SalesOrderItemPartner` | Item partner (specific + inherited from header) |
| `SalesOrderItemPricingElement` | Item pricing |
| `SalesOrderItemText` | Item text |
| `SalesOrderScheduleLine` | Schedule line -- date/quantity splits for partial deliveries |
| `VariantConfiguration` | AVC product configuration node |
| `VariantConfigurationInstance` | Multi-level configuration instance |
| `VarConfignCharacteristic` | AVC characteristics (e.g., Color) |
| `VarConfignAssignedValue` | AVC assigned values (e.g., "blue") |

**Operations:** Create (deep insert), Read (with subentity filtering), Update, Delete (single entities)

### HTTP Headers

| Header | Value | Purpose |
|--------|-------|---------|
| `prefer` | `return=representation` | Full sync response |
| `prefer` | `return=minimal` | Minimal response (key only) -- better performance |
| `prefer` | `respond-async` | Async mode; polling URL in `location` header |
| `If-Match` | ETag | Optimistic concurrency for change operations |

**Authentication:** Basic, X.509, OAuth 2.0

### Constraints

- Cannot create/update/delete sales orders with processing type P (PBS) -- read only
- Cannot process SD document category I (sales order without charge)
- Cannot create with reference to another sales document
- Cannot process multiple sales orders in single `$batch` changeset
- Max 1 PATCH per changeset
- Cannot delete full sales orders (only single entities like items)

---

## Sales Order (OData V2)

| Property | Value |
|----------|-------|
| **Protocol** | OData V2 (A2X, Synchronous) |
| **Doc URL** | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/00d244581efca007e10000000a441470.html) |

---

## Sales Order (SOAP A2A)

| Property | Value |
|----------|-------|
| **Technical Name** | `SalesOrderBulkRequest_In` |
| **Namespace** | `http://sap.com/xi/SD-SLS` |
| **Protocol** | SOAP (A2A, Asynchronous) |
| **Bulk-Enabled** | Yes (Sales Order node can occur multiple times) |
| **Messaging** | WSRM or SAP Plain SOAP (reliable messaging) |
| **AIF Namespace** | `/SDSLS` |
| **AIF Recipient** | `SDSLS_SO_BULK_IN_RECIPIENT` |
| **AIF Deployment Scenario** | `SAP_COM_0288` |
| **Monitoring** | Transaction `/AIF/ERR` (AIF) or `SRT_MONI` (SOAP) |
| **ICF Activation** | Transaction `SICF` (inactive by default) |
| **Doc URL** | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/2b2fd9fb158e4629bf9106c80dcbf7ff.html) |

### Message Header Fields

| Field | Description |
|-------|-------------|
| `ID` | SOAP message ID |
| `CreationDateTime` | Message creation timestamp |
| `SenderBusinessSystemID` | External system ID |

### Processing Notes

- Action Codes define operations for single nodes
- Complete Transmission Indicators (LCTIs) at parent level
- **No delta changes** -- complete message data required for every create/change
- Extended XML Handling enabled: omitted fields use system defaults
- To clear a field: provide field with no characters

**Authorization Objects:** `S_SERVICE`, `B_BUPA_GRP`, `C_STUE_BER`, `C_STUE_NOH`, `C_STUE_WRK`, `F_KNA1_BED`, `F_KNA1_GEN`, `F_LFA1_BEK`, `F_LFA1_GEN`, `K_KEKO`, `V_VBAK_AAT`, `V_VBAK_CCD`, `V_VBAK_VKO`, `/AIF/PROC`

**Authentication:** User ID/password (Username Token), X.509

### Constraints

- Cannot process SD document category I (sales order without charge)
- Cannot use: Header Billing Plan, Header Billing Plan Item, Item Billing Plan, Item Billing Plan Item nodes

**BAdIs:** `Sales Document Check Before Save`, `Sales Header Check`, `Sales Item Check`

---

## Other Sales Order APIs

| API Name | Type | Protocol | Doc URL |
|----------|------|----------|---------|
| Sales Order - Confirm Processing (A2A) | A2A | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/186082f3fb3b4f1ba12297f2d82639b0.html) |
| Sales Order - Send Processing Notification (A2A) | A2A | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/027c27eb8b264015b13323527a1a512d.html) |
| Sales Order - Send Error Log (A2A) | A2A | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/595fc12ed59f451c8a282f77809a1063.html) |
| Sales Order - Replicate (A2A) | A2A | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/fe62955cd8c34a489b0df6af8d36aa6a.html) |
| Sales Order/Customer Return - Create, Update, Cancel (B2B) | B2B | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/4261582b6ca44d008c72be11b9a400e2.html) |
| Sales Order/Customer Return - Confirm Processing (B2B) | B2B | SOAP | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/cf829dd7c1ef4eb08eca4575c2e518ff.html) |

---

## Sales Order Simulation

| Property | Value |
|----------|-------|
| **Technical Name** | `API_SALES_ORDER_SIMULATION_SRV` |
| **Service URL** | `/sap/opu/odata/SAP/API_SALES_ORDER_SIMULATION_SRV` |
| **Metadata** | `/sap/opu/odata/SAP/API_SALES_ORDER_SIMULATION_SRV/$metadata` |
| **Protocol** | OData (A2X, Synchronous) |
| **Doc URL** | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/b64937ce2692427594ee794ad033b8b3.html) |

### Entity Types

| Entity | Description |
|--------|-------------|
| `A_SalesOrderSimulation` | Header simulation |
| `A_SalesOrderPartnerSimulation` | Partner simulation |
| `A_SalesOrderPrcgElmntSimln` | Header price element simulation |
| `A_SalesOrderItemSimulation` | Item simulation |
| `A_SalesOrderItemPartnerSimln` | Item partner simulation |
| `A_SalesOrderItmPrcgElmntSimln` | Item price element simulation |
| `A_SalesOrderScheduleLineSimln` | Schedule line simulation |
| `A_SalesOrderCreditSimulation` | Credit limit check simulation |
| `A_SalesOrderPricingSimulation` | Pricing calculation simulation |

### Simulation Triggers (Associations)

| Association | Trigger |
|-------------|---------|
| `to_Pricing` | Price calculation (must include, otherwise no pricing data) |
| `to_ScheduleLine` | ATP check on item level |
| `to_Credit` | Credit limit check on header (pass empty association) |

**Key Behavior:** Simulated sales order is **not saved**.

**Authorization Objects:** `S_SERVICE`, `V_VBAK_AAT`, `V_VBAK_VKO`

### Constraints

- No processing type P (PBS)
- No SD document category I (without charge)
- No multiple orders in single `$batch` changeset
- Max 20 non-fatal messages per request

---

## Additional Sales Document APIs

| API Name | Type | Protocol | Doc URL |
|----------|------|----------|---------|
| Sales Document with Credit Block - Read, Check, Release, Reject (A2X) | A2X | OData | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/4f6bd74343554c3cbaa43df5ff34363d.html) |
| SD Document Order Reason - Read (A2X) | A2X | OData | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/84d3490179a44e11b6e285d359055186.html) |
| Intelligent Product Proposal - Read | A2X | OData | [Link](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/73122fae9acf4206a29b3ce0932d72d2.html) |

### Event APIs

- [Sales Order Events](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/78168e21723f4d58a631e3790a7f96b4.html)
- [Sales Document Mass Change Request Events](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/af4e455b1e5944c4b408feb83930da33.html)

**FAQ:** [Feature Comparison for Creating, Changing, and Displaying Sales Orders with APIs](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/7fac58721052484c8fe785be4669c97c.html)
