"""Query template engine for zero-code tools."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field, create_model

from app.core.exception import ToolLoadError


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
                raise ToolLoadError(f"Potentially unsafe value in parameter '{name}'")

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
            results = results[: template.result_limit]

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
    secure: bool = True,
) -> Callable[..., Any]:
    """Build an async function from a query template.

    This is used by the YAML tool loader to create tool functions.

    Args:
        template_str: SQL/query template string
        connector: Database connector
        connector_type: Type of connector
        result_limit: Maximum results to return
        secure: Whether to use SecureQueryTemplate

    Returns:
        Async function that executes the query
    """
    template_class = SecureQueryTemplate if secure else QueryTemplate
    template = template_class(
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
