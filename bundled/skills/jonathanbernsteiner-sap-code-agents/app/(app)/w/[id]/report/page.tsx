"use client";

/**
 * Migration Report tab (report restructure). Section order:
 *   executive summary → run snapshot (frozen per run) → object inventory &
 *   disposition (carries the retirement columns) → Tier 1 grouped by rule →
 *   Tier 2 grouped by object → Tier 3 collapsed → findings register (flat,
 *   mirrors the CSV export) → run history.
 * The MD/CSV exports (lib/report/render.ts) follow the same order.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import Card from "../../../../../components/ui/Card";
import DataTable from "../../../../../components/ui/DataTable";
import RunSummary from "../../../../../components/RunSummary";
import CollapsibleCard from "../../../../../components/ui/CollapsibleCard";
import ReportPipelineCard from "../../../../../components/ReportPipelineCard";
import { useReportRun, type HistoryEntry } from "../../../../../components/useReportRun";
import { buildRepoFileUrl, isRepoUrl, repoBaseUrl, repoDisplayName } from "../../../../../lib/source-links";
import { methodologyParagraphs } from "../../../../../lib/report/methodology";
import { findingStatement } from "../../../../../lib/report/finding-title";
import { NOT_AVAILABLE, NO_VALUE } from "../../../../../lib/empty-values";

interface Finding {
  object_name: string;
  object_type: string;
  category: string | null;
  rule_id: string | null;
  tier: number;
  title: string;
  detail: string;
  evidence_file: string | null;
  evidence_line: number | null;
  evidence: string | null;
  validator: string | null;
  validator_passed: boolean | null;
  suppression_reason: string | null;
  sap_note: string | null;
  simplification_item: string | null;
  source_url: string | null;
  replacement: string | null;
  rule_title: string | null;
  rule_description: string | null;
  rule_severity: string | null;
  remediation_effort: string | null;
  effort_rationale: string | null;
  verified_release: string | null;
  source_excerpt: string | null;
  excerpt_source_url: string | null;
  process_areas: string[] | null;
  extra_evidence: { file: string | null; line: number | null; evidence: string | null }[] | null;
}

interface RunSnapshot {
  total_objects: number;
  parse_ok: number;
  tiers: { "1": number; "2": number; "3": number };
  affected_objects: number;
  grades: Record<string, number>;
  usage: { rows: number; coverage_pct: number; simulated: boolean };
  categories: { category: string | null; n: number }[];
  retirement_candidates: number | null;
}

interface ReportData {
  workspace: string;
  source: string;
  source_branch: string | null;
  kind: string;
  simulated_usage: boolean;
  has_usage_data: boolean;
  run: { id: string; finished_at: string; objects_analyzed: number | null } | null;
  executive_summary: string | null;
  snapshot: RunSnapshot | null;
  grades: { A: number; B: number; C: number; D: number } | null;
  headline: {
    tier1: number;
    tier2: number;
    tier3: number;
    affected_objects: number;
    total_objects: number;
    parse_rate: string;
  };
  findings: Finding[];
  retirement: { name: string; object_type: string; call_count_24m: string; last_executed: string | null; simulated: boolean }[];
  inventory: InventoryRow[];
  findings_in_retirement: { tier1: number; tier2: number } | null;
  recommended_actions: string | null;
  suppressed?: Finding[];
}

interface InventoryRow {
  name: string;
  object_type: string;
  category: string | null;
  process_areas: string[] | null;
  grade: string | null;
  disposition: string | null;
  is_retirement_candidate: boolean;
  tier1_n: number;
  tier2_n: number;
  call_count_24m: string | null;
  last_executed: string | null;
  usage_simulated: boolean | null;
  inbound_refs: number;
}

const DISPOSITION_STYLES: Record<string, { label: string; color: string; backgroundColor: string }> = {
  retire: { label: "Retire", color: "#CC420B", backgroundColor: "#FCEDE4" },
  redesign: { label: "Redesign", color: "#CC420B", backgroundColor: "#FCEDE4" },
  adapt: { label: "Adapt", color: "#6E6660", backgroundColor: "#F0EDE8" },
  review: { label: "Expert review", color: "#6E6660", backgroundColor: "#F0EDE8" },
  keep: { label: "Keep", color: "#A49C95", backgroundColor: "#FAF8F5" },
};

const CATEGORY_LABELS: Record<string, string> = {
  abap: "ABAP programs & classes",
  enhancement: "Enhancements",
  custom_table: "Custom tables",
  interface: "Interfaces",
};
const categoryLabel = (c: string | null) => CATEGORY_LABELS[c ?? ""] ?? c ?? "Uncategorized";

export default function ReportTab() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const selected = decodeURIComponent(params.id);
  const [data, setData] = useState<ReportData | null>(null);
  const [debug, setDebug] = useState(false);

  const wsPath = (tab: string, qs = "") => `/w/${encodeURIComponent(selected)}/${tab}${qs}`;

  useEffect(() => {
    setDebug(new URLSearchParams(window.location.search).get("debug") === "1");
  }, []);

  // Guards against a slow response for a previously selected system painting
  // over the current one (fast switches), and swallows network errors.
  const loadSeq = useRef(0);
  const loadReport = useCallback(() => {
    if (!selected) return;
    const seq = ++loadSeq.current;
    fetch(`/api/report?workspace=${encodeURIComponent(selected)}${debug ? "&debug=1" : ""}`)
      .then((r) => r.json())
      .then((d) => {
        if (seq === loadSeq.current) setData(d);
      })
      .catch(() => {});
  }, [selected, debug]);

  // CO-06 — the run is started and watched through the shared hook, so the
  // Overview and this tab behave identically; when it finishes, reload the
  // report rendered below it.
  const { status: runStatus, runActive, showPipeline, startRun, runError } = useReportRun(
    selected,
    loadReport
  );

  useEffect(() => {
    if (!selected) return;
    setData(null);
    loadReport();
  }, [selected, debug, loadReport]);

  const tiered = (t: number) => (data?.findings ?? []).filter((f) => f.tier === t);
  const snap = data?.snapshot ?? null;
  // file:line citations deep-link into the repo for ingested systems only —
  // fixture systems have no public file URLs
  const fileUrl = useCallback(
    (path: string | null, line?: number | null): string | null =>
      data?.kind === "ingested" && path ? buildRepoFileUrl(data.source, data.source_branch, path, line) : null,
    [data?.kind, data?.source, data?.source_branch]
  );

  return (
    <div style={{ padding: 24, display: "flex", flexDirection: "column", gap: 16 }}>
      {/* actions */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2 style={{ fontSize: 16, fontWeight: 600, margin: 0 }}>S/4HANA migration report</h2>
        <div className="print:hidden" style={{ display: "flex", gap: 8 }}>
          {data && data.kind !== "example" && (
            <button
              onClick={startRun}
              disabled={runActive}
              style={{ fontSize: 13, fontWeight: 600, color: runActive ? "#A49C95" : "#1B1817", backgroundColor: "#FFFFFF", border: "1px solid #E8E2DB", borderRadius: 8, padding: "8px 14px", cursor: runActive ? "default" : "pointer", fontFamily: "inherit" }}
            >
              {runActive ? "Report running…" : data.run ? "Re-run report" : "Run migration report"}
            </button>
          )}
          {/* All actions share the flat secondary style. Server-rendered
              PDF (lib/report/pdf.ts) downloads directly, no print dialog. */}
          <a
            href={`/api/report/export?workspace=${encodeURIComponent(selected)}&format=pdf`}
            style={{ fontSize: 13, fontWeight: 600, color: "#1B1817", backgroundColor: "#FFFFFF", border: "1px solid #E8E2DB", borderRadius: 8, padding: "8px 14px", textDecoration: "none" }}
          >
            Export PDF
          </a>
          <a
            href={`/api/report/export?workspace=${encodeURIComponent(selected)}&format=csv`}
            style={{ fontSize: 13, fontWeight: 600, color: "#1B1817", backgroundColor: "#FFFFFF", border: "1px solid #E8E2DB", borderRadius: 8, padding: "8px 14px", textDecoration: "none" }}
          >
            Export CSV
          </a>
          <a
            href={`/api/report/export?workspace=${encodeURIComponent(selected)}&format=md`}
            style={{ fontSize: 13, fontWeight: 600, color: "#1B1817", backgroundColor: "#FFFFFF", border: "1px solid #E8E2DB", borderRadius: 8, padding: "8px 14px", textDecoration: "none" }}
          >
            Export Markdown
          </a>
        </div>
      </div>

      {runError && (
        <div className="print:hidden" style={{ fontSize: 13, color: "#CC420B", backgroundColor: "#FCEDE4", border: "1px solid #F6D9CB", borderRadius: 8, padding: "10px 12px" }}>
          {runError}
        </div>
      )}

      {/* CO-06 — live pipeline while a run is active; a failed run keeps its
          failing stage + error visible */}
      {showPipeline && runStatus && <ReportPipelineCard status={runStatus} />}

      {!data && <Card><p style={{ fontSize: 14, color: "#A49C95" }}>Loading…</p></Card>}

      {data && !data.run && (
        <Card>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>No report run yet</h3>
          <p style={{ fontSize: 13, color: "#6E6660" }}>
            {data.kind === "example"
              ? "Example systems are refreshed by the operator via `npm run report`."
              : "Use “Run migration report” to analyze this system."}
          </p>
        </Card>
      )}

      {data && (
        <>
          {/* 1 — executive summary */}
          {data.run && (
            <Card>
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 8 }}>Executive summary</h3>
              <p style={{ fontSize: 14, color: "#1B1817", lineHeight: 1.6, margin: 0 }}>
                {data.executive_summary}
              </p>
              {data.recommended_actions && (
                <p style={{ fontSize: 13.5, fontWeight: 600, color: "#1B1817", lineHeight: 1.6, marginTop: 10, marginBottom: 0 }}>
                  {data.recommended_actions}
                </p>
              )}
              <p style={{ fontSize: 11, color: "#A49C95", marginTop: 10, marginBottom: 0 }}>
                Generated prose (traced LLM call) — every number is injected from SQL and checked against
                the run snapshot; a summary that invents numbers is rejected and replaced deterministically.
                The recommended next steps line is a deterministic template over the disposition counts.
              </p>
            </Card>
          )}

          {/* 2 — run snapshot (frozen per run). Collapsed on screen: the
              Overview one tab away is the dashboard, so on this page the
              snapshot is provenance you open when you want it. The MD/PDF
              exports keep it expanded — a standalone document cannot lean on
              another tab existing. */}
          {data.run && snap && (
            <CollapsibleCard
              primary
              title={
                <>
                  Run snapshot
                  <span style={{ marginLeft: 8, fontSize: 11, fontWeight: 400, color: "#A49C95", fontFamily: "JetBrains Mono, monospace" }}>
                    run {data.run.id.slice(0, 8)} · {String(data.run.finished_at).slice(0, 16).replace("T", " ")} · Tier 1: {snap.tiers["1"]} · Tier 2: {snap.tiers["2"]}
                  </span>
                </>
              }
            >
              <p style={{ fontSize: 12, color: "#A49C95", marginTop: 0, marginBottom: 14 }}>
                The headline numbers of this analysis run, frozen when it finished. Every number is
                computed directly from the database; unverified observations (Tier 3) are never counted.
                Source:{" "}
                {isRepoUrl(data.source) ? (
                  <a
                    href={repoBaseUrl(data.source)}
                    target="_blank"
                    rel="noreferrer"
                    style={{ color: "#6E6660", textDecoration: "none", borderBottom: "1px dotted #A49C95" }}
                  >
                    {repoDisplayName(data.source)} ↗
                  </a>
                ) : (
                  <span style={{ fontFamily: "JetBrains Mono, monospace" }}>{data.source}</span>
                )}{" "}
                · {data.run.objects_analyzed ?? snap.total_objects} objects analyzed · parse success {data.headline.parse_rate}
                {" · "}
                {snap.usage.rows === 0 ? (
                  `usage coverage ${NOT_AVAILABLE}`
                ) : (
                  <>
                    usage coverage {snap.usage.coverage_pct}% ({snap.usage.rows} of {snap.total_objects} objects)
                    {snap.usage.simulated && (
                      <span style={{ marginLeft: 6, fontSize: 10, fontWeight: 600, color: "#CC420B", backgroundColor: "#FCEDE4", borderRadius: 5, padding: "1px 6px" }}>
                        SIMULATED
                      </span>
                    )}
                  </>
                )}
              </p>

              {/* identical to the Overview's card — one component, so the
                  same run is never described in two shapes */}
              <RunSummary
                totalObjects={data.run.objects_analyzed ?? snap.total_objects}
                grades={{ ...snap.grades, Ungraded: snap.grades.Ungraded ?? 0 }}
                tier1={snap.tiers["1"]}
                tier2={snap.tiers["2"]}
                affectedObjects={snap.affected_objects}
                retirementCandidates={snap.retirement_candidates}
                recommendation={data.recommended_actions}
                onGradeClick={(g) => router.push(wsPath("objects", `?grade=${encodeURIComponent(g)}`))}
              />
            </CollapsibleCard>
          )}

          {/* CO-09 — object inventory & disposition: the working table (one
              row per object, incl. the retirement evidence columns) */}
          {data.run && data.inventory.length > 0 && (
            <CollapsibleCard
              primary
              defaultOpen
              title={
                <>
                  Object inventory &amp; disposition ({data.inventory.length} objects)
                  {data.simulated_usage && (
                    <span style={{ marginLeft: 8, fontSize: 11, fontWeight: 600, color: "#CC420B", backgroundColor: "#FCEDE4", borderRadius: 6, padding: "2px 8px" }}>
                      SIMULATED USAGE DATA
                    </span>
                  )}
                </>
              }
            >
              <p style={{ fontSize: 12, color: "#A49C95", marginTop: 0, marginBottom: 12 }}>
                One row per object — the action list of this report. The disposition is derived by
                fixed rule, never by judgment: zero calls in 24 months and zero inbound references
                → Retire (dead code is deleted, not fixed — these rows are the retirement
                candidates); otherwise grade D → Redesign, C → Adapt, B → Expert review, A → Keep.
                {!data.has_usage_data && (
                  <> No usage data is available for this system — retirement analysis requires execution statistics.</>
                )}
                {data.has_usage_data && data.retirement.length === 0 && (
                  <> Usage data present; no objects met the retirement criteria.</>
                )}
                {data.findings_in_retirement && data.findings_in_retirement.tier1 + data.findings_in_retirement.tier2 > 0 && (
                  <>
                    {" "}
                    <span style={{ color: "#CC420B", fontWeight: 600 }}>
                      {data.findings_in_retirement.tier1} Tier-1 and {data.findings_in_retirement.tier2} Tier-2 findings sit in
                      retirement candidates — they leave the scope by deletion, not by fixing.
                    </span>
                  </>
                )}
              </p>
              <DataTable
                rows={data.inventory}
                rowKey={(r) => r.name}
                columns={[
                  {
                    header: "Object",
                    render: (r) => (
                      <span style={{ fontFamily: "JetBrains Mono, monospace", fontWeight: 600 }}>
                        <ObjectLink name={r.name} wsPath={wsPath} />
                      </span>
                    ),
                  },
                  { header: "Type", render: (r) => r.object_type, nowrap: true },
                  { header: "Grade", render: (r) => r.grade ?? NO_VALUE, nowrap: true },
                  { header: "Tier 1 · machine-verified", render: (r) => String(r.tier1_n), nowrap: true },
                  { header: "Tier 2 · evidence-linked", render: (r) => String(r.tier2_n), nowrap: true },
                  {
                    // the card header carries the SIMULATED badge — no
                    // per-cell suffix
                    header: "Calls (24m)",
                    render: (r) =>
                      r.call_count_24m === null ? NO_VALUE : Number(r.call_count_24m).toLocaleString("en-US"),
                    nowrap: true,
                  },
                  {
                    header: "Last executed",
                    render: (r) => (r.last_executed ? String(r.last_executed).slice(0, 10) : NO_VALUE),
                    nowrap: true,
                  },
                  { header: "Inbound refs", render: (r) => String(r.inbound_refs), nowrap: true },
                  {
                    header: "Disposition",
                    render: (r) => {
                      const s = r.disposition ? DISPOSITION_STYLES[r.disposition] : null;
                      return s ? (
                        <span style={{ fontSize: 11, fontWeight: 600, color: s.color, backgroundColor: s.backgroundColor, borderRadius: 6, padding: "2px 8px", whiteSpace: "nowrap" }}>
                          {s.label}
                        </span>
                      ) : (
                        <span style={{ color: "#A49C95" }}>ungraded</span>
                      );
                    },
                    nowrap: true,
                  },
                ]}
              />
            </CollapsibleCard>
          )}

          {/* 3 — Tier 1 grouped by rule */}
          <CollapsibleCard
            primary
            defaultOpen
            title={`Tier 1 — machine-verified by deterministic validators (${tiered(1).length})`}
          >
            <p style={{ fontSize: 12, color: "#A49C95", marginTop: 0, marginBottom: 12 }}>
              Code that will not work in S/4HANA, confirmed by automated checks on the cited line,
              grouped by incompatibility rule. Each block covers one S/4HANA change: what changed,
              SAP&apos;s own source for it, the replacement — then every affected location in this
              system&apos;s code.
            </p>
            <Tier1Groups findings={tiered(1)} wsPath={wsPath} fileUrl={fileUrl} />
          </CollapsibleCard>

          {/* 4 — Tier 2 grouped by object */}
          <CollapsibleCard
            primary
            defaultOpen
            title={`Tier 2 — evidence-linked, needs expert review (${tiered(2).length})`}
          >
            <p style={{ fontSize: 12, color: "#A49C95", marginTop: 0, marginBottom: 12 }}>
              Suspected issues a consultant should confirm, grouped by object. Each finding cites a
              real line from the stored source; Tier-2 findings are not tied to a specific SAP Note —
              that is exactly why they need expert confirmation.
            </p>
            <Tier2Groups findings={tiered(2)} wsPath={wsPath} fileUrl={fileUrl} />
          </CollapsibleCard>

          {/* 5 — Tier 3 (appendix: never counted, never persisted) */}
          <CollapsibleCard
            title={`Tier 3 — unverified observations from this run (${tiered(3).length}) — transient by design: not persisted across runs, never counted`}
          >
            <FlatFindingList findings={tiered(3)} fileUrl={fileUrl} />
          </CollapsibleCard>

          {/* 6 — findings register: the flat export table, one row per finding */}
          {data.run && data.findings.length > 0 && (
            <FindingsRegister findings={data.findings} wsPath={wsPath} fileUrl={fileUrl} />
          )}

          {debug && data.suppressed && (
            <CollapsibleCard
              accent
              title={`Suppressed findings (${data.suppressed.length}) — DEBUG VIEW, never in reports or exports`}
            >
              <FlatFindingList findings={data.suppressed} showSuppression fileUrl={fileUrl} />
            </CollapsibleCard>
          )}

          {/* methodology & data provenance — same text as the MD/PDF exports.
              Read-once trust appendix: folded, with its subject in the header. */}
          <CollapsibleCard title="Methodology &amp; data provenance — evidence tiers, rules and sources, grades, effort bands, usage">
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {methodologyParagraphs(data).map((p) => (
                <p key={p.heading} style={{ fontSize: 12.5, color: "#6E6660", lineHeight: 1.6, margin: 0 }}>
                  <span style={{ fontWeight: 600, color: "#1B1817" }}>{p.heading}.</span> {p.text}
                </p>
              ))}
            </div>
            <p style={{ fontSize: 12, color: "#A49C95", marginTop: 10, marginBottom: 0 }}>
              The full rule set is inspectable in the{" "}
              <Link href="/rules" style={{ color: "#CC420B", fontWeight: 600, textDecoration: "none" }}>
                S/4HANA rule catalog
              </Link>
              .
            </p>
          </CollapsibleCard>

          {/* 7 — run history: operational log, not part of the assessment.
              The header states the latest run so folding hides nothing. */}
          {(runStatus?.history?.length ?? 0) > 0 && (
            <CollapsibleCard
              title={`Run history (${runStatus!.history!.length}) — latest ${String(runStatus!.history![0].finished_at ?? runStatus!.history![0].started_at).slice(0, 16).replace("T", " ")}`}
            >
              <p style={{ fontSize: 12, color: "#A49C95", marginTop: 0, marginBottom: 12 }}>
                Numbers per run come from its frozen snapshot; findings are persisted for the latest run only.
              </p>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {runStatus!.history!.map((h, i) => (
                  <RunHistoryRow key={h.id} entry={h} latest={i === 0} currentRunId={data.run?.id ?? null} />
                ))}
              </div>
            </CollapsibleCard>
          )}
        </>
      )}
    </div>
  );
}

type FileUrlFn = (path: string | null, line?: number | null) => string | null;

function ObjectLink({ name, wsPath }: { name: string; wsPath: (tab: string, qs?: string) => string }) {
  return (
    <Link
      href={wsPath("objects", `?focus=${encodeURIComponent(name)}`)}
      style={{ color: "#1B1817", textDecoration: "none", borderBottom: "1px dotted #A49C95" }}
    >
      {name}
    </Link>
  );
}

function Chip({ children }: { children: React.ReactNode }) {
  return (
    <span style={{ fontSize: 11, fontWeight: 600, fontFamily: "DM Sans, sans-serif", color: "#6E6660", backgroundColor: "#F0EDE8", borderRadius: 6, padding: "1px 7px", whiteSpace: "nowrap" }}>
      {children}
    </span>
  );
}

/** file:line citation — a quiet link into the repo when one exists (ingested
 *  systems), plain text otherwise. Never competes with primary actions. */
function FileRef({ file, line, url }: { file: string | null; line: number | null; url: string | null }) {
  if (!file) return null;
  const label = `${file}${line ? `:${line}` : ""}`;
  if (!url) {
    return <span style={{ fontSize: 11, fontWeight: 400, fontFamily: "JetBrains Mono, monospace", color: "#A49C95" }}>{label}</span>;
  }
  return (
    <a
      href={url}
      target="_blank"
      rel="noreferrer"
      style={{ fontSize: 11, fontWeight: 400, fontFamily: "JetBrains Mono, monospace", color: "#6E6660", textDecoration: "none", borderBottom: "1px dotted #A49C95" }}
    >
      {label}
    </a>
  );
}

function EvidenceSnippet({ f, fileUrl }: { f: Finding; fileUrl: FileUrlFn }) {
  if (!f.evidence) return null;
  const citations: { file: string | null; line: number | null; evidence: string | null }[] = [
    { file: f.evidence_file, line: f.evidence_line, evidence: f.evidence },
    ...(f.extra_evidence ?? []),
  ];
  return (
    <div style={{ marginTop: 6, display: "flex", flexDirection: "column", gap: 6 }}>
      {citations.map(
        (c, i) =>
          c.evidence && (
            <div key={i}>
              {c.file && (
                <div style={{ marginBottom: 2 }}>
                  <FileRef file={c.file} line={c.line} url={fileUrl(c.file, c.line)} />
                </div>
              )}
              <pre style={{ fontSize: 12, fontFamily: "JetBrains Mono, monospace", backgroundColor: "#FAF8F5", border: "1px solid #E8E2DB", borderRadius: 6, padding: 8, margin: 0, whiteSpace: "pre-wrap" }}>
                {c.evidence}
              </pre>
            </div>
          )
      )}
    </div>
  );
}

/** Preserve the incoming (already sorted) order while grouping. */
function groupBy<T>(rows: T[], key: (r: T) => string): [string, T[]][] {
  const groups = new Map<string, T[]>();
  for (const row of rows) {
    const k = key(row);
    const list = groups.get(k) ?? [];
    list.push(row);
    groups.set(k, list);
  }
  return [...groups.entries()];
}

/** Tier 1 — one block per rule: title, SAP Note, explanation, replacement
 *  stated once; compact instances beneath. */
function Tier1Groups({ findings, wsPath, fileUrl }: { findings: Finding[]; wsPath: (tab: string, qs?: string) => string; fileUrl: FileUrlFn }) {
  if (findings.length === 0) return <p style={{ fontSize: 13, color: "#6E6660" }}>None.</p>;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
      {groupBy(findings, (f) => f.rule_id ?? "(no rule)").map(([ruleId, list]) => {
        const first = list[0];
        return (
          <div key={ruleId} style={{ borderLeft: "3px solid #F04E0D", paddingLeft: 12 }}>
            <div style={{ fontSize: 13.5, fontWeight: 600, color: "#1B1817" }}>
              {first.rule_title ?? ruleId}
              <span style={{ fontWeight: 400, color: "#6E6660" }}> · {list.length} finding{list.length === 1 ? "" : "s"}</span>
              {first.sap_note && (
                <>
                  {" · "}
                  <a href={`https://me.sap.com/notes/${first.sap_note}`} target="_blank" rel="noreferrer" style={{ color: "#CC420B", fontWeight: 600 }}>
                    SAP Note {first.sap_note}
                  </a>
                </>
              )}
              {first.source_url && (
                <>
                  {" · "}
                  <a href={first.source_url} target="_blank" rel="noreferrer" style={{ fontSize: 12, fontWeight: 400, color: "#6E6660", textDecoration: "none", borderBottom: "1px dotted #A49C95" }}>
                    further reading
                  </a>
                </>
              )}
              {" · "}
              <Link href={`/rules#${encodeURIComponent(ruleId)}`} style={{ fontSize: 12, fontWeight: 400, color: "#6E6660", textDecoration: "none", borderBottom: "1px dotted #A49C95" }}>
                view rule
              </Link>
              {first.rule_severity === "high" && (
                <span style={{ marginLeft: 8, fontSize: 11, fontWeight: 600, color: "#CC420B", backgroundColor: "#FCEDE4", borderRadius: 6, padding: "1px 7px", verticalAlign: "middle" }}>
                  severity high
                </span>
              )}
              {first.remediation_effort && (
                <span style={{ marginLeft: 6, fontSize: 11, fontWeight: 600, color: "#6E6660", backgroundColor: "#F0EDE8", borderRadius: 6, padding: "1px 7px", verticalAlign: "middle" }}>
                  effort {first.remediation_effort}
                </span>
              )}
            </div>
            {first.simplification_item && (
              <div style={{ fontSize: 11.5, color: "#A49C95", marginTop: 2 }}>
                Simplification item: {first.simplification_item}
                {first.verified_release ? ` · verified against the ${first.verified_release} documentation set` : ""}
              </div>
            )}
            {first.rule_description && (
              <p style={{ fontSize: 12.5, color: "#6E6660", marginTop: 4, marginBottom: 0 }}>{first.rule_description}</p>
            )}
            {/* CO-07: primary source, quoted verbatim, page-anchored public link */}
            {first.source_excerpt && (
              <blockquote style={{ borderLeft: "3px solid #E8E2DB", margin: "8px 0 0 0", padding: "2px 0 2px 12px" }}>
                <p style={{ fontSize: 12, color: "#6E6660", fontStyle: "italic", lineHeight: 1.55, margin: 0 }}>
                  “{first.source_excerpt}”
                </p>
                <div style={{ fontSize: 11, color: "#A49C95", marginTop: 3 }}>
                  — Simplification List for SAP S/4HANA 2023, quoted verbatim
                  {first.excerpt_source_url && (
                    <>
                      {" · "}
                      <a href={first.excerpt_source_url} target="_blank" rel="noreferrer" style={{ color: "#CC420B", fontWeight: 600, textDecoration: "none" }}>
                        p.{first.excerpt_source_url.split("#page=")[1]} ↗
                      </a>
                    </>
                  )}
                </div>
              </blockquote>
            )}
            {first.replacement && (
              <div style={{ fontSize: 12, color: "#1B1817", backgroundColor: "#FCEDE4", borderRadius: 6, padding: "6px 10px", marginTop: 6, display: "inline-block" }}>
                <span style={{ fontWeight: 600, color: "#CC420B" }}>Replacement: </span>
                {first.replacement}
              </div>
            )}
            <div style={{ marginTop: 10 }}>
              <DataTable
                rows={list}
                rowKey={(f, i) => `${f.object_name}:${f.evidence_line ?? i}`}
                columns={[
                  {
                    header: "Object",
                    render: (f) => (
                      <span style={{ fontFamily: "JetBrains Mono, monospace", fontWeight: 600 }}>
                        <ObjectLink name={f.object_name} wsPath={wsPath} />
                      </span>
                    ),
                  },
                  {
                    // two hits on one object (BSID line 29 vs BSAD line 37)
                    // must read as two rows, not a duplicate
                    header: "Finding",
                    render: (f) => <span style={{ color: "#1B1817" }}>{findingStatement(f)}</span>,
                  },
                  { header: "Category", render: (f) => categoryLabel(f.category), nowrap: true },
                  {
                    header: "Process areas",
                    render: (f) => ((f.process_areas ?? []).length > 0 ? (f.process_areas ?? []).join(" · ") : NO_VALUE),
                  },
                  {
                    header: "Location",
                    render: (f) =>
                      f.evidence_file ? (
                        <FileRef file={f.evidence_file} line={f.evidence_line} url={fileUrl(f.evidence_file, f.evidence_line)} />
                      ) : (
                        NO_VALUE
                      ),
                    nowrap: true,
                  },
                ]}
                expandContent={(f) =>
                  f.evidence ? (
                    <pre style={{ fontSize: 12, fontFamily: "JetBrains Mono, monospace", backgroundColor: "#FAF8F5", border: "1px solid #E8E2DB", borderRadius: 6, padding: 8, margin: 0, whiteSpace: "pre-wrap" }}>
                      {f.evidence}
                    </pre>
                  ) : null
                }
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

/** Tier 2 — one block per object: header with chips, compact finding entries. */
function Tier2Groups({ findings, wsPath, fileUrl }: { findings: Finding[]; wsPath: (tab: string, qs?: string) => string; fileUrl: FileUrlFn }) {
  if (findings.length === 0) return <p style={{ fontSize: 13, color: "#6E6660" }}>None.</p>;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
      {groupBy(findings, (f) => f.object_name).map(([objectName, list]) => {
        const first = list[0];
        return (
          <div key={objectName} style={{ borderLeft: "3px solid #A49C95", paddingLeft: 12 }}>
            <div style={{ fontSize: 13.5, fontWeight: 600, fontFamily: "JetBrains Mono, monospace", display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
              <ObjectLink name={objectName} wsPath={wsPath} />
              <Chip>{categoryLabel(first.category)}</Chip>
              {(first.process_areas ?? []).map((a) => (
                <Chip key={a}>{a}</Chip>
              ))}
              <span style={{ fontSize: 12, fontWeight: 400, fontFamily: "DM Sans, sans-serif", color: "#6E6660" }}>
                {list.length} finding{list.length === 1 ? "" : "s"}
              </span>
            </div>
            <div style={{ marginTop: 8 }}>
              <DataTable
                rows={list}
                rowKey={(f, i) => `${f.object_name}:${f.title}:${i}`}
                columns={[
                  {
                    header: "Finding",
                    render: (f) => <span style={{ fontWeight: 600, color: "#1B1817" }}>{f.title}</span>,
                  },
                  {
                    header: "SAP Note",
                    render: (f) =>
                      f.sap_note ? (
                        <a href={`https://me.sap.com/notes/${f.sap_note}`} target="_blank" rel="noreferrer" style={{ color: "#CC420B", fontWeight: 600, textDecoration: "none" }}>
                          {f.sap_note}
                        </a>
                      ) : (
                        NO_VALUE
                      ),
                    nowrap: true,
                  },
                  {
                    header: "Location",
                    render: (f) =>
                      f.evidence_file ? (
                        <>
                          <FileRef file={f.evidence_file} line={f.evidence_line} url={fileUrl(f.evidence_file, f.evidence_line)} />
                          {(f.extra_evidence?.length ?? 0) > 0 && (
                            <span style={{ fontSize: 11, color: "#A49C95", marginLeft: 6 }}>
                              +{f.extra_evidence!.length} more
                            </span>
                          )}
                        </>
                      ) : (
                        NO_VALUE
                      ),
                    nowrap: true,
                  },
                ]}
                expandContent={(f) => (
                  <div>
                    <div style={{ fontSize: 12, color: "#6E6660", whiteSpace: "pre-wrap" }}>{f.detail}</div>
                    <EvidenceSnippet f={f} fileUrl={fileUrl} />
                  </div>
                )}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

const TIER_BADGE_STYLES: Record<number, { color: string; backgroundColor: string }> = {
  1: { color: "#CC420B", backgroundColor: "#FCEDE4" },
  2: { color: "#6E6660", backgroundColor: "#F0EDE8" },
  3: { color: "#A49C95", backgroundColor: "#FAF8F5" },
};

function TierBadge({ tier }: { tier: number }) {
  const s = TIER_BADGE_STYLES[tier] ?? TIER_BADGE_STYLES[3];
  return (
    <span style={{ fontSize: 11, fontWeight: 600, borderRadius: 6, padding: "1px 7px", whiteSpace: "nowrap", ...s }}>
      Tier {tier}
    </span>
  );
}

/** Round filter pill — same visual as the objects tab's grade pills. */
function FilterPill({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      style={{
        fontSize: 12,
        fontWeight: 600,
        color: active ? "#FFFFFF" : "#6E6660",
        backgroundColor: active ? "#F04E0D" : "#FFFFFF",
        border: `1px solid ${active ? "#F04E0D" : "#E8E2DB"}`,
        borderRadius: 999,
        padding: "4px 11px",
        cursor: "pointer",
        fontFamily: "inherit",
      }}
    >
      {label}
    </button>
  );
}

/** Findings register — the interactive flat lens over the same findings the
 *  tier sections present: filter chips, flat lookup, CSV parity. Collapsed by
 *  default — the tier sections above are the document's reading path. */
function FindingsRegister({ findings, wsPath, fileUrl }: { findings: Finding[]; wsPath: (tab: string, qs?: string) => string; fileUrl: FileUrlFn }) {
  const [tierFilter, setTierFilter] = useState<number | null>(null);
  const counts = useMemo(() => {
    const c: Record<number, number> = { 1: 0, 2: 0, 3: 0 };
    for (const f of findings) c[f.tier] = (c[f.tier] ?? 0) + 1;
    return c;
  }, [findings]);
  const rows = tierFilter === null ? findings : findings.filter((f) => f.tier === tierFilter);

  return (
    <CollapsibleCard title={`Findings register (${findings.length}) — flat view, identical to the CSV export`}>
      <div style={{ display: "flex", justifyContent: "flex-end", flexWrap: "wrap", gap: 6, marginTop: 0, marginBottom: 2 }}>
        <FilterPill label={`All · ${findings.length}`} active={tierFilter === null} onClick={() => setTierFilter(null)} />
        {[1, 2, 3].map((t) => (
          <FilterPill
            key={t}
            label={`Tier ${t} · ${counts[t] ?? 0}`}
            active={tierFilter === t}
            onClick={() => setTierFilter(t)}
          />
        ))}
      </div>
      <p style={{ fontSize: 12, color: "#A49C95", marginBottom: 12 }}>
        Every finding as one row — the same rows, in the same order, as the CSV export. Click a row
        for the full detail, code evidence, and suggested replacement.
      </p>
      <DataTable
        rows={rows}
        rowKey={(f, i) => `${f.tier}:${f.object_name}:${f.evidence_line ?? "x"}:${i}`}
        columns={[
          { header: "Tier", render: (f) => <TierBadge tier={f.tier} />, nowrap: true },
          {
            header: "Object",
            render: (f) => (
              <span style={{ fontFamily: "JetBrains Mono, monospace", fontWeight: 600 }}>
                <ObjectLink name={f.object_name} wsPath={wsPath} />
              </span>
            ),
          },
          { header: "Type", render: (f) => f.object_type, nowrap: true },
          { header: "Finding", render: (f) => <span style={{ color: "#1B1817" }}>{f.title}</span>, width: "34%" },
          {
            header: "SAP Note",
            render: (f) =>
              f.sap_note ? (
                <a href={`https://me.sap.com/notes/${f.sap_note}`} target="_blank" rel="noreferrer" style={{ color: "#CC420B", fontWeight: 600, textDecoration: "none" }}>
                  {f.sap_note}
                </a>
              ) : (
                NO_VALUE
              ),
            nowrap: true,
          },
          {
            header: "Location",
            render: (f) =>
              f.evidence_file ? (
                <FileRef file={f.evidence_file} line={f.evidence_line} url={fileUrl(f.evidence_file, f.evidence_line)} />
              ) : (
                NO_VALUE
              ),
            nowrap: true,
          },
        ]}
        expandContent={(f) => (
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {f.detail && <div style={{ fontSize: 12, color: "#6E6660", whiteSpace: "pre-wrap" }}>{f.detail}</div>}
            <EvidenceSnippet f={f} fileUrl={fileUrl} />
            {f.replacement && (
              <div style={{ fontSize: 12, color: "#1B1817", backgroundColor: "#FCEDE4", borderRadius: 6, padding: "6px 10px", alignSelf: "flex-start" }}>
                <span style={{ fontWeight: 600, color: "#CC420B" }}>Replacement: </span>
                {f.replacement}
              </div>
            )}
            {f.validator && (
              <div style={{ fontSize: 11, color: "#A49C95" }}>
                Validator <span style={{ fontFamily: "JetBrains Mono, monospace" }}>{f.validator}</span>
                {f.validator_passed != null && ` — ${f.validator_passed ? "passed" : "failed"}`}
              </div>
            )}
          </div>
        )}
        emptyText="No findings in this tier."
      />
    </CollapsibleCard>
  );
}

/** Flat list — Tier 3 + the suppressed debug view. */
function FlatFindingList({ findings, showSuppression, fileUrl }: { findings: Finding[]; showSuppression?: boolean; fileUrl: FileUrlFn }) {
  if (findings.length === 0) return <p style={{ fontSize: 13, color: "#6E6660" }}>None.</p>;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {findings.map((f, i) => (
        <div key={i} style={{ borderLeft: `3px solid ${f.tier === 1 ? "#F04E0D" : f.tier === 2 ? "#A49C95" : "#E8E2DB"}`, paddingLeft: 12 }}>
          <div style={{ fontSize: 13, fontWeight: 600, fontFamily: "JetBrains Mono, monospace" }}>{f.object_name}</div>
          <div style={{ fontSize: 13, color: "#1B1817", marginTop: 2 }}>{f.title}</div>
          {showSuppression && f.suppression_reason && (
            <div style={{ fontSize: 12, color: "#CC420B", marginTop: 2 }}>Suppressed: {f.suppression_reason}</div>
          )}
          <div style={{ fontSize: 12, color: "#6E6660", marginTop: 2, whiteSpace: "pre-wrap" }}>{f.detail}</div>
          <EvidenceSnippet f={f} fileUrl={fileUrl} />
        </div>
      ))}
    </div>
  );
}

function RunHistoryRow({ entry, latest, currentRunId }: { entry: HistoryEntry; latest: boolean; currentRunId: string | null }) {
  const when = String(entry.finished_at ?? entry.started_at).slice(0, 16).replace("T", " ");
  const status =
    entry.stage === "done" ? "done" : entry.stage === "failed" ? "failed" : "running";
  const statusColor = status === "done" ? "#6E6660" : status === "failed" ? "#CC420B" : "#F04E0D";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12, fontSize: 13, padding: "8px 10px", border: "1px solid #E8E2DB", borderRadius: 8, backgroundColor: "#FFFFFF" }}>
      <span style={{ fontFamily: "JetBrains Mono, monospace", color: "#6E6660", whiteSpace: "nowrap" }}>{when}</span>
      <span style={{ fontSize: 11, fontWeight: 600, color: statusColor, backgroundColor: status === "failed" ? "#FCEDE4" : "#F0EDE8", borderRadius: 6, padding: "1px 7px" }}>
        {status.toUpperCase()}
      </span>
      {(latest || entry.id === currentRunId) && entry.stage === "done" && (
        <span style={{ fontSize: 11, fontWeight: 600, color: "#CC420B", backgroundColor: "#FCEDE4", borderRadius: 6, padding: "1px 7px" }}>
          LATEST
        </span>
      )}
      <span style={{ flex: 1, minWidth: 0, color: "#6E6660", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
        {entry.stage === "failed"
          ? entry.error ?? "failed"
          : [
              entry.objects_analyzed != null ? `${entry.objects_analyzed} objects analyzed` : null,
              entry.tier1 != null ? `Tier 1: ${entry.tier1}` : null,
              entry.tier2 != null ? `Tier 2: ${entry.tier2}` : null,
              entry.retirement != null ? `retirement: ${entry.retirement}` : null,
            ]
              .filter(Boolean)
              .join(" · ") || "no snapshot recorded (pre-restructure run)"}
      </span>
      <span style={{ fontSize: 11, color: "#A49C95", fontFamily: "JetBrains Mono, monospace" }}>{entry.id.slice(0, 8)}</span>
    </div>
  );
}
