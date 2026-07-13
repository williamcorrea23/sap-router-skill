---
name: sap-rpt1
description: SAP RPT1 — FI/CO local tabular prediction workflow, regulatory reporting, country-specific financial patterns
trigger:
  keywords: [rpt1, regulatory reporting, local tabular prediction, fi/co reporting, statutory reporting, tax prediction, local gaap]
  intent: Configuring and executing SAP FI/CO regulatory and statutory reporting per local accounting standards
prerequisites:
  - SAP FI/CO access (for country-specific reports)
  - Transaction RPT1 available in system
  - T005 (country codes) and T009/T009B (fiscal year variants) configured
  - RFC/ADT access for BAPI calls (BAPI_ACC_DOCUMENT_POST, BAPI_GL_GETACCOUNTSALDO)
---

# SAP RPT1 — Regulatory Reporting Workflow

SAP RPT1 provides country-specific local tabular prediction for FI/CO statutory reporting.

## 1. Scope

| Area | Coverage |
|---|---|
| **Local GAAP** | Country-specific accounting principles (BR GAAP, US GAAP, etc.) |
| **Tax Reporting** | VAT, GST, withholding tax prediction |
| **Statutory Reporting** | Local balance sheet, P&L |
| **Audit Support** | Predictive audit trail generation |

## 2. Configure Country-Specific Reports

```abap
" RPT1 configuration tables
" Check country-specific tax rules (T005)
SELECT * FROM t005 WHERE land1 = 'BR'.

" Fiscal year variant for statutory dates
SELECT * FROM t009 WHERE periv = lv_fiscal_variant.

" Local GAAP BAdI implementation (country-filtered)
" SE19 → Create implementation for BAdI RPT1_LOCAL_GAAP
" Filter by country to avoid cross-country conflicts
```

## 3. Execute RPT1

```
Transaction: RPT1
→ Select country code
→ Select report type (Balance Sheet / P&L / Tax)
→ Choose fiscal year and period
→ Execute → Review tabular prediction
→ Export to CSV/Excel
```

## 4. API Integration

```bash
# Via ZROUTER FI handler:
python scripts/sap_router.py route --action FI_POST_DOCUMENT
python scripts/sap_router.py route --action FI_CHECK_ACCOUNTS
python scripts/sap_router.py route --action FI_REVERSE_DOCUMENT

# CSV template for batch document posting
python scripts/xls_to_bapi.py template --output fi_doc.csv \
  --module FI --action POST_DOCUMENT
# Fields: comp_code, doc_type, doc_date, posting_date, currency, amount, account
```

## Pitfalls

- **Local GAAP BAdI not country-filtered** → Cause: BAdI implementation runs for all countries. Solution: add country check in BAdI filtering logic (use `T005` table).
- **Tax code not determined** → Cause: T005 not configured for country-specific tax rules. Solution: verify T005 entries for target country; configure tax code determination via OBCN.
- **Statutory dates offset** → Cause: fiscal year variant mismatch. Solution: ensure T009/T009B matches the reporting entity's fiscal year; check period variant in OB29.
- **Balance sheet not aligning** → Cause: local GAAP rules differ from SAP standard. Solution: configure country-specific chart of accounts (OB13) and financial statement versions (OB58).

## Verification

```bash
# Run RPT1 for a known country and verify tabular output
# SE38 → RPT1 → select country → execute → export CSV

# Check tax configuration
python scripts/sap_router.py route --action FI_CHECK_ACCOUNTS
```

## Related

- **FI handler** in ZROUTER for document posting (BAPI_ACC_DOCUMENT_POST)
- **GL account balance check** via BAPI_GL_GETACCOUNTSALDO
- **Document reversal** via BAPI_ACC_DOCUMENT_REV_POST