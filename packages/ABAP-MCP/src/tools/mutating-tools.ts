/**
 * Single source of truth for which tools mutate the SAP system.
 *
 * - `handler-map.ts` wraps AUDIT_WRAPPED_TOOLS with the audit decorator.
 * - `batch.ts` blocks every mutating tool from batch_read (read-only contract).
 *
 * Lives in its own module (not handler-map.ts) because batch.ts and
 * handler-map.ts import each other; a module-level constant shared between
 * them must come from outside that cycle.
 */

import type { AuditEvent } from "../audit.js";

/** Mutating tools audited centrally by the withAudit wrapper in handler-map. */
export const AUDIT_WRAPPED_TOOLS: ReadonlyArray<[string, AuditEvent["action"]]> = [
  ["activate_abap_object",          "write"],
  ["mass_activate",                 "write"],
  ["create_abap_program",           "write"],
  ["create_abap_class",             "write"],
  ["create_abap_interface",         "write"],
  ["create_function_group",         "write"],
  ["create_cds_view",               "write"],
  ["create_database_table",         "write"],
  ["create_message_class",          "write"],
  ["create_cds_metadata_extension", "write"],
  ["create_service_definition",     "write"],
  ["create_service_binding",        "write"],
  ["publish_service_binding",       "write"],
  ["create_data_control_language",  "write"],
  ["create_behavior_definition",    "write"],
  ["create_package",                "write"],
  ["create_test_include",           "write"],
  ["create_transport",              "write"],
  ["abapgit_pull",                  "write"],
  ["execute_abap_snippet",          "execute"],
];

/** Mutating tools that audit inside their own handlers (per-phase detail). */
export const SELF_AUDITED_TOOLS: ReadonlyArray<string> = [
  "write_abap_source",
  "edit_abap_method",
  "delete_abap_object",
];

/** Every tool that can change SAP system state, incl. the SAPWrite facade. */
export const MUTATING_TOOL_NAMES: ReadonlySet<string> = new Set([
  ...AUDIT_WRAPPED_TOOLS.map(([name]) => name),
  ...SELF_AUDITED_TOOLS,
  "SAPWrite",
]);
