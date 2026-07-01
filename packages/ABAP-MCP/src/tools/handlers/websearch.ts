/**
 * WEBSEARCH tool handlers: fetch_url, search_sap_web
 * - fetch_url: Extracts readable content from a URL via Tavily Extract API.
 * - search_sap_web: Searches SAP Help, SAP Community and SAP Notes via Tavily Search API.
 * Returns compact results (title + URL + snippet) to minimize token usage.
 */

import { Agent, type Dispatcher } from "undici";

import type { ADTClient } from "abap-adt-api";
import type { ToolResult } from "../../types.js";
import { S_FetchUrl, S_SearchSapWeb } from "../../schemas.js";
import { cfg } from "../../config.js";
import { truncateContent, pickBestResult } from "../../helpers/web.js";

function ok(text: string): ToolResult { return { content: [{ type: "text", text }] }; }
function err(text: string): ToolResult { return { content: [{ type: "text", text }], isError: true }; }

const MISSING_KEY_MESSAGE =
  "Tavily API nicht konfiguriert. " +
  "Bitte TAVILY_API_KEY in der .env setzen.\n" +
  "Setup: https://tavily.com/ → Sign up → API Key kopieren.\n" +
  "Free Tier: 1000 Searches/Monat.";

// TLS verification opt-out scoped to Tavily calls only (corporate proxies with
// self-signed certs). Never touches the ADT connection or other outbound TLS.
const webDispatcher: Dispatcher | undefined = cfg.webAllowUnauthorized
  ? new Agent({ connect: { rejectUnauthorized: false } })
  : undefined;

/** POST to a Tavily endpoint with Bearer auth, timeout and optional lax-TLS dispatcher. */
function tavilyPost(endpoint: "extract" | "search", body: object, timeoutMs: number): Promise<Response> {
  return fetch(`https://api.tavily.com/${endpoint}`, {
    method: "POST",
    signal: AbortSignal.timeout(timeoutMs),
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${cfg.tavilyApiKey}`,
    },
    body: JSON.stringify(body),
    dispatcher: webDispatcher,
  } as RequestInit);
}

/** Map a Tavily HTTP error status to an actionable German hint. */
function tavilyHttpHint(status: number): string {
  if (status === 401 || status === 403) return "TAVILY_API_KEY ungültig oder abgelaufen — Key in der .env prüfen.";
  if (status === 429 || status === 432) return "Tavily-Kontingent erschöpft (Rate-Limit/Monats-Quota) — später erneut versuchen oder Plan upgraden.";
  return "";
}

interface TavilyResult {
  title: string;
  url: string;
  content: string;
  score: number;
}

interface TavilyResponse {
  results: TavilyResult[];
  query: string;
}

const SOURCE_DOMAINS: Record<string, string[]> = {
  help:      ["help.sap.com"],
  community: ["community.sap.com"],
  notes:     ["me.sap.com", "launchpad.support.sap.com"],
};

const SOURCE_LABELS: Record<string, string> = {
  help:      "SAP Help",
  community: "SAP Community",
  notes:     "SAP Notes/KBA",
};

async function tavilySearch(
  query: string,
  includeDomains: string[],
  maxResults: number,
): Promise<TavilyResult[]> {
  const resp = await tavilyPost("search", {
    query,
    max_results: maxResults,
    include_domains: includeDomains,
    search_depth: "basic",
  }, 15_000);

  if (!resp.ok) {
    const body = await resp.text().catch(() => "");
    const hint = tavilyHttpHint(resp.status);
    throw new Error(`Tavily API HTTP ${resp.status}: ${body.slice(0, 200)}${hint ? ` — ${hint}` : ""}`);
  }

  const data = (await resp.json()) as TavilyResponse;
  return data.results ?? [];
}

function formatResults(source: string, items: TavilyResult[]): string {
  if (items.length === 0) return `### ${SOURCE_LABELS[source]}\nKeine Treffer.`;

  const lines = items.map((item, i) =>
    `${i + 1}. **${item.title}**\n   ${item.url}\n   ${item.content.replace(/\n/g, " ").trim().slice(0, 200)}`
  );
  return `### ${SOURCE_LABELS[source]} (${items.length} Treffer)\n\n${lines.join("\n\n")}`;
}

// ── fetch_url handler ─────────────────────────────────────────────────────────

interface TavilyExtractResult {
  url: string;
  raw_content: string;
}

interface TavilyExtractResponse {
  results: TavilyExtractResult[];
  failed_results?: { url: string; error: string }[];
}

const FETCH_URL_MAX_LEN = 15_000;

export async function handleFetchUrl(_client: ADTClient, args: Record<string, unknown>): Promise<ToolResult> {
  if (!cfg.tavilyApiKey) return err(MISSING_KEY_MESSAGE);

  const p = S_FetchUrl.parse(args);
  // Collected per-strategy failure details so the final error names the real
  // cause (e.g. invalid key, quota exhausted) instead of a generic guess.
  const failures: string[] = [];

  // Strategy 1: Tavily Extract API
  try {
    const resp = await tavilyPost("extract", { urls: [p.url] }, 30_000);

    if (resp.ok) {
      const data = (await resp.json()) as TavilyExtractResponse;
      const content = data.results?.[0]?.raw_content;
      if (content && content.trim().length > 0) {
        return ok(`# Inhalt von: ${p.url}\n\n${truncateContent(content, FETCH_URL_MAX_LEN)}`);
      }
      const failed = data.failed_results?.[0];
      failures.push(failed
        ? `Extract: ${failed.error}`
        : "Extract: leere Antwort (kein Inhalt extrahierbar)");
    } else {
      const body = await resp.text().catch(() => "");
      const hint = tavilyHttpHint(resp.status);
      failures.push(`Extract: HTTP ${resp.status} ${body.slice(0, 150)}${hint ? ` — ${hint}` : ""}`);
    }
  } catch (e) {
    failures.push(`Extract: ${e instanceof Error ? e.message : String(e)}`);
  }

  // Strategy 2: Fallback — Tavily Search with URL as query + include_raw_content
  try {
    const domain = new URL(p.url).hostname;
    const resp = await tavilyPost("search", {
      query: p.url,
      max_results: 3,
      include_domains: [domain],
      search_depth: "advanced",
      include_raw_content: true,
    }, 20_000);

    if (resp.ok) {
      const data = (await resp.json()) as { results: Array<{ url: string; title: string; raw_content?: string; content: string }> };
      const best = pickBestResult(p.url, data.results);
      const content = best?.raw_content || best?.content;
      if (best && content && content.trim().length > 0) {
        return ok(`# Inhalt von: ${best.url}\n**${best.title}**\n\n${truncateContent(content, FETCH_URL_MAX_LEN)}`);
      }
      failures.push("Search-Fallback: keine verwertbaren Treffer");
    } else {
      const body = await resp.text().catch(() => "");
      const hint = tavilyHttpHint(resp.status);
      failures.push(`Search-Fallback: HTTP ${resp.status} ${body.slice(0, 150)}${hint ? ` — ${hint}` : ""}`);
    }
  } catch (e) {
    failures.push(`Search-Fallback: ${e instanceof Error ? e.message : String(e)}`);
  }

  return err(
    `URL konnte nicht gelesen werden: ${p.url}\n\n` +
    `Fehlerdetails:\n${failures.map((f) => `- ${f}`).join("\n")}\n\n` +
    `Tipp: Versuche search_sap_web mit relevanten Suchbegriffen statt der direkten URL.`
  );
}

// ── search_sap_web handler ────────────────────────────────────────────────────

export async function handleSearchSapWeb(_client: ADTClient, args: Record<string, unknown>): Promise<ToolResult> {
  if (!cfg.tavilyApiKey) return err(MISSING_KEY_MESSAGE);

  const p = S_SearchSapWeb.parse(args);
  const sources = p.sources ?? ["help", "community", "notes"];
  const maxResults = p.maxResults ?? 5;

  // Enrich query with SAP ABAP context
  const enrichedQuery = `SAP ABAP ${p.query}`;

  // Run all source searches in parallel
  const results = await Promise.allSettled(
    sources.map(async (source) => {
      const domains = SOURCE_DOMAINS[source];
      if (!domains) return { source, items: [] as TavilyResult[] };
      const items = await tavilySearch(enrichedQuery, domains, maxResults);
      return { source, items };
    })
  );

  const sections: string[] = [];
  let totalHits = 0;

  for (const result of results) {
    if (result.status === "fulfilled") {
      const { source, items } = result.value;
      totalHits += items.length;
      sections.push(formatResults(source, items));
    } else {
      sections.push(`### Fehler\n${result.reason}`);
    }
  }

  if (totalHits === 0) {
    return ok(
      `# SAP Web Search: "${p.query}"\n\nKeine Treffer gefunden.\n\n` +
      `**Tipps:**\n- Andere Suchbegriffe verwenden\n- Fehlermeldung kürzen\n- Englische Begriffe probieren`
    );
  }

  return ok(
    `# SAP Web Search: "${p.query}"\n\n${sections.join("\n\n---\n\n")}\n\n` +
    `---\n🔍 ${totalHits} Treffer aus ${sources.map(s => SOURCE_LABELS[s]).join(", ")}`
  );
}
