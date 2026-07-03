#!/usr/bin/env python3
"""
SAP GUI Scripting Prerequisite Check v4.2.0

Verifies local prerequisites for SAP GUI Scripting automation
(.claude/skills/sap-gui-scripting/SKILL.md): environment variables,
SAP GUI installation, and the win32com COM bridge. The server-side
parameter sapgui/user_scripting (RZ11) cannot be probed offline;
the check prints the instruction instead.
Exit codes: 0 = all critical checks pass, 1 = missing prerequisites.
"""

import os
import sys
import platform
import argparse

__version__ = "4.2.0"

REQUIRED_ENV = ["SAPGUI_HOST", "SAPGUI_USER", "SAPGUI_PASSWORD", "SAPGUI_CLIENT"]

SAPLOGON_PATHS = [
    r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe",
    r"C:\Program Files\SAP\FrontEnd\SAPgui\saplogon.exe",
    r"C:\Program Files (x86)\SAP\FrontEnd\SAPGUI\saplogon.exe",
]


def check_env(host_override):
    ok = True
    for var in REQUIRED_ENV:
        value = host_override if (var == "SAPGUI_HOST" and host_override) else os.environ.get(var)
        if value:
            shown = "***" if "PASSWORD" in var else value
            print(f"  {var:16s}: [OK] {shown}")
        else:
            print(f"  {var:16s}: [MISSING]")
            ok = False
    return ok


def check_sapgui_installed():
    if platform.system() != "Windows":
        print("  saplogon.exe    : [SKIP] non-Windows host - run GUI MCP on a Windows machine")
        return None
    for path in SAPLOGON_PATHS:
        if os.path.isfile(path):
            print(f"  saplogon.exe    : [OK] {path}")
            return True
    print("  saplogon.exe    : [MISSING] SAP GUI for Windows not found in standard paths")
    return False


def check_win32com():
    if platform.system() != "Windows":
        print("  win32com        : [SKIP] non-Windows host")
        return None
    try:
        import win32com.client  # noqa: F401
        print("  win32com        : [OK]")
        return True
    except ImportError:
        print("  win32com        : [MISSING] Install: pip install pywin32")
        return False


def main():
    parser = argparse.ArgumentParser(description="SAP GUI Scripting Prerequisite Check v4.2.0")
    parser.add_argument("--host", help="Override SAPGUI_HOST for this check")
    args = parser.parse_args()

    print("SAP GUI SCRIPTING PREREQUISITE CHECK")
    print("=" * 50)
    print("Environment variables:")
    env_ok = check_env(args.host)
    print("Local installation:")
    gui_ok = check_sapgui_installed()
    com_ok = check_win32com()
    print("Server-side (cannot probe offline):")
    print("  RZ11 parameter sapgui/user_scripting must be TRUE on the target system.")
    print("  Verify: RZ11 -> sapgui/user_scripting -> Display -> Current Value = TRUE")

    critical_fail = (not env_ok) or gui_ok is False or com_ok is False
    print("=" * 50)
    if critical_fail:
        print("[FAIL] Missing prerequisites - see items above.")
        sys.exit(1)
    print("[OK] Local prerequisites satisfied. Confirm RZ11 setting on the SAP system.")
    sys.exit(0)


if __name__ == "__main__":
    main()
