/**
 * PDF renderer for the report export — same data and section order as the
 * MD/CSV renderers (lib/report/render.ts): metadata & run snapshot (one
 * merged table, with the grade distribution drawn as the same stacked bar
 * the UI's GradeBar renders) → executive summary → object inventory &
 * disposition (carries the retirement columns) → Tier 1 by rule → Tier 2 by
 * object → Tier 3. Pure formatting over lib/report/data.ts; no LLM near
 * numbers. Built-in Helvetica/Courier only, so no font assets to bundle.
 */
import PDFDocument from "pdfkit";
import { PRODUCT_NAME } from "../config";
import { GRADE_COLORS, GRADE_MEANINGS, GRADE_ORDER } from "../grade-scale";
import {
  DISPOSITION_LABELS,
  retirementStatement,
  type ReportData,
  type ReportFindingRow,
} from "./data";
import {
  categoryLabel,
  DISPOSITION_RULE_NOTE,
  GRADE_ROLLUP_NOTE,
  metadataSnapshotPairs,
  methodologyParagraphs,
} from "./render";
import { findingStatement } from "./finding-title";
import { NO_VALUE } from "../empty-values";

const INK = "#1B1817";
const MUTED = "#6E6660";
const FAINT = "#A49C95";
const ACCENT = "#CC420B";
const LINE = "#E8E2DB";

const MARGIN = 48;

type Doc = InstanceType<typeof PDFDocument>;

function pageWidth(doc: Doc): number {
  return doc.page.width - MARGIN * 2;
}

/** Manual page-break guard for content drawn outside the flowing-text APIs. */
function ensureRoom(doc: Doc, height: number) {
  if (doc.y + height > doc.page.height - MARGIN) doc.addPage();
}

function h2(doc: Doc, text: string) {
  ensureRoom(doc, 60);
  doc.moveDown(1.2);
  doc.font("Helvetica-Bold").fontSize(13).fillColor(INK).text(text);
  const y = doc.y + 3;
  doc.moveTo(MARGIN, y).lineTo(MARGIN + pageWidth(doc), y).lineWidth(0.7).strokeColor(LINE).stroke();
  doc.y = y + 8;
}

function h3(doc: Doc, text: string, note?: string) {
  ensureRoom(doc, 48);
  doc.moveDown(0.8);
  doc.font("Helvetica-Bold").fontSize(10.5).fillColor(INK).text(text);
  if (note) doc.font("Helvetica").fontSize(8.5).fillColor(FAINT).text(note);
  doc.moveDown(0.3);
}

function para(doc: Doc, text: string, opts: { color?: string; size?: number; indent?: number } = {}) {
  doc
    .font("Helvetica")
    .fontSize(opts.size ?? 9.5)
    .fillColor(opts.color ?? INK)
    .text(text, MARGIN + (opts.indent ?? 0), doc.y, { width: pageWidth(doc) - (opts.indent ?? 0) });
}

function keyValueRows(doc: Doc, pairs: [string, string][]) {
  const labelW = 150;
  for (const [k, v] of pairs) {
    ensureRoom(doc, 16);
    const y = doc.y;
    doc.font("Helvetica").fontSize(9).fillColor(MUTED).text(k, MARGIN, y, { width: labelW });
    doc.font("Helvetica").fontSize(9).fillColor(INK).text(v, MARGIN + labelW + 8, y, { width: pageWidth(doc) - labelW - 8 });
    doc.y = doc.y + 3;
    doc.x = MARGIN;
  }
}

/** Evidence citation + monospace quote, indented; wraps and paginates. */
function evidence(doc: Doc, f: ReportFindingRow) {
  if (!f.evidence) return;
  const one = (file: string | null, line: number | null, text: string) => {
    const loc = `${file ?? "quote not located"}${line ? `:${line}` : ""}`;
    ensureRoom(doc, 30);
    doc.font("Courier").fontSize(7.5).fillColor(FAINT).text(loc, MARGIN + 14, doc.y, { width: pageWidth(doc) - 14 });
    doc.moveDown(0.2);
    doc.font("Courier").fontSize(7.5).fillColor(MUTED).text(text, MARGIN + 14, doc.y, { width: pageWidth(doc) - 14 });
    doc.x = MARGIN;
    doc.moveDown(0.6);
  };
  one(f.evidence_file, f.evidence_line, f.evidence);
  // CO-08: merged root-cause findings list every citation
  for (const e of f.extra_evidence ?? []) {
    if (e.evidence) one(e.file, e.line, e.evidence);
  }
}

function simpleTable(doc: Doc, headers: string[], widths: number[], rows: string[][]) {
  const xs = widths.reduce<number[]>((acc, w, i) => [...acc, (acc[i] ?? MARGIN) + w], [MARGIN]);
  const drawRow = (cells: string[], bold: boolean) => {
    ensureRoom(doc, 18);
    const y = doc.y;
    doc.font(bold ? "Helvetica-Bold" : "Helvetica").fontSize(8.5);
    // row height = tallest cell, so a wrapped cell never collides with the
    // separator line drawn below the row
    const rowH = Math.max(...cells.map((c, i) => doc.heightOfString(c, { width: widths[i] - 8 })));
    cells.forEach((c, i) => {
      doc
        .font(bold ? "Helvetica-Bold" : "Helvetica")
        .fontSize(8.5)
        .fillColor(bold ? MUTED : INK)
        .text(c, xs[i], y, { width: widths[i] - 8 });
    });
    doc.y = y + rowH + 4;
    doc.x = MARGIN;
    doc.moveTo(MARGIN, doc.y - 2).lineTo(MARGIN + widths.reduce((a, b) => a + b, 0), doc.y - 2).lineWidth(0.4).strokeColor(LINE).stroke();
  };
  drawRow(headers, true);
  rows.forEach((r) => drawRow(r, false));
}

/**
 * The grade distribution as the same stacked bar the UI's GradeBar draws:
 * one segment per grade, width proportional to count, same palette
 * (lib/grade-scale.ts), legend beneath with letter + name + count so
 * identity is never color-alone.
 */
function drawGradeBar(doc: Doc, grades: Record<string, number>) {
  const total = GRADE_ORDER.reduce((a, g) => a + (grades[g] ?? 0), 0);
  if (total === 0) return;
  ensureRoom(doc, 46);
  const width = pageWidth(doc);
  const barH = 14;
  const gap = 1.5;
  const present = GRADE_ORDER.filter((g) => (grades[g] ?? 0) > 0);
  const usable = width - gap * (present.length - 1);
  let x = MARGIN;
  const y = doc.y + 2;
  for (const g of present) {
    const w = (usable * (grades[g] ?? 0)) / total;
    doc.rect(x, y, w, barH).fill(GRADE_COLORS[g].bg);
    x += w + gap;
  }
  doc.y = y + barH + 5;
  doc.x = MARGIN;
  const legend = GRADE_ORDER.filter((g) => (grades[g] ?? 0) > 0)
    .map((g) => `${g === "Ungraded" ? "Ungraded" : `${g} · ${GRADE_MEANINGS[g].name}`}: ${grades[g]}`)
    .join("    ");
  doc.font("Helvetica").fontSize(8).fillColor(MUTED).text(legend, MARGIN, doc.y, { width });
  doc.moveDown(0.3);
}

export function renderPdf(data: ReportData): Promise<Buffer> {
  return new Promise((resolve, reject) => {
    const doc = new PDFDocument({
      size: "A4",
      margins: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN },
      bufferPages: true,
      info: { Title: `S/4HANA migration report — ${data.workspace}`, Author: PRODUCT_NAME },
    });
    const chunks: Buffer[] = [];
    doc.on("data", (c: Buffer) => chunks.push(c));
    doc.on("end", () => resolve(Buffer.concat(chunks)));
    doc.on("error", reject);

    const byTier = (t: number) => data.findings.filter((f) => f.tier === t);

    // ---- title ----
    doc.font("Helvetica-Bold").fontSize(19).fillColor(INK).text("S/4HANA migration report");
    doc.font("Courier-Bold").fontSize(12).fillColor(ACCENT).text(data.workspace);
    doc.moveDown(0.4);
    para(
      doc,
      `Generated by ${PRODUCT_NAME}. Evidence tiers, used throughout: Tier 1 — machine-verified (a rule-specific deterministic validator confirmed the incompatibility on the cited line); Tier 2 — evidence-linked (the citation was located verbatim in the stored source; an expert must confirm the interpretation); Tier 3 — unverified observations, excluded from every headline number. All counts are computed by SQL.`,
      { color: MUTED, size: 8.5 }
    );
    if (data.simulated_usage) {
      doc.moveDown(0.3);
      para(doc, "Note: usage statistics in this system are SIMULATED (synthetic usage data, deterministic model).", {
        color: ACCENT,
        size: 8.5,
      });
    }

    // ---- metadata & run snapshot (one merged table) ----
    h2(doc, "Report metadata & run snapshot");
    para(
      doc,
      `What was analyzed and the run's frozen headline numbers — one table, every number computed by SQL when the run finished. ${GRADE_ROLLUP_NOTE}`,
      { color: MUTED, size: 8.5 }
    );
    doc.moveDown(0.5);
    keyValueRows(doc, metadataSnapshotPairs(data));
    if (data.snapshot) {
      doc.moveDown(0.3);
      drawGradeBar(doc, data.snapshot.grades);
    }

    // ---- executive summary ----
    h2(doc, "Executive summary");
    para(doc, data.executive_summary ?? "No report run yet — the executive summary is generated when a run finishes.");
    if (data.recommended_actions) {
      doc.moveDown(0.4);
      doc.font("Helvetica-Bold").fontSize(9.5).fillColor(INK).text(data.recommended_actions, MARGIN, doc.y, { width: pageWidth(doc) });
    }

    // ---- CO-09: object inventory & disposition (incl. retirement columns) ----
    if (data.inventory.length > 0) {
      h2(doc, `Object inventory & disposition${data.simulated_usage ? " — usage is SIMULATED" : ""}`);
      const usageNote = retirementStatement(data);
      para(doc, `One row per object — the action list of this report. ${DISPOSITION_RULE_NOTE}${usageNote ? ` ${usageNote}` : ""}`, {
        color: MUTED,
        size: 8.5,
      });
      doc.moveDown(0.5);
      // section title carries the SIMULATED badge → no per-cell (sim.) suffix
      simpleTable(
        doc,
        ["Object", "Type", "Grade", "T1 · verified", "T2 · linked", "Calls 24m", "Last exec", "Refs", "Disposition"],
        [150, 30, 28, 56, 50, 48, 50, 27, 60],
        data.inventory.map((r) => [
          r.name,
          r.object_type,
          r.grade ?? NO_VALUE,
          String(r.tier1_n),
          String(r.tier2_n),
          r.call_count_24m === null ? NO_VALUE : String(r.call_count_24m),
          r.last_executed ? String(r.last_executed).slice(0, 10) : NO_VALUE,
          String(r.inbound_refs),
          r.disposition ? DISPOSITION_LABELS[r.disposition] ?? r.disposition : "ungraded",
        ])
      );
    }

    // ---- Tier 1 grouped by rule ----
    const t1 = byTier(1);
    if (t1.length > 0) {
      h2(doc, `Tier 1 — machine-verified by deterministic validators (${t1.length})`);
      para(
        doc,
        "Grouped by incompatibility rule. Each block covers one S/4HANA change: what changed, SAP's own source for it, the replacement — then every affected location in this system's code. Every finding below was confirmed by the rule's deterministic validator on the cited line.",
        { color: MUTED, size: 8.5 }
      );
      const groups = new Map<string, ReportFindingRow[]>();
      for (const f of t1) {
        const k = f.rule_id ?? "(no rule)";
        groups.set(k, [...(groups.get(k) ?? []), f]);
      }
      for (const [ruleId, list] of groups) {
        const first = list[0];
        const noteLine = [
          first.sap_note ? `SAP Note ${first.sap_note} (https://me.sap.com/notes/${first.sap_note}), verified` : null,
          first.simplification_item ?? null,
        ]
          .filter(Boolean)
          .join(" · ");
        h3(
          doc,
          `${first.rule_title ?? ruleId} · ${list.length} finding${list.length === 1 ? "" : "s"}`,
          noteLine || undefined
        );
        if (first.rule_description) para(doc, first.rule_description, { size: 9 });
        // CO-07: primary source, quoted verbatim with the page-anchored link
        if (first.source_excerpt) {
          doc.moveDown(0.3);
          para(doc, `"${first.source_excerpt}"`, { size: 8.5, color: MUTED, indent: 14 });
          para(
            doc,
            `— Simplification List for SAP S/4HANA 2023, verbatim${first.excerpt_source_url ? ` · ${first.excerpt_source_url}` : ""}`,
            { size: 7.5, color: FAINT, indent: 14 }
          );
        }
        if (first.replacement) {
          doc.moveDown(0.2);
          para(doc, `Replacement: ${first.replacement}`, { size: 9, color: ACCENT });
        }
        if (first.remediation_effort) {
          doc.moveDown(0.15);
          para(doc, `Remediation effort (seeded band): ${first.remediation_effort}${first.effort_rationale ? ` — ${first.effort_rationale}` : ""}`, {
            size: 8.5,
            color: MUTED,
          });
        }
        if (first.source_url) {
          doc.moveDown(0.15);
          para(doc, `Further reading: ${first.source_url}`, { size: 7.5, color: FAINT });
        }
        doc.moveDown(0.4);
        for (const f of list) {
          ensureRoom(doc, 30);
          // Object · Finding · Category · Process areas · Location — the
          // finding statement disambiguates two hits on the same object
          const chips = [categoryLabel(f.category), ...(f.process_areas ?? [])].join(" · ");
          doc.font("Helvetica-Bold").fontSize(9).fillColor(INK).text(f.object_name, { continued: true });
          doc.font("Helvetica").fontSize(9).fillColor(INK).text(` — ${findingStatement(f)}`, { continued: true });
          doc.font("Helvetica").fontSize(8.5).fillColor(MUTED).text(`  (${chips})`);
          doc.moveDown(0.15);
          evidence(doc, f);
        }
      }
    }

    // ---- Tier 2 grouped by object ----
    const t2 = byTier(2);
    if (t2.length > 0) {
      h2(doc, `Tier 2 — evidence-linked, needs expert review (${t2.length})`);
      para(
        doc,
        "Grouped by object. Each finding cites a real line located verbatim in the stored source; these findings are not tied to a specific verified SAP Note — that is exactly why they need expert confirmation.",
        { color: MUTED, size: 8.5 }
      );
      const groups = new Map<string, ReportFindingRow[]>();
      for (const f of t2) groups.set(f.object_name, [...(groups.get(f.object_name) ?? []), f]);
      for (const [objectName, list] of groups) {
        const first = list[0];
        const chips = [categoryLabel(first.category), ...(first.process_areas ?? [])].join(" · ");
        h3(doc, `${objectName} (${chips})`);
        for (const f of list) {
          ensureRoom(doc, 30);
          doc
            .font("Helvetica-Bold")
            .fontSize(9)
            .fillColor(INK)
            .text(`${f.title}${f.sap_note ? ` — SAP Note ${f.sap_note}` : ""}`);
          doc.moveDown(0.15);
          para(doc, f.detail, { size: 9 });
          doc.moveDown(0.2);
          evidence(doc, f);
        }
      }
    }

    // ---- Tier 3 ----
    const t3 = byTier(3);
    if (t3.length > 0) {
      h2(doc, `Tier 3 — unverified observations from this run (${t3.length})`);
      para(
        doc,
        "Transient by design: these citations could not be located verbatim in the stored source, so they are never counted in headline numbers and are not persisted across runs (Tiers 1–2 are stable and carried forward; Tier 3 is per-run scratch).",
        { color: MUTED, size: 8.5 }
      );
      for (const f of t3) {
        h3(doc, `${f.object_name} — ${f.title}`);
        para(doc, f.detail, { size: 9 });
        doc.moveDown(0.2);
        evidence(doc, f);
      }
    }

    // ---- methodology & data provenance ----
    h2(doc, "Methodology & data provenance");
    for (const p of methodologyParagraphs(data)) {
      ensureRoom(doc, 40);
      doc.font("Helvetica-Bold").fontSize(9).fillColor(INK).text(`${p.heading}. `, { continued: true });
      doc.font("Helvetica").fontSize(9).fillColor(INK).text(p.text);
      doc.moveDown(0.4);
    }

    // ---- footer: page numbers ----
    const range = doc.bufferedPageRange();
    for (let i = range.start; i < range.start + range.count; i++) {
      doc.switchToPage(i);
      doc
        .font("Helvetica")
        .fontSize(7.5)
        .fillColor(FAINT)
        .text(`${PRODUCT_NAME} · ${data.workspace} · page ${i + 1} of ${range.count}`, MARGIN, doc.page.height - 34, {
          width: pageWidth(doc),
          align: "center",
        });
    }

    doc.end();
  });
}
