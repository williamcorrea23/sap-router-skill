"""pyautogui SAP GUI F8 activation — with AttachThreadInput for focus sharing."""
import subprocess, time, sys, os
import pyautogui
pyautogui.FAILSAFE = False
import win32gui, win32con, ctypes
from ctypes import wintypes

# Allow foreground window
ASFW = ctypes.windll.user32.AllowSetForegroundWindow
ASFW.argtypes = [wintypes.DWORD]
ASFW.restype = wintypes.BOOL
ASFW(-1)  # Allow all callers to set foreground

def find_sap_window():
    best = None; best_sz = 0
    def enum_cb(hwnd, _):
        nonlocal best, best_sz
        if win32gui.IsWindowVisible(hwnd):
            t = win32gui.GetWindowText(hwnd)
            if 'SAP' in t and 'Logon' not in t and 'Caracter' not in t:
                r = win32gui.GetWindowRect(hwnd)
                sz = (r[2]-r[0])*(r[3]-r[1])
                if sz > best_sz:
                    best_sz = sz
                    best = hwnd
        return True
    win32gui.EnumWindows(enum_cb, None)
    return best

def focus_and_click(hwnd):
    """Ensure SAP window has focus using AttachThreadInput trick."""
    curr = ctypes.windll.kernel32.GetCurrentThreadId()
    target = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None)
    if curr != target:
        ctypes.windll.user32.AttachThreadInput(curr, target, True)
    try:
        win32gui.SetForegroundWindow(hwnd)
    except:
        pass
    time.sleep(0.2)
    # Click center of window to transfer focus
    r = win32gui.GetWindowRect(hwnd)
    cx = (r[0] + r[2]) // 2
    cy = (r[1] + r[3]) // 2
    pyautogui.click(cx, cy)
    time.sleep(0.5)

# ===== MAIN =====
print("=== SAP GUI F8 Activation ===")

# Find SAP window
hwnd = find_sap_window()
if not hwnd:
    print("SAP GUI not running. Launching...")
    subprocess.Popen([
        r"C:\Program Files\SAP\FrontEnd\SAPgui\sapshcut.exe",
        "-system=10.57.203.136/00", "-client=100",
        "-user=30356735869", "-pw=Fodase@APPA2026",
        "-language=EN", "-command=/nSE38"
    ])
    time.sleep(15)
    hwnd = find_sap_window()

if not hwnd:
    print("FATAL: Cannot find SAP GUI window")
    sys.exit(1)

r = win32gui.GetWindowRect(hwnd)
print(f"SAP window: hwnd={hwnd} rect={r}")

# Maximize if small
if r[2] - r[0] < 800:
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
    time.sleep(1)
    r = win32gui.GetWindowRect(hwnd)

focus_and_click(hwnd)

# Click on the OK code field (top-left toolbar input)
ok_x = r[0] + 150
ok_y = r[1] + 55
print(f"Clicking OK field at ({ok_x}, {ok_y})")
pyautogui.click(ok_x, ok_y)
time.sleep(0.5)

# Clear and type /nSE38
pyautogui.hotkey('ctrl', 'a')
time.sleep(0.1)
pyautogui.write('/nSE38', interval=0.05)
time.sleep(0.3)
pyautogui.press('enter')
time.sleep(3)

# Now in SE38 — type program name
print("Typing ZROUTER_ACTIVATE...")
pyautogui.write('ZROUTER_ACTIVATE', interval=0.05)
time.sleep(0.5)
pyautogui.press('enter')  # This opens the program in editor
time.sleep(2)

# FOCUS: click on the editor area to ensure focus
editor_x = r[0] + 300
editor_y = r[1] + 250
print(f"Clicking editor area at ({editor_x}, {editor_y})")
pyautogui.click(editor_x, editor_y)
time.sleep(0.5)

# Try F8
print(">>> Pressing F8 (Execute)...")
pyautogui.press('f8')
time.sleep(3)

# Also try: click Execute toolbar button directly
# SAP GUI toolbar 1 button positions (approx at 1920px width, after menu bar)
print(">>> Clicking Execute button...")
# The execute button is typically around x=280-310 from window left in SE38
btn_x = r[0] + 290
btn_y = r[1] + 90
pyautogui.click(btn_x, btn_y)
time.sleep(2)

# One more: Ctrl+F3 (Back/Activate) as alternative
print(">>> Trying Ctrl+F3 (Activate)...")
pyautogui.hotkey('ctrl', 'f3')
time.sleep(2)

print("Done. All F8/Ctrl+F3/button clicks attempted.")
print("Check SAP GUI screen manually to verify.")
