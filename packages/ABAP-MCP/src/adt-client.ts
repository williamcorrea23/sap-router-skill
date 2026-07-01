/**
 * ABAP MCP Server — ADT client singleton.
 *
 * A single `abap-adt-api` `ADTClient` is created lazily on first use and
 * reused across all tool calls. The agent backing the underlying axios
 * transport is selected from a small ordered list of strategies:
 *
 *   1. BTP Connectivity Proxy        (Cloud Connector / hybrid CAP dev)
 *   2. SAProuter NI tunnel           (B2B VPN where only SAProuter is open)
 *   3. Generic HTTP CONNECT proxy    (corporate proxy or local SSH tunnel)
 *   4. Direct HTTPS                  (optionally with self-signed tolerance)
 *
 * Only one strategy is active at a time; the first configured one wins. See
 * the `readme.md` "Network connectivity" section for the matching env vars.
 */

import http from "http";
import https from "https";
import { ADTClient, createSSLConfig } from "abap-adt-api";
import type { ClientOptions } from "abap-adt-api";
import { HttpsProxyAgent } from "https-proxy-agent";
import { ErrorCode, McpError } from "@modelcontextprotocol/sdk/types.js";
import { cfg } from "./config.js";
import { ADT_CORE_DISCOVERY } from "./adt-endpoints.js";
import { SAProuterHttpsAgent } from "./saprouter-agent.js";
import { parseSapRouteString, SAProuterHop } from "./saprouter.js";
import {
  BtpConnectivityAgentBundle,
  createBtpConnectivityAgentBundle,
  loadBtpConnectivityCreds,
} from "./btp/index.js";

/** Discriminated agent spec so the wiring layer can switch on `kind` cleanly. */
type AgentSpec =
  | { kind: "http"; agent: http.Agent }
  | { kind: "https"; agent: https.Agent }
  | { kind: "none" };

let adtClient: ADTClient | null = null;
let btpBundle: BtpConnectivityAgentBundle | null = null;

/* ============================================================ *
 * Public API                                                    *
 * ============================================================ */

/**
 * Return a logged-in ADT client. The first call performs the login; later
 * calls reuse the connection after a cheap HEAD-discovery liveness probe.
 * If the session has expired, a new client is created transparently.
 */
export async function getClient(): Promise<ADTClient> {
  if (adtClient && (await isStillAlive(adtClient))) return adtClient;
  adtClient = null;

  const agentSpec = await selectAgent();
  adtClient = await buildLoggedInClient(agentSpec);
  return adtClient;
}

/* ============================================================ *
 * Agent strategy selection                                      *
 * ============================================================ */

async function selectAgent(): Promise<AgentSpec> {
  if (cfg.btpConnectivityProxy) return buildBtpConnectivityAgent();
  if (cfg.sapRouter) return buildSAProuterAgent();
  if (cfg.proxyUrl) return buildHttpProxyAgent();
  return buildDirectHttpsAgent();
}

async function buildBtpConnectivityAgent(): Promise<AgentSpec> {
  const creds = loadBtpConnectivityCreds();
  if (!creds) {
    throw new Error(
      "SAP_BTP_CONNECTIVITY_PROXY is set but no connectivity service credentials are " +
      "available. Provide one of: SAP_BTP_CONNECTIVITY_CREDS_FILE, " +
      "SAP_BTP_CONNECTIVITY_CDS_BIND_FILE + SAP_BTP_CONNECTIVITY_CDS_BIND_NAME, " +
      "or SAP_BTP_CONNECTIVITY_CLIENT_ID / _CLIENT_SECRET / _TOKEN_URL.",
    );
  }
  btpBundle = createBtpConnectivityAgentBundle(
    {
      proxyUrl: cfg.btpConnectivityProxy,
      creds,
      locationId: cfg.btpConnectivityLocationId || undefined,
      allowUnauthorized: cfg.allowUnauthorized,
      debug: cfg.btpConnectivityDebug,
    },
    cfg.url,
  );
  // Pre-fetch the JWT so the first proxy request carries Proxy-Authorization.
  await btpBundle.tokenSource.get();
  if (cfg.btpConnectivityDebug) {
    console.error(
      `[btp-connectivity] using ${btpBundle.scheme.toUpperCase()} forward proxy at ` +
      `${cfg.btpConnectivityProxy} for target ${cfg.url}`,
    );
  }
  return btpBundle.scheme === "https"
    ? { kind: "https", agent: btpBundle.agent as https.Agent }
    : { kind: "http", agent: btpBundle.agent as http.Agent };
}

function buildSAProuterAgent(): AgentSpec {
  const router = resolveFirstHop(cfg.sapRouter);
  if (cfg.sapRouterPassword) router.password = cfg.sapRouterPassword;
  return {
    kind: "https",
    agent: new SAProuterHttpsAgent({
      router,
      keepAlive: true,
      rejectUnauthorized: !cfg.allowUnauthorized,
      debug: cfg.sapRouterDebug,
    }),
  };
}

function buildHttpProxyAgent(): AgentSpec {
  return {
    kind: "https",
    agent: new HttpsProxyAgent(cfg.proxyUrl, {
      keepAlive: true,
      rejectUnauthorized: !cfg.allowUnauthorized,
    }),
  };
}

function buildDirectHttpsAgent(): AgentSpec {
  if (!cfg.allowUnauthorized) return { kind: "none" };
  const sslOptions = createSSLConfig(true);
  return sslOptions.httpsAgent
    ? { kind: "https", agent: sslOptions.httpsAgent }
    : { kind: "none" };
}

function resolveFirstHop(raw: string): SAProuterHop {
  if (raw.startsWith("/")) return parseSapRouteString(raw)[0];
  const [host, portStr] = raw.split(":");
  return { host, port: portStr ? parseInt(portStr, 10) : 3299 };
}

/* ============================================================ *
 * Client construction & maintenance                             *
 * ============================================================ */

async function buildLoggedInClient(agentSpec: AgentSpec): Promise<ADTClient> {
  const options: ClientOptions & { httpAgent?: http.Agent } = { keepAlive: true };
  if (agentSpec.kind === "https") options.httpsAgent = agentSpec.agent;
  if (agentSpec.kind === "http") options.httpAgent = agentSpec.agent;

  const client = new ADTClient(cfg.url, cfg.user, cfg.password, cfg.client, cfg.language, options);

  if (agentSpec.kind === "http") patchAxiosHttpAgent(client, agentSpec.agent);

  try {
    await client.login();
  } catch (e) {
    throw new McpError(ErrorCode.InternalError, formatLoginError(e));
  }
  return client;
}

async function isStillAlive(client: ADTClient): Promise<boolean> {
  try {
    await client.httpClient.request(ADT_CORE_DISCOVERY, { method: "HEAD" });
    return true;
  } catch {
    return false;
  }
}

function formatLoginError(err: unknown): string {
  const msg = err instanceof Error ? err.message : String(err);
  const via = describeActiveRoute();
  return (
    `ADT connection not available${via}: ${msg}. ` +
    `Check: SAP_URL (${cfg.url}) reachable through the configured route? ` +
    `Cloud Connector exposes /sap/bc/adt for that virtual host? ` +
    `SSH tunnel for the connectivity proxy still up? Credentials correct?`
  );
}

function describeActiveRoute(): string {
  if (cfg.btpConnectivityProxy) return ` (via BTP Connectivity Proxy ${cfg.btpConnectivityProxy})`;
  if (cfg.sapRouter) return ` (via SAProuter ${cfg.sapRouter})`;
  if (cfg.proxyUrl) return ` (via proxy ${cfg.proxyUrl})`;
  return "";
}

/* ============================================================ *
 * abap-adt-api axios httpAgent monkey-patch                     *
 * ============================================================ *
 *
 * `abap-adt-api` is `axios`-based and accepts `httpsAgent` in its public
 * `ClientOptions`, but does not forward an `httpAgent`. For plain `http://`
 * targets (used by the BTP Connectivity Proxy on its forward-proxy port)
 * this means axios bypasses our agent entirely and tries to DNS-resolve the
 * on-prem virtual host locally, which always fails.
 *
 * The fix is to reach into the library's hidden axios instance after the
 * client is constructed and set `defaults.httpAgent` ourselves, plus
 * `defaults.proxy = false` so axios does not also try to honour any
 * ambient `HTTP_PROXY` env var.
 *
 * If the upstream library renames its internals we log a clear warning and
 * fall back to whatever axios would have done — the resulting error is
 * surfaced to the caller, not silently swallowed.
 */

interface AxiosClientStub {
  axios?: { defaults?: { httpAgent?: http.Agent; proxy?: false } };
}
interface AdtHttpStub {
  httpclient?: AxiosClientStub;
}
interface AdtClientInternals {
  httpClient?: AdtHttpStub;
  h?: AdtHttpStub;
}

function patchAxiosHttpAgent(client: ADTClient, agent: http.Agent): void {
  const internals = client as unknown as AdtClientInternals;
  const adtHttp = internals.httpClient ?? internals.h;
  const defaults = adtHttp?.httpclient?.axios?.defaults;
  if (!defaults) {
    console.error(
      "[btp-connectivity] WARNING: could not locate axios instance inside abap-adt-api " +
      "(tried client.httpClient.httpclient.axios). http:// targets may fail with DNS errors.",
    );
    return;
  }
  defaults.httpAgent = agent;
  defaults.proxy = false;
  if (cfg.btpConnectivityDebug) {
    console.error("[btp-connectivity] injected httpAgent into abap-adt-api's axios instance");
  }
}
