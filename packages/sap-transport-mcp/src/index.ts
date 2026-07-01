#!/usr/bin/env node
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { createServer } from "./server.js";

// Never use console.log — stdout is the MCP protocol channel.
// Use console.error for all diagnostic output (goes to stderr).

async function main(): Promise<void> {
  const server = createServer();
  const transport = new StdioServerTransport();

  await server.connect(transport);

  console.error("[sap-transport-mcp] server running on stdio");
}

main().catch((error) => {
  console.error("[sap-transport-mcp] fatal error:", error);
  process.exit(1);
});
