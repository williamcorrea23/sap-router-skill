#!/usr/bin/env python3
"""Template Repository — offline code template management.

Stores ABAP code templates with {{placeholders}}. Complements
xls_to_bapi.py: where xls_to_bapi converts CSV → BAPI payload,
template_repo resolves templates → deployable ABAP code.

Placeholder substitution uses evaluate_expression pattern
(GENERATE SUBROUTINE POOL) for runtime OR offline Python string
replacement for code generation / abapGit export.

Usage:
    python scripts/template_repo.py init     # Create blank repo
    python scripts/template_repo.py add      # Add template from file
    python scripts/template_repo.py resolve  # Substitute placeholders
    python scripts/template_repo.py export   # Export as abapGit/nugget JSON
    python scripts/template_repo.py list     # List all templates
"""

import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent / "template_repo"
TEMPLATES_FILE = REPO_DIR / "templates.json"
PACKAGES_FILE = REPO_DIR / "packages.json"

PLACEHOLDER_RE = re.compile(r"\{\{(\w+)\}\}")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

class Placeholder:
    def __init__(self, name: str, required: bool = True,
                 default: str = "", data_type: str = "CHAR",
                 description: str = "", max_length: int = 200):
        self.name = name
        self.required = required
        self.default = default
        self.data_type = data_type
        self.description = description
        self.max_length = max_length

    def to_dict(self):
        return {
            "name": self.name,
            "required": self.required,
            "default": self.default,
            "dataType": self.data_type,
            "description": self.description,
            "maxLength": self.max_length,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            name=d["name"],
            required=d.get("required", True),
            default=d.get("default", ""),
            data_type=d.get("dataType", "CHAR"),
            description=d.get("description", ""),
            max_length=d.get("maxLength", 200),
        )


class Template:
    def __init__(self, template_id: str = "", module: str = "",
                 action: str = "", title: str = "", description: str = "",
                 category: str = "bapi", version: int = 1,
                 code_lines: list = None, placeholders: list = None):
        self.template_id = template_id or str(uuid.uuid4()).replace("-", "")[:32]
        self.module = module.upper()
        self.action = action.upper()
        self.title = title
        self.description = description
        self.category = category
        self.version = version
        self.code_lines = code_lines or []
        self.placeholders = placeholders or []
        self.created_at = datetime.now(timezone.utc).isoformat()

    def extract_placeholders_from_code(self):
        """Scan code_lines for {{NAME}} and auto-create placeholder entries."""
        seen = set()
        for line in self.code_lines:
            for match in PLACEHOLDER_RE.finditer(line):
                name = match.group(1)
                if name not in seen:
                    seen.add(name)
                    if not any(p.name == name for p in self.placeholders):
                        self.placeholders.append(Placeholder(name=name))

    def resolve(self, values: dict) -> str:
        """Substitute {{placeholders}} with values dict.
        Raises KeyError if a required placeholder without default is missing.
        """
        result_lines = []
        for line in self.code_lines:
            def replacer(m):
                name = m.group(1)
                if name in values:
                    return str(values[name])
                ph = next((p for p in self.placeholders if p.name == name), None)
                if ph and ph.default:
                    return ph.default
                if ph and not ph.required:
                    return ""
                raise KeyError(
                    f"Missing required placeholder '{name}' "
                    f"(in template {self.template_id})"
                )
            result_lines.append(PLACEHOLDER_RE.sub(replacer, line))
        return "\n".join(result_lines)

    def to_dict(self):
        return {
            "templateId": self.template_id,
            "module": self.module,
            "action": self.action,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "version": self.version,
            "codeLines": self.code_lines,
            "placeholders": [p.to_dict() for p in self.placeholders],
            "createdAt": self.created_at,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            template_id=d["templateId"],
            module=d.get("module", ""),
            action=d.get("action", ""),
            title=d.get("title", ""),
            description=d.get("description", ""),
            category=d.get("category", "bapi"),
            version=d.get("version", 1),
            code_lines=d.get("codeLines", []),
            placeholders=[Placeholder.from_dict(p) for p in d.get("placeholders", [])],
        )


class Package:
    def __init__(self, pkg_id: str = "", name: str = "",
                 description: str = "", version: int = 1,
                 export_format: str = "json", template_ids: list = None):
        self.pkg_id = pkg_id or str(uuid.uuid4()).replace("-", "")[:32]
        self.name = name
        self.description = description
        self.version = version
        self.export_format = export_format
        self.template_ids = template_ids or []
        self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return {
            "pkgId": self.pkg_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "exportFormat": self.export_format,
            "templateIds": self.template_ids,
            "createdAt": self.created_at,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            pkg_id=d["pkgId"],
            name=d.get("name", ""),
            description=d.get("description", ""),
            version=d.get("version", 1),
            export_format=d.get("exportFormat", "json"),
            template_ids=d.get("templateIds", []),
        )


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def load_repo():
    if not TEMPLATES_FILE.exists():
        return []
    with open(TEMPLATES_FILE, encoding="utf-8") as f:
        return [Template.from_dict(t) for t in json.load(f)]


def save_repo(templates):
    REPO_DIR.mkdir(parents=True, exist_ok=True)
    with open(TEMPLATES_FILE, "w", encoding="utf-8") as f:
        json.dump([t.to_dict() for t in templates], f, indent=2, ensure_ascii=False)


def load_packages():
    if not PACKAGES_FILE.exists():
        return []
    with open(PACKAGES_FILE, encoding="utf-8") as f:
        return [Package.from_dict(p) for p in json.load(f)]


def save_packages(packages):
    REPO_DIR.mkdir(parents=True, exist_ok=True)
    with open(PACKAGES_FILE, "w", encoding="utf-8") as f:
        json.dump([p.to_dict() for p in packages], f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_init(_args=None):
    REPO_DIR.mkdir(parents=True, exist_ok=True)
    if not TEMPLATES_FILE.exists():
        save_repo([])
    if not PACKAGES_FILE.exists():
        save_packages([])
    print(f"Repo initialized at {REPO_DIR}")
    return 0


def cmd_list(_args=None):
    templates = load_repo()
    if not templates:
        print("No templates in repo.")
        return 0
    for t in templates:
        ph_count = len(t.placeholders)
        lines = len(t.code_lines)
        print(f"  {t.template_id[:12]}  {t.module:6} {t.action:22} "
              f"v{t.version}  {lines:3} lines  {ph_count} ph  {t.title}")
    print(f"\n{len(templates)} templates total")
    return 0


def cmd_add(args):
    """Add template from ABAP file. Usage: add --file path --module MM --action CREATE_MATERIAL [--title "My title"]"""
    filepath = args.get("file", "")
    module = args.get("module", "")
    action = args.get("action", "")
    title = args.get("title", "")

    if not filepath or not module or not action:
        print("ERROR: --file, --module, --action are required", file=sys.stderr)
        return 1

    path = Path(filepath)
    if not path.exists():
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        return 1

    templates = load_repo()
    code_lines = [line.rstrip("\n") for line in path.read_text(encoding="utf-8").splitlines()]

    t = Template(
        module=module,
        action=action,
        title=title or f"{module}_{action}",
        description=f"Auto-imported from {path.name}",
        code_lines=code_lines,
    )
    t.extract_placeholders_from_code()

    templates.append(t)
    save_repo(templates)

    ph_found = len(t.placeholders)
    print(f"Added: {t.template_id[:12]}  {module} {action}  ({len(code_lines)} lines, {ph_found} placeholders)")
    if ph_found:
        print("  Placeholders:", ", ".join(f"{{{{{p.name}}}}}" for p in t.placeholders))
    return 0


def cmd_resolve(args):
    """Resolve placeholders for a template. Usage: resolve --template <id/action> [--values '{"MATNR":"X"}']"""
    tpl_ref = args.get("template", "")
    values_json = args.get("values", "{}")

    if not tpl_ref:
        print("ERROR: --template required", file=sys.stderr)
        return 1

    templates = load_repo()
    candidates = [t for t in templates
                  if t.template_id.startswith(tpl_ref)
                  or t.action == tpl_ref.upper()
                  or f"{t.module}_{t.action}" == tpl_ref.upper()]

    if not candidates:
        print(f"ERROR: No template matches '{tpl_ref}'", file=sys.stderr)
        return 1
    if len(candidates) > 1:
        print(f"Ambiguous: {len(candidates)} match. Use --template with full ID:")
        for t in candidates:
            print(f"  {t.template_id}")
        return 1

    t = candidates[0]
    try:
        values = json.loads(values_json)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in --values: {e}", file=sys.stderr)
        return 1

    try:
        result = t.resolve(values)
        print(result)
        return 0
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


def cmd_export(args):
    """Export template(s) as JSON for abapGit / nugget.
    Usage: export --template <id> [--package <pkg_id>] [--format abapgit|nugget|json]
    """
    tpl_ref = args.get("template", "")
    pkg_ref = args.get("package", "")
    fmt = args.get("format", "json")

    templates = load_repo()
    packages = load_packages()

    if tpl_ref:
        candidates = [t for t in templates
                      if t.template_id.startswith(tpl_ref)
                      or t.action == tpl_ref.upper()]
        selected = candidates
    elif pkg_ref:
        pkg = next((p for p in packages if p.pkg_id.startswith(pkg_ref) or p.name == pkg_ref), None)
        if not pkg:
            print(f"ERROR: Package '{pkg_ref}' not found", file=sys.stderr)
            return 1
        selected = [t for t in templates if t.template_id in pkg.template_ids]
    else:
        print("ERROR: --template or --package required", file=sys.stderr)
        return 1

    if not selected:
        print("ERROR: No matching templates", file=sys.stderr)
        return 1

    export = {
        "exportedAt": datetime.now(timezone.utc).isoformat(),
        "format": fmt,
        "templates": [t.to_dict() for t in selected],
    }

    out = sys.stdout
    json.dump(export, out, indent=2, ensure_ascii=False)
    print()
    return 0


def cmd_seed(args):
    """Seed repo with starter templates for all 26 actions."""
    templates = load_repo()
    existing = {(t.module, t.action) for t in templates}

    seeds = [
        # (module, action, abap_code)
        ("MM", "CREATE_MATERIAL", [
            "CALL FUNCTION 'BAPI_MATERIAL_SAVEDATA'",
            "  EXPORTING",
            "    HEADDATA       = {{HEADER}}",
            "    MATERIALDESCRIPTION = {{DESCRIPTION}}",
            "  IMPORTING",
            "    RETURN         = {{RETURN_STRUCT}}",
            "    MATERIAL       = {{MATERIAL_NUMBER}}",
            "  TABLES",
            "    MATERIALDESCRIPTION = {{DESCRIPTION_TABLE}}.",
            "IF {{RETURN_STRUCT}}-TYPE = 'E'.",
            "  CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.",
            "ELSE.",
            "  CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING WAIT = 'X'.",
            "ENDIF.",
        ]),
        ("SD", "CREATE_ORDER", [
            "CALL FUNCTION 'BAPI_SALESORDER_CREATEFROMDAT2'",
            "  EXPORTING",
            "    ORDER_HEADER_IN  = {{HEADER}}",
            "    LOGICAL_SYSTEM   = {{LOG_SYS}}",
            "  IMPORTING",
            "    SALESDOCUMENT    = {{SALES_DOC}}",
            "    RETURN           = {{RETURN_STRUCT}}",
            "  TABLES",
            "    ORDER_ITEMS_IN   = {{ITEMS_TABLE}}.",
            "IF {{RETURN_STRUCT}}-TYPE = 'E'.",
            "  CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.",
            "ELSE.",
            "  CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING WAIT = 'X'.",
            "ENDIF.",
        ]),
        ("FI", "POST_DOCUMENT", [
            "CALL FUNCTION 'BAPI_ACC_DOCUMENT_POST'",
            "  EXPORTING",
            "    DOCUMENTHEADER = {{DOC_HEADER}}",
            "  IMPORTING",
            "    OBJ_TYPE       = {{OBJ_TYPE}}",
            "    OBJ_KEY        = {{OBJ_KEY}}",
            "    RETURN         = {{RETURN_STRUCT}}",
            "  TABLES",
            "    ACCOUNTGL      = {{ACCOUNT_GL}}",
            "    ACCOUNTPAYABLE = {{ACCOUNT_AP}}",
            "    ACCOUNTTAX     = {{ACCOUNT_TAX}}.",
            "IF {{RETURN_STRUCT}}-TYPE = 'E'.",
            "  CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.",
            "ELSE.",
            "  CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING WAIT = 'X'.",
            "ENDIF.",
        ]),
        ("QM", "CREATE_INSPECTION", [
            "CALL FUNCTION 'CO_QM_INSPECTION_LOT_CREATE'",
            "  EXPORTING",
            "    I_MATERIAL      = {{MATERIAL}}",
            "    I_WERK          = {{PLANT}}",
            "    I_INSP_TYPE     = {{INSP_TYPE}}",
            "    I_INSP_QTY      = {{QUANTITY}}",
            "  IMPORTING",
            "    E_INSPECTION    = {{INSP_LOT}}",
            "  TABLES",
            "    T_RETURN        = {{RETURN_TABLE}}.",
        ]),
        ("PP", "CREATE_ORDER", [
            "CALL FUNCTION 'BAPI_PRODORD_CREATE'",
            "  EXPORTING",
            "    ORDERDATA       = {{ORDER_DATA}}",
            "  IMPORTING",
            "    ORDER_NUMBER    = {{ORDER_NUM}}",
            "    RETURN          = {{RETURN_STRUCT}}.",
            "IF {{RETURN_STRUCT}}-TYPE = 'E'.",
            "  CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.",
            "ELSE.",
            "  CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING WAIT = 'X'.",
            "ENDIF.",
        ]),
        ("WM", "CREATE_TO", [
            "CALL FUNCTION 'L_TO_CREATE_SINGLE'",
            "  EXPORTING",
            "    I_LGNUM      = {{WAREHOUSE}}",
            "    I_BWLVS      = {{MOVE_TYPE}}",
            "    I_MATNR      = {{MATERIAL}}",
            "    I_ANFME      = {{QUANTITY}}",
            "    I_ALTME      = {{BASE_UOM}}",
            "    I_VLTKZ      = {{SRC_STORAGE}}",
            "    I_NLTKZ      = {{DEST_STORAGE}}",
            "    I_COMMIT_WORK = 'X'",
            "  IMPORTING",
            "    E_TANUM      = {{TO_NUMBER}}",
            "  EXCEPTIONS",
            "    OTHERS       = 99.",
        ]),
        ("CO", "CREATE_INTERNAL_ORDER", [
            "CALL FUNCTION 'BAPI_INTERNALORDER_CREATE'",
            "  EXPORTING",
            "    I_MASTER_DATA = {{MASTER_DATA}}",
            "  IMPORTING",
            "    ORDERID       = {{ORDER_ID}}",
            "    RETURN        = {{RETURN_STRUCT}}.",
            "IF {{RETURN_STRUCT}}-TYPE = 'E'.",
            "  CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.",
            "ELSE.",
            "  CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING WAIT = 'X'.",
            "ENDIF.",
        ]),
        ("HCM", "READ_EMPLOYEE", [
            "CALL FUNCTION 'BAPI_EMPLOYEE_GETDATA'",
            "  EXPORTING",
            "    EMPLOYEE_ID = {{EMPLOYEE_ID}}",
            "  TABLES",
            "    RETURN      = {{RETURN_TABLE}}.",
        ]),
        ("BASIS", "CREATE_REQUEST", [
            "CALL FUNCTION 'TR_INSERT_REQUEST_WITH_TASKS'",
            "  EXPORTING",
            "    IV_TYPE   = {{REQUEST_TYPE}}",
            "    IV_TEXT   = {{DESCRIPTION}}",
            "  IMPORTING",
            "    EV_REQUEST = {{REQUEST_ID}}",
            "  EXCEPTIONS",
            "    OTHERS    = 99.",
        ]),
        ("BASIS", "CODE_SEARCH", [
            "DATA: lo_searcher TYPE REF TO zcl_zrouter_code_search.",
            "CREATE OBJECT lo_searcher.",
            "DATA(ls_result) = lo_searcher->search( {{PAYLOAD}} ).",
            "/ui2/cl_json=>serialize( data = ls_result ).",
        ]),
        ("BASIS", "CODE_SEARCH_STATS", [
            "DATA: lo_searcher TYPE REF TO zcl_zrouter_code_search.",
            "CREATE OBJECT lo_searcher.",
            "DATA(lt_stats) = lo_searcher->get_statistics(",
            "  iv_package = {{PACKAGE}}",
            "  iv_owner   = {{OWNER}} ).",
            "/ui2/cl_json=>serialize( data = lt_stats ).",
        ]),
        ("BASIS", "CODE_SEARCH_ADT", [
            "DATA: lo_searcher TYPE REF TO zcl_zrouter_code_search.",
            "CREATE OBJECT lo_searcher.",
            "DATA(ls_result) = lo_searcher->search( {{PAYLOAD}} ).",
            "LOOP AT ls_result-hits ASSIGNING FIELD-SYMBOL(<h>).",
            "  <h>-source_url = zcl_zrouter_code_search=>build_adt_uri(",
            "    iv_object_name = <h>-object_name",
            "    iv_object_type = <h>-object_type ).",
            "ENDLOOP.",
            "/ui2/cl_json=>serialize( data = ls_result ).",
        ]),
    ]

    added = 0
    for module, action, code_lines in seeds:
        if (module, action) not in existing:
            t = Template(
                module=module,
                action=action,
                title=f"{module} {action}",
                description=f"Starter template for {module} action {action}",
                code_lines=code_lines,
            )
            t.extract_placeholders_from_code()
            templates.append(t)
            added += 1

    save_repo(templates)
    print(f"Seeded {added} new templates (total: {len(templates)})")
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    cmd = sys.argv[1]

    # Build arg dict from remaining positional --key val pairs
    raw_args = sys.argv[2:]
    args = {}
    i = 0
    while i < len(raw_args):
        if raw_args[i].startswith("--"):
            key = raw_args[i][2:]
            if i + 1 < len(raw_args) and not raw_args[i + 1].startswith("--"):
                args[key] = raw_args[i + 1]
                i += 2
            else:
                args[key] = ""
                i += 1
        else:
            i += 1

    commands = {
        "init": cmd_init,
        "list": cmd_list,
        "add": cmd_add,
        "resolve": cmd_resolve,
        "export": cmd_export,
        "seed": cmd_seed,
    }

    fn = commands.get(cmd)
    if not fn:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print("Available: init, list, add, resolve, export, seed", file=sys.stderr)
        return 1

    return fn(args)


if __name__ == "__main__":
    sys.exit(main())
