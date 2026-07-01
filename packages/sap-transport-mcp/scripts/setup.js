#!/usr/bin/env node
/**
 * npm run setup
 *
 * One-command developer setup:
 *   1. Creates .env from .env.example (if not already present)
 *   2. Creates .mcp.json with the absolute path to dist/index.js auto-filled
 *
 * Safe to re-run — never overwrites an existing .env.
 */

import { existsSync, readFileSync, writeFileSync, copyFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..");

const BOLD  = "\x1b[1m";
const GREEN = "\x1b[32m";
const YELLOW = "\x1b[33m";
const RED   = "\x1b[31m";
const RESET = "\x1b[0m";

function ok(msg)   { console.log(`${GREEN}  ✓${RESET} ${msg}`); }
function warn(msg) { console.log(`${YELLOW}  !${RESET} ${msg}`); }
function fail(msg) { console.log(`${RED}  ✗${RESET} ${msg}`); }
function info(msg) { console.log(`    ${msg}`); }

console.log(`\n${BOLD}SAP Transport MCP — Setup${RESET}\n`);

// ─── Step 1: .env ─────────────────────────────────────────────────────────────

const envPath        = resolve(ROOT, ".env");
const envExamplePath = resolve(ROOT, ".env.example");

if (existsSync(envPath)) {
  warn(".env already exists — skipping (not overwritten)");
} else {
  if (!existsSync(envExamplePath)) {
    fail(".env.example not found — is this a complete clone?");
    process.exit(1);
  }
  copyFileSync(envExamplePath, envPath);
  ok(".env created from .env.example");
  info("→ Open .env and fill in your SAP_HOSTNAME, SAP_USERNAME, SAP_PASSWORD");
}

// ─── Step 2: .mcp.json with absolute path ─────────────────────────────────────

const mcpPath        = resolve(ROOT, ".mcp.json");
const mcpExamplePath = resolve(ROOT, ".mcp.example.json");
const distIndexPath  = resolve(ROOT, "dist", "src", "index.js");

if (!existsSync(mcpExamplePath)) {
  fail(".mcp.example.json not found — is this a complete clone?");
  process.exit(1);
}

const example = JSON.parse(readFileSync(mcpExamplePath, "utf8"));
delete example._comment;

// Inject the real absolute path
const serverEntry = example.mcpServers?.["sap-transport"];
if (!serverEntry) {
  fail('Could not find mcpServers["sap-transport"] in .mcp.example.json');
  process.exit(1);
}
serverEntry.args = [distIndexPath];

if (existsSync(mcpPath)) {
  warn(".mcp.json already exists — updating args path only");
  const existing = JSON.parse(readFileSync(mcpPath, "utf8"));
  if (existing.mcpServers?.["sap-transport"]) {
    existing.mcpServers["sap-transport"].args = [distIndexPath];
    writeFileSync(mcpPath, JSON.stringify(existing, null, 2) + "\n");
  } else {
    writeFileSync(mcpPath, JSON.stringify(example, null, 2) + "\n");
  }
} else {
  writeFileSync(mcpPath, JSON.stringify(example, null, 2) + "\n");
  ok(".mcp.json created");
}

info(`→ Server path set to: ${distIndexPath}`);

// ─── Check: dist/index.js exists ──────────────────────────────────────────────

if (!existsSync(distIndexPath)) {
  warn("dist/src/index.js does not exist yet — run 'npm run build' before starting Claude Code");
} else {
  ok("dist/src/index.js found — build is current");
}

// ─── Next steps ───────────────────────────────────────────────────────────────

console.log(`
${BOLD}Next steps:${RESET}

  1. Edit ${BOLD}.env${RESET} with your SAP credentials (see README for where to find them)
  2. Run ${BOLD}npm run build${RESET}
  3. Run ${BOLD}npm run preflight${RESET} to validate your config and test SAP connectivity
  4. Restart Claude Code — then ask: "What SAP transport tools do you have?"
`);
