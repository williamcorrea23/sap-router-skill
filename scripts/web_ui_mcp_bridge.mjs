#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import { createRequire } from "node:module";
import os from "node:os";
import path from "node:path";
import readline from "node:readline";
import { fileURLToPath } from "node:url";

import { apiFetch, browserVersion, cdpBaseUrl, fetchCsrfToken, findTab, originOf, websocketAvailable, withSession } from "./cdp_session.mjs";
import { getAction, searchActions } from "./apim_action_catalog.mjs";
import { apiRequest as oauthRequest, channelStatus as oauthStatus, toApiPath } from "./apim_oauth.mjs";
import { loadDotEnv } from "./dotenv_lite.mjs";

// Both channels read their configuration lazily, so loading .env here is enough.
loadDotEnv();

// Scope notice, mirroring the ADT servers' API-policy stance.
// SAP API Policy v.4.2026a §2.2.2 restricts autonomous agents that plan and chain
// business-API calls. This bridge is API lifecycle tooling — proxies, products,
// policies and their tests — not a channel for reading or moving business data.
const SCOPE_NOTICE =
  "API lifecycle tooling only (proxies, products, policies, key value maps and their tests). " +
  "Not for business data access. Mutations require an approval-broker grant. " +
  "See SAP API Policy: https://help.sap.com/doc/sap-api-policy/latest/en-US/API_Policy_latest.pdf";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const require = createRequire(import.meta.url);

const args = process.argv.slice(2);
const productIndex = args.indexOf("--product");
const product = productIndex >= 0 ? args[productIndex + 1] : "cpi";
const envUrl = product === "apim" ? "APIM_WEB_URL" : "CPI_WEB_URL";
const defaultName = product === "apim" ? "SAP API Management Web UI" : "SAP Integration Suite Web UI";
const isApim = product === "apim";

const RESPONSE_LIMIT = 25_000;

function response(id, result) {
  process.stdout.write(JSON.stringify({ jsonrpc: "2.0", id, result }) + "\n");
}

function error(id, code, message) {
  process.stdout.write(JSON.stringify({ jsonrpc: "2.0", id, error: { code, message } }) + "\n");
}

function payload(value, { isError = false } = {}) {
  let text = JSON.stringify(value, null, 2);
  if (text.length > RESPONSE_LIMIT) {
    text = text.slice(0, RESPONSE_LIMIT) + "\n... truncated; narrow the request.";
  }
  const result = { content: [{ type: "text", text }], structuredContent: value };
  if (isError) {
    result.isError = true;
  }
  return result;
}

function baseUrl() {
  return process.env[envUrl] || "";
}

function tenantOrigin() {
  return originOf(baseUrl());
}

function targetUrl(inputPath = "") {
  const base = baseUrl();
  if (!base) {
    return "";
  }
  const suffix = inputPath || "";
  return base.replace(/\/$/, "") + (suffix ? (suffix.startsWith("/") ? suffix : `/${suffix}`) : "");
}

// ---------------------------------------------------------------- widgets

const WIDGET_MIME = "text/html;profile=mcp-app";
const WIDGET_DIR = path.join(ROOT, "widgets", "apim");
const WIDGET_FILES = {
  "ui://apim/proxy-picker.html": { file: "proxy-picker.html", name: "APIM Proxy Picker" },
  "ui://apim/test-console.html": { file: "test-console.html", name: "APIM Test Console" },
  "ui://apim/deploy-confirm.html": { file: "deploy-confirm.html", name: "APIM Deploy Confirmation" },
};

function extAppsBundle() {
  try {
    const source = fs.readFileSync(require.resolve("@modelcontextprotocol/ext-apps/app-with-deps"), "utf8");
    return source.replace(/export\{([^}]+)\};?\s*$/, (_, body) =>
      "globalThis.ExtApps={" +
      body
        .split(",")
        .map((pair) => {
          const [local, exported] = pair.split(" as ").map((s) => s.trim());
          return `${exported ?? local}:${local}`;
        })
        .join(",") +
      "};",
    );
  } catch {
    return null;
  }
}

const widgetCache = new Map();

function widgetsEnabled() {
  return isApim && fs.existsSync(WIDGET_DIR) && extAppsBundle() !== null;
}

function widgetHtml(uri) {
  if (widgetCache.has(uri)) {
    return widgetCache.get(uri);
  }
  const entry = WIDGET_FILES[uri];
  const bundle = extAppsBundle();
  if (!entry || !bundle) {
    return null;
  }
  const file = path.join(WIDGET_DIR, entry.file);
  if (!fs.existsSync(file)) {
    return null;
  }
  const html = fs.readFileSync(file, "utf8").replace("/*__EXT_APPS_BUNDLE__*/", () => bundle);
  widgetCache.set(uri, html);
  return html;
}

function resources() {
  if (!widgetsEnabled()) {
    return [];
  }
  return Object.entries(WIDGET_FILES)
    .filter(([uri]) => widgetHtml(uri) !== null)
    .map(([uri, entry]) => ({ uri, name: entry.name, mimeType: WIDGET_MIME }));
}

function widgetMeta(uri) {
  return widgetsEnabled() && widgetHtml(uri) !== null ? { ui: { resourceUri: uri } } : undefined;
}

function withMeta(toolDefinition, uri) {
  const meta = uri ? widgetMeta(uri) : undefined;
  return meta ? { ...toolDefinition, _meta: meta } : toolDefinition;
}

// ------------------------------------------------------- approval broker

function runApprovalBroker(brokerArgs) {
  const stdout = execFileSync("python", [path.join(ROOT, "scripts", "approval_broker.py"), ...brokerArgs], {
    cwd: ROOT,
    encoding: "utf8",
  });
  return JSON.parse(stdout || "{}");
}

// Key-sorted JSON for the broker. JSON.stringify returns undefined (not a
// string) for undefined and functions, which would splice the bare token
// `undefined` into the payload and break the broker's parse — encode those as
// null instead, the way JSON.stringify does inside arrays.
function stableJson(value) {
  if (value === undefined || typeof value === "function" || typeof value === "symbol") {
    return "null";
  }
  if (value === null || typeof value !== "object") {
    const encoded = JSON.stringify(value);
    return encoded === undefined ? "null" : encoded;
  }
  if (Array.isArray(value)) {
    return `[${value.map(stableJson).join(",")}]`;
  }
  return `{${Object.keys(value)
    .sort()
    .map((key) => `${JSON.stringify(key)}:${stableJson(value[key])}`)
    .join(",")}}`;
}

// ----------------------------------------------------------------- tools

function baseTools() {
  return [
    {
      name: `${product}_webui_status`,
      description: `Report ${defaultName} bridge readiness for logged-in browser/CDP reuse.`,
      inputSchema: { type: "object", properties: {} },
    },
    {
      name: `${product}_webui_open`,
      description: `Open ${defaultName} in the user's logged-in Chrome session through CDP.`,
      inputSchema: {
        type: "object",
        properties: { path: { type: "string", description: "Optional relative path in the tenant UI." } },
      },
    },
    {
      name: `${product}_webui_capture_evidence`,
      description: "Capture title/url/text sample and optional screenshot from the logged-in UI session.",
      inputSchema: {
        type: "object",
        properties: { path: { type: "string" }, screenshot: { type: "boolean", default: false } },
      },
    },
    {
      name: `${product}_webui_plan_action`,
      description: "Create a non-mutating plan for UI work. Commit requires external approval and human-visible session.",
      inputSchema: {
        type: "object",
        properties: { action: { type: "string" }, target: { type: "string" } },
        required: ["action"],
      },
    },
  ];
}

const CHANNEL_PROP = {
  type: "string",
  enum: ["auto", "oauth", "session"],
  default: "auto",
  description:
    "Which API channel to use. 'oauth' is the SAP-documented apiportal-apiaccess service key path and is preferred; 'session' reuses the logged-in browser tab and is an unsanctioned fallback; 'auto' picks oauth when a service key is configured.",
};

function apimSessionTools() {
  return [
    {
      name: "apim_session_status",
      description:
        `Report which API channel is available and working: the SAP-documented OAuth service-key channel, or the logged-in browser session fallback. Run this first. ${SCOPE_NOTICE}`,
      inputSchema: { type: "object", properties: {} },
      annotations: { title: "APIM Channel Status", readOnlyHint: true, idempotentHint: true, openWorldHint: true },
    },
    {
      name: "apim_mcp_gateway_probe",
      description:
        "Check whether this tenant exposes the SAP Integration Suite MCP Gateway — SAP's endorsed way to publish API proxies as governed MCP servers for agents. Reports availability and which proxies look eligible.",
      inputSchema: { type: "object", properties: { channel: CHANNEL_PROP } },
      annotations: { title: "Probe MCP Gateway", readOnlyHint: true, idempotentHint: true, openWorldHint: true },
    },
    withMeta(
      {
        name: "apim_list_proxies",
        description:
          "List API proxies on the tenant. Opens an interactive proxy picker where supported.",
        inputSchema: {
          type: "object",
          properties: {
            top: { type: "integer", description: "Maximum proxies to return.", minimum: 1, maximum: 200, default: 50 },
            filter: { type: "string", description: "Optional OData $filter expression." },
            channel: CHANNEL_PROP,
          },
        },
        annotations: { title: "List APIM Proxies", readOnlyHint: true, idempotentHint: true, openWorldHint: true },
      },
      "ui://apim/proxy-picker.html",
    ),
    {
      name: "apim_api_call",
      description:
        `Read-only GET against the API portal management API. Path must stay under /apiportal/. Use apim_search_actions when unsure which path to call. ${SCOPE_NOTICE}`,
      inputSchema: {
        type: "object",
        properties: {
          path: { type: "string", description: "Tenant-relative path, e.g. /apiportal/api/1.0/Management.svc/APIProxies?$format=json" },
          channel: CHANNEL_PROP,
        },
        required: ["path"],
      },
      annotations: { title: "APIM API Call", readOnlyHint: true, idempotentHint: true, openWorldHint: true },
    },
    withMeta(
      {
        name: "apim_test_proxy",
        description:
          "Read a deployed API proxy's runtime URL and report status, latency and body, to verify the proxy works. " +
          "Restricted to this tenant's hosts and to GET/HEAD/OPTIONS; write verbs and third-party hosts are refused. " +
          "Declare the proxy's virtual host in APIM_RUNTIME_HOSTS.",
        inputSchema: {
          type: "object",
          properties: {
            url: { type: "string", description: "Full runtime URL of the proxy, on a host belonging to this tenant." },
            method: { type: "string", enum: ["GET", "HEAD", "OPTIONS"], default: "GET" },
            headers: { type: "object", description: "Optional request headers.", additionalProperties: { type: "string" } },
          },
          required: ["url"],
        },
        annotations: { title: "Test APIM Proxy", readOnlyHint: true, idempotentHint: true, openWorldHint: true },
      },
      "ui://apim/test-console.html",
    ),
    {
      name: "apim_search_actions",
      description:
        "Search the catalogue of API portal management operations (proxies, products, providers, applications, key value maps) and return their ids, parameters and whether they mutate.",
      inputSchema: {
        type: "object",
        properties: {
          query: { type: "string", description: "Natural language intent, e.g. 'export proxy bundle'." },
          include_mutating: { type: "boolean", default: true },
        },
        required: ["query"],
      },
      annotations: { title: "Search APIM Actions", readOnlyHint: true, idempotentHint: true, openWorldHint: false },
    },
    {
      name: "apim_execute_action",
      description:
        "Execute a catalogued read-only action by id through the logged-in session. Mutating actions are refused here; plan them with apim_configure_plan instead.",
      inputSchema: {
        type: "object",
        properties: {
          action_id: { type: "string", description: "Action id from apim_search_actions." },
          params: { type: "object", description: "Action parameters.", additionalProperties: true },
          channel: CHANNEL_PROP,
        },
        required: ["action_id"],
      },
      annotations: { title: "Execute APIM Action", readOnlyHint: true, openWorldHint: true },
    },
    withMeta(
      {
        name: "apim_configure_plan",
        description:
          "Create an approval plan for a mutating API portal action (import proxy, delete proxy, create product or key value map). Returns the commit command; nothing changes on the tenant yet.",
        inputSchema: {
          type: "object",
          properties: {
            action_id: { type: "string", description: "Mutating action id from apim_search_actions." },
            params: { type: "object", description: "Action parameters.", additionalProperties: true },
            bundle: { type: "string", description: "Path to the proxy ZIP for import actions." },
            payload: { type: "string", description: "JSON body for create actions." },
            channel: CHANNEL_PROP,
          },
          required: ["action_id"],
        },
        annotations: { title: "Plan APIM Change", readOnlyHint: true, openWorldHint: false },
      },
      "ui://apim/deploy-confirm.html",
    ),
    {
      name: "apim_configure_commit",
      description:
        "Consume an approved plan and apply the mutation through the logged-in session, including the portal CSRF token. Requires an approval granted with approval_broker.py.",
      inputSchema: {
        type: "object",
        properties: {
          plan_id: { type: "string", description: "Plan id from apim_configure_plan." },
          action_id: { type: "string", description: "Approval broker action id." },
          plan_hash: { type: "string" },
          argument_hash: { type: "string" },
          precondition_hash: { type: "string" },
          confirm: { type: "boolean", default: false },
        },
        required: ["plan_id", "action_id", "plan_hash", "confirm"],
      },
      annotations: { title: "Commit APIM Change", readOnlyHint: false, destructiveHint: true, openWorldHint: false },
    },
  ];
}

function tools() {
  return isApim ? [...baseTools(), ...apimSessionTools()] : baseTools();
}

// --------------------------------------------------------- playwright path

async function importPlaywright() {
  try {
    return await import("playwright");
  } catch (err) {
    return { error: err?.message || String(err) };
  }
}

async function connectBrowser() {
  const imported = await importPlaywright();
  if (imported.error) {
    return { error: `playwright not available: ${imported.error}` };
  }
  try {
    const browser = await imported.chromium.connectOverCDP(cdpBaseUrl());
    const context = browser.contexts()[0] || (await browser.newContext());
    return { browser, context };
  } catch (err) {
    return { error: `Chrome/CDP not reachable at ${cdpBaseUrl()}: ${err?.message || String(err)}` };
  }
}

// ------------------------------------------------------------- operations

async function status() {
  const base = baseUrl();
  const imported = await importPlaywright();
  const channel = websocketAvailable() ? "cdp-websocket" : imported.error ? "unavailable" : "playwright";
  return {
    product,
    ready: Boolean(base) && channel !== "unavailable",
    url_env: envUrl,
    url_configured: Boolean(base),
    cdp_url: cdpBaseUrl(),
    api_channel: channel,
    playwright: imported.error ? "missing" : "available",
    mutation_mode: "plan_approve_commit",
    cookies_export: "denied",
  };
}

async function sessionStatus() {
  const oauth = oauthStatus();
  const base = baseUrl();
  const preferred = oauth.configured ? "oauth" : "session";
  const head = {
    scope: SCOPE_NOTICE,
    preferred_channel: preferred,
    oauth_channel: { ...oauth, sanctioned: true, note: "SAP-documented path: apiportal-apiaccess service key, client_credentials." },
    session_channel_sanctioned: false,
  };
  if (oauth.configured) {
    const probe = await oauthRequest("/APIProxies?$top=1&$format=json");
    return {
      ...head,
      status: probe.status === "OK" ? "READY" : "DEGRADED",
      channel: "oauth",
      probe_http_status: probe.http_status,
      reason: probe.status === "OK" ? undefined : probe.reason || "service key configured but the management API rejected the call",
    };
  }
  if (!base) {
    return { ...head, status: "BLOCKED", reason: `no service key configured and ${envUrl} missing`, fix: `Set APIM_SERVICE_KEY_FILE for the sanctioned channel, or ${envUrl} to use the logged-in browser session.` };
  }
  if (!websocketAvailable()) {
    return { ...head, status: "DEGRADED", reason: "global WebSocket unavailable; Node 22+ required", node: process.version };
  }
  const origin = tenantOrigin();
  let browser;
  try {
    browser = await browserVersion();
  } catch (err) {
    return {
      ...head,
      status: "DEGRADED",
      reason: `Chrome/CDP not reachable at ${cdpBaseUrl()}: ${err?.message || String(err)}`,
      fix: "Run: npm run apim:connect",
    };
  }
  const tab = await findTab(origin);
  if (!tab) {
    return {
      ...head,
      status: "DEGRADED",
      reason: `no logged-in tab found for ${origin}`,
      browser: browser.Browser,
      fix: "Run: npm run apim:connect, then finish the tenant login in the opened tab.",
    };
  }
  const probe = await withSession(origin, (session) => apiFetch(session, "/apiportal/api/1.0/Management.svc/$metadata"));
  const authenticated = probe?.status === "OK";
  return {
    ...head,
    status: authenticated ? "READY" : "DEGRADED",
    channel: "session",
    origin,
    tab_url: tab.url,
    browser: browser.Browser,
    api_channel: "cdp-websocket",
    authenticated,
    probe_http_status: probe?.http_status,
    reason: authenticated ? undefined : "session probe did not return metadata; the tenant login may have expired",
    cookies_export: "denied",
  };
}

function requireSessionOrigin() {
  const origin = tenantOrigin();
  if (!origin) {
    throw new Error(`${envUrl} missing or not a valid URL`);
  }
  return origin;
}

/**
 * Pick the API channel. OAuth via the apiportal-apiaccess service key is the
 * SAP-documented path and wins whenever it is configured; the logged-in browser
 * session is the unsanctioned fallback for read and test work without a key.
 */
function resolveChannel(preferred) {
  const oauth = oauthStatus();
  if (preferred === "oauth") {
    return oauth.configured ? "oauth" : "unavailable";
  }
  if (preferred === "session") {
    return "session";
  }
  return oauth.configured ? "oauth" : "session";
}

/** Run a management-API request over whichever channel is available. */
async function managementRequest(sessionPath, { method = "GET", body = null, headers = {}, channel } = {}) {
  const selected = resolveChannel(channel);
  if (selected === "unavailable") {
    return { status: "BLOCKED", reason: "oauth channel requested but no service key configured", fix: "Set APIM_SERVICE_KEY_FILE or APIM_CLIENT_ID/APIM_CLIENT_SECRET/APIM_TOKEN_URL/APIM_API_URL." };
  }
  if (selected === "oauth") {
    const result = await oauthRequest(toApiPath(sessionPath), { method, body, headers });
    return { ...result, sanctioned: true };
  }
  const result = await withSession(requireSessionOrigin(), (session) => apiFetch(session, sessionPath, { method, body, headers }));
  return { ...result, channel: "session", sanctioned: false };
}

async function apiCall(input) {
  const requestPath = String(input?.path || "");
  if (!requestPath.startsWith("/apiportal/")) {
    return { status: "BLOCKED", reason: "path must start with /apiportal/", path: requestPath };
  }
  return managementRequest(requestPath, { channel: input?.channel });
}

function parseODataBody(result) {
  if (!result || result.status !== "OK" || typeof result.body !== "string") {
    return null;
  }
  try {
    const parsed = JSON.parse(result.body);
    return parsed?.d?.results ?? parsed?.d ?? parsed?.value ?? parsed;
  } catch {
    return null;
  }
}

async function listProxies(input) {
  const action = getAction("proxies.list");
  const { method, path: requestPath } = action.build({ top: input?.top ?? 50, filter: input?.filter });
  const result = await managementRequest(requestPath, { method, channel: input?.channel });
  const parsed = parseODataBody(result);
  if (!Array.isArray(parsed)) {
    return result;
  }
  const proxies = parsed.map((entry) => ({
    name: entry.name ?? entry.Name ?? null,
    title: entry.title ?? entry.Title ?? null,
    version: entry.version ?? null,
    state: entry.state ?? entry.status ?? null,
    api_base_path: entry.api_base_path ?? entry.apiBasePath ?? null,
  }));
  return { status: "OK", channel: result.channel, count: proxies.length, proxies };
}

// Testing a proxy means executing whatever sits behind it, so this tool is fenced
// twice: it may only reach hosts belonging to this tenant, and only with methods
// that cannot change state. Anything else belongs in the portal's Test Console,
// where a human is driving.
const SAFE_TEST_METHODS = new Set(["GET", "HEAD", "OPTIONS"]);

const PRIVATE_HOST_PATTERNS = [
  /^localhost$/i,
  /^127\./,
  /^0\./,
  /^10\./,
  /^169\.254\./,
  /^172\.(1[6-9]|2\d|3[01])\./,
  /^192\.168\./,
  /^\[?::1\]?$/,
  /^\[?f[cd][0-9a-f]{2}:/i,
];

function tenantHosts() {
  const hosts = new Set();
  const add = (value) => {
    if (!value) {
      return;
    }
    try {
      // Compare hostnames, never host:port — the runtime port differs from the portal's.
      hosts.add(new URL(/^https?:\/\//i.test(value) ? value : `https://${value}`).hostname.toLowerCase());
    } catch {
      // not a usable host reference
    }
  };
  add(baseUrl());
  const oauth = oauthStatus();
  if (oauth.configured) {
    add(oauth.api_base);
  }
  // Runtime traffic leaves through the virtual host, which shares no domain with
  // the portal, so it has to be declared.
  for (const entry of String(process.env.APIM_RUNTIME_HOSTS || "").split(",")) {
    add(entry.trim());
  }
  return hosts;
}

function checkTestTarget(url, method) {
  let parsed;
  try {
    parsed = new URL(url);
  } catch {
    return { status: "BLOCKED", reason: "url must be an absolute http(s) runtime URL" };
  }
  if (!/^https?:$/.test(parsed.protocol)) {
    return { status: "BLOCKED", reason: "url must use http or https", url };
  }
  if (!SAFE_TEST_METHODS.has(method)) {
    return {
      status: "BLOCKED",
      reason: `${method} can change state behind the proxy; this tool only issues ${[...SAFE_TEST_METHODS].join(", ")}`,
      next_step: "Exercise write operations from the portal's Test Console, where a human drives the request.",
    };
  }
  const host = parsed.hostname.toLowerCase();
  if (PRIVATE_HOST_PATTERNS.some((pattern) => pattern.test(host))) {
    return { status: "BLOCKED", reason: `${host} is a loopback, link-local or private address`, url };
  }
  const allowed = tenantHosts();
  if (allowed.size === 0) {
    return {
      status: "BLOCKED",
      reason: "no tenant hosts are known, so no test target can be trusted",
      fix: "Set APIM_RUNTIME_HOSTS to the proxy's virtual host, or configure APIM_WEB_URL / a service key.",
    };
  }
  const permitted = [...allowed].some((entry) => host === entry || host.endsWith(`.${entry}`));
  if (!permitted) {
    return {
      status: "BLOCKED",
      reason: `${host} is not a host of this tenant`,
      allowed_hosts: [...allowed],
      fix: "Add the proxy's virtual host to APIM_RUNTIME_HOSTS if it belongs to this tenant.",
    };
  }
  return null;
}

async function testProxy(input) {
  const url = String(input?.url || "");
  const method = String(input?.method || "GET").toUpperCase();
  const refusal = checkTestTarget(url, method);
  if (refusal) {
    return refusal;
  }
  const headers = input?.headers && typeof input.headers === "object" ? input.headers : {};
  const started = Date.now();
  try {
    // No body: only safe verbs reach this point, and a redirect could otherwise
    // carry the request to a host the allowlist never saw.
    const init = { method, headers, redirect: "manual", signal: AbortSignal.timeout(45_000) };
    const res = await fetch(url, init);
    const text = await res.text();
    const responseHeaders = {};
    res.headers.forEach((value, key) => {
      responseHeaders[key] = value;
    });
    return {
      status: res.ok ? "OK" : "ERROR",
      http_status: res.status,
      url,
      method,
      elapsed_ms: Date.now() - started,
      headers: responseHeaders,
      truncated: text.length > RESPONSE_LIMIT,
      body: text.slice(0, RESPONSE_LIMIT),
    };
  } catch (err) {
    return { status: "ERROR", url, method, elapsed_ms: Date.now() - started, reason: err?.message || String(err) };
  }
}

/**
 * Split an identifier into words so "McpServers" and "MCPGateway" both yield an
 * "mcp" token, while "Components" yields none.
 */
function nameHasWord(name, word) {
  return String(name)
    .split(/(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|[^A-Za-z0-9]+/)
    .some((token) => token.toLowerCase() === word);
}

/**
 * Probe for SAP's MCP Gateway — the endorsed path for exposing API proxies to
 * agents (Integration Suite, rolling out from Q2 2026). The management API is
 * not documented to advertise it, so a negative result settles nothing.
 */
async function mcpGatewayProbe(input) {
  const notes = {
    what: "SAP Integration Suite MCP Gateway publishes Published API proxies as governed MCP servers for agents.",
    why: "SAP API Policy v.4.2026a lists it among the endorsed pathways for agentic API access.",
    docs: "https://community.sap.com/t5/technology-blog-posts-by-sap/mcp-gateway-in-sap-integration-suite-your-apis-ready-for-the-age-of-agents/ba-p/14438250",
  };
  const proxies = await listProxies({ top: 200, channel: input?.channel });
  if (proxies.status !== "OK") {
    return { status: "UNKNOWN", reason: "could not list proxies to assess eligibility", detail: proxies, ...notes };
  }
  const published = proxies.proxies.filter((proxy) => String(proxy.state || "").toUpperCase().includes("PUBLISH"));
  const metadata = await managementRequest("/apiportal/api/1.0/Management.svc/$metadata", { channel: input?.channel });
  const metadataBody = typeof metadata.body === "string" ? metadata.body : "";
  // Only an entity or entity-set name counts. Matching "mcp" anywhere in the
  // metadata would fire on any namespace or attribute that happens to contain it.
  const entityNames = [...metadataBody.matchAll(/<(?:EntityType|EntitySet)\b[^>]*\bName="([^"]+)"/gi)].map((match) => match[1]);
  const gatewayEntities = entityNames.filter((name) => nameHasWord(name, "mcp"));
  return {
    // The management API is not documented to advertise the Gateway, so absence
    // of evidence is not evidence of absence — say UNKNOWN, not NOT_AVAILABLE.
    status: gatewayEntities.length > 0 ? "ENTITIES_FOUND" : "UNKNOWN",
    channel: proxies.channel,
    gateway_entities: gatewayEntities,
    metadata_read: metadata.status === "OK",
    proxy_count: proxies.count,
    published_proxy_count: published.length,
    eligible_proxies: published.slice(0, 25).map((proxy) => proxy.name),
    next_step:
      gatewayEntities.length > 0
        ? "The management API advertises MCP-named entities. Confirm in the API portal, then enable the Gateway on a Published proxy."
        : "The management API does not advertise MCP entities, which does not settle it either way — the Gateway is surfaced in the portal UI. Check Integration Suite's release status for your region.",
    ...notes,
  };
}

async function executeAction(input) {
  const action = getAction(String(input?.action_id || ""));
  if (!action) {
    return { status: "ERROR", reason: `unknown action: ${input?.action_id}`, next_step: "Call apim_search_actions first." };
  }
  if (action.mutating) {
    return {
      status: "BLOCKED",
      reason: `${action.id} mutates the tenant`,
      next_step: "Use apim_configure_plan, approve it with approval_broker.py, then apim_configure_commit.",
    };
  }
  const built = action.build(input?.params || {});
  return managementRequest(built.path, { method: built.method, channel: input?.channel });
}

const PLAN_DIR = path.join(ROOT, "scratch", "apim-plans");

/**
 * Confine upload bundles to a workspace, mirroring safe_workspace_path() in
 * cpi_client.py. Without this an agent could plan an upload of any file on disk
 * and rely on the human approval as the only thing standing between a private
 * key and the tenant.
 */
function safeWorkspacePath(value) {
  const root = path.resolve(process.env.APIM_TOOL_WORKSPACE || ROOT);
  const candidate = path.resolve(path.isAbsolute(value) ? value : path.join(root, value));
  const relative = path.relative(root, candidate);
  if (relative.startsWith("..") || path.isAbsolute(relative)) {
    throw new Error(`bundle path is outside ${process.env.APIM_TOOL_WORKSPACE ? "APIM_TOOL_WORKSPACE" : "the repository"}: ${value}`);
  }
  return candidate;
}

function planPreconditions(action, bundle, channel) {
  return {
    action_id: action.id,
    channel,
    sanctioned_channel: channel === "oauth",
    session_origin: channel === "session" ? tenantOrigin() : "",
    bundle_exists: bundle ? fs.existsSync(bundle) : true,
    mutating: action.mutating,
  };
}

async function configurePlan(input) {
  const action = getAction(String(input?.action_id || ""));
  if (!action) {
    return { status: "ERROR", reason: `unknown action: ${input?.action_id}` };
  }
  if (!action.mutating) {
    return { status: "BLOCKED", reason: `${action.id} is read-only`, next_step: "Call apim_execute_action instead." };
  }
  const params = input?.params || {};
  let bundle = null;
  if (input?.bundle) {
    try {
      bundle = safeWorkspacePath(String(input.bundle));
    } catch (err) {
      return { status: "BLOCKED", reason: err.message };
    }
    if (!fs.existsSync(bundle)) {
      return { status: "ERROR", reason: `bundle not found: ${bundle}` };
    }
  }
  const built = action.build(params);
  const channel = resolveChannel(input?.channel);
  if (channel === "unavailable") {
    return { status: "BLOCKED", reason: "oauth channel requested but no service key configured" };
  }
  const target = String(params.name || params.target || action.entity);
  const argumentsPayload = {
    action_id: action.id,
    channel,
    method: built.method,
    path: built.path,
    content_type: built.contentType || "application/json",
    bundle: bundle || "",
    payload: input?.payload ? String(input.payload) : "",
    target,
  };
  const preconditions = planPreconditions(action, bundle, channel);
  fs.mkdirSync(PLAN_DIR, { recursive: true });
  const planId = `apim-${channel}-${crypto.randomUUID()}`;
  fs.writeFileSync(
    path.join(PLAN_DIR, `${planId}.json`),
    JSON.stringify({ plan_id: planId, action: `apim.${channel}.${action.id}`, mutation: true, arguments: argumentsPayload, preconditions }, null, 2) + "\n",
    "utf8",
  );
  const broker = runApprovalBroker([
    "plan",
    "--capability",
    action.capability || "sap.apim.proxy.modify",
    "--target",
    target,
    "--summary",
    `APIM ${channel} ${action.id} ${built.method} ${built.path}`,
    "--effect",
    "mutating",
    "--arguments-json",
    stableJson(argumentsPayload),
    "--preconditions-json",
    stableJson(preconditions),
  ]);
  broker.apim_plan_id = planId;
  broker.arguments = argumentsPayload;
  broker.preconditions = preconditions;
  broker.approve_command = `python scripts/approval_broker.py approve ${broker.action_id}`;
  broker.commit_tool = {
    name: "apim_configure_commit",
    arguments: {
      plan_id: planId,
      action_id: broker.action_id,
      plan_hash: broker.plan_hash,
      argument_hash: broker.argument_hash,
      precondition_hash: broker.precondition_hash,
      confirm: true,
    },
  };
  return broker;
}

async function configureCommit(input) {
  if (!input?.confirm) {
    return { status: "BLOCKED", reason: "Missing confirm. Review and approve the plan first." };
  }
  const planPath = path.join(PLAN_DIR, `${input.plan_id}.json`);
  if (!fs.existsSync(planPath)) {
    return { status: "ERROR", reason: `plan not found: ${input.plan_id}` };
  }
  const plan = JSON.parse(fs.readFileSync(planPath, "utf8"));
  const args = plan.arguments;
  if (args.bundle && !fs.existsSync(args.bundle)) {
    return { status: "BLOCKED", reason: "preconditions-not-met", detail: `bundle missing: ${args.bundle}` };
  }
  const hashArgs = [String(input.action_id), "--plan-hash", String(input.plan_hash)];
  if (input.argument_hash) {
    hashArgs.push("--argument-hash", String(input.argument_hash));
  }
  if (input.precondition_hash) {
    hashArgs.push("--precondition-hash", String(input.precondition_hash));
  }

  // Verify now, mutate, then spend. Spending first would burn a one-time
  // approval on a transient failure the tenant never saw.
  runApprovalBroker(["verify", ...hashArgs]);

  // Never let a throw escape between verify and the approval report — the caller
  // has to learn whether the approval is still spendable.
  let outcome;
  try {
    outcome = await performMutation(args);
  } catch (err) {
    outcome = { status: "ERROR", reason: err?.message || String(err) };
  }

  if (outcome.status !== "OK") {
    return {
      ...outcome,
      plan_id: input.plan_id,
      target: args.target,
      action_id: args.action_id,
      approval: "still-open",
      next_step: `The mutation failed, so approval ${input.action_id} was not spent. Retry the commit, or reject it with: python scripts/approval_broker.py reject ${input.action_id}`,
    };
  }

  try {
    runApprovalBroker(["consume", ...hashArgs]);
  } catch (err) {
    return {
      ...outcome,
      plan_id: input.plan_id,
      target: args.target,
      action_id: args.action_id,
      approval: "applied-but-not-spent",
      warning: `The change was applied but approval ${input.action_id} could not be marked consumed: ${err?.message || String(err)}. Reject it so it cannot be replayed.`,
    };
  }
  return { ...outcome, plan_id: input.plan_id, target: args.target, action_id: args.action_id, approval: "spent" };
}

async function performMutation(args) {
  if ((args.channel || "session") === "oauth") {
    const body = args.bundle ? fs.readFileSync(args.bundle) : args.payload || null;
    const result = await oauthRequest(toApiPath(args.path), {
      method: args.method,
      body,
      binary: Boolean(args.bundle),
      headers: { "Content-Type": args.content_type },
    });
    return { ...result, sanctioned: true };
  }

  const origin = requireSessionOrigin();
  return withSession(origin, async (session) => {
    const csrf = await fetchCsrfToken(session);
    if (csrf.status !== "OK") {
      return { status: "ERROR", stage: "csrf", csrf };
    }
    const headers = { "X-CSRF-Token": csrf.token, "Content-Type": args.content_type };
    let body = null;
    if (args.bundle) {
      // Bundles are binary; hand the page a base64 string it turns back into bytes.
      const base64 = fs.readFileSync(args.bundle).toString("base64");
      const upload = await session.evaluate(`(async () => {
        const bytes = Uint8Array.from(atob(${JSON.stringify(base64)}), (c) => c.charCodeAt(0));
        const res = await fetch(${JSON.stringify(args.path)}, {
          method: ${JSON.stringify(args.method)},
          credentials: "same-origin",
          headers: ${JSON.stringify(headers)},
          body: bytes,
        });
        const text = await res.text();
        return { status: res.ok ? "OK" : "ERROR", http_status: res.status, body: text.slice(0, ${RESPONSE_LIMIT}) };
      })()`);
      return { ...upload, sanctioned: false };
    }
    body = args.payload || null;
    const result = await apiFetch(session, args.path, { method: args.method, body, headers });
    return { ...result, sanctioned: false };
  });
}

async function openUi(input) {
  const url = targetUrl(input?.path || "");
  if (!url) {
    return { status: "BLOCKED", reason: `${envUrl} missing` };
  }
  const attached = await connectBrowser();
  if (attached.error) {
    return { status: "DEGRADED", reason: attached.error, url };
  }
  const page = await attached.context.newPage();
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 45000 });
  const title = await page.title();
  return { status: "OK", url: page.url(), title, auth: "logged-in-user-browser-session" };
}

async function captureEvidence(input) {
  const opened = await openUi(input);
  if (opened.status !== "OK") {
    return opened;
  }
  const attached = await connectBrowser();
  if (attached.error) {
    return opened;
  }
  const pages = attached.context.pages();
  const page = pages[pages.length - 1];
  const text = (await page.locator("body").innerText({ timeout: 10000 }).catch(() => "")).slice(0, 2000);
  const evidence = { ...opened, text_sample: text };
  if (input?.screenshot) {
    const dir = path.join(os.tmpdir(), "sap-router-webui-evidence");
    fs.mkdirSync(dir, { recursive: true });
    const file = path.join(dir, `${product}-${Date.now()}.png`);
    await page.screenshot({ path: file, fullPage: true });
    evidence.screenshot = file;
  }
  return evidence;
}

async function callTool(name, input) {
  if (name.endsWith("_webui_status")) {
    return payload(await status());
  }
  if (name.endsWith("_webui_open")) {
    return payload(await openUi(input));
  }
  if (name.endsWith("_webui_capture_evidence")) {
    return payload(await captureEvidence(input));
  }
  if (name.endsWith("_webui_plan_action")) {
    return payload({ status: "PLAN_CREATED", product, action: input?.action, target: input?.target || "", mutation_requires_external_approval: true });
  }
  if (!isApim) {
    throw new Error(`Unknown tool: ${name}`);
  }
  switch (name) {
    case "apim_session_status":
      return payload(await sessionStatus());
    case "apim_mcp_gateway_probe":
      return payload(await mcpGatewayProbe(input));
    case "apim_api_call":
      return payload(await apiCall(input));
    case "apim_list_proxies":
      return payload(await listProxies(input));
    case "apim_test_proxy":
      return payload(await testProxy(input));
    case "apim_search_actions":
      return payload({ actions: searchActions(input?.query, { includeMutating: input?.include_mutating !== false }) });
    case "apim_execute_action":
      return payload(await executeAction(input));
    case "apim_configure_plan":
      return payload(await configurePlan(input));
    case "apim_configure_commit":
      return payload(await configureCommit(input));
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}

const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
let inFlight = 0;
let stdinClosed = false;

function settle() {
  if (stdinClosed && inFlight === 0) {
    process.exit(0);
  }
}

rl.on("line", (line) => {
  inFlight += 1;
  handleLine(line).finally(() => {
    inFlight -= 1;
    settle();
  });
});

async function handleLine(line) {
  let msg;
  try {
    msg = JSON.parse(line);
  } catch {
    return;
  }
  const id = msg.id ?? null;
  try {
    if (msg.method === "initialize") {
      const capabilities = { tools: {} };
      if (widgetsEnabled()) {
        capabilities.resources = {};
      }
      const initResult = { protocolVersion: "2024-11-05", capabilities, serverInfo: { name: `${product}-web-ui-mcp`, version: "0.3.0" } };
      if (isApim) {
        initResult.instructions = SCOPE_NOTICE;
      }
      response(id, initResult);
    } else if (msg.method === "tools/list") {
      response(id, { tools: tools() });
    } else if (msg.method === "resources/list") {
      response(id, { resources: resources() });
    } else if (msg.method === "resources/read") {
      const uri = msg.params?.uri;
      const html = widgetHtml(uri);
      if (!html) {
        error(id, -32602, `Unknown resource: ${uri}`);
      } else {
        response(id, { contents: [{ uri, mimeType: WIDGET_MIME, text: html }] });
      }
    } else if (msg.method === "tools/call") {
      response(id, await callTool(msg.params?.name, msg.params?.arguments || {}));
    } else if (msg.method === "notifications/initialized") {
      return;
    } else {
      error(id, -32601, `Unsupported method: ${msg.method}`);
    }
  } catch (err) {
    error(id, -32000, err?.message || String(err));
  }
}

// The smoke driver and stdio MCP hosts close stdin after a request batch.
// Exit once the in-flight requests have answered, so no reply is cut off.
rl.on("close", () => {
  stdinClosed = true;
  settle();
});
