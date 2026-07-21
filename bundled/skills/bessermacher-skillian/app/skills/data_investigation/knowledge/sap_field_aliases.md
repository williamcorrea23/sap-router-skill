# SAP BW Field Aliases

Users refer to SAP BW fields by various names. This reference maps common terms
to their actual Datasphere column names.

## Company Code
- User terms: Company Code, CoCd, CompCode, Company
- Datasphere column: `ZCOMPCODE`
- Example values: 1110, 5500, 1000

## Fiscal Period
- User terms: Period, Month, Fiscal Period, FiscPer
- Datasphere column: `FISCPER`
- Format: YYYYMMM (e.g., 2024012 = December 2024, 2024001 = January 2024)
- Note: January = 001, February = 002, ..., December = 012

## Consolidation Scope
- User terms: Scope, Consolidation Scope, ConScope
- Datasphere column: `ZSCOPE`
- Key values: S_LEGAL, S_LEGAL_DKK, S_LEGAL_SPECIAL, S_NONE

## Version
- User terms: Version, Ver
- Datasphere column: `ZVERSION`
- Key values: 001 (Actual), 002 (Actuals at LY budget rate), 003 (Actuals at budget rate), 004 (Actuals at NY budget rate), 021 (Forecast)
