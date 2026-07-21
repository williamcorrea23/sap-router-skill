# Guide 3: YAML Tool Definitions

This guide explains how to implement loading tools from YAML configuration files, enabling no-code tool definitions.

## Overview

Instead of writing Python classes for every tool, you can define tools in YAML:

**Before (Python-only):**
```python
class CheckGLBalanceInput(BaseModel):
    account: str = Field(description="GL account number")
    company: str = Field(description="Company code")

def check_gl_balance(account: str, company: str) -> dict:
    # Implementation...
```

**After (YAML + Python):**
```yaml
# tools.yaml
tools:
  - name: check_gl_balance
    description: Check GL account balance
    parameters:
      - name: account
        type: string
        required: true
        description: GL account number
      - name: company
        type: string
        required: true
        description: Company code
    implementation: app.skills.financial.tools:check_gl_balance
```

## Step 1: Install Dependencies

Ensure PyYAML is available:

```bash
uv add pyyaml
```

## Step 2: Create the YAML Tool Loader

Create `app/core/yaml_tools.py`:

```python
"""Load tools from YAML definitions."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Callable

import yaml
from pydantic import BaseModel, Field, create_model

from app.core.tool import Tool
from app.core.exceptions import ToolLoadError


def load_tools_from_yaml(
    yaml_path: Path | str,
    skill_name: str | None = None,
    connector: Any | None = None,
) -> list[Tool]:
    """Load tools from a tools.yaml file.

    Args:
        yaml_path: Path to tools.yaml file
        skill_name: Name of the skill (for module paths)
        connector: Optional connector to pass to tool implementations

    Returns:
        List of Tool instances

    Raises:
        ToolLoadError: If loading fails
    """
    yaml_path = Path(yaml_path)

    if not yaml_path.exists():
        raise ToolLoadError(f"tools.yaml not found: {yaml_path}")

    try:
        content = yaml.safe_load(yaml_path.read_text())
    except yaml.YAMLError as e:
        raise ToolLoadError(f"Invalid YAML in {yaml_path}: {e}") from e

    if not isinstance(content, dict):
        raise ToolLoadError("tools.yaml must be a dictionary with 'tools' key")

    tools_config = content.get("tools", [])
    if not isinstance(tools_config, list):
        raise ToolLoadError("'tools' must be a list")

    tools = []
    for tool_config in tools_config:
        try:
            tool = _build_tool(tool_config, skill_name, connector)
            tools.append(tool)
        except Exception as e:
            name = tool_config.get("name", "unknown")
            raise ToolLoadError(f"Failed to load tool '{name}': {e}") from e

    return tools


def _build_tool(
    config: dict[str, Any],
    skill_name: str | None,
    connector: Any | None,
) -> Tool:
    """Build a Tool instance from YAML configuration.

    Args:
        config: Tool configuration dictionary
        skill_name: Parent skill name
        connector: Optional connector

    Returns:
        Tool instance
    """
    # Validate required fields
    if "name" not in config:
        raise ToolLoadError("Tool missing required 'name' field")

    name = config["name"]
    description = config.get("description", f"Tool: {name}")
    parameters = config.get("parameters", [])

    # Build Pydantic input schema
    input_schema = _build_input_schema(name, parameters)

    # Get the implementation function
    if "implementation" in config:
        func = _load_implementation(config["implementation"], connector)
    elif "query_template" in config:
        func = _build_query_function(config["query_template"], connector)
    else:
        raise ToolLoadError(
            f"Tool '{name}' needs 'implementation' or 'query_template'"
        )

    return Tool(
        name=name,
        description=description,
        function=func,
        input_schema=input_schema,
    )


def _build_input_schema(
    tool_name: str,
    parameters: list[dict[str, Any]],
) -> type[BaseModel]:
    """Build a Pydantic model from parameter definitions.

    Args:
        tool_name: Name of the tool (for model naming)
        parameters: List of parameter configs

    Returns:
        Pydantic BaseModel class
    """
    # Build field definitions
    fields: dict[str, tuple[type, Any]] = {}

    for param in parameters:
        param_name = param["name"]
        param_type = _get_python_type(param.get("type", "string"))
        required = param.get("required", False)
        description = param.get("description", "")
        default = param.get("default")

        # Build field
        if required:
            field_default = ...  # Required field marker
        elif default is not None:
            field_default = Field(default=default, description=description)
        else:
            field_default = Field(default=None, description=description)
            param_type = param_type | None

        if required or default is None:
            fields[param_name] = (param_type, Field(description=description) if required else field_default)
        else:
            fields[param_name] = (param_type, field_default)

    # Handle nested objects
    for param in parameters:
        if param.get("type") == "object" and "properties" in param:
            nested_schema = _build_nested_schema(
                f"{tool_name}_{param['name']}",
                param["properties"],
            )
            fields[param["name"]] = (
                nested_schema if param.get("required") else nested_schema | None,
                Field(description=param.get("description", "")),
            )

    # Create dynamic model
    model_name = "".join(word.capitalize() for word in tool_name.split("_")) + "Input"
    return create_model(model_name, **fields)


def _build_nested_schema(
    name: str,
    properties: dict[str, Any],
) -> type[BaseModel]:
    """Build a nested Pydantic model from properties.

    Args:
        name: Model name
        properties: Property definitions

    Returns:
        Pydantic BaseModel class
    """
    fields: dict[str, tuple[type, Any]] = {}

    for prop_name, prop_config in properties.items():
        prop_type = _get_python_type(prop_config.get("type", "string"))
        description = prop_config.get("description", "")
        default = prop_config.get("default")

        if default is not None:
            fields[prop_name] = (prop_type, Field(default=default, description=description))
        else:
            fields[prop_name] = (prop_type | None, Field(default=None, description=description))

    return create_model(name, **fields)


def _get_python_type(type_str: str) -> type:
    """Convert YAML type string to Python type.

    Args:
        type_str: Type string from YAML (string, integer, number, boolean, array, object)

    Returns:
        Python type
    """
    type_map = {
        "string": str,
        "integer": int,
        "int": int,
        "number": float,
        "float": float,
        "boolean": bool,
        "bool": bool,
        "array": list,
        "list": list,
        "object": dict,
        "dict": dict,
    }

    return type_map.get(type_str.lower(), str)


def _load_implementation(
    implementation_path: str,
    connector: Any | None,
) -> Callable[..., Any]:
    """Load implementation function from module path.

    Args:
        implementation_path: Path like "app.skills.financial.tools:check_gl_balance"
        connector: Optional connector to inject

    Returns:
        Callable function

    Raises:
        ToolLoadError: If function cannot be loaded
    """
    if ":" not in implementation_path:
        raise ToolLoadError(
            f"Invalid implementation path '{implementation_path}'. "
            "Expected format: 'module.path:function_name'"
        )

    module_path, func_name = implementation_path.rsplit(":", 1)

    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        raise ToolLoadError(f"Cannot import module '{module_path}': {e}") from e

    if not hasattr(module, func_name):
        raise ToolLoadError(f"Function '{func_name}' not found in module '{module_path}'")

    func = getattr(module, func_name)

    if not callable(func):
        raise ToolLoadError(f"'{func_name}' is not callable")

    # If it's a class, instantiate with connector
    if isinstance(func, type):
        if connector:
            instance = func(connector)
        else:
            instance = func()
        # Assume it has a __call__ method
        if hasattr(instance, "__call__"):
            return instance
        raise ToolLoadError(f"Class '{func_name}' is not callable")

    # If function expects connector, create wrapper
    if connector and _function_wants_connector(func):
        return _wrap_with_connector(func, connector)

    return func


def _function_wants_connector(func: Callable) -> bool:
    """Check if a function has a 'connector' parameter."""
    import inspect

    sig = inspect.signature(func)
    return "connector" in sig.parameters


def _wrap_with_connector(func: Callable, connector: Any) -> Callable:
    """Wrap a function to inject connector."""
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, connector=connector, **kwargs)

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        return await func(*args, connector=connector, **kwargs)

    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return wrapper


def _build_query_function(
    query_template: str,
    connector: Any | None,
) -> Callable[..., Any]:
    """Build a function that executes a query template.

    This enables zero-code tools that just run SQL/OData queries.

    Args:
        query_template: SQL/OData query with {placeholders}
        connector: Connector to execute queries

    Returns:
        Async function that executes the query
    """
    if connector is None:
        raise ToolLoadError("Query template tools require a connector")

    async def execute_query(**kwargs: Any) -> dict[str, Any]:
        """Execute the query template with provided parameters."""
        # Simple string formatting (for basic templates)
        # Note: In production, use parameterized queries for security
        try:
            query = query_template.format(**kwargs)
        except KeyError as e:
            return {"error": f"Missing parameter: {e}"}

        try:
            # Try SQL execution first
            if hasattr(connector, "execute_sql"):
                results = await connector.execute_sql(query)
            elif hasattr(connector, "execute"):
                results = await connector.execute(query)
            else:
                return {"error": "Connector does not support query execution"}

            return {
                "query": query,
                "row_count": len(results),
                "rows": results[:100],  # Limit results
                "truncated": len(results) > 100,
            }
        except Exception as e:
            return {"error": str(e), "query": query}

    return execute_query


# Utility function for validation
def validate_tools_yaml(yaml_path: Path | str) -> dict[str, Any]:
    """Validate a tools.yaml file without loading implementations.

    Args:
        yaml_path: Path to tools.yaml

    Returns:
        Dict with 'valid', 'errors', 'warnings' keys
    """
    yaml_path = Path(yaml_path)
    errors = []
    warnings = []

    if not yaml_path.exists():
        return {
            "valid": False,
            "errors": [f"File not found: {yaml_path}"],
            "warnings": [],
        }

    try:
        content = yaml.safe_load(yaml_path.read_text())
    except yaml.YAMLError as e:
        return {
            "valid": False,
            "errors": [f"Invalid YAML: {e}"],
            "warnings": [],
        }

    if not isinstance(content, dict):
        errors.append("Root must be a dictionary")
        return {"valid": False, "errors": errors, "warnings": warnings}

    if "tools" not in content:
        errors.append("Missing 'tools' key")
        return {"valid": False, "errors": errors, "warnings": warnings}

    tools = content["tools"]
    if not isinstance(tools, list):
        errors.append("'tools' must be a list")
        return {"valid": False, "errors": errors, "warnings": warnings}

    seen_names = set()
    for i, tool in enumerate(tools):
        # Check name
        if "name" not in tool:
            errors.append(f"Tool at index {i} missing 'name'")
            continue

        name = tool["name"]
        if name in seen_names:
            errors.append(f"Duplicate tool name: '{name}'")
        seen_names.add(name)

        # Check description
        if "description" not in tool:
            warnings.append(f"Tool '{name}' missing description")

        # Check implementation or query_template
        has_impl = "implementation" in tool
        has_query = "query_template" in tool

        if not has_impl and not has_query:
            errors.append(f"Tool '{name}' needs 'implementation' or 'query_template'")

        if has_impl and has_query:
            warnings.append(f"Tool '{name}' has both implementation and query_template")

        # Validate parameters
        params = tool.get("parameters", [])
        if not isinstance(params, list):
            errors.append(f"Tool '{name}' parameters must be a list")
            continue

        param_names = set()
        for param in params:
            if "name" not in param:
                errors.append(f"Tool '{name}' has parameter without name")
                continue

            pname = param["name"]
            if pname in param_names:
                errors.append(f"Tool '{name}' has duplicate parameter: '{pname}'")
            param_names.add(pname)

            # Check type
            ptype = param.get("type", "string")
            valid_types = {"string", "integer", "int", "number", "float", "boolean", "bool", "array", "list", "object", "dict"}
            if ptype.lower() not in valid_types:
                warnings.append(f"Tool '{name}' parameter '{pname}' has unusual type: '{ptype}'")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }
```

## Step 3: Example tools.yaml

Create `app/skills/_templates/basic/tools.yaml`:

```yaml
# tools.yaml - Tool definitions for this skill
# Each tool needs: name, description, parameters, and either implementation or query_template

tools:
  # Tool with Python implementation
  - name: check_gl_balance
    description: |
      Check GL account balance for a specific period.
      Returns balance details including debit, credit, and net amounts.
    parameters:
      - name: account_number
        type: string
        required: true
        description: GL account number (e.g., "400000")
      - name: company_code
        type: string
        required: true
        description: SAP company code (e.g., "1000")
      - name: fiscal_year
        type: integer
        required: true
        description: Fiscal year (e.g., 2024)
      - name: period
        type: string
        required: false
        description: Specific period (e.g., "001"). If not specified, returns full year.
    implementation: app.skills.financial.tools:check_gl_balance

  # Tool with query template (zero-code)
  - name: get_cost_center_postings
    description: |
      Retrieve postings for a cost center within a date range.
      Returns list of documents with amounts and posting details.
    parameters:
      - name: cost_center
        type: string
        required: true
        description: Cost center ID
      - name: date_from
        type: string
        required: true
        description: Start date (YYYY-MM-DD)
      - name: date_to
        type: string
        required: true
        description: End date (YYYY-MM-DD)
    query_template: |
      SELECT document_number, posting_date, amount, currency, text
      FROM ZCOSTCENTER_POSTINGS
      WHERE cost_center = '{cost_center}'
        AND posting_date BETWEEN '{date_from}' AND '{date_to}'
      ORDER BY posting_date DESC

  # Tool with object parameter
  - name: compare_periods
    description: Compare financial metrics between two periods.
    parameters:
      - name: account
        type: string
        required: true
        description: GL account to compare
      - name: period_a
        type: object
        required: true
        description: First period definition
        properties:
          year:
            type: integer
            description: Fiscal year
          period:
            type: string
            description: Period number
      - name: period_b
        type: object
        required: true
        description: Second period definition
        properties:
          year:
            type: integer
            description: Fiscal year
          period:
            type: string
            description: Period number
    implementation: app.skills.financial.tools:compare_periods

  # Tool with array parameter
  - name: bulk_balance_check
    description: Check balances for multiple accounts at once.
    parameters:
      - name: accounts
        type: array
        required: true
        description: List of GL account numbers
      - name: company_code
        type: string
        required: true
        description: Company code
      - name: fiscal_year
        type: integer
        required: true
        description: Fiscal year
    implementation: app.skills.financial.tools:bulk_balance_check
```

## Step 4: Example Tool Implementations

Create `app/skills/_templates/basic/tools.py`:

```python
"""Tool implementations for the skill.

These functions are referenced by tools.yaml via the 'implementation' field.
"""

from typing import Any


async def check_gl_balance(
    account_number: str,
    company_code: str,
    fiscal_year: int,
    period: str | None = None,
    connector: Any | None = None,
) -> dict[str, Any]:
    """Check GL account balance.

    Args:
        account_number: GL account number
        company_code: SAP company code
        fiscal_year: Fiscal year
        period: Optional specific period
        connector: Database connector (injected)

    Returns:
        Balance information dict
    """
    if connector is None:
        return {"error": "No database connection available"}

    # Build query
    query = f"""
        SELECT
            account_number,
            company_code,
            fiscal_year,
            period,
            SUM(debit_amount) as total_debit,
            SUM(credit_amount) as total_credit,
            SUM(debit_amount) - SUM(credit_amount) as balance,
            currency
        FROM GL_BALANCES
        WHERE account_number = '{account_number}'
          AND company_code = '{company_code}'
          AND fiscal_year = {fiscal_year}
    """

    if period:
        query += f" AND period = '{period}'"

    query += " GROUP BY account_number, company_code, fiscal_year, period, currency"

    try:
        results = await connector.execute_sql(query)
        return {
            "account": account_number,
            "company": company_code,
            "fiscal_year": fiscal_year,
            "period": period or "full_year",
            "balances": results,
            "record_count": len(results),
        }
    except Exception as e:
        return {"error": str(e)}


async def compare_periods(
    account: str,
    period_a: dict[str, Any],
    period_b: dict[str, Any],
    connector: Any | None = None,
) -> dict[str, Any]:
    """Compare account balance between two periods.

    Args:
        account: GL account number
        period_a: First period {year, period}
        period_b: Second period {year, period}
        connector: Database connector

    Returns:
        Comparison results
    """
    if connector is None:
        return {"error": "No database connection available"}

    # Get balance for period A
    result_a = await check_gl_balance(
        account_number=account,
        company_code="1000",  # Default
        fiscal_year=period_a["year"],
        period=period_a.get("period"),
        connector=connector,
    )

    # Get balance for period B
    result_b = await check_gl_balance(
        account_number=account,
        company_code="1000",
        fiscal_year=period_b["year"],
        period=period_b.get("period"),
        connector=connector,
    )

    # Calculate difference
    balance_a = sum(b.get("balance", 0) for b in result_a.get("balances", []))
    balance_b = sum(b.get("balance", 0) for b in result_b.get("balances", []))
    difference = balance_b - balance_a
    pct_change = (difference / balance_a * 100) if balance_a else 0

    return {
        "account": account,
        "period_a": period_a,
        "period_b": period_b,
        "balance_a": balance_a,
        "balance_b": balance_b,
        "difference": difference,
        "percent_change": round(pct_change, 2),
    }


async def bulk_balance_check(
    accounts: list[str],
    company_code: str,
    fiscal_year: int,
    connector: Any | None = None,
) -> dict[str, Any]:
    """Check balances for multiple accounts.

    Args:
        accounts: List of account numbers
        company_code: Company code
        fiscal_year: Fiscal year
        connector: Database connector

    Returns:
        Dict with balances for all accounts
    """
    if connector is None:
        return {"error": "No database connection available"}

    results = {}
    for account in accounts:
        result = await check_gl_balance(
            account_number=account,
            company_code=company_code,
            fiscal_year=fiscal_year,
            connector=connector,
        )
        results[account] = result

    return {
        "company_code": company_code,
        "fiscal_year": fiscal_year,
        "accounts_checked": len(accounts),
        "results": results,
    }
```

## Testing

Create `tests/test_yaml_tools.py`:

```python
"""Tests for YAML tool loader."""

import pytest
from pathlib import Path

from app.core.yaml_tools import (
    load_tools_from_yaml,
    validate_tools_yaml,
    _build_input_schema,
    _get_python_type,
)
from app.core.exceptions import ToolLoadError


@pytest.fixture
def basic_tools_yaml(tmp_path):
    """Create a basic tools.yaml for testing."""
    content = """
tools:
  - name: simple_tool
    description: A simple test tool
    parameters:
      - name: param1
        type: string
        required: true
        description: First parameter
      - name: param2
        type: integer
        required: false
        description: Second parameter
    implementation: tests.fixtures.mock_tools:simple_function
"""
    yaml_file = tmp_path / "tools.yaml"
    yaml_file.write_text(content)
    return yaml_file


class TestValidateToolsYaml:
    def test_valid_yaml(self, basic_tools_yaml):
        result = validate_tools_yaml(basic_tools_yaml)
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_missing_file(self, tmp_path):
        result = validate_tools_yaml(tmp_path / "nonexistent.yaml")
        assert result["valid"] is False
        assert "not found" in result["errors"][0].lower()

    def test_missing_name(self, tmp_path):
        yaml_file = tmp_path / "tools.yaml"
        yaml_file.write_text("""
tools:
  - description: Tool without name
    implementation: some.module:func
""")
        result = validate_tools_yaml(yaml_file)
        assert result["valid"] is False
        assert any("missing 'name'" in e for e in result["errors"])

    def test_duplicate_names(self, tmp_path):
        yaml_file = tmp_path / "tools.yaml"
        yaml_file.write_text("""
tools:
  - name: duplicate
    description: First
    implementation: mod:func
  - name: duplicate
    description: Second
    implementation: mod:func2
""")
        result = validate_tools_yaml(yaml_file)
        assert result["valid"] is False
        assert any("duplicate" in e.lower() for e in result["errors"])


class TestBuildInputSchema:
    def test_basic_parameters(self):
        params = [
            {"name": "name", "type": "string", "required": True, "description": "Name"},
            {"name": "count", "type": "integer", "required": False, "description": "Count"},
        ]

        schema = _build_input_schema("test_tool", params)

        assert schema.__name__ == "TestToolInput"
        assert "name" in schema.model_fields
        assert "count" in schema.model_fields

    def test_all_types(self):
        params = [
            {"name": "s", "type": "string", "required": True},
            {"name": "i", "type": "integer", "required": True},
            {"name": "f", "type": "number", "required": True},
            {"name": "b", "type": "boolean", "required": True},
            {"name": "a", "type": "array", "required": True},
        ]

        schema = _build_input_schema("type_test", params)

        # Verify all fields exist
        assert len(schema.model_fields) == 5


class TestGetPythonType:
    def test_string(self):
        assert _get_python_type("string") == str

    def test_integer(self):
        assert _get_python_type("integer") == int
        assert _get_python_type("int") == int

    def test_number(self):
        assert _get_python_type("number") == float
        assert _get_python_type("float") == float

    def test_boolean(self):
        assert _get_python_type("boolean") == bool
        assert _get_python_type("bool") == bool

    def test_array(self):
        assert _get_python_type("array") == list

    def test_unknown_defaults_to_string(self):
        assert _get_python_type("unknown") == str
```

## Summary

You've implemented:

1. **load_tools_from_yaml()** - Main function to load tools from YAML
2. **Dynamic schema generation** - Creates Pydantic models from YAML parameter definitions
3. **Query templates** - Zero-code tools that execute SQL/OData queries
4. **Implementation loading** - Imports Python functions dynamically
5. **Validation** - Checks YAML structure before loading

## Query Template Security Note

The simple string formatting in `_build_query_function` is for demonstration. For production:

```python
# Use parameterized queries instead of string formatting
async def execute_query(**kwargs):
    # Build parameterized query
    query = "SELECT * FROM table WHERE col = $1"
    params = [kwargs["value"]]
    return await connector.execute(query, params)
```

## Next Steps

- Implement the [Skill CLI](04_SKILL_CLI.md) for managing skills
- Create the [OpenAPI Tool Generator](05_OPENAPI_TOOL_GENERATOR.md)
