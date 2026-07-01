/**
 * XSUAA OAuth2 token source for the SAP BTP Connectivity Proxy.
 *
 * Uses the standard `client_credentials` grant against the XSUAA tenant
 * provisioned for the connectivity service instance. Tokens are cached in
 * memory and refreshed slightly before expiry. A single in-flight fetch is
 * shared between concurrent callers to avoid stampedes.
 *
 * This module is transport-agnostic: it does **not** know about the proxy
 * itself — only the credentials needed to mint a JWT. The agent layer
 * (`./agent.ts`) injects the resulting JWT into proxy requests.
 */

import { Buffer } from "buffer";
import type { BtpConnectivityCreds } from "./credentials.js";

/** Number of seconds before expiry at which a cached token is treated as stale. */
const REFRESH_SKEW_SECONDS = 60;

/** Minimum delay before a scheduled background refresh. Guards against zero/negative values. */
const MIN_SCHEDULED_REFRESH_MS = 30_000;

interface XsuaaTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export class BtpConnectivityTokenSource {
  private cachedToken?: string;
  private cachedExpiry?: number; // epoch ms
  private inFlight?: Promise<string>;
  private refreshTimer?: NodeJS.Timeout;

  constructor(
    private readonly creds: BtpConnectivityCreds,
    private readonly debug = false,
  ) {}

  /** Return the cached token without triggering a fetch. Used for ambient `Proxy-Authorization` headers. */
  peek(): string | undefined {
    if (this.cachedToken && this.cachedExpiry && Date.now() < this.cachedExpiry) return this.cachedToken;
    return undefined;
  }

  /** Return a valid JWT, fetching one if necessary. Concurrent callers share a single fetch. */
  async get(): Promise<string> {
    const cached = this.peek();
    if (cached) return cached;
    if (this.inFlight) return this.inFlight;

    this.inFlight = this.fetchToken().finally(() => {
      this.inFlight = undefined;
    });
    return this.inFlight;
  }

  /** Cancel any scheduled refresh. Call on shutdown to allow the process to exit cleanly. */
  dispose(): void {
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
      this.refreshTimer = undefined;
    }
  }

  private async fetchToken(): Promise<string> {
    const tokenUrl = `${this.creds.url.replace(/\/$/, "")}/oauth/token`;
    const basic = Buffer.from(`${this.creds.clientid}:${this.creds.clientsecret}`, "utf-8").toString("base64");

    if (this.debug) console.error(`[btp-connectivity] requesting XSUAA token from ${tokenUrl}`);

    const response = await fetch(tokenUrl, {
      method: "POST",
      signal: AbortSignal.timeout(15_000),
      headers: {
        Authorization: `Basic ${basic}`,
        "Content-Type": "application/x-www-form-urlencoded",
        Accept: "application/json",
      },
      body: "grant_type=client_credentials",
    });

    if (!response.ok) {
      const body = await response.text().catch(() => "");
      throw new Error(
        `XSUAA token request failed: HTTP ${response.status} ${response.statusText} — ` +
        `${body.slice(0, 400)}`,
      );
    }

    const payload = (await response.json()) as XsuaaTokenResponse;
    if (!payload.access_token) {
      throw new Error(`XSUAA token response did not include access_token: ${JSON.stringify(payload).slice(0, 400)}`);
    }

    const expiresInSec = typeof payload.expires_in === "number" ? payload.expires_in : 600;
    const ttlMs = Math.max(0, (expiresInSec - REFRESH_SKEW_SECONDS) * 1000);

    this.cachedToken = payload.access_token;
    this.cachedExpiry = Date.now() + ttlMs;
    this.scheduleRefresh(ttlMs);

    if (this.debug) {
      console.error(`[btp-connectivity] obtained XSUAA token (expires in ~${expiresInSec}s)`);
    }
    return payload.access_token;
  }

  private scheduleRefresh(ttlMs: number): void {
    if (this.refreshTimer) clearTimeout(this.refreshTimer);
    const delay = Math.max(MIN_SCHEDULED_REFRESH_MS, ttlMs);
    this.refreshTimer = setTimeout(() => {
      this.get().catch((err) => {
        if (this.debug) console.error(`[btp-connectivity] background token refresh failed: ${(err as Error).message}`);
      });
    }, delay);
    this.refreshTimer.unref?.();
  }
}
