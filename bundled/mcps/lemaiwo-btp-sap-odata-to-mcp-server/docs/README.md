# SAP OData MCP Server - Documentation

## Table of Contents

### Getting Started
- [Local Development Guide](./LOCAL_RUN.md) - Running the server locally
- [Deployment Guide](./DEPLOYMENT.md) - Deploying to SAP BTP

### Architecture & Design
- **[3-Level Progressive Discovery](./THREE_LEVEL_APPROACH.md)** - Core architecture (RECOMMENDED)
- [Microsoft Copilot Compatibility](./MICROSOFT_COPILOT_COMPATIBILITY.md) - Optimizations for Copilot
- [Service Discovery Configuration](./SERVICE_DISCOVERY_CONFIG.md) - Configuring service discovery

### Legacy Documentation
- [Two-Tool Intelligent Approach](./TWO_TOOL_INTELLIGENT_APPROACH.md) - Previous 2-tool architecture (deprecated)
- [Three-Tool Approach](./THREE_TOOL_APPROACH.md) - Intermediate 3-tool design (deprecated)

---

## Quick Links

### For Users
1. Start with [LOCAL_RUN.md](./LOCAL_RUN.md) to get the server running
2. Understand the [3-Level Architecture](./THREE_LEVEL_APPROACH.md)
3. Deploy using [DEPLOYMENT.md](./DEPLOYMENT.md)

### For Developers
1. Review [THREE_LEVEL_APPROACH.md](./THREE_LEVEL_APPROACH.md) for architecture details
2. Check [hierarchical-tool-registry.ts](../src/tools/hierarchical-tool-registry.ts) for implementation
3. See [MICROSOFT_COPILOT_COMPATIBILITY.md](./MICROSOFT_COPILOT_COMPATIBILITY.md) for LLM optimizations

---

## Architecture Overview

The SAP OData MCP Server uses a **3-level progressive discovery architecture**:

```
Level 1: discover-sap-data
    “ (minimal data for decision)
Level 2: get-entity-metadata
    “ (full schema details)
Level 3: execute-sap-operation
    “ (actual operation)
```

### Benefits
- **90% less tokens** in initial discovery
- **Progressive detail** - fetch schemas only when needed
- **Clear workflow** - Discovery ’ Understanding ’ Execution
- **Better LLM experience** - smaller responses, clearer workflow

See [THREE_LEVEL_APPROACH.md](./THREE_LEVEL_APPROACH.md) for complete details.

---

## Contributing

When updating documentation:
1. Update relevant .md files in `/docs`
2. Update main [README.md](../README.md) if needed
3. Keep code examples accurate
4. Test with actual LLMs when possible

---

## Questions?

- Check the main [README.md](../README.md)
- Review [THREE_LEVEL_APPROACH.md](./THREE_LEVEL_APPROACH.md)
- See implementation in [hierarchical-tool-registry.ts](../src/tools/hierarchical-tool-registry.ts)
