/**
 * End-to-end smoke test of `getClient()` — exercises the exact code path the
 * MCP runs (including the `axios` http-agent monkey-patch) against the real
 * BTP Connectivity Proxy + on-prem ADT system.
 *
 * Usage (with `.env` configured as for the MCP itself):
 *
 *   npx tsx scripts/adt-client-smoke.ts
 */

import "../src/config.js"; // side-effecting: loads dotenv + validates required env
import { getClient } from "../src/adt-client.js";

async function main(): Promise<void> {
  const client = await getClient();
  console.log("✓ login OK; running ADT search…");
  const refs = await client.searchObject("CL_ABAP*", "", 3);
  console.log(JSON.stringify(refs, null, 2));
}

main().catch((e: Error) => {
  console.error("FAILED:", e.message ?? e);
  process.exit(1);
});
