#!/usr/bin/env python3
"""
APIM Proxy Packager - create, validate, extract and list SAP API Management proxy bundles.

Bundle structure, per help.sap.com "API Proxy Structure"
(https://help.sap.com/docs/integration-suite/sap-integration-suite/api-proxy-structure-4dfd54a):

  APIProxy/<name>.xml            - proxy header: endpoints, policies, file resources
  APIProxyEndPoint/<name>.xml    - inbound endpoint: base path, route rules, flows
  APITargetEndPoint/<name>.xml   - outbound endpoint: backend URL
  Policy/<PolicyName>.xml        - one file per policy, namespace http://www.sap.com/apimgmt
  APIResource/, FileResource/, Documentation/ - optional, omitted when empty
  manifest.json                  - packager metadata, ignored by the tenant

The tenant's own export is the authoritative layout. Before relying on a generated
bundle for a production import, export an existing proxy and diff against it:

  apim_execute_action proxies.export --name <existing proxy>
  python scripts/apim_proxy_packager.py extract --input <export.zip> --output ref/

Two starter models ship with this repo:
  echo    - TargetEndpoint pointing at a public echo service; smoke-tests without a backend
  backend - parametrised for a real backend, with API key verification and quota

Usage:
  python scripts/apim_proxy_packager.py template --kind echo --name <proxy> [--output <file.zip>]
  python scripts/apim_proxy_packager.py template --kind backend --name <proxy> --backend-url <url>
        [--basepath /path] [--output <file.zip>]

  python scripts/apim_proxy_packager.py create --name <proxy> --source <dir> [--output <file.zip>]
  python scripts/apim_proxy_packager.py validate --input <file.zip> [--json]
  python scripts/apim_proxy_packager.py extract --input <file.zip> --output <dir>
  python scripts/apim_proxy_packager.py list --input <file.zip>

Policy XML follows the patterns published in SAP/apibusinesshub-api-recipes (Apache-2.0).
"""

import argparse
import json
import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

# Bundles can come from anywhere, so parse them with defusedxml when it is
# installed; the stdlib parser is the fallback and still refuses external
# entities, but it does not guard against entity-expansion bombs.
try:
    from defusedxml.ElementTree import fromstring as xml_fromstring
except ModuleNotFoundError:  # pragma: no cover - depends on local install
    xml_fromstring = ET.fromstring

ECHO_BACKEND = "https://httpbin.org/anything"

SAP_NS = "http://www.sap.com/apimgmt"

PROXY_DESCRIPTOR = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<APIProxy>
  <name>{name}</name>
  <title>{name}</title>
  <description>{description}</description>
  <version>1</version>
  <created_at>{date}</created_at>
  <apiProxyEndPoints>
    <apiProxyEndPoint>default</apiProxyEndPoint>
  </apiProxyEndPoints>
  <apiTargetEndPoints>
    <apiTargetEndPoint>default</apiTargetEndPoint>
  </apiTargetEndPoints>
  <policies>
{policy_list}  </policies>
</APIProxy>
"""

PROXY_ENDPOINT = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ProxyEndPoint default="true">
  <name>default</name>
  <base_path>{basepath}</base_path>
  <properties/>
  <routeRules>
    <routeRule>
      <name>default</name>
      <targetEndPointName>default</targetEndPointName>
      <sequence>1</sequence>
      <faultRules/>
    </routeRule>
  </routeRules>
  <faultRules/>
  <preFlow>
    <name>PreFlow</name>
    <request>
{request_steps}    </request>
    <response>
{response_steps}    </response>
  </preFlow>
  <postFlow>
    <name>PostFlow</name>
  </postFlow>
  <conditionalFlows/>
</ProxyEndPoint>
"""

TARGET_ENDPOINT = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<TargetEndPoint default="true">
  <name>default</name>
  <url>{backend_url}</url>
  <properties/>
  <faultRules/>
  <preFlow>
    <name>PreFlow</name>
  </preFlow>
  <postFlow>
    <name>PostFlow</name>
  </postFlow>
  <conditionalFlows/>
</TargetEndPoint>
"""

STEP = """      <step>
        <name>{name}</name>
      </step>
"""

POLICY_SPIKE_ARREST = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<SpikeArrest async="true" continueOnError="false" enabled="true" xmlns="{ns}">
  <Identifier ref="client.ip"/>
  <Rate>30pm</Rate>
</SpikeArrest>
""".format(ns=SAP_NS)

POLICY_CORS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<AssignMessage async="false" continueOnError="false" enabled="true" xmlns="{ns}">
  <Set>
    <Headers>
      <Header name="Access-Control-Allow-Origin">*</Header>
      <Header name="Access-Control-Allow-Headers">origin, x-requested-with, accept, content-type, apikey</Header>
      <Header name="Access-Control-Allow-Methods">GET, PUT, POST, DELETE, PATCH, OPTIONS</Header>
    </Headers>
  </Set>
  <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
  <AssignTo createNew="false" transport="http" type="response"/>
</AssignMessage>
""".format(ns=SAP_NS)

POLICY_TRACE_HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<AssignMessage async="false" continueOnError="false" enabled="true" xmlns="{ns}">
  <Add>
    <Headers>
      <Header name="X-Router-Smoke-Test">sap-router-orchestrator</Header>
    </Headers>
  </Add>
  <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
  <AssignTo createNew="false" transport="http" type="request"/>
</AssignMessage>
""".format(ns=SAP_NS)

POLICY_VERIFY_API_KEY = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<VerifyAPIKey async="true" continueOnError="false" enabled="true" xmlns="{ns}">
  <APIKey ref="request.header.apikey"/>
</VerifyAPIKey>
""".format(ns=SAP_NS)

POLICY_QUOTA = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Quota type="calendar" async="true" continueOnError="true" enabled="true" xmlns="{ns}">
  <Identifier ref="verifyapikey.Verify-API-Key.client_id"/>
  <Allow count="10000"/>
  <Interval>1</Interval>
  <TimeUnit>month</TimeUnit>
  <Distributed>true</Distributed>
  <Synchronous>true</Synchronous>
</Quota>
""".format(ns=SAP_NS)

TEMPLATES = {
    "echo": {
        "description": "Smoke-test proxy targeting a public echo service. No backend required.",
        "backend_url": ECHO_BACKEND,
        "basepath": "/router-echo",
        "request_policies": ["Spike-Arrest", "Add-Trace-Header"],
        "response_policies": ["Add-CORS"],
        "policies": {
            "Spike-Arrest": POLICY_SPIKE_ARREST,
            "Add-Trace-Header": POLICY_TRACE_HEADER,
            "Add-CORS": POLICY_CORS,
        },
    },
    "backend": {
        "description": "Proxy for a real backend, secured with API key verification and a monthly quota.",
        "backend_url": None,
        "basepath": "/router-api",
        "request_policies": ["Verify-API-Key", "Quota", "Spike-Arrest"],
        "response_policies": ["Add-CORS"],
        "policies": {
            "Verify-API-Key": POLICY_VERIFY_API_KEY,
            "Quota": POLICY_QUOTA,
            "Spike-Arrest": POLICY_SPIKE_ARREST,
            "Add-CORS": POLICY_CORS,
        },
    },
}

REQUIRED_DIRS = ("APIProxy/", "APIProxyEndPoint/", "APITargetEndPoint/")
POLICY_DIR = "Policy/"


def steps_xml(policy_names):
    if not policy_names:
        return ""
    return "".join(STEP.format(name=name) for name in policy_names)


def build_bundle(name, kind, backend_url, basepath):
    spec = TEMPLATES[kind]
    resolved_backend = backend_url or spec["backend_url"]
    if not resolved_backend:
        raise ValueError("template kind 'backend' requires --backend-url")
    resolved_basepath = basepath or spec["basepath"]
    date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    policy_names = sorted(spec["policies"])
    files = {
        "APIProxy/{0}.xml".format(name): PROXY_DESCRIPTOR.format(
            name=name,
            description=spec["description"],
            date=date,
            policy_list="".join("    <policy>{0}</policy>\n".format(p) for p in policy_names),
        ),
        "APIProxyEndPoint/default.xml": PROXY_ENDPOINT.format(
            basepath=resolved_basepath,
            request_steps=steps_xml(spec["request_policies"]),
            response_steps=steps_xml(spec["response_policies"]),
        ),
        "APITargetEndPoint/default.xml": TARGET_ENDPOINT.format(backend_url=resolved_backend),
        "manifest.json": json.dumps(
            {
                "name": name,
                "kind": kind,
                "basepath": resolved_basepath,
                "backend_url": resolved_backend,
                "created_at": date,
                "generator": "sap-router-orchestrator apim_proxy_packager",
                "layout_source": "help.sap.com API Proxy Structure (4dfd54a)",
                "policy_source": "patterns from SAP/apibusinesshub-api-recipes (Apache-2.0)",
                "verify_against": "an export of an existing tenant proxy before production import",
            },
            indent=2,
        )
        + "\n",
    }
    for policy_name, policy_xml in spec["policies"].items():
        files["{0}{1}.xml".format(POLICY_DIR, policy_name)] = policy_xml
    return files


def write_zip(output, files):
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, content in sorted(files.items()):
            zf.writestr(path, content)


def cmd_template(args):
    if args.kind not in TEMPLATES:
        print("ERROR: unknown kind '{0}'".format(args.kind), file=sys.stderr)
        return 1
    output = args.output or "{0}-{1}.zip".format(args.name, args.kind)
    try:
        files = build_bundle(args.name, args.kind, args.backend_url, args.basepath)
    except ValueError as exc:
        print("ERROR: {0}".format(exc), file=sys.stderr)
        return 1
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    write_zip(output, files)
    size = os.path.getsize(output)
    print("Created APIM proxy bundle: {0} ({1:,} bytes)".format(output, size))
    for path in sorted(files):
        print("    {0}".format(path))
    return 0


def cmd_create(args):
    source = Path(args.source)
    if not source.is_dir():
        print("ERROR: {0} is not a directory".format(source), file=sys.stderr)
        return 1
    output = args.output or "{0}.zip".format(args.name)
    files = {}
    for item in sorted(source.rglob("*")):
        if item.is_file():
            files[item.relative_to(source).as_posix()] = item.read_text(encoding="utf-8", errors="replace")
    if not files:
        print("ERROR: no files found under {0}".format(source), file=sys.stderr)
        return 1
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    write_zip(output, files)
    print("Created APIM proxy bundle: {0} ({1:,} bytes)".format(output, os.path.getsize(output)))
    return 0


def collect_referenced_policies(endpoint_xml_bytes):
    """Policy names referenced by flow steps.

    Only <step><name> counts - an endpoint document also carries <name> for
    itself, its flows and its route rules, none of which are policies.
    """
    referenced = set()
    try:
        root = xml_fromstring(endpoint_xml_bytes)
    except ET.ParseError:
        return referenced
    for tag in ("step", "Step"):
        for step in root.iter(tag):
            for child in step:
                if child.tag.lower().endswith("name") and child.text:
                    referenced.add(child.text.strip())
    return referenced


def cmd_validate(args):
    input_path = Path(args.input)
    errors = []
    warnings = []
    report = {"input": str(input_path), "status": "OK", "errors": errors, "warnings": warnings}

    if not input_path.exists():
        errors.append("file not found: {0}".format(input_path))
    elif not zipfile.is_zipfile(input_path):
        errors.append("not a valid ZIP file: {0}".format(input_path))

    if not errors:
        with zipfile.ZipFile(input_path, "r") as zf:
            names = zf.namelist()
            for required in REQUIRED_DIRS:
                if not any(entry.startswith(required) for entry in names):
                    errors.append("missing required folder: {0}".format(required))

            for entry in names:
                if entry.endswith(".xml"):
                    try:
                        xml_fromstring(zf.read(entry))
                    except ET.ParseError as exc:
                        errors.append("{0}: invalid XML - {1}".format(entry, exc))

            # Tenant exports have used both spellings; accept either.
            policy_files = {
                Path(e).stem for e in names if e.startswith(("Policy/", "Policies/")) and e.endswith(".xml")
            }
            referenced = set()
            for entry in names:
                if entry.startswith(("APIProxyEndPoint/", "APITargetEndPoint/", "Proxies/", "Targets/")) and entry.endswith(".xml"):
                    referenced |= collect_referenced_policies(zf.read(entry))
            missing = referenced - policy_files
            for name in sorted(missing):
                errors.append("flow references policy '{0}' but {1}{0}.xml is absent".format(name, POLICY_DIR))
            for name in sorted(policy_files - referenced):
                warnings.append("policy '{0}' is defined but not referenced by any flow".format(name))

            report["entries"] = len(names)
            report["policies"] = sorted(policy_files)

    report["status"] = "ERROR" if errors else ("WARN" if warnings else "OK")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Validation: {0}".format(report["status"]))
        for item in errors:
            print("  ERROR: {0}".format(item))
        for item in warnings:
            print("  WARN: {0}".format(item))
    return 1 if errors else 0


def cmd_extract(args):
    input_path = Path(args.input)
    if not zipfile.is_zipfile(input_path):
        print("ERROR: not a valid ZIP file: {0}".format(input_path), file=sys.stderr)
        return 1
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(input_path, "r") as zf:
        zf.extractall(output)
    print("Extracted {0} to {1}".format(input_path, output))
    return 0


def cmd_list(args):
    input_path = Path(args.input)
    if not zipfile.is_zipfile(input_path):
        print("ERROR: not a valid ZIP file: {0}".format(input_path), file=sys.stderr)
        return 1
    with zipfile.ZipFile(input_path, "r") as zf:
        for info in zf.infolist():
            print("    {0} ({1:,} bytes)".format(info.filename, info.file_size))
    return 0


def main():
    parser = argparse.ArgumentParser(description="SAP API Management proxy bundle packager")
    sub = parser.add_subparsers(dest="command", required=True)

    t = sub.add_parser("template", help="Generate a starter proxy bundle")
    t.add_argument("--kind", default="echo", choices=sorted(TEMPLATES), help="Which starter model to generate")
    t.add_argument("--name", default="ZROUTER_SMOKE", help="Proxy name")
    t.add_argument("--backend-url", help="Backend URL (required for kind 'backend')")
    t.add_argument("--basepath", help="Override the proxy base path")
    t.add_argument("--output", help="Output ZIP path")

    c = sub.add_parser("create", help="Build a bundle ZIP from a source directory")
    c.add_argument("--name", required=True)
    c.add_argument("--source", required=True, help="Directory holding APIProxy/, Proxies/, Targets/, Policies/")
    c.add_argument("--output")

    v = sub.add_parser("validate", help="Validate a bundle ZIP offline")
    v.add_argument("--input", required=True)
    v.add_argument("--json", action="store_true")

    e = sub.add_parser("extract", help="Extract a bundle ZIP")
    e.add_argument("--input", required=True)
    e.add_argument("--output", required=True)

    l = sub.add_parser("list", help="List bundle contents")
    l.add_argument("--input", required=True)

    args = parser.parse_args()
    handlers = {
        "template": cmd_template,
        "create": cmd_create,
        "validate": cmd_validate,
        "extract": cmd_extract,
        "list": cmd_list,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
