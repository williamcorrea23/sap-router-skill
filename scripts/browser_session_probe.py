#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.request


def cdp_url() -> str:
    if os.environ.get("BROWSER_CDP_URL"):
        return os.environ["BROWSER_CDP_URL"].rstrip("/")
    port = os.environ.get("CHROME_DEBUGGING_PORT", "9222")
    return f"http://127.0.0.1:{port}"


def main() -> int:
    cpi_url = os.environ.get("CPI_WEB_URL")
    apim_url = os.environ.get("APIM_WEB_URL")
    base_url = cpi_url or apim_url
    if not base_url:
        result = {
            "status": "UNAVAILABLE",
            "reason": "CPI_WEB_URL or APIM_WEB_URL missing",
            "session": "not_checked",
        }
        print(json.dumps(result, indent=2))
        return 1
    endpoint = cdp_url() + "/json/version"
    try:
        with urllib.request.urlopen(endpoint, timeout=3) as response:
            payload = json.loads(response.read().decode("utf-8", errors="replace") or "{}")
        result = {
            "status": "READY",
            "url_configured": True,
            "cdp_url": cdp_url(),
            "browser": payload.get("Browser", "unknown"),
            "websocket": bool(payload.get("webSocketDebuggerUrl")),
            "reason": "Chrome/CDP reachable; logged-in session can be reused if user is already authenticated.",
        }
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        result = {
            "status": "DEGRADED",
            "url_configured": True,
            "cdp_url": cdp_url(),
            "reason": f"Chrome/CDP not reachable: {exc}",
            "fix": "Start Chrome with remote debugging, e.g. chrome.exe --remote-debugging-port=9222 --user-data-dir=%TEMP%\\sap-router-chrome, then log in to the tenant.",
        }
        print(json.dumps(result, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
