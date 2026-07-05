#!/usr/bin/env python3
"""
ZROUTER Deploy v4.2.0 — arc-1 CLI installer
Creates all 23 ZROUTER objects on SAP via npx arc-1 call.
Reads .env for credentials. Uses $TMP package (safety restriction).
"""

import subprocess
import sys
import os
import json
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEPLOY_DIR = SKILL_DIR / "deploy" / "split2"

# ── Load .env ──────────────────────────────────────────────────
def load_env():
    env_file = SKILL_DIR / ".env"
    if not env_file.exists():
        return {}
    env = {}
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()
    return env

ENV = load_env()
ARC_ENV = {
    "ARC_SAP_URL": ENV.get("ARC_SAP_URL", ""),
    "ARC_SAP_USER": ENV.get("ARC_SAP_USER", ""),
    "ARC_SAP_PASSWORD": ENV.get("ARC_SAP_PASSWORD", ""),
    "ARC_SAP_CLIENT": ENV.get("ARC_SAP_CLIENT", "100"),
    "SAP_ALLOW_WRITES": "true",
    "NODE_TLS_REJECT_UNAUTHORIZED": "0",
}

# Use node directly + arc-1 CLI to avoid Windows cmd.exe escaping
NODE_PATH = os.path.expandvars(r"%ProgramFiles%\nodejs\node.exe")
if not Path(NODE_PATH).exists():
    NODE_PATH = "node"  # fallback
ARC1_CLI = os.path.expandvars(
    r"%AppData%\Roaming\npm\node_modules\arc-1\dist\cli.js"
)
if not Path(ARC1_CLI).exists():
    ARC1_CLI = "C:\\Users\\William Correa\\AppData\\Roaming\\npm\\node_modules\\arc-1\\dist\\cli.js"

if not ARC_ENV["ARC_SAP_URL"]:
    print("ERROR: ARC_SAP_URL not set in .env")
    sys.exit(1)


# ── arc-1 CLI helpers ──────────────────────────────────────────

def run_arc1(tool: str, args: dict, timeout: int = 120) -> dict:
    """Run arc-1 CLI via node + stdin pipe (avoids Windows shell escaping)."""
    json_args = json.dumps(args)
    cmd = [NODE_PATH, ARC1_CLI, "call", tool, "--json", "-"]
    env = {**os.environ, **ARC_ENV}
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            cwd=str(SKILL_DIR), env=env, input=json_args
        )
        combined = (result.stdout + result.stderr).strip()
        ok = (
            result.returncode == 0
            and ("Created" in combined or "Successfully" in combined
                 or 'status":"success"' in combined)
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "output": "", "error": "Timeout", "combined": "", "code": -1}
    except Exception as e:
        return {"ok": False, "output": "", "error": str(e), "combined": "", "code": -1}

    return {
        "ok": ok,
        "output": result.stdout.strip(),
        "error": result.stderr.strip(),
        "combined": combined,
        "code": result.returncode,
    }


def create_object(obj_type: str, name: str, desc: str, devclass: str = "$TMP") -> dict:
    """Create ABAP object via arc-1 SAPWrite."""
    args = {
        "action": "create",
        "type": obj_type,
        "name": name.upper(),
        "description": desc,
        "devClass": devclass,
    }
    return run_arc1("SAPWrite", args)


def write_source(obj_type: str, name: str, source: str) -> dict:
    """Write source code to existing object via arc-1 SAPWrite."""
    args = {
        "action": "update",
        "type": obj_type,
        "name": name.upper(),
        "source": source,
        "lintBeforeWrite": False,  # Disable ABAP Cloud lint for on-prem SAP
    }
    return run_arc1("SAPWrite", args, timeout=120)


# ── Deploy Sequence ────────────────────────────────────────────

# Dependency-ordered: interfaces first, then standalone classes, then dependents
DEPLOY_ORDER = [
    # Exception class (standalone) — ZCX_ prefix per ABAP naming convention
    ("CLAS", "ZCX_ZROUTER", "ZROUTER Exception class"),
    # Interfaces
    ("INTF", "ZIF_ZROUTER_CONFIG", "ZROUTER Config interface"),
    ("INTF", "ZIF_ZROUTER_LOGGER", "ZROUTER Logger interface"),
    ("INTF", "ZIF_ZROUTER_HANDLER", "ZROUTER Handler interface"),
    # Infrastructure (depend on interfaces)
    ("CLAS", "ZCL_ZROUTER_CONFIG", "ZROUTER Config class"),
    ("CLAS", "ZCL_ZROUTER_LOGGER", "ZROUTER Logger class"),
    ("CLAS", "ZCL_ZROUTER_AUTHORITY", "ZROUTER Authority class"),
    # Abstract handler (depends on interfaces)
    ("CLAS", "ZCL_ZROUTER_HANDLER_ABSTRACT", "ZROUTER Abstract handler"),
    # Module handlers (depend on ABSTRACT)
    ("CLAS", "ZCL_ZROUTER_HANDLER_MM", "ZROUTER MM handler"),
    ("CLAS", "ZCL_ZROUTER_HANDLER_SD", "ZROUTER SD handler"),
    ("CLAS", "ZCL_ZROUTER_HANDLER_FI", "ZROUTER FI handler"),
    ("CLAS", "ZCL_ZROUTER_HANDLER_QM", "ZROUTER QM handler"),
    ("CLAS", "ZCL_ZROUTER_HANDLER_PP", "ZROUTER PP handler"),
    ("CLAS", "ZCL_ZROUTER_HANDLER_WM", "ZROUTER WM handler"),
    ("CLAS", "ZCL_ZROUTER_HANDLER_CO", "ZROUTER CO handler"),
    ("CLAS", "ZCL_ZROUTER_HANDLER_HCM", "ZROUTER HCM handler"),
    ("CLAS", "ZCL_ZROUTER_HANDLER_BASIS", "ZROUTER BASIS handler"),
    # Core (depends on all handlers)
    ("CLAS", "ZCL_ZROUTER_DISPATCH", "ZROUTER Central dispatcher"),
    ("CLAS", "ZCL_ZROUTER_BATCH", "ZROUTER Batch executor"),
]


def get_source_path(name: str, obj_type: str) -> Path:
    """Get path to split source file."""
    ext = "intf" if obj_type == "INTF" else "clas"
    return DEPLOY_DIR / f"{name.lower()}.{ext}.abap"


def deploy():
    """Main deploy function."""
    print("=" * 70)
    print("  ZROUTER Deploy v4.2.0 — arc-1 CLI Installer")
    print(f"  Target: {ARC_ENV['ARC_SAP_URL']}")
    print(f"  User: {ARC_ENV['ARC_SAP_USER']}")
    print(f"  Client: {ARC_ENV['ARC_SAP_CLIENT']}")
    print(f"  Package: $TMP (safety restriction)")
    print("=" * 70)
    print()

    created = []
    failed = []

    for idx, (obj_type, name, desc) in enumerate(DEPLOY_ORDER, 1):
        source_path = get_source_path(name, obj_type)
        if not source_path.exists():
            print(f"  [{idx}/{len(DEPLOY_ORDER)}] SKIP {obj_type} {name} — source file missing")
            failed.append((name, "Source file missing"))
            continue

        source = source_path.read_text(encoding="utf-8")
        print(f"  [{idx}/{len(DEPLOY_ORDER)}] {obj_type} {name} ({len(source)} chars)...", end=" ")

        # Step 1: Create object (or detect existing)
        create_result = create_object(obj_type, name, desc)
        if create_result["ok"]:
            pass  # Newly created, proceed to source write
        else:
            combined = (create_result.get("combined", "") +
                       create_result.get("output", "") +
                       create_result.get("error", ""))
            if any(x in combined.lower() for x in ["already exist", "created"]):
                print("(exists)", end=" ")
            else:
                print(f"CREATE FAILED: {create_result.get('error','')[:150]}")
                failed.append((name, "Create failed"))
                continue

        # Step 2: Write source
        result = write_source(obj_type, name, source)
        if result["ok"]:
            print("OK")
            created.append(name)
        else:
            combined2 = result.get("combined", result.get("output","") + result.get("error",""))
            print(f"SOURCE FAILED: {combined2[:200]}")
            failed.append((name, "Source write failed"))

    print()
    print("=" * 70)
    print(f"  RESULTS: {len(created)} created, {len(failed)} failed")
    if created:
        print(f"  Created: {', '.join(created)}")
    if failed:
        print(f"  Failed: {', '.join(f[0] for f in failed)}")
    print("=" * 70)

    if failed:
        print()
        print("FAILED OBJECTS:")
        for name, reason in failed:
            print(f"  - {name}: {reason}")

    return 1 if failed else 0


def cmd_probe():
    """Test connectivity."""
    print("Probing arc-1 CLI...")
    result = run_arc1("SAPWrite", {
        "action": "create",
        "type": "CLAS",
        "name": "ZCL_ZROUTER_PROBE",
        "description": "Connectivity probe",
        "devClass": "$TMP",
    }, timeout=30)
    if result["ok"]:
        print("OK: arc-1 CLI working, class created in $TMP")
    else:
        print(f"FAIL: {result['output'][:300]}")
        print(f"STDERR: {result['error'][:300]}")
    return 0 if result["ok"] else 1


def cmd_cleanup_test():
    """Remove test PoC objects."""
    for name in ["ZCL_ZROUTER_POC", "ZIF_ZROUTER_POC", "ZCL_ZROUTER_PROBE"]:
        print(f"Deleting {name}...")
        result = run_arc1("SAPWrite", {
            "action": "delete",
            "type": "CLAS" if name.startswith("ZCL_") else "INTF",
            "name": name,
        }, timeout=30)
        print(f"  {result['output'][:200]}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python zrouter_deploy.py [deploy|probe|cleanup]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "deploy":
        sys.exit(deploy())
    elif cmd == "probe":
        sys.exit(cmd_probe())
    elif cmd == "cleanup":
        cmd_cleanup_test()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
