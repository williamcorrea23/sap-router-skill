"""SAP Business Data Cloud MCP Server implementation."""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from sap_bdc_mcp.extended_tools import (
    EXTENDED_TOOL_SCHEMAS,
    dispatch_extended,
)

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    logging.info(f"Loaded environment from {env_path}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sap-bdc-mcp")

# Initialize MCP server
app = Server("sap-bdc-mcp-server")


class BDCClientManager:
    """Manages SAP BDC Connect SDK client instances."""

    def __init__(self):
        self._client = None
        self._databricks_client = None
        self._workspace_client = None

    def initialize(
        self,
        recipient_name: str = None,
        databricks_utils: Any = None,
        workspace_url: str = None,
        api_token: str = None,
    ):
        """Initialize the BDC clients.

        Args:
            recipient_name: Name of the Databricks recipient
            databricks_utils: Databricks utilities object (dbutils) - for notebook environments
            workspace_url: Databricks workspace URL - for local development
            api_token: Databricks API token - for local development

        Note:
            Either provide databricks_utils (for notebook) OR workspace_url + api_token (for local).
        """
        try:
            from bdc_connect_sdk.auth import BdcConnectClient, DatabricksClient
            from sap_bdc_mcp.local_client import LocalDatabricksClient

            # Determine which client to use
            if databricks_utils is not None:
                # Running in Databricks notebook
                logger.info("Initializing with Databricks notebook utilities")
                self._databricks_client = DatabricksClient(
                    dbutils=databricks_utils,
                    recipient_name=recipient_name
                )
            elif workspace_url and api_token:
                # Running in local development mode
                logger.info("Initializing with local credentials")
                self._databricks_client = LocalDatabricksClient(
                    workspace_url=workspace_url,
                    api_token=api_token,
                    recipient_name=recipient_name
                )
            else:
                # Try to initialize from environment variables
                logger.info("Initializing from environment variables")
                self._databricks_client = LocalDatabricksClient.from_env()

            # Initialize BDC Connect client
            self._client = BdcConnectClient(self._databricks_client)

            # Initialize Databricks workspace client for share management
            try:
                from databricks.sdk import WorkspaceClient
                self._workspace_client = WorkspaceClient()
                logger.info("Databricks workspace client initialized")
            except Exception as e:
                logger.warning(f"Could not initialize Databricks workspace client: {e}")

            logger.info("SAP BDC clients initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize BDC clients: {e}")
            raise

    @property
    def client(self):
        """Get the BDC Connect client."""
        if self._client is None:
            raise RuntimeError("BDC client not initialized. Call initialize() first.")
        return self._client

    @property
    def workspace_client(self):
        """Get the Databricks workspace client."""
        if self._workspace_client is None:
            raise RuntimeError("Databricks workspace client not initialized.")
        return self._workspace_client

    @property
    def recipient_name(self):
        """Get the configured recipient name."""
        if self._databricks_client is None:
            raise RuntimeError("Databricks client not initialized.")
        return self._databricks_client.recipient_name


# Global client manager
client_manager = BDCClientManager()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available SAP BDC tools."""
    base_tools = _base_tools()
    extended = [Tool(**schema) for schema in EXTENDED_TOOL_SCHEMAS]
    return base_tools + extended


def _base_tools() -> list[Tool]:
    return [
        Tool(
            name="create_or_update_share",
            description="Create or update a share for data distribution in SAP BDC. "
                       "Shares enable secure data sharing using Delta Sharing protocol.",
            inputSchema={
                "type": "object",
                "properties": {
                    "share_name": {
                        "type": "string",
                        "description": "Name of the share to create or update"
                    },
                    "ord_metadata": {
                        "type": "object",
                        "description": "ORD (Open Resource Discovery) metadata for the share"
                    },
                    "tables": {
                        "type": "array",
                        "description": "List of table names to include in the share",
                        "items": {"type": "string"}
                    },
                    "skip_validation": {
                        "type": "boolean",
                        "description": "v0.5.0+ — bypass the ORD pre-flight validation. Default false."
                    }
                },
                "required": ["share_name"]
            }
        ),
        Tool(
            name="create_or_update_share_csn",
            description="Create or update a share using CSN (Common Semantic Notation) format. "
                       "CSN provides a standardized way to describe data schemas.",
            inputSchema={
                "type": "object",
                "properties": {
                    "share_name": {
                        "type": "string",
                        "description": "Name of the share"
                    },
                    "csn_schema": {
                        "type": "object",
                        "description": "CSN schema definition"
                    }
                },
                "required": ["share_name", "csn_schema"]
            }
        ),
        Tool(
            name="publish_data_product",
            description="Publish a data product to make it available for consumption. "
                       "This makes the shared data discoverable and accessible.",
            inputSchema={
                "type": "object",
                "properties": {
                    "share_name": {
                        "type": "string",
                        "description": "Name of the share to publish"
                    },
                    "data_product_name": {
                        "type": "string",
                        "description": "Name of the data product"
                    }
                },
                "required": ["share_name", "data_product_name"]
            }
        ),
        Tool(
            name="delete_share",
            description="Delete a share and withdraw the shared resources. "
                       "This removes the share and makes the data no longer accessible.",
            inputSchema={
                "type": "object",
                "properties": {
                    "share_name": {
                        "type": "string",
                        "description": "Name of the share to delete"
                    }
                },
                "required": ["share_name"]
            }
        ),
        Tool(
            name="generate_csn_template",
            description="Generate a CSN template from an existing Databricks share. "
                       "This utility creates a CSN schema that can be modified as needed.",
            inputSchema={
                "type": "object",
                "properties": {
                    "share_name": {
                        "type": "string",
                        "description": "Name of the Databricks share"
                    }
                },
                "required": ["share_name"]
            }
        ),
        Tool(
            name="provision_share",
            description="End-to-end share provisioning: creates Databricks share, grants to recipient, "
                       "and registers with SAP BDC. This orchestrates the complete workflow in one operation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "share_name": {
                        "type": "string",
                        "description": "Name of the share to create"
                    },
                    "tables": {
                        "type": "array",
                        "description": "List of tables to include (format: catalog.schema.table or schema.table)",
                        "items": {"type": "string"}
                    },
                    "ord_metadata": {
                        "type": "object",
                        "description": "ORD metadata for the share (title, description, version, etc.)",
                        "properties": {
                            "title": {"type": "string"},
                            "shortDescription": {"type": "string"},
                            "description": {"type": "string"},
                            "version": {"type": "string"},
                            "releaseStatus": {"type": "string"},
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    },
                    "comment": {
                        "type": "string",
                        "description": "Optional comment for the Databricks share"
                    },
                    "auto_grant": {
                        "type": "boolean",
                        "description": "Automatically grant share to configured recipient (default: true)"
                    },
                    "skip_if_exists": {
                        "type": "boolean",
                        "description": "Skip Databricks share creation if it already exists (default: true)"
                    }
                },
                "required": ["share_name", "tables", "ord_metadata"]
            }
        ),
        Tool(
            name="validate_share_readiness",
            description="Validate that a Databricks share is ready for BDC Connect operations. "
                       "Checks: share exists, has tables, granted to recipient, and provides actionable guidance.",
            inputSchema={
                "type": "object",
                "properties": {
                    "share_name": {
                        "type": "string",
                        "description": "Name of the share to validate"
                    },
                    "check_bdc_registration": {
                        "type": "boolean",
                        "description": "Also check if share is already registered with BDC (default: false)"
                    }
                },
                "required": ["share_name"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool execution requests."""
    try:
        client = client_manager.client

        # Try extended tools first (v0.3.0+): list_shares, diagnose_share_error, etc.
        try:
            extended_result = dispatch_extended(
                name,
                arguments,
                bdc_client=client,
                workspace_client=client_manager._workspace_client,
            )
        except Exception as e:
            logger.error(f"Extended tool '{name}' raised: {e}")
            extended_result = f"❌ Extended tool '{name}' failed: {e}"

        if extended_result is not None:
            return [TextContent(type="text", text=extended_result)]

        if name == "create_or_update_share":
            share_name = arguments["share_name"]
            ord_metadata = arguments.get("ord_metadata", {})
            tables = arguments.get("tables", [])
            skip_validation = bool(arguments.get("skip_validation", False))

            # v0.5.0 — pre-flight ORD validation (skippable)
            if not skip_validation:
                from sap_bdc_mcp.extended_tools import handle_validate_ord_metadata
                # ord_metadata may be the inner ORD object OR the wrapped {"@openResourceDiscoveryV1": {...}}
                _validation_payload = ord_metadata if isinstance(ord_metadata, dict) else {}
                _validation = json.loads(
                    handle_validate_ord_metadata({"ord": _validation_payload})
                )
                if not _validation.get("valid", False):
                    return [TextContent(
                        type="text",
                        text=(
                            f"❌ Refusing to call create_or_update_share — ORD validation failed.\n"
                            f"Errors:\n  - " + "\n  - ".join(_validation.get("errors", [])) +
                            f"\n\nPass skip_validation=true to bypass."
                        )
                    )]

            result = client.create_or_update_share(
                share_name=share_name,
                ord_metadata=ord_metadata,
                tables=tables
            )

            return [TextContent(
                type="text",
                text=f"Successfully created/updated share '{share_name}'.\n"
                     f"Result: {json.dumps(result, indent=2)}"
            )]

        elif name == "create_or_update_share_csn":
            share_name = arguments["share_name"]
            csn_schema = arguments["csn_schema"]

            result = client.create_or_update_share_csn(
                share_name=share_name,
                csn_schema=csn_schema
            )

            return [TextContent(
                type="text",
                text=f"Successfully created/updated share '{share_name}' with CSN schema.\n"
                     f"Result: {json.dumps(result, indent=2)}"
            )]

        elif name == "publish_data_product":
            share_name = arguments["share_name"]
            data_product_name = arguments["data_product_name"]

            result = client.publish_data_product(
                share_name=share_name,
                data_product_name=data_product_name
            )

            return [TextContent(
                type="text",
                text=f"Successfully published data product '{data_product_name}' "
                     f"from share '{share_name}'.\n"
                     f"Result: {json.dumps(result, indent=2)}"
            )]

        elif name == "delete_share":
            share_name = arguments["share_name"]

            result = client.delete_share(share_name=share_name)

            return [TextContent(
                type="text",
                text=f"Successfully deleted share '{share_name}'.\n"
                     f"Result: {json.dumps(result, indent=2)}"
            )]

        elif name == "generate_csn_template":
            share_name = arguments["share_name"]

            from bdc_connect_sdk.utils import csn_generator

            csn_template = csn_generator.generate_csn_from_share(share_name)

            return [TextContent(
                type="text",
                text=f"Generated CSN template for share '{share_name}':\n"
                     f"{json.dumps(csn_template, indent=2)}"
            )]

        elif name == "provision_share":
            share_name = arguments["share_name"]
            tables = arguments["tables"]
            ord_metadata = arguments["ord_metadata"]
            comment = arguments.get("comment", f"Share created for BDC Connect")
            auto_grant = arguments.get("auto_grant", True)
            skip_if_exists = arguments.get("skip_if_exists", True)

            # Get workspace client and recipient name
            w = client_manager.workspace_client
            recipient_name = client_manager.recipient_name

            steps_completed = []
            errors = []

            # Step 1: Create Databricks share
            try:
                logger.info(f"Step 1: Creating Databricks share '{share_name}'")
                try:
                    w.shares.create(name=share_name, comment=comment)
                    steps_completed.append(f"✅ Created Databricks share '{share_name}'")
                    logger.info(f"Share '{share_name}' created")
                except Exception as e:
                    if "already exists" in str(e).lower() and skip_if_exists:
                        steps_completed.append(f"ℹ️ Share '{share_name}' already exists (skipped creation)")
                        logger.info(f"Share '{share_name}' already exists, skipping creation")
                    else:
                        raise
            except Exception as e:
                error_msg = f"❌ Failed to create Databricks share: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
                return [TextContent(
                    type="text",
                    text=f"Provision failed at Step 1 (Create Databricks share):\n{error_msg}"
                )]

            # Step 2: Add tables to share
            try:
                logger.info(f"Step 2: Adding {len(tables)} tables to share")
                for table in tables:
                    try:
                        w.shares.update(name=share_name, updates=[{
                            "action": "ADD",
                            "data_object": {"name": table, "data_object_type": "TABLE"}
                        }])
                        steps_completed.append(f"  ✅ Added table: {table}")
                        logger.info(f"Added table {table} to share")
                    except Exception as e:
                        if "already exists" in str(e).lower():
                            steps_completed.append(f"  ℹ️ Table {table} already in share")
                        else:
                            raise
                steps_completed.append(f"✅ Added {len(tables)} tables to share")
            except Exception as e:
                error_msg = f"❌ Failed to add tables to share: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
                return [TextContent(
                    type="text",
                    text=f"Provision failed at Step 2 (Add tables):\n{error_msg}\n\n"
                         f"Steps completed:\n" + "\n".join(steps_completed)
                )]

            # Step 3: Grant share to recipient
            if auto_grant:
                try:
                    logger.info(f"Step 3: Granting share to recipient '{recipient_name}'")
                    warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")

                    if not warehouse_id:
                        error_msg = "❌ DATABRICKS_WAREHOUSE_ID not set in environment. Cannot execute GRANT SQL."
                        errors.append(error_msg)
                        logger.error(error_msg)
                        return [TextContent(
                            type="text",
                            text=f"Provision failed at Step 3 (Grant to recipient):\n{error_msg}\n\n"
                                 f"Steps completed:\n" + "\n".join(steps_completed) + "\n\n"
                                 f"Manual step required:\n"
                                 f"  Run: GRANT SELECT ON SHARE {share_name} TO RECIPIENT `{recipient_name}`"
                        )]

                    grant_sql = f"GRANT SELECT ON SHARE {share_name} TO RECIPIENT `{recipient_name}`"

                    try:
                        w.statement_execution.execute_statement(
                            warehouse_id=warehouse_id,
                            statement=grant_sql,
                            wait_timeout="30s"
                        )
                        steps_completed.append(f"✅ Granted share to recipient '{recipient_name}'")
                        logger.info(f"Share granted to recipient")
                    except Exception as e:
                        if "already granted" in str(e).lower():
                            steps_completed.append(f"ℹ️ Share already granted to recipient '{recipient_name}'")
                        else:
                            raise
                except Exception as e:
                    error_msg = f"❌ Failed to grant share to recipient: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    return [TextContent(
                        type="text",
                        text=f"Provision failed at Step 3 (Grant to recipient):\n{error_msg}\n\n"
                             f"Steps completed:\n" + "\n".join(steps_completed) + "\n\n"
                             f"Manual step required:\n"
                             f"  Run: GRANT SELECT ON SHARE {share_name} TO RECIPIENT `{recipient_name}`"
                    )]

            # Step 4: Register with SAP BDC
            try:
                logger.info(f"Step 4: Registering share with SAP BDC")
                request_body = {
                    "ord": ord_metadata,
                    "objects": []
                }

                result = client.create_or_update_share(
                    share_name=share_name,
                    body=request_body
                )

                steps_completed.append(f"✅ Registered with SAP BDC")
                logger.info(f"Share registered with SAP BDC")

                # Format result
                if hasattr(result, '__dict__'):
                    result_dict = {k: v for k, v in result.__dict__.items() if not k.startswith('_')}
                    result_text = json.dumps(result_dict, indent=2, default=str)
                else:
                    result_text = str(result)

                return [TextContent(
                    type="text",
                    text=f"✅ Share '{share_name}' provisioned successfully!\n\n"
                         f"Steps completed:\n" + "\n".join(steps_completed) + "\n\n"
                         f"SAP BDC Registration Result:\n{result_text}"
                )]

            except Exception as e:
                error_msg = f"❌ Failed to register with SAP BDC: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
                return [TextContent(
                    type="text",
                    text=f"Provision failed at Step 4 (Register with SAP BDC):\n{error_msg}\n\n"
                         f"Steps completed:\n" + "\n".join(steps_completed) + "\n\n"
                         f"The Databricks share is ready. You can manually register it with:\n"
                         f"  create_or_update_share(share_name='{share_name}', ord_metadata=...)"
                )]

        elif name == "validate_share_readiness":
            share_name = arguments["share_name"]
            check_bdc = arguments.get("check_bdc_registration", False)

            w = client_manager.workspace_client
            recipient_name = client_manager.recipient_name

            validation_results = {
                "share_name": share_name,
                "ready_for_bdc": True,
                "checks": {},
                "warnings": [],
                "errors": [],
                "next_steps": []
            }

            # Check 1: Does the share exist?
            logger.info(f"Validating share '{share_name}' readiness...")
            try:
                share_info = w.shares.get(share_name)
                validation_results["checks"]["share_exists"] = {
                    "status": "✅ PASS",
                    "message": f"Share '{share_name}' exists in Databricks"
                }
                logger.info("Share exists")
            except Exception as e:
                validation_results["ready_for_bdc"] = False
                validation_results["checks"]["share_exists"] = {
                    "status": "❌ FAIL",
                    "message": f"Share '{share_name}' does not exist",
                    "error": str(e)
                }
                validation_results["errors"].append(
                    f"Share '{share_name}' not found in Databricks"
                )
                validation_results["next_steps"].append(
                    f"Create the share: w.shares.create(name='{share_name}')"
                )

                return [TextContent(
                    type="text",
                    text=f"❌ Validation Failed\n\n"
                         f"{json.dumps(validation_results, indent=2)}"
                )]

            # Check 2: Does the share have any objects?
            try:
                share_details = w.shares.get(share_name)
                objects = share_details.objects if hasattr(share_details, 'objects') else []

                if objects and len(objects) > 0:
                    validation_results["checks"]["has_objects"] = {
                        "status": "✅ PASS",
                        "message": f"Share has {len(objects)} object(s)",
                        "objects": [obj.name for obj in objects] if objects else []
                    }
                    logger.info(f"Share has {len(objects)} objects")
                else:
                    validation_results["ready_for_bdc"] = False
                    validation_results["checks"]["has_objects"] = {
                        "status": "❌ FAIL",
                        "message": "Share has no tables or objects"
                    }
                    validation_results["errors"].append("Share is empty - no tables added")
                    validation_results["next_steps"].append(
                        f"Add tables: w.shares.update(name='{share_name}', updates=[{{'action': 'ADD', 'data_object': {{'name': 'catalog.schema.table', 'data_object_type': 'TABLE'}}}}])"
                    )
            except Exception as e:
                validation_results["warnings"].append(f"Could not check share objects: {str(e)}")
                validation_results["checks"]["has_objects"] = {
                    "status": "⚠️ WARNING",
                    "message": "Could not verify share contents",
                    "error": str(e)
                }

            # Check 3: Is the share granted to the recipient?
            try:
                warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")

                if warehouse_id:
                    grants_sql = f"SHOW GRANTS ON SHARE {share_name}"
                    grants_result = w.statement_execution.execute_statement(
                        warehouse_id=warehouse_id,
                        statement=grants_sql,
                        wait_timeout="30s"
                    )

                    # Check if recipient is in the grants
                    granted_to_recipient = False
                    grants_list = []

                    if grants_result.result and grants_result.result.data_array:
                        for row in grants_result.result.data_array:
                            # Row format: [principal, action_type, object_type, details]
                            if row and len(row) > 0:
                                principal = str(row[0])
                                grants_list.append(principal)
                                if recipient_name in principal:
                                    granted_to_recipient = True

                    if granted_to_recipient:
                        validation_results["checks"]["granted_to_recipient"] = {
                            "status": "✅ PASS",
                            "message": f"Share is granted to recipient '{recipient_name}'",
                            "all_grants": grants_list
                        }
                        logger.info("Share is granted to recipient")
                    else:
                        validation_results["ready_for_bdc"] = False
                        validation_results["checks"]["granted_to_recipient"] = {
                            "status": "❌ FAIL",
                            "message": f"Share is NOT granted to recipient '{recipient_name}'",
                            "current_grants": grants_list
                        }
                        validation_results["errors"].append(
                            f"Share not granted to BDC Connect recipient '{recipient_name}'"
                        )
                        validation_results["next_steps"].append(
                            f"Grant share: GRANT SELECT ON SHARE {share_name} TO RECIPIENT `{recipient_name}`"
                        )
                else:
                    validation_results["warnings"].append(
                        "DATABRICKS_WAREHOUSE_ID not set - cannot verify grants"
                    )
                    validation_results["checks"]["granted_to_recipient"] = {
                        "status": "⚠️ WARNING",
                        "message": "Could not verify grants (no warehouse configured)"
                    }
                    validation_results["next_steps"].append(
                        "Set DATABRICKS_WAREHOUSE_ID to enable grant verification"
                    )

            except Exception as e:
                validation_results["warnings"].append(f"Could not check grants: {str(e)}")
                validation_results["checks"]["granted_to_recipient"] = {
                    "status": "⚠️ WARNING",
                    "message": "Could not verify grants",
                    "error": str(e)
                }
                validation_results["next_steps"].append(
                    f"Manually verify: SHOW GRANTS ON SHARE {share_name}"
                )

            # Check 4: BDC registration (optional)
            if check_bdc:
                try:
                    # Try to get share info from BDC - this will fail if not registered
                    # Note: The SDK doesn't have a direct "get share" method, so we'd need to
                    # try creating/updating and see if it's already there
                    validation_results["checks"]["bdc_registered"] = {
                        "status": "ℹ️ INFO",
                        "message": "BDC registration check requires attempting registration"
                    }
                    validation_results["warnings"].append(
                        "BDC registration status cannot be checked without attempting registration"
                    )
                except Exception as e:
                    validation_results["checks"]["bdc_registered"] = {
                        "status": "⚠️ WARNING",
                        "message": "Could not check BDC registration",
                        "error": str(e)
                    }

            # Final verdict
            if validation_results["ready_for_bdc"]:
                summary = f"✅ Share '{share_name}' is READY for BDC Connect registration!\n\n"
                summary += "All checks passed:\n"
                for check_name, check_result in validation_results["checks"].items():
                    summary += f"  {check_result['status']} {check_result['message']}\n"

                if validation_results["warnings"]:
                    summary += "\nWarnings:\n"
                    for warning in validation_results["warnings"]:
                        summary += f"  ⚠️ {warning}\n"

                summary += f"\nNext step: Register with BDC using create_or_update_share('{share_name}', ...)"
            else:
                summary = f"❌ Share '{share_name}' is NOT ready for BDC Connect\n\n"
                summary += "Errors found:\n"
                for error in validation_results["errors"]:
                    summary += f"  ❌ {error}\n"

                summary += "\nChecks:\n"
                for check_name, check_result in validation_results["checks"].items():
                    summary += f"  {check_result['status']} {check_result['message']}\n"

                if validation_results["next_steps"]:
                    summary += "\nRequired actions:\n"
                    for i, step in enumerate(validation_results["next_steps"], 1):
                        summary += f"  {i}. {step}\n"

            summary += f"\n\nDetailed Results:\n{json.dumps(validation_results, indent=2)}"

            return [TextContent(
                type="text",
                text=summary
            )]

        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


async def main():
    """Run the MCP server."""
    logger.info("Starting SAP BDC MCP Server...")

    # Initialize the client manager with credentials from environment
    try:
        client_manager.initialize()
        logger.info("BDC client manager initialized successfully")
    except Exception as e:
        logger.warning(f"Could not initialize BDC clients at startup: {e}")
        logger.warning("Clients will need to be initialized before use")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def run():
    """Synchronous entrypoint for the console script (pyproject.toml [project.scripts])."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
