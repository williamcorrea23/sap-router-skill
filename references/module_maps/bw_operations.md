# BW — Business Warehouse Operations Map

## Overview
Covers BW data modeling (ADSO, CompositeProvider), process chains monitoring (RSPC), and BEx query execution/troubleshooting.

## Actions Reference

### `BW_MONITOR_CHAIN`
- **Purpose**: Monitor/troubleshoot a process chain run.
- **Backend BAPI**: `RSPC_API_CHAIN_GET_STATUS`
- **Fields**:
  - `chain_id`: Process Chain Technical Name

### `BW_EXECUTE_QUERY`
- **Purpose**: Run/verify BEx Query output.
- **Backend BAPI**: `RRMX_REPORT_START` / RSRT query execution
- **Fields**:
  - `query_name`: BEx Query Technical Name

## T-codes
RSPC, RSRT, RSA1, RS11, RSD1

## Tables
RSPCLOGCHAIN, RSPCPROCESSLOG, RSZCOMPDIR
