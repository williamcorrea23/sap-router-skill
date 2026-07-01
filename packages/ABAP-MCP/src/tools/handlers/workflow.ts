/**
 * WORKFLOW tool handler: analyze_workflow
 * Analyzes SAP Business Workflow (classic WF / SWDD) metadata by querying
 * standard workflow tables via the ADT runQuery endpoint (read-only, no
 * ALLOW_WRITE required).
 *
 * Tables used:
 *   SWF_FLEX_HEADER  – Flexible workflow template headers (NW 7.40+)
 *   SWFTASKI         – Classic task/workflow definitions (all NW versions)
 *   SWWWIHEAD        – Work item instance headers
 *   SWF_FLEX_STEP    – Flexible workflow step definitions
 *   SWF_FLEX_ROLE    – Agent/role assignments in flexible workflows
 *   SWWUSERWI        – Work items per user (instance-level agent tracking)
 */

import type { ADTClient } from "abap-adt-api";
import type { ToolResult } from "../../types.js";
import { S_AnalyzeWorkflow } from "../../schemas.js";
import { cfg } from "../../config.js";

function ok(text: string): ToolResult { return { content: [{ type: "text", text }] }; }
function err(text: string): ToolResult { return { content: [{ type: "text", text }], isError: true }; }

/**
 * Escape a value for use inside an ABAP SQL string literal ('' doubling).
 * The data-preview backend is read-only, so this is about producing correct
 * queries (and clear errors) for values containing quotes, not about
 * preventing data mutation.
 */
function sqlLit(s: string): string {
  return s.replace(/'/g, "''");
}

/** Run a SELECT via ADT and catch errors so one failing query doesn't break the whole response. */
async function safeQuery(
  client: ADTClient,
  sql: string,
): Promise<{ rows: Record<string, string>[]; error?: string }> {
  try {
    const result = await client.runQuery(sql);
    const rows = Array.isArray(result) ? (result as Record<string, string>[]) : [];
    return { rows };
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return { rows: [], error: msg.substring(0, 120) };
  }
}

const WI_STATUS: Record<string, string> = {
  "0": "WAITING",
  "1": "READY",
  "2": "SELECTED",
  "3": "STARTED",
  "4": "COMPLETED",
  "5": "CANCELLED",
  "6": "ERROR",
  "7": "EXECUTED",
};

/** Node type mapping for SWD_NODES.NODETYPE */
const NODE_TYPE_MAP: Record<string, string> = {
  "S": "Start",
  "E": "End",
  "A": "Activity",
  "C": "Condition",
  "D": "Decision",
  "F": "Fork",
  "J": "Join",
  "L": "Loop Start",
  "M": "Loop End",
  "W": "Wait",
  "B": "Block Start",
  "N": "Block End",
  "U": "User Decision",
  "X": "Exception Handler",
  "T": "Terminating Event",
  "P": "Parallel Section",
  "R": "Reference",
  "G": "Go To",
  "H": "Ad-Hoc Anchor",
  "K": "Container Operation",
  "O": "Local Event",
  "Q": "Send Mail",
  "V": "Process Control",
  "Y": "Web Activity",
  "Z": "XML Message",
};

/** Line type mapping for SWD_LINES.LINE_TYPE */
const LINE_TYPE_MAP: Record<string, string> = {
  "N": "Normal",
  "C": "Condition True",
  "F": "Condition False",
  "E": "Exception",
  "D": "Default",
  "R": "Return",
  "T": "Timeout",
  "X": "Cancel",
  "O": "Outcome",
  "L": "Loop",
};

export async function handleAnalyzeWorkflow(
  client: ADTClient,
  args: Record<string, unknown>,
): Promise<ToolResult> {
  const p = S_AnalyzeWorkflow.parse(args);
  const max = p.maxResults ?? 20;

  switch (p.mode) {

    // ── DEFINITIONS ─────────────────────────────────────────────────────────
    case "definitions": {
      const [flex, classic] = await Promise.all([
        safeQuery(
          client,
          `SELECT * FROM SWF_FLEX_HEADER UP TO ${max} ROWS`,
        ),
        safeQuery(
          client,
          `SELECT TASKID, TASKTYPE, DESCRIPT, CREATEDBY, CREATEDON, CHANGEDBY, CHANGEDON ` +
          `FROM SWFTASKI UP TO ${max} ROWS WHERE TASKTYPE = 'WS'`,
        ),
      ]);

      const parts: string[] = ["# SAP Workflow Definitions\n"];

      if (flex.rows.length > 0) {
        parts.push(`## Flexible Workflow Templates (SWF_FLEX_HEADER) — ${flex.rows.length} found\n`);
        parts.push("```json\n" + JSON.stringify(flex.rows, null, 2) + "\n```");
      } else {
        parts.push(
          flex.error
            ? `## Flexible Workflow (SWF_FLEX_HEADER)\n⚠️ Not available: ${flex.error}`
            : "## Flexible Workflow (SWF_FLEX_HEADER)\n_No entries found._",
        );
      }

      if (classic.rows.length > 0) {
        parts.push(`\n## Classic Workflow Templates (SWFTASKI, TASKTYPE=WS) — ${classic.rows.length} found\n`);
        parts.push("```json\n" + JSON.stringify(classic.rows, null, 2) + "\n```");
      } else {
        parts.push(
          classic.error
            ? `\n## Classic Workflow (SWFTASKI)\n⚠️ Not available: ${classic.error}`
            : "\n## Classic Workflow (SWFTASKI)\n_No workflow templates (WS) found._",
        );
      }

      if (flex.rows.length === 0 && classic.rows.length === 0 && !flex.error && !classic.error) {
        parts.push(
          "\n💡 No workflow definitions found. " +
          "If workflows are used, try analyze_workflow(mode='instances') to check for running instances, " +
          "or verify that the workflow tables are populated (transaction SWDD).",
        );
      }

      return ok(parts.join("\n"));
    }

    // ── INSTANCES ───────────────────────────────────────────────────────────
    case "instances": {
      const conditions: string[] = [];

      if (p.workflowId) {
        // WI_RH_TASK contains the task ID (e.g. WS90000001)
        conditions.push(`WI_RH_TASK LIKE '%${sqlLit(p.workflowId.toUpperCase())}%'`);
      }
      if (p.status && p.status !== "all") {
        // WI_STAT contains status as text (READY, STARTED, COMPLETED, ERROR, etc.)
        const statusMap: Record<string, string> = {
          READY: "READY", STARTED: "STARTED", COMPLETED: "COMPLETED", ERROR: "ERROR",
        };
        const statusValue = statusMap[p.status.toUpperCase()] ?? p.status.toUpperCase();
        conditions.push(`WI_STAT = '${sqlLit(statusValue)}'`);
      }
      if (p.user) {
        // WI_AAGENT contains the actual agent (user)
        conditions.push(`WI_AAGENT = '${sqlLit(p.user.toUpperCase())}'`);
      }

      const where = conditions.length > 0 ? ` WHERE ${conditions.join(" AND ")}` : "";
      const sql = `SELECT WI_ID, WI_RH_TASK, WI_STAT, WI_TEXT, WI_CD, WI_CT, WI_AAGENT, WI_CREATOR, TOP_TASK FROM SWWWIHEAD UP TO ${max} ROWS${where}`;

      const result = await safeQuery(client, sql);
      if (result.error) {
        return err(
          `❌ Error querying workflow instances (SWWWIHEAD):\n${result.error}\n\n` +
          "Note: SWWWIHEAD requires SAP Workflow (BC-BMT-WFM) to be installed and configured.",
        );
      }
      if (result.rows.length === 0) {
        return ok("No workflow instances found with the given criteria.");
      }

      return ok(
        `# Workflow Instances (SWWWIHEAD) — ${result.rows.length} found\n\n` +
        "```json\n" + JSON.stringify(result.rows, null, 2) + "\n```",
      );
    }

    // ── STEPS ───────────────────────────────────────────────────────────────
    case "steps": {
      if (!p.workflowId) {
        return err("❌ workflowId is required for mode='steps'. Example: workflowId='WS12300111'");
      }
      const wfId = sqlLit(p.workflowId.toUpperCase());

      const [flex, classic, contDef] = await Promise.all([
        safeQuery(client, `SELECT * FROM SWF_FLEX_STEP UP TO ${max} ROWS WHERE WFTYPEID = '${wfId}'`),
        safeQuery(client, `SELECT * FROM SWFSTEPDEF UP TO ${max} ROWS WHERE FLOWID = '${wfId}'`),
        // SWFCONTDEF: container elements of a SWDD workflow (data flowing between steps)
        safeQuery(client, `SELECT ELEMENT, CDTYPE, EDITMODE, MANDATORY FROM SWFCONTDEF UP TO ${max} ROWS WHERE TASKID = '${wfId}'`),
      ]);

      const parts: string[] = [`# Workflow Step Definitions for ${wfId}\n`];

      if (flex.rows.length > 0) {
        parts.push(`## Flexible WF Steps (SWF_FLEX_STEP) — ${flex.rows.length} steps\n`);
        parts.push("```json\n" + JSON.stringify(flex.rows, null, 2) + "\n```");
      } else {
        parts.push(
          flex.error
            ? `## SWF_FLEX_STEP\n⚠️ ${flex.error}`
            : `## SWF_FLEX_STEP\n_No steps found for ${wfId} (only relevant for Flexible Workflow)._`,
        );
      }

      if (classic.rows.length > 0) {
        parts.push(`\n## Classic WF Steps (SWFSTEPDEF) — ${classic.rows.length} steps\n`);
        parts.push("```json\n" + JSON.stringify(classic.rows, null, 2) + "\n```");
      } else {
        parts.push(
          classic.error
            ? `\n## SWFSTEPDEF\n⚠️ ${classic.error}`
            : `\n## SWFSTEPDEF\n_No steps found for ${wfId}._`,
        );
      }

      // SWDD container: always useful regardless of WF type
      if (contDef.rows.length > 0) {
        parts.push(`\n## SWDD Container Elements (SWFCONTDEF) — ${contDef.rows.length} elements\n`);
        parts.push(
          "_Container elements are the data fields passed between workflow steps (import/export/in-out)._\n",
        );
        parts.push("```json\n" + JSON.stringify(contDef.rows, null, 2) + "\n```");
      } else if (!contDef.error) {
        parts.push(`\n## SWDD Container (SWFCONTDEF)\n_No container elements found for ${wfId}._`);
      }

      // Deep SWDD analysis via execute_abap_snippet when execution is enabled.
      // Classic SWDD step/node structure is not queryable via plain SQL — the compiled
      // workflow graph lives in internal WF runtime tables. The snippet reads SWFTASKI
      // (task header) and SWFCONTDEF (container) to give meaningful output while
      // gracefully noting that the visual step graph requires SWDD.
      if (cfg.allowWrite && cfg.allowExecute) {
        parts.push("\n## SWDD Deep Analysis (execute_abap_snippet)\n");
        try {
          // Dynamic import avoids circular dependency: handler-map → workflow → handler-map
          const { handleExecuteAbapSnippet } = await import("./query.js");
          const snippet = buildSwddStepsSnippet(wfId);
          const result = await handleExecuteAbapSnippet(client, { source: snippet });
          const text = result.content[0]?.type === "text" ? result.content[0].text : String(result.content);
          parts.push(text);
        } catch (e) {
          parts.push(`⚠️ execute_abap_snippet failed: ${e instanceof Error ? e.message : String(e)}`);
        }
      } else {
        parts.push(
          "\n> **SWDD step graph**: Classic SWDD step/node structure is compiled into an internal " +
          "WF runtime format and cannot be read via direct SQL. " +
          "Enable `ALLOW_WRITE=true` + `ALLOW_EXECUTE=true` for ABAP-snippet-based deep analysis. " +
          "Alternative: transaction **SWDD** for visual step display, or **SWI14** for task usage analysis.",
        );
      }

      return ok(parts.join("\n"));
    }

    // ── AGENTS ──────────────────────────────────────────────────────────────
    case "agents": {
      if (!p.workflowId) {
        return err("❌ workflowId is required for mode='agents'. Example: workflowId='WS12300111'");
      }
      const wfId = sqlLit(p.workflowId.toUpperCase());

      const [roles, userWi] = await Promise.all([
        safeQuery(
          client,
          `SELECT * FROM SWF_FLEX_ROLE UP TO ${max} ROWS WHERE WFTYPEID = '${wfId}'`,
        ),
        safeQuery(
          client,
          `SELECT WI_ID, TASK_OBJ, USER_ID FROM SWWUSERWI UP TO ${max} ROWS ` +
          `WHERE TASK_OBJ LIKE '%${wfId.substring(0, 10)}%'`,
        ),
      ]);

      const parts: string[] = [`# Agent/Role Assignments for ${wfId}\n`];

      if (roles.rows.length > 0) {
        parts.push(`## Role Definitions (SWF_FLEX_ROLE) — ${roles.rows.length} entries\n`);
        parts.push("```json\n" + JSON.stringify(roles.rows, null, 2) + "\n```");
      } else {
        parts.push(
          roles.error
            ? `## SWF_FLEX_ROLE\n⚠️ ${roles.error}`
            : `## SWF_FLEX_ROLE\n_No role assignments found for ${wfId}._`,
        );
      }

      if (userWi.rows.length > 0) {
        parts.push(`\n## Instance-Level Agents (SWWUSERWI) — ${userWi.rows.length} entries\n`);
        parts.push("```json\n" + JSON.stringify(userWi.rows, null, 2) + "\n```");
      } else {
        parts.push(
          userWi.error
            ? `\n## SWWUSERWI\n⚠️ ${userWi.error}`
            : `\n## SWWUSERWI\n_No agent assignments found for ${wfId}._`,
        );
      }

      if (roles.rows.length === 0 && userWi.rows.length === 0) {
        parts.push(
          `\n💡 No agent assignments found for '${wfId}'. ` +
          "Check in SWDD under step → Agent assignment, or use mode='instances' to see who worked on actual instances.",
        );
      }

      return ok(parts.join("\n"));
    }

    // ── GRAPH ───────────────────────────────────────────────────────────────
    case "graph": {
      if (!p.workflowId) {
        return err("❌ workflowId is required for mode='graph'. Example: workflowId='WS90000001'");
      }
      const wfId = sqlLit(p.workflowId.toUpperCase());

      // Query all relevant tables in parallel for the workflow graph
      const [header, nodes, lines, steps, container, nodeTexts] = await Promise.all([
        // Workflow header (description, creator, etc.)
        safeQuery(
          client,
          `SELECT TASKID, TASKTYPE, DESCRIPT, CREATEDBY, CREATEDON, CHANGEDBY, CHANGEDON ` +
          `FROM SWFTASKI WHERE TASKID = '${wfId}'`,
        ),
        // Nodes (the graph vertices)
        safeQuery(
          client,
          `SELECT WFD_ID, VERSION, NODEID, NODETYPE, BLOCKID, PAR_BLCKID, NEST_LEVEL, ` +
          `CONDIT_ID, CONT_CMD, EVT_TYPE, EVT_OTYPE, STEP_HIDE ` +
          `FROM SWD_NODES WHERE WFD_ID = '${wfId}' AND EXETYP = 'P' ` +
          `ORDER BY NODEID`,
        ),
        // Lines (the graph edges: predecessor → successor)
        safeQuery(
          client,
          `SELECT WFD_ID, VERSION, PRED_NODE, SUCC_NODE, LINE_TYPE, RETURNCODE ` +
          `FROM SWD_LINES WHERE WFD_ID = '${wfId}' AND EXETYP = 'P' ` +
          `ORDER BY PRED_NODE, SUCC_NODE`,
        ),
        // Steps (detailed step information: task, agent role, deadlines)
        safeQuery(
          client,
          `SELECT WFD_ID, VERSION, NODEID, TASK, ACT_ROLE, PRIORITY, STEP_ASYNC, ` +
          `DIAL_FLAG, CLASSIFICATION ` +
          `FROM SWD_STEPS WHERE WFD_ID = '${wfId}' AND EXETYP = 'P' ` +
          `ORDER BY NODEID`,
        ),
        // Container elements (data flowing between steps)
        safeQuery(
          client,
          `SELECT ELEMENT, REFTYPE, REFSTRUCT, REFFIELD, REFOBJTYPE, ELEMTYPE, TABELEM ` +
          `FROM SWD_WFCONT WHERE WFD_ID = '${wfId}' AND EXETYP = 'P' UP TO ${max} ROWS`,
        ),
        // Node texts (descriptions) from SWD_NODET in the configured logon
        // language (SAP 1-char key: EN -> E, DE -> D, ...).
        safeQuery(
          client,
          `SELECT NODEID, DESCRIPT FROM SWD_NODET WHERE WFD_ID = '${wfId}' AND EXETYP = 'P' ` +
          `AND LANGU = '${(cfg.language.charAt(0) || "E").toUpperCase()}' UP TO ${max} ROWS`,
        ),
      ]);

      // Build the graph response
      const parts: string[] = [`# SWDD Workflow Graph: ${wfId}\n`];

      // Header info
      if (header.rows.length > 0) {
        const h = header.rows[0];
        parts.push(`## Workflow Definition\n`);
        parts.push(`- **ID**: ${h.TASKID || wfId}`);
        parts.push(`- **Description**: ${h.DESCRIPT || "(no description)"}`);
        parts.push(`- **Type**: ${h.TASKTYPE || "WS"}`);
        parts.push(`- **Created by**: ${h.CREATEDBY || "?"} on ${h.CREATEDON || "?"}`);
        parts.push(`- **Changed by**: ${h.CHANGEDBY || "?"} on ${h.CHANGEDON || "?"}\n`);
      } else if (header.error) {
        parts.push(`## Workflow Header\n⚠️ Could not read SWFTASKI: ${header.error}\n`);
      } else {
        parts.push(`## Workflow Header\n_Workflow '${wfId}' not found in SWFTASKI._\n`);
      }

      // Build node description map
      const nodeDescMap: Record<string, string> = {};
      if (nodeTexts.rows.length > 0) {
        for (const row of nodeTexts.rows) {
          if (row.NODEID && row.DESCRIPT) {
            nodeDescMap[row.NODEID] = row.DESCRIPT;
          }
        }
      }

      // Build step info map (NODEID → step details)
      const stepMap: Record<string, Record<string, string>> = {};
      if (steps.rows.length > 0) {
        for (const row of steps.rows) {
          if (row.NODEID) {
            stepMap[row.NODEID] = row;
          }
        }
      }

      // Nodes section
      if (nodes.rows.length > 0) {
        parts.push(`## Nodes (${nodes.rows.length} total)\n`);
        parts.push("| NodeID | Type | Description | Task | Block | Level |");
        parts.push("|--------|------|-------------|------|-------|-------|");
        for (const n of nodes.rows) {
          const nodeType = NODE_TYPE_MAP[n.NODETYPE] || n.NODETYPE || "?";
          const desc = nodeDescMap[n.NODEID] || stepMap[n.NODEID]?.TASK || "";
          const task = stepMap[n.NODEID]?.TASK || "";
          parts.push(
            `| ${n.NODEID} | ${nodeType} | ${desc.substring(0, 30)} | ${task} | ${n.BLOCKID || "-"} | ${n.NEST_LEVEL || "0"} |`,
          );
        }
        parts.push("");
      } else {
        parts.push(
          nodes.error
            ? `## Nodes\n⚠️ Could not read SWD_NODES: ${nodes.error}\n`
            : `## Nodes\n_No nodes found for ${wfId}._\n`,
        );
      }

      // Edges section
      if (lines.rows.length > 0) {
        parts.push(`## Edges (${lines.rows.length} connections)\n`);
        parts.push("| From | To | Type | Condition/Returncode |");
        parts.push("|------|-----|------|---------------------|");
        for (const l of lines.rows) {
          const lineType = LINE_TYPE_MAP[l.LINE_TYPE] || l.LINE_TYPE || "?";
          const rc = l.RETURNCODE ? l.RETURNCODE.substring(0, 30) : "-";
          parts.push(`| ${l.PRED_NODE} | ${l.SUCC_NODE} | ${lineType} | ${rc} |`);
        }
        parts.push("");
      } else {
        parts.push(
          lines.error
            ? `## Edges\n⚠️ Could not read SWD_LINES: ${lines.error}\n`
            : `## Edges\n_No edges found for ${wfId}._\n`,
        );
      }

      // Steps detail section
      if (steps.rows.length > 0) {
        parts.push(`## Step Details (${steps.rows.length} steps)\n`);
        parts.push("```json");
        parts.push(JSON.stringify(steps.rows, null, 2));
        parts.push("```\n");
      }

      // Container section
      if (container.rows.length > 0) {
        parts.push(`## Container Elements (${container.rows.length} elements)\n`);
        parts.push("_Data elements passed between workflow steps:_\n");
        parts.push("| Element | Type | Reference |");
        parts.push("|---------|------|-----------|");
        for (const c of container.rows) {
          const ref = c.REFOBJTYPE || c.REFSTRUCT || c.REFFIELD || "-";
          const elemType = c.ELEMTYPE === "I" ? "Import" : c.ELEMTYPE === "E" ? "Export" : c.ELEMTYPE || "?";
          parts.push(`| ${c.ELEMENT} | ${elemType} | ${ref} |`);
        }
        parts.push("");
      }

      // Mermaid diagram
      if (nodes.rows.length > 0 && lines.rows.length > 0) {
        parts.push(`## Mermaid Diagram\n`);
        parts.push("```mermaid");
        parts.push("flowchart TD");
        // Define nodes
        for (const n of nodes.rows) {
          const nodeType = n.NODETYPE || "?";
          const desc = nodeDescMap[n.NODEID] || stepMap[n.NODEID]?.TASK || `Node ${n.NODEID}`;
          const shortDesc = desc.substring(0, 20).replace(/"/g, "'");
          // Use different shapes for different node types
          if (nodeType === "S") {
            parts.push(`    N${n.NODEID}(("${shortDesc}"))`); // Circle for Start
          } else if (nodeType === "E") {
            parts.push(`    N${n.NODEID}(("${shortDesc}"))`); // Circle for End
          } else if (nodeType === "C" || nodeType === "D") {
            parts.push(`    N${n.NODEID}{{"${shortDesc}"}}`); // Diamond for Condition/Decision
          } else if (nodeType === "F") {
            parts.push(`    N${n.NODEID}[/"${shortDesc}"/]`); // Parallelogram for Fork
          } else {
            parts.push(`    N${n.NODEID}["${shortDesc}"]`); // Rectangle for Activity
          }
        }
        // Define edges
        for (const l of lines.rows) {
          const label = l.RETURNCODE ? `|${l.RETURNCODE.substring(0, 10)}|` : "";
          parts.push(`    N${l.PRED_NODE} -->${label} N${l.SUCC_NODE}`);
        }
        parts.push("```\n");
      }

      // Usage hint
      parts.push(
        "> 💡 **Tip**: Use the Mermaid diagram above to visualize the workflow. " +
        "For the full SWDD experience, open transaction **SWDD** in SAP GUI and enter the workflow ID.",
      );

      return ok(parts.join("\n"));
    }

    default:
      return err(`❌ Unknown mode: ${String((p as { mode?: unknown }).mode)}`);
  }
}

/**
 * Builds an ABAP snippet that reads SWDD workflow metadata at runtime.
 * Uses only tables and field names known to exist on all SAP systems with
 * classic Business Workflow installed (NW 7.0+):
 *   SWFTASKI   — task header (TASKID, TASKTYPE, DESCRIPT, CREATEDBY, CREATEDON, …)
 *   SWFCONTDEF — container element definitions (ELEMENT, CDTYPE, EDITMODE, MANDATORY)
 *
 * Intentionally avoids function module calls with uncertain type interfaces so the
 * snippet passes the syntax check on all target systems.
 */
function buildSwddStepsSnippet(wfId: string): string {
  return `REPORT ztest.
DATA lv_id TYPE swf_task_id VALUE '${wfId}'.
WRITE: / '=== SWDD Workflow Detail:', lv_id.
WRITE: / ''.

" ---- Task header ----
SELECT SINGLE taskid tasktype descript createdby createdon changedby changedon
  FROM swftaski INTO @DATA(ls) WHERE taskid = @lv_id.
IF sy-subrc <> 0.
  WRITE: / 'ERROR: Workflow', lv_id, 'not found in SWFTASKI.'.
  RETURN.
ENDIF.
WRITE: / 'Description :', ls-descript.
WRITE: / 'Task Type   :', ls-tasktype.
WRITE: / 'Created by  :', ls-createdby, 'on', ls-createdon.
WRITE: / 'Changed by  :', ls-changedby, 'on', ls-changedon.
WRITE: / ''.

" ---- Container elements ----
" SWFCONTDEF holds the data elements (import/export/in-out) shared between steps.
WRITE: / '=== Container (SWFCONTDEF):'.
SELECT element cdtype editmode mandatory
  FROM swfcontdef INTO TABLE @DATA(lt_c)
  WHERE taskid = @lv_id UP TO 50 ROWS.
IF sy-subrc = 0.
  LOOP AT lt_c INTO DATA(lc).
    WRITE: / '  [', lc-element, ']  type:', lc-cdtype,
             '  edit:', lc-editmode, '  mand:', lc-mandatory.
  ENDLOOP.
ELSE.
  WRITE: / '  (no container elements)'.
ENDIF.
WRITE: / ''.

" ---- Information on step-level detail ----
WRITE: / 'Note: The compiled SWDD step/node graph is not accessible via plain SQL.'.
WRITE: / 'For visual step display: transaction SWDD (enter WF-ID above).'.
WRITE: / 'For task usage in running instances: analyze_workflow(mode=instances,workflowId=ID).'.
WRITE: / 'For who performed which step: check SWWWIHEAD filtered by task LIKE TS%.'.`;
}
