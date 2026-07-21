# Skill Creation Guide

This guide explains how to create skills and tools in Skillian.

## Overview

A **Skill** is a domain-specific capability composed of:
- **Tools**: Callable functions the LLM can invoke
- **Knowledge**: RAG documents for context (optional)
- **System Prompt**: Domain-specific instructions

Skills are defined using configuration files rather than Python classes, making them easy to create and modify.

## Directory Structure

Each skill lives in its own directory under `app/skills/`:

```
app/skills/
├── my_skill/
│   ├── SKILL.md        # Required: Metadata and instructions
│   ├── tools.yaml      # Required: Tool definitions
│   ├── tools.py        # Required: Tool implementations
│   └── knowledge/      # Optional: RAG documents
│       ├── concepts.md
│       └── examples.md
└── _templates/         # Skill templates (ignored by loader)
    └── basic/
```

Directories starting with `_` are ignored by the skill loader.

## Step 1: Create SKILL.md

The `SKILL.md` file defines skill metadata and the system prompt using YAML frontmatter and Markdown.

### Required Fields

```yaml
---
name: my-skill                    # Unique identifier (use hyphens, no spaces)
description: |
  Brief description of what this skill does.
  Include key capabilities and use cases.
---
```

### Optional Fields

```yaml
---
name: data-analyst
description: Compare and analyze data from multiple sources
version: "1.0.0"                  # Semantic versioning
author: your-name
domain: analytics                 # Business domain
tags:                             # For filtering/search
  - data-analysis
  - comparison
connector: business               # Required connector type (null if none)
license: MIT
---
```

### Markdown Sections

After the frontmatter, add Markdown sections that become the system prompt:

```markdown
# My Skill

Brief introduction explaining the skill's purpose.

## Instructions

You are a [role] assistant helping users with [domain].

Your role is to:
1. First priority
2. Second priority
3. Third priority

When handling requests:
- Important guideline
- Another guideline

## Capabilities

- Capability one
- Capability two
- Capability three

## When to Use

Activate this skill when the user asks about:
- Topic one
- Topic two

## Examples

### Example 1: Basic Query

User: "Show me sales for Q1"
Assistant: Uses the query_data tool to retrieve sales data...

### Example 2: Complex Analysis

User: "Compare current quarter to last year"
Assistant: First queries both periods, then uses compare tool...
```

### Complete Example

See [app/skills/data_analyst/SKILL.md](../app/skills/data_analyst/SKILL.md) for a real example.

## Step 2: Create tools.yaml

The `tools.yaml` file defines the tools available to the LLM.

### Basic Structure

```yaml
tools:
  - name: tool_name
    description: |
      Detailed description of what this tool does.
      Include:
      - What the tool returns
      - When to use it
      - Any important notes
    parameters:
      - name: param1
        type: string
        required: true
        description: Description shown to LLM
      - name: param2
        type: integer
        required: false
        description: Optional parameter
        default: 10
    implementation: app.skills.my_skill.tools:tool_name
```

### Parameter Types

| YAML Type | Python Type | Notes |
|-----------|-------------|-------|
| `string` | `str` | Default if not specified |
| `integer` / `int` | `int` | |
| `number` / `float` | `float` | |
| `boolean` / `bool` | `bool` | |
| `array` / `list` | `list` | |
| `object` / `dict` | `dict` | Can have nested properties |

### Nested Object Parameters

```yaml
parameters:
  - name: filters
    type: object
    required: false
    description: Filter conditions
    properties:
      company:
        type: string
        description: Filter by company code
      year:
        type: integer
        description: Filter by fiscal year
```

### Implementation Options

**Option 1: Python Function**
```yaml
implementation: app.skills.my_skill.tools:my_function
```

**Option 2: Query Template** (zero-code tool)
```yaml
query_template: |
  SELECT * FROM table WHERE field = '{param1}' AND year = {param2}
```

Query templates require a connector that supports `execute_sql()` or `execute()`.

### Tool Writing Best Practices

1. **Write detailed descriptions**: The LLM uses these to decide when and how to use tools
2. **Document return values**: Explain what the tool returns
3. **Use meaningful parameter names**: Self-documenting names help the LLM
4. **Mark required vs optional**: Only mark truly required parameters as `required: true`
5. **Provide defaults**: Set sensible defaults for optional parameters

### Complete Example

```yaml
tools:
  - name: list_sources
    description: |
      List all available data sources.

      Returns information about each configured data source including:
      - Source name and description
      - Available dimensions (grouping fields)
      - Available measures (aggregatable values)
      - Valid comparison pairs based on common dimensions

      Use this tool first to understand what data sources are available
      before querying or comparing them.
    parameters: []
    implementation: app.skills.data_analyst.tools:list_sources

  - name: query_source
    description: |
      Query a single data source with aggregation.

      Executes a query against one data source, grouping by specified
      dimensions and aggregating measures.
    parameters:
      - name: source
        type: string
        required: true
        description: Name of the source to query
      - name: dimensions
        type: array
        required: false
        description: Fields to group by
      - name: measures
        type: array
        required: false
        description: Values to aggregate
      - name: filters
        type: object
        required: false
        description: Filter conditions as dimension:value pairs
    implementation: app.skills.data_analyst.tools:query_source
```

## Step 3: Create tools.py

The `tools.py` file contains the Python implementations of your tools.

### Function Signature Pattern

```python
"""Tool implementations for my_skill."""

from typing import Any


async def my_tool(
    param1: str,
    param2: int | None = None,
    connector: Any | None = None,
) -> dict[str, Any]:
    """Tool docstring (not used by LLM - use tools.yaml description).

    Args:
        param1: First parameter
        param2: Optional second parameter
        connector: Injected by the skill loader if skill requires connector

    Returns:
        Result dictionary
    """
    # Implementation
    return {
        "status": "success",
        "data": [...],
    }
```

### Key Points

1. **Async is preferred**: Use `async def` for tools that do I/O
2. **Connector injection**: Add `connector: Any = None` parameter to receive the configured connector
3. **Return dictionaries**: Return structured data the LLM can interpret
4. **Type hints**: Use modern Python 3.10+ type hints (`str | None` not `Optional[str]`)

### Sync vs Async

Both sync and async functions are supported:

```python
# Sync function - simple operations
def list_items() -> dict[str, Any]:
    return {"items": [...]}

# Async function - I/O operations
async def fetch_data(query: str, connector: Any = None) -> dict[str, Any]:
    result = await connector.execute(query)
    return {"rows": result}
```

### Class-Based Tools

For complex tools with shared state, use a class:

```python
class MySkillTools:
    """Tool implementations with shared state."""

    def __init__(self, connector: Any):
        self._connector = connector
        self._cache = {}

    async def query(self, source: str) -> dict[str, Any]:
        if source in self._cache:
            return self._cache[source]
        result = await self._connector.execute(...)
        self._cache[source] = result
        return result


# Standalone functions for YAML loader
def get_tools_instance(connector: Any) -> MySkillTools:
    return MySkillTools(connector)


async def query(source: str, connector: Any = None) -> dict[str, Any]:
    """Wrapper function called by skill loader."""
    tools = get_tools_instance(connector)
    return await tools.query(source)
```

### Return Value Best Practices

Structure return values for LLM consumption:

```python
async def compare_sources(
    source_a: str,
    source_b: str,
    connector: Any = None,
) -> dict[str, Any]:
    # Do comparison...

    return {
        # Summary section for quick understanding
        "summary": {
            "total_rows": 100,
            "matches": 85,
            "differences": 15,
            "match_percentage": 85.0,
        },
        # Detailed data (limit large datasets)
        "differences": differences[:50],
        "truncated": len(differences) > 50,
        # Human-readable interpretation
        "interpretation": "Good alignment (85% match). 15 rows need review.",
        # Reference for follow-up queries
        "cache_key": "comparison_abc123",
    }
```

## Step 4: Add Knowledge (Optional)

Create a `knowledge/` directory with Markdown files for RAG:

```
app/skills/my_skill/
└── knowledge/
    ├── concepts.md      # Domain concepts and terminology
    ├── procedures.md    # Common procedures
    └── troubleshooting.md
```

These documents are indexed and retrieved to provide context to the LLM when answering questions.

## Connectors

If your skill needs a database or API connection, specify the connector type:

```yaml
# SKILL.md
---
connector: business   # Uses 'business' connector from factory
---
```

The connector is injected into tool functions that have a `connector` parameter:

```python
async def query(sql: str, connector: Any = None) -> dict:
    return await connector.execute(sql)
```

Available connectors are configured in `app/dependencies.py`.

## Validation

Use the CLI to validate your skill:

```bash
# Validate SKILL.md and tools.yaml
uv run python -m app.cli validate-skill my_skill

# List all discovered skills
uv run python -m app.cli list-skills
```

The validator checks:
- Required fields in SKILL.md
- Valid YAML syntax in tools.yaml
- Tool name uniqueness
- Parameter definitions
- Implementation paths (if connectors available)

## Quick Start Template

Copy the template to create a new skill:

```bash
cp -r app/skills/_templates/basic app/skills/my_skill
```

Then edit:
1. `SKILL.md` - Update name, description, instructions
2. `tools.yaml` - Define your tools
3. `tools.py` - Implement the functions

## Example: Creating a Simple Skill

### 1. SKILL.md

```yaml
---
name: calculator
description: Perform mathematical calculations and unit conversions
version: "1.0.0"
domain: utilities
tags: [math, calculator]
connector: null
---

# Calculator Skill

Helps users with mathematical calculations.

## Instructions

You are a calculator assistant. Use the available tools to perform calculations.
Always show your work and explain the steps.

## Capabilities

- Basic arithmetic (add, subtract, multiply, divide)
- Unit conversions
- Percentage calculations
```

### 2. tools.yaml

```yaml
tools:
  - name: calculate
    description: |
      Perform a mathematical calculation.
      Supports: +, -, *, /, ^, sqrt, sin, cos, tan, log
      Examples: "2 + 2", "sqrt(16)", "10 * 5 / 2"
    parameters:
      - name: expression
        type: string
        required: true
        description: Mathematical expression to evaluate
    implementation: app.skills.calculator.tools:calculate

  - name: convert_units
    description: |
      Convert between units of measurement.
      Supports length, weight, temperature, volume.
    parameters:
      - name: value
        type: number
        required: true
        description: The value to convert
      - name: from_unit
        type: string
        required: true
        description: Source unit (e.g., 'km', 'lb', 'celsius')
      - name: to_unit
        type: string
        required: true
        description: Target unit (e.g., 'm', 'kg', 'fahrenheit')
    implementation: app.skills.calculator.tools:convert_units
```

### 3. tools.py

```python
"""Calculator skill tools."""

import math
from typing import Any


def calculate(expression: str) -> dict[str, Any]:
    """Evaluate a mathematical expression."""
    # Safe evaluation (limited to math operations)
    allowed = {
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'log': math.log,
        'pi': math.pi,
        'e': math.e,
    }

    try:
        result = eval(expression, {"__builtins__": {}}, allowed)
        return {
            "expression": expression,
            "result": result,
            "type": type(result).__name__,
        }
    except Exception as e:
        return {
            "expression": expression,
            "error": str(e),
        }


CONVERSIONS = {
    ('km', 'm'): lambda x: x * 1000,
    ('m', 'km'): lambda x: x / 1000,
    ('celsius', 'fahrenheit'): lambda x: x * 9/5 + 32,
    ('fahrenheit', 'celsius'): lambda x: (x - 32) * 5/9,
    ('kg', 'lb'): lambda x: x * 2.205,
    ('lb', 'kg'): lambda x: x / 2.205,
}


def convert_units(
    value: float,
    from_unit: str,
    to_unit: str,
) -> dict[str, Any]:
    """Convert between units."""
    key = (from_unit.lower(), to_unit.lower())

    if key not in CONVERSIONS:
        return {
            "error": f"Conversion from {from_unit} to {to_unit} not supported",
            "supported": list(CONVERSIONS.keys()),
        }

    result = CONVERSIONS[key](value)
    return {
        "original": {"value": value, "unit": from_unit},
        "converted": {"value": result, "unit": to_unit},
    }
```

## Troubleshooting

### Skill not discovered
- Check directory is under `app/skills/`
- Ensure `SKILL.md` exists in the directory
- Directory name must not start with `_`

### Tools not loading
- Verify `tools.yaml` syntax with a YAML validator
- Check implementation path format: `module.path:function_name`
- Ensure the Python module is importable

### Connector not found
- Verify connector name matches one in `connector_factory`
- Check connector is registered in `app/dependencies.py`

### Parameters not passed correctly
- Ensure parameter names in YAML match function signature
- Check type mappings are correct
- Verify required fields are marked appropriately
