# FI-GL — General Ledger Configuration Guide

## Overview
General Ledger (FI-GL) is the foundation of SAP FICO. All financial transactions ultimately post to GL accounts. S/4HANA uses the **Universal Journal (ACDOCA)** which replaces 10+ ECC tables (BSEG, BSIS, BSAK, GLT0, FAGLFLEXT, COEP, etc.).

**Key S/4HANA Changes:**
- Single source of truth: ACDOCA
- Real-time financial reporting
- FI-CO reconciliation eliminated
- Document splitting mandatory
- Parallel ledgers built-in
- Embedded analytics via CDS views

---

## Configuration Roadmap (80 Steps Total)

### Phase 1: Enterprise Structure (Steps 1-7)
1. Define Company (OX15)
2. Define Company Code (OX02)
3. Assign Company ↔ Company Code (OX16)
4. Define Business Area (OX03)
5. Define Functional Area (OX10)
6. Define Fiscal Year Variant (OB29)
7. Define Posting Period Variant (OBBO)

### Phase 2: Chart of Accounts (Steps 8-12)
8. Define Chart of Accounts (OB13)
9. Assign CoA → Company Code (OB62)
10. Define Account Groups (OBD4)
11. Create GL Account Master (FS00)
12. Define Retained Earnings Account (OB53)

### Phase 3: Document Control (Steps 13-17)
13. Define Document Types (OBA7)
14. Define Posting Keys (OB41)
15. Define Field Status Variants (OBC4)
16. Define Number Ranges (FBN1)
17. Define Tolerance Groups (OBA4, OBA0)

### Phase 4: S/4HANA Universal Journal (Steps 18-20)
18. Configure Document Splitting (FAGL_SPLIT_CUST)
19. Define Parallel Ledgers (FINSC_LEDGER)
20. Assign Accounting Principles (FAGL_ACTIVATE_SAP_ACCOUNTING)

### Phase 5: Period Control (Steps 21-22)
21. Define Posting Period Variants (OBBO)
22. Open/Close Posting Periods (OB52)

---

## Detailed Configuration Steps

### 1. Define Company

**SPRO Path:** Enterprise Structure → Definition → Financial Accounting → Define Company

**Transaction:** `OX15`  
**IMG Activity:** `EC01`  
**Configuration Table:** `T880`

**Purpose:** Highest organizational unit for legal consolidation. A company can have multiple company codes.

**Prerequisites:** None - this is the starting point.

**Fields:**
- **Company (BUKRS)** [Required]: 4-char alphanumeric (e.g., `C001`)
- **Company Name** [Required]: Legal entity name (e.g., "Acme Corporation Ltd.")
- **Street/City/Country** [Optional]: Address information

**Step-by-Step:**
1. Execute transaction `OX15`
2. Click "New Entries"
3. Enter Company: `C001`
4. Enter Name: `Acme Corporation Ltd.`
5. Enter address details
6. Save (Ctrl+S)

**Example:**
```
Company: C001
Name: Acme Corporation Ltd.
City: New York
Country: US
```

**Testing:**
- Display company (OX15)
- Verify appears in assignment screen (OX16)

**Common Mistakes:**
❌ Using same code for Company and Company Code  
❌ Creating company after company codes  
✅ Create company first, plan structure

---

### 2. Define Company Code

**SPRO Path:** Enterprise Structure → Definition → Financial Accounting → Edit, Copy, Delete, Check Company Code

**Transaction:** `OX02`  
**IMG Activity:** `EC02`  
**Table:** `T001`

**Purpose:** Central organizational unit in FI. Every transaction posts to a company code. Represents independent accounting entity with own balance sheet and P&L.

**Prerequisites:** Company exists (OX15)

**Fields:**
- **Company Code (BUKRS)** [Required]: 4-char (e.g., `1000`)
- **Company Code Name** [Required]: Descriptive name
- **City** [Required]: Location
- **Country** [Required]: 2-char ISO code (US, IN, DE, GB, CN)
  - **CRITICAL:** Cannot change after transactions exist
  - Drives country-specific functionality
- **Currency** [Required]: Local currency (USD, INR, EUR, GBP, CNY)
  - **CRITICAL:** Cannot change after transactions exist
- **Language** [Required]: Default language (EN, DE, FR, JA, ZH)

**Step-by-Step:**
1. Transaction `OX02`
2. Click "New Entries"
3. Enter Company Code: `1000`
4. Enter all required fields
5. Save

**Example:**
```
Company Code: 1000
Name: Acme US Operations
City: New York
Country: US
Currency: USD
Language: EN
```

**Testing:**
- Display company code (OX02)
- Verify all fields populated
- Post test transaction (FB50) - verify CoCode 1000 available

**Common Mistakes:**
❌ Wrong currency - all transactions post in wrong currency  
❌ Wrong country - tax config incorrect  
❌ Forgetting to assign Chart of Accounts (OB62)  
✅ Triple-check Country and Currency

**Dependencies:**
- Assign to Company (OX16) - next step
- Assign Chart of Accounts (OB62)
- Assign Fiscal Year Variant (OB29 or in CoCode data)

---

### 8. Define Chart of Accounts

**SPRO Path:** Financial Accounting → General Ledger Accounting → Master Records → G/L Accounts → Preparations → Edit Chart of Accounts List

**Transaction:** `OB13`  
**Table:** `SKA1`

**Purpose:** Chart of Accounts (CoA) is the list of all GL accounts. Defines GL structure.

**Fields:**
- **Chart of Accounts (KTOPL)** [Required]: 4-char (e.g., `INT`, `US01`, `IN01`)
- **Description** [Required]: Name
- **Maintenance Language** [Required]: EN, DE, FR
- **Length of GL Account Number** [Required]: Max 10 digits
  - **CRITICAL:** Cannot change once accounts exist
- **Block Indicator** [Optional]: Usually unchecked

**Account Numbering Best Practices:**

**Range-Based Structure:**
```
100000-199999: Assets
  100000-109999: Current Assets (Cash, Bank, AR)
  110000-119999: Inventory
  120000-199999: Fixed Assets
200000-299999: Liabilities
  200000-209999: Current Liabilities (AP, Accruals)
  210000-299999: Long-term Liabilities
300000-399999: Equity
400000-499999: Revenue
500000-599999: Cost of Goods Sold
600000-699999: Operating Expenses
```

**Testing:**
- Display CoA (OB13)
- Assign to company code (OB62)
- Create GL account (FS00) - verify CoA appears

---

### 11. Create GL Account Master

**Transaction:** `FS00` (Create/Change/Display)  
**Tables:** `SKA1` (CoA segment), `SKB1` (Company Code segment)

**Purpose:** Define properties and behavior of each GL account.

**Two-Level Structure:**
1. **Chart of Accounts Segment (SKA1)** - Defined once
2. **Company Code Segment (SKB1)** - Company-specific

**Chart of Accounts Segment Fields:**
- **GL Account Number** [Required]: Up to 10 digits
- **Account Group** [Required]: Determines number range, field status
- **Short Text** [Required]: 20 characters
- **Long Text** [Optional]: 50 characters
- **P&L Statement Account Type** [Required if P&L]: Sales Revenue, Cost of Sales, Admin Expense
- **Account Type** [Required]: Balance Sheet or P&L

**Company Code Segment Fields:**
- **Currency** [Required]: Usually same as company code
- **Tax Category** [Required if tax-relevant]: Input Tax, Output Tax, Non-Taxable
- **Reconciliation Account** [Optional]: For subledger (customer/vendor)
- **Line Item Display** [Required]: ☑ for accounts needing line-item reporting
- **Open Item Management** [Optional]: ☑ for clearing accounts (GR/IR, customer, vendor)
- **Post Automatically Only** [Optional]: For automatic postings (tax, exchange rate)

**Example - Cash Account:**
```
CoA Segment:
- GL Account: 100100
- Account Group: BETR (Balance Sheet)
- Short Text: Cash in Hand
- Account Type: Balance Sheet - Asset

Company Code Segment:
- Company Code: 1000
- Currency: USD
- Tax Category: Not Tax Relevant
- Line Item Display: ☑
- Open Item Management: ☐
```

**Testing:**
- Display account (FS00)
- Post document (FB50) using account
- Display line items (FBL3N)

**Common Mistakes:**
❌ Line Item Display unchecked - cannot report line items  
❌ Wrong Tax Category - tax posting incorrect  
❌ Open Item Management checked unnecessarily - performance issue  
✅ Plan account properties before creation

---

### 18. Configure Document Splitting (S/4HANA MANDATORY)

**SPRO Path:** Financial Accounting (New) → General Ledger Accounting (New) → Business Transactions → Document Splitting

**Transaction:** `FAGL_SPLIT_CUST`  
**Table:** Various (T8G**, FAGL_SPLIT*)

**Purpose:** Document splitting ensures documents balance at Profit Center, Segment, or other dimensions. Enables real-time P&L by profit center without allocation runs.

**Key Concepts:**
- **Zero Balance:** Document must balance by company code AND by profit center/segment
- **Splitting Characteristics:** Profit Center, Segment, Business Area
- **Splitting Method:** 001 (standard) or custom

**Configuration Steps:**
1. **Activate Document Splitting:**
   - SPRO → Document Splitting → Activate Document Splitting
   - Select Company Code
   - Activate flag

2. **Define Document Splitting Characteristics:**
   - Standard: Profit Center, Segment
   - Optional: Business Area, Functional Area

3. **Classify GL Accounts:**
   - Balance Sheet accounts: Asset, Liability, Equity
   - P&L accounts: Expense, Revenue
   - Transaction: FAGL_ACCOUNT_CLASSIFICATION

4. **Define Zero Balance Clearing Account:**
   - For incomplete assignments
   - Temporary clearing during posting

5. **Define Splitting Rules:**
   - Standard rules usually sufficient
   - Custom rules for complex scenarios

6. **Test Extensively:**
   - Every transaction type
   - Cross-profit center postings
   - Verify zero balance by profit center

**Example Scenario:**
```
Posting: Salary Expense
Line 1: Debit Salary Expense 100000 (Profit Center PC01)
Line 2: Debit Salary Expense 50000 (Profit Center PC02)
Line 3: Credit Bank 150000 (No PC assigned)

Document Splitting:
System auto-splits Line 3:
- Credit Bank 100000 (PC01)
- Credit Bank 50000 (PC02)

Result: Document balances by CoCode AND by each PC
```

**Testing:**
- Post cross-PC transaction (FB50)
- Display document (FB03)
- Verify splitting occurred
- Run PC balance sheet (S_ALR_87013611)

**Common Issues:**
❌ Accounts not classified - splitting fails  
❌ Clearing account not defined - posting error  
❌ Incompatible profit center assignments  
✅ Test EVERY business transaction type

---

### 19. Define Parallel Ledgers (S/4HANA)

**SPRO Path:** Financial Accounting (New) → General Ledger Accounting (New) → Ledgers → Ledger → Define Ledgers for General Ledger Accounting

**Transaction:** `FINSC_LEDGER`

**Purpose:** Parallel ledgers allow multiple accounting principles (IFRS, Local GAAP, Tax) in one system.

**Standard Ledgers:**
- **0L:** Leading Ledger (e.g., IFRS)
- **2L:** Non-Leading Ledger (e.g., Local GAAP)
- **3L:** Non-Leading Ledger (e.g., Tax)

**Configuration:**
1. Define Ledgers
2. Assign Accounting Principles (IFRS, US-GAAP, Local GAAP)
3. Define Ledger Groups
4. Assign Fiscal Year Variants per Ledger
5. Configure Parallel Valuation (if needed)

**Use Cases:**
- IFRS for group reporting
- Local GAAP for statutory reporting
- Tax basis for tax returns
- Management accounting (internal)

---

### 22. Open/Close Posting Periods

**Transaction:** `OB52`  
**Table:** `T001B`

**Purpose:** Controls which periods are open for posting by account type.

**Configuration:**
```
Company Code: 1000
From Period: 001 / To Period: 003 (Jan-Mar open)
From Account: + / To Account: + (all accounts)
Account Type: + (all types: A=Asset, D=Customer, K=Vendor, M=Material, S=GL)
```

**Testing:**
- Post in open period → Success
- Post in closed period → Error "Posting period is not open"

---

## Advanced Topics

### Foreign Currency Valuation

**Transaction:** `FAGL_FC_VAL`

Revalue open foreign currency items at period-end:
- Balance sheet accounts (OB09)
- Open item accounts (OB10)

### Universal Journal (ACDOCA) Architecture

**ECC vs S/4HANA:**
| Feature | ECC | S/4HANA |
|---------|-----|---------|
| Tables | BSEG, BSIS, BSAK, GLT0, FAGLFLEXT, COEP | **ACDOCA only** |
| FI-CO Recon | Required (KALC) | **Eliminated** |
| Reporting | Multiple tables | Single table (faster) |
| Real-time | No | Yes |

**ACDOCA Key Fields:**
- RBUKRS - Company Code
- GJAHR - Fiscal Year
- BELNR - Document Number
- DOCLN - Line Item
- RACCT - Account Number
- PRCTR - Profit Center
- SEGMENT - Segment
- HSLVT - Amount in Local Currency
- HSLBT - Amount in Group Currency

---

## Quick Reference

### Critical Transactions
| T-Code | Description | When to Use |
|--------|-------------|-------------|
| OX15 | Define Company | First step |
| OX02 | Define Company Code | Second step |
| OB13 | Chart of Accounts | Before GL accounts |
| FS00 | GL Account Master | Create accounts |
| OBA7 | Document Types | Before posting |
| OB52 | Open/Close Periods | Period control |
| FAGL_SPLIT_CUST | Document Splitting | S/4HANA mandatory |
| FB50 | Post Journal Entry | Manual posting |
| FB03 | Display Document | Verify postings |
| FBL3N | GL Line Items | Reporting |

### Configuration Tables
| Table | Description | Key Data |
|-------|-------------|----------|
| T880 | Company | Legal entities |
| T001 | Company Code | Accounting units |
| SKA1 | GL Master (CoA) | Account definitions |
| SKB1 | GL Master (CoCode) | Company-specific |
| T003 | Document Types | Doc control |
| ACDOCA | Universal Journal | All postings (S/4HANA) |

---

This concludes FI-GL configuration. See separate files for FI-AP, FI-AR, FI-AA, CO modules.
