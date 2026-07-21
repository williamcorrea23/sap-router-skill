"""
sap_connect.py
==============
Opens a new SAP session from a running SAP Logon application.

Supports both SSO (Single Sign-On) and password-based logon:

  SSO mode:
    OpenConnection() authenticates automatically via Windows/Kerberos SSO.
    The script detects whether it lands on the login screen (client selection
    only) or jumps straight to the SAP Easy Access menu, and handles both.

  Password mode:
    Call connect_to_system(..., sso=False, user="...", password="...")
    The script fills MANDT / BNAME / BCODE / LANGU and submits.

Requirements:
    - SAP Logon must be running (no active session needed)
    - SAP GUI Scripting must be enabled:
        SAP GUI → Customising → Options → Scripting → Enable scripting ✓
    - For SSO: Windows SSO / SNC must be configured for the system entry

Usage (interactive – SSO):
    python sap_connect.py
    python sap_connect.py --system MYSYS --client 100

Usage (password logon):
    python sap_connect.py --system MYSYS --client 100 --no-sso --user YOUR_USER

Usage (from another script):
    from sap_connect import connect_to_system
    sap = connect_to_system("MYSYS", client="100")          # SSO
    sap = connect_to_system("MYSYS", client="100",          # password
                            sso=False, user="YOUR_USER")

API calls used:
    GetObject("SAPGUI")                   – attach to running SAP Logon via ROT
    GuiApplication.GetScriptingEngine     – get GuiApplication object
    GuiApplication.OpenConnection(desc)   – open new connection by Logon entry name
    GuiConnection.Children(0)             – first session
    GuiSession.Info.Transaction           – detect current screen
    findById / text / sendVKey(0)         – interact with login screen
    GuiStatusbar.MessageType              – verify login result
"""

import win32com.client
import time
import getpass
import logging
import argparse
import subprocess
import os
import sys
from typing import Optional

from sap_scripting import SapSession

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("sap_connect")

# ---------------------------------------------------------------------------
# Configuration  – edit these defaults for your environment
# ---------------------------------------------------------------------------
DEFAULT_SYSTEM   = ""       # Set to the description name exactly as shown in SAP Logon
DEFAULT_CLIENT   = ""       # SAP client number, e.g. "100" or "200"
DEFAULT_USER     = ""       # SAP username (leave empty to prompt; unused for SSO)
DEFAULT_LANGUAGE = "EN"     # Logon language
DEFAULT_SSO      = True     # True = SSO logon; False = username + password

# How long to wait (seconds) after sending vKey before reading the screen
LOGIN_WAIT       = 2.0
POPUP_WAIT       = 0.5

# SAP Logon executable – searched in order; first match wins
_SAPLOGON_CANDIDATES = [
    r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe",
    r"C:\Program Files\SAP\FrontEnd\SAPgui\saplogon.exe",
    r"C:\Program Files (x86)\SAP\SAPLogon\saplogon.exe",
]
SAPLOGON_STARTUP_TIMEOUT = 30   # seconds to wait for SAP Logon to appear in ROT

# Login screen identification – present when still on the logon screen
_LOGIN_SCREEN_FIELDS = [
    "wnd[0]/usr/txtRSYST-MANDT",   # Client field
    "wnd[0]/usr/txtRSYST-BNAME",   # Username field
]


# ===========================================================================
#  SAP Logon auto-start
# ===========================================================================

def _ensure_saplogon_running():
    """
    Return a GuiApplication object, starting SAP Logon if it is not already
    running.

    Strategy
    --------
    1. Try GetObject("SAPGUI") – if it works, SAP Logon is already up.
    2. If it fails, find saplogon.exe and launch it via subprocess.
    3. Poll GetObject("SAPGUI") for up to SAPLOGON_STARTUP_TIMEOUT seconds.
    4. Return the GuiApplication scripting engine.

    Raises
    ------
    ConnectionError  – saplogon.exe not found, or SAP Logon did not start
                       within the timeout, or scripting is disabled.
    """
    # -- Try to attach to already-running SAP Logon -------------------------
    try:
        rot_entry   = win32com.client.GetObject("SAPGUI")
        application = rot_entry.GetScriptingEngine
        log.info(f"SAP Logon already running. Active connections: {application.Children.Count}")
        return application
    except Exception:
        log.info("SAP Logon not detected – attempting to start it ...")

    # -- Find saplogon.exe --------------------------------------------------
    exe_path = None
    for candidate in _SAPLOGON_CANDIDATES:
        if os.path.isfile(candidate):
            exe_path = candidate
            break

    if exe_path is None:
        raise ConnectionError(
            "SAP Logon is not running and saplogon.exe was not found in the "
            "standard locations:\n" +
            "\n".join(f"  {p}" for p in _SAPLOGON_CANDIDATES) +
            "\nSet SAPLOGON_EXE or start SAP Logon manually and retry."
        )

    log.info(f"Launching SAP Logon from: {exe_path}")
    subprocess.Popen([exe_path])

    # -- Poll until SAP Logon registers in the ROT --------------------------
    deadline = time.time() + SAPLOGON_STARTUP_TIMEOUT
    while time.time() < deadline:
        try:
            rot_entry   = win32com.client.GetObject("SAPGUI")
            application = rot_entry.GetScriptingEngine
            log.info("SAP Logon started successfully.")
            return application
        except Exception:
            time.sleep(1.0)

    raise ConnectionError(
        f"SAP Logon was launched but did not become ready within "
        f"{SAPLOGON_STARTUP_TIMEOUT} seconds. "
        "Check that SAP GUI scripting is enabled."
    )


# ===========================================================================
#  Core connection function
# ===========================================================================

def connect_to_system(
    system:   str  = DEFAULT_SYSTEM,
    client:   str  = DEFAULT_CLIENT,
    user:     str  = DEFAULT_USER,
    password: str  = "",
    language: str  = DEFAULT_LANGUAGE,
    sso:      bool = DEFAULT_SSO,
) -> SapSession:
    """
    Open a new SAP connection and log in.

    Parameters
    ----------
    system   : SAP Logon entry description (exactly as shown in SAP Logon pad)
    client   : SAP client number, e.g. "200"
    user     : SAP username – ignored when sso=True
    password : SAP password – ignored when sso=True; prompted if sso=False and empty
    language : Logon language code, e.g. "EN"
    sso      : True  = SSO/SNC logon (Windows credentials, no password needed)
               False = standard username + password logon

    Returns
    -------
    SapSession  – connected and logged-in session wrapper

    Raises
    ------
    ConnectionError  – SAP Logon not running, scripting disabled, or system not found
    RuntimeError     – login failed (wrong credentials, locked, system unavailable)
    """

    # -- 1. Credentials (password logon only) ------------------------------
    if not sso:
        if not user:
            user = input(f"SAP user for {system}/{client}: ").strip()
        if not password:
            password = getpass.getpass(f"Password for {user}@{system}: ")

    # -- 2. Attach to SAP Logon (start it if not running) ------------------
    application = _ensure_saplogon_running()    # GuiApplication
    log.info(f"SAP Logon ready. Active connections before: {application.Children.Count}")

    # -- 3. Open a new connection to the target system ---------------------
    log.info(f"Opening connection to '{system}' (SSO={sso}) ...")
    try:
        connection = application.OpenConnection(system, True)   # True = synchronous
    except Exception as exc:
        raise ConnectionError(
            f"Cannot open connection to '{system}': {exc}\n"
            f"  • Does '{system}' exist in SAP Logon? Check exact name (case-sensitive).\n"
            f"  • For SSO entries the description often ends with ' SSO' – verify."
        ) from exc

    # -- 4. Get the newly created session ----------------------------------
    # Poll until the session and its main window are ready (avoids "data not
    # yet available" COM error that occurs when the window is still painting).
    deadline = time.time() + 30.0          # maximum 30 s to wait
    session = None
    wnd_title = ""
    while time.time() < deadline:
        try:
            session = connection.Children(0)        # GuiSession
            wnd_title = session.findById("wnd[0]").Text
            break                                   # window is ready
        except Exception:
            time.sleep(0.5)
    else:
        raise RuntimeError(
            "SAP window did not become ready within 30 seconds after OpenConnection."
        )

    log.info(f"Session opened. Window title: '{wnd_title}'")

    # -- 5. Detect current screen and handle login -------------------------
    #
    #  Three possible states after OpenConnection:
    #
    #  A) Already on SAP Easy Access / main menu
    #     → SSO authenticated fully automatically, no login screen shown
    #     → nothing to do, proceed to popup handling
    #
    #  B) Login screen is shown, client field is editable
    #     → SSO: set client (if needed) + Enter; no credentials
    #     → Password: fill all fields + Enter
    #
    #  C) Some unexpected screen (system message, maintenance, etc.)
    #     → log a warning and still try to proceed
    #
    screen_state = _detect_screen(session)
    log.info(f"Screen state after OpenConnection: {screen_state}")

    if screen_state == "LOGIN":
        _do_login(session, client, user, password, language, sso)
        time.sleep(LOGIN_WAIT)
    elif screen_state == "MENU":
        log.info("SSO authenticated automatically – skipped login screen")
    else:
        log.warning(f"Unexpected screen state '{screen_state}' – attempting to continue")

    # -- 6. Handle common post-login popups --------------------------------
    _handle_post_login_popups(session)

    # -- 7. Verify login succeeded -----------------------------------------
    _verify_login(session)

    # -- 8. Wrap in SapSession and return ----------------------------------
    conn_idx = application.Children.Count - 1   # newly added connection is last
    sap = _wrap_existing_session(application, conn_idx, session_index=0)

    info = sap.get_session_info()
    log.info(
        f"Connected – system={info['system']}, client={info['client']}, "
        f"user={info['user']}, transaction={info['transaction']}"
    )
    return sap


# ===========================================================================
#  Screen detection
# ===========================================================================

def _detect_screen(session) -> str:
    """
    Determine what screen is currently showing.

    Returns
    -------
    "LOGIN"   – standard SAP login screen (MANDT/BNAME fields present)
    "MENU"    – SAP Easy Access or any post-login screen
    "UNKNOWN" – something else
    """
    # Check for login screen: MANDT field is the reliable indicator
    mandt_field = _find_element(session, _LOGIN_SCREEN_FIELDS[0])
    if mandt_field is not None:
        return "LOGIN"

    # Check for post-login: transaction is SESSION_MANAGER (Easy Access)
    # or any other transaction that isn't blank / LOGIN
    try:
        tcode = session.Info.Transaction.strip()
        if tcode and tcode not in ("", "LOGIN"):
            return "MENU"
    except Exception:
        pass

    # Check window title for SAP Easy Access
    try:
        title = session.findById("wnd[0]").Text.strip()
        if title:                                   # any non-blank title = logged in
            return "MENU"
    except Exception:
        pass

    return "UNKNOWN"


# ===========================================================================
#  Login screen handler
# ===========================================================================

def _do_login(session, client: str, user: str, password: str,
              language: str, sso: bool) -> None:
    """
    Fill the SAP login screen and submit.

    SSO mode  : set client only (username/password pre-filled by SNC/Kerberos);
                press Enter.
    Password  : set all four fields; press Enter.
    """
    try:
        # Client is always set – it may differ from the SAP Logon default
        mandt = _find_element(session, "wnd[0]/usr/txtRSYST-MANDT")
        if mandt and mandt.Changeable:
            mandt.text = client
            log.info(f"Client set to {client}")
        else:
            log.info(f"Client field not changeable – using pre-set value")

        if not sso:
            # Username
            bname = _find_element(session, "wnd[0]/usr/txtRSYST-BNAME")
            if bname:
                bname.text = user

            # Password  (GuiPasswordField – use .text, not .Text)
            bcode = _find_element(session, "wnd[0]/usr/pwdRSYST-BCODE")
            if bcode:
                bcode.text = password

            # Language
            langu = _find_element(session, "wnd[0]/usr/txtRSYST-LANGU")
            if langu and langu.Changeable:
                langu.text = language

            log.info(f"Credentials filled: user={user}, lang={language}")
        else:
            log.info("SSO mode – skipping username/password fields")

        # Submit
        session.findById("wnd[0]").sendVKey(0)
        log.info("Login submitted (Enter)")

    except Exception as exc:
        raise RuntimeError(
            f"Error filling login screen: {exc}\n"
            "  • Field IDs may differ – check SAP version / screen layout"
        ) from exc


# ===========================================================================
#  Popup handlers
# ===========================================================================

def _handle_post_login_popups(session) -> None:
    """
    Dismiss standard popups that can appear after successful authentication:

    1. Copyright / system information dialog (title contains "SAP" or "Copyright")
       → press Enter (VKey 0)

    2. Multiple logon dialog – user already has active sessions
       Title: "System Message" / popup window wnd[1]
       Options (radio buttons):
         OPT1 – Continue this logon, terminate other sessions
         OPT2 – Continue this logon WITHOUT terminating other sessions
         OPT3 – Cancel this logon
       → we select OPT2 (continue without terminating) and confirm
    """
    time.sleep(POPUP_WAIT)

    # Check for any modal popup (wnd[1])
    for attempt in range(5):
        popup = _find_element(session, "wnd[1]")
        if popup is None:
            break

        title = popup.Text.strip().lower()
        log.info(f"Popup detected: '{popup.Text}'")

        if _find_element(session, "wnd[1]/usr/radMULTI_LOGON_OPT1"):
            # Multiple logon dialog
            _handle_multiple_logon(session)
        else:
            # Copyright / info dialog – just press Enter
            log.info("Dismissing info/copyright popup (Enter)")
            session.findById("wnd[0]").sendVKey(0)

        time.sleep(POPUP_WAIT)


def _handle_multiple_logon(session) -> None:
    """
    Handle the 'Multiple Logon' dialog.

    Selects OPT2 (continue without terminating existing sessions)
    then presses the confirm button.

    To terminate other sessions instead, change to OPT1.
    """
    log.info("Multiple logon dialog detected – selecting OPT2 (continue, keep other sessions)")
    try:
        # Select radio button OPT2
        opt2 = _find_element(session, "wnd[1]/usr/radMULTI_LOGON_OPT2")
        if opt2:
            opt2.select()
        # Confirm
        confirm_btn = _find_element(session, "wnd[1]/tbar[0]/btn[0]")
        if confirm_btn:
            confirm_btn.press()
        else:
            session.findById("wnd[1]").sendVKey(0)
        log.info("Multiple logon handled")
    except Exception as exc:
        log.warning(f"Multiple logon handling failed: {exc} – trying Enter")
        try:
            session.findById("wnd[0]").sendVKey(0)
        except Exception:
            pass


def _find_element(session, element_id: str):
    """Return element or None – never raises."""
    try:
        return session.findById(element_id)
    except Exception:
        return None


# ===========================================================================
#  Post-login verification
# ===========================================================================

def _verify_login(session) -> None:
    """
    Check whether login actually succeeded.

    Reads the status bar. If MessageType is E (error) or A (abort)
    the login failed (wrong password, user locked, system unavailable, etc.).
    """
    try:
        sbar = session.findById("wnd[0]/sbar")
        msg_type = sbar.MessageType
        msg_text = sbar.Text
    except Exception:
        # Status bar not readable – assume OK
        return

    if msg_type in ("E", "A"):
        raise RuntimeError(
            f"Login failed [{msg_type}]: {msg_text}\n"
            "  • Check username / password / client / system availability."
        )

    if msg_type == "W":
        log.warning(f"Login warning [{msg_type}]: {msg_text}")
    elif msg_type == "S" and msg_text:
        log.info(f"Login status [{msg_type}]: {msg_text}")


# ===========================================================================
#  Session wrapper helper
# ===========================================================================

def _wrap_existing_session(application, conn_idx: int,
                            session_index: int = 0) -> SapSession:
    """
    Create a SapSession wrapper around an already-open session.

    SapSession.__init__ normally calls _connect() which always uses
    Children(0). Here we bypass it and set the objects directly so we
    can point to any connection/session index.
    """
    sap = object.__new__(SapSession)          # skip __init__
    sap.connection_index = conn_idx
    sap.session_index    = session_index
    sap.application      = application
    sap.connection       = application.Children(conn_idx)
    sap.session          = sap.connection.Children(session_index)
    return sap


# ===========================================================================
#  List available systems in SAP Logon (helper)
# ===========================================================================

def list_logon_entries() -> list:
    """
    Return the description names of all entries in SAP Logon.
    Useful for finding the exact name to pass to connect_to_system().
    """
    try:
        rot_entry   = win32com.client.GetObject("SAPGUI")
        application = rot_entry.GetScriptingEngine
        # GuiApplication.Connections gives active connections – not Logon entries.
        # The Logon entries live in the SAPLogon COM object.
        try:
            logon = win32com.client.Dispatch("SapROTWr.SapROTWrapper")
        except Exception:
            pass
        # Fallback: just show active connections
        active = []
        for i in range(application.Children.Count):
            conn = application.Children(i)
            for j in range(conn.Children.Count):
                sess = conn.Children(j)
                active.append({
                    "conn_idx": i,
                    "sess_idx": j,
                    "system":   sess.Info.SystemName,
                    "client":   sess.Info.Client,
                    "user":     sess.Info.User,
                    "tcode":    sess.Info.Transaction,
                })
        return active
    except Exception as exc:
        log.warning(f"list_logon_entries: {exc}")
        return []


# ===========================================================================
#  CLI entry point
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Open a new SAP session from SAP Logon and log in.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sap_connect.py                                    # SSO, uses DEFAULT_SYSTEM/CLIENT
  python sap_connect.py --system MYSYS --client 100        # SSO explicit
  python sap_connect.py --no-sso --user YOUR_USER          # password logon
  python sap_connect.py --list                             # show active sessions
        """
    )
    parser.add_argument("--system",   default=DEFAULT_SYSTEM,
                        help=f"SAP Logon entry description (default: {DEFAULT_SYSTEM})")
    parser.add_argument("--client",   default=DEFAULT_CLIENT,
                        help=f"SAP client number (default: {DEFAULT_CLIENT})")
    parser.add_argument("--user",     default=DEFAULT_USER,
                        help="SAP username (prompted if not supplied; ignored for SSO)")
    parser.add_argument("--language", default=DEFAULT_LANGUAGE,
                        help=f"Logon language (default: {DEFAULT_LANGUAGE})")
    parser.add_argument("--no-sso",   dest="sso", action="store_false",
                        help="Use username + password instead of SSO")
    parser.set_defaults(sso=DEFAULT_SSO)
    parser.add_argument("--list",     action="store_true",
                        help="List currently active SAP sessions and exit")
    args = parser.parse_args()

    if args.list:
        sessions = list_logon_entries()
        if sessions:
            print(f"\nActive SAP sessions ({len(sessions)}):")
            for s in sessions:
                print(f"  [{s['conn_idx']}:{s['sess_idx']}]  "
                      f"{s['system']}/{s['client']}  user={s['user']}  tcode={s['tcode']}")
        else:
            print("No active SAP sessions found.")
        return

    mode = "SSO" if args.sso else f"password (user={args.user or 'prompt'})"
    print(f"\nConnecting to {args.system} / client {args.client}  [{mode}] ...")

    try:
        sap = connect_to_system(
            system   = args.system,
            client   = args.client,
            user     = args.user,
            language = args.language,
            sso      = args.sso,
        )
        info = sap.get_session_info()
        print(f"\n[OK] Connected: {info['system']} / {info['client']} / {info['user']}")
        print(f"  Transaction : {info['transaction']}")
        print(f"  Server      : {info['response_time']} ms response")
        print()
        print("Use in other scripts:")
        print("    from sap_connect import connect_to_system")
        print(f"    sap = connect_to_system('{args.system}', client='{args.client}')")
        print()

    except (ConnectionError, RuntimeError) as exc:
        log.error(str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()
