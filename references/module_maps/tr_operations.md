# TR — Treasury Operations Map

## Overview
Covers Cash position, Liquidity planning, Payment run execution, Bank statement import, and configuration checks.

## Actions Reference

### `TR_PAYMENT_RUN`
- **Purpose**: Execute payment run.
- **Backend BAPI**: F110 batch program / `FI_PAYMENT_PROPOSAL_CREATE`
- **Fields**:
  - `run_date`: Payment run date
  - `run_id`: Payment run ID (identification)
  - `company_code`: Company code

### `TR_IMPORT_STATEMENT`
- **Purpose**: Import bank statements.
- **Backend BAPI**: `RFEBKA00` (FF_5) / `FEBA` post-process
- **Fields**:
  - `format`: Statement format (e.g. MT940)
  - `file_path`: Path to file

### `TR_CASH_POSITION`
- **Purpose**: Expose liquidity cash position.
- **Backend BAPI**: FF7A / FF7B read
- **Fields**:
  - `date`: Analysis date
  - `view`: Cash position or liquidity forecast

### `TR_CHECK_CONFIG`
- **Purpose**: Verify house banks and payment parameters.
- **Tables checked**: T012, T012K, T042, T028G

## T-codes
F110, FF_5, FF7A, FF7B, FI12, FBZP, FEBAN, DMEE, OT83

## Tables
FEBKO, FEBEP, REGUH, REGUP, PAYR, T012, T012K, T042G
