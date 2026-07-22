"use client";

/**
 * S/4HANA rule catalog (CO-07) — the inspectable knowledge base. One block
 * per seeded rule: what changes in S/4HANA, the deterministic detection
 * spec, severity + effort band, and the primary source quoted verbatim from
 * the public Simplification List with a page-anchored link. Read-only.
 *
 * Layout mirrors Settings / the workspace area: 240px second-level rail on
 * the left (search + one entry per rule, scrollspy-highlighted), content
 * pane owning the full remaining width with its own scroll.
 */
import { useEffect, useMemo, useRef, useState } from "react";
import { Search } from "lucide-react";
import Card from "../../../components/ui/Card";

interface CatalogRule {
  id: string;
  title: string;
  description: string;
  severity: string;
  remediation_effort: string | null;
  effort_rationale: string | null;
  replacement: string | null;
  detection: { type: string; tables?: string[]; ops?: string[]; transactions?: string[]; functions?: string[] };
  tier1_eligible: boolean;
  verified_release: string | null;
  sap_note: string | null;
  simplification_item: string | null;
  source_url: string | null;
  source_status: string;
  source_excerpt: string | null;
  excerpt_source_url: string | null;
}

const SIMPL_LIST_URL =
  "https://help.sap.com/doc/c34b5ef72430484cb4d8895d5edd12af/2023/en-US/SIMPL_OP2023.pdf";

const SEVERITY_STYLES: Record<string, { color: string; backgroundColor: string; label: string }> = {
  high: { color: "#CC420B", backgroundColor: "#FCEDE4", label: "high — removed outright" },
  medium: { color: "#6E6660", backgroundColor: "#F0EDE8", label: "medium — compatibility views" },
};

const EFFORT_LABELS: Record<string, string> = {
  low: "low effort",
  medium: "medium effort",
  high: "high effort — redesign",
};

function Chip({ text, color, bg }: { text: string; color: string; bg: string }) {
  return (
    <span style={{ fontSize: 11, fontWeight: 600, color, backgroundColor: bg, borderRadius: 6, padding: "2px 8px", whiteSpace: "nowrap" }}>
      {text}
    </span>
  );
}

/** The detection spec rendered as data — the proof the matching is code, not vibes. */
function DetectionSpec({ d }: { d: CatalogRule["detection"] }) {
  const tokens =
    d.type === "table_access"
      ? `${(d.ops ?? []).map((o) => o.toUpperCase()).join("/")} on ${(d.tables ?? []).join(", ")}`
      : d.type === "call_transaction"
        ? `CALL TRANSACTION ${(d.transactions ?? []).join(", ")}`
        : `CALL FUNCTION ${(d.functions ?? []).join(", ")}`;
  return (
    <div style={{ fontSize: 12, fontFamily: "JetBrains Mono, monospace", color: "#6E6660", backgroundColor: "#FAF8F5", border: "1px solid #E8E2DB", borderRadius: 6, padding: "6px 10px", overflowWrap: "anywhere" }}>
      {d.type} · {tokens}
    </div>
  );
}

/** Everything a rule can be found by — feeds the rail search. */
function ruleHaystack(r: CatalogRule): string {
  const d = r.detection;
  return [
    r.id,
    r.title,
    r.description,
    r.simplification_item,
    r.sap_note,
    r.replacement,
    d.type,
    ...(d.tables ?? []),
    ...(d.ops ?? []),
    ...(d.transactions ?? []),
    ...(d.functions ?? []),
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
}

/** Rail entry — SectionSidebar item style (white card + orange accent when
 *  active), but a button that scrolls the pane instead of a route link. */
function RuleRailItem({ rule, active, onClick }: { rule: CatalogRule; active: boolean; onClick: () => void }) {
  const [hovered, setHovered] = useState(false);
  const sev = SEVERITY_STYLES[rule.severity] ?? SEVERITY_STYLES.medium;
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      title={rule.title}
      data-rail-id={rule.id}
      style={{
        display: "flex",
        alignItems: "flex-start",
        gap: 8,
        padding: "8px 12px 8px 14px",
        fontSize: 13,
        lineHeight: 1.35,
        fontWeight: active ? 600 : 400,
        color: active ? "#1B1817" : "#6E6660",
        background: active || hovered ? "#FFFFFF" : "transparent",
        border: "none",
        borderLeft: active ? "2px solid #F04E0D" : "2px solid transparent",
        borderRadius: "0 6px 6px 0",
        cursor: "pointer",
        textAlign: "left",
        width: "100%",
        boxShadow: active ? "0 1px 2px rgba(0,0,0,0.04)" : "none",
        transition: "background 0.15s, color 0.15s",
      }}
    >
      <span
        aria-hidden
        style={{ width: 7, height: 7, borderRadius: "50%", backgroundColor: sev.color, marginTop: 4, flexShrink: 0 }}
      />
      <span
        style={{
          display: "-webkit-box",
          WebkitLineClamp: 2,
          WebkitBoxOrient: "vertical",
          overflow: "hidden",
        }}
      >
        {rule.title}
      </span>
    </button>
  );
}

export default function RuleCatalogPage() {
  const [rules, setRules] = useState<CatalogRule[] | null>(null);
  const [query, setQuery] = useState("");
  const [activeId, setActiveId] = useState<string | null>(null);
  const paneRef = useRef<HTMLDivElement>(null);
  // While a click/deep-link drives the scroll, the spy stays quiet so the
  // chosen rule keeps its highlight even when it can't reach the pane top.
  const suppressSpy = useRef(false);
  const spyTimer = useRef<number | undefined>(undefined);

  useEffect(() => {
    fetch("/api/rules")
      .then((r) => r.json())
      .then((body) => setRules(body.rules ?? []))
      .catch(() => {});
    // the scrollspy re-arm timer must not fire after unmount
    const timer = spyTimer;
    return () => window.clearTimeout(timer.current);
  }, []);

  // deep links (/rules#<rule-id>) — scroll once the data has rendered
  useEffect(() => {
    if (!rules || !window.location.hash) return;
    const id = decodeURIComponent(window.location.hash.slice(1));
    suppressSpy.current = true;
    document.getElementById(id)?.scrollIntoView({ block: "start" });
    setActiveId(id);
  }, [rules]);

  // keep the active entry visible in the rail as the scrollspy moves it
  useEffect(() => {
    if (!activeId) return;
    document
      .querySelector(`[data-rail-id="${CSS.escape(activeId)}"]`)
      ?.scrollIntoView({ block: "nearest" });
  }, [activeId]);

  const filtered = useMemo(() => {
    if (!rules) return null;
    const q = query.trim().toLowerCase();
    if (!q) return rules;
    return rules.filter((r) => ruleHaystack(r).includes(q));
  }, [rules, query]);

  const scrollToRule = (id: string) => {
    setActiveId(id);
    suppressSpy.current = true;
    history.replaceState(null, "", `#${encodeURIComponent(id)}`);
    // drive the pane directly with an instant jump — smooth scrollIntoView
    // proved unreliable here, and instant matches Settings/system navigation
    const pane = paneRef.current;
    const el = document.getElementById(id);
    if (pane && el) {
      pane.scrollTop = el.getBoundingClientRect().top - pane.getBoundingClientRect().top + pane.scrollTop - 8;
    }
  };

  // Scrollspy: highlight the rule whose card is at (or last crossed) the top
  // of the pane, so the rail tracks reading position.
  const onPaneScroll = () => {
    if (suppressSpy.current) {
      // re-arm once the programmatic scroll has settled
      window.clearTimeout(spyTimer.current);
      spyTimer.current = window.setTimeout(() => {
        suppressSpy.current = false;
      }, 150);
      return;
    }
    const pane = paneRef.current;
    if (!pane || !filtered?.length) return;
    const paneTop = pane.getBoundingClientRect().top;
    let current = filtered[0].id;
    for (const r of filtered) {
      const el = document.getElementById(r.id);
      if (!el) continue;
      if (el.getBoundingClientRect().top - paneTop <= 80) current = r.id;
      else break;
    }
    setActiveId(current);
  };

  return (
    <div style={{ display: "flex", height: "calc(100vh - 56px)", overflow: "hidden", backgroundColor: "#F6F4F1" }}>
      {/* Second-level rail — Settings' SectionSidebar pattern: uppercase
          heading, search, then one scrollspy-tracked entry per rule. */}
      <nav
        className="shrink-0"
        aria-label="Rule catalog"
        style={{
          width: 240,
          borderRight: "1px solid #E8E2DB",
          backgroundColor: "#F6F4F1",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <div style={{ padding: "20px 16px 8px 16px", fontSize: 12, fontWeight: 600, color: "#A49C95", letterSpacing: 1, textTransform: "uppercase" }}>
          S/4HANA rules
        </div>
        <div style={{ padding: "0 12px 10px" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              backgroundColor: "#FFFFFF",
              border: "1px solid #E8E2DB",
              borderRadius: 8,
              padding: "6px 10px",
            }}
          >
            <Search size={14} style={{ color: "#A49C95", flexShrink: 0 }} />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search rules…"
              aria-label="Search rules"
              style={{ fontSize: 13, color: "#1B1817", border: "none", outline: "none", background: "transparent", width: "100%" }}
            />
          </div>
        </div>
        <div className="flex flex-col gap-0.5" style={{ padding: "0 8px 16px 0", overflowY: "auto", flex: 1 }}>
          {filtered?.map((r) => (
            <RuleRailItem key={r.id} rule={r} active={activeId === r.id} onClick={() => scrollToRule(r.id)} />
          ))}
          {filtered && filtered.length === 0 && (
            <p style={{ fontSize: 12, color: "#A49C95", padding: "6px 16px" }}>No rules match.</p>
          )}
        </div>
      </nav>

      <div ref={paneRef} onScroll={onPaneScroll} className="flex-1 overflow-y-auto" style={{ padding: 32 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <Card>
            <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 6 }}>S/4HANA rule catalog</h2>
            <p style={{ fontSize: 13, color: "#6E6660", lineHeight: 1.6, margin: 0 }}>
              Every S/4HANA incompatibility this tool checks for, as inspectable data: each rule cites its
              SAP Note, quotes the official{" "}
              <a href={SIMPL_LIST_URL} target="_blank" rel="noreferrer" style={{ color: "#CC420B", fontWeight: 600, textDecoration: "none" }}>
                Simplification List for SAP S/4HANA 2023 ↗
              </a>{" "}
              verbatim with a page link (public document, no login), and states the deterministic detection
              spec its Tier-1 validator executes. This rule set covers the most frequent custom-code
              simplification items; SAP&apos;s full catalog contains hundreds — rules are seeded reference
              data, and new rules of the supported detection types require no code. It complements, not
              replaces, a full ATC / SAP Readiness Check run.
            </p>
          </Card>

          {!rules && (
            <Card>
              <p style={{ fontSize: 14, color: "#A49C95" }}>Loading…</p>
            </Card>
          )}

          {rules && filtered?.length === 0 && (
            <Card>
              <p style={{ fontSize: 13, color: "#6E6660", margin: 0 }}>
                No rules match “{query}”. Search covers titles, tables, transactions, function
                modules, SAP Notes and simplification items.
              </p>
            </Card>
          )}

          {filtered?.map((r) => {
            const sev = SEVERITY_STYLES[r.severity] ?? SEVERITY_STYLES.medium;
            return (
              <div key={r.id} id={r.id} style={{ scrollMarginTop: 8 }}>
                <Card>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap", marginBottom: 6 }}>
                    <h3 style={{ fontSize: 14, fontWeight: 600, margin: 0 }}>{r.title}</h3>
                    <Chip text={sev.label} color={sev.color} bg={sev.backgroundColor} />
                    {r.remediation_effort && (
                      <Chip text={EFFORT_LABELS[r.remediation_effort] ?? r.remediation_effort} color="#6E6660" bg="#F0EDE8" />
                    )}
                    <span style={{ fontSize: 11, color: "#A49C95", fontFamily: "JetBrains Mono, monospace", marginLeft: "auto" }}>
                      {r.id}
                    </span>
                  </div>

                  {r.simplification_item && (
                    <div style={{ fontSize: 12, color: "#6E6660", marginBottom: 8 }}>
                      Simplification item: <span style={{ fontWeight: 600 }}>{r.simplification_item}</span>
                      {r.verified_release && (
                        <span style={{ color: "#A49C95" }}> · verified against the {r.verified_release} documentation set</span>
                      )}
                    </div>
                  )}

                  <p style={{ fontSize: 13, color: "#1B1817", lineHeight: 1.6, marginBottom: 10 }}>{r.description}</p>

                  {r.source_excerpt && (
                    <blockquote style={{ borderLeft: "3px solid #E8E2DB", margin: "0 0 10px 0", padding: "2px 0 2px 12px" }}>
                      <p style={{ fontSize: 12.5, color: "#6E6660", fontStyle: "italic", lineHeight: 1.6, margin: 0 }}>
                        “{r.source_excerpt}”
                      </p>
                      <div style={{ fontSize: 11, color: "#A49C95", marginTop: 4 }}>
                        — Simplification List for SAP S/4HANA 2023, quoted verbatim
                        {r.excerpt_source_url && (
                          <>
                            {" · "}
                            <a href={r.excerpt_source_url} target="_blank" rel="noreferrer" style={{ color: "#CC420B", fontWeight: 600, textDecoration: "none" }}>
                              p.{r.excerpt_source_url.split("#page=")[1]} ↗
                            </a>
                          </>
                        )}
                      </div>
                    </blockquote>
                  )}

                  <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                    <DetectionSpec d={r.detection} />
                    {r.replacement && (
                      <div style={{ fontSize: 12, color: "#1B1817", backgroundColor: "#FCEDE4", borderRadius: 6, padding: "6px 10px" }}>
                        <span style={{ fontWeight: 600, color: "#CC420B" }}>Replacement: </span>
                        {r.replacement}
                      </div>
                    )}
                    {r.effort_rationale && (
                      <div style={{ fontSize: 12, color: "#6E6660" }}>Effort rationale: {r.effort_rationale}</div>
                    )}
                    <div style={{ fontSize: 12, color: "#6E6660", display: "flex", gap: 14, flexWrap: "wrap", alignItems: "center" }}>
                      {r.sap_note && (
                        <a href={`https://me.sap.com/notes/${r.sap_note}`} target="_blank" rel="noreferrer" style={{ color: "#CC420B", fontWeight: 600, textDecoration: "none" }}>
                          SAP Note {r.sap_note} ↗
                        </a>
                      )}
                      {r.source_url && (
                        <a href={r.source_url} target="_blank" rel="noreferrer" style={{ color: "#6E6660", textDecoration: "none", borderBottom: "1px dotted #A49C95" }}>
                          further reading ↗
                        </a>
                      )}
                    </div>
                  </div>
                </Card>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
