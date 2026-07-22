/**
 * Deterministic edges → Mermaid conversion (Phase 4).
 * The LLM never writes Mermaid: this module computes diagrams purely from
 * call_edges rows, with stable ordering.
 *
 * Every edge carries its stored target_kind, classified at extraction time:
 *   workspace = another ingested object (solid, clickable)
 *   external  = not in the system: SAP standard or genuinely missing (dashed)
 *   internal  = defined inside the object itself (FORMs, local classes) —
 *               implementation detail, omitted from the dependency view unless
 *               the object has nothing else to show
 */
import { query } from "../db/client";

export type DiagramTargetKind = "workspace" | "external" | "internal";

export interface DiagramEdge {
  from: string;
  to: string;
  kind: string;
  targetKind: DiagramTargetKind;
}

export interface ObjectDiagram {
  mermaid: string;
  /** true when the fallback rendered internal routines because the object has
   *  no workspace/external dependencies at all */
  internalOnly: boolean;
}

function nodeId(name: string): string {
  return "n_" + name.replace(/[^A-Za-z0-9_]/g, "_").toLowerCase();
}

/**
 * SAP-standard name heuristic for external targets: function modules outside
 * the customer namespace (names not starting with Z, Y or a /partner/
 * namespace) and the standard BAPI_/CL_/IF_/CX_ prefixes. Only refines the
 * label of an already-external node — never part of classification.
 */
export function isSapStandardName(name: string, kind: string): boolean {
  if (/^(BAPI_|CL_|IF_|CX_)/.test(name)) return true;
  return kind === "function" && !/^[ZY/]/.test(name);
}

const KIND_RANK: Record<DiagramTargetKind, number> = { workspace: 0, internal: 1, external: 2 };

/** Pure function: edges → Mermaid flowchart. Deterministic (sorted). */
export function edgesToMermaid(edges: DiagramEdge[], focus?: string): string {
  const lines: string[] = ["graph LR"];
  // name -> strongest node class seen on any edge (workspace > internal > external)
  const nodes = new Map<string, DiagramTargetKind>();
  const edgeKindByTarget = new Map<string, string>();
  for (const e of [...edges].sort((a, b) => (a.from + a.to).localeCompare(b.from + b.to))) {
    if (!nodes.has(e.from)) nodes.set(e.from, "workspace");
    const prev = nodes.get(e.to);
    if (prev === undefined || KIND_RANK[e.targetKind] < KIND_RANK[prev]) nodes.set(e.to, e.targetKind);
    if (!edgeKindByTarget.has(e.to)) edgeKindByTarget.set(e.to, e.kind);
  }
  for (const [name, kind] of [...nodes.entries()].sort()) {
    const id = nodeId(name);
    const label =
      kind === "workspace"
        ? name
        : kind === "internal"
          ? `${name} (internal routine)`
          : isSapStandardName(name, edgeKindByTarget.get(name) ?? "")
            ? `${name} (SAP standard)`
            : `${name} (external)`;
    lines.push(`  ${id}["${label}"]`);
    if (focus && name === focus) lines.push(`  style ${id} fill:#F04E0D,color:#fff`);
    else if (kind === "external") lines.push(`  style ${id} stroke-dasharray:4,fill:#FAF8F5`);
    else if (kind === "internal") lines.push(`  style ${id} fill:#FAF8F5,color:#A49C95,stroke:#E8E2DB`);
  }
  const seen = new Set<string>();
  for (const e of [...edges].sort((a, b) => (a.from + a.to + a.kind).localeCompare(b.from + b.to + b.kind))) {
    const key = `${e.from}->${e.to}`;
    if (seen.has(key)) continue;
    seen.add(key);
    const arrow = e.targetKind === "workspace" ? "-->" : "-.->";
    lines.push(`  ${nodeId(e.from)} ${arrow}|${e.kind}| ${nodeId(e.to)}`);
  }
  return lines.join("\n");
}

/**
 * Pure function: an object's inbound + outbound edges → its dependency
 * diagram. Internal edges are omitted; when the object has ONLY internal
 * structure, they render as muted internal-routine nodes instead of an empty
 * box (internalOnly flags the caption for that case).
 */
export function buildObjectDiagram(objectName: string, edges: DiagramEdge[]): ObjectDiagram {
  const dependencies = edges.filter((e) => e.targetKind !== "internal");
  if (dependencies.length > 0) return { mermaid: edgesToMermaid(dependencies, objectName), internalOnly: false };
  const internal = edges.filter((e) => e.targetKind === "internal");
  if (internal.length > 0) return { mermaid: edgesToMermaid(internal, objectName), internalOnly: true };
  return {
    mermaid: `graph LR\n  ${nodeId(objectName)}["${objectName}"]\n  style ${nodeId(objectName)} fill:#F04E0D,color:#fff`,
    internalOnly: false,
  };
}

/** Load the 1-hop neighborhood of an object and compute its diagram. */
export async function diagramForObject(workspaceId: string, objectName: string): Promise<ObjectDiagram | null> {
  const obj = await query<{ id: string; name: string }>(
    `select id, name from objects where workspace_id = $1 and name = $2 limit 1`,
    [workspaceId, objectName.toUpperCase()]
  );
  if (obj.length === 0) return null;

  // legacy rows (target_kind null) fall back to the resolution bit — the
  // backfill script upgrades them to real classifications
  const outbound = await query<{ callee_name: string; kind: string; target_kind: DiagramTargetKind }>(
    `select callee_name, kind,
            coalesce(target_kind, case when callee_id is null then 'external' else 'workspace' end) as target_kind
     from call_edges where workspace_id = $1 and caller_id = $2
     order by callee_name limit 40`,
    [workspaceId, obj[0].id]
  );
  const inbound = await query<{ caller_name: string; kind: string }>(
    `select o.name as caller_name, e.kind
     from call_edges e join objects o on o.id = e.caller_id
     where e.workspace_id = $1 and (e.callee_id = $2 or e.callee_name = $3)
       and coalesce(e.target_kind, '') <> 'internal'
     order by o.name limit 40`,
    [workspaceId, obj[0].id, obj[0].name]
  );

  const edges: DiagramEdge[] = [
    ...inbound.map((e) => ({ from: e.caller_name, to: obj[0].name, kind: e.kind, targetKind: "workspace" as const })),
    ...outbound.map((e) => ({ from: obj[0].name, to: e.callee_name, kind: e.kind, targetKind: e.target_kind })),
  ];
  return buildObjectDiagram(obj[0].name, edges);
}
