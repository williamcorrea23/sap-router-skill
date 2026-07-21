#!/usr/bin/env python3
"""
SAP ADT REST API client — fills capability gaps not covered by adt-mcp-server.
Supports: search, list objects/packages, read/write source, transports,
          ATC checks, delete, where-used, change history, active/inactive diff,
          CDS data definitions, text elements (selections/symbols/headings).
"""

import argparse
import difflib
import json
import os
import re
import sys
import time
import urllib.parse

import requests
import urllib3
from requests.auth import HTTPBasicAuth

# TLS verification defaults to enabled. `urllib3` warning suppression is
# performed only when the user explicitly opts into insecure mode via
# `--insecure` or `SAP_ADT_INSECURE=1`. See `_resolve_tls_verify` below.

_ENV_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})


# ── Type path map (module-level, shared by all commands) ─────────────────────

TYPE_PATH_MAP = {
    "PROG/P":  "programs/programs",
    "CLAS/OC": "oo/classes",
    "INTF/OI": "oo/interfaces",
    "FUGR/FF": "functions/groups",
    "MSAG/N":  "messageclass",
    "TRAN/T":  "vit/wb/object_type/tran",
    "DEVC/K":  "packages",
    "FUNC/FF": "functions/functionModules",
    "DDLS/DF": "ddic/ddl/sources",
}

# Object-class suffix used in the text elements REST path
TEXT_ELEM_CLASS_MAP = {
    "PROG/P":  "programs",
    "FUGR/FF": "functiongroups",
    "CLAS/OC": "classes",
}

# Content-type for each text element section (GET Accept / PUT Content-Type)
TEXT_ELEM_SECTIONS = {
    "selections": "application/vnd.sap.adt.textelements.selections.v1",
    "symbols":    "application/vnd.sap.adt.textelements.symbols.v1",
    "headings":   "application/vnd.sap.adt.textelements.headings.v1",
}


# ── Destination-based credential resolution ──────────────────────────────────

def _env_or_registry(name: str) -> str | None:
    """User env var, falling back to HKCU\\Environment — `setx` values never
    reach an already-running parent process, only the registry sees them."""
    val = os.environ.get(name)
    if val:
        return val
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            return winreg.QueryValueEx(key, name)[0]
    except (ImportError, OSError):
        return None


def _resolve_destination(args) -> None:
    """Fill url/user/pwd/client/lang from a destination name like DEV_100_DEVELOPER_EN.

    Resolution order (explicit flags always win):
      url     SAP_<SID>_URL
      user    SAP_<SID>_<USER>_USER, else the <USER> part of the destination
      pwd     SAP_<SID>_<USER>_PWD   (must exist — never passed on the CLI)
      client / lang  from the destination name

    Set the secrets once per system, in a shell the agent does not run:
      setx SAP_DEV_URL "https://host:44300"
      setx SAP_DEV_DEVELOPER_PWD "<password>"
    """
    parts = args.dest.split("_")
    if len(parts) != 4:
        raise SystemExit(json.dumps({
            "error": f"--dest must look like SID_CLIENT_USER_LANG "
                     f"(e.g. DEV_100_DEVELOPER_EN), got: {args.dest}"}))
    sid, client, user, lang = (x.upper() for x in parts)
    if not args.url:
        args.url = _env_or_registry(f"SAP_{sid}_URL")
    if not args.user:
        args.user = _env_or_registry(f"SAP_{sid}_{user}_USER") or user
    if not args.pwd:
        args.pwd = _env_or_registry(f"SAP_{sid}_{user}_PWD")
    if not args.client:
        args.client = client
    if not args.lang:
        args.lang = lang
    missing = ([f"SAP_{sid}_URL"] if not args.url else []) \
        + ([f"SAP_{sid}_{user}_PWD"] if not args.pwd else [])
    if missing:
        raise SystemExit(json.dumps({
            "error": f"Missing connection values for --dest {args.dest}",
            "set_once_with": [f'setx {m} "<value>"' for m in missing]}))


# ── TLS verification ─────────────────────────────────────────────────────────

def _parse_env_bool(value: str | None) -> bool:
    """Return True when a str env value opts in (1/true/yes/on, case insensitive)."""
    if value is None:
        return False
    return value.strip().lower() in _ENV_TRUE_VALUES


def _resolve_tls_verify(args, env: dict | None = None):
    """Resolve requests-style `verify` from CLI args and environment.

    Returns True (verify with system CA trust store), False (disabled),
    or a string path to a custom CA bundle.

    Precedence:
        --insecure                 disables verification (CLI wins over env)
        --ca-bundle <path>         use that path (CLI wins over env)
        SAP_ADT_CA_BUNDLE          use that path
        SAP_ADT_INSECURE           disables verification when truthy
        (default)                  True — use system CA trust store

    Combining --insecure or SAP_ADT_INSECURE with an explicit CA bundle is
    a configuration error and is rejected with SystemExit and a JSON body.
    """
    env = os.environ if env is None else env
    cli_insecure = bool(getattr(args, "insecure", False))
    cli_ca_bundle = getattr(args, "ca_bundle", None) or None
    env_ca_bundle = env.get("SAP_ADT_CA_BUNDLE") or None
    env_insecure = _parse_env_bool(env.get("SAP_ADT_INSECURE"))

    effective_insecure = cli_insecure or (env_insecure and not cli_ca_bundle)
    effective_ca_bundle = cli_ca_bundle or (None if cli_insecure else env_ca_bundle)

    if effective_insecure and effective_ca_bundle:
        raise SystemExit(json.dumps({
            "error": "Conflicting TLS options: --insecure/SAP_ADT_INSECURE cannot be "
                     "combined with --ca-bundle/SAP_ADT_CA_BUNDLE.",
            "hint": "Pick one: either supply a CA bundle for secure verification, "
                    "or use --insecure explicitly for controlled troubleshooting.",
        }))

    if effective_insecure:
        return False
    if effective_ca_bundle:
        return effective_ca_bundle
    return True


def _warn_insecure_once(verify) -> None:
    """When verification is off, warn on stderr and suppress only the expected
    urllib3 insecure-request warning. Never print credentials or headers."""
    if verify is False:
        sys.stderr.write(
            "WARNING: TLS certificate verification is disabled (--insecure). "
            "This is unsafe. Prefer --ca-bundle <path> or SAP_ADT_CA_BUNDLE "
            "for corporate SAP systems with private CAs.\n"
        )
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ── Session ──────────────────────────────────────────────────────────────────

class _AdtSession(requests.Session):
    """Session with a default timeout so a hung SAP system can't hang the CLI."""

    def request(self, *pargs, **kwargs):
        kwargs.setdefault("timeout", 120)
        return super().request(*pargs, **kwargs)


def make_session(url: str, user: str, pwd: str, client: str, lang: str,
                 verify=True) -> requests.Session:
    """Build authenticated session with CSRF token.

    `verify` follows the requests convention: True (default) enables
    verification with the system CA trust store, False disables it,
    and a string is a path to a custom CA bundle.
    """
    s = _AdtSession()
    s.auth = HTTPBasicAuth(user, pwd)
    s.verify = verify
    s.headers.update({
        "sap-client": client,
        "sap-language": lang,
        # Locks only survive across requests in a stateful ADT session
        "X-sap-adt-sessiontype": "stateful",
    })
    resp = s.get(f"{url}/sap/bc/adt/discovery", headers={"X-CSRF-Token": "Fetch"})
    if resp.status_code in (401, 403):
        print(json.dumps({
            "error": f"Authentication failed (HTTP {resp.status_code})",
            "hint": "Check --user / --pwd / --client",
        }))
        sys.exit(1)
    csrf = resp.headers.get("x-csrf-token", "")
    if csrf:
        s.headers["X-CSRF-Token"] = csrf
    return s


# ── XML parser ────────────────────────────────────────────────────────────────

def parse_xml_refs(xml: str) -> list[dict]:
    """Extract objectReference entries from ADT search XML response."""
    pattern = (
        r'adtcore:uri="([^"]*)"[^>]*adtcore:type="([^"]*)"'
        r'[^>]*adtcore:name="([^"]*)"'
        r'(?:[^>]*adtcore:packageName="([^"]*)")?'
        r'(?:[^>]*adtcore:description="([^"]*)")?'
    )
    return [
        {
            "uri": m.group(1),
            "type": m.group(2),
            "name": m.group(3),
            "package": m.group(4) or "",
            "description": m.group(5) or "",
        }
        for m in re.finditer(pattern, xml)
    ]


# ── Lock / Unlock helpers (used by write-source and delete) ──────────────────

def _lock(s: requests.Session, base_url: str, corr_nr: str = "") -> tuple[str, str] | tuple[None, None]:
    """Lock an ADT object. Returns (lock_handle, corr_nr) or (None, None).
    Pass corr_nr to record the lock in a specific transport (avoids auto-generated transports)."""
    lock_url = f"{base_url}?_action=LOCK&accessMode=MODIFY"
    if corr_nr:
        lock_url += f"&corrNumber={corr_nr}"
    resp = s.post(
        lock_url,
        headers={
            "X-CSRF-Token": s.headers.get("X-CSRF-Token", ""),
            # Strict endpoints (e.g. ddic/ddl/sources) return 406 without the
            # lock-result media type; harmless for the lenient ones.
            "Accept": "application/*,application/vnd.sap.as+xml;charset=UTF-8;dataname=com.sap.adt.lock.Result",
        },
    )
    m = re.search(r'adtcore:lockHandle="([^"]*)"', resp.text)
    if not m:
        m = re.search(r'lockHandle["\s:=]+([A-Za-z0-9+/=]{10,})', resp.text)
    if not m:
        # S/4HANA ABAP XML format: <LOCK_HANDLE>...</LOCK_HANDLE>
        m = re.search(r'<LOCK_HANDLE>([^<]+)</LOCK_HANDLE>', resp.text)
    if not m:
        return None, None
    handle = m.group(1)
    # Extract corr number (transport) associated with this lock
    mc = re.search(r'<CORRNR>([^<]+)</CORRNR>', resp.text)
    corr_nr = mc.group(1) if mc else ""
    return handle, corr_nr


def _unlock(s: requests.Session, base_url: str, handle: str) -> None:
    """Release an ADT object lock (best-effort — must never mask the real error;
    an unreleased lock dies with the stateful session anyway)."""
    try:
        s.post(f"{base_url}?_action=UNLOCK&lockHandle={urllib.parse.quote(handle)}")
    except requests.exceptions.RequestException:
        pass


# ── ATC XML builders ──────────────────────────────────────────────────────────

def _build_atc_objectset_xml(objects: list[dict]) -> str:
    """Build ATC worklist objectset XML (step 1 of 2-step ATC flow)."""
    refs = "\n".join(
        f'  <adtcore:objectReference adtcore:uri="{o["uri"]}" '
        f'adtcore:type="{o["type"]}" adtcore:name="{o["name"]}"/>'
        for o in objects
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
{refs}
</adtcore:objectReferences>"""


def _build_atc_run_xml(objects: list[dict]) -> str:
    """Build ATC run XML (step 2 of 2-step ATC flow)."""
    refs = "\n".join(
        f'        <adtcore:objectReference adtcore:uri="{o["uri"]}" '
        f'adtcore:type="{o["type"]}" adtcore:name="{o["name"]}"/>'
        for o in objects
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<atc:run xmlns:atc="http://www.sap.com/adt/atc" maximumVerdicts="100">
  <objectSets>
    <objectSet kind="inclusive">
      <adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
{refs}
      </adtcore:objectReferences>
    </objectSet>
  </objectSets>
</atc:run>"""


# ── Creation helpers ──────────────────────────────────────────────────────────

def _post_adt(s: requests.Session, url: str, path: str, body: str,
              content_type: str, transport: str) -> dict:
    """POST to an ADT endpoint and return a status dict."""
    params = {}
    if transport:
        params["corrNr"] = transport
    resp = s.post(
        f"{url}/sap/bc/adt/{path}",
        data=body.encode("utf-8"),
        params=params,
        headers={"Content-Type": content_type, "Accept": "application/xml"},
    )
    ok = resp.status_code in (200, 201)
    location = resp.headers.get("Location", "")
    return {
        "status": resp.status_code,
        "ok": ok,
        "location": location,
        "message": "Created" if ok else resp.text[:500],
    }


def cmd_create_package(s: requests.Session, url: str, args) -> dict:
    """Create a new ABAP package (DEVC/K) via ADT REST API."""
    sw_component = getattr(args, "sw_component", "HOME") or "HOME"
    transport_layer = getattr(args, "transport_layer", "") or ""
    layer_elem = (f'    <pak:transportLayer pak:name="{transport_layer}"/>\n'
                  if transport_layer else "")
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<pak:package
  xmlns:pak="http://www.sap.com/adt/packages"
  xmlns:adtcore="http://www.sap.com/adt/core"
  adtcore:name="{args.name.upper()}"
  adtcore:description="{args.description}"
  adtcore:responsible="{args.user}"
  adtcore:masterLanguage="EN">
  <pak:attributes pak:packageType="development"/>
  <pak:superPackage adtcore:name="{args.superpackage.upper()}"/>
  <pak:applicationComponent pak:name=""/>
  <pak:transport>
    <pak:softwareComponent pak:name="{sw_component}"/>
{layer_elem}  </pak:transport>
  <pak:useAccesses/>
  <pak:packageInterfaces/>
  <pak:subPackages/>
</pak:package>"""
    return _post_adt(s, url, "packages",
                     xml, "application/vnd.sap.adt.packages.v2+xml",
                     args.transport)


def cmd_create_program(s: requests.Session, url: str, args) -> dict:
    """Create a new ABAP executable program (PROG/P) shell via ADT REST API."""
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<program:abapProgram
  xmlns:program="http://www.sap.com/adt/programs/programs"
  xmlns:adtcore="http://www.sap.com/adt/core"
  adtcore:name="{args.name.upper()}"
  adtcore:description="{args.description}"
  adtcore:responsible="{args.user}"
  adtcore:masterLanguage="EN"
  program:programType="executableProgram">
  <adtcore:packageRef adtcore:name="{args.package.upper()}"/>
</program:abapProgram>"""
    return _post_adt(s, url, "programs/programs",
                     xml, "application/vnd.sap.adt.programs.programs.v2+xml",
                     args.transport)


def cmd_create_message_class(s: requests.Session, url: str, args) -> dict:
    """Create a new message class (MSAG/N) shell via ADT REST API."""
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<msg:messageClass
  xmlns:msg="http://www.sap.com/adt/messageClasses"
  xmlns:adtcore="http://www.sap.com/adt/core"
  adtcore:name="{args.name}"
  adtcore:description="{args.description}">
  <adtcore:packageRef adtcore:name="{args.package}"/>
</msg:messageClass>"""
    # Try newer singular path first, fallback to legacy plural
    r = _post_adt(s, url, "messageclass", xml, "application/vnd.sap.adt.messageClasses+xml", args.transport)
    if not r["ok"]:
        r = _post_adt(s, url, "messageClasses", xml, "application/vnd.sap.adt.messageClasses+xml", args.transport)
    return r


def cmd_create_transaction(s: requests.Session, url: str, args) -> dict:
    """Create a report-type transaction code (TRAN/T) via ADT REST API."""
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<tran:transaction
  xmlns:tran="http://www.sap.com/adt/vit/transaction"
  xmlns:adtcore="http://www.sap.com/adt/core"
  adtcore:name="{args.name}"
  adtcore:description="{args.description}"
  tran:type="S"
  tran:program="{args.program}"
  tran:screen="1000">
  <adtcore:packageRef adtcore:name="{args.package}"/>
</tran:transaction>"""
    return _post_adt(s, url, "vit/wb/object_type/tran",
                     xml, "application/vnd.sap.adt.vit.tran+xml",
                     args.transport)


def _msgclass_base(s: requests.Session, url: str, name: str) -> str:
    """Return the correct message class base URL (path varies by SAP release)."""
    # S/4 on-prem: /sap/bc/adt/messageclass/{name}  (singular, lowercase)
    # Older:      /sap/bc/adt/messageClasses/{name} (plural, camelCase)
    for path in (f"messageclass/{name.lower()}", f"messageClasses/{name.lower()}"):
        r = s.get(f"{url}/sap/bc/adt/{path}", headers={"Accept": "*/*"})
        if r.status_code == 200:
            return f"{url}/sap/bc/adt/{path}"
    return f"{url}/sap/bc/adt/messageclass/{name.lower()}"  # default to newer path


def cmd_read_message_class(s: requests.Session, url: str, args) -> dict:
    """Read message class XML source to inspect current messages."""
    base = _msgclass_base(s, url, args.name)
    resp = s.get(base, headers={"Accept": "*/*"})
    return {"status": resp.status_code, "url": base, "content": resp.text[:8000]}


def cmd_write_messages(s: requests.Session, url: str, args) -> dict:
    """Write all messages to an existing message class (lock→PUT→unlock)."""
    # Read input before locking — a missing file must not leave a stuck lock
    with open(args.file, encoding="utf-8") as f:
        xml_body = f.read()

    base = _msgclass_base(s, url, args.name)

    # Lock
    handle, _corr = _lock(s, base)
    if not handle:
        # Try locking the messages sub-resource
        resp_lock = s.post(
            f"{base}?_action=LOCK&accessMode=MODIFY",
            headers={"X-CSRF-Token": s.headers.get("X-CSRF-Token", "")},
        )
        m = re.search(r'lockHandle["\s:=]+([A-Za-z0-9+/=]{10,})', resp_lock.text)
        if m:
            handle = m.group(1)
    if not handle:
        return {"error": "Could not lock message class — may be locked or not found"}

    try:
        put_resp = s.put(
            base,
            data=xml_body.encode("utf-8"),
            headers={
                "Content-Type": "application/vnd.sap.adt.messageClasses+xml",
                "X-sap-adt-lockhandle": handle,
            },
        )
    finally:
        _unlock(s, base, handle)

    ok = put_resp.status_code in (200, 204)
    return {
        "name": args.name,
        "put_status": put_resp.status_code,
        "message": "OK — activate to persist changes" if ok else put_resp.text[:300],
    }


def _msgclass_read_full_xml(s: requests.Session, url: str, name: str) -> tuple[str, str | None]:
    """Read full (untruncated) message class XML. Returns (base_url, xml_text or None)."""
    base = _msgclass_base(s, url, name)
    resp = s.get(base, headers={"Accept": "*/*"})
    if resp.status_code != 200:
        return base, None
    return base, resp.text


def _msgclass_lock_put_xml(s: requests.Session, base: str, xml_text: str, transport: str) -> dict:
    """Lock message class, PUT modified XML, unlock. Returns result dict."""
    handle, _ = _lock(s, base, corr_nr=transport or "")
    if not handle:
        return {"ok": False, "error": "Could not lock message class — may be locked or not found"}
    try:
        put_resp = s.put(
            base,
            data=xml_text.encode("utf-8"),
            headers={
                "Content-Type": "application/vnd.sap.adt.messageClasses+xml",
                "X-sap-adt-lockhandle": handle,
            },
        )
    finally:
        _unlock(s, base, handle)
    ok = put_resp.status_code in (200, 204)
    return {
        "ok": ok,
        "put_status": put_resp.status_code,
        "message": "OK — activate to persist changes" if ok else put_resp.text[:300],
    }


def cmd_add_message(s: requests.Session, url: str, args) -> dict:
    """Add or update (upsert) a single message in a message class by ID."""
    base, xml = _msgclass_read_full_xml(s, url, args.name)
    if xml is None:
        return {"error": f"Could not read message class {args.name}"}

    msg_id = str(args.id).zfill(3)
    # Escape XML special chars in text
    text = args.text.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
    new_elem = f'<mc:message mc:id="{msg_id}" mc:selfExplanatory="true" adtcore:description="{text}" adtcore:descriptionTextLimit="73"/>'

    # Match existing message element with this id (self-closing, single line)
    pattern = rf'<mc:message[^>]*mc:id="{re.escape(msg_id)}"[^>]*/>'
    if re.search(pattern, xml):
        xml = re.sub(pattern, new_elem, xml)
        action = "updated"
    elif "</mc:messages>" in xml:
        xml = xml.replace("</mc:messages>", f"  {new_elem}\n</mc:messages>")
        action = "added"
    else:
        return {"error": "Cannot locate </mc:messages> in response XML — unexpected format"}

    result = _msgclass_lock_put_xml(s, base, xml, getattr(args, "transport", "") or "")
    result.update({"name": args.name, "id": msg_id, "action": action})
    return result


def cmd_delete_message(s: requests.Session, url: str, args) -> dict:
    """Delete a single message by ID from an existing message class."""
    base, xml = _msgclass_read_full_xml(s, url, args.name)
    if xml is None:
        return {"error": f"Could not read message class {args.name}"}

    msg_id = str(args.id).zfill(3)
    pattern = rf'\s*<mc:message[^>]*mc:id="{re.escape(msg_id)}"[^>]*/>'
    if not re.search(pattern, xml):
        return {"error": f"Message {msg_id} not found in {args.name}"}

    xml = re.sub(pattern, "", xml)
    result = _msgclass_lock_put_xml(s, base, xml, getattr(args, "transport", "") or "")
    result.update({"name": args.name, "id": msg_id, "action": "deleted"})
    return result


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_search(s: requests.Session, url: str, args) -> list | dict:
    """Search ABAP objects by name, type, and/or package."""
    params = {"operation": "quickSearch", "query": args.query, "maxResults": args.max}
    if args.type:
        params["objectType"] = args.type
    if args.package:
        params["packageName"] = args.package
    if hasattr(args, "author") and args.author:
        params["author"] = args.author
    resp = s.get(
        f"{url}/sap/bc/adt/repository/informationsystem/search",
        params=params,
        headers={"Accept": "application/xml"},
    )
    return parse_xml_refs(resp.text)


def cmd_objects(s: requests.Session, url: str, args) -> list | dict:
    """List all objects assigned to a package."""
    params = {"operation": "quickSearch", "query": "*", "packageName": args.package, "maxResults": args.max}
    resp = s.get(
        f"{url}/sap/bc/adt/repository/informationsystem/search",
        params=params,
        headers={"Accept": "application/xml"},
    )
    return parse_xml_refs(resp.text)


def cmd_packages(s: requests.Session, url: str, args) -> dict:
    """List sub-packages inside a parent package via nodestructure."""
    resp = s.post(
        f"{url}/sap/bc/adt/repository/nodestructure",
        params={
            "parent_name": args.package,
            "parent_tech_name": args.package,
            "parent_type": "DEVC/K",
            "withShortDescriptions": "true",
        },
        headers={
            "Accept": "application/vnd.sap.as+xml;charset=utf-8;dataname=com.sap.adt.RepositoryObjectTreeContent"
        },
    )
    refs = re.findall(r'technicalName="([^"]*)"[^>]*description="([^"]*)"', resp.text)
    return {"parent": args.package, "subpackages": [{"name": n, "description": d} for n, d in refs]}


def _packages_for_user(s: requests.Session, url: str, user: str,
                       pattern: str = "Z*", max_pkgs: int = 500) -> list[dict]:
    """Return list of package dicts where adtcore:responsible == user (case-insensitive)."""
    params = {"operation": "quickSearch", "query": pattern,
              "objectType": "DEVC/K", "maxResults": max_pkgs}
    resp = s.get(f"{url}/sap/bc/adt/repository/informationsystem/search",
                 params=params, headers={"Accept": "application/xml"})
    result = []
    for pkg in parse_xml_refs(resp.text):
        encoded = pkg["name"].lower().replace("/", "%2f")
        r = s.get(f"{url}/sap/bc/adt/packages/{encoded}")
        if r.status_code != 200:
            continue
        m = re.search(r'adtcore:responsible="([^"]*)"', r.text)
        if not m or m.group(1).upper() != user.upper():
            continue
        m_desc    = re.search(r'adtcore:description="([^"]*)"', r.text)
        m_created = re.search(r'adtcore:createdBy="([^"]*)"', r.text)
        result.append({
            "name":        pkg["name"],
            "responsible": m.group(1),
            "created_by":  m_created.group(1) if m_created else "",
            "description": m_desc.group(1)    if m_desc    else "",
        })
    return result


def cmd_packages_by_responsible(s: requests.Session, url: str, args) -> list:
    """List packages where adtcore:responsible matches the given user."""
    return _packages_for_user(s, url, args.responsible,
                              pattern=args.pattern or "Z*", max_pkgs=args.max)


def cmd_objects_by_user(s: requests.Session, url: str, args) -> dict:
    """List all objects across packages owned by a user.

    Workflow: packages-by-responsible → objects per package → flat list with summary.
    Use --type to restrict to a specific object type (e.g. PROG/P for reports only).
    ADT quickSearch does not support author filtering directly — this command uses the
    package ownership as a proxy, which is the correct approach for custom-namespace work.
    """
    user    = args.target_user
    pattern = getattr(args, "pattern", "Z*") or "Z*"
    obj_type_filter = getattr(args, "type", "") or ""

    user_pkgs = _packages_for_user(s, url, user, pattern=pattern)

    all_objects: list[dict] = []
    for pkg in user_pkgs:
        params: dict = {"operation": "quickSearch", "query": "*",
                        "packageName": pkg["name"], "maxResults": 999}
        if obj_type_filter:
            params["objectType"] = obj_type_filter
        r = s.get(f"{url}/sap/bc/adt/repository/informationsystem/search",
                  params=params, headers={"Accept": "application/xml"})
        for obj in parse_xml_refs(r.text):
            obj["package_owner"] = pkg["name"]
            all_objects.append(obj)

    by_type: dict = {}
    for obj in all_objects:
        by_type[obj["type"]] = by_type.get(obj["type"], 0) + 1
    by_type = dict(sorted(by_type.items()))

    return {
        "user":            user,
        "packages_count":  len(user_pkgs),
        "packages":        [p["name"] for p in user_pkgs],
        "total_objects":   len(all_objects),
        "by_type":         by_type,
        "objects":         all_objects,
    }


def cmd_reports_by_user(s: requests.Session, url: str, args) -> dict:
    """List PROG/P (report/program) objects across packages owned by a user.

    Convenience wrapper around objects-by-user with --type PROG/P preset.
    """
    args.type = "PROG/P"
    result = cmd_objects_by_user(s, url, args)
    result["filter"] = "PROG/P only"
    return result


def cmd_source(s: requests.Session, url: str, args) -> dict:
    """Fetch source code of a program, class, interface, or function module."""
    base = TYPE_PATH_MAP.get(args.type, "programs/programs")
    path = f"{base}/{args.name.lower()}/source/main"
    resp = s.get(f"{url}/sap/bc/adt/{path}", headers={"Accept": "text/plain"})
    return {"name": args.name, "type": args.type, "status": resp.status_code, "source": resp.text}


def cmd_write_source(s: requests.Session, url: str, args) -> dict:
    """Write/update source code: lock → PUT → unlock. Does not activate."""
    base_path = TYPE_PATH_MAP.get(args.type, "programs/programs")
    base = f"{url}/sap/bc/adt/{base_path}/{args.name.lower()}"

    if args.text:
        source = args.text
    elif args.file:
        with open(args.file, encoding="utf-8") as f:
            source = f.read()
    else:
        return {"error": "Provide --file or --text"}

    transport = getattr(args, "transport", "") or ""
    handle, corr_nr = _lock(s, base, corr_nr=transport)
    if not handle:
        return {"error": "Could not obtain lock — object may be locked by another user"}
    # Prefer the caller-supplied transport; fall back to whatever the lock assigned
    effective_corr = transport or corr_nr

    qs = f"lockHandle={urllib.parse.quote(handle, safe='')}"
    if effective_corr:
        qs += f"&corrNr={effective_corr}"
    try:
        put_resp = s.put(
            f"{base}/source/main?{qs}",
            data=source.encode("utf-8"),
            headers={
                "Content-Type": "text/plain; charset=utf-8",
                "X-sap-adt-lockhandle": handle,
            },
        )
    finally:
        _unlock(s, base, handle)

    ok = put_resp.status_code in (200, 204)
    return {
        "name": args.name,
        "type": args.type,
        "put_status": put_resp.status_code,
        "transport_used": effective_corr,
        "message": "OK — use abap_activate_objects MCP tool to activate" if ok else put_resp.text[:300],
    }


def cmd_atc_check(s: requests.Session, url: str, args) -> dict:
    """Run ATC static analysis — 2-step flow: create worklist → run → poll."""
    objects = []
    for item in args.objects:
        if ":" not in item:
            return {"error": f"Invalid format '{item}' — use NAME:TYPE e.g. ZMY_PROG:PROG/P"}
        name, obj_type = item.rsplit(":", 1)
        base_path = TYPE_PATH_MAP.get(obj_type, "programs/programs")
        objects.append({
            "name": name.upper(),
            "type": obj_type,
            "uri": f"/sap/bc/adt/{base_path}/{name.lower()}",
        })

    # Step 1: create worklist
    r1 = s.post(
        f"{url}/sap/bc/adt/atc/worklists",
        data=_build_atc_objectset_xml(objects).encode("utf-8"),
        headers={"Content-Type": "application/vnd.sap.adt.atc.objectset+xml",
                 "Accept": "application/xml"},
    )
    if r1.status_code not in (200, 201):
        return {"error": "Worklist creation failed", "status": r1.status_code, "body": r1.text[:400]}

    loc = r1.headers.get("Location", "")
    wl_id = loc.rstrip("/").split("/")[-1].split("?")[0] if loc else ""
    m = re.search(r'worklistId[="]+([a-zA-Z0-9]+)', r1.text + loc)
    if m:
        wl_id = m.group(1)

    if not wl_id or wl_id == "00000000000000000000000000000000":
        return {"error": "Could not extract worklistId", "worklist_status": r1.status_code, "body": r1.text[:400]}

    # Step 2: start ATC run
    r2 = s.post(
        f"{url}/sap/bc/adt/atc/runs",
        params={"worklistId": wl_id},
        data=_build_atc_run_xml(objects).encode("utf-8"),
        headers={"Content-Type": "application/vnd.sap.adt.atc.run+xml",
                 "Accept": "application/xml"},
    )

    # Step 3: poll worklist for results (try multiple Accept headers)
    findings = []
    poll_status = "not_attempted"
    for accept_hdr in [
        "application/vnd.sap.adt.atc.worklist+xml; version=0.1",
        "application/vnd.sap.adt.atc.worklist+xml",
        "application/xml",
    ]:
        for attempt in range(6):
            time.sleep(3)
            r3 = s.get(
                f"{url}/sap/bc/adt/atc/worklists/{wl_id}",
                headers={"Accept": accept_hdr},
            )
            if r3.status_code == 200:
                poll_status = "ok"
                xml3 = r3.text
                prios  = re.findall(r'priority="(\d+)"', xml3)
                checks = re.findall(r'checkId="([^"]+)"', xml3)
                msgs   = re.findall(r'messageTitle="([^"]+)"', xml3)
                if not msgs:
                    msgs = re.findall(r'<atccore:message[^>]*>([^<]+)</atccore:message>', xml3)
                for i, (p, c) in enumerate(zip(prios, checks)):
                    findings.append({
                        "priority": int(p),
                        "check": c,
                        "message": msgs[i] if i < len(msgs) else "",
                    })
                break
            elif r3.status_code == 406:
                poll_status = f"406_accept_not_supported"
                break
            else:
                poll_status = f"poll_{r3.status_code}"
        if poll_status == "ok":
            break

    p1 = [f for f in findings if f["priority"] == 1]
    p2 = [f for f in findings if f["priority"] == 2]
    return {
        "worklist_id": wl_id,
        "run_status": r2.status_code,
        "poll_status": poll_status,
        "findings_count": len(findings),
        "p1_count": len(p1),
        "p2_count": len(p2),
        "gate": "PASS" if poll_status == "ok" and len(p1) == 0 else ("FAIL" if p1 else "UNKNOWN_POLL_UNSUPPORTED"),
        "findings": findings[:20],
    }


def cmd_activate(s: requests.Session, url: str, args) -> dict:
    """Activate ABAP objects via ADT activation endpoint."""
    refs = []
    for item in args.objects:
        if ":" not in item:
            return {"error": f"Invalid format '{item}' — use NAME:TYPE e.g. ZMY_PROG:PROG/P"}
        name, obj_type = item.rsplit(":", 1)
        base_path = TYPE_PATH_MAP.get(obj_type, "programs/programs")
        refs.append(
            f'  <adtcore:objectReference adtcore:uri="/sap/bc/adt/{base_path}/{name.lower()}" '
            f'adtcore:type="{obj_type}" adtcore:name="{name.upper()}"/>'
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">\n'
        + "\n".join(refs) + "\n"
        "</adtcore:objectReferences>"
    )

    r = s.post(
        f"{url}/sap/bc/adt/activation",
        params={"method": "activate", "preauditRequested": "true"},
        data=xml.encode("utf-8"),
        headers={
            "Content-Type": "application/vnd.sap.adt.activation.request+xml; charset=utf-8",
            "Accept": "application/vnd.sap.adt.activation.result+xml, application/xml",
        },
    )

    success = r.status_code in (200, 204)
    inactive = re.findall(r'adtcore:name="([^"]+)"[^>]*inactive', r.text)
    errors   = re.findall(r'<msg:shortText[^>]*>([^<]+)</msg:shortText>', r.text)
    return {
        "status": r.status_code,
        "success": success,
        "inactive_remaining": inactive,
        "errors": errors[:10],
        "message": "Activation OK — all objects active" if success and not inactive else r.text[:500],
    }


def cmd_transport_contents(s: requests.Session, url: str, args) -> dict:
    """Show objects recorded in a specific transport request."""
    transport = args.transport.upper()

    # Fetch CTS workbench XML (all open transports for current user)
    r = s.get(
        f"{url}/sap/bc/adt/cts/workbench",
        headers={"Accept": "application/vnd.sap.adt.cts.workbench+xml"},
    )
    if r.status_code not in (200, 201):
        return {"error": "CTS workbench fetch failed", "status": r.status_code, "body": r.text[:300]}

    xml = r.text

    # Find block for our transport
    # Format: <tm:transportRequest tm:number="DEVK900123" ...> ... </tm:transportRequest>
    block_match = re.search(
        rf'<tm:transportRequest[^>]*tm:number="{re.escape(transport)}"[^>]*>.*?</tm:transportRequest>',
        xml,
        re.DOTALL,
    )
    if not block_match:
        # Also try task level (transportTask)
        block_match = re.search(
            rf'<tm:transportTask[^>]*tm:number="{re.escape(transport)}"[^>]*>.*?</tm:transportTask>',
            xml,
            re.DOTALL,
        )

    objects = []
    description = ""
    if block_match:
        block = block_match.group(0)
        desc_m = re.search(r'tm:description="([^"]*)"', block)
        description = desc_m.group(1) if desc_m else ""
        # Parse objects: <tm:abapObject tm:name="..." tm:type="..." .../>
        obj_matches = re.findall(r'<tm:abapObject\s+([^/]*)/>', block)
        for attrs in obj_matches:
            name_m  = re.search(r'tm:name="([^"]*)"', attrs)
            type_m  = re.search(r'tm:type="([^"]*)"', attrs)
            pgmid_m = re.search(r'tm:pgmid="([^"]*)"', attrs)
            objects.append({
                "pgmid": pgmid_m.group(1) if pgmid_m else "R3TR",
                "type":  type_m.group(1)  if type_m  else "?",
                "name":  name_m.group(1)  if name_m  else "?",
            })
    else:
        return {
            "transport": transport,
            "status": r.status_code,
            "warning": f"Transport {transport} not found in workbench (may be released or owned by another user)",
            "objects": [],
        }

    return {
        "transport": transport,
        "description": description,
        "objects_count": len(objects),
        "objects": objects,
    }


def cmd_delete(s: requests.Session, url: str, args) -> dict:
    """Delete an ABAP object: lock → DELETE → done."""
    base_path = TYPE_PATH_MAP.get(args.type, "programs/programs")
    base = f"{url}/sap/bc/adt/{base_path}/{args.name.lower()}"

    handle, _corr = _lock(s, base)
    if not handle:
        return {"error": "Could not lock object — may be locked by another user"}

    params = {"lockHandle": handle}
    if args.transport:
        params["corrNr"] = args.transport

    try:
        del_resp = s.delete(base, params=params, headers={"X-sap-adt-lockhandle": handle})
    except requests.exceptions.RequestException:
        _unlock(s, base, handle)
        raise

    if del_resp.status_code not in (200, 204):
        _unlock(s, base, handle)
        return {
            "error": "Delete failed",
            "status": del_resp.status_code,
            "body": del_resp.text[:300],
        }

    return {"name": args.name, "type": args.type, "delete_status": del_resp.status_code, "message": "Deleted"}


def _parse_adt_object_tags(xml: str) -> list[dict]:
    """Extract adtcore-attributed elements regardless of attribute order."""
    result = []
    for tag in re.findall(r'<[^>]*adtcore:name="[^"]*"[^>]*>', xml):
        def _attr(a):
            m = re.search(rf'adtcore:{a}="([^"]*)"', tag)
            return m.group(1) if m else ""
        entry = {
            "uri": _attr("uri"),
            "type": _attr("type"),
            "name": _attr("name"),
            "package": _attr("packageName"),
            "description": _attr("description"),
        }
        if entry["name"] and entry["uri"]:
            result.append(entry)
    return result


def cmd_where_used(s: requests.Session, url: str, args) -> dict:
    """Find all objects that reference a given ABAP object (usage references)."""
    base_path = TYPE_PATH_MAP.get(args.type, "programs/programs")
    obj_uri = f"/sap/bc/adt/{base_path}/{args.name.lower()}"

    body = ('<?xml version="1.0" encoding="ASCII"?>\n'
            '<usagereferences:usageReferenceRequest '
            'xmlns:usagereferences="http://www.sap.com/adt/ris/usageReferences">\n'
            '  <usagereferences:affectedObjects/>\n'
            '</usagereferences:usageReferenceRequest>')
    resp = s.post(
        f"{url}/sap/bc/adt/repository/informationsystem/usageReferences",
        params={"uri": obj_uri},
        data=body.encode("utf-8"),
        headers={"Content-Type": "application/*", "Accept": "application/*"},
    )

    if resp.status_code not in (200, 201):
        return {
            "error": "where-used failed",
            "status": resp.status_code,
            "raw_xml_preview": resp.text[:300],
        }

    usages = _parse_adt_object_tags(resp.text)
    # The queried object itself is returned as well — drop it
    usages = [u for u in usages if u["uri"].rstrip("/").split("#")[0] != obj_uri][: args.max]
    result = {
        "target": args.name,
        "target_type": args.type,
        "usages_count": len(usages),
        "usages": usages,
    }
    if not usages:
        # Response schema varies by release — keep raw preview so an empty
        # result can be told apart from a parse miss
        result["raw_xml_preview"] = resp.text[:500]
    return result


def cmd_history(s: requests.Session, url: str, args) -> dict:
    """Show change history of an ABAP object."""
    base_path = TYPE_PATH_MAP.get(args.type, "programs/programs")
    base = f"{url}/sap/bc/adt/{base_path}/{args.name.lower()}"

    # Approach A: versions endpoint
    resp = s.get(f"{base}/source/versions", headers={"Accept": "application/xml"})
    if resp.status_code == 200:
        versions = re.findall(
            r'versionId="([^"]*)"[^>]*changedAt="([^"]*)"[^>]*changedBy="([^"]*)"',
            resp.text,
        )
        if versions:
            return {
                "name": args.name,
                "type": args.type,
                "source": "versions_endpoint",
                "versions": [
                    {"version": v, "changed_at": t, "changed_by": u}
                    for v, t, u in versions
                ],
            }

    # Approach B: revision link from object metadata → atom feed
    resp2 = s.get(base)
    link_m = re.search(
        r'<atom:link[^>]*href="([^"]+)"[^>]*rel="http://www\.sap\.com/adt/relations/versions"[^>]*/?>'
        r'|<atom:link[^>]*rel="http://www\.sap\.com/adt/relations/versions"[^>]*href="([^"]+)"',
        resp2.text,
    )
    if link_m:
        href = link_m.group(1) or link_m.group(2)
        rev_url = href if href.startswith("http") else (
            f"{url}{href}" if href.startswith("/") else f"{base}/{href}")
        r_feed = s.get(rev_url, headers={"Accept": "application/atom+xml;type=feed"})
        if r_feed.status_code == 200:
            entries = re.findall(r'<(?:atom:)?entry>(.*?)</(?:atom:)?entry>', r_feed.text, re.DOTALL)
            versions = []
            for e in entries:
                def _f(pat):
                    m = re.search(pat, e)
                    return m.group(1) if m else ""
                versions.append({
                    "version": _f(r'<title[^>]*>([^<]*)</title>'),
                    "changed_at": _f(r'<updated>([^<]*)</updated>'),
                    "changed_by": _f(r'<name>([^<]*)</name>'),
                })
            if versions:
                return {"name": args.name, "type": args.type,
                        "source": "revision_atom_feed", "versions": versions}

    # Approach C: object properties fallback (latest change only)
    def _ex(pattern, text):
        m = re.search(pattern, text)
        return m.group(1) if m else ""

    return {
        "name": args.name,
        "type": args.type,
        "source": "object_properties_fallback",
        "note": "Full version history unavailable on this system - showing latest change only",
        "versions": [{
            "version": "active",
            "changed_at": _ex(r'adtcore:changedAt="([^"]*)"', resp2.text),
            "changed_by": _ex(r'adtcore:changedBy="([^"]*)"', resp2.text),
            "created_at": _ex(r'adtcore:createdAt="([^"]*)"', resp2.text),
            "created_by": _ex(r'adtcore:createdBy="([^"]*)"', resp2.text),
        }],
    }


def cmd_diff(s: requests.Session, url: str, args) -> dict:
    """Compare active vs inactive (unsaved) source version."""
    base_path = TYPE_PATH_MAP.get(args.type, "programs/programs")
    source_url = f"{url}/sap/bc/adt/{base_path}/{args.name.lower()}/source/main"

    active_resp = s.get(source_url, headers={"Accept": "text/plain"})
    inactive_resp = s.get(f"{source_url}?version=inactive", headers={"Accept": "text/plain"})

    active_src = active_resp.text if active_resp.status_code == 200 else ""
    inactive_src = inactive_resp.text if inactive_resp.status_code == 200 else ""

    if not inactive_src or inactive_src == active_src:
        return {"name": args.name, "type": args.type, "has_changes": False,
                "message": "No inactive version or no pending changes"}

    diff_lines = list(difflib.unified_diff(
        active_src.splitlines(keepends=True),
        inactive_src.splitlines(keepends=True),
        fromfile=f"{args.name} (active)",
        tofile=f"{args.name} (inactive)",
    ))
    diff_text = "".join(diff_lines)
    truncated = len(diff_text) > 10_000
    return {
        "name": args.name,
        "type": args.type,
        "has_changes": True,
        "diff_lines": len(diff_lines),
        "truncated": truncated,
        "diff": diff_text[:10_000] if truncated else diff_text,
    }


def cmd_create_transport(s: requests.Session, url: str, args) -> dict:
    """Create a new Workbench transport request via /sap/bc/adt/cts/transports.

    Body is the ABAP-serialized CreateCorrectionRequest structure; the target
    system/route is derived by SAP from the package's transport layer.
    """
    if getattr(args, "type_tr", "K") == "W":
        return {"error": "Customizing requests (W) are not supported via the ADT REST "
                         "endpoint — create them in SE01/SE09"}
    desc = (args.description.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))
    devclass = getattr(args, "package", "") or ""
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
    <DATA>
      <OPERATION>I</OPERATION>
      <DEVCLASS>{devclass.upper()}</DEVCLASS>
      <REQUEST_TEXT>{desc}</REQUEST_TEXT>
      <REF/>
    </DATA>
  </asx:values>
</asx:abap>"""

    r = s.post(
        f"{url}/sap/bc/adt/cts/transports",
        data=xml.encode("utf-8"),
        headers={
            "Content-Type": "application/vnd.sap.as+xml; charset=UTF-8; dataname=com.sap.adt.CreateCorrectionRequest",
            "Accept": "text/plain",
        },
    )
    if r.status_code in (200, 201):
        # Response body/Location carries the new number, e.g. .../DEVK900124
        m = re.search(r'([A-Z0-9]{3}K[0-9]{6,})', r.text + r.headers.get("Location", ""))
        number = m.group(1) if m else r.text.strip()[:20]
        result = {"status": r.status_code, "transport": number,
                  "message": f"Transport {number} created"}
        if getattr(args, "target", ""):
            result["note"] = ("--target is not supported by this endpoint — the target "
                              "system follows the package's transport layer/route")
        return result

    return {
        "error": "Transport creation failed",
        "status": r.status_code,
        "body": r.text[:500],
        "note": "Try creating via SE01/SE09 if CTS REST is not enabled on this system",
    }


def cmd_release_transport(s: requests.Session, url: str, args) -> dict:
    """Release a transport request (tasks first, then the request)."""
    tr = args.transport.upper()
    tr_base = f"{url}/sap/bc/adt/cts/transportrequests/{tr}"

    # Step 1: find all tasks inside this transport
    r_info = s.get(tr_base, headers={"Accept": "application/xml"})
    tasks = re.findall(r'tm:number="([^"]+)"[^>]*tm:category="[Tt]ask"', r_info.text)
    if not tasks:
        # Fallback regex for task numbers (sub-requests typically end in same prefix + higher number)
        tasks = re.findall(r'<tm:task[^>]+tm:number="([^"]+)"', r_info.text)

    released_tasks = []
    task_errors = []
    for task in tasks:
        r_task = s.post(
            f"{url}/sap/bc/adt/cts/transportrequests/{task}/newreleasejobs",
            headers={"Accept": "application/*"},
        )
        if r_task.status_code in (200, 201, 204):
            released_tasks.append(task)
        else:
            task_errors.append({"task": task, "status": r_task.status_code, "body": r_task.text[:200]})

    # Step 2: release the transport itself
    r_rel = s.post(f"{tr_base}/newreleasejobs", headers={"Accept": "application/*"})

    released = r_rel.status_code in (200, 201, 204)
    return {
        "transport": tr,
        "tasks_found": tasks,
        "tasks_released": released_tasks,
        "task_errors": task_errors,
        "release_status": r_rel.status_code,
        "released": released,
        "message": ("Released" if released
                    else f"Release failed ({r_rel.status_code}) — try SE01/SE10 if REST release is not enabled"),
        "body": "" if released else r_rel.text[:400],
    }


def cmd_move_object(s: requests.Session, url: str, args) -> dict:
    """Add an ABAP object to a specific transport task (records it in the target transport).

    In CTS, 'moving' means recording the object in the target transport task.
    SAP automatically handles de-registration from the previous task when the object
    is re-locked into the new transport.
    """
    name, obj_type = (args.object.rsplit(":", 1) if ":" in args.object
                      else (args.object, "PROG/P"))
    transport = args.transport.upper()

    # Step 1: get transport details to find the first task number
    tr_base = f"{url}/sap/bc/adt/cts/transportrequests/{transport}"
    r_info = s.get(tr_base, headers={"Accept": "application/xml"})
    task_m = re.search(r'<tm:task[^>]+tm:number="([^"]+)"', r_info.text)
    if not task_m:
        task_m = re.search(r'tm:number="([A-Z0-9]+)"', r_info.text)
    task = args.task if hasattr(args, "task") and args.task else (task_m.group(1) if task_m else transport)

    base_path = TYPE_PATH_MAP.get(obj_type, "programs/programs")
    obj_uri = f"/sap/bc/adt/{base_path}/{name.lower()}"

    # Step 2: lock object into target transport — this records it in the task
    obj_url = f"{url}{obj_uri}"
    lock_url = f"{obj_url}?_action=LOCK&accessMode=MODIFY&corrNumber={transport}"
    r_lock = s.post(lock_url, headers={"X-CSRF-Token": s.headers.get("X-CSRF-Token", "")})

    handle_m = re.search(r'lockHandle["\s:=]+([A-Za-z0-9+/=]{10,})', r_lock.text)
    handle_m2 = re.search(r'adtcore:lockHandle="([^"]+)"', r_lock.text)
    handle = (handle_m2 or handle_m)
    if handle:
        handle = handle.group(1)
        _unlock(s, obj_url, handle)
        return {
            "object": name,
            "type": obj_type,
            "transport": transport,
            "task": task,
            "message": f"Object {name} recorded in transport {transport} (lock+unlock with corrNumber)",
        }

    # Fallback: POST object reference directly to task objects endpoint
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
  <adtcore:objectReference adtcore:uri="{obj_uri}"
    adtcore:type="{obj_type}" adtcore:name="{name.upper()}"/>
</adtcore:objectReferences>"""

    for task_url in [
        f"{url}/sap/bc/adt/cts/transportrequests/{task}/objects",
        f"{url}/sap/bc/adt/cts/transportrequests/{transport}/tasks/{task}/objects",
    ]:
        r = s.put(task_url, data=xml.encode("utf-8"),
                  headers={"Content-Type": "application/vnd.sap.adt.cts.task.objects+xml",
                           "Accept": "application/xml"})
        if r.status_code in (200, 204):
            return {"object": name, "type": obj_type, "transport": transport,
                    "task": task, "message": "Object added to transport task"}

    return {
        "object": name, "type": obj_type, "transport": transport,
        "lock_status": r_lock.status_code,
        "note": "Could not lock or directly add — object may already be in this transport, or locked by another user",
        "hint": "Use SE01/SE10 to manually reassign the object to the transport",
    }


def cmd_create_function_module(s: requests.Session, url: str, args) -> dict:
    """Create a new function module (FUGR/FF) inside an existing function group.

    Function modules live under their group: POST functions/groups/{group}/fmodules
    with a containerRef to the group (not packageRef).
    """
    group = args.group.upper()
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<fmodule:abapFunctionModule
  xmlns:fmodule="http://www.sap.com/adt/functions/fmodules"
  xmlns:adtcore="http://www.sap.com/adt/core"
  adtcore:name="{args.name.upper()}"
  adtcore:description="{args.description}"
  adtcore:responsible="{args.user}"
  adtcore:masterLanguage="EN">
  <adtcore:containerRef adtcore:name="{group}" adtcore:type="FUGR/F"
    adtcore:uri="/sap/bc/adt/functions/groups/{group.lower()}"/>
</fmodule:abapFunctionModule>"""

    r = _post_adt(s, url, f"functions/groups/{group.lower()}/fmodules",
                  xml, "application/*", args.transport)
    processing_type = getattr(args, "processing_type", "normal") or "normal"
    if r["ok"] and processing_type != "normal":
        r["note"] = ("Processing type cannot be set via the ADT creation API — "
                     f"set '{processing_type}' afterwards in SE37/Eclipse (FM attributes)")
    return r


def cmd_transports(s: requests.Session, url: str, args) -> dict:
    """List open transport requests, optionally filtered by owner."""
    params = {}
    if args.owner:
        params["user"] = args.owner
    resp = s.get(
        f"{url}/sap/bc/adt/cts/workbench",
        params=params,
        headers={"Accept": "application/vnd.sap.adt.cts.workbench+xml"},
    )
    transports = re.findall(r'tm:number="([^"]*)"[^>]*tm:description="([^"]*)"', resp.text)
    return {
        "status": resp.status_code,
        "transports": [{"number": n, "description": d} for n, d in transports],
    }


def cmd_create_function_group(s: requests.Session, url: str, args) -> dict:
    """Create a new ABAP function group (FUGR/FF) shell via ADT REST API."""
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<fugr:group
  xmlns:fugr="http://www.sap.com/adt/functions/groups"
  xmlns:adtcore="http://www.sap.com/adt/core"
  adtcore:name="{args.name.upper()}"
  adtcore:description="{args.description}"
  adtcore:responsible="{args.user}"
  adtcore:masterLanguage="EN">
  <adtcore:packageRef adtcore:name="{args.package.upper()}"/>
</fugr:group>"""
    return _post_adt(s, url, "functions/groups",
                     xml, "application/vnd.sap.adt.functions.groups.v3+xml",
                     args.transport)


def cmd_create_class(s: requests.Session, url: str, args) -> dict:
    """Create a new ABAP class (CLAS/OC) shell via ADT REST API."""
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<class:abapClass
  xmlns:class="http://www.sap.com/adt/oo/classes"
  xmlns:adtcore="http://www.sap.com/adt/core"
  adtcore:name="{args.name.upper()}"
  adtcore:description="{args.description}"
  adtcore:responsible="{args.user}"
  adtcore:masterLanguage="EN"
  class:final="false"
  class:visibility="public">
  <adtcore:packageRef adtcore:name="{args.package.upper()}"/>
</class:abapClass>"""
    return _post_adt(s, url, "oo/classes",
                     xml, "application/vnd.sap.adt.oo.classes.v4+xml",
                     args.transport)


def cmd_create_interface(s: requests.Session, url: str, args) -> dict:
    """Create a new ABAP interface (INTF/OI) shell via ADT REST API."""
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<intf:abapInterface
  xmlns:intf="http://www.sap.com/adt/oo/interfaces"
  xmlns:adtcore="http://www.sap.com/adt/core"
  adtcore:name="{args.name.upper()}"
  adtcore:description="{args.description}"
  adtcore:responsible="{args.user}"
  adtcore:masterLanguage="EN">
  <adtcore:packageRef adtcore:name="{args.package.upper()}"/>
</intf:abapInterface>"""
    return _post_adt(s, url, "oo/interfaces",
                     xml, "application/vnd.sap.adt.oo.interfaces.v4+xml",
                     args.transport)


def cmd_object_properties(s: requests.Session, url: str, args) -> dict:
    """Read full metadata/properties of any ABAP object."""
    base_path = TYPE_PATH_MAP.get(args.type, "programs/programs")
    obj_url = f"{url}/sap/bc/adt/{base_path}/{args.name.lower()}"

    for accept in [
        f"application/vnd.sap.adt.{base_path.replace('/', '.')}.v2+xml",
        "application/xml",
        "*/*",
    ]:
        r = s.get(obj_url, headers={"Accept": accept})
        if r.status_code == 200:
            break

    if r.status_code != 200:
        return {"error": "Object not found or not accessible", "status": r.status_code, "name": args.name}

    def _ex(pat): m = re.search(pat, r.text); return m.group(1) if m else ""
    return {
        "name": args.name,
        "type": args.type,
        "status": r.status_code,
        "description":   _ex(r'adtcore:description="([^"]*)"'),
        "package":       _ex(r'adtcore:packageName="([^"]*)"'),
        "responsible":   _ex(r'adtcore:responsible="([^"]*)"'),
        "created_by":    _ex(r'adtcore:createdBy="([^"]*)"'),
        "created_at":    _ex(r'adtcore:createdAt="([^"]*)"'),
        "changed_by":    _ex(r'adtcore:changedBy="([^"]*)"'),
        "changed_at":    _ex(r'adtcore:changedAt="([^"]*)"'),
        "master_lang":   _ex(r'adtcore:masterLanguage="([^"]*)"'),
        "inactive":      "inactive" in r.text.lower(),
        "raw_snippet":   r.text[:800],
    }


def cmd_unlock(s: requests.Session, url: str, args) -> dict:
    """Force-release a lock on an ABAP object (use when stuck lock prevents editing)."""
    base_path = TYPE_PATH_MAP.get(args.type, "programs/programs")
    base = f"{url}/sap/bc/adt/{base_path}/{args.name.lower()}"

    # Get current lock handle via OPTIONS or GET
    r_info = s.get(base, headers={"Accept": "application/xml"})
    handle_m = re.search(r'lockHandle["\s:=]+([A-Za-z0-9+/=]{10,})', r_info.text)
    handle_m2 = re.search(r'adtcore:lockHandle="([^"]*)"', r_info.text)
    handle = (handle_m2 or handle_m)
    if handle:
        handle = handle.group(1)

    if handle:
        _unlock(s, base, handle)
        return {"name": args.name, "type": args.type, "message": f"Unlocked (handle: {handle[:20]}…)"}

    # Try generic unlock via POST with no handle — some systems accept it
    r2 = s.post(
        f"{base}?_action=UNLOCK",
        headers={"X-CSRF-Token": s.headers.get("X-CSRF-Token", "")},
    )
    return {
        "name": args.name,
        "type": args.type,
        "message": "No lock handle found in object properties — tried force unlock",
        "unlock_status": r2.status_code,
        "note": "If object is locked by another user, an admin must release it via SM12.",
    }


def cmd_inactive_objects(s: requests.Session, url: str, args) -> dict:
    """List inactive (unsaved/not-yet-activated) objects for the current user."""
    user = getattr(args, "user_filter", "") or ""
    params: dict = {}
    if user:
        params["user"] = user.upper()

    # Primary endpoint: ADT inactive CTS objects list
    r = s.get(
        f"{url}/sap/bc/adt/activation/inactiveobjects",
        params=params,
        headers={"Accept": "application/vnd.sap.adt.inactivectsobjects.v1+xml, application/xml;q=0.8"},
    )

    if r.status_code == 404:
        # Fallback for older releases
        r = s.get(
            f"{url}/sap/bc/adt/workarea/inactive",
            params=params,
            headers={"Accept": "application/xml"},
        )

    if r.status_code not in (200, 201):
        return {
            "error": "Could not fetch inactive objects",
            "status": r.status_code,
            "note": "Endpoint may not be available on this system version",
            "body": r.text[:300],
        }

    objects = parse_xml_refs(r.text)
    # Also try regex for different XML format
    if not objects:
        names  = re.findall(r'adtcore:name="([^"]+)"', r.text)
        types  = re.findall(r'adtcore:type="([^"]+)"', r.text)
        objects = [{"name": n, "type": t} for n, t in zip(names, types)]

    return {
        "inactive_count": len(objects),
        "inactive_objects": objects,
        "raw_snippet": r.text[:500] if not objects else "",
    }


def cmd_delete_transport(s: requests.Session, url: str, args) -> dict:
    """Delete an empty transport request (must be empty — move objects first via SE10)."""
    transports = [t.upper() for t in args.transports]

    results = []
    for tr in transports:
        tr_url = f"{url}/sap/bc/adt/cts/transportrequests/{tr}"
        # Verify it exists
        r_get = s.get(tr_url, headers={"Accept": "application/xml"})
        if r_get.status_code == 404:
            results.append({"transport": tr, "status": 404, "message": "Not found"})
            continue
        r_del = s.delete(tr_url)
        ok = r_del.status_code in (200, 204)
        results.append({
            "transport": tr,
            "status": r_del.status_code,
            "message": "Deleted" if ok else r_del.text[:300],
        })

    return {"results": results}


def cmd_abap_unit(s: requests.Session, url: str, args) -> dict:
    """Run ABAP unit tests for one or more objects (requires ADT ABAP unit endpoint)."""
    refs = "\n".join(
        f'    <adtcore:objectReference adtcore:uri="/sap/bc/adt/{TYPE_PATH_MAP.get(t, "programs/programs")}/{n.lower()}"'
        f' adtcore:type="{t}" adtcore:name="{n.upper()}"/>'
        for item in args.objects
        for n, t in [item.rsplit(":", 1) if ":" in item else (item, "PROG/P")]
    )

    # Root must be runConfiguration (an <aunit:run> root is rejected with 400),
    # and without <options><uriType value="semantic"/> the run silently
    # matches zero test classes.
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<aunit:runConfiguration xmlns:aunit="http://www.sap.com/adt/aunit">
  <external>
    <coverage active="false"/>
  </external>
  <options>
    <uriType value="semantic"/>
    <testDeterminationStrategy sameProgram="true" assignedTests="false"/>
    <testRiskLevels harmless="true" dangerous="true" critical="true"/>
    <testDurations short="true" medium="true" long="true"/>
  </options>
  <adtcore:objectSets xmlns:adtcore="http://www.sap.com/adt/core">
    <objectSet kind="inclusive">
      <adtcore:objectReferences>
{refs}
      </adtcore:objectReferences>
    </objectSet>
  </adtcore:objectSets>
</aunit:runConfiguration>"""

    r = s.post(
        f"{url}/sap/bc/adt/abapunit/testruns",
        data=xml.encode("utf-8"),
        headers={
            "Content-Type": "application/vnd.sap.adt.abapunit.testruns.config+xml; charset=utf-8",
            "Accept": "application/vnd.sap.adt.abapunit.testruns.result+xml, application/xml",
        },
    )

    if r.status_code not in (200, 201):
        return {"error": "ABAP unit run failed", "status": r.status_code, "body": r.text[:500]}

    xml_res = r.text
    # A failing testMethod is NOT self-closing (it nests <alerts>), and some
    # releases omit executionState entirely — self-closing then means passed.
    methods = list(re.finditer(r'<testMethod\b([^>]*?)(/?)>', xml_res))
    passed = failed = skipped = 0
    method_list = []
    for tm in methods:
        attrs, self_closing = tm.group(1), tm.group(2) == "/"
        n  = re.search(r'adtcore:name="([^"]+)"', attrs)
        st = re.search(r'executionState="([^"]+)"', attrs)
        name  = n.group(1) if n else "?"
        state = st.group(1) if st else ("passed" if self_closing else "failed")
        is_pass = self_closing and state in ("executed", "passed")
        if is_pass:   passed  += 1
        elif state == "skipped": skipped += 1
        else: failed += 1
        method_list.append({"name": name, "state": state, "passed": is_pass})

    alerts = re.findall(r'<alert[^>]*>.*?</alert>', xml_res, re.DOTALL)
    failures = []
    for a in alerts[:20]:
        title  = re.search(r'<title>([^<]+)</title>', a)
        detail = re.search(r'<details>([^<]+)</details>', a)
        failures.append({
            "title":  title.group(1) if title else "?",
            "detail": detail.group(1) if detail else "",
        })

    return {
        "total": len(methods),
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "gate": "PASS" if failed == 0 else "FAIL",
        "methods": method_list,
        "failures": failures,
    }


def cmd_discovery(s: requests.Session, url: str, args) -> dict:
    """List available ADT services/endpoints on the system."""
    r = s.get(f"{url}/sap/bc/adt/discovery", headers={"Accept": "application/atomsvc+xml"})
    if r.status_code != 200:
        return {"error": "Discovery failed", "status": r.status_code}

    # Parse workspace titles and href attributes
    workspaces = re.findall(r'<atom:title[^>]*>([^<]+)</atom:title>', r.text)
    hrefs = re.findall(r'href="([^"]*)"', r.text)
    collections = re.findall(
        r'<atom:collection[^>]*href="([^"]*)"[^>]*>[^<]*<atom:title[^>]*>([^<]+)</atom:title>',
        r.text,
    )
    return {
        "status": r.status_code,
        "workspaces": workspaces,
        "collections": [{"href": h, "title": t} for h, t in collections],
        "all_hrefs_count": len(hrefs),
    }


def cmd_create_cds(s: requests.Session, url: str, args) -> dict:
    """Create a CDS Data Definition (DDLS/DF) via /sap/bc/adt/ddic/ddl/sources.

    Note: ddic/ddla/sources is a different object type (DDLA = annotation
    definitions) — data definitions must go to the DDL endpoint.
    Optionally writes initial source code immediately after creation.
    """
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ddl:ddlSource
  xmlns:ddl="http://www.sap.com/adt/ddic/ddlsources"
  xmlns:adtcore="http://www.sap.com/adt/core"
  adtcore:name="{args.name.upper()}"
  adtcore:description="{args.description}"
  adtcore:responsible="{args.user}"
  adtcore:masterLanguage="EN">
  <adtcore:packageRef adtcore:name="{args.package.upper()}"/>
</ddl:ddlSource>"""

    r = _post_adt(s, url, "ddic/ddl/sources", xml, "application/*", args.transport)

    # Optionally write initial source right after creation
    source_text = ""
    if hasattr(args, "source") and args.source:
        source_text = args.source
    elif hasattr(args, "source_file") and args.source_file:
        with open(args.source_file, encoding="utf-8") as f:
            source_text = f.read()

    if r["ok"] and source_text:
        base = f"{url}/sap/bc/adt/ddic/ddl/sources/{args.name.lower()}"
        handle, corr = _lock(s, base, corr_nr=getattr(args, "transport", "") or "")
        if not handle:
            r["source_written"] = False
            r["source_error"] = "Could not lock the new DDLS object to write initial source"
        if handle:
            transport = getattr(args, "transport", "") or corr
            qs = f"lockHandle={urllib.parse.quote(handle, safe='')}"
            if transport:
                qs += f"&corrNr={transport}"
            try:
                put_r = s.put(
                    f"{base}/source/main?{qs}",
                    data=source_text.encode("utf-8"),
                    headers={"Content-Type": "text/plain; charset=utf-8",
                             "X-sap-adt-lockhandle": handle},
                )
            finally:
                _unlock(s, base, handle)
            r["source_written"] = put_r.status_code in (200, 204)
            r["source_put_status"] = put_r.status_code

    return r


def cmd_read_text_elements(s: requests.Session, url: str, args) -> dict:
    """Read text elements (selections, symbols, headings) for a program, class, or function group.

    Endpoint: GET /sap/bc/adt/textelements/{obj_class}/{name}/source/{section}
    Supported types: PROG/P (default), CLAS/OC, FUGR/FF.
    Returns each section as a plain-text block (the format ADT uses natively).
    """
    obj_type = getattr(args, "type", "PROG/P") or "PROG/P"
    obj_class = TEXT_ELEM_CLASS_MAP.get(obj_type, "programs")
    name = args.name.lower()
    base = f"{url}/sap/bc/adt/textelements/{obj_class}/{name}"

    requested = getattr(args, "section", None)
    sections_to_read = [requested] if requested else list(TEXT_ELEM_SECTIONS.keys())

    result: dict = {"name": args.name, "type": obj_type, "sections": {}}
    for sect in sections_to_read:
        ct = TEXT_ELEM_SECTIONS[sect]
        r = s.get(f"{base}/source/{sect}", headers={"Accept": ct})
        if r.status_code != 200:
            r = s.get(f"{base}/source/{sect}", headers={"Accept": "*/*"})
        result["sections"][sect] = {
            "status": r.status_code,
            "content": r.text if r.status_code == 200 else "",
            "error": r.text[:200] if r.status_code != 200 else "",
        }

    return result


def cmd_write_text_elements(s: requests.Session, url: str, args) -> dict:
    """Write a text element section (selections/symbols/headings) via lock→PUT→unlock.

    Content format mirrors what GET returns — plain text with ADT-specific syntax:
      selections:  "FIELDNAME  =Description text"
      symbols:     "@MaxLength:N\\nCODE=Text"
      headings:    "key=value"

    Supported types: PROG/P (default), CLAS/OC, FUGR/FF.
    """
    obj_type = getattr(args, "type", "PROG/P") or "PROG/P"
    obj_class = TEXT_ELEM_CLASS_MAP.get(obj_type, "programs")
    name = args.name.lower()
    base = f"{url}/sap/bc/adt/textelements/{obj_class}/{name}"

    section = args.section
    ct_write = TEXT_ELEM_SECTIONS[section]

    if args.text:
        content = args.text
    elif args.file:
        with open(args.file, encoding="utf-8") as f:
            content = f.read()
    else:
        return {"error": "Provide --file or --text with the text element content"}

    # Lock — try text element object first, then fall back to the program object
    lock_base = base
    handle, corr = _lock(s, lock_base, corr_nr=getattr(args, "transport", "") or "")
    if not handle:
        lock_base = f"{url}/sap/bc/adt/{TYPE_PATH_MAP.get(obj_type, 'programs/programs')}/{name}"
        handle, corr = _lock(s, lock_base, corr_nr=getattr(args, "transport", "") or "")
    if not handle:
        return {"error": "Could not lock object for text element write — may be locked by another user"}

    transport = getattr(args, "transport", "") or corr
    qs = f"lockHandle={urllib.parse.quote(handle, safe='')}"
    if transport:
        qs += f"&corrNr={transport}"

    try:
        put_r = s.put(
            f"{base}/source/{section}?{qs}",
            data=content.encode("utf-8"),
            headers={
                "Content-Type": ct_write,
                "X-sap-adt-lockhandle": handle,
            },
        )
    finally:
        _unlock(s, lock_base, handle)

    ok = put_r.status_code in (200, 204)
    return {
        "name": args.name,
        "type": obj_type,
        "section": section,
        "put_status": put_r.status_code,
        "transport_used": transport,
        "message": "OK — activate to persist changes" if ok else put_r.text[:300],
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="SAP ADT REST API client — browse, search, and query ABAP repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples (use --url / --user / --pwd / --client for all):
  Search programs starting with Z:
    adt-client ... search "Z*" --type PROG/P --package ZPACKAGE

  Read source code:
    adt-client ... source ZMY_PROG --type PROG/P

  Write source (lock→PUT→unlock; activate separately):
    adt-client ... write-source ZMY_PROG --file source.abap --type PROG/P

  Create package with transport layer:
    adt-client ... create-package ZTEST --description "My package" --superpackage ZHOME --transport DEVK900001 --sw-component HOME --transport-layer ZDEV

  Create program / class / interface / function-group:
    adt-client ... create-program ZMY_PROG --description "..." --package ZPKG --transport DEVK900001
    adt-client ... create-class ZCL_HELPER --description "..." --package ZPKG --transport DEVK900001
    adt-client ... create-interface ZIF_CONTRACT --description "..." --package ZPKG --transport DEVK900001
    adt-client ... create-function-group ZFUGR --description "..." --package ZPKG --transport DEVK900001

  Activate objects:
    adt-client ... activate ZMY_PROG:PROG/P ZCL_HELPER:CLAS/OC

  Run ABAP unit tests:
    adt-client ... abap-unit ZMY_PROG:PROG/P

  Run ATC static analysis:
    adt-client ... atc-check ZMY_PROG:PROG/P

  Object metadata:
    adt-client ... object-properties ZMY_PROG --type PROG/P

  Where-used / history / diff:
    adt-client ... where-used ZCL_MY_CLASS --type CLAS/OC
    adt-client ... history ZMY_PROG --type PROG/P
    adt-client ... diff ZMY_PROG --type PROG/P

  List open transports / transport objects:
    adt-client ... transports --owner DEVUSER
    adt-client ... transport-contents DEVK900001

  Delete empty transport request:
    adt-client ... delete-transport DEVK900002 --force

  List all objects / reports / packages by user:
    adt-client ... objects-by-user DEVUSER
    adt-client ... objects-by-user DEVUSER --type CLAS/OC
    adt-client ... reports-by-user DEVUSER
    adt-client ... packages-by-responsible DEVUSER --pattern "Z*"
    adt-client ... transports --owner DEVUSER

  Create CDS Data Definition:
    adt-client ... create-cds ZCDS_MY_VIEW --description "My view" --package ZPKG --transport DEVK900001
    adt-client ... create-cds ZCDS_MY_VIEW --description "My view" --package ZPKG --source-file my_view.ddls

  Read / write text elements:
    adt-client ... read-text-elements ZMY_PROG --type PROG/P
    adt-client ... read-text-elements ZMY_PROG --section selections
    adt-client ... write-text-elements ZMY_PROG --section selections --file sel.txt --transport DEVK900001
    adt-client ... write-text-elements ZMY_PROG --section symbols --text "@MaxLength:10\nTITLE=My Title"

  Release stuck lock:
    adt-client ... unlock ZMY_PROG --type PROG/P

  Show inactive objects:
    adt-client ... inactive-objects

  Discover available ADT endpoints:
    adt-client ... discovery
        """,
    )
    p.add_argument("--dest", help="Destination name SID_CLIENT_USER_LANG (e.g. DEV_100_DEVELOPER_EN); "
                                  "resolves url/user/pwd from SAP_<SID>_* env vars — see SKILL.md")
    p.add_argument("--url", help="SAP system base URL (e.g. https://host:44300); overrides --dest")
    p.add_argument("--user", help="SAP logon user; overrides --dest")
    p.add_argument("--pwd", help="SAP password (prefer --dest + env var; avoids plaintext on the CLI)")
    p.add_argument("--client", help="SAP client (default: 100, or the client from --dest)")
    p.add_argument("--lang", help="Logon language (default: EN, or the language from --dest)")
    p.add_argument("--ca-bundle", dest="ca_bundle", metavar="PATH",
                   help="Path to a PEM CA bundle for corporate SAP systems with private CAs. "
                        "Overrides SAP_ADT_CA_BUNDLE. Cannot be combined with --insecure.")
    p.add_argument("--insecure", action="store_true",
                   help="UNSAFE: disable TLS certificate verification for this invocation. "
                        "Intended only for controlled troubleshooting and non-production "
                        "environments. Cannot be combined with --ca-bundle.")

    sub = p.add_subparsers(dest="command", required=True, metavar="command")

    # search
    sp = sub.add_parser("search", help="Search ABAP objects by name/type/package")
    sp.add_argument("query", help='Search query — use * for all, e.g. "ZCL*"')
    sp.add_argument("--type", help="Object type, e.g. PROG/P  CLAS/OC  DEVC/K  TABL/DT")
    sp.add_argument("--package", help="Filter by package name")
    sp.add_argument("--author", help="Filter by author/responsible user")
    sp.add_argument("--max", type=int, default=100, metavar="N", help="Max results (default: 100)")

    # objects
    op = sub.add_parser("objects", help="List all objects assigned to a package")
    op.add_argument("package", help="Package name, e.g. \\$TMP or ZPACKAGE")
    op.add_argument("--max", type=int, default=999, metavar="N", help="Max results (default: 999)")

    # packages
    pp = sub.add_parser("packages", help="List sub-packages inside a parent package")
    pp.add_argument("package", help="Parent package name, e.g. \\$TMP")

    # source
    srcp = sub.add_parser("source", help="Read source code of an ABAP object")
    srcp.add_argument("name", help="Object name, e.g. ZCDS_VIEW")
    srcp.add_argument("--type", default="PROG/P", help="Object type (default: PROG/P)")

    # write-source
    wp = sub.add_parser("write-source", help="Write/update source code (lock->PUT->unlock; does not activate)")
    wp.add_argument("name", help="Object name, e.g. ZMY_PROG")
    wp.add_argument("--type", default="PROG/P", help="Object type (default: PROG/P)")
    wp.add_argument("--file", help="Path to .abap source file (UTF-8)")
    wp.add_argument("--text", help="Inline source text")
    wp.add_argument("--transport", default="", help="Transport request number to lock into (avoids auto-generated transports)")

    # packages-by-responsible
    prp = sub.add_parser("packages-by-responsible", help="List packages by responsible user")
    prp.add_argument("responsible", help="Responsible user, e.g. DEVUSER")
    prp.add_argument("--pattern", default="Z*", help="Package name pattern (default: Z*)")
    prp.add_argument("--max", type=int, default=500, metavar="N", help="Max packages to scan (default: 500)")

    # objects-by-user
    obu = sub.add_parser("objects-by-user",
                         help="List all objects across packages owned by a user (packages-by-responsible + objects per package)")
    obu.add_argument("target_user", metavar="USER", help="SAP user, e.g. DEVUSER")
    obu.add_argument("--pattern", default="Z*", help="Package name pattern (default: Z*)")
    obu.add_argument("--type", default="", metavar="TYPE",
                     help="Filter by object type, e.g. PROG/P CLAS/OC (omit for all types)")

    # reports-by-user
    rbu = sub.add_parser("reports-by-user",
                         help="List PROG/P (reports/programs) across packages owned by a user")
    rbu.add_argument("target_user", metavar="USER", help="SAP user, e.g. DEVUSER")
    rbu.add_argument("--pattern", default="Z*", help="Package name pattern (default: Z*)")

    # atc-check
    ap = sub.add_parser("atc-check", help="Run ATC static analysis on ABAP objects")
    ap.add_argument("objects", nargs="+", help="Objects as NAME:TYPE e.g. ZMY_PROG:PROG/P")

    # delete
    dp = sub.add_parser("delete", help="Delete an ABAP object (requires --transport for non-$TMP)")
    dp.add_argument("name", help="Object name, e.g. ZMY_PROG")
    dp.add_argument("--type", default="PROG/P", help="Object type (default: PROG/P)")
    dp.add_argument("--transport", help="Transport request number (required for non-$TMP objects)")
    dp.add_argument("--force", action="store_true", help="Skip confirmation prompt (for agent/non-interactive use)")

    # where-used
    up = sub.add_parser("where-used", help="Find all objects that reference a given object")
    up.add_argument("name", help="Object name, e.g. ZCL_MY_CLASS")
    up.add_argument("--type", default="CLAS/OC", help="Object type (default: CLAS/OC)")
    up.add_argument("--max", type=int, default=100, metavar="N", help="Max results (default: 100)")

    # history
    hp = sub.add_parser("history", help="Show change history of an ABAP object")
    hp.add_argument("name", help="Object name, e.g. ZMY_PROG")
    hp.add_argument("--type", default="PROG/P", help="Object type (default: PROG/P)")

    # diff
    dfp = sub.add_parser("diff", help="Compare active vs inactive (unsaved) source version")
    dfp.add_argument("name", help="Object name, e.g. ZMY_PROG")
    dfp.add_argument("--type", default="PROG/P", help="Object type (default: PROG/P)")

    # transports
    tp = sub.add_parser("transports", help="List open transport requests")
    tp.add_argument("--owner", metavar="USER", help="Filter by transport owner/user")

    # create-package
    cpp = sub.add_parser("create-package", help="Create a new ABAP package (DEVC/K)")
    cpp.add_argument("name", help="Package name, e.g. ZHABA_MDM")
    cpp.add_argument("--description", required=True, help="Short description")
    cpp.add_argument("--superpackage", required=True, help="Parent package name")
    cpp.add_argument("--transport", default="", help="Transport request number")
    cpp.add_argument("--sw-component", default="HOME", dest="sw_component",
                     help="Software component (default: HOME)")
    cpp.add_argument("--transport-layer", default="", dest="transport_layer",
                     help="Transport layer, e.g. ZDEV (leave empty for local)")

    # create-program
    crp = sub.add_parser("create-program", help="Create a new ABAP report/program (PROG/P)")
    crp.add_argument("name", help="Program name, e.g. ZMY_REPORT")
    crp.add_argument("--description", required=True, help="Short description")
    crp.add_argument("--package", required=True, help="Package name")
    crp.add_argument("--transport", default="", help="Transport request number")

    # create-message-class
    cmp = sub.add_parser("create-message-class", help="Create a new message class (MSAG/N)")
    cmp.add_argument("name", help="Message class name, e.g. ZMSAG")
    cmp.add_argument("--description", required=True, help="Short description")
    cmp.add_argument("--package", required=True, help="Package name")
    cmp.add_argument("--transport", default="", help="Transport request number")

    # create-transaction
    ctp = sub.add_parser("create-transaction", help="Create a report transaction code (TRAN/T)")
    ctp.add_argument("name", help="Transaction code, e.g. ZMY_TCODE")
    ctp.add_argument("--description", required=True, help="Short description")
    ctp.add_argument("--program", required=True, help="Linked program name")
    ctp.add_argument("--package", required=True, help="Package name")
    ctp.add_argument("--transport", default="", help="Transport request number")

    # create-function-group
    cfg = sub.add_parser("create-function-group", help="Create a new function group (FUGR/FF)")
    cfg.add_argument("name", help="Function group name, e.g. ZFUGR_UTILS")
    cfg.add_argument("--description", required=True, help="Short description")
    cfg.add_argument("--package", required=True, help="Package name")
    cfg.add_argument("--transport", default="", help="Transport request number")

    # create-class
    ccl = sub.add_parser("create-class", help="Create a new ABAP class (CLAS/OC)")
    ccl.add_argument("name", help="Class name, e.g. ZCL_MY_HELPER")
    ccl.add_argument("--description", required=True, help="Short description")
    ccl.add_argument("--package", required=True, help="Package name")
    ccl.add_argument("--transport", default="", help="Transport request number")

    # create-interface
    cif = sub.add_parser("create-interface", help="Create a new ABAP interface (INTF/OI)")
    cif.add_argument("name", help="Interface name, e.g. ZIF_MY_CONTRACT")
    cif.add_argument("--description", required=True, help="Short description")
    cif.add_argument("--package", required=True, help="Package name")
    cif.add_argument("--transport", default="", help="Transport request number")

    # read-message-class
    rmp = sub.add_parser("read-message-class", help="Read current XML of a message class")
    rmp.add_argument("name", help="Message class name")

    # write-messages
    wmp = sub.add_parser("write-messages", help="Write messages XML to an existing message class")
    wmp.add_argument("name", help="Message class name")
    wmp.add_argument("--file", required=True, help="Path to XML file with messages")

    # add-message / update-message (upsert — same implementation)
    for _cmd, _help in (
        ("add-message",    "Add or update a single message in a message class (upsert by ID)"),
        ("update-message", "Update text of an existing message in a message class (upsert by ID)"),
    ):
        _p = sub.add_parser(_cmd, help=_help)
        _p.add_argument("name", help="Message class name")
        _p.add_argument("--id",        required=True, help="Message number, e.g. 001")
        _p.add_argument("--text",      required=True, help="Message text")
        _p.add_argument("--transport", help="Transport request number")

    # delete-message
    dmp = sub.add_parser("delete-message", help="Delete a single message by ID from a message class")
    dmp.add_argument("name", help="Message class name")
    dmp.add_argument("--id",        required=True, help="Message number to delete, e.g. 001")
    dmp.add_argument("--transport", help="Transport request number")

    # object-properties
    objp = sub.add_parser("object-properties", help="Read full metadata/properties of any ABAP object")
    objp.add_argument("name", help="Object name")
    objp.add_argument("--type", default="PROG/P", help="Object type (default: PROG/P)")

    # unlock
    unlp = sub.add_parser("unlock", help="Force-release a lock on an ABAP object")
    unlp.add_argument("name", help="Object name")
    unlp.add_argument("--type", default="PROG/P", help="Object type (default: PROG/P)")

    # inactive-objects
    inap = sub.add_parser("inactive-objects", help="List inactive (not-yet-activated) objects")
    inap.add_argument("--user-filter", default="", dest="user_filter",
                      metavar="USER", help="Filter by user (optional)")

    # delete-transport
    dtp = sub.add_parser("delete-transport",
                         help="Delete empty transport request(s) — move objects to another transport first")
    dtp.add_argument("transports", nargs="+", help="Transport number(s), e.g. DEVK900123")
    dtp.add_argument("--force", action="store_true", help="Skip confirmation (for agent use)")

    # create-transport
    ctrp = sub.add_parser("create-transport", help="Create a new Workbench transport request")
    ctrp.add_argument("--description", required=True, help="Transport description")
    ctrp.add_argument("--package", default="", help="Package (DEVCLASS) — determines transport route (optional)")
    ctrp.add_argument("--target", default="", help="Deprecated — target follows the package's transport layer")
    ctrp.add_argument("--type-tr", default="K", dest="type_tr",
                      choices=["K", "W"], help="K=Workbench (default); W=Customizing is not supported via ADT REST")

    # release-transport
    rtrp = sub.add_parser("release-transport", help="Release a transport request (tasks first, then request)")
    rtrp.add_argument("transport", help="Transport number, e.g. DEVK900001")

    # move-object
    motp = sub.add_parser("move-object",
                          help="Record an object into a transport task (re-lock with target corrNumber)")
    motp.add_argument("object", help="Object as NAME:TYPE e.g. ZMY_PROG:PROG/P")
    motp.add_argument("--transport", required=True, help="Target transport number")
    motp.add_argument("--task", default="", help="Task number within transport (auto-detected if omitted)")

    # create-function-module
    cfm = sub.add_parser("create-function-module", help="Create a function module (FUNC/FF) in a function group")
    cfm.add_argument("name", help="Function module name, e.g. Z_MY_FUNCTION")
    cfm.add_argument("--description", required=True, help="Short description")
    cfm.add_argument("--group", required=True, help="Parent function group name (FUGR), e.g. ZFUGR_UTILS")
    cfm.add_argument("--package", default="", help="Ignored — the FM inherits the function group's package")
    cfm.add_argument("--transport", default="", help="Transport request number")
    cfm.add_argument("--processing-type", default="normal", dest="processing_type",
                     choices=["normal", "remote-enabled", "update"],
                     help="FM processing type (default: normal)")

    # abap-unit
    aup = sub.add_parser("abap-unit", help="Run ABAP unit tests for one or more objects")
    aup.add_argument("objects", nargs="+", help="Objects as NAME:TYPE e.g. ZMY_PROG:PROG/P (type optional, default PROG/P)")

    # activate
    actp = sub.add_parser("activate", help="Activate ABAP objects via ADT activation endpoint")
    actp.add_argument("objects", nargs="+", help="Objects as NAME:TYPE e.g. ZMY_PROG:PROG/P")

    # transport-contents
    tcp = sub.add_parser("transport-contents", help="Show objects in a specific transport request")
    tcp.add_argument("transport", help="Transport number, e.g. DEVK900123")

    # discovery
    discp = sub.add_parser("discovery", help="List available ADT services/endpoints on the system")

    # create-cds
    ccds = sub.add_parser("create-cds",
                          help="Create a CDS Data Definition (DDLS/DF) via ddic/ddl/sources")
    ccds.add_argument("name", help="CDS view name, e.g. ZCDS_MY_VIEW")
    ccds.add_argument("--description", required=True, help="Short description")
    ccds.add_argument("--package", required=True, help="Package name")
    ccds.add_argument("--transport", default="", help="Transport request number")
    ccds.add_argument("--source", default="",
                      help="Inline initial DDLS source code (optional — writes after creation)")
    ccds.add_argument("--source-file", default="", dest="source_file",
                      help="Path to .ddls source file to write after creation (optional)")

    # read-text-elements
    rtep = sub.add_parser("read-text-elements",
                          help="Read text elements (selections/symbols/headings) for a program, class, or function group")
    rtep.add_argument("name", help="Object name, e.g. ZMY_PROG")
    rtep.add_argument("--type", default="PROG/P",
                      help="Object type: PROG/P (default), CLAS/OC, FUGR/FF")
    rtep.add_argument("--section", choices=["selections", "symbols", "headings"],
                      help="Specific section to read (reads all three if omitted)")

    # write-text-elements
    wtep = sub.add_parser("write-text-elements",
                          help="Write a text element section (lock→PUT→unlock; activate separately)")
    wtep.add_argument("name", help="Object name, e.g. ZMY_PROG")
    wtep.add_argument("--type", default="PROG/P",
                      help="Object type: PROG/P (default), CLAS/OC, FUGR/FF")
    wtep.add_argument("--section", required=True,
                      choices=["selections", "symbols", "headings"],
                      help="Text element section to write")
    wtep.add_argument("--file", help="Path to text file with section content (UTF-8)")
    wtep.add_argument("--text", help="Inline section content")
    wtep.add_argument("--transport", default="", help="Transport request number")

    return p


def main():
    # Windows consoles default to cp1252 — non-ASCII SAP descriptions would
    # crash json output with ensure_ascii=False
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = build_parser()
    args = parser.parse_args()

    if args.dest:
        _resolve_destination(args)
    missing = [f for f, v in (("--url", args.url), ("--user", args.user),
                              ("--pwd", args.pwd)) if not v]
    if missing:
        parser.error(f"missing {', '.join(missing)} — pass them explicitly "
                     f"or use --dest with SAP_<SID>_* env vars (see SKILL.md)")
    args.client = args.client or "100"
    args.lang = args.lang or "EN"

    # Resolve TLS verification before opening a session.
    tls_verify = _resolve_tls_verify(args)
    _warn_insecure_once(tls_verify)

    # Inject --user into args so creation commands can set adtcore:responsible
    # (args.user is already the SAP logon user from the global --user flag)

    # Confirmation guards for destructive operations
    if args.command == "delete" and not getattr(args, "force", False):
        confirm = input(f"Delete {args.name} ({args.type})? [y/N] ").strip()
        if confirm.lower() != "y":
            print(json.dumps({"message": "Aborted"}))
            return

    if args.command == "delete-transport" and not getattr(args, "force", False):
        trs = ", ".join(getattr(args, "transports", []))
        confirm = input(f"Delete transport(s) {trs}? This cannot be undone. [y/N] ").strip()
        if confirm.lower() != "y":
            print(json.dumps({"message": "Aborted"}))
            return

    try:
        session = make_session(args.url, args.user, args.pwd, args.client, args.lang,
                               verify=tls_verify)
    except requests.exceptions.RequestException as e:
        print(json.dumps({"error": f"Could not connect to {args.url}: {e}"}))
        sys.exit(1)

    handlers = {
        "search":                   cmd_search,
        "objects":                  cmd_objects,
        "packages":                 cmd_packages,
        "packages-by-responsible":  cmd_packages_by_responsible,
        "objects-by-user":          cmd_objects_by_user,
        "reports-by-user":          cmd_reports_by_user,
        "source":                   cmd_source,
        "write-source":             cmd_write_source,
        "atc-check":                cmd_atc_check,
        "delete":                   cmd_delete,
        "where-used":               cmd_where_used,
        "history":                  cmd_history,
        "diff":                     cmd_diff,
        "transports":               cmd_transports,
        "create-package":           cmd_create_package,
        "create-program":           cmd_create_program,
        "create-message-class":     cmd_create_message_class,
        "create-transaction":       cmd_create_transaction,
        "create-function-group":    cmd_create_function_group,
        "create-class":             cmd_create_class,
        "create-interface":         cmd_create_interface,
        "read-message-class":       cmd_read_message_class,
        "write-messages":           cmd_write_messages,
        "add-message":              cmd_add_message,
        "update-message":           cmd_add_message,
        "delete-message":           cmd_delete_message,
        "object-properties":        cmd_object_properties,
        "unlock":                   cmd_unlock,
        "inactive-objects":         cmd_inactive_objects,
        "delete-transport":         cmd_delete_transport,
        "create-transport":         cmd_create_transport,
        "release-transport":        cmd_release_transport,
        "move-object":              cmd_move_object,
        "create-function-module":   cmd_create_function_module,
        "abap-unit":                cmd_abap_unit,
        "activate":                 cmd_activate,
        "transport-contents":       cmd_transport_contents,
        "discovery":                cmd_discovery,
        "create-cds":               cmd_create_cds,
        "read-text-elements":       cmd_read_text_elements,
        "write-text-elements":      cmd_write_text_elements,
    }

    try:
        result = handlers[args.command](session, args.url, args)
    except requests.exceptions.RequestException as e:
        print(json.dumps({"error": f"HTTP request failed: {e}"}))
        sys.exit(1)
    except OSError as e:
        print(json.dumps({"error": f"File error: {e}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"{type(e).__name__}: {e}"}))
        sys.exit(1)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
