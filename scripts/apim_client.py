#!/usr/bin/env python3
"""SAP API Management API helper with plan/approval/commit semantics."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import mimetypes
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN_DIR = ROOT / "scratch" / "apim-plans"


def load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def stable_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def json_sha256(value: object) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def shell_quote(value: object) -> str:
    text = str(value)
    if not text:
        return '""'
    if any(ch.isspace() for ch in text) or any(ch in text for ch in '"&|<>'):
        return '"' + text.replace('"', '\\"') + '"'
    return text


def odata_quote(value: str) -> str:
    return value.replace("'", "''")


def run_approval_broker(command_args: list[str]) -> dict:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "approval_broker.py")] + command_args,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        payload = {"status": "ERROR", "error": result.stdout or result.stderr}
    if result.returncode != 0:
        raise RuntimeError(json.dumps(payload))
    return payload


class ApimClient:
    def __init__(self) -> None:
        self.base = os.environ.get("APIM_HOST", "").rstrip("/")
        self.user = os.environ.get("APIM_USER", "")
        self.password = os.environ.get("APIM_PASSWORD", "")
        self.csrf_token = ""

    def _headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.user and self.password:
            token = base64.b64encode(f"{self.user}:{self.password}".encode()).decode()
            headers["Authorization"] = f"Basic {token}"
        if self.csrf_token:
            headers["X-CSRF-Token"] = self.csrf_token
        if extra:
            headers.update(extra)
        return headers

    def configured(self) -> tuple[bool, str]:
        if not self.base:
            return False, "APIM_HOST missing"
        if not self.user or not self.password:
            return False, "APIM_USER/APIM_PASSWORD missing"
        return True, "configured"

    def request(self, path: str, method: str = "GET", body: bytes | None = None, headers: dict[str, str] | None = None) -> dict:
        ok, reason = self.configured()
        if not ok:
            return {"status": "BLOCKED", "reason": reason}
        url = self.base + path
        req = urllib.request.Request(url, data=body, method=method, headers=self._headers(headers))
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                payload = response.read().decode("utf-8", errors="replace")
                return {"status": "OK", "http_status": response.status, "url": url, "body": payload[:20000]}
        except urllib.error.HTTPError as exc:
            return {"status": "ERROR", "http_status": exc.code, "url": url, "body": exc.read().decode("utf-8", errors="replace")[:20000]}
        except urllib.error.URLError as exc:
            return {"status": "ERROR", "url": url, "reason": str(exc.reason)}

    def fetch_csrf(self) -> dict:
        result = self.request("/apiportal/api/1.0/Management.svc/", headers={"X-CSRF-Token": "Fetch"})
        # urllib does not expose headers through request() result, so fetch directly here.
        ok, reason = self.configured()
        if not ok:
            return {"status": "BLOCKED", "reason": reason}
        req = urllib.request.Request(
            self.base + "/apiportal/api/1.0/Management.svc/",
            method="GET",
            headers=self._headers({"X-CSRF-Token": "Fetch"}),
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                self.csrf_token = response.headers.get("X-CSRF-Token", "")
                return {"status": "OK", "token_received": bool(self.csrf_token)}
        except urllib.error.HTTPError as exc:
            token = exc.headers.get("X-CSRF-Token", "") if exc.headers else ""
            if token:
                self.csrf_token = token
                return {"status": "OK", "token_received": True, "http_status": exc.code}
            return {"status": "ERROR", "http_status": exc.code, "body": exc.read().decode("utf-8", errors="replace")[:20000], "prior": result}
        except urllib.error.URLError as exc:
            return {"status": "ERROR", "reason": str(exc.reason), "prior": result}

    def mutate(self, path: str, method: str, body: bytes, content_type: str, strategy: str) -> dict:
        csrf = self.fetch_csrf()
        if csrf.get("status") != "OK":
            return {"status": "ERROR", "stage": "csrf", "csrf": csrf}
        attempts = []

        def attempt(name: str, actual_method: str, extra: dict[str, str] | None = None) -> dict:
            headers = {"Content-Type": content_type}
            if extra:
                headers.update(extra)
            result = self.request(path, method=actual_method, body=body, headers=headers)
            attempts.append({"strategy": name, "method": actual_method, "http_status": result.get("http_status"), "status": result.get("status")})
            return result

        primary = attempt(method.lower(), method)
        if primary.get("status") == "OK":
            primary["attempts"] = attempts
            return primary
        blocked = primary.get("http_status") in {403, 405, 501}
        if strategy in {"auto", "post-override"} and method.upper() != "POST" and blocked:
            override = attempt("post-override", "POST", {"X-HTTP-Method-Override": method.upper()})
            override["attempts"] = attempts
            return override
        primary["attempts"] = attempts
        return primary


def default_proxy_bundle_path(target: str) -> str:
    proxy_id = urllib.parse.quote(odata_quote(target), safe="")
    return f"/apiportal/api/1.0/Management.svc/APIProxies('{proxy_id}')/$value"


def deploy_arguments(args: argparse.Namespace) -> dict:
    path = args.path or default_proxy_bundle_path(args.target)
    return {
        "bundle": str(Path(args.bundle).resolve()) if args.bundle else "",
        "target": args.target,
        "path": path,
        "method": args.method.upper(),
        "strategy": args.strategy,
        "content_type": args.content_type or (mimetypes.guess_type(args.bundle or "")[0] or "application/octet-stream"),
    }


def deploy_preconditions(args: argparse.Namespace) -> dict:
    return {
        "bundle_exists": bool(args.bundle and Path(args.bundle).exists()),
        "host_configured": bool(os.environ.get("APIM_HOST")),
        "user_configured": bool(os.environ.get("APIM_USER")),
        "password_configured": bool(os.environ.get("APIM_PASSWORD")),
    }


def plan_deploy(args: argparse.Namespace) -> dict:
    PLAN_DIR.mkdir(parents=True, exist_ok=True)
    arguments = deploy_arguments(args)
    preconditions = deploy_preconditions(args)
    if not preconditions["bundle_exists"]:
        raise ValueError(f"Bundle file not found: {args.bundle}")
    plan_id = f"apim-{uuid.uuid4()}"
    local_plan = {
        "plan_id": plan_id,
        "action": "apim.deploy",
        "mutation": True,
        "requires_approval": True,
        "arguments": arguments,
        "preconditions": preconditions,
    }
    (PLAN_DIR / f"{plan_id}.json").write_text(json.dumps(local_plan, indent=2) + "\n", encoding="utf-8")
    broker_plan = run_approval_broker([
        "plan",
        "--capability", "sap.apim.proxy.deploy",
        "--target", args.target,
        "--summary", f"APIM deploy {args.target} via {arguments['method']} {arguments['path']}",
        "--effect", "mutating",
        "--arguments-json", stable_json(arguments),
        "--preconditions-json", stable_json(preconditions),
    ])
    commit = [
        "python", "scripts/apim_client.py", "deploy", "execute",
        "--plan-id", plan_id,
        "--action-id", broker_plan["action_id"],
        "--plan-hash", broker_plan["plan_hash"],
        "--argument-hash", broker_plan["argument_hash"],
        "--precondition-hash", broker_plan["precondition_hash"],
        "--confirm",
    ]
    broker_plan["apim_plan_id"] = plan_id
    broker_plan["arguments"] = arguments
    broker_plan["preconditions"] = preconditions
    broker_plan["commit_command"] = " ".join(shell_quote(item) for item in commit)
    return broker_plan


def execute_plan(args: argparse.Namespace) -> dict:
    if not args.confirm:
        return {"status": "BLOCKED", "reason": "Missing --confirm. Review and approve the plan first."}
    path = PLAN_DIR / f"{args.plan_id}.json"
    if not path.exists():
        return {"status": "ERROR", "reason": f"Plan not found: {args.plan_id}"}
    plan = json.loads(path.read_text(encoding="utf-8"))
    arguments = plan["arguments"]
    preconditions = deploy_preconditions(argparse.Namespace(bundle=arguments["bundle"]))
    if not all(preconditions.values()):
        return {"status": "BLOCKED", "reason": "preconditions-not-met", "preconditions": preconditions}
    run_approval_broker([
        "consume",
        args.action_id,
        "--plan-hash", args.plan_hash,
        "--argument-hash", args.argument_hash or json_sha256(arguments),
        "--precondition-hash", args.precondition_hash or json_sha256(preconditions),
    ])
    body = Path(arguments["bundle"]).read_bytes()
    client = ApimClient()
    result = client.mutate(
        arguments["path"],
        arguments["method"],
        body,
        arguments["content_type"],
        arguments["strategy"],
    )
    result["plan_id"] = args.plan_id
    result["target"] = arguments["target"]
    return result


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser(description="SAP API Management helper.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("health")
    proxies = sub.add_parser("proxies")
    proxies.add_argument("action", choices=["list", "export"])
    proxies.add_argument("--id")
    policies = sub.add_parser("policies")
    policies.add_argument("action", choices=["validate"])
    policies.add_argument("--file", required=True)
    deploy = sub.add_parser("deploy")
    deploy.add_argument("action", choices=["plan", "execute"])
    deploy.add_argument("--bundle")
    deploy.add_argument("--target", default="default")
    deploy.add_argument("--path", help="Relative APIM Management.svc/API path. Defaults to APIProxies('<target>')/$value.")
    deploy.add_argument("--method", choices=["PUT", "POST", "PATCH", "DELETE"], default="PUT")
    deploy.add_argument("--strategy", choices=["auto", "direct", "post-override"], default="auto")
    deploy.add_argument("--content-type")
    deploy.add_argument("--plan-id")
    deploy.add_argument("--action-id")
    deploy.add_argument("--plan-hash")
    deploy.add_argument("--argument-hash")
    deploy.add_argument("--precondition-hash")
    deploy.add_argument("--confirm", action="store_true")
    args = parser.parse_args()

    client = ApimClient()
    if args.command == "health":
        ok, reason = client.configured()
        if not ok:
            result = {"status": "BLOCKED", "host_configured": bool(client.base), "auth_configured": bool(client.user and client.password), "reason": reason}
        else:
            result = client.request("/apiportal/api/1.0/Management.svc/APIProxies?$top=1")
            result["host_configured"] = True
            result["auth_configured"] = True
    elif args.command == "proxies":
        if args.action == "list":
            result = client.request("/apiportal/api/1.0/Management.svc/APIProxies")
        else:
            if not args.id:
                print("ERROR: --id required", file=sys.stderr)
                return 2
            proxy_id = urllib.parse.quote(args.id, safe="")
            result = client.request(f"/apiportal/api/1.0/Management.svc/APIProxies('{proxy_id}')")
    elif args.command == "policies":
        policy = Path(args.file)
        result = {"status": "OK" if policy.exists() and policy.suffix.lower() == ".xml" else "ERROR", "file": str(policy), "rule": "Policy file must exist and be XML."}
    elif args.command == "deploy":
        try:
            if args.action == "plan":
                if not args.bundle:
                    print("ERROR: --bundle required", file=sys.stderr)
                    return 2
                result = plan_deploy(args)
            else:
                for required in ("plan_id", "action_id", "plan_hash"):
                    if not getattr(args, required):
                        print(f"ERROR: --{required.replace('_', '-')} required", file=sys.stderr)
                        return 2
                result = execute_plan(args)
        except Exception as exc:
            result = {"status": "ERROR", "reason": str(exc)}
    else:
        result = {"status": "ERROR", "reason": "unknown command"}

    print(json.dumps(result, indent=2))
    return 0 if result.get("status") in {"OK", "PENDING"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
