/**
 * INTENT FACADE handlers: SAPRead, SAPWrite, SAPSearch, SAPDiagnose
 *
 * A small set of consolidated "verb" tools that delegate to the existing
 * granular handlers via an `operation` discriminator. Clients that don't use
 * deferred loading see only ~4 schemas instead of 50, cutting the schema-token
 * footprint dramatically while the full granular tools remain available behind
 * find_tools for power use. No business logic lives here — it is pure routing,
 * so behaviour (safety guards, audit, locking) is inherited from the delegate.
 */

import type { ADTClient } from "abap-adt-api";
import type { ToolResult } from "../../types.js";
import { S_IntentRead, S_IntentWrite, S_IntentSearch, S_IntentDiagnose } from "../../schemas.js";
import { HANDLER_MAP } from "../handler-map.js";

function err(text: string): ToolResult { return { content: [{ type: "text", text }], isError: true }; }

/** operation → concrete granular tool name, per facade. */
const READ_OPS: Record<string, string> = {
  source: "read_abap_source",
  method: "read_abap_method",
  contract: "get_abap_contract",
  info: "get_object_info",
  where_used: "where_used",
  table: "get_table_contents",
  table_fields: "get_table_fields",
  ddic: "get_ddic_element",
  revisions: "get_revisions",
  context: "analyze_abap_context",
};
const WRITE_OPS: Record<string, string> = {
  source: "write_abap_source",
  method: "edit_abap_method",
  activate: "activate_abap_object",
  pretty_print: "pretty_print",
  create_program: "create_abap_program",
  create_class: "create_abap_class",
  create_interface: "create_abap_interface",
  create_function_group: "create_function_group",
  create_cds_view: "create_cds_view",
  create_table: "create_database_table",
  create_message_class: "create_message_class",
  create_metadata_extension: "create_cds_metadata_extension",
  create_service_definition: "create_service_definition",
  create_service_binding: "create_service_binding",
  publish_service_binding: "publish_service_binding",
  create_dcl: "create_data_control_language",
  create_bdef: "create_behavior_definition",
  create_package: "create_package",
  delete: "delete_abap_object",
};
const SEARCH_OPS: Record<string, string> = {
  objects: "search_abap_objects",
  source: "search_source_code",
  call_graph: "get_call_graph",
  dead_code: "find_dead_code",
};
const DIAGNOSE_OPS: Record<string, string> = {
  syntax: "run_syntax_check",
  atc: "run_atc_check",
  unit: "run_unit_tests",
  ddic_validate: "validate_ddic_references",
  clean_abap: "review_clean_abap",
  dumps: "get_short_dumps",
  dump_detail: "get_short_dump_detail",
  traces: "get_traces",
  trace_detail: "get_trace_detail",
  workflow: "analyze_workflow",
};

async function dispatch(
  client: ADTClient,
  map: Record<string, string>,
  operation: string,
  args: Record<string, unknown>,
  extra: any,
): Promise<ToolResult> {
  const target = map[operation];
  if (!target) {
    return err(`Unknown operation '${operation}'. Available: ${Object.keys(map).join(", ")}`);
  }
  const handler = HANDLER_MAP.get(target);
  if (!handler) return err(`Internal error: no handler registered for '${target}'.`);
  return handler(client, args ?? {}, extra);
}

export async function handleSapRead(client: ADTClient, args: Record<string, unknown>, extra?: any): Promise<ToolResult> {
  const p = S_IntentRead.parse(args);
  return dispatch(client, READ_OPS, p.operation, p.args ?? {}, extra);
}
export async function handleSapWrite(client: ADTClient, args: Record<string, unknown>, extra?: any): Promise<ToolResult> {
  const p = S_IntentWrite.parse(args);
  return dispatch(client, WRITE_OPS, p.operation, p.args ?? {}, extra);
}
export async function handleSapSearch(client: ADTClient, args: Record<string, unknown>, extra?: any): Promise<ToolResult> {
  const p = S_IntentSearch.parse(args);
  return dispatch(client, SEARCH_OPS, p.operation, p.args ?? {}, extra);
}
export async function handleSapDiagnose(client: ADTClient, args: Record<string, unknown>, extra?: any): Promise<ToolResult> {
  const p = S_IntentDiagnose.parse(args);
  return dispatch(client, DIAGNOSE_OPS, p.operation, p.args ?? {}, extra);
}
