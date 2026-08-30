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


def apim_oauth_configured() -> bool:
    """The APIM bridge prefers the documented service-key channel, which needs no browser."""
    if os.environ.get("APIM_SERVICE_KEY_FILE"):
        return True
    return all(
        os.environ.get(name)
        for name in ("APIM_API_URL", "APIM_TOKEN_URL", "APIM_CLIENT_ID", "APIM_CLIENT_SECRET")
    )


def main() -> int:
    cpi_url = os.environ.get("CPI_WEB_URL")
    apim_url = os.environ.get("APIM_WEB_URL")
    base_url = cpi_url or apim_url
    # A configured APIM service key settles the APIM case on its own: that channel
    # needs no browser, so requiring one would report a working tenant as degraded.
    # CPI_WEB_URL means this probe is being run for CPI, where the key does not apply.
    if not cpi_url and apim_oauth_configured():
        print(json.dumps({
            "status": "READY",
            "channel": "oauth",
            "reason": "APIM service key configured; the browser session channel is not needed.",
            "session": "not_required",
        }, indent=2))
        return 0
    if not base_url:
        result = {
            "status": "UNAVAILABLE",
            "reason": "no APIM service key, and CPI_WEB_URL or APIM_WEB_URL missing",
            "session": "not_checked",
            "fix": "Set APIM_SERVICE_KEY_FILE for the documented channel, or CPI_WEB_URL/APIM_WEB_URL for the browser session fallback.",
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
