# Financial Accounting (FI) Operations

## Overview
Covers General Ledger postings, document reversals, GL Account checks, and FI configuration verification.

## Actions Reference

### `FI_POST_DOCUMENT`
- **Purpose**: Post a General Ledger or Accounts Payable/Receivable document.
- **Backend BAPI**: `BAPI_ACC_DOCUMENT_POST`
- **Fields**:
  - `comp_code`: Company code (T001)
  - `doc_date`: Document Date
  - `pstng_date`: Posting Date
  - `doc_type`: Document Type (T003)
  - `username`: Posting User
  - `items`: Array of line items (account, amount, cost_center, profit_center)

### `FI_REVERSE_DOCUMENT`
- **Purpose**: Reverse a posted financial document.
- **Backend BAPI**: `BAPI_ACC_DOCUMENT_REV_POST`
- **Fields**:
  - `obj_type`: Object Type
  - `obj_key`: Object Key (Document Number + Company Code + Fiscal Year)
  - `reason`: Reversal Reason

### `FI_CHECK_ACCOUNTS`
- **Purpose**: Verify if GL accounts are active and mapped.
- **Tables**: `SKA1`, `SKB1`, `SKAT`

### `FI_CHECK_CONFIG`
- **Purpose**: Verify FI configuration tables.
- **Tables checked**:
  - `T001` (company codes)
  - `T004` (chart of accounts)
  - `T003` (document types)
  - `T009` (fiscal year variants)
