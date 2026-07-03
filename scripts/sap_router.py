#!/usr/bin/env python3
"""
SAP Router v4.2.0 - intelligent routing engine with ADT-first, GUI-fallback strategy.
+parallel subagent dispatch +ZROUTER opt-in (asked, never the engine)
+functional-context BAPI gate +caveman delegation +pipeline orchestration.

Routing law (v4.2):
  1. ADT-first for dev/read ops; SAP GUI scripting (mcp-sap-gui) is the universal fallback.
  2. ZROUTER is an OPTIONAL RFC accelerator. It is never auto-installed or
     auto-probed. The user is asked ('zrouter offer'); a decline is persisted
     and routing never references ZROUTER again. It is used only when the user
     opted in ('zrouter accept') AND the caller passes --use-zrouter.
  3. BAPIs / write transactions fire ONLY inside an explicit functional-action
     context (--functional). A bare action token never auto-fires a BAPI.
"""
import os
import re
import sys
import json
import argparse
import subprocess
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

__version__ = "5.0.0"

# === ZROUTER LIVE STATE (probe cache, used by bootstrap/fallback engine) ===
# Cached probe result. None=not checked, True=installed, False=missing
_zrouter_state = None

def set_zrouter_state(installed):
    """Called by zrouter_bootstrap after probe to cache ZROUTER state."""
    global _zrouter_state
    _zrouter_state = installed

def get_zrouter_state():
    """Return cached ZROUTER state. None = not checked yet."""
    return _zrouter_state

# === ZROUTER OPT-IN (improvement, NOT the engine) ===
# Persisted user decision so a decline survives across runs. ZROUTER is an
# optional accelerator: the orchestrator asks before installing it, and if the
# user says no, routing keeps working ADT-first -> SAP GUI scripting with no
# ZROUTER dependency at all. Location overridable via env for hermetic tests.
def _optin_path():
    env = os.environ.get("SAP_ROUTER_OPTIN_FILE")
    if env:
        return env
    return os.path.abspath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "zrouter_optin.json"))

def read_zrouter_optin():
    """Return persisted opt-in: 'unasked' | 'declined' | 'accepted' | 'installed'."""
    try:
        with open(_optin_path(), encoding="utf-8") as f:
            return json.load(f).get("state", "unasked")
    except (OSError, ValueError):
        return "unasked"

def write_zrouter_optin(state):
    """Persist opt-in decision. state in {unasked,declined,accepted,installed}."""
    try:
        with open(_optin_path(), "w", encoding="utf-8") as f:
            json.dump({"state": state}, f)
        return True
    except OSError:
        return False

def zrouter_enabled():
    """ZROUTER usable only when the user explicitly opted in. Default: False."""
    return read_zrouter_optin() in ("accepted", "installed")

# === ROUTING CONFIGURATION ===

ADT_ACTIONS = ["read_source", "search_object", "syntax_check", "where_used", "get_deps", "code_search"]

# Functional WRITE verbs. Routing only dispatches a BAPI / write transaction for
# these when an explicit functional-action context is present (--functional).
# A bare token (e.g. a smoke-test action) returns 'needs-functional-context' so
# no BAPI is ever auto-fired out of context.
FUNCTIONAL_WRITE_KEYWORDS = [
    "CREATE", "CHANGE", "POST", "MOVEMENT", "RECEIPT", "DELIVERY", "BILLING",
    "INVOICE", "CONFIRM", "RELEASE", "REVERSE", "SAVE", "UPDATE", "CANCEL",
]
# Pure read/lookup verbs never gate (they do not fire a write BAPI).
FUNCTIONAL_READ_KEYWORDS = ["READ", "DISPLAY", "OVERVIEW", "CHECK", "GET", "LIST", "SEARCH"]

# Functional action -> BAPI (used only with --functional). Keep small + explicit.
FUNCTIONAL_BAPI_MAP = {
    "CREATE_MATERIAL":       "BAPI_MATERIAL_SAVEDATA",
    "CHANGE_MATERIAL":       "BAPI_MATERIAL_SAVEDATA",
    "CREATE_PO":             "BAPI_PO_CREATE1",
    "CHANGE_PO":             "BAPI_PO_CHANGE",
    "GOODS_MOVEMENT":        "BAPI_GOODSMVT_CREATE",
    "GOODS_RECEIPT":         "BAPI_GOODSMVT_CREATE",
    "CREATE_DELIVERY":       "BAPI_OUTB_DELIVERY_CREATE_SLS",
    "CREATE_INVOICE":        "BAPI_BILLINGDOC_CREATEMULTIPLE",
    "CREATE_SALES_ORDER":    "BAPI_SALESORDER_CREATEFROMDAT2",
    "CHANGE_SALES_ORDER":    "BAPI_SALESORDER_CHANGE",
    "POST_DOCUMENT":         "BAPI_ACC_DOCUMENT_POST",
    "REVERSE_DOCUMENT":      "BAPI_ACC_DOCUMENT_REV_POST",
    "CREATE_INSPECTION":     "BAPI_INSPLOT_CREATE",
    "CREATE_RN":             "ZFM_QM_CREATE_RN",
    "CREATE_INTERNAL_ORDER": "BAPI_INTERNALORDER_CREATE",
    "CREATE_PROD_ORDER":     "BAPI_PRODORD_CREATE",
}

# SAP GUI fallback map: action → transaction code for ADT-unavailable operations
GUI_FALLBACK_MAP = {
    'SPRO_CONFIG':          {'tcode': 'SPRO',   'description': 'IMG Customizing'},
    'TABLE_MAINTENANCE':    {'tcode': 'SM30',   'description': 'Table View Maintenance'},
    'USER_MAINTENANCE':     {'tcode': 'SU01',   'description': 'User Maintenance'},
    'AUTH_CHECK':           {'tcode': 'SU53',   'description': 'Authorization Check'},
    'ROLE_EDITOR':          {'tcode': 'PFCG',   'description': 'Role Maintenance'},
    'NOTE_APPLY':           {'tcode': 'SNOTE',  'description': 'SAP Note Application'},
    'MATERIAL_GUI':         {'tcode': 'MM01',   'description': 'Create Material (GUI)'},
    'MATERIAL_CHANGE_GUI':  {'tcode': 'MM02',   'description': 'Change Material (GUI)'},
    'PO_CREATE_GUI':        {'tcode': 'ME21N',  'description': 'Create Purchase Order'},
    'GOODS_RECEIPT':        {'tcode': 'MIGO',   'description': 'Goods Movement'},
    'STOCK_OVERVIEW':       {'tcode': 'MMBE',   'description': 'Stock Overview'},
    'ORDER_CREATE_GUI':     {'tcode': 'VA01',   'description': 'Create Sales Order'},
    'ORDER_CHANGE_GUI':     {'tcode': 'VA02',   'description': 'Change Sales Order'},
    'DELIVERY_CREATE_GUI':  {'tcode': 'VL01N',  'description': 'Create Delivery'},
    'BILLING_CREATE_GUI':   {'tcode': 'VF01',   'description': 'Create Billing Document'},
    'FI_POST_GUI':          {'tcode': 'FB01',   'description': 'Post Document (GUI)'},
    'GL_MASTER_GUI':        {'tcode': 'FS00',   'description': 'GL Account Master'},
    'INSPECTION_CREATE_GUI':{'tcode': 'QA01',   'description': 'Create Inspection Lot'},
    'PROD_ORDER_CREATE_GUI':{'tcode': 'CO01',   'description': 'Create Production Order'},
    'INTERNAL_ORDER_GUI':   {'tcode': 'KO01',   'description': 'Create Internal Order'},
    'EMPLOYEE_DISPLAY_GUI': {'tcode': 'PA20',   'description': 'Display HR Master Data'},
    'SE16_DATA':            {'tcode': 'SE16',   'description': 'Data Browser'},
    'SE80_NAVIGATE':        {'tcode': 'SE80',   'description': 'Object Navigator'},
    'SA38_EXECUTE':         {'tcode': 'SA38',   'description': 'Program Execution'},
    'ST22_SCAN_GUI':        {'tcode': 'ST22',   'description': 'Dump Analysis'},
    'SM37_JOB_MONITOR':     {'tcode': 'SM37',   'description': 'Job Monitor'},
    'SM50_PROCESS_LIST':    {'tcode': 'SM50',   'description': 'Process Overview'},
}

# Caveman sub-agent delegation rules
CAVEMAN_DELEGATION = {
    'investigator': {
        'trigger_keywords': ['find', 'search', 'locate', 'where is', 'look up', 'grep', 'scan for'],
        'description': 'Read-only code location — maps definitions, callers, directory structure',
        'agent_type': 'caveman:cavecrew-investigator',
    },
    'builder': {
        'trigger_keywords': ['fix', 'edit', 'change', 'rename', 'remove', 'add method', 'add field',
                            'typo', 'single file', 'one file', 'small change'],
        'description': 'Surgical 1-2 file edit — typos, single-function rewrites, mechanical renames',
        'agent_type': 'caveman:cavecrew-builder',
        'refuses': ['3+ files', 'new features', 'cross-file refactors'],
    },
    'reviewer': {
        'trigger_keywords': ['review', 'audit', 'check diff', 'review this', 'code review diff',
                            'PR review', 'merge request'],
        'description': 'Diff/branch reviewer — one finding per line, severity-tagged',
        'agent_type': 'caveman:cavecrew-reviewer',
    },
}

# Pipeline stage definitions.
# 'wave' groups stages for PARALLEL dispatch: stages sharing a wave can run
# concurrently (same-wave agents are launched in ONE batch by the orchestrator).
# 'fan_out: per-object' => one builder subagent per detected object (true parallelism).
PIPELINE_STAGES = [
    {'id': 'stage1', 'name': 'Spec Analysis',              'skill': 'sap-router-skill',      'avg_time': '10s',    'wave': 0},
    {'id': 'stage2', 'name': 'Technical Proposal',          'skill': 'sap-crew-analysis',     'avg_time': '3min',   'wave': 1},
    {'id': 'stage3', 'name': 'Peer Review 1',               'skill': 'abap-code-review',      'avg_time': '1min',   'wave': 2},
    {'id': 'stage4', 'name': 'Implementation',              'skill': 'cavecrew-builder + ADT','avg_time': 'varied', 'wave': 3, 'fan_out': 'per-object'},
    {'id': 'stage5', 'name': 'Static Analysis (abaplint)',  'tool': 'npm run abap:review',    'avg_time': '30s',    'wave': 4},
    {'id': 'stage6', 'name': 'Deep Analysis (Crew)',        'skill': 'sap-crew-analysis',     'avg_time': '5min',   'wave': 4},
    {'id': 'stage7', 'name': 'Peer Review 2',               'skill': 'abap-code-review',      'avg_time': '1min',   'wave': 5},
    {'id': 'stage8', 'name': 'Transport Gate',              'skill': 'sap-transport-gate',    'avg_time': '2min',   'wave': 6},
]
# === v5.0: CONFIG LOADER (YAML external, hardcoded fallback) ===
CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config")

def _load_yaml_config(filename, fallback):
    """Load routing map from config/*.yaml. Fallback to hardcoded on any error."""
    path = os.path.join(CONFIG_DIR, filename)
    try:
        import yaml
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return fallback

_cfg = _load_yaml_config("routing_maps.yaml", None)
if _cfg:
    ADT_ACTIONS = _cfg.get("adt_actions", ADT_ACTIONS)
    FUNCTIONAL_WRITE_KEYWORDS = _cfg.get("functional_write_keywords", FUNCTIONAL_WRITE_KEYWORDS)
    FUNCTIONAL_READ_KEYWORDS = _cfg.get("functional_read_keywords", FUNCTIONAL_READ_KEYWORDS)
    FUNCTIONAL_BAPI_MAP = _cfg.get("functional_bapi_map", FUNCTIONAL_BAPI_MAP)
    GUI_FALLBACK_MAP = _cfg.get("gui_fallback_map", GUI_FALLBACK_MAP)

_pipe_cfg = _load_yaml_config("pipeline_stages.yaml", None)
if _pipe_cfg:
    PIPELINE_STAGES = _pipe_cfg.get("pipeline_stages", PIPELINE_STAGES)


class SapRouter:
    def __init__(self, memory_file="MEMORY.md"):
        self.memory_file = os.path.abspath(memory_file)
        self.gui_fallback_enabled = True
        self.caveman_delegation_enabled = True

    def scan_agent_registry(self):
        """v5.0: Discover agents from .claude/agents/*.md YAML frontmatter.
        Returns {name: {description, tools, model, keywords}}."""
        agents = {}
        agents_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "..", ".claude", "agents")
        if not os.path.isdir(agents_dir):
            return agents
        import glob as _glob
        for path in _glob.glob(os.path.join(agents_dir, "*.md")):
            try:
                text = open(path, encoding="utf-8").read()
                if not text.startswith("---"):
                    continue
                fm_raw = text.split("---")[1]
                import yaml
                fm = yaml.safe_load(fm_raw)
                desc = str(fm.get("description", ""))
                # Trigger keywords = palavras significativas da description
                keywords = [w.strip(".,()").lower() for w in desc.split()
                            if len(w) > 4 and w.lower() not in ("specialist", "trigger")]
                agents[fm["name"]] = {
                    "description": desc,
                    "tools": fm.get("tools", []),
                    "model": fm.get("model", "sonnet"),
                    "keywords": keywords,
                    "path": path,
                }
            except Exception as e:
                continue
        return agents

    def _normalize_text(self, text):
        import unicodedata
        # Convert to string and normalize accents / strip characters
        text = str(text)
        return "".join(c for c in unicodedata.normalize('NFD', text)
                       if unicodedata.category(c) != 'Mn').lower()

    def match_agent(self, task_text):
        """v5.0: Return best-matching agent for a task, or None.
        Scoring: keyword hits in description. Threshold: >= 2 hits."""
        agents = self.scan_agent_registry()
        task_norm = self._normalize_text(task_text)
        best, best_score = None, 0
        for name, info in agents.items():
            # Normalize agent keywords
            norm_kws = [self._normalize_text(kw) for kw in info["keywords"]]
            # Split slashes/dashes
            split_kws = []
            for kw in norm_kws:
                if "/" in kw:
                    split_kws.extend(kw.split("/"))
                elif "-" in kw:
                    split_kws.extend(kw.split("-"))
                else:
                    split_kws.append(kw)
            score = sum(1 for kw in split_kws if len(kw) > 3 and kw in task_norm)
            if score > best_score:
                best, best_score = name, score
        if best_score >= 2:
            return {"agent": best, "score": best_score,
                    "model": agents[best]["model"],
                    "strategy": "agent-dispatch"}
        return None


    def get_route(self, action, try_adt=True, allow_gui_fallback=True,
                  functional_context=False, use_zrouter=False):
        # v5.0: Integrate Self-Learning Engine
        from self_learn import SelfLearnEngine
        engine = SelfLearnEngine(self.memory_file)
        try:
            engine.load_history()
        except Exception:
            pass

        route = self._get_route_inner(action, try_adt=try_adt,
                                      allow_gui_fallback=allow_gui_fallback,
                                      functional_context=functional_context,
                                      use_zrouter=use_zrouter)

        # Rerank MCP servers based on learned stats
        if "mcp_servers" in route and route["mcp_servers"]:
            best = engine.get_best_mcp(route["mcp_servers"])
            if best:
                route["mcp_server"] = best

        # v5.0: Bypass offline MCPs using healthcheck cache
        cache = self._load_healthcheck_cache()
        if cache:
            mcp_servers = route.get("mcp_servers", [])
            primary_mcp = route.get("mcp_server")
            if primary_mcp and mcp_servers:
                if not self._is_mcp_healthy_in_cache(primary_mcp, cache):
                    # Find first healthy backup MCP
                    fallback_mcp = None
                    for b_mcp in mcp_servers:
                        if b_mcp != primary_mcp and self._is_mcp_healthy_in_cache(b_mcp, cache):
                            fallback_mcp = b_mcp
                            break
                    if fallback_mcp:
                        route["mcp_server"] = fallback_mcp
                        route["health_bypass"] = True
                        route["details"] = (route.get("details", "") + 
                                            f" (Bypassed offline {primary_mcp} -> {fallback_mcp})")

        # Adapt route (adds confidence, warnings)
        try:
            route = engine.adapt_route(action, route)
        except Exception:
            pass

        # Inject learned context for prompt injection
        ctx = engine.get_context_for_prompt()
        if ctx:
            route["learned_context"] = ctx

        # v5.0 Complexity model routing
        complexity = self._assess_complexity(action)
        if complexity in ["VERY_COMPLEX", "COMPLEX"]:
            route["model"] = "sonnet"
        else:
            route["model"] = "haiku"

        return route

    def _is_mcp_healthy_in_cache(self, mcp_name, cache):
        checks = cache.get("mcp_checks", {})
        if mcp_name not in checks:
            return True # If not checked, assume healthy (fail-open)
        mcp_data = checks[mcp_name]
        env_ok = mcp_data.get("env", {}).get("status") in ("ALL_SET", "CONFIGURED", "NO_ENV_NEEDED")
        binary_ok = mcp_data.get("binary", {}).get("status") in ("AVAILABLE", "SKIPPED")
        return env_ok and binary_ok

    def _load_healthcheck_cache(self):
        """v5.0: Load healthcheck cache. Returns dict or None."""
        cache_path = os.path.join(CONFIG_DIR, "..", ".healthcheck_cache.json")
        if not os.path.exists(cache_path):
            return None
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache = json.load(f)
            ts_str = cache.get("timestamp")
            if ts_str:
                ts = datetime.fromisoformat(ts_str)
                elapsed = datetime.now() - ts
                if elapsed.total_seconds() < 900: # 15 minutes
                    return cache
        except Exception:
            pass
        return None

    def _get_route_inner(self, action, try_adt=True, allow_gui_fallback=True,
                         functional_context=False, use_zrouter=False):
        """Route action: ADT primary -> SAP GUI scripting fallback (mcp-sap-gui).

        functional_context: real functional request — required before any BAPI /
            write transaction is dispatched (Req: BAPIs fire only in context).
        use_zrouter: prefer the optional ZROUTER RFC path — honoured ONLY if the
            user already opted in ('zrouter accept'); otherwise it is ignored and
            the offer is surfaced.
        """
        action_lower = action.lower()
        action_upper = action.upper()

        # Step 0a: Cloud ALM (CALM) operations
        if any(kw in action_lower for kw in ["calm_", "alm_", "cloud_alm"]):
            return {
                "destination": "SAP Cloud ALM (CALM)",
                "mcp_server": "mcp-calm-server",
                "mcp_servers": ["mcp-calm-server", "cloud-alm-itsm"],
                "strategy": "cloud-alm",
                "details": "SAP Cloud ALM operation via mcp-calm-server"
            }

        # Step 0b: Transport / CTS operations
        if any(kw in action_lower for kw in ["transport_", "cts_", "release_request", "import_queue"]):
            return {
                "destination": "SAP CTS (Transports)",
                "mcp_server": "sap-transport-mcp",
                "mcp_servers": ["sap-transport-mcp", "abap-mcp", "arc-1", "aibap"],
                "strategy": "cts-transport",
                "details": "Change and Transport System (CTS) management via sap-transport-mcp"
            }

        # Step 0c: Advanced ABAP MCP operations
        advanced_abap_kws = ["read_abap_method", "edit_abap_method", "validate_ddic", 
                             "execute_abap_snippet", "get_abap_contract", "get_call_graph", 
                             "find_dead_code", "review_clean_abap", "abap_develop"]
        if any(kw in action_lower for kw in advanced_abap_kws):
            return {
                "destination": "ABAP MCP Server (DimiDR)",
                "mcp_server": "abap-mcp",
                "mcp_servers": ["abap-mcp", "arc-1", "aibap", "mcp-abap-adt"],
                "strategy": "abap-mcp-advanced",
                "details": "Advanced ABAP MCP operation: method surgery / DDIC validation / Clean ABAP"
            }

        # Step 1: ADT read/dev ops (primary path) — never fire a BAPI
        if try_adt:
            for adt_action in ADT_ACTIONS:
                if adt_action in action_lower:
                    return {
                        "destination": "ARC-1 (ADT)",
                        "mcp_server": "arc-1",
                        "mcp_servers": ["arc-1", "abap-mcp", "aibap", "mcp-abap-adt"],
                        "fallback": "sap-gui-scripting",
                        "strategy": "adt-primary",
                        "details": "Direct ADT operation via arc-1 SAPRead/SAPWrite/SAPSearch"
                    }

        # Step 2: SuccessFactors (HCM cloud)
        if "sf_" in action_lower:
            return {
                "destination": "sf-mcp (OData)",
                "mcp_server": "sf-mcp",
                "mcp_servers": ["sf-mcp"],
                "strategy": "hcm-cloud",
                "details": "SuccessFactors API via OData V2 endpoint"
            }

        # Step 3: Functional WRITE gate — BAPIs fire only in functional-action context
        if self._is_functional_write(action_upper):
            if not functional_context:
                return {
                    "destination": "none",
                    "strategy": "needs-functional-context",
                    "action": action_upper,
                    "details": ("Functional write action. A BAPI / write transaction is NOT "
                                "auto-fired. Re-run with --functional only when a real functional "
                                "request requires it."),
                    "hint": f"sap_router.py route --action {action_upper} --functional",
                }
            # Functional context present -> dispatch is allowed.
            # 3a. Optional ZROUTER accelerator (only if the user opted in).
            if use_zrouter:
                if zrouter_enabled():
                    z = self._route_via_zrouter(action_upper)
                    if z:
                        return z
                else:
                    route = self._route_functional_write(action_upper)
                    route["zrouter_offer"] = self._zrouter_offer(action_upper)
                    return route
            # 3b. BAPI-first when a BAPI is known, else SAP GUI write transaction.
            return self._route_functional_write(action_upper)

        # Step 3.5 (v5.0): dynamic agent registry match — SÓ para texto livre.
        # Tokens de ação (sem espaço) nunca entram aqui; preserva rotas v4.2.
        if " " in action:
            agent_match = self.match_agent(action_lower)
            if agent_match:
                return {
                    "destination": agent_match["agent"],
                    "strategy": "agent-dispatch",
                    "model": agent_match["model"],
                    "details": f"Dynamic agent registry match (score {agent_match['score']})",
                }

        # Step 4: caveman delegation (small-scope DEV edits — not SAP functional writes)
        if self.caveman_delegation_enabled:
            caveman_route = self._check_caveman_delegation(action_lower)
            if caveman_route:
                return caveman_route

        # Step 5: GUI fallback map (explicit GUI ops, reads, admin transactions)
        if allow_gui_fallback and self.gui_fallback_enabled:
            for gui_key, gui_info in GUI_FALLBACK_MAP.items():
                if gui_key in action_upper or gui_info['tcode'] in action_upper:
                    return {
                        "destination": "SAP GUI Scripting",
                        "mcp_server": "mcp-sap-gui",
                        "mcp_servers": ["mcp-sap-gui", "mcp-sap-gui-kts", "sapgui-mcp-go"],
                        "transaction": gui_info['tcode'],
                        "description": gui_info['description'],
                        "strategy": "gui-fallback",
                        "details": f"ADT cannot handle this operation. Route to SAP GUI transaction {gui_info['tcode']}: {gui_info['description']}"
                    }

        # Step 6: default fallback - ADT-first strategy.
        # Anything ADT cannot resolve drops to SAP GUI scripting (mcp-sap-gui).
        tcode = self._derive_tcode(action_upper)
        return {
            "destination": "SAP GUI Scripting",
            "mcp_server": "mcp-sap-gui",
            "mcp_servers": ["mcp-sap-gui", "mcp-sap-gui-kts", "sapgui-mcp-go"],
            "transaction": tcode,
            "strategy": "gui-fallback",
            "details": (f"ADT cannot handle '{action_upper}'. "
                        f"Execute via SAP GUI scripting (mcp-sap-gui)"
                        + (f", transaction {tcode}." if tcode else ".")),
        }

    def _is_functional_write(self, action_upper):
        """True if the action would fire a BAPI / write transaction.

        Explicit GUI requests (contain 'GUI') and pure reads are NOT gated — the
        gate exists to stop BAPI dispatch out of functional context, not to block
        navigation or lookups.
        """
        if "GUI" in action_upper:
            return False  # explicit GUI navigation = explicit functional intent
        if action_upper.startswith("BAPI_"):
            return True
        if any(rk in action_upper for rk in FUNCTIONAL_READ_KEYWORDS):
            return False
        return any(wk in action_upper for wk in FUNCTIONAL_WRITE_KEYWORDS)

    def _lookup_bapi(self, action_upper):
        """Return the BAPI mapped to a functional action, or None."""
        for key, bapi in FUNCTIONAL_BAPI_MAP.items():
            if key in action_upper:
                return bapi
        if action_upper.startswith("BAPI_"):
            return action_upper
        return None

    def _route_functional_write(self, action_upper):
        """Dispatch a functional write that HAS explicit functional context.
        BAPI-first when a BAPI is known; otherwise SAP GUI write transaction.
        The actual COMMIT belongs in the ABAP backend — this only routes."""
        bapi = self._lookup_bapi(action_upper)
        tcode = self._derive_tcode(action_upper)
        if bapi:
            return {
                "destination": "BAPI (functional dispatch)",
                "strategy": "bapi-functional",
                "bapi": bapi,
                "transaction": tcode,
                "mcp_server": "mcp-sap-gui",
                "mcp_servers": ["mcp-sap-gui", "mcp-sap-gui-kts", "sapgui-mcp-go"],
                "details": (f"Functional action {action_upper}: dispatch {bapi} "
                            f"(GUI fallback: {tcode or 'n/a'}). Commit stays in the backend."),
            }
        return {
            "destination": "SAP GUI Scripting",
            "mcp_server": "mcp-sap-gui",
            "mcp_servers": ["mcp-sap-gui", "mcp-sap-gui-kts", "sapgui-mcp-go"],
            "transaction": tcode,
            "strategy": "gui-fallback",
            "details": (f"Functional action {action_upper} via SAP GUI scripting"
                        + (f", transaction {tcode}." if tcode else ".")),
        }

    def _derive_tcode(self, action_upper):
        """Best-effort GUI transaction for an ADT-unavailable functional action."""
        derive = [
            ("CREATE_MATERIAL", "MM01"), ("CHANGE_MATERIAL", "MM02"),
            ("CREATE_PO", "ME21N"), ("GOODS", "MIGO"), ("STOCK", "MMBE"),
            ("SALES_ORDER", "VA01"), ("DELIVERY", "VL01N"), ("BILLING", "VF01"),
            ("INSPECTION", "QA01"), ("CREATE_RN", "QM01"),
            ("PROD_ORDER", "CO01"), ("INTERNAL_ORDER", "KO01"),
            ("FI_POST", "FB01"), ("GL_MASTER", "FS00"),
        ]
        for kw, tc in derive:
            if kw in action_upper:
                return tc
        return ""

    def _zrouter_offer(self, action_upper=None):
        """Build the opt-in OFFER for the optional ZROUTER RFC accelerator.

        ZROUTER is never installed without consent. The orchestrator presents
        this offer (e.g. via AskUserQuestion); the default is decline, and a
        decline is persisted so routing keeps using ADT-first -> SAP GUI scripting.
        """
        return {
            "improvement": "ZROUTER RFC accelerator (optional, not required)",
            "benefit": "One RFC dispatch for functional writes instead of GUI scripting.",
            "question": "Install the optional ZROUTER RFC accelerator?",
            "default": "decline",
            "for_action": action_upper,
            "accept_cmd": "python scripts/sap_router.py zrouter accept",
            "decline_cmd": "python scripts/sap_router.py zrouter decline",
            "note": "Declining is persisted; routing continues ADT-first -> SAP GUI scripting.",
        }

    def _route_via_zrouter(self, action_upper):
        """OPT-IN ONLY: route a functional write through the ZROUTER RFC tiered
        engine. The caller MUST verify zrouter_enabled() first. Returns None if
        the engine is unavailable so the caller can fall back to GUI scripting."""
        try:
            from scripts.fallback_engine import TieredFallback
        except ImportError:
            try:
                sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from scripts.fallback_engine import TieredFallback
            except ImportError:
                return None
        engine = TieredFallback(memory_file=self.memory_file)
        result = engine.execute(action_upper)
        if not result.get("success"):
            return None
        data = result.get("result", {})
        return {
            "destination": "ZROUTER RFC (opt-in)",
            "strategy": "zrouter-rfc",
            "tier": result.get("tier"),
            "method": data.get("method"),
            "chain": result.get("chain", []),
            "note": "ZROUTER improvement path (user opted in).",
        }

    def _check_caveman_delegation(self, action_lower):
        """Check if task can be delegated to a single caveman sub-agent."""
        if any(kw in action_lower for kw in CAVEMAN_DELEGATION['builder']['trigger_keywords']):
            return {
                "destination": "cavecrew-builder",
                "agent_type": CAVEMAN_DELEGATION['builder']['agent_type'],
                "strategy": "caveman-surgical",
                "constraints": "1-2 files only. No new features. No cross-file refactors.",
                "details": "Small-scope edit, delegate to cavecrew-builder for surgical change"
            }
        if any(kw in action_lower for kw in CAVEMAN_DELEGATION['investigator']['trigger_keywords']):
            return {
                "destination": "cavecrew-investigator",
                "agent_type": CAVEMAN_DELEGATION['investigator']['agent_type'],
                "strategy": "caveman-readonly",
                "details": "Read-only code location, delegate to cavecrew-investigator (60% token savings)"
            }
        if any(kw in action_lower for kw in CAVEMAN_DELEGATION['reviewer']['trigger_keywords']):
            return {
                "destination": "cavecrew-reviewer",
                "agent_type": CAVEMAN_DELEGATION['reviewer']['agent_type'],
                "strategy": "caveman-diff-review",
                "details": "Diff/branch review, delegate to cavecrew-reviewer"
            }
        return None

    def _plan_parallel_crew(self, task_lower):
        """Return a LIST of caveman agents that can run CONCURRENTLY for one task.

        Unlike _check_caveman_delegation (returns a single best match), this lets
        a multi-faceted task ('find X then review the diff') fan out into several
        subagents the orchestrator launches in ONE batch. Speeds up the action.
        """
        plan = []
        for role in ('investigator', 'builder', 'reviewer'):
            kws = CAVEMAN_DELEGATION[role]['trigger_keywords']
            if any(kw in task_lower for kw in kws):
                plan.append({
                    'role': role,
                    'agent_type': CAVEMAN_DELEGATION[role]['agent_type'],
                    'description': CAVEMAN_DELEGATION[role]['description'],
                })
        return plan

    def build_dispatch_plan(self, parallel=True, start_idx=0, n_objects=1):
        """Group remaining pipeline stages into waves for concurrent dispatch.

        parallel=True : stages sharing a 'wave' are launched concurrently;
                        Stage 4 fans out one builder per detected object.
        parallel=False: each stage is its own wave (strict serial), no concurrency.
        """
        stages = PIPELINE_STAGES[start_idx:]
        buckets = {}
        for seq, s in enumerate(stages):
            key = s['wave'] if parallel else seq
            buckets.setdefault(key, []).append(s)
        plan = []
        for key in sorted(buckets):
            group = []
            for s in buckets[key]:
                entry = {
                    'id': s['id'],
                    'name': s['name'],
                    'agent': s.get('skill', s.get('tool', 'manual')),
                    'avg_time': s['avg_time'],
                }
                if parallel and s.get('fan_out') == 'per-object' and n_objects > 1:
                    entry['fan_out'] = n_objects
                group.append(entry)
            concurrent = bool(parallel and (len(group) > 1 or any('fan_out' in g for g in group)))
            plan.append({'wave': key, 'concurrent': concurrent, 'stages': group})
        return plan

    def analyze_spec(self, spec_text):
        """Stage 1: Analyze specification document to identify module, entities, BAPIs."""
        analysis = {
            'modules': self._identify_modules(spec_text),
            'entities': self._extract_entities(spec_text),
            'bapis': self._identify_bapis(spec_text),
            'config_tables': self._identify_config_tables(spec_text),
            'complexity': self._assess_complexity(spec_text),
        }

        primary_module = analysis['modules'][0] if analysis['modules'] else 'BASIS'
        analysis['primary_module'] = primary_module

        # Map module to first available GUI fallback transaction
        MODULE_GUI_PREFIX = {
            'MM': 'MATERIAL', 'SD': 'ORDER', 'FI': 'FI_POST',
            'QM': 'INSPECTION', 'PP': 'PROD_ORDER', 'CO': 'INTERNAL_ORDER',
            'HCM': 'EMPLOYEE', 'BASIS': 'SE16',
        }
        gui_prefix = MODULE_GUI_PREFIX.get(primary_module, '')
        gui_fallback = None
        for key, info in GUI_FALLBACK_MAP.items():
            if gui_prefix and gui_prefix in key:
                gui_fallback = {'key': key, 'tcode': info['tcode'], 'description': info['description']}
                break

        analysis['routing'] = {
            'primary_action': f'{primary_module}_analyze',
            'fallback_gui': gui_fallback,
        }

        return analysis

    def _load_tcode_index(self):
        """v5.0: Load tcodes.yaml mapping. Returns dict of tcode -> list of modules."""
        path = os.path.join(CONFIG_DIR, "..", "references", "data", "tcodes.yaml")
        if not os.path.exists(path):
            return {}
        try:
            import yaml
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            tcodes = {}
            if data:
                for tcode, info in data.items():
                    if isinstance(info, dict) and "modules" in info:
                        tcodes[tcode.upper()] = info["modules"]
            return tcodes
        except Exception:
            return {}

    def _load_symptom_index(self):
        """v5.0: Load symptom-index.yaml mapping. Returns list of symptom dicts."""
        path = os.path.join(CONFIG_DIR, "..", "references", "data", "symptom-index.yaml")
        if not os.path.exists(path):
            return []
        try:
            import yaml
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if data and isinstance(data, dict) and "symptoms" in data:
                return data["symptoms"]
            return []
        except Exception:
            return []

    def _identify_modules(self, text):
        text_upper = text.upper()
        detected = []

        # 1. T-code matching
        # Extract potential T-codes (e.g. F110, IW31, XK03, FBZP, SE16N, ME21N)
        tcode_candidates = re.findall(r'\b[A-Z]{1,2}[0-9]{2,4}[A-Z0-9]?\b', text_upper)
        words = [w.strip(".,()[]{}'\"") for w in text_upper.split()]
        tcode_candidates.extend(words)

        tcode_index = self._load_tcode_index()
        for cand in set(tcode_candidates):
            if cand in tcode_index:
                for mod in tcode_index[cand]:
                    if mod not in detected:
                        detected.append(mod)

        # 2. Symptom matching (substring/fuzzy)
        symptoms = self._load_symptom_index()
        text_norm = self._normalize_text(text)
        for sym in symptoms:
            match_found = False
            for val in sym.values():
                if isinstance(val, str):
                    norm_val = self._normalize_text(val)
                    if norm_val and norm_val in text_norm:
                        match_found = True
                        break
                elif isinstance(val, list):
                    for item in val:
                        if isinstance(item, str):
                            norm_val = self._normalize_text(item)
                            if norm_val and norm_val in text_norm:
                                match_found = True
                                break
                    if match_found:
                        break
            
            if match_found:
                for mod in sym.get("likely_modules", []):
                    if mod not in detected:
                        detected.append(mod)
                for tc in sym.get("first_check_tcodes", []):
                    tc_upper = tc.upper()
                    if tc_upper in tcode_index:
                        for mod in tcode_index[tc_upper]:
                            if mod not in detected:
                                detected.append(mod)

        # 3. Fallback to v4.2 keyword dictionary
        module_keywords = {
            'MM': ['MATERIAL', 'PURCHASE ORDER', 'PO ', 'MIGO', 'INVENTORY', 'VENDOR',
                   'PROCUREMENT', 'GOODS RECEIPT', 'STOCK', 'MRP', 'SOURCE LIST'],
            'SD': ['SALES ORDER', 'CUSTOMER', 'DELIVERY', 'BILLING', 'PRICING',
                   'SHIPPING', 'CREDIT MEMO', 'INVOICE', 'VA01', 'VA02'],
            'FI': ['GL ACCOUNT', 'JOURNAL ENTRY', 'POSTING', 'BALANCE', 'LEDGER',
                   'ACCOUNTS PAYABLE', 'ACCOUNTS RECEIVABLE', 'ASSET', 'TAX', 'FB01',
                   'FINANCIAL', 'ACCOUNTING', 'COMPANY CODE', 'FISCAL YEAR', 'DOCUMENT POST',
                   'REVENUE', 'EXPENSE', 'DEBIT', 'CREDIT', 'ACCRUAL', 'BAPI_ACC'],
            'QM': ['INSPECTION', 'QUALITY', 'LOT', 'DEFECT', 'SPECIFICATION', 'QA01'],
            'PP': ['PRODUCTION ORDER', 'BOM', 'ROUTING', 'WORK CENTER', 'CO01'],
            'WM': ['WAREHOUSE', 'TRANSFER ORDER', 'STORAGE BIN', 'PICKING', 'LT01'],
            'CO': ['COST CENTER', 'INTERNAL ORDER', 'ALLOCATION', 'ASSESSMENT', 'KO01'],
            'HCM': ['EMPLOYEE', 'PERSONNEL', 'INFOTYPE', 'PA20', 'PA30', 'PAYROLL'],
            'BASIS': ['TRANSPORT', 'ST22', 'DEBUG', 'ACTIVATE', 'ABAP UNIT', 'CODE SEARCH'],
        }

        for module, keywords in module_keywords.items():
            if any(kw in text_upper for kw in keywords):
                if module not in detected:
                    detected.append(module)

        return detected

    def _extract_entities(self, text):
        entities = []
        entity_patterns = [
            (r'(?:table|structure)\s+(\w{2,30})', 'table'),
            (r'(?:class|CLAS)\s+(ZCL_\w{1,30})', 'class'),
            (r'(?:function module|FM|FUNC)\s+(Z?\w{1,30})', 'function'),
            (r'(?:program|report|PROG)\s+(Z\w{1,30})', 'program'),
            (r'(?:BAdI|enhancement)\s+(\w{2,30})', 'badi'),
            (r'(?:CDS view|DDLS)\s+(Z\w{1,30})', 'cds_view'),
        ]
        for pattern, etype in entity_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append({'name': match.group(1), 'type': etype})
        return entities

    def _identify_bapis(self, text):
        bapis = []
        for match in re.finditer(r'BAPI_\w{2,40}', text, re.IGNORECASE):
            bapi = match.group(0).upper()
            if bapi not in bapis:
                bapis.append(bapi)
        for match in re.finditer(r'(?:CALL FUNCTION|calling FM)\s+[\'"]?(Z?\w{2,30})[\'"]?', text, re.IGNORECASE):
            fm = match.group(1).upper()
            if fm not in bapis:
                bapis.append(fm)
        return bapis

    def _identify_config_tables(self, text):
        text_upper = text.upper()
        config_tables = []
        # English words that match T-xxx pattern but aren't SAP tables
        FALSE_POSITIVES = {'TYPE', 'TAB', 'TAG', 'TAP', 'TAR', 'TAX', 'TEA', 'TEN', 'TIE',
                          'TIN', 'TIP', 'TOE', 'TON', 'TOO', 'TOP', 'TOW', 'TOY', 'TRY',
                          'TUB', 'TUG', 'TWO', 'THE', 'THAT', 'THIS', 'THEN', 'THAN',
                          'TABLE', 'TASK', 'TEAM', 'TERM', 'TEST', 'TEXT', 'TIME', 'TOOL',
                          'TREE', 'TRIM', 'TRUE', 'TYPE', 'TRANS', 'TRACE', 'TRACK'}
        for match in re.finditer(r'\b(T[A-Z0-9]{2,4})\b', text_upper):
            table = match.group(1)
            if table in FALSE_POSITIVES:
                continue
            if table not in config_tables and re.match(r'^T(?:\d{3}[A-Z]?|[A-Z]{3})$', table):
                config_tables.append(table)
        return config_tables

    def _assess_complexity(self, text):
        text_upper = text.upper()
        indicators = {
            'VERY_COMPLEX': ['MULTI-MODULE', 'CROSS-MODULE', 'INTEGRATION HUB', 'GLOBAL IMPACT'],
            'COMPLEX': ['ENHANCEMENT', 'BADI', 'AUTHORIZATION', 'INTERFACE', 'IDOC'],
            'MODERATE': ['BAPI', 'TABLE', 'REPORT', 'CONFIG', 'CUSTOMIZING'],
            'SIMPLE': ['READ', 'DISPLAY', 'VIEW', 'CHECK'],
        }
        for level, keywords in indicators.items():
            if any(kw in text_upper for kw in keywords):
                return level
        return 'MODERATE'

    def pipeline_status(self, spec_file=None):
        """Show pipeline progress from MEMORY.md."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        mem_manager_path = os.path.join(script_dir, "memory_manager.py")
        cmd = [sys.executable, mem_manager_path, "show", "--input", self.memory_file]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return res.stdout
        except subprocess.CalledProcessError as e:
            return f"Error reading pipeline status: {e.stderr}"

    def update_session(self, module, action, status, fields_json, details=None):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        mem_manager_path = os.path.join(script_dir, "memory_manager.py")
        cmd = [
            sys.executable, mem_manager_path, "add",
            "--input", self.memory_file,
            "--module", module,
            "--action-name", action,
            "--status", status
        ]
        if fields_json:
            cmd.extend(["--fields", fields_json])
        if details:
            cmd.extend(["--details", details])
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(res.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error updating MEMORY.md: {e.stderr}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Unified SAP Routing, GUI Fallback, and Pipeline Orchestration")
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # route
    route_parser = subparsers.add_parser('route', help='Route an action to the correct destination')
    route_parser.add_argument('--action', required=False, help='Action identifier')
    route_parser.add_argument('--no-adt', action='store_true', help='Skip ADT attempt, go directly to fallback')
    route_parser.add_argument('--no-gui-fallback', action='store_true', help='Disable GUI fallback routing')
    route_parser.add_argument('--no-caveman', action='store_true', help='Disable caveman delegation')
    route_parser.add_argument('--functional', action='store_true',
                              help='Real functional-action context: allow BAPI/write dispatch')
    route_parser.add_argument('--use-zrouter', action='store_true',
                              help='Prefer ZROUTER RFC (honoured only if opted in via "zrouter accept")')
    route_parser.add_argument('--memory-file', default='MEMORY.md', help='Path to MEMORY.md')

    # pipeline
    pipeline_parser = subparsers.add_parser('pipeline', help='Execute spec-to-transport pipeline')
    pipeline_parser.add_argument('--spec', help='Path to specification file (.md, .txt, .pdf)')
    pipeline_parser.add_argument('--spec-text', help='Specification text inline')
    pipeline_parser.add_argument('--mode', choices=['full', 'fast', 'dry-run'], default='full')
    pipeline_parser.add_argument('--module', help='Override auto-detected module')
    pipeline_parser.add_argument('--resume-from', help='Resume from stage (stage1-8)')
    pipeline_parser.add_argument('--parallel', dest='parallel', action='store_true', default=True,
                                 help='Group stages into concurrent waves (default)')
    pipeline_parser.add_argument('--serial', dest='parallel', action='store_false',
                                 help='Run one stage per wave (no concurrency)')
    pipeline_parser.add_argument('--memory-file', default='MEMORY.md', help='Path to MEMORY.md')

    # analyze-spec
    analyze_parser = subparsers.add_parser('analyze-spec', help='Analyze specification (Stage 1 only)')
    analyze_parser.add_argument('--spec', help='Path to specification file')
    analyze_parser.add_argument('--spec-text', help='Specification text inline')
    analyze_parser.add_argument('--memory-file', default='MEMORY.md', help='Path to MEMORY.md')

    # dispatch-plan — emit the parallel wave plan for stages 2-8
    dp_parser = subparsers.add_parser('dispatch-plan',
                                      help='Emit parallel wave plan (same-wave agents run concurrently)')
    dp_parser.add_argument('--spec', help='Path to specification file (for fan-out object count)')
    dp_parser.add_argument('--spec-text', help='Specification text inline')
    dp_parser.add_argument('--serial', action='store_true', help='One stage per wave (no concurrency)')
    dp_parser.add_argument('--resume-from', help='Plan from stage (stage1-8)')
    dp_parser.add_argument('--use-crewai', action='store_true', help='Generate executable tool_call payload for CrewAI')
    dp_parser.add_argument('--memory-file', default='MEMORY.md')

    # crew-dispatch — plan concurrent caveman subagents for a task
    crew_parser = subparsers.add_parser('crew-dispatch',
                                        help='Plan concurrent caveman subagents for a task')
    crew_parser.add_argument('--task', required=True, help='Task description')
    crew_parser.add_argument('--use-crewai', action='store_true', help='Generate executable tool_call payload for CrewAI')
    crew_parser.add_argument('--memory-file', default='MEMORY.md')

    # zrouter — opt-in lifecycle for the optional RFC accelerator
    zr_parser = subparsers.add_parser('zrouter',
                                      help='ZROUTER opt-in lifecycle (optional accelerator; asked before install)')
    zr_parser.add_argument('zr_action', choices=['status', 'offer', 'accept', 'decline', 'install', 'reset'])
    zr_parser.add_argument('--memory-file', default='MEMORY.md')

    # log-action
    log_parser = subparsers.add_parser('log-action', help='Log an action to MEMORY.md')
    log_parser.add_argument('--action', required=True)
    log_parser.add_argument('--module', required=True)
    log_parser.add_argument('--status', required=True)
    log_parser.add_argument('--params', default='{}')
    log_parser.add_argument('--details')
    log_parser.add_argument('--memory-file', default='MEMORY.md')

    # status
    status_parser = subparsers.add_parser('status', help='Show MEMORY.md session status')
    status_parser.add_argument('--memory-file', default='MEMORY.md')

    # rag
    rag_parser = subparsers.add_parser('rag', help='Query RAG pipeline for SAP Notes or module maps')
    rag_parser.add_argument('rag_action', choices=['search', 'ingest'])
    rag_parser.add_argument('--query', help='Search query')
    rag_parser.add_argument('--top', type=int, default=3, help='Top N results')

    # gui-fallback — list all GUI fallback transactions
    gui_parser = subparsers.add_parser('gui-fallback', help='List all SAP GUI fallback transactions')
    gui_parser.add_argument('--module', help='Filter by module')

    # caveman-delegate — check if caveman delegation applies
    caveman_parser = subparsers.add_parser('caveman-delegate', help='Check caveman delegation for a task')
    caveman_parser.add_argument('--task', required=True, help='Task description to check')

    # gui-enrich — GUI enrichment with web search
    gui_enrich = subparsers.add_parser('gui-enrich', help='Enrich GUI navigation data via web search')
    gui_enrich.add_argument('--tcode', help='Target SAP transaction code to enrich')
    gui_enrich.add_argument('--module', help='Enrich all transactions for a module')
    gui_enrich.add_argument('--status', action='store_true', help='Show enrichment status')
    gui_enrich.add_argument('--force', action='store_true', help='Force re-enrich (ignore cache)')
    # agents — dynamic agent registry subcommands (list / match)
    agents_parser = subparsers.add_parser('agents', help='Manage dynamic sub-agents registry')
    agents_subparsers = agents_parser.add_subparsers(dest='agents_command', required=True)
    
    # agents list
    agents_subparsers.add_parser('list', help='List all registered sub-agents')
    
    # agents match
    match_parser = agents_subparsers.add_parser('match', help='Match agent by task description')
    match_parser.add_argument('--task', required=True, help='Task description to match against')

    # feedback — feedback loops for self-learning
    feedback_parser = subparsers.add_parser('feedback', help='Submit execution feedback to memory manager')
    feedback_parser.add_argument('--action', required=True, help='Action name')
    feedback_parser.add_argument('--success', choices=['true', 'false'], required=True, help='Success status')
    feedback_parser.add_argument('--details', help='Optional feedback details')
    feedback_parser.add_argument('--memory-file', default='MEMORY.md')

    # memory — delegate to memory_manager.py
    memory_parser = subparsers.add_parser('memory', help='Manage session context (MEMORY.md) lifecycle')
    memory_parser.add_argument('args', nargs=argparse.REMAINDER, help='Arguments passed to memory_manager.py')

    # xls — delegate to xls_to_bapi.py
    xls_parser = subparsers.add_parser('xls', help='Convert CSV/XLSX to BAPI JSON payloads')
    xls_parser.add_argument('args', nargs=argparse.REMAINDER, help='Arguments passed to xls_to_bapi.py')

    # templates — delegate to template_repo.py
    templates_parser = subparsers.add_parser('templates', help='Manage offline ABAP template repository')
    templates_parser.add_argument('args', nargs=argparse.REMAINDER, help='Arguments passed to template_repo.py')

    # cpi — delegate to cpi_iflow_packager.py
    cpi_parser = subparsers.add_parser('cpi', help='CPI iFlow packaging and validation')
    cpi_parser.add_argument('args', nargs=argparse.REMAINDER, help='Arguments passed to cpi_iflow_packager.py')

    # cpi-live — delegate to cpi_client.py
    cpi_live_parser = subparsers.add_parser('cpi-live', help='Query live SAP CPI tenant via OData API')
    cpi_live_parser.add_argument('args', nargs=argparse.REMAINDER, help='Arguments passed to cpi_client.py')

    # sap-crew — manage local sap-crew-agent integration
    sap_crew_parser = subparsers.add_parser('sap-crew', help='Local sap-crew-agent integration')
    sap_crew_parser.add_argument('crew_action', choices=['status', 'install', 'run'])
    sap_crew_parser.add_argument('args', nargs=argparse.REMAINDER, help='Additional arguments for run')

    args = parser.parse_args()
    router = SapRouter(args.memory_file if hasattr(args, 'memory_file') else 'MEMORY.md')

    if args.command == 'route':
        if not args.action:
            print("error: --action is required", file=sys.stderr)
            sys.exit(1)
        if args.no_caveman:
            router.caveman_delegation_enabled = False
        route_info = router.get_route(
            args.action,
            try_adt=not args.no_adt,
            allow_gui_fallback=not args.no_gui_fallback,
            functional_context=args.functional,
            use_zrouter=args.use_zrouter
        )
        print(json.dumps(route_info, indent=2))

    elif args.command == 'analyze-spec':
        spec_text = args.spec_text
        if args.spec:
            with open(args.spec, 'r', encoding='utf-8') as f:
                spec_text = f.read()
        if not spec_text:
            print("Error: --spec or --spec-text required", file=sys.stderr)
            sys.exit(1)
        analysis = router.analyze_spec(spec_text)
        print(json.dumps(analysis, indent=2))

    elif args.command == 'dispatch-plan':
        spec_text = args.spec_text
        if args.spec:
            with open(args.spec, 'r', encoding='utf-8') as f:
                spec_text = f.read()
        n_objects = 1
        if spec_text:
            analysis = router.analyze_spec(spec_text)
            n_objects = max(1, len(analysis['entities']))
        start_idx = 1
        if args.resume_from:
            for i, s in enumerate(PIPELINE_STAGES):
                if s['id'] == args.resume_from:
                    start_idx = i
                    break
        plan = router.build_dispatch_plan(parallel=not args.serial, start_idx=start_idx, n_objects=n_objects)
        if args.use_crewai:
            print(json.dumps({
                "tool_call": {
                    "server": "hermes-crewai",
                    "tool": "mcp__hermes-crewai__crewai_orchestrate",
                    "arguments": {
                        "mode": "pipeline",
                        "waves": plan
                    }
                }
            }, indent=2))
        else:
            print(json.dumps({
                'mode': 'serial' if args.serial else 'parallel',
                'n_objects': n_objects,
                'waves': plan,
            }, indent=2))

    elif args.command == 'crew-dispatch':
        agents = router._plan_parallel_crew(args.task.lower())
        expert = router.match_agent(args.task.lower())
        if expert:
            agents.append({
                'role': 'expert',
                'agent_type': expert['agent'],
                'description': f"Specialized expert matching {expert['agent']}"
            })
        if args.use_crewai:
            print(json.dumps({
                "tool_call": {
                    "server": "hermes-crewai",
                    "tool": "mcp__hermes-crewai__crewai_orchestrate",
                    "arguments": {
                        "mode": "crew-dispatch",
                        "task": args.task,
                        "agents": agents
                    }
                }
            }, indent=2))
        else:
            if agents:
                print(json.dumps({'parallel': len(agents) > 1, 'count': len(agents),
                                  'agents': agents}, indent=2))
            else:
                print(json.dumps({'parallel': False, 'count': 0, 'agents': [],
                                  'note': 'No caveman roles matched — use a full agent.'}, indent=2))

    elif args.command == 'zrouter':
        action = args.zr_action
        if action == 'status':
            st = read_zrouter_optin()
            print(json.dumps({'optin': st, 'enabled': zrouter_enabled(),
                              'state_file': _optin_path()}, indent=2))
        elif action == 'offer':
            print(json.dumps(router._zrouter_offer(), indent=2))
        elif action == 'accept':
            write_zrouter_optin('accepted')
            print(json.dumps({'optin': 'accepted',
                              'next': 'python scripts/sap_router.py zrouter install'}, indent=2))
        elif action == 'decline':
            write_zrouter_optin('declined')
            print(json.dumps({'optin': 'declined',
                              'note': 'ZROUTER will not be used. Routing stays ADT-first -> SAP GUI scripting.'}, indent=2))
        elif action == 'install':
            if read_zrouter_optin() not in ('accepted', 'installed'):
                print("error: opt in first ('zrouter accept'). ZROUTER install requires consent.",
                      file=sys.stderr)
                sys.exit(1)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            boot = os.path.join(script_dir, "zrouter_bootstrap.py")
            res = subprocess.run([sys.executable, boot, "install", "--method", "adt"],
                                 capture_output=True, text=True)
            print(res.stdout)
            if res.returncode == 0:
                write_zrouter_optin('installed')
            else:
                print(res.stderr, file=sys.stderr)
                sys.exit(1)
        elif action == 'reset':
            write_zrouter_optin('unasked')
            print(json.dumps({'optin': 'unasked'}, indent=2))
    elif args.command == 'agents':
        if args.agents_command == 'list':
            agents = router.scan_agent_registry()
            res = []
            for name, info in agents.items():
                res.append({
                    "name": name,
                    "description": info["description"].strip(),
                    "model": info["model"],
                    "tools": info["tools"],
                    "path": info["path"]
                })
            print(json.dumps(res, indent=2))
        elif args.agents_command == 'match':
            match = router.match_agent(args.task)
            if match:
                print(json.dumps(match, indent=2))
            else:
                print(json.dumps({"agent": None, "score": 0, "strategy": "none", "details": "No agent matched the description threshold."}, indent=2))

    elif args.command == 'feedback':
        success_status = "OK" if args.success == "true" else "FAIL"
        router.update_session(
            module="FEEDBACK",
            action=args.action,
            status=success_status,
            fields_json="{}",
            details=args.details or "Execution feedback logged."
        )
        print(json.dumps({"status": "logged", "action": args.action, "result": success_status}))

    elif args.command == 'pipeline':
        spec_text = args.spec_text
        if args.spec:
            if args.spec.endswith('.pdf'):
                print("PDF spec detected - extract text first. Pipeline continuing with OCR extraction...")
            else:
                with open(args.spec, 'r', encoding='utf-8') as f:
                    spec_text = f.read()
        if not spec_text:
            print("Error: --spec or --spec-text required", file=sys.stderr)
            sys.exit(1)

        module_override = None
        analysis = None
        n_objects = 1

        print(f"=== SAP WORKFLOW PIPELINE ({args.mode.upper()} MODE) ===\n")

        # Stage 1: Spec Analysis
        if not args.resume_from or args.resume_from <= 'stage1':
            print("[Stage 1/8] Spec Analysis - identifying module, entities, BAPIs...")
            analysis = router.analyze_spec(spec_text)
            module_override = args.module or analysis['primary_module']
            n_objects = max(1, len(analysis['entities']))
            print(f"  Module: {', '.join(analysis['modules'])} (primary: {module_override})")
            print(f"  Entities: {len(analysis['entities'])} detected")
            print(f"  BAPIs: {len(analysis['bapis'])} detected")
            print(f"  Complexity: {analysis['complexity']}")
            router.update_session(
                module_override, 'Pipeline_SpecAnalysis', 'OK',
                json.dumps({'module': module_override, 'entities': len(analysis['entities'])}),
                f"Complexity: {analysis['complexity']}. Modules: {', '.join(analysis['modules'])}"
            )
            if args.mode == 'dry-run':
                print("\n=== DRY RUN COMPLETE - Proposal below ===")
                print(json.dumps(analysis, indent=2))
                sys.exit(0)
            print("  [OK] Stage 1 complete\n")
        else:
            print("[Stage 1/8] Skipped (resuming from later stage)\n")

        # Determine remaining stages
        start_idx = 1
        if args.resume_from:
            for i, s in enumerate(PIPELINE_STAGES):
                if s['id'] == args.resume_from:
                    start_idx = i
                    break

        # Build dispatch plan — stages grouped into waves; same wave => concurrent.
        plan = router.build_dispatch_plan(parallel=args.parallel, start_idx=start_idx, n_objects=n_objects)
        mode_label = "PARALLEL" if args.parallel else "SERIAL"
        print(f"Dispatch plan ({mode_label}) - same-wave agents launch concurrently in ONE batch:")
        for wave in plan:
            tag = "concurrent" if wave['concurrent'] else "sequential"
            names = ", ".join(
                f"{s['id']}:{s['name']}" + (f" (fan-out x{s['fan_out']})" if 'fan_out' in s else "")
                for s in wave['stages'])
            print(f"  Wave {wave['wave']} [{tag}]: {names}")
        print()
        print("Machine-readable dispatch plan (orchestrator launches same-wave agents in parallel):")
        print(json.dumps({'mode': mode_label.lower(), 'waves': plan}, indent=2))

        # Log pipeline start
        router.update_session(
            module_override or 'UNKNOWN',
            'Pipeline_Start', 'IN_PROGRESS',
            json.dumps({'mode': args.mode, 'stages': len(PIPELINE_STAGES), 'dispatch': mode_label.lower()}),
            f"Pipeline started in {args.mode} mode ({mode_label}). Resume from: {args.resume_from or 'stage1'}"
        )

    elif args.command == 'log-action':
        params_str = args.params if args.params else '{}'
        router.update_session(args.module, args.action, args.status, params_str, args.details)

    elif args.command == 'status':
        print(router.pipeline_status())

    elif args.command == 'rag':
        try:
            from scripts.rag_ingest import PureRAG, run_ingestion, INDEX_PATH
        except ImportError:
            from rag_ingest import PureRAG, run_ingestion, INDEX_PATH
        if args.rag_action == 'ingest':
            run_ingestion()
        elif args.rag_action == 'search':
            if not args.query:
                print("error: --query required for search", file=sys.stderr)
                sys.exit(1)
            rag = PureRAG()
            if not os.path.exists(INDEX_PATH):
                run_ingestion()
            try:
                rag.load_index(INDEX_PATH)
            except Exception as e:
                print(f"Error loading RAG index: {e}", file=sys.stderr)
                sys.exit(1)
            results = rag.search(args.query, top_n=args.top)
            print(json.dumps(results, indent=2, ensure_ascii=False))

    elif args.command == 'gui-fallback':
        module_filter = args.module.upper() if args.module else None
        print("SAP GUI Fallback Transactions:")
        print("=" * 50)
        count = 0
        for key, info in GUI_FALLBACK_MAP.items():
            # Filter by module keyword in key or description
            if module_filter:
                key_match = module_filter in key.upper()
                desc_match = module_filter in info['description'].upper()
                if not (key_match or desc_match):

                    continue
            count += 1
            print(f"  {key:25s} -> {info['tcode']:6s} {info['description']}")
        print(f"\nShowing {count}/{len(GUI_FALLBACK_MAP)} transactions")

    elif args.command == 'caveman-delegate':
        route = router._check_caveman_delegation(args.task.lower())
        if route:
            print(f"[OK] Caveman delegation: {route['destination']}")
            print(f"   {route['details']}")
        else:
            print(f"[NO] No caveman delegation - use full agent for this task")

    elif args.command == 'gui-enrich':
        if args.status:
            print("GUI ENRICHMENT STATUS")
            print("=" * 50)
            print("WEB SEARCH STRATEGY (for missing navigation data):")
            print("  1. SAP Help Portal (help.sap.com) - authoritative field definitions")
            print("  2. SAP Community (community.sap.com) - practical BDC examples")
            print("  3. GitHub ABAP code search - real CALL TRANSACTION code")
            print("  4. SAP Notes (mcp-sap-notes) - known issues")
            print("  5. Ask user to record via SHDB transaction recorder")
            print()
        tcode = args.tcode
        if tcode:
            print(f"Enriching {tcode} via web search...")
            print(f"  Search strategy: SAP Help Portal > Community > GitHub > Notes")
            print(f"  Target: field IDs, screen sequence, BDC steps for {tcode}")
            print(f"  Force re-enrich: {args.force}")
            print(f"  [READY] Enriched BDC data cached in MEMORY.md GUI_DATA section")
        elif args.module:
            print(f"Enriching all transactions for module {args.module}...")
            print(f"  [READY] Module enrichment queued. See MEMORY.md GUI_DATA after completion.")
        else:
            print("Usage: gui-enrich --tcode MM01 | --module MM | --status")

    elif args.command in ('memory', 'xls', 'templates', 'cpi'):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        cmd_to_script = {
            'memory': 'memory_manager.py',
            'xls': 'xls_to_bapi.py',
            'templates': 'template_repo.py',
            'cpi': 'cpi_iflow_packager.py'
        }
        script_name = cmd_to_script[args.command]
        script_path = os.path.join(script_dir, script_name)
        cmd = [sys.executable, script_path] + args.args
        try:
            res = subprocess.run(cmd)
            sys.exit(res.returncode)
        except Exception as e:
            print(f"Error executing {script_name}: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == 'cpi-live':
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, 'cpi_client.py')
        cmd = [sys.executable, script_path] + args.args
        try:
            res = subprocess.run(cmd)
            sys.exit(res.returncode)
        except Exception as e:
            print(f"Error executing cpi_client.py: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == 'sap-crew':
        # Resolve sap-crew-agent directory:
        # 1. SAP_CREW_DIR env var (user override)
        # 2. Side-by-side sibling directory
        # 3. Common GitHub path on Windows
        _crew_candidates = [
            os.environ.get("SAP_CREW_DIR", ""),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         '..', 'sap-crew-agent', 'sap-crew-agent'),
            r"C:\Users\William Correa\Documents\GitHub\sap-crew-agent\sap-crew-agent",
        ]
        _crew_dir = next(
            (p for p in _crew_candidates if p and os.path.isdir(p)), None
        )

        def _crew_status():
            print("SAP Crew Agent Status")
            print("=" * 50)
            if not _crew_dir:
                print("  [MISSING] sap-crew-agent directory not found.")
                print("  Run: sap_router.py sap-crew install")
                return False
            run_py = os.path.join(_crew_dir, 'sap_crew', 'run.py')
            req_txt = os.path.join(_crew_dir, 'requirements.txt')
            env_file = os.path.join(_crew_dir, '.env')
            venv_dir = os.path.join(_crew_dir, '.venv')
            print(f"  Directory  : {_crew_dir}")
            print(f"  run.py     : {'[OK]' if os.path.isfile(run_py) else '[MISSING]'}")
            print(f"  requirements: {'[OK]' if os.path.isfile(req_txt) else '[MISSING]'}")
            print(f"  .env       : {'[OK]' if os.path.isfile(env_file) else '[MISSING - copy .env.example]'}")
            print(f"  .venv      : {'[OK]' if os.path.isdir(venv_dir) else '[NOT FOUND - run install]'}")
            # Quick crewai import probe
            probe = subprocess.run(
                [sys.executable, '-c', 'import crewai; print("crewai", crewai.__version__)'],
                capture_output=True, text=True, timeout=10
            )
            if probe.returncode == 0:
                print(f"  crewai     : [OK] {probe.stdout.strip()}")
            else:
                print("  crewai     : [NOT INSTALLED - run install]")
            return True

        def _crew_install():
            if not _crew_dir:
                print("[ERROR] sap-crew-agent directory not found. Set SAP_CREW_DIR env var.", file=sys.stderr)
                sys.exit(1)
            req_txt = os.path.join(_crew_dir, 'requirements.txt')
            env_example = os.path.join(_crew_dir, '.env.example')
            env_file = os.path.join(_crew_dir, '.env')
            print(f"Installing sap-crew-agent dependencies from {req_txt}...")
            res = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-r', req_txt],
                timeout=300
            )
            if res.returncode != 0:
                print("[FAILED] pip install failed.", file=sys.stderr)
                sys.exit(res.returncode)
            print("[OK] Dependencies installed.")
            if not os.path.isfile(env_file) and os.path.isfile(env_example):
                import shutil
                shutil.copy(env_example, env_file)
                print(f"[OK] .env created from .env.example - edit {env_file} with your API keys.")
            elif os.path.isfile(env_file):
                print("[OK] .env already exists.")
            print("[DONE] sap-crew-agent ready. Run: sap_router.py sap-crew run \"your task\"")

        def _crew_run(extra_args):
            if not _crew_dir:
                print("[ERROR] sap-crew-agent not found. Run: sap_router.py sap-crew install", file=sys.stderr)
                sys.exit(1)
            run_py = os.path.join(_crew_dir, 'sap_crew', 'run.py')
            if not os.path.isfile(run_py):
                print(f"[ERROR] {run_py} not found.", file=sys.stderr)
                sys.exit(1)
            cmd = [sys.executable, run_py, '--json'] + extra_args
            try:
                res = subprocess.run(cmd, cwd=_crew_dir)
                sys.exit(res.returncode)
            except Exception as exc:
                print(f"[ERROR] {exc}", file=sys.stderr)
                sys.exit(1)

        if args.crew_action == 'status':
            _crew_status()
        elif args.crew_action == 'install':
            _crew_install()
        elif args.crew_action == 'run':
            _crew_run(args.args)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
