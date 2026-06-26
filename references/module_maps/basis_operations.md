# Basis & ABAP Dev Operations

## Overview
Includes transport request operations, ST22 dumps analysis, code syntax checking/analysis, and direct source file packaging (.nugg format).

## Actions Reference

### `BASIS_CREATE_REQUEST`
- **Purpose**: Create a new Customizing or Workbench transport request.
- **Backend FM**: `TR_INSERT_REQUEST_WITH_TASKS`
- **Fields**:
  - `description`: Text/title of request
  - `target`: Target system (optional)
  - `type`: 'K' (Workbench) or 'W' (Customizing)
  - `owner`: Owner username (default: sy-uname)

### `BASIS_RELEASE_REQUEST`
- **Purpose**: Release a transport request.
- **Backend FM**: `TR_RELEASE_REQUEST`
- **Fields**:
  - `request`: Transport request ID (e.g. DEVK900042)

### `BASIS_ST22_SCAN`
- **Purpose**: Read recent runtime dumps.
- **Direct tables**: `SNAP`, `SNAPT`
- **Fields**:
  - `period`: 24h, 7d, 30d
  - `program_filter`: Program name pattern (e.g. Z*)
  - `user_filter`: Username pattern

### `BASIS_CODE_ANALYSIS`
- **Purpose**: Run ABAP Test Cockpit (ATC) check or Code Inspector variant.
- **Route**: Executed via ADT tool wrappers.

### `BASIS_CREATE_NUGG`
- **Purpose**: Download specific program code and its includes in SAPlink .nugg format.
- **Backend FM**: `RPY_PROGRAM_READ`
