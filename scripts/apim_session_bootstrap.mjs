#!/usr/bin/env node
// Bring up the API Management access channels from one command.
//
//   node scripts/apim_session_bootstrap.mjs connect   start Chrome with remote debugging, open the tenant, wait for login
//   node scripts/apim_session_bootstrap.mjs status    report which channel is usable
//   node scripts/apim_session_bootstrap.mjs test      run the bundled echo proxy against the tenant
//
// The service-key OAuth channel is SAP's documented path and needs no browser.
// The browser session channel exists for tenants where no service key is available;
// the user logs in themselves and the credentials never leave the browser.
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { setTimeout as delay } from "node:timers/promises";
import { fileURLToPath } from "node:url";

import { apiFetch, browserVersion, cdpBaseUrl, findTab, originOf, websocketAvailable, withSession } from "./cdp_session.mjs";
import { apiRequest as oauthRequest, channelStatus as oauthStatus } from "./apim_oauth.mjs";
import { loadDotEnv } from "./dotenv_lite.mjs";

// Both channels read their configuration lazily, so loading .env here is enough.
loadDotEnv();

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const CHROME_CANDIDATES = [
  process.env.CHROME_PATH,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
  "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/usr/bin/google-chrome",
  "/usr/bin/chromium",
].filter(Boolean);

function findChrome() {
  return CHROME_CANDIDATES.find((candidate) => fs.existsSync(candidate)) || null;
}

function report(value) {
  process.stdout.write(JSON.stringify(value, null, 2) + "\n");
}

async function cdpReachable() {
  try {
    return await browserVersion();
  } catch {
    return null;
  }
}

async function connect() {
  const webUrl = process.env.APIM_WEB_URL || "";
  const oauth = oauthStatus();
  if (!webUrl) {
    return {
      status: "BLOCKED",
      reason: "APIM_WEB_URL missing",
      fix: "Set APIM_WEB_URL to the API portal URL, e.g. https://<subaccount>.integrationsuite.cfapps.<region>.hana.ondemand.com",
      oauth_channel: oauth,
    };
  }
  if (!websocketAvailable()) {
    return { status: "BLOCKED", reason: "global WebSocket unavailable; Node 22+ required", node: process.version };
  }

  let browser = await cdpReachable();
  let launched = false;
  if (!browser) {
    const chrome = findChrome();
    if (!chrome) {
      return {
        status: "BLOCKED",
        reason: "no Chrome/Edge binary found",
        fix: "Set CHROME_PATH, or start the browser yourself: chrome.exe --remote-debugging-port=9222 --user-data-dir=%TEMP%\\sap-router-chrome",
      };
    }
    const port = process.env.CHROME_DEBUGGING_PORT || "9222";
    const profile = path.join(process.env.TEMP || process.env.TMPDIR || "/tmp", "sap-router-chrome");
    const child = spawn(chrome, [`--remote-debugging-port=${port}`, `--user-data-dir=${profile}`, webUrl], {
      detached: true,
      stdio: "ignore",
    });
    child.unref();
    launched = true;
    for (let attempt = 0; attempt < 20 && !browser; attempt += 1) {
      await delay(500);
      browser = await cdpReachable();
    }
    if (!browser) {
      return { status: "DEGRADED", reason: `browser started but CDP is not answering at ${cdpBaseUrl()}`, profile };
    }
  }

  const origin = originOf(webUrl);
  const deadlineMs = Number(process.env.APIM_LOGIN_TIMEOUT_MS || 180_000);
  const started = Date.now();
  let authenticated = false;
  let tab = null;
  while (Date.now() - started < deadlineMs) {
    tab = await findTab(origin);
    if (tab) {
      const probe = await withSession(origin, (session) => apiFetch(session, "/apiportal/api/1.0/Management.svc/$metadata"));
      if (probe?.status === "OK") {
        authenticated = true;
        break;
      }
    }
    await delay(3000);
  }

  return {
    status: authenticated ? "READY" : "PENDING_LOGIN",
    launched_browser: launched,
    browser: browser.Browser,
    cdp_url: cdpBaseUrl(),
    origin,
    tab_url: tab?.url || null,
    authenticated,
    channel: "session",
    sanctioned: false,
    note: "Browser session reuse is not an SAP-documented API channel. Prefer the service-key OAuth channel where one is available.",
    oauth_channel: oauth,
    next_step: authenticated
      ? "Run: npm run apim:test"
      : `Finish the tenant login in the opened tab, then run: npm run apim:session (waited ${Math.round((Date.now() - started) / 1000)}s)`,
  };
}

async function status() {
  const oauth = oauthStatus();
  const result = {
    scope: "API lifecycle tooling only. See SAP API Policy: https://help.sap.com/doc/sap-api-policy/latest/en-US/API_Policy_latest.pdf",
    oauth_channel: { ...oauth, sanctioned: true },
  };
  if (oauth.configured) {
    const probe = await oauthRequest("/APIProxies?$top=1&$format=json");
    result.status = probe.status === "OK" ? "READY" : "DEGRADED";
    result.channel = "oauth";
    result.probe_http_status = probe.http_status;
    if (probe.status !== "OK") {
      result.reason = probe.reason || "service key configured but the management API rejected the call";
    }
    return result;
  }
  const webUrl = process.env.APIM_WEB_URL || "";
  if (!webUrl) {
    result.status = "BLOCKED";
    result.reason = "no service key configured and APIM_WEB_URL missing";
    return result;
  }
  const origin = originOf(webUrl);
  const browser = await cdpReachable();
  if (!browser) {
    result.status = "DEGRADED";
    result.channel = "session";
    result.reason = `Chrome/CDP not reachable at ${cdpBaseUrl()}`;
    result.fix = "Run: npm run apim:connect";
    return result;
  }
  const probe = await withSession(origin, (session) => apiFetch(session, "/apiportal/api/1.0/Management.svc/$metadata"));
  result.status = probe?.status === "OK" ? "READY" : "DEGRADED";
  result.channel = "session";
  result.sanctioned = false;
  result.origin = origin;
  result.probe_http_status = probe?.http_status;
  return result;
}

async function test() {
  const runtimeUrl = process.env.APIM_TEST_PROXY_URL || "";
  const bundle = path.join(ROOT, "scratch", "apim", "echo.zip");
  const channel = await status();
  const out = { channel_status: channel, bundle_present: fs.existsSync(bundle), bundle };
  if (!runtimeUrl) {
    out.status = "PARTIAL";
    out.reason = "APIM_TEST_PROXY_URL not set, so only the offline checks ran";
    out.next_step =
      "Generate a bundle with: python scripts/apim_proxy_packager.py template --kind echo --name ZROUTER_SMOKE --output scratch/apim/echo.zip, " +
      "deploy it, then set APIM_TEST_PROXY_URL to its runtime URL.";
    return out;
  }
  const started = Date.now();
  try {
    const response = await fetch(runtimeUrl, { signal: AbortSignal.timeout(45_000) });
    const text = await response.text();
    out.status = response.ok ? "OK" : "ERROR";
    out.http_status = response.status;
    out.elapsed_ms = Date.now() - started;
    out.url = runtimeUrl;
    out.body = text.slice(0, 2000);
  } catch (err) {
    out.status = "ERROR";
    out.url = runtimeUrl;
    out.reason = err?.message || String(err);
  }
  return out;
}

const command = process.argv[2] || "status";
const handlers = { connect, status, test };
const handler = handlers[command];
if (!handler) {
  report({ status: "ERROR", reason: `unknown command: ${command}`, commands: Object.keys(handlers) });
  process.exit(1);
}
const result = await handler();
report(result);
process.exit(["READY", "OK", "PARTIAL"].includes(result.status) ? 0 : 1);
