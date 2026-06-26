#!/usr/bin/env python3
"""
SAP Router v4.1 - intelligent routing engine with ADT-first, GUI-fallback strategy.
+parallel subagent dispatch +ZROUTER opt-in (asked, never the engine)
+functional-context BAPI gate +caveman delegation +pipeline orchestration.

Routing law (v4.1):
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

__version__ = "4.1.0"

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


class SapRouter:
    def __init__(self, memory_file="MEMORY.md"):
        self.memory_file = memory_file
        self.gui_fallback_enabled = True
        self.caveman_delegation_enabled = True

    def get_route(self, action, try_adt=True, allow_gui_fallback=True,
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

        # Step 1: ADT read/dev ops (primary path) — never fire a BAPI
        if try_adt:
            for adt_action in ADT_ACTIONS:
                if adt_action in action_lower:
                    return {
                        "destination": "ARC-1 (ADT)",
                        "mcp_server": "arc-1",
                        "fallback": "sap-gui-scripting",
                        "strategy": "adt-primary",
                        "details": "Direct ADT operation via arc-1 SAPRead/SAPWrite/SAPSearch"
                    }

        # Step 2: SuccessFactors (HCM cloud)
        if "sf_" in action_lower:
            return {
                "destination": "sf-mcp (OData)",
                "mcp_server": "sf-mcp",
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
                "details": (f"Functional action {action_upper}: dispatch {bapi} "
                            f"(GUI fallback: {tcode or 'n/a'}). Commit stays in the backend."),
            }
        return {
            "destination": "SAP GUI Scripting",
            "mcp_server": "mcp-sap-gui",
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

    def _identify_modules(self, text):
        text_upper = text.upper()
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

        detected = []
        for module, keywords in module_keywords.items():
            if any(kw in text_upper for kw in keywords):
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
    dp_parser.add_argument('--memory-file', default='MEMORY.md')

    # crew-dispatch — plan concurrent caveman subagents for a task
    crew_parser = subparsers.add_parser('crew-dispatch',
                                        help='Plan concurrent caveman subagents for a task')
    crew_parser.add_argument('--task', required=True, help='Task description')
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
        print(json.dumps({
            'mode': 'serial' if args.serial else 'parallel',
            'n_objects': n_objects,
            'waves': plan,
        }, indent=2))

    elif args.command == 'crew-dispatch':
        agents = router._plan_parallel_crew(args.task.lower())
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

    elif args.command == 'pipeline':
        spec_text = args.spec_text
        if args.spec:
            if args.spec.endswith('.pdf'):
                print("PDF spec detected — extract text first. Pipeline continuing with OCR extraction...")
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
        print(f"Dispatch plan ({mode_label}) — same-wave agents launch concurrently in ONE batch:")
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
            print(f"[NO] No caveman delegation — use full agent for this task")

    elif args.command == 'gui-enrich':
        if args.status:
            print("GUI ENRICHMENT STATUS")
            print("=" * 50)
            print("WEB SEARCH STRATEGY (for missing navigation data):")
            print("  1. SAP Help Portal (help.sap.com) — authoritative field definitions")
            print("  2. SAP Community (community.sap.com) — practical BDC examples")
            print("  3. GitHub ABAP code search — real CALL TRANSACTION code")
            print("  4. SAP Notes (mcp-sap-notes) — known issues")
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

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
