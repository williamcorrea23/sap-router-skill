"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { PanelLeftClose, PanelLeftOpen } from "lucide-react";
import Card from "../../../../../components/ui/Card";
import GradeBadge, { GRADE_COLORS, GRADE_MEANINGS, type Grade } from "../../../../../components/ui/GradeBadge";
import Markdown, { stripMarkdown } from "../../../../../components/Markdown";
import MermaidDiagram from "../../../../../components/MermaidDiagram";
import { buildRepoFileUrl } from "../../../../../lib/source-links";

interface ObjectRow {
  name: string;
  object_type: string;
  category: string | null;
  parse_status: string;
  summary_snippet: string;
  call_count_24m: string | null;
  last_executed: string | null;
  simulated: boolean | null;
  inbound_refs: string;
  grade: Grade;
  process_areas: string[] | null;
}

interface Finding {
  tier: number;
  title: string;
  detail: string;
  evidence_file: string | null;
  evidence_line: number | null;
  evidence: string | null;
  validator: string | null;
  validator_passed: boolean | null;
  severity: string | null;
  replacement: string | null;
  sap_note: string | null;
  source_url: string | null;
}

interface Detail {
  object: {
    name: string;
    object_type: string;
    category: string | null;
    files: string[];
    parse_status: string;
    summary: string | null;
    summary_model: string | null;
    source: string;
  };
  /** provenance — file:line citations link into the repo for ingested systems */
  workspace: { kind: string; source: string | null; source_branch: string | null } | null;
  grade: Grade;
  process_areas: string[];
  usage: { call_count_24m: string; last_executed: string | null; simulated: boolean } | null;
  simulated_usage: boolean;
  findings: Finding[];
  mermaid: string | null;
  diagram_internal_only: boolean;
}

// useSearchParams needs a Suspense boundary for prerendering — thin wrapper.
export default function ObjectsTab() {
  return (
    <Suspense fallback={null}>
      <ObjectsTabInner />
    </Suspense>
  );
}

function ObjectsTabInner() {
  const params = useParams<{ id: string }>();
  const searchParams = useSearchParams();
  const workspace = decodeURIComponent(params.id);
  const [rows, setRows] = useState<ObjectRow[]>([]);
  const [filter, setFilter] = useState("");
  const [gradeFilter, setGradeFilter] = useState("");
  const [areaFilter, setAreaFilter] = useState("");
  const [active, setActive] = useState<string | null>(null);
  const [detail, setDetail] = useState<Detail | null>(null);
  const [focusConsumed, setFocusConsumed] = useState(false);
  // list pane: full width while browsing, slim once a detail is open,
  // collapsible to a strip so the detail gets the whole page
  const [listCollapsed, setListCollapsed] = useState(false);

  // reset selection when navigating to a DIFFERENT workspace's objects tab
  // (the page component instance survives the param change)
  const prevWorkspace = useRef<string>("");
  useEffect(() => {
    if (prevWorkspace.current && prevWorkspace.current !== workspace) {
      setActive(null);
      setDetail(null);
      setFilter("");
      setGradeFilter("");
      setAreaFilter("");
      setListCollapsed(false);
    }
    if (workspace) prevWorkspace.current = workspace;
  }, [workspace]);

  // deep links: ?focus=NAME (top-bar search), ?grade=D (overview grade
  // segment), ?area=Purchasing (process chips / overview panel). Keyed on
  // the search params so a query-only navigation (searching again while this
  // tab is already open) applies the new deep link too — reading
  // window.location once on mount missed those.
  useEffect(() => {
    const focus = searchParams.get("focus");
    if (focus) {
      setFilter(focus.toUpperCase());
      setActive(focus.toUpperCase());
    }
    setGradeFilter(searchParams.get("grade") ?? "");
    setAreaFilter(searchParams.get("area") ?? "");
    setFocusConsumed(true);
  }, [searchParams]);

  useEffect(() => {
    if (!workspace || !focusConsumed) return;
    // small debounce so typing in the filter doesn't fire per keystroke;
    // cancelled-guard so a stale response never overwrites a newer one
    let cancelled = false;
    const timer = setTimeout(() => {
      const qs = new URLSearchParams({ workspace, q: filter });
      if (gradeFilter) qs.set("grade", gradeFilter);
      if (areaFilter) qs.set("process_area", areaFilter);
      fetch(`/api/objects?${qs}`)
        .then((r) => r.json())
        .then((d) => {
          if (!cancelled) setRows(d.objects ?? []);
        })
        .catch(() => {});
    }, 150);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [workspace, filter, gradeFilter, areaFilter, focusConsumed]);

  useEffect(() => {
    if (!workspace || !active) return;
    let cancelled = false;
    setDetail(null);
    fetch(`/api/object?workspace=${encodeURIComponent(workspace)}&name=${encodeURIComponent(active)}`)
      .then((r) => r.json())
      .then((d) => {
        if (!cancelled) setDetail(d);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [workspace, active]);

  return (
    <div style={{ padding: 24, display: "flex", gap: 16, height: "100%", boxSizing: "border-box" }}>
      <div
        style={{
          // constant slim width — no jump when selecting an object;
          // collapsed: icon strip only
          width: listCollapsed ? 40 : 320,
          flexShrink: 0,
          display: "flex",
          flexDirection: "column",
          gap: 12,
          transition: "width 220ms ease",
        }}
      >
        {listCollapsed ? (
          <button
            onClick={() => setListCollapsed(false)}
            title="Show object list"
            aria-label="Show object list"
            style={{
              display: "inline-flex", alignItems: "center", justifyContent: "center",
              width: 34, height: 34, backgroundColor: "#FFFFFF", color: "#6E6660",
              border: "1px solid #E8E2DB", borderRadius: 8, cursor: "pointer",
            }}
          >
            <PanelLeftOpen size={16} />
          </button>
        ) : (
          <>
        <div style={{ display: "flex", gap: 8 }}>
        <input
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="Filter by name…"
          style={{
            flex: 1,
            minWidth: 0,
            fontSize: 13,
            padding: "8px 12px",
            borderRadius: 8,
            border: "1px solid #E8E2DB",
            backgroundColor: "#FAF8F5",
            outline: "none",
            fontFamily: "inherit",
          }}
        />
        <button
          onClick={() => setListCollapsed(true)}
          title="Hide object list"
          aria-label="Hide object list"
          style={{
            display: "inline-flex", alignItems: "center", justifyContent: "center",
            width: 34, height: 34, flexShrink: 0, backgroundColor: "#FFFFFF", color: "#6E6660",
            border: "1px solid #E8E2DB", borderRadius: 8, cursor: "pointer",
          }}
        >
          <PanelLeftClose size={16} />
        </button>
        </div>
        {/* grade filter pills — same filter the overview's grade segments deep-link into */}
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          <GradePill label="All" active={gradeFilter === ""} onClick={() => setGradeFilter("")} />
          {(["A", "B", "C", "D", "Ungraded"] as const).map((g) => (
            <GradePill
              key={g}
              label={g}
              color={GRADE_COLORS[g].bg}
              title={GRADE_MEANINGS[g].description}
              active={gradeFilter === g}
              onClick={() => setGradeFilter(g)}
            />
          ))}
        </div>
        {areaFilter && (
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            <FilterChip label={`Process: ${areaFilter}`} onClear={() => setAreaFilter("")} />
          </div>
        )}
        {/* right padding = gutter for the overlay scrollbar, so the thumb
            never draws over the cards' rounded corners */}
        <div style={{ overflowY: "auto", flex: 1, display: "flex", flexDirection: "column", gap: 6, paddingRight: 8 }}>
          {rows.map((o) => (
            <button
              key={`${o.object_type}|${o.name}`}
              onClick={() => setActive(o.name)}
              style={{
                textAlign: "left",
                backgroundColor: active === o.name ? "#FCEDE4" : "#FFFFFF",
                border: `1px solid ${active === o.name ? "#F04E0D" : "#E8E2DB"}`,
                borderRadius: 10,
                padding: "10px 12px",
                cursor: "pointer",
                fontFamily: "inherit",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8 }}>
                <span style={{ display: "inline-flex", alignItems: "center", gap: 6, minWidth: 0 }}>
                  <GradeBadge grade={o.grade} size={16} />
                  <span style={{ fontSize: 13, fontWeight: 600, color: "#1B1817", fontFamily: "JetBrains Mono, monospace", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {o.name}
                  </span>
                </span>
                <span style={{ fontSize: 11, color: "#A49C95", flexShrink: 0 }}>{o.object_type}</span>
              </div>
              <div style={{ fontSize: 12, color: "#6E6660", marginTop: 2, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                {stripMarkdown(o.summary_snippet || "") || (o.parse_status === "failed" ? "parse failed — raw source stored" : "")}
              </div>
              <div style={{ fontSize: 11, color: "#A49C95", marginTop: 4, display: "flex", gap: 10, flexWrap: "wrap" }}>
                <span>{o.inbound_refs} inbound refs</span>
                {o.call_count_24m !== null && (
                  <span>
                    {Number(o.call_count_24m).toLocaleString("en-US")} calls/24m
                    {o.simulated ? " (simulated)" : ""}
                  </span>
                )}
                {o.category && <span>{o.category}</span>}
                {(o.process_areas ?? []).map((a) => (
                  <ProcessChip key={a} area={a} onClick={() => setAreaFilter(a)} />
                ))}
              </div>
            </button>
          ))}
          {rows.length === 0 && <div style={{ fontSize: 13, color: "#A49C95", padding: 12 }}>No objects.</div>}
        </div>
          </>
        )}
      </div>

      <div style={{ flex: 1, overflowY: "auto", paddingRight: 8 }}>
        {!active && (
          <Card>
            <p style={{ fontSize: 14, color: "#6E6660" }}>Select an object to see its documentation, dependencies and findings.</p>
          </Card>
        )}
        {active && !detail && (
          <Card>
            <p style={{ fontSize: 14, color: "#A49C95" }}>Loading {active}…</p>
          </Card>
        )}
        {detail && detail.object && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <Card>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
                <span style={{ display: "inline-flex", alignItems: "center", gap: 8, minWidth: 0 }}>
                  <GradeBadge grade={detail.grade} size={22} />
                  <h2 style={{ fontSize: 17, fontWeight: 600, fontFamily: "JetBrains Mono, monospace" }}>{detail.object.name}</h2>
                  {detail.process_areas.map((a) => (
                    <ProcessChip key={a} area={a} onClick={() => { setAreaFilter(a); }} />
                  ))}
                </span>
                <span style={{ fontSize: 12, color: "#A49C95", flexShrink: 0 }}>
                  {detail.object.object_type}
                  {detail.object.category ? ` · ${detail.object.category}` : ""} · parse {detail.object.parse_status}
                </span>
              </div>
              {detail.object.summary ? (
                <>
                  <div style={{ marginTop: 10 }}>
                    <Markdown>{detail.object.summary}</Markdown>
                  </div>
                  <p style={{ fontSize: 11, color: "#A49C95", marginTop: 8 }}>
                    Auto-generated documentation ({detail.object.summary_model}); grounded in the stored source below.
                  </p>
                </>
              ) : (
                <p style={{ fontSize: 13, color: "#A49C95", marginTop: 10 }}>No summary generated.</p>
              )}
              {detail.usage && (
                <p style={{ fontSize: 13, color: "#6E6660", marginTop: 8 }}>
                  Usage (24 months): <strong>{Number(detail.usage.call_count_24m).toLocaleString("en-US")}</strong> calls
                  {detail.usage.last_executed ? `, last executed ${String(detail.usage.last_executed).slice(0, 10)}` : ", never executed"}
                  {detail.usage.simulated && (
                    <span style={{ marginLeft: 8, fontSize: 11, fontWeight: 600, color: "#CC420B", backgroundColor: "#FCEDE4", borderRadius: 6, padding: "2px 8px" }}>
                      SIMULATED
                    </span>
                  )}
                </p>
              )}
            </Card>

            {detail.findings.length > 0 && (
              <Card>
                <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 2 }}>S/4HANA findings</h3>
                <p style={{ fontSize: 12, color: "#A49C95", marginBottom: 10 }}>
                  Incompatibilities found in this object. Tier 1 = machine-verified on the cited line;
                  Tier 2 = evidence-linked, needs expert review.
                </p>
                <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                  {detail.findings.map((f, i) => (
                    <div key={i} style={{ borderLeft: `3px solid ${f.tier === 1 ? "#F04E0D" : f.tier === 2 ? "#A49C95" : "#E8E2DB"}`, paddingLeft: 12 }}>
                      <div style={{ fontSize: 13, fontWeight: 600 }}>
                        Tier {f.tier} — {f.title}
                        {f.sap_note && <span style={{ fontWeight: 400, color: "#6E6660" }}> · SAP Note {f.sap_note}</span>}
                      </div>
                      <div style={{ fontSize: 13, color: "#6E6660", marginTop: 2 }}>{f.detail}</div>
                      {f.evidence && (
                        <div style={{ marginTop: 6 }}>
                          {f.evidence_file && (
                            <div style={{ marginBottom: 2 }}>
                              <CitationRef
                                file={f.evidence_file}
                                line={f.evidence_line}
                                workspace={detail.workspace}
                              />
                            </div>
                          )}
                          <pre style={{ fontSize: 12, fontFamily: "JetBrains Mono, monospace", backgroundColor: "#FAF8F5", border: "1px solid #E8E2DB", borderRadius: 6, padding: 8, margin: 0, whiteSpace: "pre-wrap" }}>
                            {f.evidence}
                          </pre>
                        </div>
                      )}
                      {/* CO-04: display-only remediation — Tier-1 renders the
                          rule's seeded replacement, Tier-2 is expert-review */}
                      {f.tier === 1 && f.replacement && (
                        <div style={{ fontSize: 12, color: "#1B1817", backgroundColor: "#FCEDE4", borderRadius: 6, padding: "8px 10px", marginTop: 6 }}>
                          <span style={{ fontWeight: 600, color: "#CC420B" }}>Suggested remediation: </span>
                          {f.replacement}
                        </div>
                      )}
                      {f.tier === 2 && (
                        <div style={{ fontSize: 12, color: "#6E6660", marginTop: 6 }}>
                          <span style={{ fontWeight: 600 }}>Requires expert review</span> — evidence-linked
                          finding; interpretation is not machine-verified.
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </Card>
            )}

            {detail.mermaid && (
              <Card>
                <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>Dependencies</h3>
                <p style={{ fontSize: 11, color: "#A49C95", marginBottom: 10 }}>
                  {detail.diagram_internal_only
                    ? "This object has no external dependencies; showing internal structure."
                    : "Computed from extracted call edges — solid nodes are objects in this system, dashed nodes are external / SAP standard; internal routines are not dependencies and are omitted."}
                </p>
                <MermaidDiagram definition={detail.mermaid} />
              </Card>
            )}

            <Card>
              <div style={{ display: "flex", alignItems: "baseline", gap: 10, marginBottom: 10, flexWrap: "wrap" }}>
                <h3 style={{ fontSize: 14, fontWeight: 600, margin: 0 }}>Source</h3>
                {detail.object.files.map((file) => (
                  <CitationRef key={file} file={file} line={null} workspace={detail.workspace} />
                ))}
              </div>
              <pre style={{ fontSize: 12, fontFamily: "JetBrains Mono, monospace", backgroundColor: "#FAF8F5", border: "1px solid #E8E2DB", borderRadius: 8, padding: 12, overflowX: "auto", maxHeight: 480 }}>
                {detail.object.source.slice(0, 40000)}
              </pre>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}

/** file:line citation — quiet link to the file on the repo host (with line
 *  anchor) for repo-ingested systems; plain text for fixture systems. */
function CitationRef({
  file,
  line,
  workspace,
}: {
  file: string;
  line: number | null;
  workspace: Detail["workspace"];
}) {
  const url =
    workspace?.kind === "ingested"
      ? buildRepoFileUrl(workspace.source, workspace.source_branch, file, line)
      : null;
  const label = `${file}${line ? `:${line}` : ""}`;
  if (!url) {
    return <span style={{ fontSize: 11, fontFamily: "JetBrains Mono, monospace", color: "#A49C95" }}>{label}</span>;
  }
  return (
    <a
      href={url}
      target="_blank"
      rel="noreferrer"
      style={{ fontSize: 11, fontFamily: "JetBrains Mono, monospace", color: "#6E6660", textDecoration: "none", borderBottom: "1px dotted #A49C95" }}
    >
      {label}
    </a>
  );
}

/** Round grade-filter pill; the color dot mirrors the grade ramp so pills and
 *  overview segments read as the same scale. */
function GradePill({
  label,
  color,
  title,
  active,
  onClick,
}: {
  label: string;
  color?: string;
  title?: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      title={title}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
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
      {color && (
        <span
          style={{
            width: 9,
            height: 9,
            borderRadius: 999,
            backgroundColor: color,
            border: active ? "1px solid rgba(255,255,255,0.6)" : "1px solid rgba(0,0,0,0.06)",
            flexShrink: 0,
          }}
        />
      )}
      {label}
    </button>
  );
}

function FilterChip({ label, onClear }: { label: string; onClear: () => void }) {
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 12, fontWeight: 600, color: "#CC420B", backgroundColor: "#FCEDE4", borderRadius: 6, padding: "3px 8px" }}>
      {label}
      <button
        onClick={onClear}
        aria-label={`Clear filter ${label}`}
        style={{ background: "none", border: "none", color: "#CC420B", cursor: "pointer", padding: 0, fontSize: 12, lineHeight: 1, fontFamily: "inherit" }}
      >
        ✕
      </button>
    </span>
  );
}

/** Process-area chip (CO-05). A span, not a button — it renders inside the
 *  list-row buttons; clicks filter the list. */
function ProcessChip({ area, onClick }: { area: string; onClick: () => void }) {
  return (
    <span
      role="button"
      tabIndex={0}
      onClick={(e) => {
        e.stopPropagation();
        onClick();
      }}
      onKeyDown={(e) => {
        if (e.key === "Enter") {
          e.stopPropagation();
          onClick();
        }
      }}
      title={`Filter by process area ${area}`}
      style={{ fontSize: 11, fontWeight: 600, color: "#6E6660", backgroundColor: "#F0EDE8", borderRadius: 6, padding: "1px 7px", cursor: "pointer", whiteSpace: "nowrap" }}
    >
      {area}
    </span>
  );
}
