#!/usr/bin/env node

import { SAPBTPMCPServer } from './server.js';

async function main() {
  const docsPath = process.env.SAP_BTP_DOCS_PATH;

  const server = new SAPBTPMCPServer(docsPath);

  try {
    await server.initialize();
    await server.run();
  } catch (error) {
    console.error('Fatal error:', error);
    process.exit(1);
  }
}

main();
