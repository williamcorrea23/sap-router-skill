#!/usr/bin/env node
/**
 * npm run preflight
 *
 * Validates your setup before connecting to Claude Code:
 *   1. Checks .env exists and all required variables are set
 *   2. Detects placeholder values (e.g. "your-sap-host.example.com")
 *   3. Tests real HTTPS connectivity to your SAP system
 *   4. Verifies the SAP ADT service responds
 *   5. Confirms dist/index.js exists (build is current)
 *
 * Run this after 'npm run build' and before registering with Claude Code.
 */

import { existsSync, readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import https from "https";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..");

const BOLD   = "\x1b[1m";
const GREEN  = "\x1b[32m";
const YELLOW = "\x1b[33m";
const RED    = "\x1b[31m";
const RESET  = "\x1b[0m";

function ok(msg)   { console.log(`${GREEN}  ✓${RESET} ${msg}`); }
function warn(msg) { console.log(`${YELLOW}  !${RESET} ${msg}`); }
function fail(msg) { console.log(`${RED}  ✗${RESET} ${msg}`); }
function info(msg) { console.log(`    ${msg}`); }

let passed = 0;
let failed = 0;
let warned = 0;

function pass(msg)    { ok(msg);   passed++; }
function problem(msg) { fail(msg); failed++; }
function notice(msg)  { warn(msg); warned++; }

console.log(`\n${BOLD}SAP Transport MCP — Preflight Check${RESET}\n`);

// ─── Load .env manually (avoid ESM/CJS issues with dotenv) ───────────────────

const envPath = resolve(ROOT, ".env");
if (!existsSync(envPath)) {
  problem(".env file not found — run 'npm run setup' first");
  console.log(`\n${RED}Preflight failed — fix the above issues and retry.${RESET}\n`);
  process.exit(1);
}

const env = {};
const envLines = readFileSync(envPath, "utf8").split("\n");
for (const line of envLines) {
  const trimmed = line.trim();
  if (!trimmed || trimmed.startsWith("#")) continue;
  const eqIdx = trimmed.indexOf("=");
  if (eqIdx < 0) continue;
  const key = trimmed.slice(0, eqIdx).trim();
  const val = trimmed.slice(eqIdx + 1).trim();
  env[key] = val;
}

// ─── Check 1: Required variables ─────────────────────────────────────────────

console.log(`${BOLD}[1] Required environment variables${RESET}`);

const REQUIRED = ["SAP_HOSTNAME", "SAP_SYSNR", "SAP_CLIENT", "AUTH_METHOD"];
for (const key of REQUIRED) {
  if (!env[key]) {
    problem(`${key} is not set in .env`);
  } else {
    pass(`${key} = ${key.includes("PASSWORD") ? "***" : env[key]}`);
  }
}

const authMethod = env["AUTH_METHOD"];
if (authMethod === "basic") {
  for (const key of ["SAP_USERNAME", "SAP_PASSWORD"]) {
    if (!env[key]) problem(`${key} is required when AUTH_METHOD=basic`);
    else pass(`${key} is set`);
  }
} else if (authMethod === "certificate") {
  if (!env["CERT_THUMBPRINT"]) problem("CERT_THUMBPRINT is required when AUTH_METHOD=certificate");
  else pass(`CERT_THUMBPRINT is set`);
  if (!env["SAP_USERNAME"]) problem("SAP_USERNAME is required even for certificate auth");
  else pass("SAP_USERNAME is set");
} else if (authMethod) {
  problem(`AUTH_METHOD="${authMethod}" is invalid — must be "basic" or "certificate"`);
}

// ─── Check 2: Placeholder detection ──────────────────────────────────────────

console.log(`\n${BOLD}[2] Placeholder value detection${RESET}`);

const PLACEHOLDERS = {
  SAP_HOSTNAME: ["your-sap-host.example.com", "example.com"],
  SAP_USERNAME: ["your_sap_user", "your_user", "YOUR_SAP_USER"],
  SAP_PASSWORD: ["your_sap_password", "YOUR_SAP_PASSWORD"],
  CERT_THUMBPRINT: ["AB:CD:EF:12:34:56"],
};

let anyPlaceholder = false;
for (const [key, placeholders] of Object.entries(PLACEHOLDERS)) {
  const val = env[key];
  if (!val) continue;
  if (placeholders.some((p) => val.toLowerCase().includes(p.toLowerCase()))) {
    problem(`${key} still has a placeholder value: "${val}"`);
    info(`→ Replace with your real SAP value in .env`);
    anyPlaceholder = true;
  }
}
if (!anyPlaceholder) pass("No placeholder values detected");

// ─── Check 3: SAP_SYSNR format ────────────────────────────────────────────────

console.log(`\n${BOLD}[3] Format validation${RESET}`);

const sysnr = env["SAP_SYSNR"];
if (sysnr && !/^\d{2}$/.test(sysnr)) {
  problem(`SAP_SYSNR="${sysnr}" must be exactly 2 digits (e.g. "00", "01")`);
} else if (sysnr) {
  pass(`SAP_SYSNR format OK (${sysnr})`);
}

const client = env["SAP_CLIENT"];
if (client && !/^\d{3}$/.test(client)) {
  problem(`SAP_CLIENT="${client}" must be exactly 3 digits (e.g. "100")`);
} else if (client) {
  pass(`SAP_CLIENT format OK (${client})`);
}

// ─── Check 4: dist/index.js exists ───────────────────────────────────────────

console.log(`\n${BOLD}[4] Build output${RESET}`);

const distIndex = resolve(ROOT, "dist", "src", "index.js");
if (!existsSync(distIndex)) {
  problem("dist/src/index.js not found — run 'npm run build' first");
} else {
  pass("dist/src/index.js exists");
}

// ─── Check 5: SAP connectivity ───────────────────────────────────────────────

console.log(`\n${BOLD}[5] SAP connectivity${RESET}`);

const hostname = env["SAP_HOSTNAME"];
const sysnrRaw = env["SAP_SYSNR"] ?? "00";
const clientVal = env["SAP_CLIENT"] ?? "100";
const langVal   = env["SAP_LANGUAGE"] ?? "EN";
const portOverride = env["SAP_HTTPS_PORT"] ? parseInt(env["SAP_HTTPS_PORT"], 10) : null;
const port = portOverride ?? (8000 + parseInt(sysnrRaw, 10));

if (!hostname || PLACEHOLDERS.SAP_HOSTNAME.some((p) => hostname.includes(p))) {
  notice("Skipping connectivity test — SAP_HOSTNAME is not configured");
} else {
  const username = env["SAP_USERNAME"] ?? "";
  const password = env["SAP_PASSWORD"] ?? "";
  const token = Buffer.from(`${username}:${password}`).toString("base64");

  info(`Testing HTTPS connection to ${hostname}:${port} ...`);

  await new Promise((resolve) => {
    const req = https.request(
      {
        hostname,
        port,
        path: "/sap/bc/adt/discovery",
        method: "GET",
        timeout: 10000,
        rejectUnauthorized: false, // allow self-signed certs during preflight
        headers: {
          Authorization: `Basic ${token}`,
          "sap-client": clientVal,
          "sap-language": langVal,
          Accept: "application/json",
        },
      },
      (res) => {
        const status = res.statusCode ?? 0;
        if (status === 200 || status === 401) {
          // 401 means we reached SAP — credentials may be wrong but SAP is there
          if (status === 401) {
            problem(`SAP ADT responded with 401 Unauthorized`);
            info(`→ Check SAP_USERNAME and SAP_PASSWORD in .env`);
            info(`→ Confirm your user has role SAP_BC_DWB_ABAPDEVELOPER`);
          } else {
            pass(`SAP ADT responded HTTP ${status} — connection OK`);
          }
        } else if (status === 403) {
          notice(`SAP ADT responded HTTP 403 — connected but authorization issue`);
          info(`→ Confirm ICF service /sap/bc/adt/ is activated (transaction SICF)`);
          info(`→ Check user has S_ADT_RES authorization object`);
        } else if (status === 404) {
          problem(`SAP ADT responded HTTP 404 — /sap/bc/adt/ not found`);
          info(`→ ICF service /sap/bc/adt/ may not be activated (transaction SICF)`);
          info(`→ Ask your Basis admin to activate it`);
        } else {
          notice(`SAP responded HTTP ${status} — unexpected, but SAP is reachable`);
        }
        res.resume();
        resolve();
      }
    );

    req.on("timeout", () => {
      req.destroy();
      problem(`Connection timed out to ${hostname}:${port}`);
      info(`→ Check VPN — on-prem SAP requires VPN access`);
      info(`→ Verify SAP_HOSTNAME and SAP_SYSNR are correct`);
      info(`→ For cloud/BTP systems, set SAP_HTTPS_PORT=443 in .env`);
      resolve();
    });

    req.on("error", (e) => {
      if (e.code === "ECONNREFUSED") {
        problem(`Connection refused to ${hostname}:${port}`);
        info(`→ Port ${port} is not open — verify SAP_SYSNR (port = 8000 + sysnr)`);
        info(`→ For cloud/BTP: set SAP_HTTPS_PORT=443 in .env`);
      } else if (e.code === "ENOTFOUND") {
        problem(`Hostname not found: ${hostname}`);
        info(`→ Check SAP_HOSTNAME spelling in .env`);
        info(`→ Ensure VPN is connected if this is an on-prem system`);
      } else {
        problem(`Connection error: ${e.message}`);
      }
      resolve();
    });

    req.end();
  });
}

// ─── Summary ─────────────────────────────────────────────────────────────────

console.log(`\n${"─".repeat(50)}`);
console.log(`${BOLD}Summary:${RESET} ${GREEN}${passed} passed${RESET}  ${failed > 0 ? RED : ""}${failed} failed${RESET}  ${warned > 0 ? YELLOW : ""}${warned} warnings${RESET}\n`);

if (failed > 0) {
  console.log(`${RED}${BOLD}Preflight failed.${RESET} Fix the issues above before starting Claude Code.\n`);
  process.exit(1);
} else if (warned > 0) {
  console.log(`${YELLOW}${BOLD}Preflight passed with warnings.${RESET} Review warnings before use.\n`);
} else {
  console.log(`${GREEN}${BOLD}All checks passed.${RESET} You are ready to connect to Claude Code.\n`);
  console.log(`Next: restart Claude Code, then ask "What SAP transport tools do you have?"\n`);
}
