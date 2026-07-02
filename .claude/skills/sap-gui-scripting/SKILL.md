---
name: sap-gui-scripting
description: >-
  SAP GUI Scripting automation — fallback when ADT cannot handle an operation.
  Navigates transactions, executes BDC, reads ALV grids, handles popups.
  Use for SPRO, SU01, SM30, SE16, SNOTE, and any transaction ADT cannot run.
trigger:
  - "SAP GUI"
  - "GUI scripting"
  - "BDC recording"
  - "batch input"
  - "SM30"
  - "SPRO"
  - "SU01"
  - "SU53"
  - "ALV grid"
  - "dynpro navigation"
  - "ADT failed try GUI"
  - "navigate to transaction"
  - "SE16 data browser"
---

# SAP GUI Scripting — ADT Fallback & Transaction Automation

When ADT MCP returns "not supported", fall back to SAP GUI Scripting.
Uses mario-andreschak/mcp-sap-gui (TypeScript) or kts982/mcp-sap-gui (Python).

## Prerequisites

- SAP GUI installed on the machine running the MCP (no GUI on server-only hosts)
- SAP GUI Scripting enabled: RZ11 → `sapgui/user_scripting` → TRUE
- Environment variables set: `SAPGUI_HOST`, `SAPGUI_USER`, `SAPGUI_PASSWORD`, `SAPGUI_CLIENT`
- SHDB transaction recorder available for capturing field IDs

## 1. MCP Configuration

```json
{
  "mcp-sap-gui": {
    "type": "stdio",
    "command": "node",
    "args": ["/opt/data/mcp-sap-gui/dist/index.js"],
    "env": {
      "SAPGUI_HOST": "${SAPGUI_HOST}",
      "SAPGUI_USER": "${SAPGUI_USER}",
      "SAPGUI_PASSWORD": "${SAPGUI_PASSWORD}",
      "SAPGUI_CLIENT": "${SAPGUI_CLIENT}"
    }
  }
}
```

## 2. Transaction Navigation Map

- **Basis/Dev**: SM30 (table maint), SE16 (data browser), SPRO (customizing),
  SU01 (user admin), PFCG (roles), SU53 (auth check), SNOTE (notes)
- **MM**: MM01/MM02 (material), ME21N (PO), MIGO (goods receipt), MMBE (stock)
- **SD**: VA01/VA02 (orders), VL01N (delivery), VF01 (billing)
- **FI**: FB01 (post doc), FB02 (change doc), FS00 (GL master), F110 (auto payment)
- **QM**: QA01, QE01, QM01 | **PP**: CO01, CS01, MD04 | **HCM**: PA20, PA30, PA40

## 3. BDC / Batch Input Pattern

```python
# /opt/data/scripts/sap_gui_bdc.py
import win32com.client

def execute_bdc(session, transaction, bdcdata, mode='N'):
    """Execute BDC recording. mode: N=no display, A=all, E=errors only."""
    session.StartTransaction(transaction)
    for step in bdcdata:
        for field_name, field_value in step.get('fields', {}).items():
            try:
                session.findById(field_name).text = field_value
            except Exception as e:
                log_field_skip(field_name, str(e))
        if step.get('okcode'):
            session.findById('wnd[0]').sendVKey(step['okcode'])
    return session

# Example: SM30 table maintenance
BDC_SM30 = [
    {'fields': {'wnd[0]/usr/txtVIEW-AREA': 'ZROUTER_TMPL'},
     'okcode': '0'}  ➀ Enter
]
session = win32com.client.Dispatch("SapGui.ScriptingCtrl")
connection = session.OpenConnection(SAPGUI_HOST)
execute_bdc(connection.Children(0), 'SM30', BDC_SM30)
```

## 4. ALV Grid Reading

```python
# /opt/data/scripts/sap_gui_alv.py
def read_alv_grid(session, grid_id='wnd[1]/usr/cntlGRID1/shellcont/shell'):
    """Read ALV grid data. Works for MMBE, MB51, ME2M, VA05, FBL1N, KSB1."""
    grid = session.findById(grid_id)
    headers = [grid.GetColumnHeader(c) for c in range(grid.ColumnCount)]
    rows = []
    for r in range(grid.RowCount):
        rows.append({headers[c]: grid.GetCellValue(r, c)
                     for c in range(grid.ColumnCount)})
    return rows
```

## 5. Popup / Modal Handling

```python
# /opt/data/scripts/sap_gui_popup.py
def handle_popup(session, button='OK'):
    """Detect and dismiss modal popup. Returns True if handled."""
    try:
        popup = session.findById('wnd[1]')
        actions = {'OK': 0, 'CANCEL': 12, 'YES': 'btn[0]', 'NO': 'btn[1]'}
        act = actions.get(button, 0)
        if isinstance(act, int):
            popup.sendVKey(act)
        else:
            popup.findById(act).press()
        return True
    except Exception:
        return False
```

## 6. ADT-First Routing Strategy

```python
# /opt/data/scripts/sap_router_fallback.py
GUI_FALLBACK = [
    'SPRO', 'SM30', 'SU01', 'SU53', 'PFCG', 'SNOTE',
    'MM01', 'MM02', 'ME21N', 'MIGO', 'MMBE',
    'VA01', 'VA02', 'VL01N', 'VF01',
    'FB01', 'FB02', 'FS00', 'F110',
    'QA01', 'CO01', 'KO01', 'PA20', 'PA30'
]

def route(action, try_adt=True):
    """Route: ADT first → GUI fallback → ZROUTER RFC."""
    if try_adt and adt_supports(action):
        return {"dest": "ADT", "fallback": "sap-gui-scripting"}
    if action.upper() in GUI_FALLBACK:
        return {"dest": "SAP GUI", "mcp": "mcp-sap-gui", "tcode": action}
    return {"dest": "ZROUTER RFC"}
```

## Pitfalls

- **SAP GUI Scripting not enabled**:
  - Cause: `sapgui/user_scripting` is FALSE in RZ11.
  - Solution: Set to TRUE via RZ11 and restart SAP GUI.
- **Field IDs change across SAP versions**:
  - Cause: Screen modifications in support packages shift field positions.
  - Solution: Use SHDB transaction recorder to capture correct field IDs before scripting.
- **Popups break BDC navigation silently**:
  - Cause: Modal window appears between steps; script tries next field on wrong screen.
  - Solution: Call `handle_popup()` after every `sendVKey` in BDC loops.
- **Password hardcoded in script**:
  - Cause: Developer embeds credentials for convenience.
  - Solution: Always use environment variables or secure vault — never hardcode.
- **BDC mode A floods with screens in production**:
  - Cause: Mode 'A' shows every screen — useful for debug, terrible for batch.
  - Solution: Use mode 'N' (no display) for production, 'E' for error-only visibility.
- **No SAP GUI on server host**:
  - Cause: MCP runs on Linux server without SAP GUI installed.
  - Solution: Run GUI MCP on a Windows machine with SAP GUI, or use RFC/BAPI instead.

## Verification

```bash
# Verify SAP GUI scripting is enabled
python3 /opt/data/scripts/check_gui_scripting.py --host "$SAPGUI_HOST"

# Verify MCP config exists
test -f /opt/data/.mcp/sap-gui.json && echo "OK: MCP config found" || echo "FAIL: no config"

# Verify BDC script syntax
python3 -m py_compile /opt/data/scripts/sap_gui_bdc.py && echo "OK: BDC script valid"

# Verify environment variables are set
test -n "$SAPGUI_HOST" && test -n "$SAPGUI_USER" && echo "OK: env set" || echo "FAIL: missing env"
```
