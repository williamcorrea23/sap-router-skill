# Consolidated Management PnL Report

## Overview

The Consolidated Management PnL (CM) report is the primary group financial consolidation
report in SAP BPC. It shows consolidated financial data across company codes,
versions, and scopes.

## Report Versions

| Version Code | Name | Datasphere Table | Description |
|---|---|---|---|
| 001 | Actual | CV_ZBC_AA61 | Actual financial data |
| 002 | Actuals at last year budget rate | CV_ZBC_AA61 | Actuals re-translated at prior year budget FX rates |
| 003 | Actuals at budget rate | CV_ZBC_AA61 | Actuals re-translated at current budget FX rates |
| 004 | Actuals at next year budget rate | CV_ZBC_AA61 | Actuals re-translated at next year budget FX rates |
| 021 | Forecast | CV_ZBC_AA62 | Forecast/planning data |

## Key Dimensions

- **ZCOMPCODE** (`ZCOMPCODE`): Company code (e.g., 1110, 5500)
- **ZVERSION** (`ZVERSION`): Version code (001, 002, etc.)
- **FISCPER**: Fiscal period in format YYYYMMM (e.g., 2024012 = December 2024)
- **ZSCOPE** (`ZSCOPE`): Consolidation scope

## Data Pipeline

Data flows through:

```
Source Systems -> BPC Mart (CV_ZFI_AA01) -> Reporting (CV_ZBC_AA61 / CV_ZBC_AA62)
```

If data is missing in the CM report, it could be missing at any point in this pipeline.

**Important:** The BPC mart table (`CV_ZFI_AA01`) is structurally different from the
Consolidated Management PnL reporting tables (`CV_ZBC_AA61` / `CV_ZBC_AA62`).
The BPC mart does **not** have `ZSCOPE` or `ZVERSION` fields — these are
added during the consolidation process. All data in `CV_ZFI_AA01` is the source
for `CV_ZBC_AA61`. When checking the BPC mart, only filter by company code and
fiscal period.

## Scope Values and Their Meaning

- **S_LEGAL**: Legal consolidation scope — full consolidation applied
- **S_LEGAL_DKK**: Legal scope in DKK currency
- **S_LEGAL_SPECIAL**: Special legal consolidation scope
- **S_NONE**: No scope — indicates that only currency conversion was performed,
  consolidation stopped before applying a scope. This is a diagnostic indicator
  that the consolidation process did not complete.

## Common Investigation Patterns

### Data exists with S_NONE only
When data is present but only under scope S_NONE, it means the BPC consolidation
engine performed currency conversion but stopped before assigning a consolidation scope.
This typically happens when:
- The company code is not in the ownership table for that period
- The consolidation process encountered an error after currency conversion

### No data at all in reporting
When no data exists in the reporting table (CV_ZBC_AA61/62), the data may still
exist in the BPC mart table (CV_ZFI_AA01). If it does, the
reporting data load likely failed or was not triggered.
