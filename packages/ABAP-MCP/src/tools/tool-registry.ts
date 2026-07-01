/**
 * ABAP MCP Server — Tool Registry
 * Categories, core tools, deferred tool loading, and short descriptions.
 */

import { TOOLS } from "./tool-definitions.js";
import { S_FindTools, S_ListTools } from "../schemas.js";

export const TOOL_CATEGORIES: Record<string, string[]> = {
  SEARCH:      ["search_abap_objects", "search_source_code"],
  READ:        ["read_abap_source", "read_abap_method", "get_abap_contract", "get_object_info",
                "where_used", "get_code_completion",
                "find_definition", "get_revisions", "get_ddic_element", "get_table_fields",
                "get_table_contents", "get_fix_proposals", "analyze_abap_context"],
  WRITE:       ["write_abap_source", "edit_abap_method", "activate_abap_object", "mass_activate", "pretty_print"],
  CREATE:      ["create_abap_program", "create_abap_class", "create_abap_interface",
                "create_function_group", "create_cds_view", "create_database_table",
                "create_message_class", "create_cds_metadata_extension",
                "create_service_definition", "create_service_binding",
                "publish_service_binding", "create_data_control_language",
                "create_behavior_definition", "create_package"],
  DELETE:      ["delete_abap_object"],
  TEST:        ["run_unit_tests", "create_test_include"],
  QUALITY:     ["run_syntax_check", "run_atc_check", "validate_ddic_references", "review_clean_abap"],
  DIAGNOSTICS: ["get_short_dumps", "get_short_dump_detail", "get_traces", "get_trace_detail"],
  TRANSPORT:   ["get_transport_info", "get_transport_objects", "create_transport"],
  ABAPGIT:     ["get_abapgit_repos", "abapgit_pull"],
  QUERY:       ["analyze_workflow", "run_select_query", "get_inactive_objects", "execute_abap_snippet"],
  DOCUMENTATION: ["get_abap_keyword_doc", "get_abap_class_doc", "get_module_best_practices", "search_abap_syntax", "search_clean_abap"],
  WEBSEARCH:   ["fetch_url", "search_sap_web"],
  BATCH:       ["batch_read"],
  ANALYSIS:    ["get_call_graph", "find_dead_code"],
  INTENT:      ["SAPRead", "SAPWrite", "SAPSearch", "SAPDiagnose"],
};

export const CORE_TOOL_NAMES = new Set([
  "find_tools",
  "list_tools",
  "analyze_abap_context",
  "search_abap_syntax",       // mandatory in abap_develop Step 5.1
  "validate_ddic_references", // mandatory in abap_develop Step 5.3
  "batch_read",               // performance: always available for parallel reads
  "fetch_url",                // URL content extraction — read any web page (SPA-compatible)
  "search_sap_web",           // web search for SAP Help, Community & Notes — used in abap_develop Steps 2 & 5
  "get_abap_contract",        // context compression — cheap API-surface reads of dependencies
  // Intent facade: consolidated verbs always available so clients can use a
  // small tool surface instead of discovering 50 granular tools.
  "SAPRead",
  "SAPWrite",
  "SAPSearch",
  "SAPDiagnose",
]);

export const enabledTools = new Set<string>();

export const FIND_TOOLS_ENTRY = {
  name: "find_tools",
  description: "Finds and enables ABAP tools by search term or category. " +
    "⚠️ Most tools are deferred — call this BEFORE using any non-core tool! " +
    "Categories: SEARCH, READ, WRITE, CREATE (programs, classes, interfaces, function groups, CDS views, tables, " +
    "message classes, CDS metadata extensions, service definitions, service bindings, data control language), " +
    "DELETE, TEST, QUALITY (syntax check, ATC, Clean ABAP review, DDIC validation), " +
    "DIAGNOSTICS (short dumps, traces), TRANSPORT, ABAPGIT, QUERY, " +
    "DOCUMENTATION (ABAP syntax help), WEBSEARCH (Google SAP web search), BATCH (parallel read operations), " +
    "ANALYSIS (call graph, dead-code detection), INTENT (consolidated SAPRead/SAPWrite/SAPSearch/SAPDiagnose verbs). " +
    "Enabled tools become immediately available.",
  schema: S_FindTools,
  requiresAdt: false,
};

export const LIST_TOOLS_ENTRY = {
  name: "list_tools",
  description:
    "Returns a compact overview of ALL 50+ available tools with short descriptions, grouped by category. " +
    "Shows which tools are currently active (core/enabled) vs. deferred. " +
    "Use this to discover the right tool for a task. Unlike find_tools, this does NOT enable tools — it only lists them.",
  schema: S_ListTools,
  requiresAdt: false,
};

export const TOOL_SHORT_DESCRIPTIONS: Record<string, string> = {
  search_abap_objects:    "Search objects by name pattern (wildcard *)",
  search_source_code:    "Full-text search across all ABAP source code",
  read_abap_source:      "Read source code (with includeRelated for full context)",
  read_abap_method:      "Read a single method block (token-efficient)",
  get_abap_contract:     "Compressed public interface of a class/interface (no bodies)",
  get_object_info:       "Read metadata/structure of an object",
  where_used:            "Find all usages of an object in the system",
  get_code_completion:   "Code completion suggestions for a cursor position",
  find_definition:       "Navigate to the definition of a token in source",
  get_revisions:         "Version history of an object (date, author, transport)",
  get_ddic_element:      "DDIC info for table/view/data element/domain",
  get_table_fields:      "Field catalog of a table (name, type, key, length, description)",
  get_table_contents:    "Read table contents directly as JSON",
  get_fix_proposals:     "Quick-fix proposals for a source position",
  analyze_abap_context:  "Deep context analysis: source + includes + references",
  write_abap_source:     "Write source & activate (lock→write→check→activate→unlock)",
  edit_abap_method:      "Rewrite a single method body & activate (cheap one-method edit)",
  activate_abap_object:  "Activate a saved object",
  mass_activate:         "Activate multiple objects at once",
  pretty_print:          "Format source via SAP Pretty Printer",
  create_abap_program:   "Create new program (report/include)",
  create_abap_class:     "Create new class (ZCL_/YCL_)",
  create_abap_interface: "Create new interface (ZIF_/YIF_)",
  create_function_group: "Create new function group",
  create_cds_view:       "Create new CDS view (DDLS)",
  create_database_table: "Create new transparent table (TABL)",
  create_message_class:             "Create new message class (MSAG)",
  create_cds_metadata_extension:    "Create new CDS Metadata Extension (DDLX) for UI annotations",
  create_service_definition:        "Create new OData Service Definition (SRVD)",
  create_service_binding:           "Create new OData Service Binding (SRVB) → V2_UI, V2_WEB_API, V4_UI or V4_WEB_API",
  publish_service_binding:          "Publish a Service Binding to activate the OData endpoint",
  create_data_control_language:     "Create new CDS Data Control Language source (DCLS) for access control",
  create_behavior_definition:       "Create new RAP Behavior Definition (BDEF) — direct ADT HTTP, BDL via write_abap_source",
  create_package:                   "Create new package (DEVC) — HOME=transportable, LOCAL=non-transportable",
  delete_abap_object:    "Permanently delete an object (⛔ irreversible)",
  run_unit_tests:        "Run ABAP Unit Tests, return results",
  create_test_include:   "Create test include (CCAU) for a class",
  run_syntax_check:      "Syntax check without saving",
  run_atc_check:         "ATC check (code quality findings)",
  validate_ddic_references: "Check field references against DDIC before writing",
  review_clean_abap:     "Static Clean ABAP compliance review",
  get_short_dumps:       "List latest short dumps (ST22)",
  get_short_dump_detail: "Details of a specific short dump",
  get_traces:            "List performance traces (SAT)",
  get_trace_detail:      "Details of a specific trace",
  get_transport_info:    "Available transports for an object/package",
  get_transport_objects:  "List objects in a transport request",
  create_transport:      "Create a new transport request",
  get_abapgit_repos:     "List abapGit repositories in the system",
  abapgit_pull:          "Pull from Git into SAP (abapGit)",
  analyze_workflow:      "Analyze SAP Business Workflow: definitions, instances, steps, agents",
  run_select_query:      "Execute SELECT on SAP tables (read-only)",
  execute_abap_snippet:  "Run temporary ABAP code snippet (auto-deleted)",
  get_inactive_objects:   "List inactive objects of current user",
  get_abap_keyword_doc:  "ABAP keyword docs from help.sap.com",
  get_abap_class_doc:    "ABAP class/interface docs from help.sap.com",
  get_module_best_practices: "Module-specific SAP best practices (FI, MM, SD…)",
  search_clean_abap:     "Search Clean ABAP Styleguide for best practices",
  search_abap_syntax:    "Search ABAP syntax docs from help.sap.com",
  fetch_url:             "Fetch & extract readable content from any URL (SPA-compatible)",
  search_sap_web:        "Web search across SAP Help, Community & Notes (Google CSE)",
  batch_read:            "Execute multiple read-only tools in one parallel MCP call",
  get_call_graph:        "Where-used dependency graph (Mermaid) for impact analysis",
  find_dead_code:        "Flag objects with no inbound usages (removal candidates)",
  SAPRead:               "Consolidated READ verb (source/method/contract/info/…)",
  SAPWrite:              "Consolidated WRITE verb (source/method/create/delete/…)",
  SAPSearch:             "Consolidated SEARCH verb (objects/source/call_graph/dead_code)",
  SAPDiagnose:           "Consolidated QUALITY/DIAGNOSTICS verb (syntax/atc/unit/…)",
  find_tools:            "Find & enable deferred tools by category/query",
  list_tools:            "Compact overview of ALL available tools & status",
};

// Build combined tool list (TOOLS + find_tools + list_tools)
export const ALL_TOOLS = [...TOOLS, FIND_TOOLS_ENTRY, LIST_TOOLS_ENTRY];

// Tools flagged `requiresAdt: false` in their definition never touch the SAP
// system; the server skips the ADT connection for them. Derived from the tool
// definitions so the flag lives next to each tool and the set cannot drift.
export const NO_ADT_TOOL_NAMES: ReadonlySet<string> = new Set(
  ALL_TOOLS.filter((t) => t.requiresAdt === false).map((t) => t.name),
);
