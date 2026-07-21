import { HierarchicalSAPToolRegistry } from './tools/hierarchical-tool-registry.js';
import { SAPToolRegistry } from './tools/sap-tool-registry.js';
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { randomUUID } from "node:crypto";
import 'dotenv/config';
import { DestinationService } from './services/destination-service.js';
import { SAPClient } from './services/sap-client.js';
import { Logger } from './utils/logger.js';
import { Config } from './utils/config.js';

import { ErrorHandler } from './utils/error-handler.js';
import { ODataService } from './types/sap-types.js';

export class MCPServer {
    private logger: Logger;
    private sapClient: SAPClient;
    private discoveredServices: ODataService[];
    private mcpServer: McpServer;
    private toolRegistry: HierarchicalSAPToolRegistry | SAPToolRegistry;
    private userToken?: string;

    constructor(discoveredServices: ODataService[]) {
        this.logger = new Logger('mcp-server');
        const config = new Config();
        const destinationService = new DestinationService(this.logger, config);
        this.sapClient = new SAPClient(destinationService, this.logger);
        this.discoveredServices = discoveredServices;
        this.mcpServer = new McpServer({
            name: "btp-sap-odata-to-mcp-server",
            version: "2.0.0"
        });
        this.mcpServer.server.onerror = (error) => {
            this.logger.error('MCP Server Error:', error);
            ErrorHandler.handle(error);
        };

        // Choose registry type based on env variable
        const registryType = process.env.MCP_TOOL_REGISTRY_TYPE || 'hierarchical';
        if (registryType === 'flat') {
            this.toolRegistry = new SAPToolRegistry(this.mcpServer, this.sapClient, this.logger, this.discoveredServices);
            this.logger.info('Using SAPToolRegistry (flat) for MCP tool exposure');
        } else {
            this.toolRegistry = new HierarchicalSAPToolRegistry(this.mcpServer, this.sapClient, this.logger, this.discoveredServices);
            this.logger.info('Using HierarchicalSAPToolRegistry for MCP tool exposure');
        }
    }

    /**
     * Set the user's JWT token for authenticated operations
     */
    setUserToken(token?: string): void {
        this.userToken = token;
        if (this.toolRegistry instanceof HierarchicalSAPToolRegistry) {
            this.toolRegistry.setUserToken(token);
        }
        // Note: SAPToolRegistry doesn't support user tokens yet
        this.logger.debug(`User token ${token ? 'set' : 'cleared'} for MCP server`);
    }

    async initialize(): Promise<void> {
        try {
            // Check which registry type we're using
            if (this.toolRegistry instanceof HierarchicalSAPToolRegistry) {
                // HierarchicalSAPToolRegistry has both methods
                this.toolRegistry.registerServiceMetadataResources();
                await this.toolRegistry.registerDiscoveryTools();
            } else if (this.toolRegistry instanceof SAPToolRegistry) {
                // SAPToolRegistry has different methods
                this.toolRegistry.registerServiceMetadataResources();
                await this.toolRegistry.registerServiceCRUDTools();
            }
            this.logger.info('🔧 Registered MCP tools for SAP operations');
        } catch (error) {
            this.logger.error('❌ Failed to initialize server:', error);
            throw error;
        }
    }

    async connectStdio(): Promise<void> {
        const transport = new StdioServerTransport();
        await this.mcpServer.connect(transport);
        this.logger.info('📡 Connected to stdio transport');
    }

    createHTTPTransport(options?: {
        enableDnsRebindingProtection?: boolean;
        allowedHosts?: string[];
    }): StreamableHTTPServerTransport {
        return new StreamableHTTPServerTransport({
            sessionIdGenerator: () => randomUUID(),
            enableDnsRebindingProtection: options?.enableDnsRebindingProtection || true,
            allowedHosts: options?.allowedHosts || ['127.0.0.1', 'localhost']
        });
    }

    getServer(): McpServer {
        return this.mcpServer;
    }
}

export async function createMCPServer(discoveredServices: ODataService[], userToken?: string): Promise<MCPServer> {
    const server = new MCPServer(discoveredServices);
    if (userToken) {
        server.setUserToken(userToken);
    }
    await server.initialize();
    return server;
}

export async function runStdioServer(discoveredServices: ODataService[]): Promise<void> {
    const logger = new Logger('sap-mcp-server');
    try {
        const server = await createMCPServer(discoveredServices);
        await server.connectStdio();
        logger.info('SAP MCP Server running on stdio...');
    } catch (error) {
        logger.error('Failed to start SAP MCP Server:', error);
        process.exit(1);
    }
}