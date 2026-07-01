/**
 * Resolve a BTP destination definition through the destination service.
 *
 * Mainly useful for discovering non-obvious values like
 * `CloudConnectorLocationId` (needed when a subaccount has multiple Cloud
 * Connectors) and the virtual host/port that the Cloud Connector exposes.
 *
 * Usage (from the repo root, with `cf ssh … -L 20003:…` running):
 *
 *   SAP_BTP_CF_HOME=/abs/path/to/<project> \
 *   SAP_BTP_DESTINATION_CDS_BIND_FILE=/abs/path/.cdsrc-private.json \
 *   SAP_BTP_DESTINATION_CDS_BIND_NAME=destinations \
 *   npx tsx scripts/btp-destination-inspect.ts EAM_MDC
 *
 *   # …or list every destination configured for the subaccount:
 *   npx tsx scripts/btp-destination-inspect.ts --list
 *
 * Alternatively, point straight at a pre-fetched service-key JSON:
 *
 *   SAP_BTP_DESTINATION_CREDS_FILE=/path/to/destination-key.json \
 *   npx tsx scripts/btp-destination-inspect.ts EAM_MDC
 */

import fs from "fs";
import path from "path";
import { execFileSync } from "child_process";

interface DestinationCreds {
  clientid: string;
  clientsecret: string;
  /** XSUAA URL, e.g. https://<subaccount>.authentication.<region>.hana.ondemand.com */
  url: string;
  /** Destination service REST base URI. */
  uri: string;
}

interface CdsBinding {
  instance: string;
  key: string;
}

interface Destination {
  Name?: string;
  Type?: string;
  ProxyType?: string;
  Authentication?: string;
  URL?: string;
  CloudConnectorLocationId?: string;
}

async function main(): Promise<void> {
  const name = process.argv[2];
  const creds = loadCreds();
  const token = await fetchToken(creds);
  console.log(`destination service: ${creds.uri}\n`);

  if (!name || name === "--list") {
    await listDestinations(creds, token);
    return;
  }
  await showDestination(creds, token, name);
}

/* ------------------------------------------------------------------ *
 * Credential resolution                                               *
 * ------------------------------------------------------------------ */

function loadCreds(): DestinationCreds {
  const file = process.env.SAP_BTP_DESTINATION_CREDS_FILE;
  if (file) {
    const creds = unwrapCreds(readJson(file));
    if (creds) return creds;
    throw new Error(`${file} is not a valid destination service key.`);
  }
  const cdsFile = process.env.SAP_BTP_DESTINATION_CDS_BIND_FILE;
  const cdsName = process.env.SAP_BTP_DESTINATION_CDS_BIND_NAME ?? "destinations";
  if (!cdsFile) {
    throw new Error("Set SAP_BTP_DESTINATION_CDS_BIND_FILE or SAP_BTP_DESTINATION_CREDS_FILE.");
  }
  const binding = findBinding(readJson(cdsFile), cdsName);
  if (!binding) throw new Error(`No binding '${cdsName}' in ${cdsFile}.`);

  const env: NodeJS.ProcessEnv = { ...process.env };
  const cfHome = process.env.SAP_BTP_CF_HOME ?? process.env.CF_HOME;
  if (cfHome) env.CF_HOME = path.resolve(cfHome);

  const stdout = execFileSync("cf", ["service-key", binding.instance, binding.key], {
    encoding: "utf-8",
    timeout: 30_000,
    env,
  });
  const firstBrace = stdout.indexOf("{");
  if (firstBrace < 0) throw new Error(`cf service-key produced no JSON: ${stdout.slice(0, 200)}`);
  const creds = unwrapCreds(JSON.parse(stdout.slice(firstBrace)));
  if (!creds) throw new Error(`Service key for ${binding.instance}/${binding.key} has unexpected shape.`);
  return creds;
}

function readJson(p: string): unknown {
  const abs = path.isAbsolute(p) ? p : path.resolve(process.cwd(), p);
  return JSON.parse(fs.readFileSync(abs, "utf-8")) as unknown;
}

function unwrapCreds(raw: unknown): DestinationCreds | undefined {
  if (!raw || typeof raw !== "object") return undefined;
  const obj = raw as Record<string, unknown>;
  const url = obj.url as string | undefined ?? (obj.authentication as Record<string, string> | undefined)?.url;
  if (typeof obj.clientid === "string" && typeof obj.clientsecret === "string" && typeof obj.uri === "string" && typeof url === "string") {
    return { clientid: obj.clientid, clientsecret: obj.clientsecret, url, uri: obj.uri };
  }
  if (obj.credentials) return unwrapCreds(obj.credentials);
  return undefined;
}

interface CdsSlot {
  binding?: CdsBinding;
}
type CdsRequires = Record<string, CdsSlot | Record<string, CdsSlot | undefined> | undefined>;

function findBinding(raw: unknown, name: string): CdsBinding | undefined {
  if (!raw || typeof raw !== "object") return undefined;
  const requires = (raw as { requires?: CdsRequires }).requires;
  if (!requires) return undefined;
  const candidates: Array<CdsSlot | undefined> = [requires[name] as CdsSlot | undefined];
  for (const k of Object.keys(requires)) {
    if (!/^\[.+\]$/.test(k)) continue;
    const group = requires[k] as Record<string, CdsSlot | undefined> | undefined;
    candidates.push(group?.[name]);
  }
  for (const c of candidates) {
    if (c?.binding?.instance && c.binding.key) return c.binding;
  }
  return undefined;
}

/* ------------------------------------------------------------------ *
 * Destination service calls                                            *
 * ------------------------------------------------------------------ */

async function fetchToken(creds: DestinationCreds): Promise<string> {
  const res = await fetch(`${creds.url.replace(/\/+$/, "")}/oauth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "client_credentials",
      client_id: creds.clientid,
      client_secret: creds.clientsecret,
    }).toString(),
  });
  if (!res.ok) throw new Error(`token fetch ${res.status}: ${await res.text().catch(() => "")}`);
  const payload = (await res.json()) as { access_token: string };
  return payload.access_token;
}

async function listDestinations(creds: DestinationCreds, token: string): Promise<void> {
  const r = await fetch(
    `${creds.uri.replace(/\/+$/, "")}/destination-configuration/v1/subaccountDestinations`,
    { headers: { Authorization: `Bearer ${token}` } },
  );
  if (!r.ok) {
    console.error(`HTTP ${r.status}: ${await r.text()}`);
    process.exit(1);
  }
  const list = (await r.json()) as Destination[];
  const widths = { name: 26, type: 8, proxy: 10, loc: 14 } as const;
  const head = ["NAME".padEnd(widths.name), "TYPE".padEnd(widths.type), "PROXY".padEnd(widths.proxy), "LOC_ID".padEnd(widths.loc), "URL"].join(" ");
  console.log(head);
  console.log("-".repeat(head.length));
  for (const d of list) {
    console.log([
      (d.Name ?? "").padEnd(widths.name),
      (d.Type ?? "").padEnd(widths.type),
      (d.ProxyType ?? "").padEnd(widths.proxy),
      (d.CloudConnectorLocationId ?? "").padEnd(widths.loc),
      d.URL ?? "",
    ].join(" "));
  }
  const ids = new Set(list.map((d) => d.CloudConnectorLocationId).filter(Boolean));
  console.log(`\nDistinct CloudConnectorLocationId values: ${[...ids].join(", ") || "(none)"}`);
}

async function showDestination(creds: DestinationCreds, token: string, name: string): Promise<void> {
  const res = await fetch(
    `${creds.uri.replace(/\/+$/, "")}/destination-configuration/v1/destinations/${encodeURIComponent(name)}`,
    { headers: { Authorization: `Bearer ${token}` } },
  );
  if (!res.ok) {
    console.error(`HTTP ${res.status}: ${await res.text()}`);
    process.exit(1);
  }
  const payload = (await res.json()) as { destinationConfiguration?: Destination } & Destination;
  console.log(JSON.stringify(payload, null, 2));
  const dest = payload.destinationConfiguration ?? payload;
  console.log("\n--- summary ---");
  console.log(`URL                       : ${dest.URL ?? "(none)"}`);
  console.log(`ProxyType                 : ${dest.ProxyType ?? "(none)"}`);
  console.log(`Authentication            : ${dest.Authentication ?? "(none)"}`);
  console.log(`CloudConnectorLocationId  : ${dest.CloudConnectorLocationId ?? "(default / empty)"}`);
}

main().catch((e: Error) => {
  console.error("FAILED:", e.message ?? e);
  process.exit(1);
});
