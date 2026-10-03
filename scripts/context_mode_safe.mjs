// Reviewed embedded entrypoint: bypass upstream self-repair, startup fetches and hooks.
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
process.env.CONTEXT_MODE_EMBEDDED_PLUGIN_TOOLS = '1';
process.env.CONTEXT_MODE_PLATFORM = 'codex';
process.env.CONTEXT_MODE_PROJECT_DIR = root;
process.env.CONTEXT_MODE_DIR = path.join(root, '.sap-router', 'context-mode');
const { server } = await import('../bundled/tools/context-mode/server.bundle.mjs');
const { StdioServerTransport } = await import('../bundled/tools/context-mode/node_modules/@modelcontextprotocol/sdk/dist/esm/server/stdio.js');
await server.connect(new StdioServerTransport());
