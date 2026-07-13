import os
import sys
import argparse
import json
import hashlib
import mimetypes
import subprocess
import urllib.parse
from pathlib import Path

# Fallback requests check
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Load .env if present
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

ROOT = Path(__file__).resolve().parent.parent


def env_value(*names):
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return ""


def get_oauth_token():
    url = env_value("CPI_OAUTH_TOKEN_URL", "CPI_TOKEN_URL")
    client_id = env_value("CPI_OAUTH_CLIENT_ID", "CPI_CLIENT_ID")
    client_secret = env_value("CPI_OAUTH_CLIENT_SECRET", "CPI_CLIENT_SECRET")
    
    if not url or not client_id or not client_secret:
        raise ValueError("Missing CPI OAuth configuration in environment (CPI_OAUTH_TOKEN_URL, CPI_OAUTH_CLIENT_ID, CPI_OAUTH_CLIENT_SECRET)")
    
    payload = {"grant_type": "client_credentials"}
    response = requests.post(url, data=payload, auth=(client_id, client_secret))
    response.raise_for_status()
    return response.json().get("access_token")


def cpi_base_url():
    base_url = env_value("CPI_BASE_URL", "CPI_TENANT_URL")
    if not base_url:
        raise ValueError("Missing CPI_BASE_URL in environment")
    return base_url.rstrip("/")


def cpi_session():
    token = get_oauth_token()
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {token}", "Accept": "application/json"})
    return session


def query_cpi_odata(endpoint, params=None):
    session = cpi_session()
    url = f"{cpi_base_url()}{endpoint}"
    response = session.get(url, params=params)
    response.raise_for_status()
    return response.json()


def fetch_csrf(session, endpoint="/api/v1/"):
    url = f"{cpi_base_url()}{endpoint}"
    response = session.get(url, headers={"X-CSRF-Token": "Fetch"})
    response.raise_for_status()
    token = response.headers.get("X-CSRF-Token") or response.headers.get("x-csrf-token")
    if token:
        session.headers.update({"X-CSRF-Token": token})
    return token


def stable_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def json_sha256(value):
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def shell_quote(value):
    text = str(value)
    if not text:
        return '""'
    if any(ch.isspace() for ch in text) or any(ch in text for ch in '"&|<>'):
        return '"' + text.replace('"', '\\"') + '"'
    return text


def odata_quote(value):
    return str(value).replace("'", "''")


def design_artifact_path(artifact_id, version):
    return f"/api/v1/IntegrationDesigntimeArtifacts(Id='{odata_quote(artifact_id)}',Version='{odata_quote(version)}')"


def read_binary(path):
    candidate = Path(path)
    if not candidate.exists() or not candidate.is_file():
        raise ValueError(f"ZIP file not found: {path}")
    return candidate.read_bytes()


def cpi_mutating_request(session, method, endpoint, body=b"", headers=None):
    fetch_csrf(session)
    url = f"{cpi_base_url()}{endpoint}"
    response = session.request(method, url, data=body, headers=headers or {}, timeout=60)
    return response


def method_is_blocked(response):
    text = response.text[:500].lower()
    return response.status_code in {403, 405, 501} and any(token in text for token in ("method", "put", "not allowed", "not implemented", "forbidden"))


def upload_iflow_zip(artifact_id, version, zip_file, strategy="auto"):
    session = cpi_session()
    body = read_binary(zip_file)
    content_type = mimetypes.guess_type(zip_file)[0] or "application/zip"
    endpoint = design_artifact_path(artifact_id, version) + "/$value"
    headers = {"Content-Type": content_type, "Accept": "application/json"}
    attempts = []

    def attempt(name, method, extra_headers=None):
        request_headers = dict(headers)
        request_headers.update(extra_headers or {})
        response = cpi_mutating_request(session, method, endpoint, body=body, headers=request_headers)
        attempts.append({"strategy": name, "method": method, "http_status": response.status_code, "ok": response.ok})
        return response

    if strategy in {"auto", "put"}:
        response = attempt("put", "PUT")
        if response.ok:
            return {"status": "OK", "operation": "upload", "strategy": "put", "attempts": attempts, "body": response.text[:20000]}
        if strategy == "put" or not method_is_blocked(response):
            response.raise_for_status()

    if strategy in {"auto", "post-override"}:
        response = attempt("post-override", "POST", {"X-HTTP-Method-Override": "PUT"})
        if response.ok:
            return {"status": "OK", "operation": "upload", "strategy": "post-override", "attempts": attempts, "body": response.text[:20000]}
        response.raise_for_status()

    return {"status": "ERROR", "operation": "upload", "attempts": attempts}


def deploy_runtime_artifact(artifact_id, version):
    session = cpi_session()
    params = urllib.parse.urlencode({"Id": f"'{artifact_id}'", "Version": f"'{version}'"}, safe="'")
    endpoint = f"/api/v1/DeployIntegrationDesigntimeArtifact?{params}"
    response = cpi_mutating_request(session, "POST", endpoint, body=b"", headers={"Content-Type": "application/octet-stream"})
    if not response.ok:
        response.raise_for_status()
    return {"status": "OK", "operation": "deploy-runtime", "http_status": response.status_code, "body": response.text[:20000]}


def deploy_arguments(args):
    return {
        "artifact_id": args.artifact_id,
        "version": args.version,
        "zip": str(Path(args.zip).resolve()) if args.zip else "",
        "strategy": args.strategy,
        "runtime_deploy": bool(args.runtime_deploy),
    }


def deploy_preconditions(args):
    checks = {
        "zip_exists": bool(args.zip and Path(args.zip).exists()) if args.zip else True,
        "base_url_configured": bool(env_value("CPI_BASE_URL", "CPI_TENANT_URL")),
        "token_url_configured": bool(env_value("CPI_OAUTH_TOKEN_URL", "CPI_TOKEN_URL")),
        "client_id_configured": bool(env_value("CPI_OAUTH_CLIENT_ID", "CPI_CLIENT_ID")),
        "client_secret_configured": bool(env_value("CPI_OAUTH_CLIENT_SECRET", "CPI_CLIENT_SECRET")),
    }
    return checks


def run_approval_broker(command_args):
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


def plan_deploy(args):
    arguments = deploy_arguments(args)
    preconditions = deploy_preconditions(args)
    if not preconditions["zip_exists"]:
        raise ValueError(f"ZIP file not found: {args.zip}")
    summary_parts = [f"CPI deploy {args.artifact_id}:{args.version}"]
    if args.zip:
        summary_parts.append(f"upload via {args.strategy}")
    if args.runtime_deploy:
        summary_parts.append("runtime deploy via POST")
    plan = run_approval_broker([
        "plan",
        "--capability", "sap.cpi.artifact.deploy",
        "--target", f"{args.artifact_id}:{args.version}",
        "--summary", "; ".join(summary_parts),
        "--effect", "mutating",
        "--arguments-json", stable_json(arguments),
        "--preconditions-json", stable_json(preconditions),
    ])
    commit = [
        "python", "scripts/cpi_client.py", "deploy", "commit",
        "--artifact-id", args.artifact_id,
        "--version", args.version,
        "--strategy", args.strategy,
        "--action-id", plan["action_id"],
        "--plan-hash", plan["plan_hash"],
        "--argument-hash", plan["argument_hash"],
        "--precondition-hash", plan["precondition_hash"],
    ]
    if args.zip:
        commit.extend(["--zip", arguments["zip"]])
    if args.runtime_deploy:
        commit.append("--runtime-deploy")
    plan["commit_command"] = " ".join(shell_quote(item) for item in commit)
    plan["arguments"] = arguments
    plan["preconditions"] = preconditions
    return plan


def commit_deploy(args):
    arguments = deploy_arguments(args)
    preconditions = deploy_preconditions(args)
    if not all(preconditions.values()):
        return {"status": "BLOCKED", "reason": "preconditions-not-met", "preconditions": preconditions}
    run_approval_broker([
        "consume",
        args.action_id,
        "--plan-hash", args.plan_hash,
        "--argument-hash", args.argument_hash or json_sha256(arguments),
        "--precondition-hash", args.precondition_hash or json_sha256(preconditions),
    ])
    steps = []
    if args.zip:
        steps.append(upload_iflow_zip(args.artifact_id, args.version, args.zip, args.strategy))
    if args.runtime_deploy:
        steps.append(deploy_runtime_artifact(args.artifact_id, args.version))
    return {"status": "OK", "artifact_id": args.artifact_id, "version": args.version, "steps": steps}

def test_connection():
    try:
        token = get_oauth_token()
        print("OAuth2 Token retrieval: [OK]")
        base_url = os.environ.get("CPI_BASE_URL")
        if base_url:
            url = f"{base_url.rstrip('/')}/api/v1/"
            headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
            res = requests.get(url, headers=headers)
            print(f"CPI Service Catalog connection: [{res.status_code}]")
        return True
    except Exception as e:
        print(f"Connection check failed: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Python CPI OData Client")
    subparsers = parser.add_subparsers(dest="command", required=True)

    if not HAS_REQUESTS:
        print("Missing dependency 'requests'. Install: pip install requests", file=sys.stderr)
        sys.exit(1)
    
    subparsers.add_parser("test-connection", help="Validate OAuth2 token and API connectivity")
    
    packages_parser = subparsers.add_parser("packages", help="List or query integration packages")
    packages_parser.add_argument("--id", help="Filter by specific package ID")
    
    artifacts_parser = subparsers.add_parser("artifacts", help="List or query integration artifacts")
    artifacts_parser.add_argument("--package-id", help="Filter by package ID")
    artifacts_parser.add_argument("--runtime", action="store_true", help="List runtime artifacts instead of designtime")
    
    logs_parser = subparsers.add_parser("logs", help="Get message processing logs")
    logs_parser.add_argument("--top", type=int, default=10, help="Number of records to fetch")

    deploy_parser = subparsers.add_parser("deploy", help="Plan or commit CPI iFlow upload/deploy")
    deploy_sub = deploy_parser.add_subparsers(dest="deploy_command", required=True)
    for name in ("plan", "commit"):
        action_parser = deploy_sub.add_parser(name)
        action_parser.add_argument("--artifact-id", required=True, help="Integration flow artifact Id")
        action_parser.add_argument("--version", default="active", help="Design-time artifact version")
        action_parser.add_argument("--zip", help="Optional iFlow ZIP to upload before runtime deploy")
        action_parser.add_argument("--strategy", choices=["auto", "put", "post-override"], default="auto", help="Upload method strategy when --zip is used")
        action_parser.add_argument("--runtime-deploy", action="store_true", help="Call DeployIntegrationDesigntimeArtifact after upload or as standalone deploy")
    commit_parser = deploy_sub.choices["commit"]
    commit_parser.add_argument("--action-id", required=True)
    commit_parser.add_argument("--plan-hash", required=True)
    commit_parser.add_argument("--argument-hash")
    commit_parser.add_argument("--precondition-hash")
    
    args = parser.parse_args()
    
    if args.command == "test-connection":
        success = test_connection()
        sys.exit(0 if success else 1)
        
    elif args.command == "packages":
        try:
            endpoint = "/api/v1/IntegrationPackages"
            if args.id:
                endpoint += f"('{args.id}')"
            data = query_cpi_odata(endpoint)
            print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Error querying packages: {e}", file=sys.stderr)
            sys.exit(1)
            
    elif args.command == "artifacts":
        try:
            if args.runtime:
                endpoint = "/api/v1/IntegrationRuntimeArtifacts"
            else:
                endpoint = "/api/v1/IntegrationDesigntimeArtifacts"
                
            params = {}
            if args.package_id and not args.runtime:
                params["$filter"] = f"PackageId eq '{args.package_id}'"
                
            data = query_cpi_odata(endpoint, params=params)
            print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Error querying artifacts: {e}", file=sys.stderr)
            sys.exit(1)
            
    elif args.command == "logs":
        try:
            endpoint = "/api/v1/MessageProcessingLogs"
            params = {"$top": args.top}
            data = query_cpi_odata(endpoint, params=params)
            print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Error querying logs: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.command == "deploy":
        try:
            result = plan_deploy(args) if args.deploy_command == "plan" else commit_deploy(args)
            print(json.dumps(result, indent=2))
            sys.exit(0 if result.get("status") == "OK" or result.get("status") == "PENDING" else 1)
        except Exception as e:
            print(json.dumps({"status": "ERROR", "error": str(e)}, indent=2), file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
