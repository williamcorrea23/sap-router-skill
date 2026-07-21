# Microsoft Copilot Compatibility Improvements

## Overview

The hierarchical tool registry has been optimized to just **3 progressive discovery tools** with token-efficient design and clear workflow separation, specifically designed to work excellently with Microsoft Copilot Studio and other AI assistants.

## Major Update: 3-Level Progressive Discovery

The registry has been redesigned with a 3-level architecture optimized for token efficiency:

### Evolution

- **Original**: 200+ tools (one per entity operation)
- **v1**: 4 tools (search, discover, schema, execute)
- **v2**: 3 tools (combined search+discover)
- **v3**: 2 tools (intelligent universal discovery + execute)
- **v4 (Current)**: **3 tools** (progressive discovery: minimal → full → execute)

### New Structure (3 Levels)

1. **discover-sap-data** (Level 1) - Lightweight discovery with minimal data
   - Returns only: serviceId, serviceName, entityName, entityCount
   - Optimized for LLM decision-making
   - ~90% less data than full schemas
   - Fallback: Returns ALL services if no matches

2. **get-entity-metadata** (Level 2) - Full schema on-demand
   - Returns complete entity schema with all properties
   - Only fetched when needed (after Level 1 selection)
   - Includes types, keys, capabilities, constraints

3. **execute-sap-operation** (Level 3) - Authenticated CRUD operations
   - Uses metadata from Level 2
   - Performs actual operations with user auth

**Revolutionary Benefits:**

- **Token Efficient** - Level 1 returns 90% less data
- **Progressive Detail** - Fetch full schemas only when needed
- **Clear Workflow** - Discovery → Understand → Execute
- **Better Tool Selection** - Clear separation of concerns
- **Optimal for Copilot** - Smaller responses fit within token limits
- **Scalable** - Works with hundreds of services

See [THREE_LEVEL_APPROACH.md](./THREE_LEVEL_APPROACH.md) for complete details.

## Key Changes

### 1. Removed Emoji Characters from Tool Descriptions

**Before:**
```typescript
description: "🔐 AUTHENTICATION AWARE: Search and filter..."
```

**After:**
```typescript
description: "AUTHENTICATION AWARE: Search and filter..."
```

**Reason:** Emojis can cause parsing issues in some AI systems and don't add semantic value for machine processing.

### 2. Replaced Enum Types with String Types

**Before:**
```typescript
category: z.enum(["business-partner", "sales", "finance", "procurement", "hr", "logistics", "all"]).optional()
```

**After:**
```typescript
category: z.string().optional().describe("Service category filter. Valid values: business-partner, sales, finance, procurement, hr, logistics, all. Default: all")
```

**Reason:** Microsoft Copilot Studio interprets enum inputs as plain strings, which can cause type mismatches. Using string types with descriptive validation instructions works better across different AI platforms.

### 3. Flattened Nested Schema Objects

**Before:**
```typescript
queryOptions: z.object({
    $filter: z.string().optional(),
    $select: z.string().optional(),
    $expand: z.string().optional(),
    $orderby: z.string().optional(),
    $top: z.number().optional(),
    $skip: z.number().optional()
}).optional()
```

**After:**
```typescript
filterString: z.string().optional().describe("OData $filter query option value. Use OData filter syntax without the '$filter=' prefix. Examples: \"Status eq 'Active'\", \"Amount gt 1000\"..."),
selectString: z.string().optional().describe("OData $select query option value. Comma-separated list of property names without the '$select=' prefix. Example: \"Name,Status,CreatedDate\"..."),
expandString: z.string().optional().describe("OData $expand query option value. Comma-separated list of navigation properties without the '$expand=' prefix. Example: \"Customer,Items\"..."),
orderbyString: z.string().optional().describe("OData $orderby query option value. Specify property and direction without the '$orderby=' prefix. Examples: \"Name desc\", \"CreatedDate asc\"..."),
topNumber: z.number().optional().describe("OData $top query option value. Number of records to return (limit/page size). This will be converted to the $top parameter..."),
skipNumber: z.number().optional().describe("OData $skip query option value. Number of records to skip (offset for pagination). This will be converted to the $skip parameter...")
```

**Important Note:** These flattened parameters are internally mapped to OData query parameters:

- `filterString` → `$filter` query parameter
- `selectString` → `$select` query parameter
- `expandString` → `$expand` query parameter
- `orderbyString` → `$orderby` query parameter
- `topNumber` → `$top` query parameter
- `skipNumber` → `$skip` query parameter

The implementation automatically constructs the proper OData query URL with the `$` prefixes. Users simply provide the values:

- `filterString: "Status eq 'Active'"` becomes `?$filter=Status eq 'Active'` in the OData request
- `selectString: "Name,Status"` becomes `?$select=Name,Status` in the OData request
- `topNumber: 10` becomes `?$top=10` in the OData request

**Reason:** Microsoft Copilot Studio has known issues with nested object schemas:
- Reference type inputs may be filtered out
- Complex nested structures can be truncated
- Flat schemas are more reliably interpreted

### 4. Improved Response Formatting

**Before:**
```
📋 Next step: Use 'discover-service-entities'...
⚠️ IMPORTANT: Always use the 'id' field...
```

**After:**
```
== NEXT STEPS ==
1. Use the 'discover-service-entities' tool to see entities within a service
2. Set the serviceId parameter to the 'id' field from the results above
3. IMPORTANT: Use the 'id' field as serviceId, NOT the 'title' field
```

**Reason:** Structured, numbered lists are easier for AI assistants to parse and understand than free-form text with emojis.

### 5. Added Input Validation

Added runtime validation for string-based enum values:

```typescript
// Validate category for better Copilot compatibility
const validCategories = ["business-partner", "sales", "finance", "procurement", "hr", "logistics", "all"];
if (!validCategories.includes(category)) {
    category = "all"; // Default to 'all' if invalid category provided
}
```

**Reason:** Since we can't use Zod enums, we need runtime validation to ensure data integrity.

## OData Query Syntax Guide

The tool descriptions now include explicit OData syntax guidance to help AI assistants construct proper queries:

### Filter String ($filter)

AI assistants should construct filter expressions using OData operators:

- **Comparison operators:** `eq` (equals), `ne` (not equals), `gt` (greater than), `lt` (less than), `ge` (>=), `le` (<=)
- **Logical operators:** `and`, `or`, `not`
- **Examples:**
  - `filterString: "Status eq 'Active'"` - Filter by status
  - `filterString: "Amount gt 1000"` - Filter by amount greater than 1000
  - `filterString: "Name eq 'John' and Status eq 'Active'"` - Combined filter

### Select String ($select)

Comma-separated list of property names to return:

- `selectString: "Name,Status,CreatedDate"`
- `selectString: "CustomerID,CustomerName,Address"`

### Expand String ($expand)

Comma-separated list of navigation properties to include:

- `expandString: "Customer,Items"`
- `expandString: "OrderDetails,ShippingAddress"`

### Order By String ($orderby)

Property name with optional direction (asc/desc):

- `orderbyString: "Name desc"`
- `orderbyString: "CreatedDate asc"`
- `orderbyString: "Amount desc, Name asc"` - Multiple sort fields

### Top Number ($top)

Number of records to return:

- `topNumber: 10` - Return top 10 records

### Skip Number ($skip)

Number of records to skip for pagination:

- `skipNumber: 20` - Skip first 20 records

**Important:** AI assistants should provide these values WITHOUT the `$` prefix. The server implementation automatically adds the proper OData query parameter prefixes.

## Backward Compatibility

The changes maintain full backward compatibility:

1. **Legacy queryOptions support:** The flattened parameters are merged with legacy `queryOptions` object if provided
2. **Default values:** All optional parameters have sensible defaults
3. **Same functionality:** All existing features work exactly as before

## Testing with Microsoft Copilot

To test the improved compatibility:

1. **Configure MCP Server in Copilot Studio:**
   ```yaml
   # Add your server configuration
   server:
     url: http://localhost:3000
     transport: http
   ```

2. **Test Tool Discovery:**
   - Verify all 4 tools appear in Copilot Studio
   - Check that tool descriptions are properly displayed
   - Confirm input parameters are all visible

3. **Test Tool Invocation:**
   ```
   User: "Search for sales services"
   Expected: Copilot calls search-sap-services with category="sales"

   User: "List entities in service API_SALES_ORDER_SRV"
   Expected: Copilot calls discover-service-entities with correct serviceId

   User: "Read the first 10 sales orders"
   Expected: Copilot calls execute-entity-operation with operation="read" and topNumber=10
   ```

## Known Microsoft Copilot Limitations

Based on Microsoft's documentation, the following limitations exist:

1. **Schema Property Support:**
   - `exclusiveMinimum` and similar constraints may cause exceptions
   - Use `minimum`/`maximum` instead

2. **Type Support:**
   - Reference types may be filtered out
   - Array types with multiple types get truncated
   - Use simple types when possible

3. **Dynamic Updates:**
   - Copilot Studio dynamically reflects tool changes
   - No manual refresh needed when tools are updated

## Configuration

No additional configuration is required. The hierarchical tool registry is used by default. To switch to the flat registry (not recommended for Copilot):

```env
MCP_TOOL_REGISTRY_TYPE=flat
```

## Benefits for Other AI Assistants

These improvements benefit all AI assistants, not just Microsoft Copilot:

- **Claude:** Cleaner, more parseable tool definitions
- **GitHub Copilot:** Better understanding of parameter relationships
- **ChatGPT:** Improved tool selection accuracy
- **Other MCP Clients:** Enhanced compatibility across the ecosystem

## References

- [Microsoft Copilot Studio MCP Documentation](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-mcp)
- [MCP Known Issues with Tool Definitions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-mcp#known-issues)
- [Model Context Protocol Specification](https://modelcontextprotocol.io)
