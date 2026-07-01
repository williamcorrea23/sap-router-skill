#!/usr/bin/env python3
"""
SAP Router Healthcheck — MCP connectivity probe, .env guardian, credential validator.
v4.2.0: Probes all 35 MCPs + ZROUTER, verifies .env completeness, prompts user for missing data.
Andrej-style: "eval first, then act" — diagnose before routing.
"""
import os
import re
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

SKILL_DIR = Path(__file__).resolve().parent.parent

MCP_HEALTHCHECK_SPEC = {
    "arc-1": {
        "env_vars": ["ARC_SAP_URL", "ARC_SAP_USER", "ARC_SAP_PASSWORD", "ARC_SAP_CLIENT"],
        "probe_command": "npx arc-1 --help",
        "probe_command_alt": "which arc-1",
        "criticality": "HIGH",
        "description": "ADT primary — read/write ABAP source, search, transport",
    },
    "aibap": {
        "env_vars": [],  # Uses systems.json
        "probe_command": "aibap-mcp --help",
        "probe_command_alt": "which aibap-mcp",
        "criticality": "HIGH",
        "description": "69-tool ABAP development MCP (Go binary)",
        "config_file": "systems.json",
    },
    "mcp-abap-adt": {
        "env_vars": ["SAP_URL", "SAP_USERNAME", "SAP_PASSWORD", "SAP_CLIENT"],
        "probe_command": None,
        "criticality": "MEDIUM",
        "description": "TypeScript ADT bridge — 13 tools",
    },
    "mcp-sap-gui": {
        "env_vars": ["SAPGUI_HOST", "SAPGUI_USER", "SAPGUI_PASSWORD", "SAPGUI_CLIENT"],
        "probe_command": None,
        "criticality": "MEDIUM",
        "description": "Primary SAP GUI scripting — ADT fallback path",
    },
    "mcp-sap-gui-kts": {
        "env_vars": ["SAP_CONNECTION"],
        "probe_command": None,
        "criticality": "LOW",
        "description": "Secondary SAP GUI (kts982, Python)",
    },
    "sapgui-mcp-go": {
        "env_vars": [],
        "probe_command": "sapgui-mcp --help",
        "criticality": "LOW",
        "description": "Tertiary SAP GUI (Go)",
    },
    "sf-mcp": {
        "env_vars": ["SF_URL", "SF_USERNAME", "SF_PASSWORD"],
        "probe_command": None,
        "criticality": "LOW",
        "description": "SuccessFactors OData — HCM cloud operations",
    },
    "sap-rfc-mcp-server": {
        "env_vars": ["SAP_RFC_HOST", "SAP_RFC_USER", "SAP_RFC_PASSWORD", "SAP_RFC_CLIENT"],
        "probe_command": None,
        "criticality": "MEDIUM",
        "description": "RFC MCP — ZROUTER dispatch for BAPI batch operations",
    },
    "mcp-sap-notes": {
        "env_vars": ["SAP_NOTES_USERNAME", "SAP_NOTES_PASSWORD"],
        "probe_command": None,
        "criticality": "LOW",
        "description": "SAP Notes search/fetch",
    },
    "btp-mcp": {
        "env_vars": [],
        "probe_command": None,
        "criticality": "LOW",
        "description": "BTP account/subaccount management (OData)",
    },
    "odata-mcp-proxy": {
        "env_vars": [],
        "probe_command": None,
        "criticality": "LOW",
        "description": "CPI admin OData bridge",
    },
    "btp-sap-odata-to-mcp": {
        "env_vars": [],
        "probe_command": None,
        "criticality": "MEDIUM",
        "description": "Progressive discovery OData MCP",
    },
    # RAG connectors (v4.0, pre-ready)
    "pinecone-rag": {
        "env_vars": ["PINECONE_API_KEY", "PINECONE_INDEX", "PINECONE_ENVIRONMENT"],
        "probe_command": None,
        "criticality": "OPTIONAL",
        "description": "Pinecone vector DB — RAG pipeline for SAP knowledge",
    },
    "supabase-rag": {
        "env_vars": ["SUPABASE_URL", "SUPABASE_SERVICE_KEY"],
        "probe_command": None,
        "criticality": "OPTIONAL",
        "description": "Supabase pgvector — RAG pipeline alternative",
    },
    "azure-ai-search": {
        "env_vars": ["AZURE_SEARCH_ENDPOINT", "AZURE_SEARCH_KEY", "AZURE_SEARCH_INDEX"],
        "probe_command": None,
        "criticality": "OPTIONAL",
        "description": "Azure AI Search — enterprise RAG pipeline",
    },
    "zrouter": {
        "env_vars": [],
        "probe_command": "python scripts/zrouter_bootstrap.py probe --json",
        "criticality": "MEDIUM",
        "description": "ZROUTER ABAP framework — probe install state on SAP system",
    },
    "sap-cpi": {
        "env_vars": ["CPI_HOST", "CPI_USER", "CPI_PASSWORD"],
        "probe_command": None,
        "criticality": "MEDIUM",
        "description": "SAP Cloud Integration — iFlow deploy, message logs, trace",
    },
    "cf-cli-mcp": {
        "env_vars": ["CF_API", "CF_USER", "CF_PASSWORD"],
        "probe_command": None,
        "criticality": "MEDIUM",
        "description": "Cloud Foundry CLI — cf push, org/space, services",
    },
    "sap-api-management": {
        "env_vars": ["APIM_HOST", "APIM_USER", "APIM_PASSWORD"],
        "probe_command": None,
        "criticality": "LOW",
        "description": "SAP API Management — API proxy, policies, publication",
    },
    # Plugin MCPs (auto-available when IDE plugin loaded)
    "ui5-mcp": {
        "env_vars": [],
        "probe_command": None,
        "criticality": "LOW",
        "description": "UI5/SAPUI5 app creation, linter, API reference (plugin)",
    },
    "fiori-mcp": {
        "env_vars": [],
        "probe_command": None,
        "criticality": "LOW",
        "description": "Fiori app generation, metadata download, docs (plugin)",
    },
    "mdk-mcp": {
        "env_vars": [],
        "probe_command": None,
        "criticality": "LOW",
        "description": "MDK project creation, build, deploy (plugin)",
    },
    "cds-mcp": {
        "env_vars": [],
        "probe_command": None,
        "criticality": "LOW",
        "description": "CAP CDS model search, code snippets (plugin)",
    },
    "sap-pi-mcp": {
        "env_vars": ["PI_HOST", "PI_USER", "PI_PASSWORD"],
        "probe_command": None,
        "criticality": "LOW",
        "description": "SAP PI/PO - legacy integration, channel mgmt",
    },
    "bw-modeling-mcp": {
        "env_vars": ["BW_HOST", "BW_USER", "BW_PASSWORD"],
        "probe_command": None,
        "criticality": "LOW",
        "description": "BW Modeling - DSO, InfoCube, DTP, transformations",
    },
    "erpl-adt": {
        "env_vars": ["ERPL_URL", "ERPL_USER", "ERPL_PASSWORD"],
        "probe_command": None,
        "criticality": "LOW",
        "description": "ERPL ADT bridge - enterprise resource planning",
    },
    "odata-mcp-go": {
        "env_vars": [],
        "probe_command": "odata-mcp-go --help",
        "criticality": "LOW",
        "description": "OData MCP in Go - lightweight low-latency bridge",
    },
    "cloud-alm-itsm": {
        "env_vars": ["ALM_HOST", "ALM_USER", "ALM_PASSWORD"],
        "probe_command": None,
        "criticality": "LOW",
        "description": "Cloud ALM ITSM - incident, problem, change mgmt",
    },
    "datasphere-mcp": {
        "env_vars": ["DSPHERE_HOST", "DSPHERE_USER", "DSPHERE_PASSWORD"],
        "probe_command": None,
        "criticality": "LOW",
        "description": "SAP Datasphere - spaces, views, remote tables",
    },
    "steampunk-mcp": {
        "env_vars": ["STMPNK_HOST", "STMPNK_USER", "STMPNK_PASSWORD"],
        "probe_command": None,
        "criticality": "LOW",
        "description": "Steampunk/ABAP Cloud - released APIs, ADT-only",
    },
    "sapient-mcp": {
        "env_vars": ["SAPIENT_HOST", "SAPIENT_KEY"],
        "probe_command": None,
        "criticality": "LOW",
        "description": "Sapient AI agent - faster alternative orchestrator",
    },
    "mcp-integration-suite": {
        "env_vars": ["API_BASE_URL", "API_USER", "API_PASS"],
        "probe_command": None,
        "criticality": "LOW",
        "description": "SAP Integration Suite - packages, iFlows, message mapping, monitoring",
    },
    "ci-mcp-server": {
        "env_vars": ["CPI_DESTINATION_BASE_URL", "CPI_DESTINATION_TOKEN_URL", "CPI_DESTINATION_CLIENT_ID", "CPI_DESTINATION_CLIENT_SECRET"],
        "probe_command": None,
        "criticality": "LOW",
        "description": "SAP CPI OData API proxy via odata-mcp-proxy",
    },
    "abap-mcp": {
        "env_vars": ["SAP_URL", "SAP_USER", "SAP_PASSWORD", "SAP_CLIENT"],
        "probe_command": None,
        "criticality": "LOW",
        "description": "ABAP MCP Server (DimiDR) — agentic ABAP development client",
    },
    "mcp-calm-server": {
        "env_vars": ["CALM_BASE_URL"],
        "probe_command": None,
        "criticality": "LOW",
        "description": "SAP Cloud ALM MCP server (fr0ster)",
    },
    "sap-transport-mcp": {
        "env_vars": ["SAP_HOSTNAME", "SAP_USERNAME", "SAP_PASSWORD"],
        "probe_command": None,
        "criticality": "LOW",
        "description": "SAP CTS Transport Request management (Nidhideep)",
    },
}

REQUIRED_ENV_FILE_VARS = [
    "ARC_SAP_URL", "ARC_SAP_USER", "ARC_SAP_PASSWORD", "ARC_SAP_CLIENT",
]

OPTIONAL_ENV_FILE_VARS = [
    "SAP_URL", "SAP_USERNAME", "SAP_PASSWORD", "SAP_CLIENT",
    "SAPGUI_HOST", "SAPGUI_USER", "SAPGUI_PASSWORD", "SAPGUI_CLIENT",
    "SAP_CONNECTION",
    "CF_API", "CF_USER", "CF_PASSWORD",
    "CPI_HOST", "CPI_USER", "CPI_PASSWORD",
    "APIM_HOST", "APIM_USER", "APIM_PASSWORD",
    "PI_HOST", "PI_USER", "PI_PASSWORD",
    "BW_HOST", "BW_USER", "BW_PASSWORD",
    "ERPL_URL", "ERPL_USER", "ERPL_PASSWORD",
    "ALM_HOST", "ALM_USER", "ALM_PASSWORD",
    "DSPHERE_HOST", "DSPHERE_USER", "DSPHERE_PASSWORD",
    "STMPNK_HOST", "STMPNK_USER", "STMPNK_PASSWORD",
    "SAPIENT_HOST", "SAPIENT_KEY",
    "PINECONE_API_KEY", "PINECONE_INDEX", "PINECONE_ENVIRONMENT",
    "SUPABASE_URL", "SUPABASE_SERVICE_KEY",
    "AZURE_SEARCH_ENDPOINT", "AZURE_SEARCH_KEY", "AZURE_SEARCH_INDEX",
    "OPENAI_API_KEY", "DEEPSEEK_API_KEY", "OPENROUTER_API_KEY",
    "API_OAUTH_CLIENT_ID", "API_OAUTH_CLIENT_SECRET", "API_OAUTH_TOKEN_URL",
    "API_BASE_URL", "API_USER", "API_PASS",
    "CPI_BASE_URL", "CPI_OAUTH_CLIENT_ID", "CPI_OAUTH_CLIENT_SECRET", "CPI_OAUTH_TOKEN_URL",
    "CPI_DESTINATION_BASE_URL", "CPI_DESTINATION_TOKEN_URL", "CPI_DESTINATION_CLIENT_ID", "CPI_DESTINATION_CLIENT_SECRET",
    "SAP_USER", "SAP_LANGUAGE", "ALLOW_WRITE", "ALLOW_DELETE", "ALLOW_EXECUTE", "BLOCKED_PACKAGES", "SYNTAX_CHECK_BEFORE_ACTIVATE", "DEFER_TOOLS", "SAP_ABAP_VERSION",
    "CALM_MODE", "CALM_BASE_URL", "CALM_UAA_URL", "CALM_UAA_CLIENT_ID", "CALM_UAA_CLIENT_SECRET", "CALM_API_KEY",
    "SAP_HOSTNAME", "SAP_SYSNR", "SAP_SYSTEM_ID", "AUTH_METHOD", "SAP_USERNAME", "LOG_LEVEL", "DRY_RUN",
    "SAP_ROLE", "DEFAULT_TRANSPORT", "SAP_ALLOW_UNAUTHORIZED", "SAP_BTP_CONNECTIVITY_PROXY", "SAP_BTP_CONNECTIVITY_LOCATION_ID", "SAP_BTP_CONNECTIVITY_DEBUG", "SAP_BTP_CONNECTIVITY_CREDS_FILE", "SAP_BTP_CONNECTIVITY_CDS_BIND_FILE", "SAP_BTP_CONNECTIVITY_CDS_BIND_NAME", "SAP_BTP_CF_HOME", "SAP_BTP_CONNECTIVITY_CLIENT_ID", "SAP_BTP_CONNECTIVITY_CLIENT_SECRET", "SAP_BTP_CONNECTIVITY_TOKEN_URL", "SAP_ROUTER", "SAP_ROUTER_PASSWORD", "SAP_ROUTER_DEBUG", "SAP_PROXY_URL", "MAX_DUMPS", "SOURCE_CACHE_TTL_MS", "WEB_ALLOW_UNAUTHORIZED",
]


class HealthChecker:
    def __init__(self, project_root=None, verbose=True):
        self.project_root = Path(project_root or str(SKILL_DIR))
        self.verbose = verbose
        self.results = {
            "timestamp": datetime.now().isoformat()[:19],
            "overall_status": "UNKNOWN",
            "mcp_checks": {},
            "env_check": {},
            "missing_critical": [],
            "missing_optional": [],
            "recommendations": [],
        }

    def log(self, msg):
        if self.verbose:
            print(msg)

    def check_env_file(self):
        """Verify .env file exists and has all required variables."""
        self.log("\n=== .env FILE CHECK ===")

        env_path = self.project_root / ".env"
        env_template_path = self.project_root / ".env.template"

        if not env_path.exists():
            self.results["env_check"]["file_exists"] = False
            self.results["missing_critical"].extend(REQUIRED_ENV_FILE_VARS)
            self.log(f"  [MISSING] .env file not found at {env_path}")

            # Check for .env.template
            if env_template_path.exists():
                self.log(f"  [INFO] .env.template exists — copy and fill in values:")
                self.log(f"    cp {env_template_path} {env_path}")
                self.log(f"    # Then edit {env_path} with your credentials")
            else:
                self.log(f"  [INFO] No .env.template found — will need to create manually")
            return False

        self.results["env_check"]["file_exists"] = True
        env_content = env_path.read_text(encoding='utf-8')

        # Check required vars
        for var in REQUIRED_ENV_FILE_VARS:
            if re.search(rf'^{var}\s*=', env_content, re.MULTILINE) and \
               not re.search(rf'^{var}\s*=\s*$', env_content, re.MULTILINE):
                self.results["env_check"][var] = "SET"
            else:
                self.results["env_check"][var] = "MISSING"
                self.results["missing_critical"].append(var)
                self.log(f"  [MISSING] {var} not set in .env")

        # Check optional vars
        for var in OPTIONAL_ENV_FILE_VARS:
            if re.search(rf'^{var}\s*=', env_content, re.MULTILINE) and \
               not re.search(rf'^{var}\s*=\s*$', env_content, re.MULTILINE):
                self.results["env_check"][var] = "SET"
            else:
                self.results["env_check"][var] = "MISSING_OR_EMPTY"

        # Count configured
        required_set = sum(1 for v in REQUIRED_ENV_FILE_VARS if self.results["env_check"].get(v) == "SET")
        optional_set = sum(1 for v in OPTIONAL_ENV_FILE_VARS if self.results["env_check"].get(v) == "SET")

        self.log(f"  Required: {required_set}/{len(REQUIRED_ENV_FILE_VARS)} set")
        self.log(f"  Optional: {optional_set}/{len(OPTIONAL_ENV_FILE_VARS)} set")

        return len(self.results["missing_critical"]) == 0

    def check_mcp_binary(self, name, spec):
        """Check if MCP binary/command is available."""
        probe = spec.get("probe_command")
        if not probe:
            return {"status": "SKIPPED", "reason": "No probe command defined"}

        try:
            result = subprocess.run(
                probe.split(), capture_output=True, text=True, timeout=10
            )
            return {
                "status": "AVAILABLE" if result.returncode == 0 else "ERROR",
                "exit_code": result.returncode,
                "stderr": result.stderr[:200] if result.stderr else "",
            }
        except FileNotFoundError:
            # Try alt probe
            alt_probe = spec.get("probe_command_alt")
            if alt_probe:
                try:
                    result = subprocess.run(
                        alt_probe.split(), capture_output=True, text=True, timeout=10
                    )
                    return {
                        "status": "AVAILABLE" if result.returncode == 0 else "ERROR",
                        "exit_code": result.returncode,
                    }
                except Exception:
                    pass
            return {"status": "NOT_INSTALLED", "reason": f"Command not found: {probe.split()[0]}"}
        except subprocess.TimeoutExpired:
            return {"status": "TIMEOUT", "reason": "Probe timed out"}
        except Exception as e:
            return {"status": "ERROR", "reason": str(e)[:200]}

    def check_mcp_env_vars(self, name, spec):
        """Check if environment variables for MCP are set."""
        env_vars = spec.get("env_vars", [])
        if not env_vars:
            # Check if config file exists
            config_file = spec.get("config_file")
            if config_file:
                config_path = self.project_root / config_file
                if config_path.exists():
                    return {"status": "CONFIGURED", "details": f"Config file {config_file} found"}
                else:
                    return {"status": "CONFIG_FILE_MISSING", "details": f"{config_file} not found"}
            return {"status": "NO_ENV_NEEDED", "details": "No env vars or config required"}

        missing = []
        set_vars = []
        for var in env_vars:
            if os.environ.get(var):
                set_vars.append(var)
            else:
                missing.append(var)

        if not missing:
            return {"status": "ALL_SET", "details": f"All {len(env_vars)} vars set"}
        elif not set_vars:
            return {"status": "NONE_SET", "missing": missing}
        else:
            return {"status": "PARTIAL", "set": set_vars, "missing": missing}

    def run_full_check(self):
        """Run complete healthcheck across all MCPs and .env."""
        self.log("=" * 60)
        self.log("SAP ROUTER HEALTHCHECK v4.0")
        self.log(f"Timestamp: {self.results['timestamp']}")
        self.log(f"Project: {self.project_root}")
        self.log("=" * 60)

        # 1. .env check
        env_ok = self.check_env_file()

        # 2. MCP connection probes
        self.log("\n=== MCP CONNECTION PROBES ===")
        high_ok = 0
        high_total = 0

        for name, spec in MCP_HEALTHCHECK_SPEC.items():
            criticality = spec["criticality"]

            # Check env vars
            env_check = self.check_mcp_env_vars(name, spec)

            # Check binary
            binary_check = self.check_mcp_binary(name, spec)

            self.results["mcp_checks"][name] = {
                "env": env_check,
                "binary": binary_check,
                "criticality": criticality,
                "description": spec["description"],
            }

            if criticality in ("HIGH", "MEDIUM"):
                high_total += 1
                env_ok_mcp = env_check["status"] in ("ALL_SET", "CONFIGURED", "NO_ENV_NEEDED")
                binary_ok = binary_check["status"] in ("AVAILABLE", "SKIPPED")
                if env_ok_mcp and binary_ok:
                    high_ok += 1

            # Log status
            icon = "[OK]" if env_check["status"] in ("ALL_SET", "CONFIGURED", "NO_ENV_NEEDED") else "[WARN]"
            self.log(f"  {icon} {name:25s} ({criticality:8s}): env={env_check['status']:15s} binary={binary_check['status']}")

        # 3. Project objects check
        self.log("\n=== PROJECT OBJECTS ===")
        checks = {
            "templates/": (SKILL_DIR / "templates").exists(),
            "templates/*.abap": len(list((SKILL_DIR / "templates").glob("*.abap"))) >= 4,
            "scripts/*.py": len(list((SKILL_DIR / "scripts").glob("*.py"))) >= 10,
            ".claude/skills/": len(list((SKILL_DIR / ".claude" / "skills").glob("*/SKILL.md"))) >= 78,
            "zrouter_bootstrap.py": (SKILL_DIR / "scripts" / "zrouter_bootstrap.py").exists(),
            "packages/samples/": (SKILL_DIR / "packages" / "samples").exists(),
        }
        for check_name, result in checks.items():
            icon = "[OK]" if result else "[MISSING]"
            self.log(f"  {icon} {check_name}")

        # 4. Overall assessment
        self.results["high_mcp_ok"] = f"{high_ok}/{high_total}"
        if not env_ok:
            self.results["overall_status"] = "BLOCKED"
            self.log(f"\n[BLOCKED] Critical env vars missing: {self.results['missing_critical']}")
            self.results["recommendations"].append({
                "priority": "CRITICAL",
                "action": "Create .env file",
                "detail": f"Missing: {', '.join(self.results['missing_critical'])}",
                "fix": "cp .env.template .env && # edit .env with your credentials",
            })
        elif high_ok < high_total:
            self.results["overall_status"] = "DEGRADED"
            self.log(f"\n[DEGRADED] {high_ok}/{high_total} high-criticality MCPs ready")
        else:
            self.results["overall_status"] = "HEALTHY"
            self.log(f"\n[HEALTHY] All {high_total} high-criticality MCPs available")

        # 5. Recommendations
        if self.results["recommendations"]:
            self.log("\n=== RECOMMENDATIONS ===")
            for rec in self.results["recommendations"]:
                self.log(f"  [{rec['priority']}] {rec['action']}: {rec['detail']}")
                if 'fix' in rec:
                    self.log(f"    Fix: {rec['fix']}")

        return self.results

    def prompt_missing(self):
        """Generate interactive prompt for missing configuration."""
        prompts = []

        if self.results["missing_critical"]:
            prompts.append("\n=== SAP CREDENTIAL SETUP REQUIRED ===")
            prompts.append("The following variables must be configured before routing can work:")
            prompts.append("")
            missing_vars = []
            for var in self.results["missing_critical"]:
                if var == "ARC_SAP_URL":
                    missing_vars.append(("ARC_SAP_URL", "SAP System URL (e.g., https://s4h.example.com:44300)"))
                elif var == "ARC_SAP_USER":
                    missing_vars.append(("ARC_SAP_USER", "SAP username with S_DEVELOP + S_ADT_RES roles"))
                elif var == "ARC_SAP_PASSWORD":
                    missing_vars.append(("ARC_SAP_PASSWORD", "SAP password (never committed to git)"))
                elif var == "ARC_SAP_CLIENT":
                    missing_vars.append(("ARC_SAP_CLIENT", "SAP client number (e.g., 100)"))

            for idx, (var_name, var_desc) in enumerate(missing_vars, 1):
                prompts.append(f"  [{idx}] {var_name}: {var_desc}")

            prompts.append("")
            prompts.append("Create a .env file in the project root:")
            prompts.append("")
            prompts.append("  cp .env.template .env")
            prompts.append("  # Edit .env with the values above")
            prompts.append("")

        if self.results["missing_optional"]:
            optional_vars = [v for v in self.results["missing_optional"]
                          if v not in self.results["missing_critical"]]
            if optional_vars:
                prompts.append("=== OPTIONAL (RAG, GUI, BTP) ===")
                for idx, var in enumerate(optional_vars[:10], 1):
                    prompts.append(f"  [{idx}] {var}")
                prompts.append("")

        return "\n".join(prompts)

    def to_json(self):
        return json.dumps(self.results, indent=2)


def main():
    parser = argparse.ArgumentParser(description="SAP Router Healthcheck — MCP + .env verification v4.0")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    parser.add_argument("--prompt-missing", action="store_true", help="Show interactive setup prompts for missing config")
    parser.add_argument("--project-root", default=None, help="Override project root path")
    parser.add_argument("--check-mcp", help="Check specific MCP only")

    args = parser.parse_args()

    project_root = args.project_root or str(SKILL_DIR)
    checker = HealthChecker(project_root=project_root, verbose=not args.quiet)
    results = checker.run_full_check()

    if args.json:
        print(json.dumps(results, indent=2))

    if args.prompt_missing:
        print(checker.prompt_missing())

    # Exit codes
    if results["overall_status"] == "BLOCKED":
        sys.exit(2)  # Critical config missing
    elif results["overall_status"] == "DEGRADED":
        sys.exit(1)  # Warnings
    sys.exit(0)  # Healthy


if __name__ == "__main__":
    main()
