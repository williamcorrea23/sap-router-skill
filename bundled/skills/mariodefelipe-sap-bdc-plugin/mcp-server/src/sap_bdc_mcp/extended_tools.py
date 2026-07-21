"""Extended MCP tools for SAP BDC — adds discovery and troubleshooting capabilities.

New tools added in v0.3.0:
    - list_shares:                    List all Databricks Delta shares visible to the caller
    - get_share_details:              Detailed info about a single share (objects, comments, metadata)
    - list_recipients:                List configured Delta Sharing recipients
    - validate_tenant_hostname:       Pre-flight validation for BDC tenant hostname (SAP Notes 3652165 & 3705747)
    - check_deletion_vectors:         Detect Delta tables with Deletion Vectors enabled (SAP Note 3706399)
    - cleanup_orphaned_data_product:  Orphan data product handling (SAP Note 3720724)
    - diagnose_share_error:           Map error messages to SAP Note resolutions

New tools added in v0.5.0 (driven by SAP help.sap.com 2026-05-02 batch — supportfiles4):
    - validate_databricks_privileges: Check the principal has CREATE CATALOG, CREATE SHARE,
                                      SET SHARE PERMISSION, USE PROVIDER, USE RECIPIENT,
                                      USE SHARE on the metastore
    - validate_ord_metadata:          Validate ORD JSON before publishing (title/shortDescription/
                                      description rules, visibility/releaseStatus enums, ISO dates)
    - list_unsupported_share_assets:  Flag assets in a catalog/schema that cannot be shared via
                                      Delta Sharing to BDC (e.g. materialized views)
"""

import json
import logging
import os
import re
from typing import Any

logger = logging.getLogger("sap-bdc-mcp.extended")


# ---------------------------------------------------------------------------
# Tool schema definitions (returned from list_tools())
# ---------------------------------------------------------------------------

EXTENDED_TOOL_SCHEMAS = [
    {
        "name": "list_shares",
        "description": "List all Databricks Delta shares visible to the current workspace. "
                       "Returns share names, creation time, owner, and comment.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of shares to return (default: 100)"
                }
            }
        }
    },
    {
        "name": "get_share_details",
        "description": "Get full details about a Databricks share including the list of objects "
                       "(tables/views), owner, creation info, and comments.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "share_name": {
                    "type": "string",
                    "description": "Name of the share to inspect"
                }
            },
            "required": ["share_name"]
        }
    },
    {
        "name": "list_recipients",
        "description": "List all Delta Sharing recipients configured in the Databricks workspace. "
                       "Useful for discovering the recipient name to use in other tools.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "validate_tenant_hostname",
        "description": "Validate a proposed BDC tenant hostname against SAP's rules. "
                       "Catches the common failure documented in SAP Notes 3652165 and 3705747 "
                       "(uppercase letters cause silent provisioning hangs; duplicate hostnames rejected).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "hostname": {
                    "type": "string",
                    "description": "The proposed tenant hostname to validate"
                }
            },
            "required": ["hostname"]
        }
    },
    {
        "name": "check_deletion_vectors",
        "description": "Pre-flight check for SAP Note 3706399: detect whether any tables in a "
                       "Databricks share have Deletion Vectors enabled. Tables with DV enabled cannot "
                       "be published to the SAP BDC catalog and cause error 500 'unable to serve request'.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "share_name": {
                    "type": "string",
                    "description": "Name of the share to inspect"
                }
            },
            "required": ["share_name"]
        }
    },
    {
        "name": "cleanup_orphaned_data_product",
        "description": "Handle the orphan scenario from SAP Note 3720724: a Databricks share was deleted "
                       "manually, but the Data Product remains 'Active' in the BDC Catalog and cannot be "
                       "unpublished normally. This tool surfaces the issue with guidance and, where possible, "
                       "attempts SDK-level deletion.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "share_name": {
                    "type": "string",
                    "description": "Name of the orphaned share / data product"
                },
                "force": {
                    "type": "boolean",
                    "description": "Attempt SDK-level cleanup (default: false — produces guidance only)"
                }
            },
            "required": ["share_name"]
        }
    },
    {
        "name": "diagnose_share_error",
        "description": "Map an SAP BDC / Databricks error message to the relevant SAP Note and "
                       "resolution steps. Knows about OIDC code exchange failures, error 500s on CSN "
                       "sharing, SCIM 'only one replace' errors, CIS integration issues, and more.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "error_message": {
                    "type": "string",
                    "description": "The error message or error text to diagnose"
                },
                "context": {
                    "type": "string",
                    "description": "Optional additional context (e.g., 'happened during share publish')"
                }
            },
            "required": ["error_message"]
        }
    },
    {
        "name": "validate_databricks_privileges",
        "description": "Pre-flight check that the executing principal has the metastore privileges "
                       "required to share data products to/from BDC. Required: CREATE CATALOG, "
                       "CREATE SHARE, SET SHARE PERMISSION, USE PROVIDER, USE RECIPIENT, USE SHARE. "
                       "Source: SAP help.sap.com 'Working with Data Products in SAP Databricks' (May 2026).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "principal": {
                    "type": "string",
                    "description": "User or group name to validate. Defaults to the current Databricks principal if omitted."
                }
            },
            "required": []
        }
    },
    {
        "name": "validate_ord_metadata",
        "description": "Validate Open Resource Discovery (ORD) JSON before publishing a data product. "
                       "Catches the most common publish failures locally — required fields, "
                       "description != shortDescription, visibility/releaseStatus enum values, "
                       "ISO 8601 dates, and sunset >= deprecation. Pure-logic, no SDK call.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ord": {
                    "type": "object",
                    "description": "ORD object (the value of @openResourceDiscoveryV1)"
                }
            },
            "required": ["ord"]
        }
    },
    {
        "name": "list_unsupported_share_assets",
        "description": "Scan a Databricks catalog/schema and flag assets that cannot be shared via "
                       "Delta Sharing to BDC. As of May 2026 the only known unsupported type is "
                       "materialized views. Returns a list with full_name, type, and a hint.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "catalog": {
                    "type": "string",
                    "description": "Databricks catalog name to scan"
                },
                "schema": {
                    "type": "string",
                    "description": "Optional schema name within the catalog. If omitted, scans all schemas."
                }
            },
            "required": ["catalog"]
        }
    }
]


# ---------------------------------------------------------------------------
# Tool handlers — called by server.py dispatcher
# ---------------------------------------------------------------------------

def handle_list_shares(arguments: dict, workspace_client) -> str:
    """List Databricks Delta shares."""
    max_results = arguments.get("max_results", 100)
    try:
        shares = list(workspace_client.shares.list())[:max_results]
        rows = []
        for s in shares:
            rows.append({
                "name": getattr(s, "name", None),
                "owner": getattr(s, "owner", None),
                "created_at": str(getattr(s, "created_at", "")),
                "comment": getattr(s, "comment", None),
            })
        return (
            f"Found {len(rows)} share(s):\n"
            f"{json.dumps(rows, indent=2, default=str)}"
        )
    except Exception as e:
        return f"❌ Failed to list shares: {e}"


def handle_get_share_details(arguments: dict, workspace_client) -> str:
    """Detailed share info."""
    share_name = arguments["share_name"]
    try:
        s = workspace_client.shares.get(share_name)
        objects = []
        for obj in (getattr(s, "objects", None) or []):
            objects.append({
                "name": getattr(obj, "name", None),
                "data_object_type": getattr(obj, "data_object_type", None),
                "shared_as": getattr(obj, "shared_as", None),
                "added_at": str(getattr(obj, "added_at", "")),
                "history_data_sharing_status": str(getattr(obj, "history_data_sharing_status", "")),
            })
        details = {
            "name": getattr(s, "name", None),
            "owner": getattr(s, "owner", None),
            "comment": getattr(s, "comment", None),
            "created_at": str(getattr(s, "created_at", "")),
            "updated_at": str(getattr(s, "updated_at", "")),
            "object_count": len(objects),
            "objects": objects,
        }
        return f"Share '{share_name}' details:\n{json.dumps(details, indent=2, default=str)}"
    except Exception as e:
        return f"❌ Failed to get share details for '{share_name}': {e}"


def handle_list_recipients(arguments: dict, workspace_client) -> str:
    """List Delta Sharing recipients."""
    try:
        recipients = list(workspace_client.recipients.list())
        rows = []
        for r in recipients:
            rows.append({
                "name": getattr(r, "name", None),
                "authentication_type": str(getattr(r, "authentication_type", "")),
                "owner": getattr(r, "owner", None),
                "comment": getattr(r, "comment", None),
                "created_at": str(getattr(r, "created_at", "")),
            })
        return f"Found {len(rows)} recipient(s):\n{json.dumps(rows, indent=2, default=str)}"
    except Exception as e:
        return f"❌ Failed to list recipients: {e}"


def handle_validate_tenant_hostname(arguments: dict, *_args) -> str:
    """Validate proposed tenant hostname per SAP rules.

    References:
      - SAP Note 3652165: BDC Core provisioning hangs when hostname has uppercase letters.
        Only lowercase [a-z], digits [0-9], and hyphen '-' are allowed.
      - SAP Note 3705747: Hostnames must be unique within a region.
    """
    hostname = arguments["hostname"]
    errors = []
    warnings = []

    if not hostname:
        return "❌ Hostname is empty."

    if len(hostname) < 3:
        errors.append("Hostname is too short (minimum 3 characters recommended).")
    if len(hostname) > 63:
        errors.append("Hostname exceeds 63 characters — most SAP host validators reject this.")

    if hostname != hostname.lower():
        errors.append(
            "❌ Hostname contains uppercase letters. Per SAP Note 3652165 this causes "
            "BDC Core provisioning to hang silently. Use only [a-z0-9-]."
        )

    if not re.fullmatch(r"[a-z0-9-]+", hostname):
        errors.append(
            "❌ Hostname contains characters outside [a-z0-9-]. Remove underscores, dots, "
            "uppercase, or other special chars."
        )

    if hostname.startswith("-") or hostname.endswith("-"):
        errors.append("❌ Hostname must not start or end with a hyphen.")

    if "--" in hostname:
        warnings.append("⚠️  Double hyphens are allowed but discouraged for readability.")

    warnings.append(
        "ℹ️  SAP Note 3705747: hostnames must be unique within the region. "
        "This tool cannot verify uniqueness remotely — try the provisioning and watch for "
        "'The host name XXX is already being used'."
    )

    if errors:
        return (
            f"❌ Hostname '{hostname}' is INVALID:\n"
            + "\n".join(f"  {e}" for e in errors)
            + "\n\nWarnings:\n"
            + "\n".join(f"  {w}" for w in warnings)
        )

    return (
        f"✅ Hostname '{hostname}' passes syntactic validation.\n\n"
        + "\n".join(f"  {w}" for w in warnings)
    )


def handle_check_deletion_vectors(arguments: dict, workspace_client) -> str:
    """Detect deletion vectors on tables in a share (SAP Note 3706399)."""
    share_name = arguments["share_name"]
    warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")

    if not warehouse_id:
        return (
            "⚠️  DATABRICKS_WAREHOUSE_ID is not set — cannot run SQL to inspect Deletion Vectors.\n"
            "Set it and retry, or manually run:\n"
            "  DESCRIBE DETAIL <table>  — look at 'delta.enableDeletionVectors' in properties."
        )

    try:
        share = workspace_client.shares.get(share_name)
        objects = getattr(share, "objects", None) or []
        if not objects:
            return f"Share '{share_name}' has no objects — nothing to check."

        flagged = []
        for obj in objects:
            table_full = getattr(obj, "name", None)
            if not table_full:
                continue
            try:
                res = workspace_client.statement_execution.execute_statement(
                    warehouse_id=warehouse_id,
                    statement=f"DESCRIBE DETAIL {table_full}",
                    wait_timeout="30s",
                )
                # Parse the 'properties' column — typically column index may vary.
                if res.result and res.result.data_array:
                    for row in res.result.data_array:
                        row_str = json.dumps(row, default=str)
                        if "enableDeletionVectors" in row_str and "true" in row_str.lower():
                            flagged.append(table_full)
                            break
            except Exception as e:
                logger.warning(f"Could not inspect {table_full}: {e}")

        if flagged:
            return (
                f"❌ Share '{share_name}' has {len(flagged)} table(s) with Deletion Vectors enabled:\n"
                + "\n".join(f"  - {t}" for t in flagged)
                + "\n\nPer SAP Note 3706399, publishing to the BDC catalog will fail with error 500.\n"
                "Resolution:\n"
                "  ALTER TABLE <t> SET TBLPROPERTIES ('delta.enableDeletionVectors' = 'false');\n"
                "  Then REORG TABLE <t> APPLY (PURGE); to rewrite data files."
            )

        return (
            f"✅ Share '{share_name}' — no Deletion Vectors detected on {len(objects)} table(s). "
            "Safe to publish per SAP Note 3706399."
        )

    except Exception as e:
        return f"❌ Failed to check deletion vectors: {e}"


def handle_cleanup_orphaned_data_product(arguments: dict, bdc_client) -> str:
    """Handle orphaned data product scenario (SAP Note 3720724)."""
    share_name = arguments["share_name"]
    force = arguments.get("force", False)

    guidance = (
        f"SAP Note 3720724: Orphaned data product '{share_name}'\n\n"
        "Scenario: Delta share was deleted manually in Databricks but the Data Product remains\n"
        "'Active' in the BDC catalog and normal unpublish does not work.\n\n"
        "Recommended resolution:\n"
        "  1. Recreate an empty share with the same name in Databricks\n"
        "  2. Grant it to your recipient\n"
        "  3. Call unpublish_data_product() then delete_share() via this MCP server\n"
        "  4. Finally drop the temporary empty share\n\n"
        "Alternative: open an SAP support case quoting SAP Note 3720724 for manual catalog cleanup."
    )

    if not force:
        return guidance

    # Best-effort: try SDK delete_share directly
    try:
        result = bdc_client.delete_share(share_name=share_name)
        return (
            f"✅ Attempted SDK-level cleanup of '{share_name}':\n"
            f"{json.dumps(result, indent=2, default=str)}\n\n"
            "If the data product still appears Active in the BDC Cockpit, fall back to the "
            "guidance below.\n\n" + guidance
        )
    except Exception as e:
        return (
            f"❌ Force cleanup failed: {e}\n\n"
            "Falling back to manual guidance:\n\n" + guidance
        )


# ---------------------------------------------------------------------------
# Symptom → SAP Note map for diagnose_share_error
# ---------------------------------------------------------------------------

_DIAGNOSTIC_RULES = [
    {
        "patterns": [r"oidc[_\s]+code[_\s]+exchange[_\s]+failure",
                     r"error\s+logging\s+you\s+in.*oidc"],
        "note": "SAP Note 3678584",
        "title": "SAP Databricks OIDC Code Exchange Failure",
        "cause": "Databricks client ID/secret pair expires every 6 months.",
        "resolution": (
            "1. Exclude the affected IAS tenant from the Formation type "
            "'Integration with SAP Databricks'.\n"
            "2. Re-include the IAS tenant (regenerates the client secret).\n"
            "3. Retry login."
        ),
    },
    {
        "patterns": [r"unable\s+to\s+serve\s+your\s+request",
                     r"errorCode.*500.*create_or_update_share_csn",
                     r"HTTP response body.*\"errorCode\":500"],
        "note": "SAP Notes 3706399 & 3717031",
        "title": "Generic 500 error when publishing CSN / Delta Share to BDC",
        "cause": (
            "Possible causes:\n"
            "  - Deletion Vectors enabled on shared tables (3706399)\n"
            "  - Missing permissions on the share or recipient\n"
            "  - Assets missing on the shared table\n"
            "  - Metastore admin changed"
        ),
        "resolution": (
            "1. Run check_deletion_vectors(share_name=...) to rule out 3706399.\n"
            "2. Verify SHOW GRANTS ON SHARE <share> includes the BDC recipient.\n"
            "3. Verify all referenced tables still exist and are accessible.\n"
            "4. Confirm the metastore admin has not changed."
        ),
    },
    {
        "patterns": [r"only\s+one\s+replace\s+operation\s+is\s+allowed",
                     r"scimType.*invalidValue"],
        "note": "SAP Note 3738570",
        "title": "Databricks SCIM rejects SAP IPS multi-replace PATCH",
        "cause": "Databricks SCIM allows only one replace op per PATCH; SAP IPS sends multiple.",
        "resolution": (
            "Apply the workaround in SAP Note 3738570 (IPS transformation to split PATCHes) "
            "or provision the users one at a time until Databricks lifts the restriction."
        ),
    },
    {
        "patterns": [r"sap\s+cloud\s+identity\s+service\s+integration\s+not\s+configured",
                     r"already\s+part\s+of\s+another\s+formation"],
        "note": "SAP Notes 3706392 & 3694878",
        "title": "CIS integration not configured on SAP Databricks",
        "cause": (
            "Either:\n"
            "  - CIS integration is genuinely not yet configured (3706392), or\n"
            "  - You are trying to use the same CIS for a second Databricks tenant (3694878), "
            "which is not supported in a single formation."
        ),
        "resolution": (
            "For 3706392: wait up to 30 minutes after provisioning, or open a support case "
            "with component BDC-DBX-CON.\n"
            "For 3694878: provision the second Databricks tenant with a different CIS, or join "
            "it to a new formation."
        ),
    },
    {
        "patterns": [r"the\s+host\s+name\s+\S+\s+is\s+already\s+being\s+used"],
        "note": "SAP Note 3705747",
        "title": "Duplicate hostname during BDC Cockpit provisioning",
        "cause": "Hostname already registered by another user in the same region.",
        "resolution": "Choose a unique hostname. Use validate_tenant_hostname() to precheck.",
    },
    {
        "patterns": [r"provisioning.*hangs", r"provisioning.*stuck",
                     r"taking\s+long.*provisioning"],
        "note": "SAP Note 3652165",
        "title": "BDC Core provisioning hangs",
        "cause": "tenantHostName contains uppercase letters — silent failure.",
        "resolution": (
            "Delete the failed instance; recreate with a hostname in [a-z0-9-] only. "
            "Use validate_tenant_hostname() to precheck."
        ),
    },
    {
        "patterns": [r"orphan(ed)?\s+data\s+product", r"data\s+product.*active.*after.*delete"],
        "note": "SAP Note 3720724",
        "title": "Orphan data product in BDC catalog",
        "cause": "Delta share was deleted in Databricks UI, BDC catalog still sees the Data Product.",
        "resolution": "Use cleanup_orphaned_data_product() or open SAP support quoting 3720724.",
    },
    {
        "patterns": [r"-0001-11-30", r"negative\s+date", r"00000000.*date"],
        "note": "SAP Note 3736857",
        "title": "Null SAP dates become negative dates in Databricks",
        "cause": "SAP blank date '00000000' is parsed by Spark as year -1, month 11, day 30.",
        "resolution": (
            "In your Transformation Flow, coerce '00000000' (or equivalent null sentinels) "
            "to true SQL NULL before the downstream date cast."
        ),
    },
    {
        "patterns": [r"business\s+name.*missing.*unity\s+catalog"],
        "note": "SAP Note 3725086",
        "title": "Business Name missing in Unity Catalog",
        "cause": "Historical limitation — Databricks now supports this metadata.",
        "resolution": (
            "Ensure the SAP Databricks / Enterprise Databricks cluster runtime is recent enough; "
            "the fix is delivered. Re-mount the share if necessary."
        ),
    },
    {
        "patterns": [r"hana\s+cloud.*not\s+listed.*customer\s+landscape"],
        "note": "SAP Note 3731036",
        "title": "HANA Cloud instance not visible in BDC Customer Landscape",
        "cause": "SAP HANA Cloud Central is not running in the subaccount.",
        "resolution": (
            "Ensure HANA Cloud Central is active in the subaccount — it acts as the Data Product "
            "gateway for all HANA instances in that subaccount."
        ),
    },
]


def handle_diagnose_share_error(arguments: dict, *_args) -> str:
    """Map an error message to the relevant SAP Note and resolution."""
    error = arguments["error_message"]
    context = arguments.get("context", "")
    haystack = (error + " " + context).lower()

    hits = []
    for rule in _DIAGNOSTIC_RULES:
        for pat in rule["patterns"]:
            if re.search(pat, haystack, re.IGNORECASE):
                hits.append(rule)
                break

    if not hits:
        return (
            "🤔 No matching SAP Note found for this error message.\n\n"
            "Recommended next steps:\n"
            "  - Open SAP Note 3653192 (main Databricks/BDC troubleshooting guide)\n"
            "  - Follow SAP Note 3568017 for guidance on opening a support case\n"
            "  - Include the full stack trace, request ID, and timestamp in your case"
        )

    parts = [f"Found {len(hits)} matching SAP Note(s):\n"]
    for h in hits:
        parts.append(
            f"\n━━━ {h['note']}: {h['title']} ━━━\n"
            f"Cause: {h['cause']}\n"
            f"Resolution:\n{h['resolution']}\n"
        )
    return "\n".join(parts)



# ---------------------------------------------------------------------------
# v0.5.0 handlers — driven by 2026-05-02 SAP help.sap.com batch
# ---------------------------------------------------------------------------

REQUIRED_METASTORE_PRIVILEGES = (
    "CREATE CATALOG",
    "CREATE SHARE",
    "SET SHARE PERMISSION",
    "USE PROVIDER",
    "USE RECIPIENT",
    "USE SHARE",
)


def handle_validate_databricks_privileges(arguments: dict, workspace_client) -> str:
    """Pre-flight: confirm principal has the 6 metastore privileges needed for BDC sharing."""
    principal = arguments.get("principal")

    if workspace_client is None:
        return (
            "[error] No Databricks workspace client available. Configure DATABRICKS_HOST + "
            "DATABRICKS_TOKEN, or run inside a Databricks notebook with dbutils."
        )

    try:
        meta = workspace_client.metastores.summary()
        metastore_id = getattr(meta, "metastore_id", None) or (
            meta.get("metastore_id") if isinstance(meta, dict) else None
        )
        if not metastore_id:
            return "[error] Unable to resolve metastore id from workspace_client.metastores.summary()"

        if not principal:
            try:
                me = workspace_client.current_user.me()
                principal = getattr(me, "user_name", None) or (
                    me.get("userName") if isinstance(me, dict) else None
                ) or "<unknown>"
            except Exception:
                principal = "<current-principal>"

        try:
            effective = workspace_client.grants.get_effective(
                securable_type="METASTORE",
                full_name=metastore_id,
                principal=principal,
            )
        except Exception as e:
            return f"[error] Could not query effective grants on metastore {metastore_id}: {e}"

        granted = set()
        assignments = getattr(effective, "privilege_assignments", None) or []
        for a in assignments:
            privs = getattr(a, "privileges", None) or []
            for pp in privs:
                pname = getattr(pp, "privilege", None) or (
                    pp.get("privilege") if isinstance(pp, dict) else str(pp)
                )
                if pname:
                    granted.add(str(pname).upper())

        missing = [p for p in REQUIRED_METASTORE_PRIVILEGES if p not in granted]
        result = {
            "ok": len(missing) == 0,
            "principal": principal,
            "metastore_id": metastore_id,
            "required": list(REQUIRED_METASTORE_PRIVILEGES),
            "granted_subset": sorted(granted & set(REQUIRED_METASTORE_PRIVILEGES)),
            "missing": missing,
            "hint": (
                "All required privileges granted." if not missing else
                "Grant the missing privileges via Catalog > Manage > Metastore > Permissions > Grant. "
                "Source: SAP help.sap.com 'Working with Data Products in SAP Databricks' (May 2026)."
            ),
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"[error] validate_databricks_privileges failed: {e}"


_VISIBILITY_VALUES = {"public", "interval", "private"}
_RELEASE_STATUS_VALUES = {"active", "beta", "deprecated"}


def _is_iso8601(s: str) -> bool:
    if not isinstance(s, str):
        return False
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:?\d{2})?)?$", s))


def handle_validate_ord_metadata(arguments: dict, *_args) -> str:
    """Validate ORD JSON. Pure-logic — no SDK call."""
    ord_obj = arguments.get("ord") or {}
    errors: list = []
    warnings: list = []

    if isinstance(ord_obj, dict) and "@openResourceDiscoveryV1" in ord_obj and isinstance(
        ord_obj["@openResourceDiscoveryV1"], dict
    ):
        ord_obj = ord_obj["@openResourceDiscoveryV1"]

    for field in ("title", "shortDescription", "description"):
        v = ord_obj.get(field) if isinstance(ord_obj, dict) else None
        if not v or not isinstance(v, str) or not v.strip():
            errors.append(f"Required field '{field}' is missing or empty")

    short = (ord_obj.get("shortDescription") if isinstance(ord_obj, dict) else "") or ""
    desc = (ord_obj.get("description") if isinstance(ord_obj, dict) else "") or ""
    if short and desc and short.strip() and short.strip() in desc:
        errors.append(
            "ORD rule: 'description' must NOT contain the 'shortDescription' value. "
            "Rewrite description to avoid quoting shortDescription verbatim."
        )

    vis = ord_obj.get("visibility") if isinstance(ord_obj, dict) else None
    if vis is not None and vis not in _VISIBILITY_VALUES:
        errors.append(f"visibility must be one of {sorted(_VISIBILITY_VALUES)}; got {vis!r}")

    rs = ord_obj.get("releaseStatus") if isinstance(ord_obj, dict) else None
    if rs is not None and rs not in _RELEASE_STATUS_VALUES:
        errors.append(f"releaseStatus must be one of {sorted(_RELEASE_STATUS_VALUES)}; got {rs!r}")

    dep = ord_obj.get("deprecationDate") if isinstance(ord_obj, dict) else None
    sun = ord_obj.get("sunsetDate") if isinstance(ord_obj, dict) else None
    if dep is not None and not _is_iso8601(dep):
        errors.append(f"deprecationDate must be ISO 8601; got {dep!r}")
    if sun is not None and not _is_iso8601(sun):
        errors.append(f"sunsetDate must be ISO 8601; got {sun!r}")
    if dep and sun and _is_iso8601(dep) and _is_iso8601(sun) and sun < dep:
        errors.append(
            f"sunsetDate ({sun}) must be greater than or equal to deprecationDate ({dep})"
        )

    if isinstance(ord_obj, dict):
        if not ord_obj.get("industry"):
            warnings.append("Optional 'industry' is empty — recommended for data product discovery")
        if not ord_obj.get("lineOfBusiness"):
            warnings.append("Optional 'lineOfBusiness' is empty — recommended for data product discovery")

    return json.dumps({
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "spec_reference": "https://sap.github.io/csn-interop-specification/",
    }, indent=2)


def handle_list_unsupported_share_assets(arguments: dict, workspace_client) -> str:
    """Scan a catalog (optionally a schema within it) for Delta Sharing-unsupported asset types."""
    catalog = (arguments.get("catalog") or "").strip()
    schema = (arguments.get("schema") or "").strip() or None

    if not catalog:
        return "[error] 'catalog' argument is required"

    if workspace_client is None:
        return (
            "[error] No Databricks workspace client available. Configure DATABRICKS_HOST + "
            "DATABRICKS_TOKEN, or run inside a Databricks notebook with dbutils."
        )

    unsupported: list = []
    inspected = 0
    try:
        if schema:
            class _S:
                def __init__(self, n): self.name = n
            schemas_iter = [_S(schema)]
        else:
            try:
                schemas_iter = list(workspace_client.schemas.list(catalog_name=catalog))
            except Exception as e:
                return f"[error] Could not list schemas in catalog {catalog}: {e}"

        for sch in schemas_iter:
            sch_name = getattr(sch, "name", None) or (
                sch.get("name") if isinstance(sch, dict) else None
            )
            if not sch_name:
                continue
            try:
                tables = list(workspace_client.tables.list(catalog_name=catalog, schema_name=sch_name))
            except Exception as e:
                unsupported.append({
                    "full_name": f"{catalog}.{sch_name}.*",
                    "type": "ERROR",
                    "reason": f"Could not list tables: {e}",
                })
                continue

            for t in tables:
                inspected += 1
                ttype = getattr(t, "table_type", None)
                ttype_str = (
                    ttype.value if hasattr(ttype, "value") else str(ttype) if ttype else ""
                ).upper()
                tname = getattr(t, "name", None)
                if "MATERIALIZED" in ttype_str:
                    unsupported.append({
                        "full_name": f"{catalog}.{sch_name}.{tname}",
                        "type": ttype_str,
                        "reason": "Materialized views are not supported by SAP Databricks Delta Sharing",
                        "fix": "Re-expose as a regular view, or persist as a Delta table",
                    })

        return json.dumps({
            "catalog": catalog,
            "schema": schema,
            "inspected_count": inspected,
            "unsupported_count": len(unsupported),
            "unsupported": unsupported,
            "source": "SAP help.sap.com 'Working with Data Products in SAP Databricks' (page 9)",
        }, indent=2)
    except Exception as e:
        return f"[error] list_unsupported_share_assets failed: {e}"


# ---------------------------------------------------------------------------
# Dispatcher — called from server.py
# ---------------------------------------------------------------------------

HANDLERS = {
    "list_shares": handle_list_shares,
    "get_share_details": handle_get_share_details,
    "list_recipients": handle_list_recipients,
    "validate_tenant_hostname": handle_validate_tenant_hostname,
    "check_deletion_vectors": handle_check_deletion_vectors,
    "cleanup_orphaned_data_product": handle_cleanup_orphaned_data_product,
    "diagnose_share_error": handle_diagnose_share_error,
    # v0.5.0
    "validate_databricks_privileges": handle_validate_databricks_privileges,
    "validate_ord_metadata": handle_validate_ord_metadata,
    "list_unsupported_share_assets": handle_list_unsupported_share_assets,
}


def dispatch_extended(name: str, arguments: dict, *, bdc_client=None, workspace_client=None):
    """Invoke an extended tool handler. Returns a string result."""
    handler = HANDLERS.get(name)
    if not handler:
        return None  # signal that this isn't an extended tool

    # Handlers that need the workspace client
    if name in {
        "list_shares", "get_share_details", "list_recipients",
        "check_deletion_vectors",
        # v0.5.0
        "validate_databricks_privileges", "list_unsupported_share_assets",
    }:
        return handler(arguments, workspace_client)
    # Handler that needs the BDC SDK client
    if name == "cleanup_orphaned_data_product":
        return handler(arguments, bdc_client)
    # Pure-logic handlers (validate_tenant_hostname, diagnose_share_error,
    # validate_ord_metadata)
    return handler(arguments)
