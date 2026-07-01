import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";

// Read tools
import { transportListTool, TransportListInputSchema } from "../tools/transport-list.tool.js";
import { transportGetTool, TransportGetInputSchema } from "../tools/transport-get.tool.js";
import { transportObjectsTool, TransportObjectsInputSchema } from "../tools/transport-objects.tool.js";
import { importQueueTool, ImportQueueInputSchema } from "../tools/import-queue.tool.js";
import { systemInfoTool, SystemInfoInputSchema } from "../tools/system-info.tool.js";

// Write tools
import { transportCreateTool, TransportCreateInputSchema } from "../tools/transport-create.tool.js";
import { transportReleaseTool, TransportReleaseInputSchema } from "../tools/transport-release.tool.js";
import { transportDeleteTool, TransportDeleteInputSchema } from "../tools/transport-delete.tool.js";

export function createServer(): McpServer {
  const server = new McpServer({
    name: "sap-transport-mcp",
    version: "0.1.0",
  });

  registerReadTools(server);
  registerWriteTools(server);

  return server;
}

function registerReadTools(server: McpServer): void {
  server.tool(
    systemInfoTool.name,
    systemInfoTool.description,
    SystemInfoInputSchema.shape,
    async () => {
      const result = await systemInfoTool.handler({});
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
    }
  );

  server.tool(
    transportListTool.name,
    transportListTool.description,
    TransportListInputSchema.shape,
    async ({ owner, status, systemId }) => {
      const result = await transportListTool.handler({ owner, status, systemId });
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
    }
  );

  server.tool(
    transportGetTool.name,
    transportGetTool.description,
    TransportGetInputSchema.shape,
    async ({ transportNumber, systemId }) => {
      const result = await transportGetTool.handler({ transportNumber, systemId });
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
    }
  );

  server.tool(
    transportObjectsTool.name,
    transportObjectsTool.description,
    TransportObjectsInputSchema.shape,
    async ({ transportNumber, systemId }) => {
      const result = await transportObjectsTool.handler({ transportNumber, systemId });
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
    }
  );

  server.tool(
    importQueueTool.name,
    importQueueTool.description,
    ImportQueueInputSchema.shape,
    async ({ targetSystemId, systemId }) => {
      const result = await importQueueTool.handler({ targetSystemId, systemId });
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
    }
  );
}

function registerWriteTools(server: McpServer): void {
  server.tool(
    transportCreateTool.name,
    transportCreateTool.description,
    TransportCreateInputSchema.shape,
    async ({ description, type, targetSystem, systemId }) => {
      const result = await transportCreateTool.handler({ description, type, targetSystem, systemId });
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
    }
  );

  server.tool(
    transportReleaseTool.name,
    transportReleaseTool.description,
    TransportReleaseInputSchema.shape,
    async ({ transportNumber, systemId }) => {
      const result = await transportReleaseTool.handler({ transportNumber, systemId });
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
    }
  );

  server.tool(
    transportDeleteTool.name,
    transportDeleteTool.description,
    TransportDeleteInputSchema.shape,
    async ({ transportNumber, systemId }) => {
      const result = await transportDeleteTool.handler({ transportNumber, systemId });
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
    }
  );
}
