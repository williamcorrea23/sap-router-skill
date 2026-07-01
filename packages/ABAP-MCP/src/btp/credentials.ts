/**
 * SAP BTP Connectivity service credential resolution.
 *
 * Credentials needed to authenticate against the Connectivity Proxy:
 *   - clientid + clientsecret + url (XSUAA base URL)
 *
 * Resolved from one of three sources, in priority order:
 *
 *   1. SAP_BTP_CONNECTIVITY_CREDS_FILE
 *      Path to a service-key JSON file (as produced by
 *      `cf service-key <inst> <key> > creds.json`).
 *
 *   2. SAP_BTP_CONNECTIVITY_CDS_BIND_FILE + SAP_BTP_CONNECTIVITY_CDS_BIND_NAME
 *      A CAP `.cdsrc-private.json` plus the bound service name (e.g.
 *      `connectivity`). The file only carries a CF instance/key reference;
 *      live credentials are materialized via `cf service-key`.
 *
 *   3. SAP_BTP_CONNECTIVITY_CLIENT_ID / _CLIENT_SECRET / _TOKEN_URL
 *      Direct environment variables.
 *
 * The `cf` shell-out honors `SAP_BTP_CF_HOME` (or the standard `CF_HOME`) so
 * that the MCP can use a per-project CF session distinct from the user's
 * global one — useful when several projects target different CF orgs/spaces.
 */

import fs from "fs";
import path from "path";
import { execFileSync } from "child_process";

export interface BtpConnectivityCreds {
  readonly clientid: string;
  readonly clientsecret: string;
  /** XSUAA base URL, e.g. https://<subaccount>.authentication.<region>.hana.ondemand.com */
  readonly url: string;
}

/**
 * Resolve credentials from the first configured source. Returns `undefined`
 * when no source is configured; throws when a source is configured but
 * yields no usable credentials (so misconfiguration fails loudly).
 */
export function loadBtpConnectivityCreds(): BtpConnectivityCreds | undefined {
  const credsFile = env("SAP_BTP_CONNECTIVITY_CREDS_FILE");
  if (credsFile) return loadFromKeyFile(credsFile);

  const cdsBindFile = env("SAP_BTP_CONNECTIVITY_CDS_BIND_FILE");
  const cdsBindName = env("SAP_BTP_CONNECTIVITY_CDS_BIND_NAME");
  if (cdsBindFile && cdsBindName) return loadFromCdsBinding(cdsBindFile, cdsBindName);

  return loadFromEnvVars();
}

/* ------------------------------------------------------------------ */
/* Source 1: pre-fetched service-key JSON file                         */
/* ------------------------------------------------------------------ */

function loadFromKeyFile(filePath: string): BtpConnectivityCreds {
  const raw = readJsonFile(filePath);
  const creds = unwrapCreds(raw);
  if (creds) return creds;
  throw new Error(
    `SAP_BTP_CONNECTIVITY_CREDS_FILE=${filePath} is not a valid connectivity service key. ` +
    `Expected an object with { clientid, clientsecret, url } at the top level or under .credentials.`,
  );
}

/* ------------------------------------------------------------------ */
/* Source 2: CAP .cdsrc-private.json binding reference + cf shell-out  */
/* ------------------------------------------------------------------ */

function loadFromCdsBinding(filePath: string, bindingName: string): BtpConnectivityCreds {
  const raw = readJsonFile(filePath);
  const binding = findCdsBinding(raw, bindingName);
  if (!binding) {
    throw new Error(
      `No CAP binding named '${bindingName}' in ${filePath}. ` +
      `Run 'cds bind --to <cf-service-instance> --for hybrid' for that service first.`,
    );
  }
  if (!binding.instance || !binding.key) {
    throw new Error(
      `CAP binding '${bindingName}' in ${filePath} is missing { instance, key }. ` +
      `Expected a CF service-key binding.`,
    );
  }
  const cfHome = env("SAP_BTP_CF_HOME") || env("CF_HOME") || undefined;
  const payload = fetchCfServiceKey(binding.instance, binding.key, cfHome);
  const creds = unwrapCreds(payload);
  if (creds) return creds;
  throw new Error(
    `cf service-key ${binding.instance} ${binding.key} returned a payload without ` +
    `{ clientid, clientsecret, url }. Is this really a connectivity (XSUAA-backed) service instance?`,
  );
}

/* ------------------------------------------------------------------ */
/* Source 3: explicit environment variables                            */
/* ------------------------------------------------------------------ */

function loadFromEnvVars(): BtpConnectivityCreds | undefined {
  const clientid = env("SAP_BTP_CONNECTIVITY_CLIENT_ID");
  const clientsecret = env("SAP_BTP_CONNECTIVITY_CLIENT_SECRET");
  const url = env("SAP_BTP_CONNECTIVITY_TOKEN_URL") || env("SAP_BTP_CONNECTIVITY_URL");
  if (clientid && clientsecret && url) return { clientid, clientsecret, url };
  return undefined;
}

/* ------------------------------------------------------------------ */
/* Helpers                                                             */
/* ------------------------------------------------------------------ */

function env(name: string): string {
  return (process.env[name] ?? "").trim();
}

function readJsonFile(filePath: string): unknown {
  const abs = path.isAbsolute(filePath) ? filePath : path.resolve(process.cwd(), filePath);
  if (!fs.existsSync(abs)) throw new Error(`File not found: ${abs}`);
  return JSON.parse(fs.readFileSync(abs, "utf-8")) as unknown;
}

/** Walk likely shapes (raw service-key, wrapped under `.credentials`, single-element VCAP array). */
function unwrapCreds(raw: unknown): BtpConnectivityCreds | undefined {
  if (!raw || typeof raw !== "object") return undefined;
  const obj = raw as Record<string, unknown>;

  if (typeof obj.clientid === "string" && typeof obj.clientsecret === "string" && typeof obj.url === "string") {
    return { clientid: obj.clientid, clientsecret: obj.clientsecret, url: obj.url };
  }
  if (obj.credentials) return unwrapCreds(obj.credentials);
  if (Array.isArray(raw) && raw.length > 0) {
    const first = raw[0] as Record<string, unknown> | undefined;
    return unwrapCreds(first?.credentials ?? first);
  }
  return undefined;
}

interface CdsBindingRef {
  instance?: string;
  key?: string;
}

/** Single-service slot inside `requires`, as written by `cds bind`. */
interface CdsServiceSlot {
  binding?: CdsBindingRef;
}
/** Profile group inside `requires` (e.g. the `[hybrid]` block). */
type CdsProfileGroup = Record<string, CdsServiceSlot | undefined>;
/** Outer `requires` map: either a direct slot or a profile group keyed by `[name]`. */
type CdsRequires = Record<string, CdsServiceSlot | CdsProfileGroup | undefined>;

/** Tolerates the `requires.[hybrid].<name>` profile wrapping that `cds bind --for hybrid` produces. */
function findCdsBinding(raw: unknown, name: string): CdsBindingRef | undefined {
  if (!raw || typeof raw !== "object") return undefined;
  const requires = (raw as { requires?: CdsRequires }).requires;
  if (!requires) return undefined;

  const direct = requires[name] as CdsServiceSlot | undefined;
  if (direct?.binding?.instance) return direct.binding;

  for (const key of Object.keys(requires)) {
    if (!/^\[.+\]$/.test(key)) continue;
    const group = requires[key] as CdsProfileGroup | undefined;
    const inner = group?.[name];
    if (inner?.binding?.instance) return inner.binding;
  }
  return undefined;
}

function fetchCfServiceKey(instance: string, key: string, cfHome?: string): unknown {
  const childEnv: NodeJS.ProcessEnv = { ...process.env };
  if (cfHome) {
    const resolved = path.isAbsolute(cfHome) ? cfHome : path.resolve(process.cwd(), cfHome);
    if (!fs.existsSync(resolved)) {
      throw new Error(
        `SAP_BTP_CF_HOME / CF_HOME=${cfHome} (resolved to ${resolved}) does not exist. ` +
        `Create the folder and run 'CF_HOME=${resolved} cf login ...' once.`,
      );
    }
    childEnv.CF_HOME = resolved;
  }

  let stdout: string;
  try {
    stdout = execFileSync("cf", ["service-key", instance, key], {
      encoding: "utf-8",
      stdio: ["ignore", "pipe", "pipe"],
      timeout: 30_000,
      env: childEnv,
    });
  } catch (err) {
    const combined = collectCfOutput(err);
    throw new Error(
      `cf service-key ${instance} ${key} failed${cfHome ? ` (CF_HOME=${cfHome})` : ""}: ` +
      `${diagnoseCfFailure(combined, instance, key, cfHome)}\n` +
      `--- cf output ---\n${combined.slice(0, 800) || "(no output)"}`,
    );
  }

  const firstBrace = stdout.indexOf("{");
  if (firstBrace < 0) {
    throw new Error(
      `cf service-key ${instance} ${key} returned no JSON. ` +
      `The service key most likely does not exist; create it with ` +
      `'cf create-service-key ${instance} ${key}'.\nRaw output: ${stdout.slice(0, 400)}`,
    );
  }
  return JSON.parse(stdout.slice(firstBrace));
}

function collectCfOutput(err: unknown): string {
  const e = err as { stdout?: { toString?: () => string }; stderr?: { toString?: () => string }; message?: string };
  const out = e?.stdout?.toString?.() ?? "";
  const errOut = e?.stderr?.toString?.() ?? "";
  return `${out}\n${errOut}\n${e?.message ?? ""}`.trim();
}

/** Map common `cf` failure modes to actionable single-line hints. */
function diagnoseCfFailure(output: string, instance: string, key: string, cfHome?: string): string {
  const where = cfHome ?? "$HOME";
  if (/spawn cf ENOENT/i.test(output)) {
    return `cf CLI not found on PATH. Install with 'brew install cloudfoundry/tap/cf-cli@8' (macOS).`;
  }
  if (/not logged in/i.test(output) || /please log in/i.test(output)) {
    return `cf is not authenticated. Run 'CF_HOME=${where} cf login -a https://api.cf.<region>.hana.ondemand.com --sso' first.`;
  }
  if (/token (?:has )?expired/i.test(output) || /401/.test(output) || /unauthorized/i.test(output)) {
    return `cf session expired. Re-run 'CF_HOME=${where} cf login --sso' (or 'cf auth' to refresh).`;
  }
  if (/no org and space targeted/i.test(output) || /no space targeted/i.test(output) || /no api endpoint set/i.test(output)) {
    return `cf has no org/space targeted in this CF_HOME. Run 'CF_HOME=${where} cf target -o <org> -s <space>'.`;
  }
  if (/service instance .* (?:not found|doesn't exist)/i.test(output)) {
    return `service instance '${instance}' not found in the targeted org/space.`;
  }
  if (/service key .* (?:not found|doesn't exist)/i.test(output)) {
    return `service key '${key}' on '${instance}' not found. Create it with 'cf create-service-key ${instance} ${key}'.`;
  }
  return `unrecognized cf failure — see raw output below.`;
}
