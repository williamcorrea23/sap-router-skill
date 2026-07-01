/**
 * ABAP MCP Server — Zod Schemas
 * Parameter validation for all MCP tools.
 */

import { z } from "zod";

// --- SEARCH ---
export const S_Search = z.object({
  query:       z.string().describe("Name pattern, wildcards * supported, e.g. 'ZCL_*SERVICE*'"),
  maxResults:  z.number().int().min(1).max(100).default(20).optional(),
  objectType:  z.string().optional().describe(
    "ADT type, e.g. PROG/P | CLAS/OC | FUGR/F | INTF/OI | DDLS/DF | TABL/DT | DOMA/DE | DTEL/DE | MSAG/E | SICF/SC. Empty = all types."
  ),
});

export const S_SearchSourceCode = z.object({
  searchString: z.string().describe("Text to search for in ABAP source code, e.g. 'Hallo', 'READ TABLE', 'BAPI_USER_GET_DETAIL'"),
  maxResults:   z.number().int().min(1).max(200).default(50).optional()
    .describe("Max results to return (default 50, max 200)"),
});

// --- READ ---
export const S_ReadSource = z.object({
  objectUrl: z.string().describe("ADT URL, e.g. /sap/bc/adt/programs/programs/ztest"),
  includeRelated: z.boolean().default(false).optional().describe(
    "If true, all related objects are automatically read along: " +
    "class includes (definitions, implementations, macros, test classes), " +
    "program includes (INCLUDE statements resolved), function group includes. " +
    "Recommended to understand the full context of an object."
  ),
});
export const S_ObjectInfo = z.object({
  objectUrl: z.string().describe("ADT URL of the object"),
});
export const S_WhereUsed = z.object({
  objectUrl:  z.string().describe("ADT URL of the object to search"),
  maxResults: z.number().int().min(1).max(200).default(50).optional(),
});
export const S_CodeCompletion = z.object({
  objectUrl:   z.string().describe("ADT URL of the object (context for completion)"),
  source:      z.string().describe("Current source code with cursor position"),
  line:        z.number().int().min(1).describe("Cursor line (1-based)"),
  column:      z.number().int().min(0).describe("Cursor column (0-based)"),
});

// --- WRITE ---
export const S_WriteSource = z.object({
  objectUrl:          z.string().describe("ADT URL without /source/main suffix"),
  source:             z.string().optional().describe("Complete ABAP source code — use only for short snippets (< 20 lines). For larger programs, write to a temp file and use 'sourcePath' instead."),
  sourcePath:         z.string().optional().describe("PREFERRED: Path to a local file with the ABAP source. Write source to disk first (e.g. /tmp/zmy_prog.abap), then pass this path. Faster, cheaper, and avoids JSON escaping issues."),
  transport:          z.string().optional().describe("Transport request, e.g. DEVK900123"),
  activateAfterWrite: z.boolean().default(true).optional().describe("Activate after writing (default: true)"),
  skipSyntaxCheck:    z.boolean().default(false).optional().describe("Skip syntax check (not recommended)"),
  mainProgram:        z.string().optional().describe("Main program for syntax check of includes — name (e.g. ZRYBAK_AI_TEST) or ADT URL"),
}).refine(d => !!(d.source ?? d.sourcePath), {
  message: "Either 'source' or 'sourcePath' must be provided",
});
export const S_Activate = z.object({
  objectUrl:  z.string().describe("ADT URL of the object"),
  objectName: z.string().describe("Object name, e.g. ZTEST or ZCL_FOO"),
});
export const S_MassActivate = z.object({
  objects: z.array(z.object({
    objectUrl:  z.string().describe("ADT URL"),
    objectName: z.string().describe("Object name"),
    objectType: z.string().optional().describe("ADT type, e.g. PROG/P, PROG/I, CLAS/OC (optional, derived from URL)"),
  })).describe("List of objects to activate (max. 50)"),
});
export const S_PrettyPrint = z.object({
  source:      z.string().describe("ABAP source code to format"),
  objectUrl:   z.string().optional().describe("ADT URL (for context, optional)"),
});

// --- CREATE ---
export const S_CreateProgram = z.object({
  name:        z.string().min(1).max(30).describe("Program name, must start with Z or Y"),
  description: z.string().max(40).describe("Short description (max 40 characters)"),
  devClass:    z.string().describe("Package, e.g. ZLOCAL or $TMP"),
  transport:   z.string().optional().describe("Transport request (empty for local objects)"),
  programType: z.enum(["P", "I"]).default("P").optional().describe("P = Executable (Report), I = Include (default: P)"),
});
export const S_CreateClass = z.object({
  name:          z.string().min(1).max(30).describe("Class name, must start with ZCL_ or YCL_"),
  description:   z.string().max(40).describe("Short description"),
  devClass:      z.string().describe("Package"),
  transport:     z.string().optional(),
  superClass:    z.string().optional().describe("Super class, e.g. CL_ABAP_UNIT_ASSERT"),
  classCategory: z.enum(["generalObjectType", "behaviorPool"]).default("generalObjectType").optional()
    .describe("Class category: 'generalObjectType' (default) or 'behaviorPool' for RAP behavior pool classes (ZBP_*)"),
});
export const S_CreateInterface = z.object({
  name:        z.string().min(1).max(30).describe("Interface name, must start with ZIF_ or YIF_"),
  description: z.string().max(40).describe("Short description"),
  devClass:    z.string().describe("Package"),
  transport:   z.string().optional(),
});
export const S_CreateFunctionGroup = z.object({
  name:        z.string().min(1).max(26).describe("Function group name, must start with Z or Y"),
  description: z.string().max(40).describe("Short description"),
  devClass:    z.string().describe("Package"),
  transport:   z.string().optional(),
});
export const S_CreateCdsView = z.object({
  name:        z.string().min(1).max(30).describe("CDS name, must start with Z or Y"),
  description: z.string().max(40).describe("Short description"),
  devClass:    z.string().describe("Package"),
  transport:   z.string().optional(),
  source:      z.string().optional().describe("Initial CDS source code (required on some on-premise systems)"),
  sourcePath:  z.string().optional().describe("Path to a local file containing the initial CDS source (alternative to source)"),
}).refine(d => !(d.source && d.sourcePath), { message: "Provide either source or sourcePath, not both" });
export const S_CreateTable = z.object({
  name:        z.string().min(1).max(16).describe("Table name, must start with Z or Y"),
  description: z.string().max(40).describe("Short description"),
  devClass:    z.string().describe("Package"),
  transport:   z.string().optional(),
});
export const S_CreateMessageClass = z.object({
  name:        z.string().min(1).max(20).describe("Message class name, must start with Z or Y"),
  description: z.string().max(40).describe("Short description"),
  devClass:    z.string().describe("Package"),
  transport:   z.string().optional(),
});
export const S_CreateCdsMetadataExtension = z.object({
  name:        z.string().min(1).max(30).describe("Metadata extension name, must start with Z or Y"),
  description: z.string().max(40).describe("Short description"),
  devClass:    z.string().describe("Package"),
  transport:   z.string().optional(),
});
export const S_CreateServiceDefinition = z.object({
  name:        z.string().min(1).max(30).describe("Service definition name, must start with Z or Y"),
  description: z.string().max(40).describe("Short description"),
  devClass:    z.string().describe("Package"),
  transport:   z.string().optional(),
});
export const S_CreateServiceBinding = z.object({
  name:              z.string().min(1).max(26).describe("Service binding name, must start with Z or Y"),
  description:       z.string().max(40).describe("Short description"),
  devClass:          z.string().describe("Package"),
  transport:         z.string().optional(),
  serviceDefinition: z.string().describe("Name of the SRVD service definition to bind, e.g. ZSD_ORDERS_SRV_D"),
  bindingType:       z.enum(["V2_WEB_API", "V2_UI", "V4_WEB_API", "V4_UI"]).default("V2_UI").describe("V2_UI = OData V2 Fiori/SAPUI5; V2_WEB_API = OData V2 external API; V4_UI = OData V4 Fiori/SAPUI5; V4_WEB_API = OData V4 external API"),
});
export const S_PublishServiceBinding = z.object({
  name:    z.string().describe("Service binding name, e.g. ZSD_ORDERS_SRV_B"),
  version: z.string().default("0001").optional().describe("Content version, typically '0001'"),
});
export const S_CreateDataControlLanguage = z.object({
  name:        z.string().min(1).max(30).describe("DCL source name, must start with Z or Y"),
  description: z.string().max(40).describe("Short description"),
  devClass:    z.string().describe("Package"),
  transport:   z.string().optional(),
});
export const S_CreateBehaviorDefinition = z.object({
  name:        z.string().min(1).max(30).describe("BDEF name — must match the root CDS entity name exactly; must start with Z or Y"),
  description: z.string().max(40).describe("Short description"),
  devClass:    z.string().describe("Package"),
  transport:   z.string().optional(),
});
export const S_CreatePackage = z.object({
  name:             z.string().min(1).max(30).describe("Package name (DEVC), must start with Z or Y"),
  description:      z.string().max(60).describe("Short description"),
  softwareComponent: z.string().default("HOME").optional().describe("Software component: 'HOME' for a transportable package, 'LOCAL' for a non-transportable local package (default: HOME)"),
  transportLayer:   z.string().optional().describe("Transport layer for transportable packages (omit for the system default or for LOCAL packages)"),
  superPackage:     z.string().optional().describe("Parent (super) package name, if this should be a sub-package"),
  packageType:      z.string().default("development").optional().describe("Package type: 'development' (default), 'structure', or 'main'"),
  transport:        z.string().optional().describe("Transport request (corrNr) — required when creating a transportable package on systems that demand one"),
});

// --- DELETE ---
export const S_DeleteObject = z.object({
  objectUrl:  z.string().describe("ADT URL of the object to delete"),
  objectName: z.string().describe("Object name (for confirmation)"),
  transport:  z.string().optional().describe("Transport request"),
});

// --- TEST ---
export const S_RunTests = z.object({
  objectUrl: z.string().describe("ADT URL of the class or program"),
});
export const S_CreateTestInclude = z.object({
  classUrl: z.string().describe("ADT URL of the class, e.g. /sap/bc/adt/oo/classes/zcl_foo"),
});

// --- QUALITY ---
export const S_SyntaxCheck = z.object({
  objectUrl:   z.string().describe("ADT URL of the object"),
  source:      z.string().describe("ABAP source code"),
  mainProgram: z.string().optional().describe("Main program (for includes) — name or ADT URL"),
});
export const S_RunAtc = z.object({
  objectUrl:  z.string().describe("ADT URL of the object to check"),
  checkVariant: z.string().default("DEFAULT").optional().describe("ATC check variant (default: DEFAULT)"),
});
export const S_ValidateDdic = z.object({
  source: z.string().describe("ABAP source code to validate program logic for"),
});

// --- DIAGNOSTICS ---
export const S_GetDumps = z.object({
  maxResults: z.number().int().min(1).max(100).default(20).optional()
    .describe("Max dumps to return (default: MAX_DUMPS env, 20)"),
  user:       z.string().optional().describe("Filter by user"),
});
export const S_GetDumpDetail = z.object({
  dumpId: z.string().describe("Dump ID from get_short_dumps"),
});
export const S_GetTraces = z.object({
  maxResults: z.number().int().min(1).max(50).default(10).optional(),
  user:       z.string().optional().describe("Filter by user"),
});
export const S_GetTraceDetail = z.object({
  traceId: z.string().describe("Trace ID from get_traces"),
});

// --- TRANSPORT ---
export const S_TransportInfo = z.object({
  objectUrl: z.string().describe("ADT URL of the object"),
  devClass:  z.string().describe("Package of the object"),
});
export const S_TransportObjects = z.object({
  transportId: z.string().describe("Transport request, e.g. DEVK900123"),
});

// --- ABAPGIT ---
export const S_GitRepos = z.object({
  objectUrl: z.string().optional().describe("System connection URL (empty = active system)"),
});
export const S_GitPull = z.object({
  repoId:    z.string().describe("abapGit repository ID"),
  transport: z.string().optional().describe("Transport request for pull"),
});

// --- QUERY ---
export const S_Query = z.object({
  query: z.string().describe("SELECT statement, e.g. SELECT * FROM T001 UP TO 10 ROWS"),
});
export const S_ExecuteSnippet = z.object({
  source: z.string().describe(
    "Complete executable ABAP code. Must be a valid program — " +
    "starts with REPORT or PROGRAM, ends with a period. " +
    "Output via WRITE statements. No SELECTION-SCREEN."
  ),
});

// --- NEW TOOLS ---
export const S_FindDefinition = z.object({
  objectUrl:   z.string().describe("ADT URL of the source object (context)"),
  source:      z.string().describe("Current source code"),
  line:        z.number().int().min(1).describe("Token line (1-based)"),
  startColumn: z.number().int().min(0).describe("Token start column (0-based)"),
  endColumn:   z.number().int().min(0).describe("Token end column (0-based)"),
  mainProgram: z.string().optional().describe("Main program (for includes)"),
});
export const S_GetRevisions = z.object({
  objectUrl: z.string().describe("ADT URL of the object"),
});
export const S_CreateTransport = z.object({
  objectUrl:      z.string().describe("ADT URL of the object"),
  description:    z.string().max(60).describe("Transport description text"),
  devClass:       z.string().describe("Package"),
  transportLayer: z.string().optional().describe("Transport layer (optional)"),
});
export const S_FixProposals = z.object({
  objectUrl:   z.string().describe("ADT URL of the object"),
  source:      z.string().describe("Current source code"),
  line:        z.number().int().min(1).describe("Error line (1-based)"),
  column:      z.number().int().min(0).describe("Error column (0-based)"),
});
export const S_GetDdicElement = z.object({
  path: z.string().describe("DDIC path, e.g. table name or CDS view name"),
});
export const S_GetInactiveObjects = z.object({});
export const S_GetTableContents = z.object({
  tableName: z.string().describe("Name of the DDIC table"),
  maxRows:   z.number().int().min(1).max(1000).default(100).optional().describe("Max. number of rows (default: 100)"),
});
export const S_GetTableFields = z.object({
  tableName: z.string().describe("Name of the DDIC table (e.g. VBAK, MARA, BKPF)"),
});

// --- CONTEXT ANALYSIS ---
export const S_AnalyzeContext = z.object({
  objectUrl: z.string().describe("ADT URL of the main object"),
  depth: z.enum(["shallow", "deep"]).default("deep").optional()
    .describe("shallow = main source + direct includes only; deep = recursively all references"),
  mode: z.enum(["full", "contract"]).default("full").optional()
    .describe("full = embed complete source of main + includes; contract = compress each to its public signatures only (much fewer tokens — use when you only need the API surface, not the bodies)"),
});

// --- DOCUMENTATION ---
export const S_GetAbapKeywordDoc = z.object({
  keyword: z.string().describe("ABAP keyword (e.g. SELECT, LOOP, READ TABLE, MODIFY)"),
  version: z.string().optional().describe("ABAP version (e.g. 'latest', '758', '754'). Default: cfg.sapAbapVersion"),
});
export const S_GetAbapClassDoc = z.object({
  className: z.string().describe("ABAP class name or interface (e.g. CL_SALV_TABLE, IF_AMDP_MARKER_HDB)"),
  version: z.string().optional().describe("ABAP version (e.g. 'latest', '758', '754'). Default: cfg.sapAbapVersion"),
});
export const S_GetModuleBestPractices = z.object({
  module: z.enum(["FI", "CO", "MM", "SD", "PP", "PM", "QM", "HR", "HCM", "PS", "WM", "EWM", "BASIS", "BC", "ABAP"])
    .describe("SAP module (e.g. FI, MM, SD, ABAP)"),
});
export const S_SearchCleanAbap = z.object({
  query: z.string().describe(
    "Search query in the SAP Clean ABAP Styleguide (e.g. 'naming conventions', 'error handling', 'SELECT', 'method length', 'comments'). " +
    "Returns the most relevant sections from the official github.com/SAP/styleguides Clean ABAP Guide."
  ),
  maxResults: z.number().int().min(1).max(5).optional()
    .describe("Maximum number of sections (1–5, default: 2)"),
});
export const S_ReviewCleanAbap = z.object({
  source: z.string().describe(
    "ABAP source code to review for Clean ABAP compliance. " +
    "Detects anti-patterns (Hungarian notation, obsolete statements, etc.) " +
    "and returns findings with relevant Clean ABAP guideline excerpts."
  ),
  maxFindings: z.number().int().min(1).max(50).optional()
    .describe("Maximum number of findings to report (1–50, default: 10)"),
});
export const S_SearchAbapSyntax = z.object({
  query: z.string().describe(
    "Free-text search query for ABAP syntax (e.g. 'SELECT UP TO ROWS', 'LOOP AT clause order', 'READ TABLE WITH KEY'). " +
    "The tool identifies the main keyword, loads the official SAP documentation page and returns the relevant syntax section."
  ),
  version: z.string().optional().describe("ABAP version (e.g. 'latest', '758', '754'). Default: cfg.sapAbapVersion"),
});

// --- BATCH ---
export const S_BatchRead = z.object({
  operations: z.array(z.object({
    tool: z.string().describe(
      "Tool name — any read-only tool: search_abap_objects, search_source_code, " +
      "read_abap_source, get_object_info, where_used, get_code_completion, " +
      "find_definition, get_revisions, get_ddic_element, get_table_contents, " +
      "get_fix_proposals, get_inactive_objects, analyze_abap_context, " +
      "run_select_query, get_short_dumps, get_short_dump_detail, get_traces, " +
      "get_trace_detail, get_transport_info, get_transport_objects, " +
      "get_abapgit_repos, run_syntax_check, run_atc_check, " +
      "validate_ddic_references, review_clean_abap, " +
      "get_abap_keyword_doc, get_abap_class_doc, get_module_best_practices, " +
      "search_clean_abap, search_abap_syntax, search_sap_web"
    ),
    args: z.record(z.unknown()).describe("Arguments for the tool (same as calling the tool directly)"),
    label: z.string().optional().describe("Optional label to identify this operation in the result"),
  })).min(1).max(20).describe("List of operations to execute in parallel (1–20)"),
});

// --- WEB FETCH ---
export const S_FetchUrl = z.object({
  url: z.string().url().describe(
    "URL to fetch and extract readable content from (e.g. 'https://help.sap.com/docs/...'). " +
    "Works with JavaScript-rendered pages (SPAs) like SAP Help Portal."
  ),
});

// --- WEB SEARCH ---
export const S_SearchSapWeb = z.object({
  query: z.string().describe(
    "Search query — error message, topic, SAP Note number, or any SAP-related question " +
    "(e.g. 'CX_SY_OPEN_SQL_DB error SELECT', 'ALV grid editable', 'SAP Note 2081285')"
  ),
  sources: z.array(z.enum(["help", "community", "notes"]))
    .optional()
    .describe("Which sources to search: 'help' (help.sap.com), 'community' (community.sap.com), 'notes' (me.sap.com). Default: all three."),
  maxResults: z.number().int().min(1).max(10).default(5).optional()
    .describe("Maximum results per source (1–10, default: 5)"),
});

// --- METHOD-LEVEL SURGERY ---
export const S_ReadMethod = z.object({
  objectUrl:  z.string().describe("ADT URL of the class/interface, e.g. /sap/bc/adt/oo/classes/zcl_foo"),
  methodName: z.string().describe("Method name (case-insensitive). For interface methods use 'if_x~method'."),
});
export const S_EditMethod = z.object({
  objectUrl:          z.string().describe("ADT URL of the class (without /source/main)"),
  methodName:         z.string().describe("Name of the method to replace (case-insensitive)"),
  source:             z.string().describe(
    "New method BODY — the statements between METHOD…ENDMETHOD (no METHOD/ENDMETHOD keywords needed; " +
    "if you include them they are stripped). The original METHOD header and indentation are preserved. " +
    "Far cheaper than rewriting the whole class with write_abap_source."),
  transport:          z.string().optional().describe("Transport request"),
  activateAfterWrite: z.boolean().default(true).optional().describe("Activate after writing (default: true)"),
  skipSyntaxCheck:    z.boolean().default(false).optional().describe("Skip syntax check (not recommended)"),
});

// --- CONTRACT (context compression) ---
export const S_GetContract = z.object({
  objectUrl: z.string().describe("ADT URL of a class or interface, e.g. /sap/bc/adt/oo/classes/zcl_foo"),
});

// --- ANALYSIS (call graph, dead code) ---
export const S_CallGraph = z.object({
  objectUrl: z.string().describe("ADT URL of the object to analyze (the graph root)"),
  depth:     z.number().int().min(1).max(4).default(2).optional()
    .describe("How many where-used levels to expand (1–4, default 2)"),
  maxNodes:  z.number().int().min(5).max(200).default(60).optional()
    .describe("Node cap to keep the graph readable (default 60)"),
});
export const S_FindDeadCode = z.object({
  objectUrls: z.array(z.string()).min(1).max(50)
    .describe("ADT URLs of objects to check for inbound usages (1–50). Objects with zero usages are flagged as removal candidates."),
});

// --- INTENT FACADE ---
// Some MCP clients (e.g. Claude Code) serialise the nested `args` object as a
// JSON string instead of a real object. Zod's z.record() then rejects it with
// "Expected object, received string". Coerce a stringified payload back into an
// object before validation so the consolidated verbs accept both shapes.
const coerceArgsObject = z.preprocess((v) => {
  if (typeof v === "string") {
    const s = v.trim();
    if (s === "") return undefined;
    try {
      const parsed = JSON.parse(s);
      // Only accept JSON that decodes to a plain object; otherwise leave the
      // original value so zod surfaces a meaningful validation error.
      if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) return parsed;
    } catch {
      /* fall through – let zod report the type mismatch */
    }
  }
  return v;
}, z.record(z.unknown()).optional());

export const S_IntentRead = z.object({
  operation: z.string().describe(
    "What to read: source | method | contract | info | where_used | table | table_fields | ddic | revisions | context"),
  args: coerceArgsObject.describe("Arguments for the underlying tool (same shape as the granular tool)"),
});
export const S_IntentWrite = z.object({
  operation: z.string().describe(
    "What to write: source | method | activate | pretty_print | create_program | create_class | create_interface | " +
    "create_function_group | create_cds_view | create_table | create_message_class | create_metadata_extension | " +
    "create_service_definition | create_service_binding | publish_service_binding | create_dcl | create_bdef | create_package | delete"),
  args: coerceArgsObject.describe("Arguments for the underlying tool (same shape as the granular tool)"),
});
export const S_IntentSearch = z.object({
  operation: z.string().describe("What to search: objects | source | call_graph | dead_code"),
  args: coerceArgsObject.describe("Arguments for the underlying tool"),
});
export const S_IntentDiagnose = z.object({
  operation: z.string().describe(
    "What to diagnose: syntax | atc | unit | ddic_validate | clean_abap | dumps | dump_detail | traces | trace_detail | workflow"),
  args: coerceArgsObject.describe("Arguments for the underlying tool"),
});

// --- WORKFLOW ANALYSIS ---
export const S_AnalyzeWorkflow = z.object({
  mode: z.enum(["definitions", "instances", "steps", "agents", "graph"]).default("definitions")
    .describe(
      "What to analyze: " +
      "'definitions' = list workflow templates (SWF_FLEX_HEADER + SWFTASKI), " +
      "'instances' = list running/completed workflow instances (SWWWIHEAD), " +
      "'steps' = show step definitions for one workflow (needs workflowId), " +
      "'agents' = show agent/role assignments for one workflow (needs workflowId), " +
      "'graph' = return the complete SWDD step-by-step graph with nodes, edges, and step details (needs workflowId)"
    ),
  workflowId: z.string().optional()
    .describe("Workflow or task ID, e.g. 'WS12300111' (Workflow) or 'TS12300120' (Task). Required for modes 'steps' and 'agents'."),
  status: z.enum(["all", "READY", "STARTED", "COMPLETED", "ERROR"]).default("all").optional()
    .describe("Filter instances by status (mode='instances' only). Default: all"),
  maxResults: z.number().int().min(1).max(100).default(20).optional()
    .describe("Max results to return (default: 20)"),
  user: z.string().optional()
    .describe("Filter instances by SAP user/agent (mode='instances' only)"),
});

// --- META TOOLS ---
export const S_FindTools = z.object({
  query: z.string().optional().describe("Search pattern for tool names/descriptions"),
  category: z.string().optional().describe(
    "Category: SEARCH | READ | WRITE | CREATE | DELETE | TEST | QUALITY | DIAGNOSTICS | TRANSPORT | ABAPGIT | QUERY | DOCUMENTATION | WEBSEARCH | BATCH | ANALYSIS | INTENT"
  ),
  enable: z.boolean().optional().default(true).describe("Enable tools (default: true)"),
});
export const S_ListTools = z.object({
  category: z.string().optional().describe(
    "Filter by category: SEARCH | READ | WRITE | CREATE | DELETE | TEST | QUALITY | DIAGNOSTICS | TRANSPORT | ABAPGIT | QUERY | DOCUMENTATION | WEBSEARCH | BATCH | ANALYSIS | INTENT. Omit for all."
  ),
});
