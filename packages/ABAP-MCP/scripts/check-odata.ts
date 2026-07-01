/** One-off: inspect the ZAUTH_API_V4 binding + try the OData V4 runtime metadata. */
import "../src/config.js";
import { getClient } from "../src/adt-client.js";

async function tryGet(client: any, url: string, accept?: string) {
  try {
    const resp = await client.httpClient.request(url, {
      method: "GET",
      headers: accept ? { Accept: accept } : undefined,
    });
    console.log(`\n=== GET ${url} → ${resp.status ?? "OK"} ===`);
    console.log(String(resp.body).slice(0, 1800));
  } catch (e: any) {
    console.log(`\n=== GET ${url} → ERR: ${e?.message ?? e} ===`);
  }
}

async function main() {
  const client = await getClient();
  console.log("login OK");
  await tryGet(client, "/sap/bc/adt/businessservices/odatav4/ZAUTH_API_V4",
    "application/vnd.sap.adt.businessservices.odatav4.v1+xml");
  // Common OData V4 runtime patterns for a local binding:
  await tryGet(client, "/sap/opu/odata4/sap/zauth_api_v4/srvd_a2x/sap/zauth_srv/0001/$metadata");
  await tryGet(client, "/sap/opu/odata4/sap/zauth_api_v4/0001/$metadata");
}

main().catch((e: Error) => { console.error("FAILED:", e?.message ?? e); process.exit(1); });
