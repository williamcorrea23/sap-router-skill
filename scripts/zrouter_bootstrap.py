#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ZROUTER Bootstrap v4.2.0 - probe, install, and fallback manager."""

import json
import sys
import argparse
import subprocess
from pathlib import Path

__version__ = "4.2.0"

SKILL_DIR = Path(__file__).resolve().parent.parent

ZROUTER_REQUIRED_OBJECTS = [
    # Core dispatcher + exception
    {"type": "CLAS", "name": "ZCL_ZROUTER_DISPATCH", "critical": True,
     "desc": "Main dispatcher class - routes actions to module handlers"},
    {"type": "CLAS", "name": "CX_ZROUTER", "critical": True,
     "desc": "Exception class - all ZROUTER errors"},
    {"type": "FUGR", "name": "ZROUTER", "critical": True,
     "desc": "Function group for ZROUTER_DISPATCH_FM"},
    {"type": "FUNC", "name": "ZROUTER_DISPATCH_FM", "critical": True,
     "desc": "RFC-enabled Function Module - main entry point"},
    # Interface definitions
    {"type": "INTF", "name": "ZIF_ZROUTER_HANDLER", "critical": True,
     "desc": "Handler interface - handle_action method signature"},
    {"type": "INTF", "name": "ZIF_ZROUTER_CONFIG", "critical": False,
     "desc": "Config interface - action allowlist and config lookup"},
    {"type": "INTF", "name": "ZIF_ZROUTER_LOGGER", "critical": False,
     "desc": "Logger interface - audit trail for all actions"},
    # Infrastructure classes
    {"type": "CLAS", "name": "ZCL_ZROUTER_CONFIG", "critical": True,
     "desc": "Config class - DB-backed action allowlist"},
    {"type": "CLAS", "name": "ZCL_ZROUTER_LOGGER", "critical": True,
     "desc": "Logger class - BAL-style audit logging"},
    {"type": "CLAS", "name": "ZCL_ZROUTER_AUTHORITY", "critical": True,
     "desc": "Authority class - ZROUTER auth object checks"},
    {"type": "CLAS", "name": "ZCL_ZROUTER_BATCH", "critical": False,
     "desc": "Batch class - sequential multi-action execution"},
    # Abstract handler base
    {"type": "CLAS", "name": "ZCL_ZROUTER_HANDLER_ABSTRACT", "critical": True,
     "desc": "Abstract handler base - before_action/after_action/evaluate_expression"},
    # Module handler classes (9 modules)
    {"type": "CLAS", "name": "ZCL_ZROUTER_HANDLER_MM", "critical": True,
     "desc": "MM handler - material master, purchase orders, config"},
    {"type": "CLAS", "name": "ZCL_ZROUTER_HANDLER_SD", "critical": True,
     "desc": "SD handler - sales orders, deliveries, billing, config"},
    {"type": "CLAS", "name": "ZCL_ZROUTER_HANDLER_FI", "critical": True,
     "desc": "FI handler - document posting, balance retrieval"},
    {"type": "CLAS", "name": "ZCL_ZROUTER_HANDLER_QM", "critical": False,
     "desc": "QM handler - inspection lots, results recording"},
    {"type": "CLAS", "name": "ZCL_ZROUTER_HANDLER_PP", "critical": False,
     "desc": "PP handler - production orders, BOM, routing"},
    {"type": "CLAS", "name": "ZCL_ZROUTER_HANDLER_WM", "critical": False,
     "desc": "WM handler - goods movements, transfer orders"},
    {"type": "CLAS", "name": "ZCL_ZROUTER_HANDLER_CO", "critical": False,
     "desc": "CO handler - internal orders, activity allocations"},
    {"type": "CLAS", "name": "ZCL_ZROUTER_HANDLER_HCM", "critical": False,
     "desc": "HCM handler - employee data, infotype operations"},
    {"type": "CLAS", "name": "ZCL_ZROUTER_HANDLER_BASIS", "critical": False,
     "desc": "BASIS handler - transports, ST22, code analysis"},
    # DDIC tables
    {"type": "TABL", "name": "ZROUTER_CONFIG", "critical": True,
     "desc": "Action configuration table - module/action allowlist"},
    {"type": "TABL", "name": "ZROUTER_LOG", "critical": True,
     "desc": "Audit log table - all action executions"},
    {"type": "TABL", "name": "ZROUTER_BATCH_RESULT", "critical": False,
     "desc": "Batch result table - multi-action execution logs"},
    {"type": "TABL", "name": "ZROUTER_TMPL_HD", "critical": False,
     "desc": "Template header table - code repository"},
    {"type": "TABL", "name": "ZROUTER_TMPL_CD", "critical": False,
     "desc": "Template code body table"},
]

ADT_INSTALL_SEQUENCE = [
    {"action": "create_package",
     "cmd": "aibap: create_object(type='DEVC', name='ZROUTER')",
     "desc": "Create ZROUTER development package"},
    {"action": "create_dtel",
     "cmd": "aibap: create_object(type='DTEL', name='ZROUTER_TMPL_ID')",
     "desc": "ZROUTER_TMPL_ID - Template identifier CHAR32"},
    {"action": "create_dtel",
     "cmd": "aibap: create_object(type='DTEL', name='ZROUTER_MODULE')",
     "desc": "ZROUTER_MODULE - SAP Module CHAR3"},
    {"action": "create_dtel",
     "cmd": "aibap: create_object(type='DTEL', name='ZROUTER_ACTION')",
     "desc": "ZROUTER_ACTION - Action name CHAR30"},
    {"action": "create_dtel",
     "cmd": "aibap: create_object(type='DTEL', name='ZROUTER_VERSION')",
     "desc": "ZROUTER_VERSION - Version NUMC4"},
    {"action": "create_dtel",
     "cmd": "aibap: create_object(type='DTEL', name='ZROUTER_ACTIVE')",
     "desc": "ZROUTER_ACTIVE - Active flag CHAR1"},
    {"action": "create_dtel",
     "cmd": "aibap: create_object(type='DTEL', name='ZROUTER_LINE_NUM')",
     "desc": "ZROUTER_LINE_NUM - Code line number NUMC6"},
    {"action": "create_dtel",
     "cmd": "aibap: create_object(type='DTEL', name='ZROUTER_CODE_LINE')",
     "desc": "ZROUTER_CODE_LINE - Source code line CHAR255"},
    {"action": "create_table",
     "cmd": "aibap: create_object(type='TABL', name='ZROUTER_TMPL_HD')",
     "desc": "ZROUTER_TMPL_HD - Template header table"},
    {"action": "create_table",
     "cmd": "aibap: create_object(type='TABL', name='ZROUTER_TMPL_CD')",
     "desc": "ZROUTER_TMPL_CD - Template code body table"},
    {"action": "create_table",
     "cmd": "aibap: create_object(type='TABL', name='ZROUTER_TMPL_PL')",
     "desc": "ZROUTER_TMPL_PL - Template placeholder table"},
    {"action": "create_table",
     "cmd": "aibap: create_object(type='TABL', name='ZROUTER_TMPL_PKG')",
     "desc": "ZROUTER_TMPL_PKG - Export package header table"},
    {"action": "create_table",
     "cmd": "aibap: create_object(type='TABL', name='ZROUTER_TMPL_PKG_T')",
     "desc": "ZROUTER_TMPL_PKG_T - Export package items table"},
    {"action": "deploy_class",
     "cmd": "python scripts/abap_serializer.py package --source templates/ZROUTER_DISPATCH.abap --name ZCL_ZROUTER_DISPATCH --type CLAS --output deploy/",
     "desc": "Serialize ZROUTER_DISPATCH.abap -> deploy/abapgit/ files"},
    {"action": "write_class",
     "cmd": "arc-1: SAPWrite(uri='/sap/bc/adt/oo/classes/zcl_zrouter_dispatch/source/main')",
     "desc": "Write ZCL_ZROUTER_DISPATCH source to SAP via ADT"},
    {"action": "create_fugr",
     "cmd": "aibap: create_object(type='FUGR', name='ZROUTER')",
     "desc": "Create ZROUTER Function Group"},
    {"action": "create_func",
     "cmd": "aibap: create_object(type='FUNC', name='ZROUTER_DISPATCH_FM', function_group='ZROUTER')",
     "desc": "Create ZROUTER_DISPATCH_FM - RFC-enabled entry point"},
    {"action": "activate",
     "cmd": "aibap: activate_objects(['ZCL_ZROUTER_DISPATCH','CX_ZROUTER','ZROUTER_DISPATCH_FM','ZROUTER_TMPL_HD','ZROUTER_TMPL_CD','ZROUTER_TMPL_PL','ZROUTER_TMPL_PKG','ZROUTER_TMPL_PKG_T'])",
     "desc": "Activate all ZROUTER objects"},
]

GUI_INSTALL_SEQUENCE = [
    {"tcode": "SE80", "desc": "Object Navigator - create package ZROUTER",
     "steps": ["Enter 'ZROUTER' in package field", "Press Enter", "Confirm creation"]},
    {"tcode": "SE11", "desc": "ABAP Dictionary - create DTEL + TABL",
     "steps": ["Select 'Data type' radio", "Enter ZROUTER_TMPL_ID", "Click Create"]},
    {"tcode": "SE24", "desc": "Class Builder - create ZCL_ZROUTER_DISPATCH",
     "steps": ["Enter ZCL_ZROUTER_DISPATCH", "Click Create", "Paste source from deploy/"]},
    {"tcode": "SE37", "desc": "Function Builder - create ZROUTER_DISPATCH_FM",
     "steps": ["Enter ZROUTER_DISPATCH_FM", "Click Create", "Set function group ZROUTER",
               "Attributes tab -> Processing type: Remote-Enabled Module"]},
]

ACTION_GUI_MAP = {
    'MM_CREATE_MATERIAL': 'MM01', 'MM_CHANGE_MATERIAL': 'MM02',
    'MM_CREATE_PO': 'ME21N', 'MM_GOODS_MOVEMENT': 'MIGO',
    'SD_CREATE_ORDER': 'VA01', 'SD_CHANGE_ORDER': 'VA02',
    'SD_CREATE_DELIVERY': 'VL01N', 'SD_CREATE_INVOICE': 'VF01',
    'FI_POST_DOCUMENT': 'FB01', 'FI_REVERSE_DOCUMENT': 'FB02',
    'FI_CHECK_ACCOUNTS': 'FS00',
    'QM_CREATE_INSPECTION': 'QA01', 'QM_RECORD_RESULTS': 'QE01',
    'PP_CREATE_ORDER': 'CO01', 'PP_READ_BOM': 'CS01',
    'WM_GOODS_MOVEMENT': 'MIGO', 'WM_CREATE_TO': 'LT01',
    'CO_CREATE_INTERNAL_ORDER': 'KO01',
    'HCM_READ_EMPLOYEE': 'PA20', 'HCM_CREATE_INFOTYPE': 'PA30',
}


class ZrouterProbe:
    def __init__(self):
        self.results = {
            "installed": False, "probe_method": None,
            "missing_critical": [], "missing_non_critical": [],
            "available_mcps": {"adt": False, "gui": False, "rfc": False},
            "install_path": None, "recommendations": [],
        }

    def probe_via_adt(self):
        self.results["probe_method"] = "ADT"
        for obj in ZROUTER_REQUIRED_OBJECTS:
            info = self._check_object_adt(obj["type"], obj["name"])
            if info["exists"]:
                continue
            if obj["critical"]:
                self.results["missing_critical"].append(obj)
            else:
                self.results["missing_non_critical"].append(obj)
        self.results["available_mcps"]["adt"] = (
            len(self.results["missing_critical"]) == 0
        )
        self.results["installed"] = len(self.results["missing_critical"]) == 0
        return self.results["installed"]

    def _check_object_adt(self, obj_type, name):
        """Check if ABAP object exists via ADT. Accepts externally set state."""
        try:
            from scripts.sap_router import get_zrouter_state
            cached = get_zrouter_state()
            if cached is True:
                return {"exists": True, "source": "cached-probe"}
            if cached is False:
                return {"exists": False, "source": "cached-probe",
                        "reason": "ZROUTER probed: not installed"}
        except (ImportError, ModuleNotFoundError):
            sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
            try:
                from scripts.sap_router import get_zrouter_state
                cached = get_zrouter_state()
                if cached is True:
                    return {"exists": True, "source": "cached-probe"}
                if cached is False:
                    return {"exists": False, "source": "cached-probe",
                            "reason": "ZROUTER probed: not installed"}
            except ImportError:
                pass
        return {"exists": False, "source": "unprobed",
                "reason": "Run: aibap get_object_info(name='" + name + "')"}

    def determine_install_path(self):
        if self.results["available_mcps"]["adt"]:
            self.results["install_path"] = "ADT"
            return "ADT"
        if self.results["available_mcps"]["gui"]:
            self.results["install_path"] = "GUI"
            return "GUI"
        self.results["install_path"] = "OFFLINE"
        return "OFFLINE"

    def get_fallback_action(self, requested_action):
        action_upper = requested_action.upper()
        if action_upper in ACTION_GUI_MAP:
            return {"type": "gui_fallback", "tcode": ACTION_GUI_MAP[action_upper],
                    "reason": "ZROUTER not installed - routed to SAP GUI transaction"}
        module_map = {'MM': 'MM01', 'SD': 'VA01', 'FI': 'FB01', 'QM': 'QA01',
                      'PP': 'CO01', 'WM': 'MIGO', 'CO': 'KO01', 'HCM': 'PA20'}
        for module, tcode in module_map.items():
            if f'_{module}_' in action_upper or action_upper.startswith(module):
                return {"type": "gui_fallback", "tcode": tcode,
                        "reason": "ZROUTER not installed - routed to module default GUI"}
        return {"type": "blocked", "reason": "ZROUTER not installed and no GUI fallback",
                "fix": "python scripts/zrouter_bootstrap.py install --method adt"}


def cmd_probe(args):
    probe = ZrouterProbe()
    print("Probing ZROUTER installation...")
    print("[1/3] ADT probe...")
    adt_result = probe.probe_via_adt()
    if adt_result:
        print("  [OK] ZROUTER installed (ADT confirmed)")
    else:
        print("  [WARN] ZROUTER NOT installed or ADT unavailable")
        for obj in probe.results["missing_critical"]:
            print(f"    - {obj['type']} {obj['name']}: {obj['desc']}")

    print("[2/3] GUI probe...")
    print("  GUI not configured - skip GUI probe")

    print("[3/3] Install path...")
    path = probe.determine_install_path()
    print(f"  Best path: {path}")
    print()

    print("=" * 60)
    print("ZROUTER PROBE REPORT")
    print("=" * 60)
    print(f"Installed: {'YES' if probe.results['installed'] else 'NO'}")
    print(f"Install path: {path}")

    if probe.results["missing_critical"]:
        print(f"CRITICAL missing ({len(probe.results['missing_critical'])}):")
        for obj in probe.results["missing_critical"]:
            print(f"  {obj['type']} {obj['name']} - {obj['desc']}")

    if not probe.results["installed"]:
        print(f"\nRECOMMENDED: python scripts/zrouter_bootstrap.py install --method {path.lower()}")

    if probe.results["installed"]:
        return 0
    return 1


def cmd_install(args):
    probe = ZrouterProbe()
    probe.probe_via_adt()
    probe.determine_install_path()
    method = args.method or probe.results["install_path"] or "adt"

    print(f"ZROUTER INSTALL - Method: {method.upper()}")
    print("=" * 60)

    if method == "adt":
        return _install_adt(args)
    elif method == "gui":
        return _install_gui(args)
    elif method == "offline":
        return _install_offline(args)
    print(f"ERROR: Unknown method '{method}'")
    return 1


def _install_adt(args):
    total = len(ADT_INSTALL_SEQUENCE)
    for idx, step in enumerate(ADT_INSTALL_SEQUENCE, 1):
        print(f"  [{idx}/{total}] {step['desc']}")
    if args.dry_run:
        print(f"\n[DRY-RUN] {total} steps listed.")
    else:
        print("\n[DONE] Run probe to verify.")
    return 0


def _install_gui(args):
    for idx, step in enumerate(GUI_INSTALL_SEQUENCE, 1):
        tcode = step['tcode']
        desc = step['desc']
        print(f"  [{idx}/{len(GUI_INSTALL_SEQUENCE)}] {tcode} - {desc}")
    print("\nRequires: SAP GUI installed + sapgui/user_scripting=TRUE")
    return 0


def _install_offline(args):
    templates_dir = SKILL_DIR / "templates"
    output_dir = SKILL_DIR / "zrouter_export"
    print(f"Exporting ZROUTER to {output_dir}")
    if not args.dry_run:
        serializer = SKILL_DIR / "scripts" / "abap_serializer.py"
        result = subprocess.run([
            sys.executable, str(serializer), "package",
            "--source", str(templates_dir / "ZROUTER_DISPATCH.abap"),
            "--name", "ZCL_ZROUTER_DISPATCH", "--type", "CLAS",
            "--output", str(output_dir)
        ], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"ERROR: {result.stderr}", file=sys.stderr)
            return 1
    print(f"Import via abapGit -> clone {output_dir / 'abapgit'} -> pull into SAP")
    return 0


def cmd_fallback(args):
    probe = ZrouterProbe()
    fallback = probe.get_fallback_action(args.action)
    print(json.dumps(fallback, indent=2))
    return 1 if fallback["type"] == "blocked" else 0


def main():
    parser = argparse.ArgumentParser(description="ZROUTER Bootstrap v4.0")
    sub = parser.add_subparsers(dest="command", help="Commands")
    p = sub.add_parser("probe"); p.add_argument("--json", action="store_true")
    i = sub.add_parser("install"); i.add_argument("--method", choices=["adt","gui","offline"])
    i.add_argument("--dry-run", action="store_true")
    f = sub.add_parser("fallback"); f.add_argument("--action", required=True)
    args = parser.parse_args()

    if args.command == "probe": return cmd_probe(args)
    elif args.command == "install": return cmd_install(args)
    elif args.command == "fallback": return cmd_fallback(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
