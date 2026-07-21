# SAP S/4HANA FICO Implementation Skill - Framework Guide

This document explains how to expand the skill with additional modules, localizations, and integrations.

---

## Reference File Structure Standard

Every reference file should follow this template:

### Module Reference Files (references/fi-modules/, references/co-modules/)

```markdown
# [Module Name] — [Full Name] Configuration Guide

## Overview
[1-2 paragraphs: What is this module, business purpose, when used]

## L1-L5 Business Capabilities Covered
[List the SAP business capability hierarchy this module addresses]

Example:
- **L4:** General Ledger Accounting
  - **L5:** Capture Source Transactions
  - **L5:** Create Chart of Accounts
  [...]

## Configuration Steps (End-to-End)

### 1. [Config Step Name]

**SPRO Path:**  
[Full menu path from SAP Customizing Implementation Guide]

**Transaction Code:** `[T-CODE]`

**IMG Activity:** `[IMG_CODE]` (if applicable)

**Configuration Table:** `[TABLE_NAME]`

**Purpose:**  
[What this config does, when it's needed, business context]

**Prerequisites:**
[What must be configured first - with transaction codes]

**Fields:**
- **[Field Name] (Field Technical Name)** [Required/Optional]: [What it does, example values, impact]
- **[Field Name]** [Required/Optional]: [...]

**Step-by-Step Instructions:**
1. Navigate to transaction `[T-CODE]`
2. [Action with screenshot placeholder marker]
3. Fill in fields:
   - **[Field]**: [Value]
4. Save

**Example Configuration:**
```
[Show realistic example with actual values]
```

**Testing:**
- **Unit Test:**
  1. [How to verify this config]
  2. Transaction: `[T-CODE]`
  3. Expected result: [What you should see]

- **Integration Test:** [If applicable - end-to-end scenario]

**Dependencies:**
- **Depends on:** [Prior config with T-code]
- **Affects:** [Downstream config]
- **Used in:** [Business processes that rely on this]

**Common Mistakes:**
- ❌ [Mistake 1]
- ❌ [Mistake 2]
- ✅ Best practice: [...]

**Troubleshooting:**
| Issue | Cause | Solution |
|-------|-------|----------|
| [Error message] | [Root cause] | [Fix with T-code] |

**S/4HANA Specifics:**
[Any differences from ECC, new features, deprecated functions]

---

[Repeat for each major config step in sequence]

## Advanced Configurations

### [Niche Scenario 1]
[How to handle complex requirements]

### [Niche Scenario 2]
[...]

## Country-Specific Considerations
[If module has localization aspects]

## Integration Points
[How this module integrates with others - with T-codes]

## Performance Considerations
[Volume thresholds, indexing, archiving]

## Maintenance & Support
[Common support issues, how to troubleshoot]

## Quick Reference

### Transaction Codes Summary
| T-Code | Description | Purpose |
|--------|-------------|---------|
| [CODE] | [Name] | [When to use] |

### Configuration Tables
| Table | Description | Key Fields |
|-------|-------------|------------|
| [TABLE] | [Purpose] | [Primary keys] |

---

This concludes the [Module Name] configuration guide.
```

---

## Integration Reference Files (references/integrations/)

```markdown
# [Module A]-[Module B] Integration Guide

## Overview
[What data flows between modules, business scenarios]

## Integration Points (L5 Level)

### Integration Point 1: [Name]
**Business Scenario:** [When this happens]

**Data Flow:** [Module A] → [Module B]

**Transaction Codes:**
- Source: `[T-CODE]` in [Module A]
- Destination: `[T-CODE]` in [Module B]

**Configuration Required:**

#### Step 1: [Config Activity]
**SPRO Path:** [...]
**Transaction:** `[T-CODE]`
**Table:** `[TABLE]`

[Full config instructions]

#### Step 2: [...]

**Testing:**
1. Create test transaction in [Module A]
2. Verify automatic posting in [Module B]
3. Check GL document (FB03)
4. Verify account determination

**Troubleshooting:**
[Common integration errors]

---

[Repeat for each integration point]

## Automatic Account Determination
[Detailed table-by-table config]

## End-to-End Test Scenarios
[Complete business process flows]

## Common Issues
[Typical problems with solutions]
```

---

## Localization Reference Files (references/localizations/)

### Detailed Country Files (Top 10)

```markdown
# [Country Name] Localization Guide

## Overview
[Country-specific regulatory requirements, tax system, statutory reporting]

## Legal & Regulatory Context
- **Tax Authority:** [Name]
- **Tax Types:** [VAT, Income Tax, WHT, etc.]
- **Fiscal Year:** [Standard calendar or variant]
- **Statutory Reports:** [Required reports]
- **E-Filing Requirements:** [Yes/No, system]

## Configuration Steps

### 1. Tax Configuration

#### 1.1 Tax Procedure Setup
**SPRO Path:** [Country-specific path]
**Transaction:** `OBYZ`, `FTXP`
**Table:** `T007S`, `T001`, `T007V`

[Detailed setup]

#### 1.2 Tax Codes
**Transaction:** `FTXP`

[Table of tax codes with rates]

### 2. Withholding Tax (if applicable)

[Configuration steps]

### 3. Country-Specific GL Accounts

[Required statutory accounts]

### 4. Statutory Reporting

[How to generate required reports]

### 5. E-Filing Integration

[API connections, file formats]

## Business Process Examples

### Example 1: [Vendor Invoice with Tax]
[Step-by-step with screenshots markers]

### Example 2: [...]

## Compliance Checklist
☐ [Requirement 1]
☐ [Requirement 2]
[...]

## SAP Notes
[Relevant SAP Notes for this country]

## External References
[Links to tax authority websites, documentation]
```

### Localization Framework (For other countries)

```markdown
# Country Localization Framework

## How to Configure Any Country

### Step 1: Identify Country Version
**Transaction:** `SPRO` → [Country Versions path]
**Table:** `T005`

### Step 2: Research SAP Notes
- Search: "Country [XX] localization S/4HANA"
- SAP Support Portal
- Country-specific user groups

### Step 3: Tax Configuration Framework
[Generic approach applicable to any country]

### Step 4: Chart of Accounts Considerations
[Statutory account requirements]

### Step 5: Reporting Requirements
[How to identify and configure]

---

[Continue with generic framework]
```

---

## Testing Reference Files (references/testing/)

```markdown
# Unit Testing Guide

## Testing Methodology

For every config step:
1. **Positive Test:** Config works as expected
2. **Negative Test:** System prevents incorrect data
3. **Integration Test:** Config affects downstream correctly

## Module-by-Module Test Scripts

### FI-GL Unit Tests

#### Test 1: Post Simple GL Journal
**Test ID:** FI-GL-UT-001
**Purpose:** Verify GL accounts and posting keys work
**Prerequisites:** GL accounts created, periods open
**Steps:**
1. Transaction `FB50`
2. Enter: CoCode, Doc Date, Posting Date
3. Line 1: Debit GL [Account], Amount [X], Posting Key 40
4. Line 2: Credit GL [Account], Amount [X], Posting Key 50
5. Save
**Expected Result:** Document posted, number assigned
**Verification:** Transaction `FBL3N` - line items visible

---

[Continue for all modules]

## Integration Test Scenarios

### Procure-to-Pay (P2P)

**Scenario:** Purchase of material with invoice and payment

**Test Steps:**
1. Create Purchase Order (ME21N)
   - Material: [X]
   - Vendor: [Y]
   - Quantity: [Z]
   - Save → Note PO number

2. Goods Receipt (MIGO)
   - Movement Type: 101
   - Reference: PO number from step 1
   - Post GR → Note Material Document

3. Verify GL Posting (FB03)
   - Search by Material Document
   - Expected: Debit Inventory, Credit GR/IR Clearing
   - Accounts: [Specific GL accounts]

4. Invoice Verification (MIRO)
   - Reference: PO number
   - Amount matches GR
   - Post IR → Note Accounting Document

5. Verify GL Posting (FB03)
   - Expected: Debit GR/IR Clearing, Credit Vendor
   - Accounts: [Specific GL accounts]

6. Automatic Payment (F110)
   - Run payment proposal
   - Execute payment run
   - Generate payment file

7. Verify GL Posting (FB03)
   - Expected: Debit Vendor, Credit Bank
   - Accounts: [Specific GL accounts]

8. End-to-End Verification
   - Transaction `FBL3N` - Inventory GL should show net debit
   - Transaction `FBL1N` - Vendor account should be cleared
   - Transaction `FK10N` - Vendor balance should be zero

**Expected Final State:**
- Inventory increased by [Amount]
- Bank decreased by [Amount]
- Vendor cleared (zero balance)
- GR/IR cleared (zero balance)

---

[Continue for O2C, R2R, etc.]

## Test Data Templates
[Sample vendors, customers, materials, etc.]

## Test Result Documentation
[How to document test outcomes]
```

---

## How to Expand This Skill

### Priority Order for Adding Content:

1. **FI Modules (Critical):**
   - ✅ FI-GL-general-ledger.md (DONE - 450+ lines provided as example)
   - ⏳ FI-AP-accounts-payable.md (Use framework above)
   - ⏳ FI-AR-accounts-receivable.md
   - ⏳ FI-AA-asset-accounting.md
   - ⏳ FI-BL-bank-accounting.md
   - ⏳ FI-TR-treasury.md (if needed)

2. **CO Modules (Critical):**
   - ⏳ CO-OM-cost-centers.md
   - ⏳ CO-IO-internal-orders.md
   - ⏳ CO-PA-profitability-analysis.md
   - ⏳ CO-PC-product-costing.md
   - ⏳ CO-PCA-profit-centers.md

3. **Integrations (High Priority):**
   - ⏳ MM-FI-integration.md
   - ⏳ SD-FI-integration.md
   - ⏳ PP-CO-integration.md
   - ⏳ PS-FI-integration.md
   - ⏳ HR-FI-integration.md

4. **Top 10 Country Localizations:**
   - ⏳ india-localization.md
   - ⏳ usa-localization.md
   - ⏳ germany-localization.md
   - ⏳ uk-localization.md
   - ⏳ china-localization.md
   - ⏳ france-localization.md
   - ⏳ japan-localization.md
   - ⏳ brazil-localization.md
   - ⏳ canada-localization.md
   - ⏳ australia-localization.md

5. **Testing Guides:**
   - ⏳ unit-testing-guide.md
   - ⏳ integration-testing-guide.md

6. **External Integrations:**
   - ⏳ external-banking.md
   - ⏳ external-treasury.md
   - ⏳ external-tax-engines.md

### Time Estimate per File:
- FI/CO Module: 4-6 hours (400-600 lines)
- Integration: 2-3 hours (200-300 lines)
- Country Localization: 3-4 hours (300-400 lines)
- Testing Guide: 2-3 hours (200-300 lines)

### Total Estimated Effort:
- 6 FI modules × 5 hours = 30 hours
- 5 CO modules × 5 hours = 25 hours
- 5 Integrations × 2.5 hours = 12.5 hours
- 10 Countries × 3.5 hours = 35 hours
- 2 Testing guides × 2.5 hours = 5 hours
- 3 External integrations × 2 hours = 6 hours
**Total: ~113 hours of content creation**

This can be done incrementally - skill works immediately with current structure, improves as you add modules.

---

## Quick Start for Contributors

To add a new module:
1. Copy the template from this file
2. Fill in all sections with SAP-accurate content
3. Verify transaction codes in S/4HANA system
4. Test the configuration steps yourself
5. Add screenshot placeholders: `[Screenshot: Transaction XYZ - Field ABC]`
6. Save as `[module-name].md` in appropriate folder
7. Skill automatically picks it up when users ask about that module

---

This framework ensures consistency across all reference files and makes the skill expandable by multiple contributors.
