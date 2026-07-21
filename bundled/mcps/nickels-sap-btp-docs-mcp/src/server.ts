import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ErrorCode,
  McpError
} from '@modelcontextprotocol/sdk/types.js';
import { DocumentIndex } from './indexer/document-index.js';
import { searchDocs, type SearchDocsArgs } from './tools/search.js';
import { getDocument, type GetDocumentArgs } from './tools/get-document.js';
import { getServiceDocs, type GetServiceDocsArgs } from './tools/get-service.js';
import { listCategories } from './tools/list-categories.js';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export class SAPBTPMCPServer {
  private server: Server;
  private index: DocumentIndex;
  private docsPath: string;

  constructor(docsPath?: string) {
    // Default to docs/sap-btp-docs/docs relative to project root
    this.docsPath = docsPath || path.join(__dirname, '..', 'docs', 'sap-btp-docs', 'docs');

    this.server = new Server(
      {
        name: 'sap-btp-documentation-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.index = new DocumentIndex(this.docsPath);

    this.setupHandlers();
  }

  private setupHandlers(): void {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'search_btp_docs',
            description: 'Semantically search SAP BTP documentation. Returns relevant documents with excerpts and relevance scores.',
            inputSchema: {
              type: 'object',
              properties: {
                query: {
                  type: 'string',
                  description: 'Search query for BTP documentation (e.g., "Cloud Foundry deployment", "CAP service", "SAP HANA Cloud")',
                },
                service_area: {
                  type: 'string',
                  enum: ['all', 'development', 'administration', 'integration', 'security'],
                  description: 'Limit search to specific service area (default: all)',
                  default: 'all',
                },
                limit: {
                  type: 'number',
                  description: 'Maximum number of results to return (default: 10)',
                  default: 10,
                  minimum: 1,
                  maximum: 50,
                },
              },
              required: ['query'],
            },
          },
          {
            name: 'get_btp_document',
            description: 'Get the complete content of a specific BTP documentation page by its path.',
            inputSchema: {
              type: 'object',
              properties: {
                path: {
                  type: 'string',
                  description: 'Relative path to the document (as returned from search results)',
                },
              },
              required: ['path'],
            },
          },
          {
            name: 'get_service_documentation',
            description: 'Get comprehensive documentation for a specific SAP BTP service (e.g., "SAP HANA Cloud", "Cloud Foundry", "Kyma Runtime").',
            inputSchema: {
              type: 'object',
              properties: {
                service_name: {
                  type: 'string',
                  description: 'Name of the SAP BTP service',
                },
              },
              required: ['service_name'],
            },
          },
          {
            name: 'list_btp_categories',
            description: 'List all available documentation categories and their contents. Useful for exploring what documentation is available.',
            inputSchema: {
              type: 'object',
              properties: {},
            },
          },
        ],
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'search_btp_docs': {
            const result = await searchDocs(this.index, args as unknown as SearchDocsArgs);
            return {
              content: [{ type: 'text', text: result }],
            };
          }

          case 'get_btp_document': {
            const result = await getDocument(this.index, args as unknown as GetDocumentArgs);
            return {
              content: [{ type: 'text', text: result }],
            };
          }

          case 'get_service_documentation': {
            const result = await getServiceDocs(this.index, args as unknown as GetServiceDocsArgs);
            return {
              content: [{ type: 'text', text: result }],
            };
          }

          case 'list_btp_categories': {
            const result = await listCategories(this.index);
            return {
              content: [{ type: 'text', text: result }],
            };
          }

          default:
            throw new McpError(
              ErrorCode.MethodNotFound,
              `Unknown tool: ${name}`
            );
        }
      } catch (error) {
        if (error instanceof McpError) {
          throw error;
        }

        throw new McpError(
          ErrorCode.InternalError,
          `Tool execution failed: ${error}`
        );
      }
    });
  }

  async initialize(): Promise<void> {
    console.error('Initializing SAP BTP Documentation MCP Server...');
    console.error(`Documentation path: ${this.docsPath}`);
    await this.index.buildIndex();
    console.error('Server ready!');
  }

  async run(): Promise<void> {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('SAP BTP MCP Server running on stdio');
  }
}
