---
name: sap-rpt1
description: SAP RPT1 — FI/CO local tabular prediction workflow, regulatory reporting guidance, local accounting standard compliance, tax prediction models. Use when working with SAP FI/CO regulatory reporting, configuring local accounting predictions, or implementing country-specific financial reporting workflows.
---

# SAP RPT1

FI/CO local tabular prediction workflow for regulatory reporting guidance.

## Purpose

SAP-RPT-1-OSS provides guidance for FI/CO local tabular prediction workflows — country-specific financial reporting patterns and regulatory compliance prediction for local accounting standards.

## Scope

| Area | Coverage |
|---|---|
| Local GAAP | Country-specific accounting principles |
| Tax Reporting | VAT, GST, withholding tax prediction |
| Statutory Reporting | Balance sheet, P&L per local standard |
| Audit Support | Predictive audit trail generation |

## Integration with ZROUTER

ZROUTER FI handler supports RPT1-related actions:
- POST_DOCUMENT → BAPI_ACC_DOCUMENT_POST
- CHECK_ACCOUNTS → BAPI_GL_GETACCOUNTSALDO
- REVERSE_DOCUMENT → BAPI_ACC_DOCUMENT_REV_POST

## CSV Template

```bash
python scripts/xls_to_bapi.py template --output fi_doc.csv --module FI --action POST_DOCUMENT
# Fields: comp_code, doc_type, doc_date, posting_date, currency, amount, account
```

## Gotchas
- Local GAAP rules vary by country — ensure BAdI implementations are country-filtered
- Tax code determination requires T005 (country-specific tax rules) configuration
- Statutory reporting dates must align with fiscal year variant (T009/T009B)
