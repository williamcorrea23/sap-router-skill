/** One-off: discover valid transport layers (and the default) on the system. */
import "../src/config.js";
import { getClient } from "../src/adt-client.js";

async function tryGet(client: any, url: string, accept?: string) {
  try {
    const resp = await client.httpClient.request(url, {
      method: "GET",
      headers: accept ? { Accept: accept } : undefined,
    });
    console.log(`\n=== GET ${url} → OK ===`);
    console.log(String(resp.body).slice(0, 2000));
  } catch (e: any) {
    console.log(`\n=== GET ${url} → ERR: ${e?.message ?? e} ===`);
  }
}

async function main() {
  const client = await getClient();
  console.log("✓ login OK");
  await tryGet(client, "/sap/bc/adt/packages/valuehelps/transportlayers");
  await tryGet(client, "/sap/bc/adt/cts/transportlayers");
  await tryGet(client, "/sap/bc/adt/cts/transportrequests/searchconfiguration/configurations");
}

main().catch((e: Error) => { console.error("FAILED:", e?.message ?? e); process.exit(1); });
