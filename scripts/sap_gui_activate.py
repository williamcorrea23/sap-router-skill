"""Activate ABAP objects via SAP GUI automation — SE38 ZROUTER_ACTIVATE F8"""
import subprocess, time, sys
import pyautogui
pyautogui.FAILSAFE = False

import win32gui, win32con, win32api, ctypes
from ctypes import wintypes

# --- AllowSetForegroundWindow (bypass foreground lock) ---
ASFW = ctypes.windll.user32.AllowSetForegroundWindow
ASFW.argtypes = [wintypes.DWORD]
ASFW.restype = wintypes.BOOL
ASFW(-1)

# --- Find SAP window ---
def find_sap():
    state = {'best': None, 'best_sz': 0}
    def f(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            t = win32gui.GetWindowText(hwnd)
            if 'SAP' in t and 'Logon' not in t and 'Caracter' not in t:
                r = win32gui.GetWindowRect(hwnd)
                sz = (r[2]-r[0])*(r[3]-r[1])
                if sz > state['best_sz']:
                    state['best_sz'] = sz
                    state['best'] = hwnd
        return True
    win32gui.EnumWindows(f, None)
    return state['best']

# --- Launch SAP GUI if not running ---
hwnd = find_sap()
if not hwnd:
    print("SAP GUI not running. Launching...")
    subprocess.Popen([
        r"C:\Program Files\SAP\FrontEnd\SAPgui\sapshcut.exe",
        "-system=10.57.203.136/00", "-client=100",
        "-user=30356735869", "-pw=Fodase@APPA2026", "-language=EN"
    ])
    time.sleep(8)
    hwnd = find_sap()

if not hwnd:
    print("ERROR: Cannot find SAP GUI window")
    sys.exit(1)

print(f"SAP GUI window found: hwnd={hwnd}")

# Move on-screen and maximize
r = win32gui.GetWindowRect(hwnd)
if r[0] < -1000 or r[2] < 100:
    print(f"Window off-screen at {r}, moving to (0,0)")
    win32gui.MoveWindow(hwnd, 0, 0, r[2]-r[0], r[3]-r[1], True)
    time.sleep(0.5)

win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
time.sleep(0.5)

# --- AttachThreadInput for focus sharing ---
current_thread = ctypes.windll.kernel32.GetCurrentThreadId()
target_thread = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None)
if current_thread != target_thread:
    ctypes.windll.user32.AttachThreadInput(current_thread, target_thread, True)

try:
    win32gui.SetForegroundWindow(hwnd)
except Exception as e:
    print(f"SetForegroundWindow: {e}")

time.sleep(0.3)

# Click on window to transfer focus
r = win32gui.GetWindowRect(hwnd)
cx = (r[0] + r[2]) // 2
cy = (r[1] + r[3]) // 2
pyautogui.click(cx, cy)
time.sleep(0.5)

# --- Navigate to SE38 ---
print("Navigating to SE38...")
# Click OK box first (top-left area where command field usually is)
pyautogui.click(r[0] + 100, r[1] + 60)
time.sleep(0.3)
pyautogui.hotkey('ctrl', 'a')  # Select all in command field
time.sleep(0.1)
pyautogui.write('/nSE38', interval=0.05)
time.sleep(0.3)
pyautogui.press('enter')
time.sleep(2)

# --- Type program name ---
print("Typing ZROUTER_ACTIVATE...")
pyautogui.write('ZROUTER_ACTIVATE', interval=0.05)
time.sleep(0.5)
pyautogui.press('enter')
time.sleep(1)

# --- Try F8 to execute ---
print("Attempting F8...")
pyautogui.press('f8')
time.sleep(2)

# --- Check if F8 worked by looking for result ---
# If F8 failed, try clicking the Execute toolbar button
# The execute button is usually the 8th toolbar icon (gears icon)
print("Checking if SAP is still on SE38 editor screen...")
# Try clicking Execute icon area (roughly x=320, y=100 from window corner)
try:
    ex = r[0] + 320
    ey = r[1] + 100
    print(f"Clicking Execute button at ({ex}, {ey})...")
    pyautogui.click(ex, ey)
    time.sleep(2)
except Exception as e:
    print(f"Execute button click failed: {e}")

# --- Try menu Program > Execute > Direct ---
print("Trying menu: Alt+P for Program, then Execute...")
pyautogui.press('alt')
time.sleep(0.3)
pyautogui.press('p')  # Program menu
time.sleep(0.5)
pyautogui.press('f8')  # Execute (might be F8 shortcut in menu)
time.sleep(0.5)
# If menu is open, try letter 'e' for Execute
pyautogui.press('e')
time.sleep(2)

print("Done. Activate result: check SAP GUI screen.")
