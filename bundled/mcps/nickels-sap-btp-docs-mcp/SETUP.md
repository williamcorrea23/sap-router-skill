# Setup Guide for SAP BTP Documentation MCP Server

This guide will help you set up and configure the SAP BTP Documentation MCP server for use with Claude Desktop.

## Prerequisites

1. **Node.js 20+**: Ensure you have Node.js version 20.0.0 or higher installed
   ```bash
   node --version
   ```

2. **Claude Desktop**: Install Claude Desktop application

## Step-by-Step Setup

### 1. Install Dependencies

Navigate to the project directory and install dependencies:

```bash
cd /Users/nicolaas/code/dlwr-dnl-btp-documentation-mcp
source ~/.zshrc && nvm use
npm install
```

### 2. Build the Server

Compile the TypeScript code:

```bash
npm run build
```

This will:
- Compile TypeScript to JavaScript in the `build/` directory
- Make the entry point executable
- The SAP BTP docs are already cloned in `docs/sap-btp-docs/`

### 3. Configure Claude Desktop

#### Locate the Configuration File

The Claude Desktop configuration file is located at:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

#### Add MCP Server Configuration

Edit the configuration file and add the SAP BTP MCP server:

```json
{
  "mcpServers": {
    "sap-btp-docs": {
      "command": "node",
      "args": [
        "/Users/nicolaas/code/dlwr-dnl-btp-documentation-mcp/build/index.js"
      ]
    }
  }
}
```

**Important**: Use the absolute path to your `build/index.js` file.

#### If You Already Have Other MCP Servers

If you already have other MCP servers configured, add the SAP BTP server to the existing configuration:

```json
{
  "mcpServers": {
    "existing-server": {
      "command": "...",
      "args": ["..."]
    },
    "sap-btp-docs": {
      "command": "node",
      "args": [
        "/Users/nicolaas/code/dlwr-dnl-btp-documentation-mcp/build/index.js"
      ]
    }
  }
}
```

### 4. Restart Claude Desktop

After modifying the configuration:

1. Completely quit Claude Desktop (Cmd+Q)
2. Relaunch Claude Desktop

### 5. Verify Installation

In Claude Desktop, start a new conversation and check for the MCP server:

1. Look for the 🔌 icon or tools indicator
2. You should see 4 available tools:
   - `search_btp_docs`
   - `get_btp_document`
   - `get_service_documentation`
   - `list_btp_categories`

### 6. Test the Server

Try a simple query in Claude Desktop:

```
Can you search the BTP documentation for "Cloud Foundry deployment"?
```

Claude should use the `search_btp_docs` tool to search the documentation.

## Advanced Configuration

### Custom Documentation Path

If you want to use a different location for the SAP BTP documentation:

1. Update the Claude Desktop configuration with an environment variable:

```json
{
  "mcpServers": {
    "sap-btp-docs": {
      "command": "node",
      "args": [
        "/Users/nicolaas/code/dlwr-dnl-btp-documentation-mcp/build/index.js"
      ],
      "env": {
        "SAP_BTP_DOCS_PATH": "/path/to/your/custom/docs/folder"
      }
    }
  }
}
```

### Update Documentation

To update the SAP BTP documentation to the latest version:

```bash
cd docs/sap-btp-docs
git pull origin main
```

Then restart the MCP server by restarting Claude Desktop.

## Troubleshooting

### Server Not Starting

**Check logs**: Claude Desktop logs can help diagnose issues:
```
~/Library/Logs/Claude/
```

**Verify build**: Ensure the build was successful:
```bash
ls -la build/index.js
```

The file should exist and be executable.

**Check Node version**:
```bash
node --version
# Should be 20.0.0 or higher
```

### Tools Not Appearing

1. **Restart Claude Desktop completely** (Cmd+Q, then relaunch)
2. **Verify configuration path**: Ensure the path in `claude_desktop_config.json` is absolute and correct
3. **Check JSON syntax**: Ensure the configuration file has valid JSON (no trailing commas, proper quotes)

### Search Returns No Results

1. **Verify docs are cloned**:
   ```bash
   ls docs/sap-btp-docs/docs/
   ```
   Should contain markdown files

2. **Rebuild index**: Restart the server (restart Claude Desktop)

### Performance Issues

If indexing is slow:

1. **Check documentation size**:
   ```bash
   du -sh docs/sap-btp-docs/
   ```

2. **Monitor memory**: The server uses ~50-100MB of RAM during operation

## Development Mode

For development and testing, you can run the server directly:

```bash
npm run dev
```

Or use the MCP Inspector for debugging:

```bash
npx @modelcontextprotocol/inspector node build/index.js
```

## Updating the Server

When updating the server code:

1. Pull latest changes (if using git)
2. Rebuild:
   ```bash
   npm run build
   ```
3. Restart Claude Desktop

## Integration with delaware Workflows

### For Team Members

Share this configuration with team members:

1. Clone the repository
2. Follow steps 1-4 above
3. Share the absolute path for their machines

### For ConnectedBrain 2.0

To integrate with ConnectedBrain orchestration:

1. Use the server as a semantic knowledge module
2. Configure with appropriate service area filters
3. Implement caching for frequently accessed documents

## Next Steps

Once setup is complete:

1. **Explore categories**: Use `list_btp_categories` to see available documentation
2. **Test searches**: Try searching for specific BTP services or concepts
3. **Retrieve documents**: Use search results to get full documentation pages
4. **Integrate into workflows**: Use for client engagements and solution design

## Support

For assistance:
- **Internal**: Contact delaware Netherlands Data & AI team
- **Issues**: Check build logs and Claude Desktop logs
- **Documentation**: Refer to main README.md

---

**Ready to use the SAP BTP Documentation MCP Server!** 🚀
