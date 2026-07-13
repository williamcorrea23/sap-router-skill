#!/usr/bin/env node
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import readline from "node:readline";

const args = process.argv.slice(2);
const productIndex = args.indexOf("--product");
const product = productIndex >= 0 ? args[productIndex + 1] : "cpi";
const envUrl = product === "apim" ? "APIM_WEB_URL" : "CPI_WEB_URL";
const defaultName = product === "apim" ? "SAP API Management Web UI" : "SAP Integration Suite Web UI";

function cdpUrl() {
  return process.env.BROWSER_CDP_URL || `http://127.0.0.1:${process.env.CHROME_DEBUGGING_PORT || "9222"}`;
}

function response(id, result) {
  process.stdout.write(JSON.stringify({ jsonrpc: "2.0", id, result }) + "\n");
}

function error(id, code, message) {
  process.stdout.write(JSON.stringify({ jsonrpc: "2.0", id, error: { code, message } }) + "\n");
}

function tools() {
  return [
    {
      name: `${product}_webui_status`,
      description: `Report ${defaultName} bridge readiness for logged-in browser/CDP reuse.`,
      inputSchema: { type: "object", properties: {} }
    },
    {
      name: `${product}_webui_open`,
      description: `Open ${defaultName} in the user's logged-in Chrome session through CDP.`,
      inputSchema: {
        type: "object",
        properties: {
          path: { type: "string", description: "Optional relative path in the tenant UI." }
        }
      }
    },
    {
      name: `${product}_webui_capture_evidence`,
      description: "Capture title/url/text sample and optional screenshot from the logged-in UI session.",
      inputSchema: {
        type: "object",
        properties: {
          path: { type: "string" },
          screenshot: { type: "boolean", default: false }
        }
      }
    },
    {
      name: `${product}_webui_plan_action`,
      description: "Create a non-mutating plan for UI work. Commit requires external approval and human-visible session.",
      inputSchema: {
        type: "object",
        properties: {
          action: { type: "string" },
          target: { type: "string" }
        },
        required: ["action"]
      }
    }
  ];
}

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
    const browser = await imported.chromium.connectOverCDP(cdpUrl());
    const context = browser.contexts()[0] || await browser.newContext();
    return { browser, context };
  } catch (err) {
    return { error: `Chrome/CDP not reachable at ${cdpUrl()}: ${err?.message || String(err)}` };
  }
}

function targetUrl(inputPath = "") {
  const baseUrl = process.env[envUrl] || "";
  if (!baseUrl) {
    return "";
  }
  const suffix = inputPath || "";
  return baseUrl.replace(/\/$/, "") + (suffix ? (suffix.startsWith("/") ? suffix : `/${suffix}`) : "");
}

async function status() {
  const baseUrl = process.env[envUrl] || "";
  const imported = await importPlaywright();
  return {
    product,
    ready: Boolean(baseUrl) && !imported.error,
    url_env: envUrl,
    url_configured: Boolean(baseUrl),
    cdp_url: cdpUrl(),
    playwright: imported.error ? "missing" : "available",
    mutation_mode: "plan_approve_commit",
    cookies_export: "denied"
  };
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
  if (name.endsWith("_status")) {
    return { content: [{ type: "text", text: JSON.stringify(await status(), null, 2) }] };
  }
  if (name.endsWith("_open")) {
    return { content: [{ type: "text", text: JSON.stringify(await openUi(input), null, 2) }] };
  }
  if (name.endsWith("_capture_evidence")) {
    return { content: [{ type: "text", text: JSON.stringify(await captureEvidence(input), null, 2) }] };
  }
  if (name.endsWith("_plan_action")) {
    return {
      content: [{ type: "text", text: JSON.stringify({ status: "PLAN_CREATED", product, action: input?.action, target: input?.target || "", mutation_requires_external_approval: true }, null, 2) }]
    };
  }
  throw new Error(`Unknown tool: ${name}`);
}

const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
rl.on("line", async (line) => {
  let msg;
  try {
    msg = JSON.parse(line);
  } catch {
    return;
  }
  const id = msg.id ?? null;
  try {
    if (msg.method === "initialize") {
      response(id, { protocolVersion: "2024-11-05", capabilities: { tools: {} }, serverInfo: { name: `${product}-web-ui-mcp`, version: "0.2.0" } });
    } else if (msg.method === "tools/list") {
      response(id, { tools: tools() });
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
});
