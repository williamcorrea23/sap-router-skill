# SAP BTP Documentation MCP Server

A Model Context Protocol (MCP) server providing semantic search and intelligent access to SAP Business Technology Platform (BTP) documentation.

## Overview

This MCP server enables AI assistants like Claude to search, retrieve, and understand SAP BTP documentation efficiently. It provides semantic search capabilities across the entire BTP documentation repository.

## Features

- **Semantic Search**: Intelligent search across all SAP BTP documentation
- **Category Filtering**: Search within specific areas (development, administration, integration, security)
- **Document Retrieval**: Get complete documentation pages with table of contents
- **Service-Specific Documentation**: Quick access to documentation for specific BTP services
- **Relevance Scoring**: Results ranked by relevance to your query

## Installation

### Prerequisites

- Node.js 20.0.0 or higher
- npm or yarn

### Quick Start

1. Clone this repository:
```bash
git clone <repository-url>
cd dlwr-dnl-btp-documentation-mcp
```

2. Install dependencies:
```bash
source ~/.zshrc && nvm use
npm install
```

3. Build the server:
```bash
npm run build
```

4. The SAP BTP documentation will be automatically cloned during first build (located in `docs/sap-btp-docs/`)

## Configuration

### Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "sap-btp-docs": {
      "command": "node",
      "args": [
        "/absolute/path/to/dlwr-dnl-btp-documentation-mcp/build/index.js"
      ]
    }
  }
}
```

### Custom Documentation Path

To use a different documentation location:

```json
{
  "mcpServers": {
    "sap-btp-docs": {
      "command": "node",
      "args": [
        "/absolute/path/to/dlwr-dnl-btp-documentation-mcp/build/index.js"
      ],
      "env": {
        "SAP_BTP_DOCS_PATH": "/path/to/custom/docs"
      }
    }
  }
}
```

## Available Tools

### 1. search_btp_docs

Semantically search SAP BTP documentation.

**Parameters:**
- `query` (required): Search query string
- `service_area` (optional): Filter by area ('all', 'development', 'administration', 'integration', 'security')
- `limit` (optional): Maximum results (1-50, default: 10)

**Example:**
```
Search for "Cloud Foundry deployment best practices"
```

### 2. get_btp_document

Retrieve complete content of a specific documentation page.

**Parameters:**
- `path` (required): Relative path to document (from search results)

**Example:**
```
Get document at path "docs/30-development/deploy-app.md"
```

### 3. get_service_documentation

Get comprehensive documentation for a specific SAP BTP service.

**Parameters:**
- `service_name` (required): Name of the BTP service

**Example:**
```
Get documentation for "SAP HANA Cloud"
```

### 4. list_btp_categories

List all available documentation categories and top documents.

**Example:**
```
Show all available documentation categories
```

## Development

### Project Structure

```
dlwr-dnl-btp-documentation-mcp/
├── src/
│   ├── index.ts              # Entry point
│   ├── server.ts             # MCP server implementation
│   ├── types/
│   │   └── index.ts          # TypeScript type definitions
│   ├── indexer/
│   │   ├── markdown-parser.ts    # Markdown document parser
│   │   └── document-index.ts     # Document indexing & search
│   └── tools/
│       ├── search.ts             # Search tool implementation
│       ├── get-document.ts       # Document retrieval tool
│       ├── get-service.ts        # Service documentation tool
│       └── list-categories.ts    # Category listing tool
├── docs/
│   └── sap-btp-docs/         # SAP BTP documentation (cloned)
├── build/                     # Compiled JavaScript output
├── package.json
├── tsconfig.json
└── README.md
```

### Build Commands

```bash
# Build once
npm run build

# Build and watch for changes
npm run watch

# Run the server directly
npm run dev
```

### Testing

Test the server using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector node build/index.js
```

## Architecture

### Document Indexing

The server indexes all markdown files from the SAP BTP documentation repository on startup:

1. **Parsing**: Uses `unified` and `remark` to parse markdown with frontmatter
2. **Extraction**: Extracts metadata, headings, sections, and keywords
3. **Indexing**: Creates a searchable index using Fuse.js for fuzzy semantic search
4. **Categorization**: Automatically categorizes documents based on folder structure

### Search Strategy

- **Multi-field search**: Searches across titles, headings, content, and keywords
- **Weighted scoring**: Titles and keywords weighted higher than content
- **Fuzzy matching**: Handles typos and partial matches
- **Context extraction**: Returns relevant excerpts around matched terms

## Use Cases

### For delaware Netherlands Team

- **Quick Reference**: Instant access to BTP documentation during client engagements
- **Training**: Support for DI AI Program training and enablement
- **Solution Design**: Research integration patterns and best practices
- **Troubleshooting**: Find solutions for specific BTP issues

### For AI Agents (ConnectedBrain 2.0)

- **Semantic Module**: Integrate as a knowledge module in multi-agent orchestration
- **Context Provider**: Supply BTP-specific context for solution generation
- **Code Assistant**: Help generate BTP-compliant code and configurations

## Performance

- **Initial Index Build**: ~5-10 seconds (depending on documentation size)
- **Search Queries**: <100ms (in-memory search)
- **Memory Usage**: ~50-100MB (indexed documents)

## Roadmap

### Phase 2 Enhancements
- Vector embeddings for improved semantic search
- Code sample extraction and indexing
- Integration pattern recognition
- Auto-update mechanism for documentation

### Phase 3 Advanced Features
- Graph database for service relationships
- Context caching for frequently accessed docs
- Integration with SAP Help Portal
- Multi-language support

## Contributing

This is a delaware Netherlands internal tool. For questions or contributions, contact the Data & AI team.

## License

MIT License - Internal delaware Netherlands use

## Support

For issues or questions:
- Internal: delaware Netherlands Data & AI team
- Documentation: [SAP BTP Official Docs](https://help.sap.com/docs/btp)

---

**Built with ❤️ by delaware Netherlands Data & AI Team**

*Part of our "platform-first, cloud-native" AI-empowered operations initiative*
