"""Activate ABAP objects via SAP GUI COM Scripting API — bypasses UIPI."""
import time, sys, subprocess
import win32com.client

def get_session():
    """Connect to running SAP GUI session"""
    try:
        sap_gui = win32com.client.GetObject("SAPGUI")
        if not sap_gui:
            print("SAPGUI not running")
            return None
        app = sap_gui.GetScriptingEngine
        if not app:
            print("Scripting engine not available")
            return None
        # Get first connection
        conn = app.Children(0)
        if not conn:
            print("No SAP connection")
            return None
        sess = conn.Children(0)
        if not sess:
            print("No SAP session")
            return None
        print(f"SAP session OK — system: {conn.System}")
        return sess
    except Exception as e:
        print(f"SAP GUI COM error: {e}")
        return None

def run_se38_program(sess, program_name):
    """Navigate to SE38 and execute a program.
    On success returns True.
    """
    try:
        # Get main window
        wnd = sess.findById("wnd[0]")

        # Enter /nSE38 in command field
        print("Navigating to SE38...")
        wnd.findById("tbar[0]/okcd").text = "/nSE38"
        wnd.SendVKey(0)  # Enter
        time.sleep(2)

        # Type program name
        print(f"Typing {program_name}...")
        wnd.findById("usr/ctxtRS38M-PROGRAMM").text = program_name
        wnd.SendVKey(0)  # Enter
        time.sleep(1)

        # Execute program (F8 = SendVKey(8))
        print("Pressing F8 to execute...")
        wnd.SendVKey(8)  # F8
        time.sleep(3)

        print("Program executed. Check SAP GUI for results.")
        return True

    except Exception as e:
        print(f"SE38 navigation error: {e}")
        return False

# --- Main ---
print("=== ZROUTER ACTIVATION via SAP GUI COM Scripting ===")

sess = get_session()
if not sess:
    print("ERROR: Cannot connect to SAP GUI session")
    sys.exit(1)

# Navigate to SE38 and execute ZROUTER_ACTIVATE
ok = run_se38_program(sess, "ZROUTER_ACTIVATE")
print(f"Result: {'OK' if ok else 'FAILED'}")
