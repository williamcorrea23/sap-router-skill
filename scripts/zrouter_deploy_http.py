#!/usr/bin/env python3
"""
ZROUTER Deploy via SAP ADT REST API (HTTP direct — no MCP needed).

Creates all ZROUTER ABAP objects using raw ADT HTTP calls.
Credentials from .env or environment.

Usage:
  python scripts/zrouter_deploy_http.py --split-only    # Just split template
  python scripts/zrouter_deploy_http.py --create-only   # Create objects (no source)
  python scripts/zrouter_deploy_http.py --full           # Split + create + write source
  python scripts/zrouter_deploy_http.py --activate       # Activate all ZROUTER objects
"""

import os
import re
import sys
import json
import base64
import urllib.request
import urllib.error
import argparse
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "templates" / "zrouter_dispatch.prog.abap"
DEPLOY_DIR = SKILL_DIR / "deploy" / "zrouter" / "split"
DEPLOY_DIR.mkdir(parents=True, exist_ok=True)

# --- Load .env ---
try:
    from dotenv import load_dotenv
    load_dotenv(SKILL_DIR / ".env")
except ImportError:
    pass

SAP_URL = os.environ.get("ARC_SAP_URL") or os.environ.get("SAP_URL")
SAP_USER = os.environ.get("ARC_SAP_USER") or os.environ.get("SAP_USER")
SAP_PASSWORD = os.environ.get("ARC_SAP_PASSWORD") or os.environ.get("SAP_PASSWORD")
SAP_CLIENT = os.environ.get("ARC_SAP_CLIENT") or os.environ.get("SAP_CLIENT")
if not all([SAP_URL, SAP_USER, SAP_PASSWORD, SAP_CLIENT]):
    raise SystemExit("Missing ARC_SAP_URL/ARC_SAP_USER/ARC_SAP_PASSWORD/ARC_SAP_CLIENT for ZROUTER HTTP deploy.")

# --- ADT REST API helpers ---
AUTH_HEADER = "Basic " + base64.b64encode(f"{SAP_USER}:{SAP_PASSWORD}".encode()).decode()
BASE_HEADERS = {
    "Authorization": AUTH_HEADER,
    "Content-Type": "application/xml",
    "Accept": "application/xml",
}
import ssl
SSL_CTX = ssl.create_default_context()
if os.environ.get("SAP_ALLOW_UNAUTHORIZED", "").lower() == "true":
    if os.environ.get("SAP_ENV", "").upper() in {"PROD", "PRD", "PRODUCTION"}:
        raise SystemExit("Refusing insecure TLS in production. Configure a trusted CA instead.")
    SSL_CTX.check_hostname = False
    SSL_CTX.verify_mode = ssl.CERT_NONE


# CSRF token cache + session cookies
_csrf_token = None
import http.cookiejar
_cookie_jar = http.cookiejar.CookieJar()
_opener = None

def _get_opener():
    """Get or create a persistent URL opener with cookie handling."""
    global _opener
    if _opener is None:
        https_handler = urllib.request.HTTPSHandler(context=SSL_CTX)
        cookie_handler = urllib.request.HTTPCookieProcessor(_cookie_jar)
        _opener = urllib.request.build_opener(https_handler, cookie_handler)
    return _opener


def _get_csrf_token():
    """Fetch CSRF token from SAP ADT (required for POST/PUT/DELETE)."""
    global _csrf_token
    if _csrf_token:
        return _csrf_token
    url = f"{SAP_URL}/sap/bc/adt/oo/classes?_client={SAP_CLIENT}"
    headers = {**BASE_HEADERS, "X-CSRF-Token": "fetch"}
    req = urllib.request.Request(url, headers=headers, method="GET")
    opener = _get_opener()
    try:
        with opener.open(req, timeout=30) as resp:
            _csrf_token = resp.headers.get("x-csrf-token", "")
            print("  CSRF token obtained.")
            return _csrf_token
    except urllib.error.HTTPError as e:
        token = e.headers.get("x-csrf-token", "") if hasattr(e, 'headers') else ""
        if token:
            _csrf_token = token
            return token
        print(f"  CSRF fetch error: HTTP {e.code} - {e.read().decode('utf-8', errors='replace')[:200]}")
        return ""


def adt_request(method, path, data=None, content_type="application/xml"):
    """Make ADT REST API request."""
    url = f"{SAP_URL}{path}?_client={SAP_CLIENT}"
    headers = {**BASE_HEADERS, "Content-Type": content_type}

    # Add CSRF token for mutating requests
    if method in ("POST", "PUT", "DELETE", "PATCH"):
        token = _get_csrf_token()
        if token:
            headers["X-CSRF-Token"] = token

    body = data.encode("utf-8") if isinstance(data, str) else data

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    opener = _get_opener()
    try:
        with opener.open(req, timeout=30) as resp:
            result = resp.read()
            return {"status": resp.status, "body": result.decode("utf-8", errors="replace")}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        return {"status": e.code, "error": body}


def create_class(name, description="ZROUTER Class", super_class=None):
    """Create ABAP class via ADT."""
    abap_lang = SAP_CLIENT
    xml = f'''<?xml version="1.0" encoding="utf-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:name="{name}" adtcore:parentName="{SAP_CLIENT}" adtcore:type="CLAS/OC">
<adtcore:properties>
<adtcore:property adtcore:name="ABAP_LANGUAGE_VERSION" adtcore:value="STANDARD"/>
<adtcore:property adtcore:name="DESCRIPTION" adtcore:value="{description}"/>
<adtcore:property adtcore:name="EXPOSURE" adtcore:value="PUBLIC"/>
<adtcore:property adtcore:name="FIX_POINT_ARITHMETIC" adtcore:value="false"/>
'''
    if super_class:
        xml += f'<adtcore:property adtcore:name="SUPER_CLASS" adtcore:value="{super_class}"/>\n'
    xml += '''</adtcore:properties>
</adtcore:objectReference>
</adtcore:objectReferences>'''
    return adt_request("POST", "/sap/bc/adt/oo/classes", xml)


def create_interface(name, description="ZROUTER Interface"):
    """Create ABAP interface via ADT."""
    xml = f'''<?xml version="1.0" encoding="utf-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:name="{name}" adtcore:parentName="{SAP_CLIENT}" adtcore:type="INTF/OI">
<adtcore:properties>
<adtcore:property adtcore:name="ABAP_LANGUAGE_VERSION" adtcore:value="STANDARD"/>
<adtcore:property adtcore:name="DESCRIPTION" adtcore:value="{description}"/>
<adtcore:property adtcore:name="EXPOSURE" adtcore:value="PUBLIC"/>
</adtcore:properties>
</adtcore:objectReference>
</adtcore:objectReferences>'''
    return adt_request("POST", "/sap/bc/adt/oo/interfaces", xml)


def write_source(object_type, name, source_code):
    """Write ABAP source code via ADT."""
    if object_type == "CLAS":
        path = f"/sap/bc/adt/oo/classes/{name.lower()}/source/main"
    else:
        path = f"/sap/bc/adt/oo/interfaces/{name.lower()}/source/main"
    return adt_request("PUT", path, source_code, "text/plain; charset=utf-8")


def activate(object_type, name):
    """Activate ABAP object via ADT."""
    uri = f"/sap/bc/adt/oo/classes/{name.lower()}" if object_type == "CLAS" else f"/sap/bc/adt/oo/interfaces/{name.lower()}"
    xml = f'''<?xml version="1.0" encoding="utf-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:name="{name}" adtcore:type="{object_type}/OC" adtcore:uri="{uri}">
</adtcore:objectReference>
</adtcore:objectReferences>'''
    return adt_request("POST", "/sap/bc/adt/activation", xml)


# --- Parse template ---
def split_template():
    with open(TEMPLATE, encoding="utf-8", errors="replace") as f:
        content = f.read()

    objects = []
    current_name = None
    current_type = None
    current_lines = []
    in_object = False
    depth = 0

    for line in content.split("\n"):
        m_cls = re.match(r"^(CLASS|INTERFACE)\s+(\w+)\s+(DEFINITION|PUBLIC)", line, re.IGNORECASE)
        if m_cls and not in_object:
            current_type = "INTF" if m_cls.group(1).upper() == "INTERFACE" else "CLAS"
            current_name = m_cls.group(2).upper()
            current_lines = [line]
            in_object = True
            depth = 1
            continue

        if in_object:
            current_lines.append(line)
            if re.match(r"^\s*(CLASS|INTERFACE)\s", line, re.IGNORECASE):
                depth += 1
            if re.match(r"^\s*ENDCLASS\.", line, re.IGNORECASE):
                depth -= 1
                if depth == 0:
                    objects.append({"name": current_name, "type": current_type, "lines": current_lines})
                    in_object = False
            elif re.match(r"^\s*ENDINTERFACE\.", line, re.IGNORECASE):
                depth -= 1
                if depth == 0:
                    objects.append({"name": current_name, "type": current_type, "lines": current_lines})
                    in_object = False

    # Save split files
    for obj in objects:
        out_path = DEPLOY_DIR / f"{obj['name']}.abap"
        source = "\n".join(obj["lines"])
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(source)

    return objects


CREATE_ORDER = [
    ("CX_ZROUTER", "CLAS", "CX_STATIC_CHECK"),
    ("ZIF_ZROUTER_HANDLER", "INTF", None),
    ("ZIF_ZROUTER_CONFIG", "INTF", None),
    ("ZIF_ZROUTER_LOGGER", "INTF", None),
    ("ZCL_ZROUTER_CONFIG", "CLAS", None),
    ("ZCL_ZROUTER_LOGGER", "CLAS", None),
    ("ZCL_ZROUTER_AUTHORITY", "CLAS", None),
    ("ZCL_ZROUTER_HANDLER_ABSTRACT", "CLAS", None),
    ("ZCL_ZROUTER_HANDLER_MM", "CLAS", "ZCL_ZROUTER_HANDLER_ABSTRACT"),
    ("ZCL_ZROUTER_HANDLER_SD", "CLAS", "ZCL_ZROUTER_HANDLER_ABSTRACT"),
    ("ZCL_ZROUTER_HANDLER_FI", "CLAS", "ZCL_ZROUTER_HANDLER_ABSTRACT"),
    ("ZCL_ZROUTER_HANDLER_QM", "CLAS", "ZCL_ZROUTER_HANDLER_ABSTRACT"),
    ("ZCL_ZROUTER_HANDLER_PP", "CLAS", "ZCL_ZROUTER_HANDLER_ABSTRACT"),
    ("ZCL_ZROUTER_HANDLER_WM", "CLAS", "ZCL_ZROUTER_HANDLER_ABSTRACT"),
    ("ZCL_ZROUTER_HANDLER_CO", "CLAS", "ZCL_ZROUTER_HANDLER_ABSTRACT"),
    ("ZCL_ZROUTER_HANDLER_HCM", "CLAS", "ZCL_ZROUTER_HANDLER_ABSTRACT"),
    ("ZCL_ZROUTER_HANDLER_BASIS", "CLAS", "ZCL_ZROUTER_HANDLER_ABSTRACT"),
    ("ZCL_ZROUTER_DISPATCH", "CLAS", None),
    ("ZCL_ZROUTER_BATCH", "CLAS", None),
]


def main():
    parser = argparse.ArgumentParser(description="ZROUTER Deploy via SAP ADT REST API")
    parser.add_argument("--split-only", action="store_true")
    parser.add_argument("--create-only", action="store_true")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--activate", action="store_true")
    parser.add_argument("--object", help="Single object name to process")
    args = parser.parse_args()

    print(f"SAP URL: {SAP_URL}")
    print(f"User: {SAP_USER}")

    if args.split_only or args.full:
        print("\n--- Splitting template ---")
        objects = split_template()
        print(f"Split {len(objects)} objects to {DEPLOY_DIR}")

    if args.create_only or args.full:
        print("\n--- Creating objects ---")
        obj_map = {o["name"]: o for o in split_template()}

        for name, obj_type, super_cls in CREATE_ORDER:
            if args.object and args.object.upper() != name:
                continue

            print(f"\n{obj_type} {name}...")

            if obj_type == "INTF":
                result = create_interface(name)
            else:
                result = create_class(name, super_class=super_cls)

            if result["status"] in (200, 201):
                print(f"  Created OK (HTTP {result['status']})")
            elif result["status"] == 409:
                print(f"  Already exists (HTTP 409) — skipping")
            else:
                print(f"  ERROR HTTP {result['status']}: {result.get('error', '')[:200]}")
                continue

            # Write source
            if name in obj_map:
                source = "\n".join(obj_map[name]["lines"])
                result2 = write_source(obj_type, name, source)
                if result2["status"] in (200, 201, 204):
                    print(f"  Source written OK")
                else:
                    print(f"  SOURCE ERROR HTTP {result2['status']}: {result2.get('error', '')[:200]}")

    if args.activate:
        print("\n--- Activating objects ---")
        for name, obj_type, _ in CREATE_ORDER:
            if args.object and args.object.upper() != name:
                continue
            print(f"Activating {obj_type} {name}...")
            result = activate(obj_type, name)
            if result["status"] in (200, 201, 204):
                print(f"  OK")
            else:
                print(f"  HTTP {result['status']}: {result.get('error', '')[:200]}")


if __name__ == "__main__":
    main()
