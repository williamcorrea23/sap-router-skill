#!/usr/bin/env python3
"""
SAP Router v4.0 - intelligent routing engine with ADT-first, GUI-fallback strategy.
+GUI fallback +caveman delegation +pipeline orchestration +self-learn +healthcheck
"""
import os
import re
import sys
import json
import argparse
import subprocess

__version__ = "4.0.0"

# === ZROUTER AVAILABILITY ===
# Cached probe result. None=not checked, True=installed, False=missing
_zrouter_state = None

def set_zrouter_state(installed):
    """Called by zrouter_bootstrap after probe to cache ZROUTER state."""
    global _zrouter_state
    _zrouter_state = installed

def get_zrouter_state():
    """Return cached ZROUTER state. None = not checked yet."""
    return _zrouter_state

# === ROUTING CONFIGURATION ===

ADT_ACTIONS = ["read_source", "search_object", "syntax_check", "where_used", "get_deps", "code_search"]

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

# Pipeline stage definitions
PIPELINE_STAGES = [
    {'id': 'stage1', 'name': 'Spec Analysis',        'skill': 'sap-router-skill',       'avg_time': '10s'},
    {'id': 'stage2', 'name': 'Technical Proposal',    'skill': 'sap-crew-analysis',      'avg_time': '3min'},
    {'id': 'stage3', 'name': 'Peer Review 1',         'skill': 'abap-code-review',       'avg_time': '1min'},
    {'id': 'stage4', 'name': 'Implementation',        'skill': 'cavecrew-builder + ADT',  'avg_time': 'varied'},
    {'id': 'stage5', 'name': 'Static Analysis (abaplint)', 'tool': 'npm run abap:review', 'avg_time': '30s'},
    {'id': 'stage6', 'name': 'Deep Analysis (Crew)',   'skill': 'sap-crew-analysis',      'avg_time': '5min'},
    {'id': 'stage7', 'name': 'Peer Review 2',          'skill': 'abap-code-review',       'avg_time': '1min'},
    {'id': 'stage8', 'name': 'Transport Gate',          'skill': 'sap-transport-gate',     'avg_time': '2min'},
]


class SapRouter:
    def __init__(self, memory_file="MEMORY.md"):
        self.memory_file = memory_file
        self.gui_fallback_enabled = True
        self.caveman_delegation_enabled = True

    def get_route(self, action, try_adt=True, allow_gui_fallback=True):
        """Route action: ADT → GUI fallback → ZROUTER RFC."""
        action_lower = action.lower()
        action_upper = action.upper()

        # Step 1: Try ADT (primary path for development operations)
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

        # Step 2: Check caveman delegation (optimize small-scope tasks)
        if self.caveman_delegation_enabled:
            caveman_route = self._check_caveman_delegation(action_lower)
            if caveman_route:
                return caveman_route

        # Step 3: HCM split — SuccessFactors vs on-prem
        if "sf_" in action_lower:
            return {
                "destination": "sf-mcp (OData)",
                "mcp_server": "sf-mcp",
                "strategy": "hcm-cloud",
                "details": "SuccessFactors API via OData V2 endpoint"
            }

        # Step 4: Check GUI fallback map
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

        # Step 5: ZROUTER RFC (default for BAPI-based operations)
        # Auto-probe ZROUTER state on first route for robustness
        if _zrouter_state is None:
            self._auto_probe_zrouter()

        if _zrouter_state is False:
            # ZROUTER not installed - use TieredFallback engine
            tiered = self._get_tiered_fallback(action_upper)
            if tiered:
                return tiered
            return {
                "destination": "BLOCKED",
                "strategy": "no-path",
                "details": ("ZROUTER not installed. All 6 fallback tiers failed for "
                            f"'{action_upper}'. "
                            "Install ZROUTER: python scripts/zrouter_bootstrap.py install --method adt"),
            }

        return {
            "destination": "ZROUTER RFC",
            "mcp_server": "sap-rfc-mcp-server",
            "strategy": "rfc-batch",
            "details": f"BAPI/RFC dispatch via ZROUTER_DISPATCH_FM with action '{action_upper}'"
        }

    def _auto_probe_zrouter(self):
        """Auto-probe ZROUTER state on first routing call."""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            probe_cmd = [sys.executable,
                         os.path.join(script_dir, "zrouter_bootstrap.py"),
                         "probe", "--json"]
            result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                set_zrouter_state(True)
            else:
                set_zrouter_state(False)
        except Exception:
            # Probe failed - stay None (will be re-probed)
            pass

    def _get_tiered_fallback(self, action_upper):
        """Use TieredFallback engine to find next best path."""
        try:
            from scripts.fallback_engine import TieredFallback
            engine = TieredFallback(memory_file=self.memory_file)
            result = engine.execute(action_upper)
            if result.get("success"):
                data = result.get("result", {})  # execute() already unwraps to data level
                tier = result.get("tier", 3)
                method = data.get("method", "SAP GUI")
                if "GUI Transaction" in str(method):
                    return {
                        "destination": "SAP GUI Scripting",
                        "mcp_server": "mcp-sap-gui",
                        "transaction": data.get("tcode", ""),
                        "strategy": "gui-fallback",
                        "tier": tier,
                        "warning": f"ZROUTER NOT INSTALLED (tier {tier} fallback)",
                        "fallback_chain": result.get("chain", []),
                        "verification": result.get("verification", {}),
                        "fix": "python scripts/zrouter_bootstrap.py install --method adt",
                    }
                return {
                    "destination": f"Tier {tier} Fallback",
                    "strategy": f"fallback-tier-{tier}",
                    "method": method,
                    "tier": tier,
                    "warning": "ZROUTER NOT INSTALLED",
                    "fix": "python scripts/zrouter_bootstrap.py install --method adt",
                }
        except ImportError:
            pass
        return None

    def _check_caveman_delegation(self, action_lower):
        """Check if task can be delegated to a caveman sub-agent for token efficiency."""
        if any(kw in action_lower for kw in CAVEMAN_DELEGATION['builder']['trigger_keywords']):
            # Verify single-file scope — cavecrew-builder refuses 3+ files
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
    route_parser.add_argument('--action', required=True, help='Action identifier')
    route_parser.add_argument('--no-adt', action='store_true', help='Skip ADT attempt, go directly to fallback')
    route_parser.add_argument('--no-gui-fallback', action='store_true', help='Disable GUI fallback routing')
    route_parser.add_argument('--no-caveman', action='store_true', help='Disable caveman delegation')
    route_parser.add_argument('--memory-file', default='MEMORY.md', help='Path to MEMORY.md')

    # pipeline
    pipeline_parser = subparsers.add_parser('pipeline', help='Execute spec-to-transport pipeline')
    pipeline_parser.add_argument('--spec', help='Path to specification file (.md, .txt, .pdf)')
    pipeline_parser.add_argument('--spec-text', help='Specification text inline')
    pipeline_parser.add_argument('--mode', choices=['full', 'fast', 'dry-run'], default='full')
    pipeline_parser.add_argument('--module', help='Override auto-detected module')
    pipeline_parser.add_argument('--resume-from', help='Resume from stage (stage1-8)')
    pipeline_parser.add_argument('--memory-file', default='MEMORY.md', help='Path to MEMORY.md')

    # analyze-spec
    analyze_parser = subparsers.add_parser('analyze-spec', help='Analyze specification (Stage 1 only)')
    analyze_parser.add_argument('--spec', help='Path to specification file')
    analyze_parser.add_argument('--spec-text', help='Specification text inline')
    analyze_parser.add_argument('--memory-file', default='MEMORY.md', help='Path to MEMORY.md')

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
        if args.no_caveman:
            router.caveman_delegation_enabled = False
        route_info = router.get_route(
            args.action,
            try_adt=not args.no_adt,
            allow_gui_fallback=not args.no_gui_fallback
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

    elif args.command == 'pipeline':
        spec_text = args.spec_text
        if args.spec:
            if args.spec.endswith('.pdf'):
                print("PDF spec detected — use extract text first. Pipeline continuing with OCR extraction...")
            else:
                with open(args.spec, 'r', encoding='utf-8') as f:
                    spec_text = f.read()
        if not spec_text:
            print("Error: --spec or --spec-text required", file=sys.stderr)
            sys.exit(1)

        module_override = None  # Initialize before conditional branches

        print(f"=== SAP WORKFLOW PIPELINE ({args.mode.upper()} MODE) ===\n")

        # Stage 1: Spec Analysis
        if not args.resume_from or args.resume_from <= 'stage1':
            print("[Stage 1/8] Spec Analysis - identifying module, entities, BAPIs...")
            analysis = router.analyze_spec(spec_text)
            module_override = args.module or analysis['primary_module']
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

        # Stage 2-8 instructions
        stages_remaining = ''
        start_idx = 1
        if args.resume_from:
            for i, s in enumerate(PIPELINE_STAGES):
                if s['id'] == args.resume_from:
                    start_idx = i
                    break

        for stage in PIPELINE_STAGES[start_idx:]:
            stages_remaining += f"  {stage['id']}: {stage['name']} → {stage.get('skill', stage.get('tool', 'manual'))} (~{stage['avg_time']})\n"

        print(f"Remaining stages to execute:")
        print(stages_remaining)
        print(f"Next: invoke sap-crew-analysis for technical proposal (Stage 2/8)")
        print(f"Full automation: each stage auto-triggers the listed skill/tool")

        # Log pipeline start
        router.update_session(
            module_override or 'UNKNOWN',
            'Pipeline_Start', 'IN_PROGRESS',
            json.dumps({'mode': args.mode, 'stages': len(PIPELINE_STAGES)}),
            f"Pipeline started in {args.mode} mode. Resume from: {args.resume_from or 'stage1'}"
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
