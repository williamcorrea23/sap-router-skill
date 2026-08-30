// SAP-sanctioned API Management channel: OAuth 2.0 client_credentials against the
// `apiportal-apiaccess` service key.
//
// This is the documented programmatic path for the API portal management APIs
// (help.sap.com — "Accessing API Management APIs Programmatically"). The browser
// session channel in cdp_session.mjs stays available as an unsanctioned fallback
// for read/test work when no service key is present.
//
// Secrets are read at call time and never logged or returned to callers.
import fs from "node:fs";
import path from "node:path";

export const RESPONSE_BODY_LIMIT = 25_000;

const tokenCache = new Map();

function readServiceKeyFile() {
  const file = process.env.APIM_SERVICE_KEY_FILE;
  if (!file) {
    return null;
  }
  const resolved = path.resolve(file);
  if (!fs.existsSync(resolved)) {
    throw new Error(`APIM_SERVICE_KEY_FILE not found: ${resolved}`);
  }
  return JSON.parse(fs.readFileSync(resolved, "utf8"));
}

function pick(source, ...keys) {
  for (const key of keys) {
    const value = key.split(".").reduce((acc, part) => (acc && typeof acc === "object" ? acc[part] : undefined), source);
    if (typeof value === "string" && value) {
      return value;
    }
  }
  return "";
}

/** Resolve the service-key credentials from a key file or discrete env vars. */
export function resolveCredentials() {
  let key = {};
  try {
    key = readServiceKeyFile() || {};
  } catch (err) {
    return { configured: false, reason: err.message };
  }
  const apiBase = (process.env.APIM_API_URL || pick(key, "url", "api_url")).replace(/\/$/, "");
  let tokenUrl = process.env.APIM_TOKEN_URL || pick(key, "tokenurl", "tokenUrl", "uaa.tokenurl", "uaa.url");
  const clientId = process.env.APIM_CLIENT_ID || pick(key, "clientId", "client_id", "uaa.clientid");
  const clientSecret = process.env.APIM_CLIENT_SECRET || pick(key, "clientSecret", "client_secret", "uaa.clientsecret");
  if (tokenUrl && !/\/oauth\/token$/.test(tokenUrl)) {
    tokenUrl = tokenUrl.replace(/\/$/, "") + "/oauth/token";
  }
  const missing = [
    !apiBase && "api url (APIM_API_URL or service key 'url')",
    !tokenUrl && "token url (APIM_TOKEN_URL or service key 'tokenurl')",
    !clientId && "client id",
    !clientSecret && "client secret",
  ].filter(Boolean);
  if (missing.length) {
    return { configured: false, reason: `missing ${missing.join(", ")}` };
  }
  return { configured: true, apiBase, tokenUrl, clientId, clientSecret };
}

/** Report configuration state without ever exposing the secret. */
export function channelStatus() {
  const creds = resolveCredentials();
  if (!creds.configured) {
    return { configured: false, reason: creds.reason, source: process.env.APIM_SERVICE_KEY_FILE ? "service-key-file" : "env" };
  }
  return {
    configured: true,
    api_base: creds.apiBase,
    token_url: creds.tokenUrl,
    client_id_suffix: creds.clientId.slice(-6),
    source: process.env.APIM_SERVICE_KEY_FILE ? "service-key-file" : "env",
  };
}

async function accessToken(creds) {
  const cached = tokenCache.get(creds.clientId);
  if (cached && cached.expiresAt > Date.now() + 30_000) {
    return cached.token;
  }
  const basic = Buffer.from(`${creds.clientId}:${creds.clientSecret}`).toString("base64");
  const response = await fetch(creds.tokenUrl, {
    method: "POST",
    headers: {
      Authorization: `Basic ${basic}`,
      "Content-Type": "application/x-www-form-urlencoded",
      Accept: "application/json",
    },
    body: "grant_type=client_credentials",
    signal: AbortSignal.timeout(30_000),
  });
  if (!response.ok) {
    const detail = (await response.text()).slice(0, 500);
    throw new Error(`token request failed with HTTP ${response.status}: ${detail}`);
  }
  const body = await response.json();
  const token = body.access_token;
  if (!token) {
    throw new Error("token response carried no access_token");
  }
  const ttlMs = (Number(body.expires_in) || 3600) * 1000;
  tokenCache.set(creds.clientId, { token, expiresAt: Date.now() + ttlMs });
  return token;
}

/**
 * Call the API portal management API with a bearer token.
 * `apiPath` is relative to the service key's `url` (e.g. "/APIProxies?$format=json").
 */
export async function apiRequest(apiPath, { method = "GET", body = null, headers = {}, binary = false } = {}) {
  const creds = resolveCredentials();
  if (!creds.configured) {
    return { status: "BLOCKED", reason: creds.reason, channel: "oauth" };
  }
  let token;
  try {
    token = await accessToken(creds);
  } catch (err) {
    return { status: "ERROR", stage: "token", reason: err.message, channel: "oauth" };
  }
  const url = creds.apiBase + (apiPath.startsWith("/") ? apiPath : `/${apiPath}`);
  const init = {
    method: method.toUpperCase(),
    headers: { Authorization: `Bearer ${token}`, Accept: "application/json", ...headers },
    signal: AbortSignal.timeout(60_000),
  };
  if (body !== null && body !== undefined && init.method !== "GET" && init.method !== "HEAD") {
    init.body = binary ? body : String(body);
  }
  try {
    const response = await fetch(url, init);
    const text = await response.text();
    const responseHeaders = {};
    response.headers.forEach((value, key) => {
      responseHeaders[key] = value;
    });
    return {
      status: response.ok ? "OK" : "ERROR",
      http_status: response.status,
      url,
      channel: "oauth",
      headers: responseHeaders,
      truncated: text.length > RESPONSE_BODY_LIMIT,
      body: text.slice(0, RESPONSE_BODY_LIMIT),
    };
  } catch (err) {
    return { status: "ERROR", url, channel: "oauth", reason: err.message };
  }
}

/**
 * Strip the `/apiportal/api/1.0/Management.svc` prefix that the session channel
 * needs, since the service key's `url` already points at the management service.
 */
export function toApiPath(sessionPath) {
  return sessionPath.replace(/^\/apiportal\/api\/1\.0\/Management\.svc/, "") || "/";
}
