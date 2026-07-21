# SAP BW Business Database - Schema and Scenario Documentation

## Business Scenario Overview

The mock data represents a **multinational manufacturing corporation** with headquarters in Germany and subsidiaries in the US and UK. The company sells hardware products, software licenses, and professional services.

### Corporate Structure

```
CORP (Group/Consolidated Entity)
├── 1000 - TechCorp GmbH (Germany - HQ)
│   ├── Segment: SEG01 (EMEA Operations)
│   ├── Profit Center: PC1001
│   ├── Local Currency: EUR
│   └── Products: Hardware (PROD_A), Software (PROD_B)
│
├── 2000 - TechCorp Inc (USA)
│   ├── Segment: SEG02 (Americas Operations)
│   ├── Profit Center: PC2001
│   ├── Local Currency: USD
│   └── Products: Hardware (PROD_A)
│
└── 3000 - TechCorp Ltd (UK)
    ├── Segment: SEG03 (UK Operations)
    ├── Profit Center: PC3001
    ├── Local Currency: GBP
    └── Products: Services (PROD_C)
```

### Data Flow Architecture

```
┌─────────────────┐    ┌─────────────────────┐    ┌─────────────────┐
│  fi_reporting   │───▶│ consolidation_mart  │───▶│  bpc_reporting  │
│  (Transactional)│    │   (Aggregated)      │    │  (Consolidated) │
└─────────────────┘    └─────────────────────┘    └─────────────────┘
     FI Module              BW Aggregation           BPC Reporting
   Line-item detail      IC eliminations           Group currency
   Document level        Segment rollups           Final reports
```

---

## Reference Master Data

Use these values consistently when adding new tables or extending seed data.

### Company Codes (ZCOMPCODE)

| Code | Name | Country | Currency | Segment | Profit Center | Controlling Area |
|------|------|---------|----------|---------|---------------|------------------|
| 1000 | TechCorp GmbH | Germany | EUR | SEG01 | PC1001 | 1000 |
| 2000 | TechCorp Inc | USA | USD | SEG02 | PC2001 | 2000 |
| 3000 | TechCorp Ltd | UK | GBP | SEG03 | PC3001 | 3000 |
| CORP | Group Entity | - | EUR | GROUP | - | - |

### Chart of Accounts (ZCHRT_ACS: CAGR)

| Range | Category | Examples |
|-------|----------|----------|
| 0100000-0199999 | Assets | Fixed assets, Accumulated depreciation |
| 0900000 | Accum. Depreciation | Counter account for depreciation |
| 1300000 | Inventory | Stock accounts |
| 1400000 | Accounts Receivable | Customer receivables |
| 1410000 | IC Receivables | Intercompany receivables |
| 2000000 | Accounts Payable | Vendor payables |
| 2100000 | Bank/Cash | Cash and bank accounts |
| 4000000 | Revenue | External sales revenue |
| 4100000 | IC Revenue | Intercompany sales |
| 5000000 | COGS | Cost of goods sold |
| 5100000 | IC COGS | Intercompany cost of goods |
| 6100000 | R&D Expenses | Research and development |
| 6200000 | Personnel | Salaries and wages |
| 6300000 | Operating Expenses | General operating costs |
| 6400000 | Depreciation | Depreciation expense |
| 7000000 | FX Adjustments | Currency translation |
| 7100000 | Consolidation Adj | Consolidation adjustments |

### Group Accounts (ZGRPACCT)

| Code | Description | Maps to GL |
|------|-------------|------------|
| G4000000 | Group Revenue | 4000000 |
| G4100000 | Group IC Revenue | 4100000 |
| G5000000 | Group COGS | 5000000 |
| G5100000 | Group IC COGS | 5100000 |
| G6100000 | Group R&D | 6100000 |
| G6200000 | Group Personnel | 6200000 |
| G6300000 | Group OpEx | 6300000 |
| G6400000 | Group Depreciation | 6400000 |
| G7000000 | Group FX Adj | 7000000 |
| G7100000 | Group Cons Adj | 7100000 |

### Functional Areas (ZFUNCAREA)

| Code | Description |
|------|-------------|
| SALES | Sales & Distribution |
| COGS | Cost of Goods Sold |
| ADMIN | General Administration |
| RND | Research & Development |
| FIN | Finance & Treasury |

### Product Hierarchy

| Level 1 (ZPRODH1) | Level 2 (ZPRODH2) | Description |
|-------------------|-------------------|-------------|
| PROD_A | HARDWARE | Physical products |
| PROD_B | SOFTWARE | Software licenses |
| PROD_C | SERVICES | Professional services |

### Customers (ZCUSTOMER)

| Code | Name | Company | Region |
|------|------|---------|--------|
| CUST001 | Acme Corp | 1000 | EMEA |
| CUST002 | Beta Industries | 1000 | EMEA |
| CUST100 | Delta Systems | 2000 | Americas |
| CUST200 | Epsilon Ltd | 3000 | UK |

### Vendors (ZVENDOR)

| Code | Name | Company | Type |
|------|------|---------|------|
| VEND001 | Supplier One | 1000 | Materials |
| VEND002 | Office Supplies Co | 1000 | Services |
| VEND100 | US Parts Inc | 2000 | Materials |

### Materials (ZMATERIAL)

| Code | Description | Product Hierarchy | Unit |
|------|-------------|-------------------|------|
| MAT001 | Product A - Standard | PROD_A/HARDWARE | PC |
| MAT002 | Product B - Premium | PROD_B/SOFTWARE | PC |
| MAT003 | Service Package | PROD_C/SERVICES | HR |

### Versions (ZVERSION)

| Code | Description | Purpose |
|------|-------------|---------|
| ACTUAL | Actual Data | Posted FI transactions |
| BUDGET | Annual Budget | Approved annual plan |
| FORECAST | Rolling Forecast | Updated projections |

### Fiscal Periods (0FISCPER)

Format: `YYYYPPP` where PPP is period (001-012 for monthly)

| Period | Description |
|--------|-------------|
| 2024001 | January 2024 |
| 2024002 | February 2024 |
| 2024003 | March 2024 |
| ... | ... |
| 2024012 | December 2024 |

### Fiscal Year Variant (0FISCVARNT)

| Code | Description |
|------|-------------|
| K4 | Calendar Year (Jan-Dec) |

### Document Types (ZAC_DOCTP)

| Code | Description |
|------|-------------|
| DR | Customer Invoice |
| KR | Vendor Invoice |
| SA | G/L Account Document |
| AF | Asset Posting (Depreciation) |
| AB | Accounting Document (Accruals) |

### Debit/Credit Indicator (ZFIDBCRIN)

| Code | Description |
|------|-------------|
| S | Debit (Soll) |
| H | Credit (Haben) |

### BPC Data Sources (ZBPC_SRC / ZDSOURCE)

| Code | Description |
|------|-------------|
| FI | Financial Accounting data |
| CO | Controlling data |
| BP | BPC Planning input |
| FC | Forecast data |
| FI_DATA | FI transactional data |
| CO_DATA | Controlling allocations |
| BPC_PLAN | BPC planning entries |
| BPC_FCST | BPC forecast entries |
| MANUAL | Manual adjustments |

### Specifications (ZSPEC)

| Code | Description |
|------|-------------|
| REV | Revenue |
| COGS | Cost of Goods Sold |
| OPEX | Operating Expenses |
| IC_REV | Intercompany Revenue |
| IC_COGS | Intercompany COGS |
| IC_ELIM | IC Elimination Entry |
| PERSONNEL | Personnel Costs |
| DEPR | Depreciation |
| FX_ADJ | FX Adjustment |
| CONS_ADJ | Consolidation Adjustment |

### PC Areas (ZPC_AREA / ZPPC_AREA)

| Code | Description |
|------|-------------|
| EMEA | Europe, Middle East, Africa |
| AMER | Americas |
| GROUP | Consolidated Group |

### Scopes (ZSCOPE)

| Code | Description |
|------|-------------|
| CONSOL | Consolidated reporting |
| PLAN | Planning scope |
| FCST | Forecast scope |

---

## Sample Business Transactions

### 1. External Customer Sale (Company 1000)

Company 1000 sells 500 units of Product A to customer CUST001 for €125,000:

**fi_reporting entries:**
- Line 1: Debit Revenue (4000000) €125,000
- Line 2: Credit AR (1400000) €125,000
- Line 3: Debit COGS (5000000) €75,000
- Line 4: Credit Inventory (1300000) €75,000

### 2. Intercompany Sale (1000 → 2000)

HQ sells 200 units to US subsidiary at €50,000:

**fi_reporting (Company 1000):**
- Debit IC Revenue (4100000) €50,000
- Credit IC AR (1410000) €50,000

**consolidation_mart:**
- IC Revenue entry with partner company 2000
- IC Elimination entry (spec: IC_ELIM) reversing the IC transaction

### 3. Operating Expenses

Monthly salary posting for Company 1000:

**fi_reporting:**
- Debit Personnel (6200000) €45,000
- Credit Bank (2100000) €45,000

### 4. Currency Translation

US subsidiary revenue translated from USD to EUR (group currency):
- Local: $95,000 USD
- Group: €86,363.64 EUR (rate ~1.10)

---

## Adding New Tables

When creating additional tables, ensure consistency by:

1. **Use the same company codes**: 1000, 2000, 3000, CORP
2. **Use the same fiscal periods**: 2024001-2024012
3. **Use the same versions**: ACTUAL, BUDGET, FORECAST
4. **Reference existing master data**: customers, vendors, materials, GL accounts
5. **Maintain intercompany relationships**: Partner fields should reference valid company codes
6. **Use consistent currencies**: EUR (1000, group), USD (2000), GBP (3000)

---

# Table Definitions

# Database Table **fi_reporting** Fields

## Characteristics / Dimensions

| Field Name | Description | Data Type | Length | Key |
|------------|-------------|-----------|--------|-----|
| ZCUSTPSG | Customer from PSG | CHAR | 10 | |
| ZREF_KEY | Reference Key | CHAR | 20 | |
| ZBILL_NUM | Billing document | CHAR | 10 | |
| ZSALESORG | Sales Organization | CHAR | 4 | |
| ZDIVISION | Division | CHAR | 2 | |
| ZDISTCHAN | Distribution Channel | CHAR | 2 | |
| ZMEREVOPA | Profitability Segment (CO-PA) | NUMC | 10 | |
| ZASGN_NO | Assignment number | CHAR | 18 | |
| ZACLEDGER | Ledger | CHAR | 2 | ✓ (4) |
| ZAC_DOCNR | Document Number (General Ledger View) | CHAR | 10 | ✓ (5) |
| ZRECTYPE | Record Type | CHAR | 1 | ✓ (6) |
| ZVERSION | Version | CHAR | 10 | ✓ (7) |
| 0FISCPER | Fiscal year / period | NUMC | 7 | ✓ (1) |
| ZAC_DOCLN | Line Item (General Ledger View) | CHAR | 6 | ✓ (3) |
| 0FISCVARNT | Fiscal year variant | CHAR | 2 | ✓ (2) |
| ZCOMPCODE | Company Code | CHAR | 4 | ✓ (8) |
| ZPST_DATE | Posting Date in the Document | DATS | 8 | |
| 0CALYEAR | Calendar Year | NUMC | 4 | |
| 0CALQUARTER | Calendar Year/Quarter | NUMC | 5 | |
| 0CALMONTH | Calendar Year/Month | NUMC | 6 | |
| 0FISCYEAR | Fiscal year | NUMC | 4 | |
| ZITEM_NUM | Number of line item within accounting document | NUMC | 3 | |
| ZCHRT_ACS | Chart of accounts | CHAR | 4 | |
| ZGL_ACCT | G/L Account | CHAR | 10 | |
| ZAC_DOCNO | Accounting document number | CHAR | 10 | |
| ZDOC_DATE | Document Date | DATS | 8 | |
| ZMOVE_TP | Movement Type | CHAR | 3 | |
| ZAC_DOCTP | FI Document type | CHAR | 2 | |
| ZPROF_CTR | Profit center | CHAR | 10 | |
| ZSEGMENT | Segment for Segmental Reporting | CHAR | 10 | |
| ZPCOMPANY | Partner Company | CHAR | 6 | |
| ZPCOMPCD | Company code of partner | CHAR | 4 | |
| ZPSEGMENT | Partner Segment for Segmental Reporting | CHAR | 10 | |
| ZPOSTXT | Item Text | CHAR | 60 | |
| ZDOCHDTXT | Document Text | CHAR | 25 | |
| ZNDCOSTMR | Non-deductible costs marker | CHAR | 10 | |
| ZCO_AREA | Controlling area | CHAR | 4 | |
| ZCOORDER | Order Number | CHAR | 12 | |
| ZPRODLINE | Production Line | CHAR | 8 | |
| ZFUNCAREA | Functional area | CHAR | 16 | |
| ZCUSTOMER | Customer | CHAR | 10 | |
| ZPLANT | Plant | CHAR | 5 | |
| ZSORD_ITM | Sales document item | NUMC | 6 | |
| ZDOC_NUMB | Sales Document | CHAR | 10 | |
| ZMATERIAL | Material | CHAR | 18 | |
| ZBWTAR | Valuation type | CHAR | 10 | |
| ZPART_PC | Partner profit center | CHAR | 10 | |
| ZCOSTCTR | Cost Center | CHAR | 10 | |
| ZCOSTELMT | Cost Element | CHAR | 10 | |
| ZFI_XBLNR | Reference document number | CHAR | 16 | |
| ZREF_DOCN | Reference document number | CHAR | 16 | |
| ZREF_CLNN | Reference cleaning number | CHAR | 16 | |
| ZFIDBCRIN | Debit/Credit Indicator | CHAR | 1 | |
| ZWBS_ELMT | Work Breakdown Structure Element (WBS Element) | CHAR | 24 | |
| ZNETWORK | Network | CHAR | 12 | |
| ZVENDOR | Vendor | CHAR | 10 | |
| ZOI_EBELN | Purchasing document number | CHAR | 10 | |
| ZOI_EBELP | Item number of purchasing document | NUMC | 5 | |
| ZCLRDOCNO | Clearing Document Number | CHAR | 10 | |
| ZCLR_DATE | Clearing date | DATS | 8 | |

## Key Figures

| Field Name | Description | Data Type | Length | Aggregation |
|------------|-------------|-----------|--------|-------------|
| 0CS_TRN_QTY | Periodic quantity | QUAN | 17:3 | SUM |
| 0CURKEY_LC | Currency Key for Local Currency | CUKY | 5 | |
| 0CS_TRN_LC | Period Value in Local Currency | CURR | 17:2 | SUM |
| ZAMNT_DC | Amount in document currency | CURR | 17:2 | SUM |
| 0DOC_CURRCY | Document currency | CUKY | 5 | |
| 0QUANTITY | Quantity | QUAN | 17:3 | SUM |
| 0UNIT | Unit of Measure | UNIT | 3 | |


# Database Table **consolidation_mart** Fields

## Characteristics

| Field Name | Description | Data Type | Length |
|------------|-------------|-----------|--------|
| ZPCOMPCD | Company code of partner | CHAR | 4 |
| ZVERSION | Version | CHAR | 10 |
| 0FISCPER | Fiscal year / period | NUMC | 7 |
| 0FISCVARNT | Fiscal year variant | CHAR | 2 |
| ZCOMPCODE | Company Code | CHAR | 4 |
| ZPCOMPANY | Partner Company | CHAR | 6 |
| ZGRPACCT | Group Account | CHAR | 10 |
| ZPC_AREA | PC Area | CHAR | 20 |
| ZPPC_AREA | Partner PC Area | CHAR | 20 |
| ZCHRT_ACS | Chart of accounts | CHAR | 4 |
| ZGL_ACCT | G/L Account | CHAR | 10 |
| ZSPEC | Specifications | CHAR | 10 |
| ZMOVE_TP | Movement Type | CHAR | 3 |
| ZPROF_CTR | Profit center | CHAR | 10 |
| ZSEGMENT | Segment for Segmental Reporting | CHAR | 10 |
| ZPSEGMENT | Partner Segment for Segmental Reporting | CHAR | 10 |
| ZPRODH1 | Product hierarchy level 1 | CHAR | 18 |
| ZPRODH2 | Product hierarchy level 2 | CHAR | 18 |
| ZCO_AREA | Controlling area | CHAR | 4 |
| ZFUNCAREA | Functional area | CHAR | 16 |
| ZBWTAR | Valuation type | CHAR | 10 |
| ZPART_PC | Partner profit center | CHAR | 10 |
| ZBPC_SRC | Source of data for BPC Mart (technical) | CHAR | 2 |

## Key Figures

| Field Name | Description | Data Type | Length | Aggregation |
|------------|-------------|-----------|--------|-------------|
| 0CS_YTD_QTY | Cumulative Quantity | QUAN | 17:3 | SUM |
| 0CS_TRN_QTY | Periodic quantity | QUAN | 17:3 | SUM |
| 0UNIT | Unit of Measure | UNIT | 3 | |
| 0CS_YTD_LC | Cumulative (YTD) Value in Local Currency | CURR | 17:2 | SUM |
| 0CS_TRN_LC | Period Value in Local Currency | CURR | 17:2 | SUM |
| 0CURKEY_LC | Currency Key for Local Currency | CUKY | 5 | |


# Database Table **bpc_reporting** Fields

## Characteristics

| Field Name | Description | Data Type | Length |
|------------|-------------|-----------|--------|
| ZVERSION | Version | CHAR | 10 |
| ZSCOPE | Scope | CHAR | 10 |
| ZPC_AREA | PC Area | CHAR | 20 |
| ZCOMPCODE | Company Code | CHAR | 4 |
| ZPPC_AREA | Partner PC Area | CHAR | 20 |
| ZPCOMPCD | Company code of partner | CHAR | 4 |
| ZGRPACCT | Group Account | CHAR | 10 |
| ZFUNCAREA | Functional area | CHAR | 16 |
| ZSPEC | Specifications | CHAR | 10 |
| ZDSOURCE | Data Source | CHAR | 30 |
| 0FISCPER | Fiscal year / period | NUMC | 7 |
| 0FISCVARNT | Fiscal year variant | CHAR | 2 |

## Key Figures

| Field Name | Description | Data Type | Length | Aggregation |
|------------|-------------|-----------|--------|-------------|
| 0CS_TRN_LC | Period Value in Local Currency | CURR | 17:2 | SUM |
| 0CS_TRN_GC | Period Value in Group Currency | CURR | 17:2 | SUM |
