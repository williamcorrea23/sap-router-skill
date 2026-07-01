/**
 * HTTP(S) agent factory for routing traffic through the SAP BTP
 * Connectivity Proxy.
 *
 * Proxy modes (chosen per the scheme of the target URL — *not* the backend):
 *
 *   - target http://  →  HTTP forward proxy  (proxy listener on :20003)
 *                        The proxy reads the absolute-form Request-URI and
 *                        forwards it to the Cloud Connector tunnel. Add the
 *                        token + location-ID as `Proxy-Authorization` and
 *                        `SAP-Connectivity-SCC-Location_ID` headers on every
 *                        request.
 *
 *   - target https:// →  HTTP CONNECT proxy  (proxy listener on :20004)
 *                        The proxy opens an opaque TCP tunnel; TLS happens
 *                        end-to-end with the on-prem system. The auth and
 *                        location-ID headers travel on the CONNECT line.
 *
 * The location-ID header MUST be sent as plain ASCII despite older SAP
 * documentation hinting at base64. Empirically the proxy rejects base64
 * values with HTTP 503. The `SAP_BTP_CONNECTIVITY_LOCATION_ID_BASE64=true`
 * escape hatch is kept for tenants that enforce the opposite convention.
 */

import http from "http";
import https from "https";
import type { OutgoingHttpHeaders } from "http";
import { HttpProxyAgent } from "http-proxy-agent";
import { HttpsProxyAgent } from "https-proxy-agent";
import { BtpConnectivityTokenSource } from "./token.js";
import type { BtpConnectivityCreds } from "./credentials.js";

export interface BtpConnectivityAgentConfig {
  /** XSUAA-issued credentials for the connectivity service instance. */
  readonly creds: BtpConnectivityCreds;
  /** Local URL of the proxy listener, e.g. `http://localhost:20003`. */
  readonly proxyUrl: string;
  /** Cloud Connector location-ID. Empty string targets the default tunnel. */
  readonly locationId?: string;
  /** When the proxy listener is HTTPS with a self-signed cert (rare). */
  readonly allowUnauthorized?: boolean;
  /** Emit verbose logs to stderr. */
  readonly debug?: boolean;
}

export interface BtpConnectivityAgentBundle {
  /** Live JWT source. The agent's per-request `headers` callback reads from it. */
  readonly tokenSource: BtpConnectivityTokenSource;
  /** Either an HttpProxyAgent or HttpsProxyAgent instance, pre-configured. */
  readonly agent: http.Agent | https.Agent;
  /** The scheme of the *target* URL — drives which agent type was created. */
  readonly scheme: "http" | "https";
}

/**
 * Build a proxy agent bundle for the given target URL.
 *
 * @param config Connectivity proxy configuration.
 * @param targetUrl The eventual on-prem URL the agent will be used to reach.
 *                  Used to decide between an HTTP forward agent (port 20003)
 *                  and an HTTPS CONNECT agent (port 20004).
 */
export function createBtpConnectivityAgentBundle(
  config: BtpConnectivityAgentConfig,
  targetUrl: string,
): BtpConnectivityAgentBundle {
  const tokenSource = new BtpConnectivityTokenSource(config.creds, config.debug);
  const scheme = pickScheme(targetUrl);
  const headersFn = buildHeadersFn(tokenSource, config);

  const agent: http.Agent | https.Agent =
    scheme === "https"
      ? new HttpsProxyAgent(config.proxyUrl, {
          keepAlive: true,
          rejectUnauthorized: !config.allowUnauthorized,
          headers: headersFn,
        })
      : new HttpProxyAgent(config.proxyUrl, {
          keepAlive: true,
          headers: headersFn,
        });

  return { tokenSource, agent, scheme };
}

function pickScheme(targetUrl: string): "http" | "https" {
  try {
    return new URL(targetUrl).protocol === "https:" ? "https" : "http";
  } catch {
    return "http";
  }
}

function buildHeadersFn(
  tokenSource: BtpConnectivityTokenSource,
  config: BtpConnectivityAgentConfig,
): () => OutgoingHttpHeaders {
  const encodeBase64 = process.env.SAP_BTP_CONNECTIVITY_LOCATION_ID_BASE64 === "true";
  return () => {
    const headers: OutgoingHttpHeaders = {};
    const token = tokenSource.peek();
    if (token) headers["Proxy-Authorization"] = `Bearer ${token}`;
    if (config.locationId) {
      headers["SAP-Connectivity-SCC-Location_ID"] = encodeBase64
        ? Buffer.from(config.locationId, "utf-8").toString("base64")
        : config.locationId;
    }
    if (config.debug) {
      console.error(
        `[btp-connectivity] proxy headers: Proxy-Authorization=${token ? "Bearer <jwt>" : "<missing>"}, ` +
        `SAP-Connectivity-SCC-Location_ID=${headers["SAP-Connectivity-SCC-Location_ID"] ?? "<none>"}`,
      );
    }
    return headers;
  };
}
