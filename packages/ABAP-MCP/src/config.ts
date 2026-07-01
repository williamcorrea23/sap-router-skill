/**
 * ABAP MCP Server — runtime configuration.
 *
 * Loads `.env` if present, then derives a single frozen `cfg` object from
 * the process environment. Validation happens here at the boundary so the
 * rest of the codebase can rely on plain typed fields without re-checking.
 */

import { config as dotenvConfig } from "dotenv";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

// Load .env from the project root (parent of dist/) so the server works
// regardless of the current working directory.
dotenvConfig({ path: resolve(dirname(fileURLToPath(import.meta.url)), "..", ".env") });

const SAP_ROUTE_PATTERN = /\/H\/[^/]+\/S\/\d+/i;

/* ------------------------------------------------------------------ *
 * Small env helpers                                                   *
 * ------------------------------------------------------------------ */

const str = (name: string, fallback = ""): string => (process.env[name] ?? fallback).trim();

/**
 * Parse a boolean from a raw env value. Accepts `true` / `1` / `yes` / `on`
 * (any case, surrounding whitespace ignored); everything else is `false`.
 * An unset or empty value falls back to `fallback`. Exported (and pure) so it
 * can be unit-tested without importing the side-effecting `cfg` below.
 */
export const parseBoolean = (raw: string | undefined, fallback = false): boolean => {
  if (raw === undefined) return fallback;
  const v = raw.trim().toLowerCase();
  if (v === "") return fallback;
  return v === "true" || v === "1" || v === "yes" || v === "on";
};

const bool = (name: string, fallback = false): boolean => parseBoolean(process.env[name], fallback);
const list = (name: string, fallback: string): string[] =>
  str(name, fallback)
    .split(",")
    .map((s) => s.trim().toUpperCase())
    .filter(Boolean);
const int = (name: string, fallback: number): number => {
  const raw = process.env[name];
  if (raw === undefined || raw === "") return fallback;
  const n = parseInt(raw, 10);
  return Number.isFinite(n) ? n : fallback;
};

/* ------------------------------------------------------------------ *
 * Cross-field validations that should fail loudly on startup          *
 * ------------------------------------------------------------------ */

const rawUrl = str("SAP_URL");

if (SAP_ROUTE_PATTERN.test(rawUrl)) {
  console.error(
    "ERROR: SAP_URL contains an SAProuter route (e.g. '/H/host/S/3299'). " +
    "SAProuter speaks SAP NI binary protocol (RFC/GUI) and cannot tunnel HTTPS for ADT. " +
    "Use the HTTPS base URL of the Web Dispatcher (e.g. https://yourhost.example.com) " +
    "or set SAP_PROXY_URL to a CONNECT-capable HTTP(S) proxy.",
  );
  process.exit(1);
}

const proxyUrl =
  str("SAP_PROXY_URL") ||
  str("HTTPS_PROXY") ||
  str("https_proxy") ||
  str("HTTP_PROXY") ||
  str("http_proxy");

/**
 * Identifier that distinguishes this server instance from other instances
 * pointing at different SAP systems. Used to namespace `serverInfo.name`
 * so MCP clients like Claude Desktop don't collapse multiple servers into
 * one connector entry (they dedupe by `serverInfo.name`).
 *
 * Resolution order:
 *   1. SAP_INSTANCE_ID — set explicitly by the operator / wrapper script.
 *   2. First DNS label of SAP_URL — works out of the box for distinct hosts.
 *   3. "default" — last-resort fallback for single-server installs.
 */
const instanceId = str("SAP_INSTANCE_ID") || deriveInstanceIdFromUrl(rawUrl) || "default";

function deriveInstanceIdFromUrl(raw: string): string {
  try {
    const host = new URL(raw).hostname;
    const firstLabel = host.split(".")[0] ?? "";
    return slug(firstLabel);
  } catch {
    return "";
  }
}

/** Normalize to a safe MCP identifier: lowercase, alnum + dashes. */
function slug(s: string): string {
  return s
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

/* ------------------------------------------------------------------ *
 * The frozen, typed configuration surface                             *
 * ------------------------------------------------------------------ */

export const cfg = Object.freeze({
  // ── SAP backend ────────────────────────────────────────────────
  url: rawUrl,
  user: str("SAP_USER"),
  password: str("SAP_PASSWORD"),
  client: str("SAP_CLIENT", "100"),
  language: str("SAP_LANGUAGE", "EN"),
  allowUnauthorized: bool("SAP_ALLOW_UNAUTHORIZED"),

  // ── Safety / write controls ───────────────────────────────────
  allowWrite: bool("ALLOW_WRITE"),
  allowDelete: bool("ALLOW_DELETE"),
  allowExecute: bool("ALLOW_EXECUTE"),
  blockedPackages: list("BLOCKED_PACKAGES", "SAP,SHD"),
  defaultTransport: str("DEFAULT_TRANSPORT"),
  syntaxCheckBeforeActivate: bool("SYNTAX_CHECK_BEFORE_ACTIVATE", true),

  // ── Operational ───────────────────────────────────────────────
  instanceId,
  maxDumps: int("MAX_DUMPS", 20),
  deferTools: bool("DEFER_TOOLS", true),
  sapAbapVersion: str("SAP_ABAP_VERSION", "latest"),
  tavilyApiKey: str("TAVILY_API_KEY"),
  // Disable TLS certificate verification ONLY for outbound web calls
  // (Tavily fetch_url/search_sap_web) — for corporate proxies that intercept
  // TLS with self-signed certs. Deliberately separate from
  // SAP_ALLOW_UNAUTHORIZED, which stays scoped to the ADT connection.
  webAllowUnauthorized: bool("WEB_ALLOW_UNAUTHORIZED"),

  // ── Governance ────────────────────────────────────────────────
  // Role layers on top of the ALLOW_* flags: it can only *further* restrict,
  // never grant. Default "admin" preserves the legacy behaviour where the
  // ALLOW_* flags are the sole gate (no surprise for existing single-user
  // setups). Set SAP_ROLE=viewer/developer to tighten in shared deployments.
  role: (() => {
    const r = str("SAP_ROLE", "admin").toLowerCase();
    return (["viewer", "developer", "admin"] as const).includes(r as never) ? r : "admin";
  })() as "viewer" | "developer" | "admin",
  auditLogFile: str("AUDIT_LOG_FILE"),

  // ── Network routing — exactly one of these will be active ─────
  proxyUrl,
  sapRouter: str("SAP_ROUTER"),
  sapRouterPassword: str("SAP_ROUTER_PASSWORD"),
  sapRouterDebug: bool("SAP_ROUTER_DEBUG"),
  btpConnectivityProxy: str("SAP_BTP_CONNECTIVITY_PROXY"),
  btpConnectivityLocationId: str("SAP_BTP_CONNECTIVITY_LOCATION_ID"),
  btpConnectivityDebug: bool("SAP_BTP_CONNECTIVITY_DEBUG"),
} as const);

export type Config = typeof cfg;

/* ------------------------------------------------------------------ *
 * Final required-field check                                          *
 * ------------------------------------------------------------------ */

const missing = (["url", "user", "password"] as const).filter((k) => !cfg[k]);
if (missing.length > 0) {
  const envNames = { url: "SAP_URL", user: "SAP_USER", password: "SAP_PASSWORD" } as const;
  console.error(
    `ERROR: required environment variable(s) missing: ${missing.map((k) => envNames[k]).join(", ")}. ` +
    `Set them in your .env file or the MCP client config.`,
  );
  process.exit(1);
}
