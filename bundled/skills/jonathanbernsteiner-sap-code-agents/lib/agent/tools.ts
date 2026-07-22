/**
 * The four workspace-scoped agent tools (Phase 4).
 *
 * Every number returned here is computed by SQL — the model only relays it.
 * Unresolved call targets are visibly marked; usage rows carry their
 * `simulated` flag so the model can (and must) label synthetic data.
 */
import type Anthropic from "@anthropic-ai/sdk";
import { query } from "../db/client";

export const TOOL_DEFINITIONS: Anthropic.Tool[] = [
  {
    name: "search_objects",
    description:
      "Search objects in the current workspace by name or summary text. Returns name, type, category, parse status, a summary snippet, the SQL-computed migration_risk_grade (A best … D worst, null = not yet covered by a report run) and process_areas (derived from the object's table accesses). Use this first to find relevant objects. For process-level questions ('everything in Goods Movement'), pass process_area with an empty query.",
    input_schema: {
      type: "object",
      properties: {
        query: { type: "string", description: "Substring to match against object names and summaries (case-insensitive). May be empty when process_area is set." },
        process_area: {
          type: "string",
          description:
            "Optional exact process-area filter, e.g. 'Goods Movement / Inventory', 'Purchasing', 'Sales', 'Finance', 'Pricing / Conditions', 'Material Master', 'Vendor Master', 'Production'",
        },
        limit: { type: "integer", description: "Max results (default 10, max 20)" },
      },
      required: ["query"],
    },
  },
  {
    name: "read_object",
    description:
      "Read one object: full metadata, the Haiku-generated summary, the SQL-computed migration_risk_grade and process_areas, and the raw ABAP source (truncated if very large). Use the exact object name.",
    input_schema: {
      type: "object",
      properties: {
        name: { type: "string", description: "Exact object name, e.g. ZCL_GM_MOVEMENT_SERVICE" },
      },
      required: ["name"],
    },
  },
  {
    name: "where_used",
    description:
      "Dependency lookup for one object: which objects call/reference it (callers), and what it calls/references (callees). Each callee carries its resolution: 'resolved' (an object in this workspace), '[internal]' (a FORM/local routine defined inside the object itself — implementation detail, not a dependency), or '[external]' (not ingested here; likely SAP standard when the name is not Z*/Y* — never assume what it does).",
    input_schema: {
      type: "object",
      properties: {
        name: { type: "string", description: "Exact object name" },
      },
      required: ["name"],
    },
  },
  {
    name: "get_usage_stats",
    description:
      "Usage statistics (24-month call counts, last execution). Without a name: returns most-used and zero-usage objects for the workspace. With a name: that object's row. If usage is simulated, every result says so — repeat that label in your answer.",
    input_schema: {
      type: "object",
      properties: {
        name: { type: "string", description: "Optional exact object name" },
      },
      required: [],
    },
  },
];

const SOURCE_LIMIT = 28_000;

/**
 * Resolve a workspace by name. When companyId is given (all API paths),
 * visibility is company-scoped: own workspaces plus global examples.
 * Without it (trusted scripts: seeder, benchmark, report job) the lookup is
 * unrestricted.
 */
export async function resolveWorkspace(
  name: string,
  companyId?: string
): Promise<{ id: string; simulated_usage: boolean } | null> {
  const rows = await query<{ id: string; simulated_usage: boolean }>(
    companyId
      ? `select id, simulated_usage from workspaces where name = $1 and (kind = 'example' or company_id = $2)`
      : `select id, simulated_usage from workspaces where name = $1`,
    companyId ? [name, companyId] : [name]
  );
  return rows[0] ?? null;
}

export async function executeTool(
  workspaceId: string,
  toolName: string,
  input: Record<string, unknown>
): Promise<string> {
  switch (toolName) {
    case "search_objects": {
      const q = String(input.query ?? "").trim();
      const processArea = String(input.process_area ?? "").trim();
      const limit = Math.min(Number(input.limit) || 10, 20);
      if (!q && !processArea) return JSON.stringify({ error: "query or process_area is required" });
      const rows = await query(
        `select o.name, o.object_type, o.category, o.parse_status,
                left(coalesce(o.summary, ''), 240) as summary_snippet,
                g.grade as migration_risk_grade,
                (select array_agg(pa.process_area order by pa.process_area)
                 from object_process_areas pa where pa.object_id = o.id) as process_areas
         from objects o
         left join object_risk_grades g on g.object_id = o.id
         where o.workspace_id = $1 and ($2 = '' or o.name ilike $3 or o.summary ilike $3)
           and ($4 = '' or exists (select 1 from object_process_areas pa
                                   where pa.object_id = o.id and pa.process_area = $4))
         order by (o.name ilike $3) desc, o.name
         limit $5`,
        [workspaceId, q, `%${q}%`, processArea, limit]
      );
      return JSON.stringify({ matches: rows, count: rows.length });
    }

    case "read_object": {
      const name = String(input.name ?? "").trim().toUpperCase();
      const rows = await query<{ source: string; [k: string]: unknown }>(
        `select o.name, o.object_type, o.category, o.files, o.parse_status, o.parse_errors,
                o.summary, o.summary_model, o.source,
                g.grade as migration_risk_grade,
                (select array_agg(pa.process_area order by pa.process_area)
                 from object_process_areas pa where pa.object_id = o.id) as process_areas
         from objects o
         left join object_risk_grades g on g.object_id = o.id
         where o.workspace_id = $1 and o.name = $2
         order by case o.object_type when 'CLAS' then 0 when 'INTF' then 1 when 'PROG' then 2 else 3 end
         limit 1`,
        [workspaceId, name]
      );
      if (rows.length === 0) {
        return JSON.stringify({ error: `object '${name}' not found in this workspace` });
      }
      const row = rows[0];
      const truncated = row.source.length > SOURCE_LIMIT;
      return JSON.stringify({
        ...row,
        source: row.source.slice(0, SOURCE_LIMIT),
        source_truncated: truncated,
      });
    }

    case "where_used": {
      const name = String(input.name ?? "").trim().toUpperCase();
      const obj = await query<{ id: string }>(
        `select id from objects where workspace_id = $1 and name = $2 limit 1`,
        [workspaceId, name]
      );
      if (obj.length === 0) {
        return JSON.stringify({ error: `object '${name}' not found in this workspace` });
      }
      const callers = await query(
        `select o.name as caller, e.kind, e.file, e.line
         from call_edges e join objects o on o.id = e.caller_id
         where e.workspace_id = $1 and (e.callee_id = $2 or e.callee_name = $3)
           and coalesce(e.target_kind, '') <> 'internal'
         order by o.name limit 100`,
        [workspaceId, obj[0].id, name]
      );
      const callees = await query(
        `select e.callee_name as target, e.kind, e.file, e.line,
                case coalesce(e.target_kind, case when e.callee_id is null then 'external' else 'workspace' end)
                  when 'internal' then '[internal]'
                  when 'workspace' then 'resolved'
                  else '[external]'
                end as resolution
         from call_edges e
         where e.workspace_id = $1 and e.caller_id = $2
         order by e.callee_name limit 100`,
        [workspaceId, obj[0].id]
      );
      const accesses = await query(
        `select op, table_name, dynamic, file, line, evidence
         from table_accesses where workspace_id = $1 and object_id = $2
         order by table_name, line limit 100`,
        [workspaceId, obj[0].id]
      );
      return JSON.stringify({ object: name, callers, callees, table_accesses: accesses });
    }

    case "get_usage_stats": {
      const [ws] = await query<{ simulated_usage: boolean }>(
        `select simulated_usage from workspaces where id = $1`,
        [workspaceId]
      );
      const label = ws?.simulated_usage
        ? "SIMULATED DATA — usage statistics for this workspace are synthetic (deterministic model) and must be labeled as simulated in any answer."
        : undefined;
      const name = input.name ? String(input.name).trim().toUpperCase() : undefined;
      if (name) {
        const rows = await query(
          `select o.name, u.call_count_24m, u.last_executed, u.simulated
           from usage_stats u join objects o on o.id = u.object_id
           where u.workspace_id = $1 and o.name = $2`,
          [workspaceId, name]
        );
        if (rows.length === 0) {
          return JSON.stringify({ object: name, usage: null, note: "no usage data available for this object" });
        }
        return JSON.stringify({ simulated_label: label, usage: rows[0] });
      }
      const top = await query(
        `select o.name, o.object_type, u.call_count_24m, u.last_executed, u.simulated
         from usage_stats u join objects o on o.id = u.object_id
         where u.workspace_id = $1 order by u.call_count_24m desc limit 10`,
        [workspaceId]
      );
      if (top.length === 0) {
        return JSON.stringify({ note: "no usage data available for this workspace" });
      }
      const dead = await query(
        `select o.name, o.object_type, u.call_count_24m
         from usage_stats u join objects o on o.id = u.object_id
         where u.workspace_id = $1 and u.call_count_24m = 0 order by o.name limit 25`,
        [workspaceId]
      );
      return JSON.stringify({ simulated_label: label, most_used: top, zero_usage: dead });
    }

    default:
      return JSON.stringify({ error: `unknown tool ${toolName}` });
  }
}
