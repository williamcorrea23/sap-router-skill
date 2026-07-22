/**
 * Migration report job.
 *
 * Findings are collected in memory, then pushed through the systemic quality
 * pipeline — dedupe → claim-evidence check → suppression — and written in one
 * pass under a report_runs row. Called by the CLI (scripts/report.ts).
 *
 * Tiers: deterministic validator confirmed → Tier 1; parser evidence without
 * validator confirmation, or located verbatim LLM citation → Tier 2;
 * unlocatable or claim-unsupported LLM observation → Tier 3. Headline numbers
 * are never produced here — the report API computes them with SQL.
 */
import Anthropic from "@anthropic-ai/sdk";
import { query } from "../db/client";
import { sourceSegments, locateQuote } from "../parser/segments";
import { RULES, runValidator, validateEvidence, type Rule } from "../validators";
import { checkClaim } from "./claims";
import { dedupeFindings, mergeRootCauses, type DraftFinding } from "./dedupe";
import { computeSnapshot, generateExecutiveSummary } from "./summary";
import { evaluateSuppression, loadSuppressionRules } from "./suppress";

const LLM_MODEL = "claude-sonnet-5";
const LLM_CONCURRENCY = 6;
const LLM_SOURCE_LIMIT = 30_000;

export interface DbObject {
  id: string;
  name: string;
  object_type: string;
  files: string[];
  parse_status: string;
  source: string;
}

export interface RunReportResult {
  runId: string;
  tier1: number;
  tier2: number;
  tier3: number;
  suppressed: number;
  llmScope: number;
  spotcheck: { reconfirmed: number; total: number };
}

/** Up to 3 lines of context around a cited line (A1), 1-based line number. */
function contextWindow(segmentText: string, line: number): string {
  const lines = segmentText.split("\n");
  const slice = lines.slice(Math.max(0, line - 2), Math.min(lines.length, line + 1));
  while (slice.length && slice[0].trim() === "") slice.shift();
  while (slice.length && slice[slice.length - 1].trim() === "") slice.pop();
  return slice.join("\n");
}

async function deterministicPass(wsId: string, objects: DbObject[]): Promise<DraftFinding[]> {
  const drafts: DraftFinding[] = [];
  const tableRules = RULES.filter((r) => r.detection.type === "table_access");
  const scanRules = RULES.filter((r) => r.detection.type !== "table_access");

  // --- table_access rules over parsed accesses ---
  for (const rule of tableRules) {
    const rows = await query<{
      object_id: string;
      op: string;
      table_name: string;
      file: string;
      line: number;
      evidence: string;
    }>(
      `select object_id, op, table_name, file, line, evidence
       from table_accesses
       where workspace_id = $1 and table_name = any($2) and op = any($3)`,
      [wsId, rule.detection.tables ?? [], rule.detection.ops ?? []]
    );
    for (const row of rows) {
      const obj = objects.find((o) => o.id === row.object_id);
      if (!obj) continue;
      const segment = sourceSegments(obj.source, obj.files).find((s) => s.file === row.file);
      const confirmed = segment ? validateEvidence(rule, segment.text, row.line) : false;
      const what = `${row.op.toUpperCase()} on ${row.table_name}`;
      drafts.push({
        objectId: obj.id,
        ruleId: rule.id,
        tier: confirmed ? 1 : 2,
        title: `${what} — ${rule.title}`,
        detail: confirmed
          ? `Machine-verified: deterministic validator '${rule.id}' confirmed this ${what} at the cited line. ${rule.description}`
          : `Parser recorded this ${what}, but the deterministic validator could not confirm the exact cited line — needs expert review. ${rule.description}`,
        file: row.file,
        line: row.line,
        evidence: row.evidence,
        validator: rule.id,
        validatorPassed: confirmed,
        op: row.op,
        token: row.table_name,
        ruleTitle: rule.title,
        ruleDescription: rule.description,
      });
    }
  }

  // --- call_transaction / function_call rules over raw source segments ---
  for (const obj of objects) {
    for (const segment of sourceSegments(obj.source, obj.files)) {
      for (const rule of scanRules) {
        for (const match of runValidator(rule, segment.text)) {
          drafts.push({
            objectId: obj.id,
            ruleId: rule.id,
            tier: 1,
            title: `${match.detail} — ${rule.title}`,
            detail: `Machine-verified: deterministic validator '${rule.id}' matched this statement. ${rule.description}`,
            file: segment.file,
            line: match.line,
            evidence: match.statement.slice(0, 500),
            validator: rule.id,
            validatorPassed: true,
            ruleTitle: rule.title,
            ruleDescription: rule.description,
          });
        }
      }
    }
  }
  return drafts;
}

/**
 * CO-08 — sticky Tier-2 identity. Before a new run replaces the findings,
 * the previous run's displayed Tier-2 LLM findings are re-verified against
 * the CURRENT stored source (verbatim evidence must still locate) and carried
 * into the new run with their exact wording. Merged findings are exploded
 * back into one draft per citation so the dedupe/merge machinery rebuilds
 * the group cleanly. On unchanged source the Tier-2 set therefore converges
 * and is identical run over run; on changed source stale findings drop
 * because their quotes no longer locate. Fabrication-safe: a carried finding
 * is exactly as evidence-backed as a fresh one.
 */
async function loadCarriedTier2(wsId: string, objects: DbObject[]): Promise<DraftFinding[]> {
  const rows = await query<{
    object_id: string;
    title: string;
    detail: string;
    evidence_file: string | null;
    evidence_line: number | null;
    evidence: string | null;
    extra_evidence: { file: string | null; line: number | null; evidence: string | null }[] | null;
  }>(
    `select object_id, title, detail, evidence_file, evidence_line, evidence, extra_evidence
     from findings
     where workspace_id = $1 and tier = 2 and rule_id is null and not suppressed`,
    [wsId]
  );
  const out: DraftFinding[] = [];
  for (const r of rows) {
    const obj = objects.find((o) => o.id === r.object_id);
    if (!obj) continue;
    // strip previous merge annotations so re-merging does not stack them, and
    // the legacy per-finding "Evidence-linked (…)" prefix — that statement now
    // lives once in the Tier 2 section intro, not on every finding
    const baseDetail = r.detail
      .replace(/\n\nSame root cause at \d+ further location[^]*$/, "")
      .replace(/\n\nThis issue appears at \d+ locations in this object[^]*$/, "")
      .replace(/\n\nAlso reported for this line:[^]*$/, "")
      .replace(/^Evidence-linked \(verbatim citation located in source; interpretation needs expert review\): /, "");
    const citations = [
      { file: r.evidence_file, line: r.evidence_line, evidence: r.evidence },
      ...(r.extra_evidence ?? []),
    ];
    for (const c of citations) {
      if (!c.evidence || !c.file) continue;
      const segment = sourceSegments(obj.source, obj.files).find((s) => s.file === c.file);
      if (!segment || !segment.text.includes(c.evidence)) continue; // source changed → drop
      out.push({
        objectId: r.object_id,
        ruleId: null,
        tier: 2,
        title: r.title,
        detail: baseDetail,
        file: c.file,
        line: c.line,
        evidence: c.evidence,
        validator: null,
        validatorPassed: null,
      });
    }
  }
  return out;
}

interface LlmFinding {
  title: string;
  description: string;
  quote: string;
}

function parseLlmJson(text: string): LlmFinding[] {
  const cleaned = text.replace(/```json/gi, "").replace(/```/g, "").trim();
  const start = cleaned.indexOf("[");
  const end = cleaned.lastIndexOf("]");
  if (start === -1 || end === -1) return [];
  try {
    const arr = JSON.parse(cleaned.slice(start, end + 1));
    if (!Array.isArray(arr)) return [];
    return arr
      .filter((f) => f && typeof f.title === "string" && typeof f.quote === "string")
      .slice(0, 5)
      .map((f) => ({
        title: String(f.title).slice(0, 200),
        description: String(f.description ?? "").slice(0, 800),
        quote: String(f.quote).slice(0, 400),
      }));
  } catch {
    return [];
  }
}

async function llmPass(
  wsId: string,
  objects: DbObject[],
  deterministic: DraftFinding[],
  log: (s: string) => void,
  onProgress?: (done: number) => Promise<void>
): Promise<DraftFinding[]> {
  const client = new Anthropic();
  const drafts: DraftFinding[] = [];

  const existingByObject = new Map<string, { line: number | null; file: string | null; title: string }[]>();
  for (const d of deterministic) {
    const list = existingByObject.get(d.objectId) ?? [];
    list.push({ line: d.line, file: d.file, title: d.title });
    existingByObject.set(d.objectId, list);
  }

  const queue = [...objects];
  let done = 0;
  async function worker() {
    for (;;) {
      const obj = queue.shift();
      if (!obj) return;
      const already = existingByObject.get(obj.id) ?? [];
      const alreadyText = already.length
        ? `\n\nAlready flagged by deterministic rules (do NOT repeat these):\n${already.map((a) => `- ${a.title} (${a.file}:${a.line})`).join("\n")}`
        : "";
      const prompt = `You are auditing custom ABAP for SAP S/4HANA migration incompatibilities.

Analyze the object ${obj.name} (${obj.object_type}) below. Report ONLY concrete S/4HANA incompatibilities or migration-relevant defects that are visible in this source — e.g. semantic issues like hard-coded field lengths that changed in S/4HANA (material number extension to 40 chars), reliance on eliminated functionality, assumptions invalidated by the simplified data model. Do not report style issues, performance tips unrelated to S/4HANA, or generalities.

STRICT EVIDENCE RULE: report a finding ONLY if the quoted line ITSELF demonstrates the claimed problem. If the issue spans several lines, quote the single line that shows it most directly. Any table, transaction, function module or length your title mentions as the problem must be visible in the quoted line. A plain declaration that merely uses a table or type is NOT evidence of an incompatibility. Findings whose quote does not visibly contain the claimed pattern are mechanically rejected.

Known non-issues (do not report): WERKS/plant field length (CHAR 4, unchanged in S/4HANA); field-length observations on anything other than the material number.${alreadyText}

Respond with ONLY a JSON array (no prose). Each element:
{"title": "<short issue title>", "description": "<why this breaks or changes behavior in S/4HANA, 1-3 sentences>", "quote": "<ONE line copied VERBATIM from the source that shows the issue — exact characters, no paraphrasing>"}

If there is nothing to report, respond with [].

\`\`\`abap
${obj.source.slice(0, LLM_SOURCE_LIMIT)}
\`\`\``;
      const started = Date.now();
      try {
        // CO-08 note: this model rejects the `temperature` parameter, so
        // run-over-run stability comes from the structural layer instead —
        // root-cause merge + claim check produce a canonical finding set.
        const res = await client.messages.create({
          model: LLM_MODEL,
          max_tokens: 1200,
          messages: [{ role: "user", content: prompt }],
        });
        const text = res.content.filter((b) => b.type === "text").map((b) => (b as { text: string }).text).join("");
        await query(
          `insert into traces (workspace_id, object_id, kind, model, input, output, input_tokens, output_tokens, duration_ms)
           values ($1, $2, 'report', $3, $4, $5, $6, $7, $8)`,
          [wsId, obj.id, LLM_MODEL, JSON.stringify({ prompt_chars: prompt.length }), JSON.stringify({ text: text.slice(0, 6000) }), res.usage.input_tokens, res.usage.output_tokens, Date.now() - started]
        );
        const findings = parseLlmJson(text);
        const segments = sourceSegments(obj.source, obj.files);
        for (const f of findings) {
          const located = locateQuote(segments, f.quote);
          // deterministic rules already cover that line → skip the duplicate
          if (located && already.some((a) => a.file === located.file && a.line !== null && Math.abs(a.line - located.line) <= 1)) {
            continue;
          }
          if (located) {
            const segment = segments.find((s) => s.file === located.file);
            drafts.push({
              objectId: obj.id,
              ruleId: null,
              tier: 2,
              title: f.title,
              // the evidence-tier statement is made once in the Tier 2 section
              // intro; the finding carries only its own claim
              detail: f.description,
              file: located.file,
              line: located.line,
              evidence: segment ? contextWindow(segment.text, located.line) : located.verbatim,
              validator: null,
              validatorPassed: null,
            });
          } else {
            drafts.push({
              objectId: obj.id,
              ruleId: null,
              tier: 3,
              title: f.title,
              detail: `Unverified observation — the model's citation could not be located verbatim in the stored source. ${f.description}`,
              file: null,
              line: null,
              evidence: f.quote,
              validator: null,
              validatorPassed: null,
            });
          }
        }
      } catch (e) {
        log(`  llm pass failed for ${obj.name}: ${(e as Error).message}`);
      }
      done++;
      if (done % 25 === 0) log(`  llm pass: ${done}/${objects.length}`);
      // live pipeline counter (CO-06): every few objects + the final one
      if (onProgress && (done % 5 === 0 || done === objects.length)) {
        await onProgress(done).catch(() => {});
      }
    }
  }
  await Promise.all(Array.from({ length: LLM_CONCURRENCY }, worker));
  return drafts;
}

export async function runReport(
  workspaceName: string,
  opts: { skipLlm?: boolean; log?: (s: string) => void; runId?: string } = {}
): Promise<RunReportResult> {
  const log = opts.log ?? console.log;
  const [ws] = await query<{ id: string }>(`select id from workspaces where name = $1`, [workspaceName]);
  if (!ws) throw new Error(`workspace '${workspaceName}' not found`);

  const objects = await query<DbObject>(
    `select id, name, object_type, files, parse_status, source from objects where workspace_id = $1 order by name`,
    [ws.id]
  );

  // CO-06: the web trigger pre-creates the run row (stage 'queued') so it can
  // return the id immediately; the CLI path still creates it here.
  let run: { id: string };
  if (opts.runId) {
    run = { id: opts.runId };
    await query(
      `update report_runs set llm_pass = $2, objects_analyzed = $3 where id = $1`,
      [run.id, !opts.skipLlm, objects.length]
    );
  } else {
    [run] = await query<{ id: string }>(
      `insert into report_runs (workspace_id, llm_pass, objects_analyzed) values ($1, $2, $3) returning id`,
      [ws.id, !opts.skipLlm, objects.length]
    );
  }

  // Pipeline stage + counters (CO-06): persisted job state, polled by the UI.
  let currentStage = "queued";
  const setStage = (fields: Record<string, unknown>) => {
    if (typeof fields.stage === "string" && fields.stage !== "failed") currentStage = fields.stage;
    const keys = Object.keys(fields);
    const sets = keys.map((k, i) => `${k} = $${i + 2}`).join(", ");
    return query(`update report_runs set ${sets} where id = $1`, [run.id, ...keys.map((k) => fields[k])]);
  };

  try {
    await setStage({ stage: "analyzing" });
    const deterministic = await deterministicPass(ws.id, objects);
    log(`deterministic pass: ${deterministic.length} raw hits from ${RULES.length} rules`);

    // CO-08: sticky Tier-2 identity — re-verified carry-over from the
    // previous run, loaded before the findings table is replaced
    const carried = await loadCarriedTier2(ws.id, objects);
    if (carried.length > 0) log(`carry-over: ${carried.length} re-verified Tier-2 citations from the previous run`);

    let llmDrafts: DraftFinding[] = [];
    let llmScope = 0;
    if (!opts.skipLlm) {
      // LLM scope: every object that touches the database or calls functions/
      // transactions (others cannot carry the incompatibility classes we
      // report); small workspaces are swept completely.
      let scope = objects;
      if (objects.length > 50) {
        const withSignals = await query<{ id: string }>(
          `select distinct o.id from objects o
           where o.workspace_id = $1 and (
             exists (select 1 from table_accesses t where t.object_id = o.id)
             or exists (select 1 from call_edges e where e.caller_id = o.id and e.kind = 'function')
           )`,
          [ws.id]
        );
        const ids = new Set(withSignals.map((r) => r.id));
        scope = objects.filter((o) => ids.has(o.id));
        log(`llm pass scope: ${scope.length}/${objects.length} objects (with DB access or function calls)`);
      }
      llmScope = scope.length;
      await setStage({ analyze_total: scope.length });
      llmDrafts = await llmPass(ws.id, scope, deterministic, log, (done) =>
        setStage({ objects_done: done }).then(() => {})
      );
    } else {
      await setStage({ analyze_total: objects.length, objects_done: objects.length });
    }
    return await finishReport(ws.id, run, objects, deterministic, [...carried, ...llmDrafts], llmScope, setStage, {
      skipLlm: opts.skipLlm,
      log,
    });
  } catch (e) {
    await setStage({
      stage: "failed",
      failed_stage: currentStage,
      error: String((e as Error).message).slice(0, 500),
    }).catch(() => {});
    throw e;
  }
}

async function finishReport(
  wsId: string,
  run: { id: string },
  objects: DbObject[],
  deterministic: DraftFinding[],
  llmDrafts: DraftFinding[],
  llmScope: number,
  setStage: (fields: Record<string, unknown>) => Promise<unknown>,
  finishOpts: { skipLlm?: boolean; log: (s: string) => void }
): Promise<RunReportResult> {
  const ws = { id: wsId };
  await setStage({ stage: "validating" });

  // --- systemic quality pipeline: A3 dedupe → A1 claim check → CO-08
  //     root-cause merge → A2 suppression ---
  const deduped = dedupeFindings([...deterministic, ...llmDrafts]);

  for (const d of deduped) {
    if (d.tier !== 2) continue;
    const check = checkClaim(d.title, d.evidence);
    if (!check.supported) {
      d.tier = 3;
      d.detail = `Downgraded from Tier 2 by the claim-evidence check: claimed token(s) ${check.missing.join(", ")} do not appear in the cited evidence. ${d.detail}`;
    }
  }

  const merged = mergeRootCauses(deduped);

  const suppressionRules = await loadSuppressionRules();
  for (const d of merged) {
    const hit = evaluateSuppression(suppressionRules, { title: d.title, detail: d.detail, ruleId: d.ruleId });
    if (hit) {
      d.suppressed = true;
      d.suppressionReason = `[${hit.ruleId}] ${hit.reason}`;
    }
  }

  // --- single write under this run ---
  await setStage({ stage: "rendering" });
  await query(`delete from findings where workspace_id = $1`, [ws.id]);
  for (let i = 0; i < merged.length; i += 100) {
    const batch = merged.slice(i, i + 100);
    const values: unknown[] = [];
    const rowsSql = batch
      .map((d, j) => {
        const b = j * 15;
        values.push(
          ws.id, d.objectId, d.ruleId, d.tier, d.title, d.detail, d.file, d.line,
          d.evidence, d.validator, d.validatorPassed, d.suppressed ?? false,
          d.suppressionReason ?? null, run.id,
          d.extraEvidence ? JSON.stringify(d.extraEvidence) : null
        );
        return `($${b + 1}, $${b + 2}, $${b + 3}, $${b + 4}, $${b + 5}, $${b + 6}, $${b + 7}, $${b + 8}, $${b + 9}, $${b + 10}, $${b + 11}, $${b + 12}, $${b + 13}, $${b + 14}, $${b + 15})`;
      })
      .join(",");
    await query(
      `insert into findings (workspace_id, object_id, rule_id, tier, title, detail, evidence_file,
                             evidence_line, evidence, validator, validator_passed, suppressed,
                             suppression_reason, run_id, extra_evidence)
       values ${rowsSql}`,
      values
    );
  }
  // Freeze the run: finished_at first (the object_risk_grades view grades
  // from the latest *finished* run), then the SQL snapshot, then the
  // executive summary whose prose is guarded against inventing numbers.
  // Stage flips to 'done' only once snapshot + summary are stored.
  await query(`update report_runs set finished_at = now() where id = $1`, [run.id]);
  const snapshot = await computeSnapshot(ws.id, run.id);
  const objectsAnalyzed = objects.length;
  const executiveSummary = await generateExecutiveSummary({
    wsId: ws.id,
    runId: run.id,
    snapshot,
    objectsAnalyzed,
    skipLlm: finishOpts.skipLlm,
    log: finishOpts.log,
  });
  await query(
    `update report_runs set stage = 'done', snapshot = $2, executive_summary = $3 where id = $1`,
    [run.id, JSON.stringify(snapshot), executiveSummary]
  );

  // --- spot-check: every displayed Tier-1 finding re-validates on its evidence ---
  const tier1 = merged.filter((d) => d.tier === 1 && !d.suppressed);
  let reconfirmed = 0;
  for (const d of tier1) {
    const obj = objects.find((o) => o.id === d.objectId)!;
    const rule = RULES.find((r) => r.id === d.ruleId) as Rule;
    const segment = sourceSegments(obj.source, obj.files).find((s) => s.file === d.file);
    if (segment && d.line !== null && validateEvidence(rule, segment.text, d.line)) reconfirmed++;
  }

  const visible = merged.filter((d) => !d.suppressed);
  return {
    runId: run.id,
    tier1: visible.filter((d) => d.tier === 1).length,
    tier2: visible.filter((d) => d.tier === 2).length,
    tier3: visible.filter((d) => d.tier === 3).length,
    suppressed: merged.length - visible.length,
    llmScope,
    spotcheck: { reconfirmed, total: tier1.length },
  };
}
