#!/usr/bin/env node
/**
 * ABAP MCP Server — entry point.
 * Prints a startup banner, connects the MCP stdio transport, and starts serving.
 */

import "dotenv/config";

import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

import { cfg } from "./config.js";
import { getClient } from "./adt-client.js";
import { server } from "./server.js";
import { CORE_TOOL_NAMES, ALL_TOOLS } from "./tools/tool-registry.js";

async function main(): Promise<void> {
  printBanner();
  await tryInitialConnect();
  console.error("");

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("✅ MCP Server läuft auf stdio — bereit für Verbindungen");
}

function printBanner(): void {
  const onOff = (b: boolean): string => (b ? "✅ aktiv" : "❌ deaktiviert");
  console.error("╔══════════════════════════════════════════╗");
  console.error("║   ABAP MCP Server v2.0 — Extended        ║");
  console.error("╚══════════════════════════════════════════╝");
  console.error(`  Instance: ${cfg.instanceId}`);
  console.error(`  System  : ${cfg.url}`);
  printNetworkRoute();
  console.error(`  User    : ${cfg.user}  Client: ${cfg.client}  Lang: ${cfg.language}`);
  console.error(`  Write   : ${onOff(cfg.allowWrite)}`);
  console.error(`  Delete  : ${onOff(cfg.allowDelete)}`);
  if (cfg.allowWrite) {
    console.error(`  Blocked : ${cfg.blockedPackages.join(", ") || "keine"}`);
    console.error(`  Execute : ${onOff(cfg.allowExecute)}`);
  }
  const toolsLabel = cfg.deferTools
    ? `${CORE_TOOL_NAMES.size} initial (${ALL_TOOLS.length} gesamt, deferred)`
    : `${ALL_TOOLS.length} registriert`;
  console.error(`  Tools   : ${toolsLabel}`);
  console.error(`  Doku    : help.sap.com v${cfg.sapAbapVersion}`);
  const webTls = cfg.webAllowUnauthorized ? " (⚠️ TLS-Verifikation für Web-Calls deaktiviert)" : "";
  console.error(`  WebSrch : ${cfg.tavilyApiKey ? `✅ aktiv${webTls}` : "❌ nicht konfiguriert"}`);
  console.error(`  Prompts : 1 (abap_develop)`);
}

function printNetworkRoute(): void {
  if (cfg.btpConnectivityProxy) {
    const loc = cfg.btpConnectivityLocationId ? ` loc=${cfg.btpConnectivityLocationId}` : "";
    const dbg = cfg.btpConnectivityDebug ? " (debug)" : "";
    console.error(`  BTP CP  : ${cfg.btpConnectivityProxy}${loc}${dbg}`);
    return;
  }
  if (cfg.sapRouter) {
    console.error(`  Router  : ${cfg.sapRouter}${cfg.sapRouterDebug ? " (debug)" : ""}`);
    return;
  }
  if (cfg.proxyUrl) console.error(`  Proxy   : ${cfg.proxyUrl}`);
}

async function tryInitialConnect(): Promise<void> {
  try {
    await getClient();
    console.error("  ADT     : ✅ Verbunden");
  } catch (e) {
    console.error(`  ADT     : ⚠️  Verbindung fehlgeschlagen — ${(e as Error).message}`);
    console.error("            Server läuft weiter; Verbindung wird beim ersten Tool-Aufruf erneut versucht.");
  }
}

main().catch((e) => {
  console.error("Fataler Fehler:", e);
  process.exit(1);
});
