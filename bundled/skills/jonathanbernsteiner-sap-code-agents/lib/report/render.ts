/**
 * Report renderers (MD/CSV) — used by the export API. Pure formatting over
 * lib/report/data.ts: no LLM anywhere near the numbers.
 *
 * Section order (report restructure, identical on-screen and in MD):
 *   metadata & run snapshot (one merged table) → executive summary →
 *   object inventory & disposition (carries the retirement columns) →
 *   Tier 1 grouped by rule → Tier 2 grouped by object → Tier 3.
 * Exactly two data surfaces: the per-object action table and the per-finding
 * evidence sections. CSV: columns unchanged; rows follow the same order
 * (data.findings is already sorted Tier 1 by rule, Tier 2/3 by object).
 */
import { PRODUCT_NAME } from "../config";
import { isRepoUrl } from "../source-links";
import {
  DISPOSITION_LABELS,
  gradeDistributionLine,
  retirementStatement,
  type ReportData,
  type ReportFindingRow,
} from "./data";
import { findingStatement } from "./finding-title";
import { NOT_AVAILABLE, NO_VALUE } from "../empty-values";

const CATEGORY_LABELS: Record<string, string> = {
  abap: "ABAP programs & classes",
  enhancement: "Enhancements",
  custom_table: "Custom tables",
  interface: "Interfaces",
};

export function categoryLabel(category: string | null): string {
  return CATEGORY_LABELS[category ?? ""] ?? category ?? "Uncategorized";
}

export { methodologyParagraphs, SIMPL_LIST_URL } from "./methodology";
import { methodologyParagraphs } from "./methodology";

function usageStatus(data: ReportData): string {
  if (!data.has_usage_data) return `${NOT_AVAILABLE} — no execution statistics for this system`;
  return data.simulated_usage ? "present — SIMULATED (synthetic usage data, deterministic model)" : "present";
}

/**
 * One merged table: report identity + the run's frozen snapshot numbers.
 * (Previously two tables — "Report metadata" and "Run snapshot" — that
 * repeated each other's object count, grades and usage rows.)
 */
export function metadataSnapshotPairs(data: ReportData, opts: { mdLinks?: boolean } = {}): [string, string][] {
  // provenance: repo URLs become links in Markdown (plain URLs elsewhere);
  // fixture markers ("fixtures", "abapgit-cache") stay plain text
  const source = opts.mdLinks && isRepoUrl(data.source) ? `<${data.source}>` : data.source;
  const pairs: [string, string][] = [
    ["System", data.workspace],
    ["Source", source],
    ["Generated at", data.run ? new Date(data.run.finished_at).toISOString() : "no report run recorded"],
    ["Report run ID", data.run?.id ?? NOT_AVAILABLE],
    ["Objects analyzed", String(data.run?.objects_analyzed ?? data.headline.total_objects)],
    ["Parse success rate", data.headline.parse_rate],
  ];
  const snap = data.snapshot;
  if (!snap) {
    pairs.push(["Usage data", usageStatus(data)], ["Risk grades", gradeDistributionLine(data)]);
    return pairs;
  }
  const sim = snap.usage.simulated ? " — SIMULATED (synthetic usage data, deterministic model)" : "";
  pairs.push(
    ["Tier 1 findings (machine-verified)", String(snap.tiers["1"])],
    ["Tier 2 findings (evidence-linked)", String(snap.tiers["2"])],
    ["Affected objects (Tier 1+2)", String(snap.affected_objects)],
    ["Risk grades", gradeDistributionLine(data)],
    [
      "Usage data",
      snap.usage.rows === 0
        ? `${NOT_AVAILABLE} — no execution statistics for this system`
        : `${snap.usage.coverage_pct}% coverage (${snap.usage.rows} of ${snap.total_objects} objects)${sim}`,
    ],
    ["Object categories", snap.categories.map((c) => `${categoryLabel(c.category)}: ${c.n}`).join(" · ")],
    [
      `Retirement candidates${snap.usage.simulated ? " (simulated usage)" : ""}`,
      snap.retirement_candidates === null ? `${NOT_AVAILABLE} — no usage data` : String(snap.retirement_candidates),
    ]
  );
  if (data.findings_in_retirement && data.findings_in_retirement.tier1 + data.findings_in_retirement.tier2 > 0) {
    pairs.push([
      "Findings in retirement candidates",
      `${data.findings_in_retirement.tier1} Tier-1 · ${data.findings_in_retirement.tier2} Tier-2 — leave scope if retired instead of fixed`,
    ]);
  }
  return pairs;
}

/**
 * The grade↔finding relationship, stated once where grades first appear.
 * Shared verbatim by the MD and PDF renderers.
 */
export const GRADE_ROLLUP_NOTE =
  "A risk grade rolls up each object's findings — worst finding wins: " +
  "D = uses a construct removed outright (redesign), C = machine-verified but adaptable findings (adapt), " +
  "B = evidence-linked findings only (expert review), A = clean.";

/** Stable grouping helper that preserves the incoming (already sorted) order. */
function groupBy<T>(rows: T[], key: (r: T) => string): Map<string, T[]> {
  const groups = new Map<string, T[]>();
  for (const row of rows) {
    const k = key(row);
    const list = groups.get(k) ?? [];
    list.push(row);
    groups.set(k, list);
  }
  return groups;
}

function evidenceBlock(f: ReportFindingRow): string {
  if (!f.evidence) return "";
  const one = (file: string | null, line: number | null, evidence: string) => {
    const loc = `${file ?? "quote not located"}${line ? `:${line}` : ""}`;
    const quoted = evidence
      .split("\n")
      .map((l) => `> ${l}`)
      .join("\n");
    return `> \`${loc}\`\n>\n> \`\`\`abap\n${quoted}\n> \`\`\`\n\n`;
  };
  let out = one(f.evidence_file, f.evidence_line, f.evidence);
  // CO-08: merged root-cause findings list every citation
  for (const e of f.extra_evidence ?? []) {
    if (e.evidence) out += one(e.file, e.line, e.evidence);
  }
  return out;
}

function instanceLine(f: ReportFindingRow): string {
  // Object · Finding · Category · Process areas · Location — the finding
  // statement makes two hits on one object read as two rows, not a duplicate
  const chips = [categoryLabel(f.category), ...(f.process_areas ?? [])].join(" · ");
  const loc = f.evidence_file ? ` — \`${f.evidence_file}:${f.evidence_line}\`` : "";
  return `**${f.object_name}** — ${findingStatement(f)} (${chips})${loc}\n\n${evidenceBlock(f)}`;
}

/** Tier 1 — grouped by rule: title, SAP Note, explanation and replacement
 *  stated once; beneath it the compact instances. */
function tier1Section(rows: ReportFindingRow[]): string | null {
  if (rows.length === 0) return null;
  const groups = groupBy(rows, (f) => f.rule_id ?? "(no rule)");
  const body = [...groups.entries()]
    .map(([ruleId, list]) => {
      const first = list[0];
      const note = first.sap_note
        ? ` — SAP Note ${first.sap_note} (https://me.sap.com/notes/${first.sap_note}), verified`
        : "";
      const header = `### ${first.rule_title ?? ruleId}${note} · ${list.length} finding${list.length === 1 ? "" : "s"}`;
      const simplItem = first.simplification_item
        ? `Simplification item: ${first.simplification_item}${first.verified_release ? ` (verified against the ${first.verified_release} documentation set)` : ""}\n\n`
        : "";
      const explanation = first.rule_description ? `${first.rule_description}\n\n` : "";
      // CO-07: the primary source, quoted verbatim with its page-anchored link
      const sourceQuote = first.source_excerpt
        ? `> Source (Simplification List, verbatim${first.excerpt_source_url ? `, ${first.excerpt_source_url}` : ""}):\n> "${first.source_excerpt}"\n\n`
        : "";
      // Tertiary link: SAP-authored public page only, kept as muted further reading
      const furtherReading = first.source_url ? `Further reading: ${first.source_url}\n\n` : "";
      const effort = first.remediation_effort
        ? `Remediation effort (seeded band): ${first.remediation_effort}${first.effort_rationale ? ` — ${first.effort_rationale}` : ""}\n\n`
        : "";
      const replacement = first.replacement ? `Replacement: ${first.replacement}\n\n` : "";
      return `${header}\n\n${simplItem}${explanation}${sourceQuote}${replacement}${effort}${furtherReading}${list.map(instanceLine).join("")}`;
    })
    .join("\n");
  return (
    `## Tier 1 — machine-verified by deterministic validators (${rows.length})\n\n` +
    `Grouped by incompatibility rule. Each block covers one S/4HANA change: what changed, SAP's own source for it, the replacement — then every affected location in this system's code. Every finding below was confirmed by the rule's deterministic validator on the cited line.\n\n` +
    body
  );
}

/** Tier 2 — grouped by object: object header, findings as compact entries. */
function tier2Section(rows: ReportFindingRow[]): string | null {
  if (rows.length === 0) return null;
  const groups = groupBy(rows, (f) => f.object_name);
  const body = [...groups.entries()]
    .map(([objectName, list]) => {
      const first = list[0];
      const chips = [categoryLabel(first.category), ...(first.process_areas ?? [])].join(" · ");
      const entries = list
        .map(
          (f) =>
            `**${f.title}**${f.sap_note ? ` — SAP Note ${f.sap_note}` : ""}\n\n${f.detail}\n\n${evidenceBlock(f)}`
        )
        .join("");
      return `### ${objectName} (${chips})\n\n${entries}`;
    })
    .join("\n");
  return (
    `## Tier 2 — evidence-linked, needs expert review (${rows.length})\n\n` +
    `Grouped by object. Each finding cites a real line located verbatim in the stored source; these findings are not tied to a specific verified SAP Note — that is exactly why they need expert confirmation.\n\n` +
    body
  );
}

function tier3Section(rows: ReportFindingRow[]): string | null {
  if (rows.length === 0) return null;
  const body = rows
    .map((f) => `### ${f.object_name} — ${f.title}\n\n${f.detail}\n\n${evidenceBlock(f)}`)
    .join("\n");
  return (
    `## Tier 3 — unverified observations from this run (${rows.length})\n\n` +
    `Transient by design: these citations could not be located verbatim in the stored source, so they are never counted in headline numbers and are not persisted across runs (Tiers 1–2 are stable and carried forward; Tier 3 is per-run scratch).\n\n` +
    body
  );
}

/**
 * The disposition derivation rule, stated at the point of consumption (the
 * table intro doubles as the column-header explanation in MD). Shared by the
 * MD and PDF renderers; the on-screen table states the same rule.
 */
export const DISPOSITION_RULE_NOTE =
  "The disposition is derived by fixed rule, never by judgment: zero calls in 24 months and zero inbound " +
  "references → Retire (dead code is deleted, not fixed — these rows ARE the retirement candidates); " +
  "otherwise grade D → Redesign, C → Adapt, B → Expert review, A → Keep.";

/** CO-09 — the consultant's working table: one row per object, including the
 *  retirement evidence (calls, last executed, inbound refs). */
function inventorySection(data: ReportData): string | null {
  if (data.inventory.length === 0) return null;
  const usageNote = retirementStatement(data);
  // the section title carries the SIMULATED badge, so the usage cells stay
  // unsuffixed — one label per table, not one per cell
  const rows = data.inventory
    .map((r) => {
      const usage = r.call_count_24m === null ? NO_VALUE : String(r.call_count_24m);
      const lastExec = r.last_executed ? String(r.last_executed).slice(0, 10) : NO_VALUE;
      const disposition = r.disposition ? DISPOSITION_LABELS[r.disposition] ?? r.disposition : "ungraded";
      return `| ${r.name} | ${r.object_type} | ${(r.process_areas ?? []).join("; ") || NO_VALUE} | ${r.grade ?? NO_VALUE} | ${r.tier1_n} | ${r.tier2_n} | ${usage} | ${lastExec} | ${r.inbound_refs} | ${disposition} |`;
    })
    .join("\n");
  return (
    `## Object inventory & disposition${data.simulated_usage ? " — usage is SIMULATED" : ""}\n\n` +
    `One row per object — the action list of this report. ${DISPOSITION_RULE_NOTE}` +
    (usageNote ? ` ${usageNote}` : "") +
    `\n\n` +
    `| Object | Type | Process areas | Grade | Tier 1 · machine-verified | Tier 2 · evidence-linked | Calls (24m) | Last executed | Inbound refs | Disposition |\n` +
    `| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n` +
    rows
  );
}

export function renderMarkdown(data: ReportData): string {
  const byTier = (t: number) => data.findings.filter((f) => f.tier === t);

  const sections = [
    `## Executive summary\n\n${
      data.executive_summary ??
      "No report run yet — the executive summary is generated when a run finishes."
    }${data.recommended_actions ? `\n\n**${data.recommended_actions}**` : ""}`,
    inventorySection(data),
    tier1Section(byTier(1)),
    tier2Section(byTier(2)),
    tier3Section(byTier(3)),
    `## Methodology & data provenance\n\n` +
      methodologyParagraphs(data)
        .map((p) => `**${p.heading}.** ${p.text}`)
        .join("\n\n"),
  ].filter(Boolean);

  return `# S/4HANA migration report — ${data.workspace}

Generated by ${PRODUCT_NAME}. Evidence tiers, used throughout: **Tier 1 —
machine-verified** (a rule-specific deterministic validator confirmed the
incompatibility on the cited line); **Tier 2 — evidence-linked** (the citation
was located verbatim in the stored source; an expert must confirm the
interpretation); **Tier 3 — unverified** observations, excluded from every
headline number. All counts are computed by SQL.
${data.simulated_usage ? `\n> **Note:** usage statistics in this system are **SIMULATED** (synthetic usage data, deterministic model).\n` : ""}
## Report metadata & run snapshot

What was analyzed and the run's frozen headline numbers — one table, every
number computed by SQL when the run finished. ${GRADE_ROLLUP_NOTE}

| Field | Value |
| --- | --- |
${metadataSnapshotPairs(data, { mdLinks: true })
  .map(([k, v]) => `| ${k} | ${v} |`)
  .join("\n")}

${sections.join("\n\n")}
`;
}

/**
 * CO-09 — the CSV is a ready-to-use triage worklist: one header row (no
 * comment lines — imports clean into Excel/Power Query), one row per finding
 * carrying the object's grade, disposition and usage, and four empty triage
 * columns (status, assigned_to, decision, comment) for the review team to
 * fill in. System + run id are columns so multi-system workbooks stay
 * traceable.
 */
export const CSV_HEADER =
  "system,run_id,tier,object,object_type,grade,disposition,finding,severity,remediation_effort," +
  "sap_note,simplification_item,process_areas,evidence_file,evidence_line,evidence,extra_locations," +
  "validator,validator_passed,replacement,detail,calls_24m,inbound_refs,status,assigned_to,decision,comment";

export function renderCsv(data: ReportData): string {
  const esc = (v: unknown) => `"${String(v ?? "").replace(/"/g, '""')}"`;
  const byObject = new Map(data.inventory.map((r) => [r.name, r]));
  const rows = data.findings.map((f) => {
    const inv = byObject.get(f.object_name);
    const extraLocations = (f.extra_evidence ?? [])
      .map((e) => `${e.file ?? "?"}:${e.line ?? "?"}`)
      .join("; ");
    return [
      data.workspace,
      data.run?.id ?? "",
      f.tier,
      f.object_name,
      f.object_type,
      inv?.grade ?? "",
      inv?.disposition ?? "",
      f.title,
      f.rule_severity ?? "",
      f.remediation_effort ?? "",
      f.sap_note,
      f.simplification_item ?? "",
      (f.process_areas ?? []).join("; "),
      f.evidence_file,
      f.evidence_line,
      f.evidence,
      extraLocations,
      f.validator,
      f.validator_passed,
      f.replacement,
      f.detail,
      inv?.call_count_24m != null ? `${inv.call_count_24m}${inv.usage_simulated ? " (simulated)" : ""}` : "",
      inv?.inbound_refs ?? "",
      "", // status — triage column, intentionally empty
      "", // assigned_to
      "", // decision
      "", // comment
    ]
      .map(esc)
      .join(",");
  });
  return [CSV_HEADER, ...rows].join("\n") + "\n";
}
