#!/usr/bin/env python3
"""Read an existing SAP GUI session/window. Never log on or navigate."""
import json
import platform


def probe():
    if platform.system() != 'Windows':
        return {'status': 'UNAVAILABLE', 'reason': 'Windows COM is required.'}
    try:
        import win32com.client
        application = win32com.client.GetObject('SAPGUI').GetScriptingEngine
        for i in range(application.Children.Count):
            connection = application.Children(i)
            for j in range(connection.Children.Count):
                session = connection.Children(j)
                if session.Busy:
                    continue
                window = session.FindById('wnd[0]')
                if window and isinstance(window.Text, str):
                    return {'status': 'READY', 'session_read': True, 'screen_read': True}
        return {'status': 'DEGRADED', 'reason': 'No readable, non-busy session.'}
    except ImportError:
        return {'status': 'UNAVAILABLE', 'reason': 'pywin32 is not installed in the selected Python runtime.'}
    except Exception as exc:
        return {'status': 'UNAVAILABLE', 'reason': type(exc).__name__ + ': existing GUI session unavailable.'}


if __name__ == '__main__':
    result = probe()
    print(json.dumps(result))
    raise SystemExit(0 if result['status'] == 'READY' else 1)
