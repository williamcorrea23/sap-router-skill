/**
 * Smoke test for the new `create_package` tool — exercises handleCreatePackage
 * against the live ADT system (same code path the MCP runs) and creates the
 * ZAUTH package for the SUIM→RAP OData V4 app.
 *
 * Usage (with `.env` configured as for the MCP itself):
 *
 *   npx tsx scripts/create-package-smoke.ts [HOME|LOCAL] [transportLayer] [transportRequest]
 */

import "../src/config.js"; // side-effecting: loads dotenv + validates required env
import { getClient } from "../src/adt-client.js";
import { handleCreatePackage } from "../src/tools/handlers/create.js";

async function main(): Promise<void> {
  const swComp = (process.argv[2] || "HOME").toUpperCase();
  const transportLayer = process.argv[3];
  const transport = process.argv[4];

  const client = await getClient();
  console.log(`✓ login OK; creating package ZAUTH (softwareComponent=${swComp}${transportLayer ? `, layer=${transportLayer}` : ""}${transport ? `, transport=${transport}` : ""})…`);

  const args: Record<string, unknown> = {
    name: "ZAUTH",
    description: "SUIM RAP - read-only OData V4",
    softwareComponent: swComp,
  };
  if (transportLayer) args.transportLayer = transportLayer;
  if (transport) args.transport = transport;

  const res = await handleCreatePackage(client, args);
  console.log(res.isError ? "RESULT (error):" : "RESULT:");
  console.log(res.content[0]?.text);
  if (res.isError) process.exit(2);
}

main().catch((e: Error) => {
  console.error("FAILED:", e?.message ?? e);
  process.exit(1);
});
