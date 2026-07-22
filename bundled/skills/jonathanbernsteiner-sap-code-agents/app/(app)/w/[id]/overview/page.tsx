"use client";

/**
 * System Overview (Change Order 04) — the workspace landing tab. Answers
 * "how healthy is this codebase for migration?" at a glance. Every number is
 * SQL-computed by /api/overview; grades come from the object_risk_grades view.
 * The workspace comes from the /w/[id] route — no picker here.
 */
import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Card from "../../../../../components/ui/Card";
import RunSummary from "../../../../../components/RunSummary";
import { NOT_AVAILABLE } from "../../../../../lib/empty-values";
import ReportPipelineCard from "../../../../../components/ReportPipelineCard";
import { useReportRun } from "../../../../../components/useReportRun";

interface Overview {
  workspace: string;
  kind: string;
  simulated_usage: boolean;
  header: {
    objects: number;
    edges: number;
    table_accesses: number;
    parse_ok: number;
    parse_rate: string;
    categories: { category: string | null; n: number }[];
  };
  run: { id: string; finished_at: string } | null;
  grades: Record<string, number>;
  usage: { rows: number; coverage_pct: number };
  findings_by_severity: { tier: number; severity: string; n: number }[];
  retirement_candidates: number | null;
  affected_objects: number;
  /** the report's deterministic disposition sentence — the overview's answer
   *  to "what do we actually do?" (null before the first run) */
  recommended_actions: string | null;
  process_areas: { process_area: string; n: number }[];
}

const CATEGORY_LABELS: Record<string, string> = {
  abap: "ABAP programs & classes",
  enhancement: "Enhancements",
  custom_table: "Custom tables",
  interface: "Interfaces",
};

const num = (v: number) => Number(v).toLocaleString("en-US");

export default function OverviewTab() {
  const params = useParams<{ id: string }>();
  const workspace = decodeURIComponent(params.id);
  const router = useRouter();
  const [data, setData] = useState<Overview | null>(null);
  const [loadError, setLoadError] = useState(false);

  const wsPath = (tab: string, qs = "") => `/w/${encodeURIComponent(workspace)}/${tab}${qs}`;

  // seq-guard: a slow response for a previously selected workspace must not
  // paint over the current one; a network failure shows an error instead of
  // loading forever
  const loadSeq = useRef(0);
  const loadOverview = useCallback(
    (clear = false) => {
      if (!workspace) return;
      const seq = ++loadSeq.current;
      if (clear) {
        setData(null);
        setLoadError(false);
      }
      fetch(`/api/overview?workspace=${encodeURIComponent(workspace)}`)
        .then((r) => r.json())
        .then((d) => {
          if (seq !== loadSeq.current) return;
          if (d.error) setLoadError(true);
          else setData(d);
        })
        .catch(() => {
          if (seq === loadSeq.current) setLoadError(true);
        });
    },
    [workspace]
  );

  useEffect(() => {
    loadOverview(true);
  }, [loadOverview]);

  // a run can be started from here and is watched here — no tab hop
  const refresh = useCallback(() => loadOverview(), [loadOverview]);
  const { status, runActive, showPipeline, startRun, runError } = useReportRun(workspace, refresh);

  const gotoGrade = (grade: string) => router.push(wsPath("objects", `?grade=${encodeURIComponent(grade)}`));
  const tierTotal = (tier: number) =>
    (data?.findings_by_severity ?? []).filter((s) => s.tier === tier).reduce((a, s) => a + s.n, 0);

  return (
    <div style={{ padding: 24, display: "flex", flexDirection: "column", gap: 16 }}>
      {!data && !loadError && <Card><p style={{ fontSize: 14, color: "#A49C95" }}>Loading…</p></Card>}
      {!data && loadError && (
        <Card>
          <p style={{ fontSize: 14, color: "#6E6660" }}>
            The overview could not be loaded. Check your connection and reload the page.
          </p>
        </Card>
      )}

      {data && (
        <>
          {/* 1 — header stats */}
          <Card>
            <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 2 }}>System overview</h2>
            <p style={{ fontSize: 12, color: "#A49C95", marginBottom: 12 }}>
              What was ingested from this system&apos;s custom code and how completely it could be analyzed.
            </p>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 12 }}>
              <Stat label="Objects" value={num(data.header.objects)} hint="Custom code objects ingested: programs, classes, tables, enhancements, interfaces." />
              <Stat label="Call edges" value={num(data.header.edges)} hint="Detected calls between objects — who uses whom." />
              <Stat label="Table accesses" value={num(data.header.table_accesses)} hint="Places where code reads or writes a database table." />
              <Stat label="Parse success" value={data.header.parse_rate} hint="Share of objects the ABAP parser understood fully." />
              {/* Usage coverage sits with parse success: both measure how
                  complete the INPUT is, not what was found. Stated in both
                  states so a missing retirement analysis is never silent. */}
              {data.usage.rows === 0 ? (
                // "n/a", never "None": next to a coverage label "None" reads
                // as a measured zero — nothing runs — instead of "we have no
                // measurements". The why lives on Connections and in the
                // report's methodology, not repeated here.
                <Stat
                  label="Usage coverage"
                  value={NOT_AVAILABLE}
                  hint="No execution statistics — retirement analysis unavailable."
                />
              ) : (
                <Stat
                  label="Usage coverage"
                  value={`${data.usage.coverage_pct}%`}
                  badge={data.simulated_usage ? "SIMULATED" : undefined}
                  hint={`${num(data.usage.rows)} of ${num(data.header.objects)} objects have execution statistics — what identifies dead code you can retire instead of migrating.`}
                />
              )}
            </div>
          </Card>

          {showPipeline && status && (
            <ReportPipelineCard status={status} linkToReport={wsPath("report")} />
          )}
          {runError && (
            <div style={{ fontSize: 13, color: "#CC420B", backgroundColor: "#FCEDE4", border: "1px solid #F6D9CB", borderRadius: 8, padding: "10px 12px" }}>
              {runError}
            </div>
          )}

          {/* 2 — the run's headline: total, the risk split, the evidence
              behind it. Same component the report renders, so the two pages
              cannot describe one run in two shapes. */}
          {data.run ? (
            <Card>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8, gap: 12, flexWrap: "wrap" }}>
                <h3 style={{ fontSize: 14, fontWeight: 600, margin: 0 }}>Migration risk</h3>
                <span style={{ fontSize: 11, color: "#A49C95", fontFamily: "JetBrains Mono, monospace" }}>
                  latest run {String(data.run.finished_at).slice(0, 16).replace("T", " ")}
                </span>
              </div>
              <RunSummary
                totalObjects={data.header.objects}
                grades={data.grades}
                tier1={tierTotal(1)}
                tier2={tierTotal(2)}
                affectedObjects={data.affected_objects}
                retirementCandidates={data.retirement_candidates}
                recommendation={data.recommended_actions}
                onGradeClick={gotoGrade}
              />
              <div style={{ display: "flex", gap: 12, marginTop: 12 }}>
                <a href={wsPath("report")} style={{ fontSize: 13, fontWeight: 600, color: "#CC420B" }}>
                  Open full report →
                </a>
              </div>
            </Card>
          ) : (
            <Card>
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>No migration report yet</h3>
              <p style={{ fontSize: 13, color: "#6E6660", marginBottom: 12 }}>
                Risk grades and the findings summary appear after the first report run analyzes this system.
              </p>
              <button
                onClick={startRun}
                disabled={runActive || data.kind === "example"}
                style={{ fontSize: 13, fontWeight: 600, color: "#FFFFFF", backgroundColor: runActive || data.kind === "example" ? "#A49C95" : "#F04E0D", border: "none", borderRadius: 8, padding: "10px 18px", cursor: runActive || data.kind === "example" ? "default" : "pointer", fontFamily: "inherit" }}
              >
                {runActive ? "Report running…" : "Run migration report"}
              </button>
              {data.kind === "example" && (
                <p style={{ fontSize: 12, color: "#A49C95", marginTop: 8, marginBottom: 0 }}>
                  Example systems are refreshed by the operator.
                </p>
              )}
            </Card>
          )}

          {/* 3 — what the system is made of, side by side: object categories
              (technical shape) and process coverage (business shape). Usage
              coverage moved up into the ingestion stats. */}
          <div style={{ display: "grid", gridTemplateColumns: data.process_areas.length > 0 ? "1fr 1fr" : "1fr", gap: 16 }}>
            <Card>
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 2 }}>Object categories</h3>
              <p style={{ fontSize: 12, color: "#A49C95", marginBottom: 10 }}>
                What kinds of custom objects make up this system.
              </p>
              <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                {data.header.categories.map((c) => (
                  <div key={c.category ?? "none"} style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}>
                    <span style={{ color: "#6E6660" }}>{CATEGORY_LABELS[c.category ?? ""] ?? c.category ?? "Uncategorized"}</span>
                    <span style={{ fontWeight: 600 }}>{num(c.n)}</span>
                  </div>
                ))}
              </div>
              {data.header.categories.some((c) => c.category === "enhancement") && (
                <p style={{ fontSize: 11, color: "#A49C95", marginTop: 10 }}>
                  Enhancements hook into SAP standard code; their anchor points can change or disappear in
                  S/4HANA, so they carry elevated migration risk even without findings.
                </p>
              )}
            </Card>

            {/* Process coverage (CO-05) — objects per business process area,
                derived from table accesses via the seeded table_process_map */}
            {data.process_areas.length > 0 && (
            <Card>
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 2 }}>Process coverage</h3>
              <p style={{ fontSize: 12, color: "#A49C95", marginBottom: 10 }}>
                Objects per business process area, derived from database table accesses. Click to see the objects.
              </p>
              <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                {data.process_areas.map((p) => (
                  <button
                    key={p.process_area}
                    onClick={() => router.push(wsPath("objects", `?area=${encodeURIComponent(p.process_area)}`))}
                    style={{ display: "flex", justifyContent: "space-between", fontSize: 13, background: "none", border: "none", cursor: "pointer", padding: "3px 0", fontFamily: "inherit", textAlign: "left" }}
                  >
                    <span style={{ color: "#CC420B", fontWeight: 600 }}>{p.process_area}</span>
                    <span style={{ color: "#1B1817", fontWeight: 600 }}>{num(p.n)}</span>
                  </button>
                ))}
              </div>
            </Card>
            )}
          </div>

        </>
      )}
    </div>
  );
}

function Stat({ label, value, accent, hint, badge }: { label: string; value: string; accent?: boolean; hint?: string; badge?: string }) {
  return (
    <div>
      <div style={{ fontSize: 20, fontWeight: 600, color: accent ? "#CC420B" : "#1B1817" }}>
        {value}
        {badge && (
          <span style={{ marginLeft: 6, fontSize: 10, fontWeight: 600, color: "#CC420B", backgroundColor: "#FCEDE4", borderRadius: 5, padding: "2px 6px", verticalAlign: "middle" }}>
            {badge}
          </span>
        )}
      </div>
      <div style={{ fontSize: 12, color: "#6E6660" }}>{label}</div>
      {hint && <div style={{ fontSize: 11, color: "#A49C95", marginTop: 3, lineHeight: 1.45 }}>{hint}</div>}
    </div>
  );
}
