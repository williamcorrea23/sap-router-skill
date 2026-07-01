/**
 * End-to-end smoke test for the BTP Connectivity Proxy mode.
 *
 *   1. Resolve XSUAA credentials via the configured source.
 *   2. Fetch a JWT.
 *   3. Open a proxied request to `SAP_URL` + a probe path (default
 *      `/sap/bc/adt/discovery`) and print the response.
 *
 * Usage (from the repo root):
 *
 *   SAP_URL=http://mdadneap1.merckgroup.com:44300 \
 *   SAP_BTP_CONNECTIVITY_PROXY=http://localhost:20003 \
 *   SAP_BTP_CONNECTIVITY_CDS_BIND_FILE=/abs/.cdsrc-private.json \
 *   SAP_BTP_CONNECTIVITY_CDS_BIND_NAME=connectivity \
 *   SAP_BTP_CONNECTIVITY_LOCATION_ID=<loc>            # optional
 *   SAP_USER=… SAP_PASSWORD=… SAP_CLIENT=100          # optional, to test basic-auth
 *   npx tsx scripts/btp-connectivity-smoke.ts [/sap/bc/adt/discovery]
 */

import http from "http";
import https from "https";
import { URL } from "url";
import {
  loadBtpConnectivityCreds,
  BtpConnectivityTokenSource,
  createBtpConnectivityAgentBundle,
} from "../src/btp/index.js";

interface HttpResult {
  status: number;
  body: string;
}

async function main(): Promise<void> {
  const sapUrl = process.env.SAP_URL;
  const proxyUrl = process.env.SAP_BTP_CONNECTIVITY_PROXY;
  if (!sapUrl || !proxyUrl) {
    fail("set SAP_URL and SAP_BTP_CONNECTIVITY_PROXY.");
  }
  const probePath = process.argv[2] ?? "/sap/bc/adt/discovery";

  console.log("Step 1: loading connectivity credentials…");
  const creds = loadBtpConnectivityCreds();
  if (!creds) fail("no credentials available — set one of the SAP_BTP_CONNECTIVITY_* env groups.");
  console.log(`  ✓ clientid=${creds.clientid.slice(0, 8)}…  url=${creds.url}`);

  console.log("Step 2: fetching XSUAA token (client_credentials)…");
  const tokenSource = new BtpConnectivityTokenSource(creds, true);
  const token = await tokenSource.get().catch((e: Error) => fail(`token fetch failed: ${e.message}`));
  console.log(`  ✓ got token (length=${token.length}).`);

  console.log(`Step 3: probing ${sapUrl}${probePath} via ${proxyUrl}…`);
  const bundle = createBtpConnectivityAgentBundle(
    {
      proxyUrl,
      creds,
      locationId: process.env.SAP_BTP_CONNECTIVITY_LOCATION_ID || undefined,
      allowUnauthorized: process.env.SAP_ALLOW_UNAUTHORIZED === "true",
      debug: true,
    },
    sapUrl,
  );
  await bundle.tokenSource.get();
  console.log(`  scheme=${bundle.scheme} (chosen from SAP_URL)`);

  const result = await doRequest(new URL(probePath, sapUrl), buildHeaders(), bundle.agent, bundle.scheme);
  console.log(`  ✓ HTTP ${result.status}`);
  console.log(`  body[0..400]: ${result.body.slice(0, 400)}`);

  if (result.status === 405 && /HTTPS proxying is not supported/i.test(result.body)) {
    console.error(
      "\nNOTE: The connectivity proxy on this port only accepts plain HTTP forward-proxying. " +
      "Switch SAP_URL to use http:// (not https://) — the Cloud Connector handles the back-end TLS.",
    );
  }

  bundle.tokenSource.dispose();
}

function buildHeaders(): Record<string, string> {
  const headers: Record<string, string> = { Accept: "application/atom+xml,application/xml,*/*" };
  if (process.env.SAP_USER && process.env.SAP_PASSWORD) {
    const b64 = Buffer.from(`${process.env.SAP_USER}:${process.env.SAP_PASSWORD}`).toString("base64");
    headers.Authorization = `Basic ${b64}`;
  }
  if (process.env.SAP_CLIENT) headers["sap-client"] = process.env.SAP_CLIENT;
  return headers;
}

function doRequest(
  target: URL,
  headers: Record<string, string>,
  agent: http.Agent | https.Agent,
  scheme: "http" | "https",
): Promise<HttpResult> {
  return new Promise((resolve, reject) => {
    const transport = scheme === "https" ? https : http;
    const req = transport.request(
      {
        method: "GET",
        host: target.hostname,
        port: target.port || (scheme === "https" ? 443 : 80),
        path: target.pathname + target.search,
        headers,
        agent,
        rejectUnauthorized: false,
      },
      (res) => {
        let body = "";
        res.on("data", (c: Buffer) => (body += c.toString()));
        res.on("end", () => resolve({ status: res.statusCode ?? 0, body }));
      },
    );
    req.on("error", reject);
    req.end();
  });
}

function fail(message: string): never {
  console.error(`ERROR: ${message}`);
  process.exit(1);
}

main().catch((e: Error) => {
  console.error("FAILED:", e.message ?? e);
  process.exit(1);
});
