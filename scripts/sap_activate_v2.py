"""SAP GUI activation — maximize window, use OK code or Alt menu instead of F8."""
import subprocess, time, sys
import pyautogui
pyautogui.FAILSAFE = False
import win32gui, win32con, ctypes
from ctypes import wintypes

ASFW = ctypes.windll.user32.AllowSetForegroundWindow
ASFW.argtypes = [wintypes.DWORD]
ASFW.restype = wintypes.BOOL
ASFW(-1)

def find_sap():
    best = None; best_sz = 0
    def cb(hwnd, _):
        nonlocal best, best_sz
        if win32gui.IsWindowVisible(hwnd):
            t = win32gui.GetWindowText(hwnd)
            if 'SAP' in t and 'Logon' not in t and 'Caracter' not in t:
                r = win32gui.GetWindowRect(hwnd)
                sz = (r[2]-r[0])*(r[3]-r[1])
                if sz > best_sz: best_sz = sz; best = hwnd
        return True
    win32gui.EnumWindows(cb, None)
    return best

def attach_and_focus(hwnd):
    curr = ctypes.windll.kernel32.GetCurrentThreadId()
    target = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None)
    if curr != target:
        ctypes.windll.user32.AttachThreadInput(curr, target, True)
    try:
        win32gui.SetForegroundWindow(hwnd)
    except: pass
    time.sleep(0.3)
    r = win32gui.GetWindowRect(hwnd)
    pyautogui.click((r[0]+r[2])//2, (r[1]+r[3])//2)
    time.sleep(0.5)

# === MAIN ===
hwnd = find_sap()
if not hwnd:
    print("Launching SAP GUI...")
    subprocess.Popen([
        r"C:\Program Files\SAP\FrontEnd\SAPgui\sapshcut.exe",
        "-system=10.57.203.136/00", "-client=100",
        "-user=30356735869", "-pw=Fodase@APPA2026",
        "-language=EN", "-command=/nSE38"
    ])
    time.sleep(15)
    hwnd = find_sap()

if not hwnd:
    print("FATAL: no SAP window")
    sys.exit(1)

# MAXIMIZE
print("Maximizing SAP GUI...")
win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
time.sleep(1)
r = win32gui.GetWindowRect(hwnd)
print(f"Window rect: {r} size: {r[2]-r[0]}x{r[3]-r[1]}")

attach_and_focus(hwnd)
time.sleep(0.5)

# Navigate to SE38
print("Navigating to SE38...")
ok_x = r[0] + 150
ok_y = r[1] + 55
pyautogui.click(ok_x, ok_y)
time.sleep(0.3)
pyautogui.hotkey('ctrl', 'a')
time.sleep(0.1)
pyautogui.write('/nSE38', interval=0.05)
time.sleep(0.3)
pyautogui.press('enter')
time.sleep(3)

# Type program name
print("Loading ZROUTER_ACTIVATE...")
pyautogui.write('ZROUTER_ACTIVATE', interval=0.05)
time.sleep(0.5)
pyautogui.press('enter')
time.sleep(2)

# APPROACH 1: OK code "EXEC"
print("Trying OK code EXEC + Enter...")
pyautogui.click(ok_x, ok_y)
time.sleep(0.2)
pyautogui.hotkey('ctrl', 'a')
time.sleep(0.1)
pyautogui.write('EXEC', interval=0.05)
time.sleep(0.3)
pyautogui.press('enter')
time.sleep(3)

# APPROACH 2: Alt menu Program → Execute
print("Trying Alt+P menu → E (Execute)...")
pyautogui.press('alt')
time.sleep(0.3)
pyautogui.press('p')  # Program menu
time.sleep(0.5)
pyautogui.press('f8')  # Try F8 while menu is open
time.sleep(0.3)
pyautogui.press('enter')
time.sleep(2)

# APPROACH 3: Try F8 again (maybe maximize helped)
print("Final F8 attempt...")
pyautogui.click(r[0] + 300, r[1] + 300)  # Click editor area
time.sleep(0.5)
pyautogui.press('f8')
time.sleep(3)

print("All approaches attempted. Check status.")
