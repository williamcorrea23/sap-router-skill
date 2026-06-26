---
name: sap-gui-scripting
description: >-
  SAP GUI Scripting automation — fallback path when ADT cannot handle an operation.
  Auto-navigates transactions via SAP GUI MCP, executes BDC/batch input, reads
  ALV grids, handles popups/dynpros. Use for SPRO config, SU01 user admin,
  SM30 table maintenance, SE16 data browser, PFTC task maintenance, SNOTE
  and any transaction ADT cannot execute. Triggers on: "SAP GUI", "transaction
  SA38/SE38", "BDC recording", "batch input", "SM30", "SPRO", "SU01", "SU53",
  "ALV grid", "screen painter", "dynpro navigation", "ADT failed try GUI",
  "navigate to transaction", "open SAP Easy Access".
---

# SAP GUI Scripting — ADT Fallback & Transaction Automation

When ADT MCP returns "not supported" or "function not available", fall back
to SAP GUI Scripting via configured GUI MCP (mario-andreschak/mcp-sap-gui).

## Architecture

```
Request: "Create SPRO entry for BSART=ZNBX"
    │
    ▼
sap_router.py: ADT?
    │ SAPWrite → "Cannot create customizing entry"
    ▼
sap-gui-scripting (this skill):
    │ 1. Launch SAP GUI session (or attach existing)
    │ 2. Navigate: /nSPRO → tree expand → transaction select
    │ 3. Execute BDC/batch input recording
    │ 4. Verify: table read via SE16
    │ 5. Return result with screenshot/captured data
    ▼
MEMORY.md: status: OK, details: SPRO entry created
```

## MCP Configuration

### Primary: mario-andreschak/mcp-sap-gui (TypeScript)

```json
{
  "mcp-sap-gui": {
    "type": "stdio",
    "command": "node",
    "args": ["dist/index.js"],
    "env": {
      "SAPGUI_HOST": "${SAPGUI_HOST}",
      "SAPGUI_USER": "${SAPGUI_USER}",
      "SAPGUI_PASSWORD": "${SAPGUI_PASSWORD}",
      "SAPGUI_CLIENT": "${SAPGUI_CLIENT}"
    },
    "description": "SAP GUI automation — connect, navigate transactions, execute BDC, read ALV, handle popups"
  }
}
```

### Fallback: kts982/mcp-sap-gui (Python)

```json
{
  "mcp-sap-gui-kts": {
    "type": "stdio",
    "command": "python",
    "args": ["-m", "mcp_sap_gui"],
    "env": {
      "SAP_CONNECTION": "${SAP_CONNECTION_STRING}"
    },
    "description": "SAP GUI MCP (kts982) — Python-based GUI bridge, broader transaction coverage"
  }
}
```

## Transaction Navigation Map

### Basis / ABAP Dev

| Task | ADT Can? | GUI Fallback | Transaction Path |
|---|---|---|---|
| Table maintenance (SM30) | ❌ No write | ✅ | `/nSM30 → table name → maintain` |
| SE16 data browser | ❌ Read-only | ✅ | `/nSE16 → table → execute` |
| SPRO customizing | ❌ No | ✅ | `/nSPRO → tree nav → IMG activity` |
| SU01 user maintenance | ❌ No | ✅ | `/nSU01 → user → change` |
| PFCG role editor | ❌ No | ✅ | `/nPFCG → role → change` |
| SU53 auth check | ❌ No | ✅ | `/nSU53 → read` |
| SA38 program execute | ✅ Via SUBMIT | ✅ | `/nSA38 → program → F8` |
| SE38 with dynpro | ✅ Source only | ✅ | `/nSE38 → program → display` |
| SNOTE apply note | ❌ No | ✅ | `/nSNOTE → note → implement` |
| SE80 Object Navigator | ✅ Via ADT | ✅ | `/nSE80 → tree → open object` |
| SES_ADT_XXX tests | ⚡ Syntax only | ✅ | Full test execution |

### MM (Materials Management)

| Task | ADT Can? | GUI Fallback | Transaction Path |
|---|---|---|---|
| MM01 create material | ❌ No write | ✅ | `/nMM01 → material → views → save` |
| MM02 change material | ❌ No write | ✅ | `/nMM02 → material → change` |
| ME21N create PO | ❌ Via BAPI | ✅ | `/nME21N → vendor → items → save` |
| MIGO goods receipt | ❌ No | ✅ | `/nMIGO → movement → post` |
| MMBE stock overview | ⚡ Read | ✅ | `/nMMBE → material → plant → execute` |
| ME51N purchase req | ❌ No | ✅ | `/nME51N → items → save` |
| MB51 material doc list | ❌ No | ✅ | `/nMB51 → material → execute` |

### SD (Sales & Distribution)

| Task | ADT Can? | GUI Fallback | Transaction Path |
|---|---|---|---|
| VA01 create order | ❌ Via BAPI | ✅ | `/nVA01 → type → sold-to → items → save` |
| VA02 change order | ❌ No write | ✅ | `/nVA02 → order → change` |
| VL01N delivery | ❌ Via BAPI | ✅ | `/nVL01N → ref → items → save` |
| VF01 billing | ❌ Via BAPI | ✅ | `/nVF01 → delivery → save` |
| VF04 billing list | ❌ No | ✅ | `/nVF04 → criteria → execute` |

### FI (Financial Accounting)

| Task | ADT Can? | GUI Fallback | Transaction Path |
|---|---|---|---|
| FB01 post document | ❌ Via BAPI | ✅ | `/nFB01 → header → items → post` |
| FB02 change doc | ❌ No | ✅ | `/nFB02 → doc → change` |
| FS00 GL master | ❌ No | ✅ | `/nFS00 → account → change` |
| F110 auto payment | ❌ No | ✅ | `/nF110 → parameters → schedule` |

### QM / PP / WM / CO / HCM

| Module | Key GUI Transactions |
|---|---|
| QM | QA01, QA02, QE01, QM01, QS21 |
| PP | CO01, CO02, CS01, CA01, MD04 |
| WM | MIGO, LT01, LT02, LS01, LX01 |
| CO | KO01, KS01, KA01, KSB1 |
| HCM | PA20, PA30, PA40, PT01, PC00 |

## BDC / Batch Input Pattern

```python
# sap_gui_session.py — BDC execution pattern
def execute_bdc(session, transaction, bdcdata, mode='N'):
    """
    Execute BDC recording via SAP GUI.
    session: connected SAP GUI session object
    transaction: target T-code
    bdcdata: list of dicts with PROGRAM, DYNPRO, fields
    mode: 'N' (no display), 'A' (all screens), 'E' (errors only)
    """
    session.StartTransaction(transaction)

    for step in bdcdata:
        session.findById(step['PROGRAM'])
        session.findById(step['DYNPRO'])

        for field_name, field_value in step['fields'].items():
            try:
                session.findById(field_name).text = field_value
            except Exception as e:
                # Field may be invisible/disabled — log and continue
                log_field_skip(field_name, str(e))

        if step.get('okcode'):
            session.findById('wnd[0]').sendVKey(step['okcode'])

    return session

# Example: MM01 create material (basic data view)
BDC_MM01_BASIC = [
    {
        'PROGRAM': 'SAPLMGMM',
        'DYNPRO': '0060',
        'fields': {
            'RMMG1-MATNR': 'MAT0001',
            'RMMG1-MBRSH': 'M',      # Industry: Mechanical
            'RMMG1-MTART': 'FERT',   # Material type: Finished
        },
        'okcode': '0'
    },
    # ... more steps per view selected
]
```

## ALV Grid Reading Pattern

```python
def read_alv_grid(session, grid_id='wnd[1]/usr/cntlGRID1/shellcont/shell'):
    """
    Read data from an ALV grid into a list of dicts.
    Works for: MMBE, MB51, ME2M, VA05, FBL1N, KSB1, etc.
    """
    grid = session.findById(grid_id)

    # Get row count
    row_count = grid.RowCount

    # Get column headers
    col_count = grid.ColumnCount
    headers = []
    for col in range(col_count):
        headers.append(grid.GetColumnHeader(col))

    # Read rows
    rows = []
    for row in range(row_count):
        row_data = {}
        for col in range(col_count):
            row_data[headers[col]] = grid.GetCellValue(row, col)
        rows.append(row_data)

    return rows
```

## Popup / Modal Handling

```python
def handle_popup(session, expected_title=None, default_button='OK'):
    """
    Detect and handle modal popup dialogs.
    Returns True if popup was handled.
    """
    try:
        # Check for modal popup (usually wnd[1])
        popup = session.findById('wnd[1]')

        if expected_title and expected_title not in popup.Text:
            return False

        # Press default button
        if default_button == 'OK':
            popup.sendVKey(0)  # Enter
        elif default_button == 'CANCEL':
            popup.sendVKey(12)  # Cancel
        elif default_button == 'YES':
            popup.findById('btn[0]').press()
        elif default_button == 'NO':
            popup.findById('btn[1]').press()

        return True
    except Exception:
        return False
```

## Integration with sap_router.py

```python
# Added to SapRouter.get_route():
GUI_FALLBACK_MODULES = [
    'SPRO', 'SM30', 'SU01', 'SU53', 'PFCG', 'SNOTE',
    'MM01', 'MM02', 'ME21N', 'MIGO', 'MMBE',
    'VA01', 'VA02', 'VL01N', 'VF01',
    'FB01', 'FB02', 'FS00', 'F110',
    'QA01', 'CO01', 'KO01', 'PA20', 'PA30'
]

def get_route_with_fallback(self, action, try_adt=True):
    """Route with ADT-first, GUI-fallback strategy."""
    action_upper = action.upper()

    # Step 1: Try ADT (primary path)
    if try_adt:
        for adt_action in ADT_ACTIONS:
            if adt_action in action.lower():
                return {
                    "destination": "ARC-1 (ADT)",
                    "fallback": "sap-gui-scripting",
                    "status": "attempting ADT"
                }

    # Step 2: Check if GUI fallback is available
    gui_transaction = GUI_TRANSACTION_MAP.get(action_upper)
    if gui_transaction:
        return {
            "destination": "SAP GUI Scripting",
            "mcp": "mcp-sap-gui",
            "transaction": gui_transaction,
            "status": "ADT not available — routed to GUI"
        }

    # Step 3: ZROUTER RFC (for BAPI-based operations)
    return {
        "destination": "ZROUTER RFC",
        "status": "routed to RFC dispatcher"
    }

GUI_TRANSACTION_MAP = {
    'SPRO_CONFIG': 'SPRO',
    'TABLE_MAINTENANCE': 'SM30',
    'USER_MAINTENANCE': 'SU01',
    'AUTH_CHECK': 'SU53',
    'ROLE_EDITOR': 'PFCG',
    'NOTE_APPLY': 'SNOTE',
    'MATERIAL_CREATE_VIA_GUI': 'MM01',
    'MATERIAL_CHANGE_VIA_GUI': 'MM02',
    'PO_CREATE_VIA_GUI': 'ME21N',
    'GOODS_RECEIPT': 'MIGO',
    'STOCK_OVERVIEW': 'MMBE',
    'ORDER_CREATE_VIA_GUI': 'VA01',
    'ORDER_CHANGE_VIA_GUI': 'VA02',
    'DELIVERY_CREATE_VIA_GUI': 'VL01N',
    'BILLING_CREATE_VIA_GUI': 'VF01',
    'FI_POST_DOCUMENT_GUI': 'FB01',
    'FI_CHANGE_DOC_GUI': 'FB02',
    'GL_MASTER_GUI': 'FS00',
    'AUTO_PAYMENT_GUI': 'F110',
    'INSPECTION_CREATE_GUI': 'QA01',
    'PROD_ORDER_CREATE_GUI': 'CO01',
    'INTERNAL_ORDER_GUI': 'KO01',
    'EMPLOYEE_DISPLAY_GUI': 'PA20',
}
```

## Pre-Flight Check

Before routing to GUI:

1. **Verify SAP GUI is installed**: `session = win32com.client.Dispatch("SapGui.ScriptingCtrl")`
2. **Check connection exists**: `connection = session.OpenConnection(host, system_number)`
3. **Detect screen state**: if already in a transaction, handle gracefully
4. **Record transaction path**: log every screen for auditability

## Gotchas

- **SAP GUI Scripting must be enabled**: RZ11 → `sapgui/user_scripting` → TRUE
- **No GUI on server**: SAP GUI must be installed on the machine running the MCP
- **Popups break navigation**: Always check for modal windows between steps
- **Field names change across SAP versions**: Use transaction recorder (SHDB) to capture correct field IDs
- **Long-running transactions**: Set session timeout higher (default 120s)
- **Password fields**: Never hardcode — always pass via env var or secure vault
- **Batch vs interactive**: BDC mode 'E' shows errors only; mode 'A' shows all for debugging
- **ALV grid variant**: ALV may be classic or modern (CL_GUI_ALV_GRID) — adapt grid ID pattern
- **GUI MCP fallback priority**: mario-andreschak > kts982 > Hochfrequenz/sapgui.mcp
