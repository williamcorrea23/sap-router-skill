# Guide 6: Query Templates

This guide explains how to implement query templates that enable zero-code tool definitions for simple database queries.

## Overview

Query templates allow you to define tools entirely in YAML without writing Python:

```yaml
tools:
  - name: get_gl_balances
    description: Get GL account balances for a period
    parameters:
      - name: account
        type: string
        required: true
      - name: fiscal_year
        type: integer
        required: true
    query_template: |
      SELECT account, period, balance
      FROM GL_BALANCES
      WHERE account = '{account}'
        AND fiscal_year = {fiscal_year}
```

The system automatically:
1. Validates parameters
2. Substitutes values into the template
3. Executes via the configured connector
4. Returns formatted results

## Step 1: Create Template Engine

Create `app/core/query_template.py`:

```python
"""Query template engine for zero-code tools."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable
from string import Template

from pydantic import BaseModel, Field, create_model

from app.core.exceptions import ToolLoadError


@dataclass
class QueryTemplate:
    """A query template with parameter substitution."""

    template: str
    connector_type: str = "datasphere"
    result_limit: int = 100
    timeout: int = 60

    # Parsed from template
    _parameters: list[str] = field(default_factory=list, init=False)
    _optional_blocks: list[tuple[str, str]] = field(default_factory=list, init=False)

    def __post_init__(self):
        """Parse template to extract parameters."""
        self._parse_template()

    def _parse_template(self) -> None:
        """Extract parameter names and optional blocks from template."""
        # Find simple parameters: {param_name}
        simple_params = re.findall(r"\{(\w+)\}", self.template)
        self._parameters = list(set(simple_params))

        # Find optional/conditional blocks: {% if param %}...{% endif %}
        optional_pattern = r"\{%\s*if\s+(\w+)\s*%\}(.*?)\{%\s*endif\s*%\}"
        self._optional_blocks = re.findall(optional_pattern, self.template, re.DOTALL)

    def render(self, **kwargs: Any) -> str:
        """Render the template with provided parameters.

        Args:
            **kwargs: Parameter values

        Returns:
            Rendered query string

        Raises:
            ToolLoadError: If required parameter is missing
        """
        result = self.template

        # Process conditional blocks first
        for param_name, block_content in self._optional_blocks:
            pattern = r"\{%\s*if\s+" + param_name + r"\s*%\}.*?\{%\s*endif\s*%\}"

            if kwargs.get(param_name) is not None:
                # Include block content with parameter substituted
                rendered_block = block_content.format(**kwargs)
                result = re.sub(pattern, rendered_block, result, flags=re.DOTALL)
            else:
                # Remove entire block
                result = re.sub(pattern, "", result, flags=re.DOTALL)

        # Substitute remaining parameters
        for param in self._parameters:
            if param not in kwargs and param not in [b[0] for b in self._optional_blocks]:
                raise ToolLoadError(f"Missing required parameter: {param}")

            placeholder = "{" + param + "}"
            value = kwargs.get(param, "")

            # Handle different types
            if isinstance(value, str):
                # Escape single quotes for SQL
                value = value.replace("'", "''")
            elif isinstance(value, bool):
                value = "true" if value else "false"
            elif value is None:
                value = "NULL"

            result = result.replace(placeholder, str(value))

        # Clean up extra whitespace
        result = re.sub(r"\n\s*\n", "\n", result)
        result = result.strip()

        return result

    @property
    def parameters(self) -> list[str]:
        """Get list of parameter names."""
        return self._parameters.copy()

    @property
    def optional_parameters(self) -> list[str]:
        """Get list of optional parameter names."""
        return [name for name, _ in self._optional_blocks]


class QueryTemplateExecutor:
    """Execute query templates against connectors."""

    def __init__(self, connector: Any):
        """Initialize with a database connector.

        Args:
            connector: Async database connector with execute_sql method
        """
        self.connector = connector

    async def execute(
        self,
        template: QueryTemplate,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Execute a query template.

        Args:
            template: Query template to execute
            **kwargs: Parameter values

        Returns:
            Result dictionary with rows and metadata
        """
        try:
            query = template.render(**kwargs)
        except Exception as e:
            return {"error": f"Template rendering failed: {e}", "rows": []}

        try:
            # Execute query
            if hasattr(self.connector, "execute_sql"):
                results = await self.connector.execute_sql(query)
            elif hasattr(self.connector, "execute"):
                results = await self.connector.execute(query)
            else:
                return {"error": "Connector does not support query execution", "rows": []}

            # Apply result limit
            truncated = len(results) > template.result_limit
            results = results[:template.result_limit]

            return {
                "query": query,
                "row_count": len(results),
                "rows": results,
                "truncated": truncated,
            }

        except Exception as e:
            return {
                "error": str(e),
                "query": query,
                "rows": [],
            }


def build_query_function(
    template_str: str,
    connector: Any,
    connector_type: str = "datasphere",
    result_limit: int = 100,
) -> Callable[..., Any]:
    """Build an async function from a query template.

    This is used by the YAML tool loader to create tool functions.

    Args:
        template_str: SQL/query template string
        connector: Database connector
        connector_type: Type of connector
        result_limit: Maximum results to return

    Returns:
        Async function that executes the query
    """
    template = QueryTemplate(
        template=template_str,
        connector_type=connector_type,
        result_limit=result_limit,
    )
    executor = QueryTemplateExecutor(connector)

    async def query_function(**kwargs: Any) -> dict[str, Any]:
        """Execute the query template with provided parameters."""
        return await executor.execute(template, **kwargs)

    return query_function


def build_schema_from_template(
    template_str: str,
    parameter_configs: list[dict[str, Any]] | None = None,
) -> type[BaseModel]:
    """Build Pydantic schema from template parameters.

    Args:
        template_str: Query template string
        parameter_configs: Optional parameter configurations from YAML

    Returns:
        Pydantic BaseModel class
    """
    template = QueryTemplate(template=template_str)

    # Build parameter config lookup
    config_map = {}
    if parameter_configs:
        for config in parameter_configs:
            config_map[config["name"]] = config

    fields: dict[str, tuple[type, Any]] = {}

    for param in template.parameters:
        config = config_map.get(param, {})

        # Determine type
        param_type_str = config.get("type", "string")
        param_type = _get_python_type(param_type_str)

        # Determine if required (not in optional blocks)
        is_optional = param in template.optional_parameters
        required = config.get("required", not is_optional)

        description = config.get("description", f"Parameter: {param}")

        if required:
            fields[param] = (param_type, Field(description=description))
        else:
            fields[param] = (param_type | None, Field(default=None, description=description))

    return create_model("QueryInput", **fields)


def _get_python_type(type_str: str) -> type:
    """Convert type string to Python type."""
    type_map = {
        "string": str,
        "integer": int,
        "int": int,
        "number": float,
        "float": float,
        "boolean": bool,
        "bool": bool,
        "date": str,  # Keep as string for SQL compatibility
        "datetime": str,
        "array": list,
        "list": list,
    }
    return type_map.get(type_str.lower(), str)


# Jinja2-style template support (optional, more powerful)
class AdvancedQueryTemplate:
    """Query template with Jinja2-style syntax support.

    Supports:
    - {% if condition %}...{% endif %}
    - {% for item in items %}...{% endfor %}
    - {{ variable | filter }}
    """

    def __init__(self, template: str):
        self.template = template
        self._jinja_env = None

    def _get_jinja_env(self):
        """Lazy-load Jinja2 environment."""
        if self._jinja_env is None:
            try:
                from jinja2 import Environment, BaseLoader
                self._jinja_env = Environment(
                    loader=BaseLoader(),
                    autoescape=False,
                    variable_start_string="{{",
                    variable_end_string="}}",
                    block_start_string="{%",
                    block_end_string="%}",
                )
                # Add SQL-safe filter
                self._jinja_env.filters["sql_escape"] = lambda s: str(s).replace("'", "''")
            except ImportError:
                raise ToolLoadError("Jinja2 required for advanced templates: pip install jinja2")
        return self._jinja_env

    def render(self, **kwargs: Any) -> str:
        """Render template with Jinja2."""
        env = self._get_jinja_env()
        template = env.from_string(self.template)
        return template.render(**kwargs)
```

## Step 2: Update YAML Tool Loader

Update `app/core/yaml_tools.py` to use query templates:

```python
# Add to existing yaml_tools.py

from app.core.query_template import (
    build_query_function,
    build_schema_from_template,
    QueryTemplate,
)


def _build_tool(
    config: dict[str, Any],
    skill_name: str | None,
    connector: Any | None,
) -> Tool:
    """Build a Tool instance from YAML configuration."""
    name = config["name"]
    description = config.get("description", f"Tool: {name}")
    parameters = config.get("parameters", [])

    # Check for query template
    if "query_template" in config:
        if connector is None:
            raise ToolLoadError(f"Tool '{name}' has query_template but no connector")

        template_str = config["query_template"]

        # Build function from template
        func = build_query_function(
            template_str=template_str,
            connector=connector,
            connector_type=config.get("connector", "datasphere"),
            result_limit=config.get("result_limit", 100),
        )

        # Build schema from template + parameter configs
        input_schema = build_schema_from_template(template_str, parameters)

    elif "implementation" in config:
        # Existing implementation loading logic
        func = _load_implementation(config["implementation"], connector)
        input_schema = _build_input_schema(name, parameters)

    else:
        raise ToolLoadError(f"Tool '{name}' needs 'implementation' or 'query_template'")

    return Tool(
        name=name,
        description=description,
        function=func,
        input_schema=input_schema,
    )
```

## Step 3: Example tools.yaml with Templates

```yaml
# app/skills/financial/tools.yaml
tools:
  # Simple query template
  - name: get_gl_balances
    description: |
      Get GL account balances for a specific fiscal year.
      Returns period-level balances with debit/credit breakdown.
    parameters:
      - name: account
        type: string
        required: true
        description: GL account number (e.g., "400000")
      - name: company_code
        type: string
        required: true
        description: Company code (e.g., "1000")
      - name: fiscal_year
        type: integer
        required: true
        description: Fiscal year (e.g., 2024)
    query_template: |
      SELECT
        account_number,
        company_code,
        fiscal_year,
        period,
        SUM(debit_amount) as debit,
        SUM(credit_amount) as credit,
        SUM(debit_amount - credit_amount) as balance,
        currency
      FROM GL_LINE_ITEMS
      WHERE account_number = '{account}'
        AND company_code = '{company_code}'
        AND fiscal_year = {fiscal_year}
      GROUP BY account_number, company_code, fiscal_year, period, currency
      ORDER BY period
    result_limit: 100

  # Query with optional parameters
  - name: search_cost_postings
    description: |
      Search cost center postings with optional filters.
      Can filter by cost center, date range, and amount threshold.
    parameters:
      - name: company_code
        type: string
        required: true
        description: Company code
      - name: cost_center
        type: string
        required: false
        description: Cost center (optional, searches all if not specified)
      - name: date_from
        type: string
        required: false
        description: Start date YYYY-MM-DD (optional)
      - name: date_to
        type: string
        required: false
        description: End date YYYY-MM-DD (optional)
      - name: min_amount
        type: number
        required: false
        description: Minimum amount filter (optional)
    query_template: |
      SELECT
        document_number,
        cost_center,
        posting_date,
        amount,
        currency,
        cost_element,
        description
      FROM COST_CENTER_POSTINGS
      WHERE company_code = '{company_code}'
        {% if cost_center %}AND cost_center = '{cost_center}'{% endif %}
        {% if date_from %}AND posting_date >= '{date_from}'{% endif %}
        {% if date_to %}AND posting_date <= '{date_to}'{% endif %}
        {% if min_amount %}AND ABS(amount) >= {min_amount}{% endif %}
      ORDER BY posting_date DESC
    result_limit: 500

  # Aggregation query
  - name: summarize_by_cost_element
    description: Summarize postings by cost element for analysis
    parameters:
      - name: cost_center
        type: string
        required: true
        description: Cost center to analyze
      - name: fiscal_year
        type: integer
        required: true
        description: Fiscal year
    query_template: |
      SELECT
        cost_element,
        cost_element_name,
        COUNT(*) as posting_count,
        SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as total_debit,
        SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as total_credit,
        SUM(amount) as net_amount
      FROM COST_CENTER_POSTINGS
      WHERE cost_center = '{cost_center}'
        AND fiscal_year = {fiscal_year}
      GROUP BY cost_element, cost_element_name
      ORDER BY ABS(SUM(amount)) DESC

  # Complex query with joins
  - name: reconcile_intercompany
    description: |
      Reconcile intercompany balances between two company codes.
      Identifies discrepancies in IC postings.
    parameters:
      - name: company_a
        type: string
        required: true
        description: First company code
      - name: company_b
        type: string
        required: true
        description: Second company code
      - name: fiscal_year
        type: integer
        required: true
        description: Fiscal year to reconcile
    query_template: |
      WITH company_a_balances AS (
        SELECT
          trading_partner,
          SUM(amount) as balance
        FROM IC_POSTINGS
        WHERE company_code = '{company_a}'
          AND trading_partner = '{company_b}'
          AND fiscal_year = {fiscal_year}
        GROUP BY trading_partner
      ),
      company_b_balances AS (
        SELECT
          trading_partner,
          SUM(amount) as balance
        FROM IC_POSTINGS
        WHERE company_code = '{company_b}'
          AND trading_partner = '{company_a}'
          AND fiscal_year = {fiscal_year}
        GROUP BY trading_partner
      )
      SELECT
        '{company_a}' as company_a,
        '{company_b}' as company_b,
        COALESCE(a.balance, 0) as company_a_balance,
        COALESCE(b.balance, 0) as company_b_balance,
        COALESCE(a.balance, 0) + COALESCE(b.balance, 0) as difference
      FROM company_a_balances a
      FULL OUTER JOIN company_b_balances b ON 1=1
```

## Step 4: Security Considerations

Update `app/core/query_template.py` to add security:

```python
class SecureQueryTemplate(QueryTemplate):
    """Query template with SQL injection protection."""

    # Dangerous patterns to reject
    DANGEROUS_PATTERNS = [
        r";\s*DROP\s+",
        r";\s*DELETE\s+",
        r";\s*UPDATE\s+",
        r";\s*INSERT\s+",
        r";\s*ALTER\s+",
        r";\s*CREATE\s+",
        r";\s*TRUNCATE\s+",
        r"--",  # SQL comments
        r"/\*",  # Block comments
        r"UNION\s+SELECT",
        r"INTO\s+OUTFILE",
        r"INTO\s+DUMPFILE",
    ]

    def render(self, **kwargs: Any) -> str:
        """Render with security validation."""
        # Validate parameter values
        for name, value in kwargs.items():
            if isinstance(value, str):
                self._validate_string_param(name, value)

        # Render template
        result = super().render(**kwargs)

        # Validate final query
        self._validate_query(result)

        return result

    def _validate_string_param(self, name: str, value: str) -> None:
        """Check parameter value for injection attempts."""
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise ToolLoadError(
                    f"Potentially unsafe value in parameter '{name}'"
                )

    def _validate_query(self, query: str) -> None:
        """Validate the complete rendered query."""
        # Must be a SELECT statement
        query_upper = query.strip().upper()
        if not query_upper.startswith("SELECT") and not query_upper.startswith("WITH"):
            raise ToolLoadError("Only SELECT queries are allowed")

        # Check for dangerous patterns in final query
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                raise ToolLoadError("Query contains potentially unsafe patterns")
```

## Testing

Create `tests/test_query_template.py`:

```python
"""Tests for query template engine."""

import pytest

from app.core.query_template import (
    QueryTemplate,
    SecureQueryTemplate,
    build_query_function,
    build_schema_from_template,
)
from app.core.exceptions import ToolLoadError


class TestQueryTemplate:
    def test_simple_substitution(self):
        template = QueryTemplate(
            template="SELECT * FROM table WHERE id = '{id}'"
        )
        result = template.render(id="123")
        assert result == "SELECT * FROM table WHERE id = '123'"

    def test_multiple_parameters(self):
        template = QueryTemplate(
            template="SELECT * FROM t WHERE a = '{a}' AND b = {b}"
        )
        result = template.render(a="foo", b=42)
        assert "a = 'foo'" in result
        assert "b = 42" in result

    def test_optional_block_included(self):
        template = QueryTemplate(
            template="SELECT * FROM t WHERE 1=1 {% if name %}AND name = '{name}'{% endif %}"
        )
        result = template.render(name="test")
        assert "AND name = 'test'" in result

    def test_optional_block_excluded(self):
        template = QueryTemplate(
            template="SELECT * FROM t WHERE 1=1 {% if name %}AND name = '{name}'{% endif %}"
        )
        result = template.render()
        assert "AND name" not in result

    def test_escape_single_quotes(self):
        template = QueryTemplate(
            template="SELECT * FROM t WHERE name = '{name}'"
        )
        result = template.render(name="O'Brien")
        assert "O''Brien" in result

    def test_missing_required_param(self):
        template = QueryTemplate(
            template="SELECT * FROM t WHERE id = '{id}'"
        )
        with pytest.raises(ToolLoadError, match="Missing required parameter"):
            template.render()

    def test_parameter_extraction(self):
        template = QueryTemplate(
            template="SELECT * FROM t WHERE a = '{a}' AND b = '{b}'"
        )
        assert set(template.parameters) == {"a", "b"}


class TestSecureQueryTemplate:
    def test_rejects_drop_statement(self):
        template = SecureQueryTemplate(
            template="SELECT * FROM t WHERE id = '{id}'"
        )
        with pytest.raises(ToolLoadError, match="unsafe"):
            template.render(id="1; DROP TABLE users;")

    def test_rejects_union_injection(self):
        template = SecureQueryTemplate(
            template="SELECT * FROM t WHERE id = '{id}'"
        )
        with pytest.raises(ToolLoadError, match="unsafe"):
            template.render(id="1 UNION SELECT password FROM users")

    def test_allows_safe_values(self):
        template = SecureQueryTemplate(
            template="SELECT * FROM t WHERE name = '{name}'"
        )
        result = template.render(name="John Doe")
        assert "John Doe" in result


class TestBuildSchemaFromTemplate:
    def test_extracts_parameters(self):
        template = "SELECT * FROM t WHERE a = '{a}' AND b = {b}"
        schema = build_schema_from_template(template)

        assert "a" in schema.model_fields
        assert "b" in schema.model_fields

    def test_uses_parameter_configs(self):
        template = "SELECT * FROM t WHERE id = '{id}'"
        configs = [
            {"name": "id", "type": "integer", "description": "Record ID"}
        ]
        schema = build_schema_from_template(template, configs)

        field = schema.model_fields["id"]
        assert field.description == "Record ID"
```

## Summary

You've implemented:

1. **QueryTemplate** - Template rendering with parameter substitution
2. **Optional blocks** - Conditional query sections with `{% if %}{% endif %}`
3. **SecureQueryTemplate** - SQL injection protection
4. **Auto-schema generation** - Pydantic models from templates
5. **Integration** - YAML loader support for query_template

## Security Best Practices

1. **Always use SecureQueryTemplate** in production
2. **Validate parameter types** before substitution
3. **Use parameterized queries** when connector supports them
4. **Limit result sets** to prevent memory issues
5. **Log queries** for audit purposes

## Next Steps

- Implement [Skill Migration](07_SKILL_MIGRATION.md) for converting existing skills
- Create the [Index document](00_INDEX.md) for navigation
