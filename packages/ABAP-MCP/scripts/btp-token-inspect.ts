/**
 * Decode the XSUAA JWT the connectivity service issues to us and print the
 * most relevant claims. Useful when the connectivity proxy answers HTTP 503
 * "no SCC matching the requested tunnel" — the most common root cause is
 * the wrong subaccount / audience in the access token.
 *
 * Usage:
 *
 *   SAP_BTP_CONNECTIVITY_CDS_BIND_FILE=… SAP_BTP_CONNECTIVITY_CDS_BIND_NAME=connectivity \
 *   npx tsx scripts/btp-token-inspect.ts
 */

import { loadBtpConnectivityCreds, BtpConnectivityTokenSource } from "../src/btp/index.js";

interface JwtClaims {
  iss?: string;
  zid?: string;
  client_id?: string;
  cid?: string;
  aud?: string[];
  grant_type?: string;
  scope?: string[];
  ext_attr?: Record<string, unknown>;
}

async function main(): Promise<void> {
  const creds = loadBtpConnectivityCreds();
  if (!creds) {
    console.error("No connectivity credentials available.");
    process.exit(1);
  }
  const tokenSource = new BtpConnectivityTokenSource(creds, true);
  const token = await tokenSource.get();

  const [, payload] = token.split(".");
  const claims = JSON.parse(Buffer.from(payload, "base64").toString("utf-8")) as JwtClaims;
  console.log(JSON.stringify(claims, null, 2));

  console.log("\n--- key claims ---");
  console.log(`iss              : ${claims.iss}`);
  console.log(`zid (subaccount) : ${claims.zid}`);
  console.log(`client_id        : ${claims.client_id}`);
  console.log(`cid              : ${claims.cid}`);
  console.log(`aud              : ${(claims.aud ?? []).join(", ")}`);
  console.log(`grant_type       : ${claims.grant_type}`);
  console.log(`scope            : ${(claims.scope ?? []).slice(0, 5).join(", ")}…`);
  console.log(`ext_attr         : ${JSON.stringify(claims.ext_attr ?? {})}`);

  tokenSource.dispose();
}

main().catch((e: Error) => {
  console.error(e.message ?? e);
  process.exit(1);
});
