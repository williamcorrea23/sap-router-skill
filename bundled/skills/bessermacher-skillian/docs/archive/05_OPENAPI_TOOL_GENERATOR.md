# Guide 5: OpenAPI Tool Generator

This guide explains how to automatically generate tools from OpenAPI specifications, enabling rapid integration with SAP APIs.

## Overview

Instead of manually writing tools for each API endpoint, you can:

1. Obtain the OpenAPI spec from SAP Datasphere or other APIs
2. Run the generator to create tools automatically
3. Optionally customize the generated tools

```bash
# Generate tools from OpenAPI spec
uv run skillian openapi generate specs/datasphere_api.yaml --skill datasphere

# Preview without writing
uv run skillian openapi preview specs/datasphere_api.yaml
```

## Step 1: Install Dependencies

```bash
uv add openapi-core pyyaml
```

## Step 2: Create the OpenAPI Loader

Create `app/core/openapi_loader.py`:

```python
"""Generate tools from OpenAPI specifications."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml
from pydantic import BaseModel, Field, create_model

from app.core.tool import Tool
from app.core.exceptions import ToolLoadError


@dataclass
class OpenAPIEndpoint:
    """Parsed OpenAPI endpoint information."""

    path: str
    method: str
    operation_id: str
    summary: str
    description: str
    parameters: list[dict[str, Any]]
    request_body: dict[str, Any] | None
    responses: dict[str, Any]
    tags: list[str]


@dataclass
class OpenAPISpec:
    """Parsed OpenAPI specification."""

    title: str
    version: str
    description: str
    servers: list[dict[str, str]]
    endpoints: list[OpenAPIEndpoint]
    schemas: dict[str, Any]

    @classmethod
    def from_file(cls, path: Path | str) -> "OpenAPISpec":
        """Load OpenAPI spec from file."""
        path = Path(path)

        if not path.exists():
            raise ToolLoadError(f"OpenAPI spec not found: {path}")

        content = path.read_text()

        if path.suffix in (".yaml", ".yml"):
            data = yaml.safe_load(content)
        else:
            import json
            data = json.loads(content)

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OpenAPISpec":
        """Parse OpenAPI spec from dictionary."""
        info = data.get("info", {})

        endpoints = []
        paths = data.get("paths", {})

        for path, path_item in paths.items():
            for method in ["get", "post", "put", "patch", "delete"]:
                if method not in path_item:
                    continue

                operation = path_item[method]

                endpoint = OpenAPIEndpoint(
                    path=path,
                    method=method.upper(),
                    operation_id=operation.get("operationId", _generate_operation_id(path, method)),
                    summary=operation.get("summary", ""),
                    description=operation.get("description", ""),
                    parameters=operation.get("parameters", []) + path_item.get("parameters", []),
                    request_body=operation.get("requestBody"),
                    responses=operation.get("responses", {}),
                    tags=operation.get("tags", []),
                )
                endpoints.append(endpoint)

        return cls(
            title=info.get("title", "API"),
            version=info.get("version", "1.0.0"),
            description=info.get("description", ""),
            servers=data.get("servers", []),
            endpoints=endpoints,
            schemas=data.get("components", {}).get("schemas", {}),
        )


def _generate_operation_id(path: str, method: str) -> str:
    """Generate operation ID from path and method."""
    # Remove path parameters and clean up
    clean_path = re.sub(r"\{[^}]+\}", "", path)
    clean_path = clean_path.strip("/").replace("/", "_")
    return f"{method}_{clean_path}"


class OpenAPIToolGenerator:
    """Generate Tool instances from OpenAPI specifications."""

    def __init__(
        self,
        spec: OpenAPISpec,
        base_url: str | None = None,
        http_client: Any | None = None,
    ):
        """Initialize the generator.

        Args:
            spec: Parsed OpenAPI specification
            base_url: Override base URL (uses spec servers if not provided)
            http_client: HTTP client for making requests (httpx.AsyncClient)
        """
        self.spec = spec
        self.base_url = base_url or self._get_base_url()
        self.http_client = http_client

    def _get_base_url(self) -> str:
        """Get base URL from spec servers."""
        if self.spec.servers:
            return self.spec.servers[0].get("url", "")
        return ""

    def generate_tools(
        self,
        filter_tags: list[str] | None = None,
        filter_methods: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> list[Tool]:
        """Generate tools from all endpoints.

        Args:
            filter_tags: Only include endpoints with these tags
            filter_methods: Only include these HTTP methods
            exclude_patterns: Regex patterns to exclude paths

        Returns:
            List of Tool instances
        """
        tools = []

        for endpoint in self.spec.endpoints:
            # Apply filters
            if filter_tags and not any(tag in endpoint.tags for tag in filter_tags):
                continue

            if filter_methods and endpoint.method not in filter_methods:
                continue

            if exclude_patterns:
                if any(re.search(p, endpoint.path) for p in exclude_patterns):
                    continue

            try:
                tool = self._generate_tool(endpoint)
                tools.append(tool)
            except Exception as e:
                print(f"Warning: Failed to generate tool for {endpoint.operation_id}: {e}")

        return tools

    def _generate_tool(self, endpoint: OpenAPIEndpoint) -> Tool:
        """Generate a Tool from an endpoint.

        Args:
            endpoint: OpenAPI endpoint

        Returns:
            Tool instance
        """
        # Build input schema
        input_schema = self._build_input_schema(endpoint)

        # Build description
        description = endpoint.summary or endpoint.description or f"{endpoint.method} {endpoint.path}"

        # Create the execution function
        func = self._create_endpoint_function(endpoint)

        return Tool(
            name=self._sanitize_name(endpoint.operation_id),
            description=description,
            function=func,
            input_schema=input_schema,
        )

    def _build_input_schema(self, endpoint: OpenAPIEndpoint) -> type[BaseModel]:
        """Build Pydantic model from endpoint parameters."""
        fields: dict[str, tuple[type, Any]] = {}

        # Process path and query parameters
        for param in endpoint.parameters:
            name = param["name"]
            required = param.get("required", False)
            schema = param.get("schema", {})
            description = param.get("description", "")

            param_type = self._schema_to_type(schema)

            if required:
                fields[name] = (param_type, Field(description=description))
            else:
                fields[name] = (param_type | None, Field(default=None, description=description))

        # Process request body
        if endpoint.request_body:
            content = endpoint.request_body.get("content", {})
            json_content = content.get("application/json", {})
            body_schema = json_content.get("schema", {})

            if body_schema:
                # Add body as a single parameter
                body_type = self._schema_to_model(f"{endpoint.operation_id}_body", body_schema)
                required = endpoint.request_body.get("required", False)

                if required:
                    fields["body"] = (body_type, Field(description="Request body"))
                else:
                    fields["body"] = (body_type | None, Field(default=None, description="Request body"))

        model_name = self._sanitize_name(endpoint.operation_id) + "Input"
        return create_model(model_name, **fields)

    def _schema_to_type(self, schema: dict[str, Any]) -> type:
        """Convert OpenAPI schema to Python type."""
        schema_type = schema.get("type", "string")

        type_map = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        return type_map.get(schema_type, str)

    def _schema_to_model(self, name: str, schema: dict[str, Any]) -> type[BaseModel]:
        """Convert complex schema to Pydantic model."""
        if schema.get("type") != "object":
            # Simple type, wrap in model
            return create_model(name, value=(self._schema_to_type(schema), ...))

        properties = schema.get("properties", {})
        required = schema.get("required", [])

        fields: dict[str, tuple[type, Any]] = {}

        for prop_name, prop_schema in properties.items():
            prop_type = self._schema_to_type(prop_schema)
            description = prop_schema.get("description", "")

            if prop_name in required:
                fields[prop_name] = (prop_type, Field(description=description))
            else:
                fields[prop_name] = (prop_type | None, Field(default=None, description=description))

        return create_model(name, **fields)

    def _create_endpoint_function(self, endpoint: OpenAPIEndpoint) -> Callable[..., Any]:
        """Create async function that calls the API endpoint."""
        path = endpoint.path
        method = endpoint.method.lower()
        base_url = self.base_url

        async def call_endpoint(**kwargs: Any) -> dict[str, Any]:
            """Execute API call."""
            import httpx

            # Build URL with path parameters
            url = base_url + path
            path_params = {}
            query_params = {}
            body = None

            for param in endpoint.parameters:
                name = param["name"]
                if name not in kwargs or kwargs[name] is None:
                    continue

                value = kwargs[name]

                if param.get("in") == "path":
                    path_params[name] = value
                elif param.get("in") == "query":
                    query_params[name] = value

            # Substitute path parameters
            for name, value in path_params.items():
                url = url.replace(f"{{{name}}}", str(value))

            # Extract body
            if "body" in kwargs and kwargs["body"] is not None:
                body = kwargs["body"]
                if hasattr(body, "model_dump"):
                    body = body.model_dump()

            # Make request
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.request(
                        method=method,
                        url=url,
                        params=query_params if query_params else None,
                        json=body,
                        timeout=60,
                    )

                    return {
                        "status_code": response.status_code,
                        "data": response.json() if response.content else None,
                        "url": str(response.url),
                    }
            except Exception as e:
                return {
                    "error": str(e),
                    "url": url,
                }

        return call_endpoint

    def _sanitize_name(self, name: str) -> str:
        """Convert operation ID to valid tool name."""
        # Replace non-alphanumeric with underscore
        name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
        # Remove consecutive underscores
        name = re.sub(r"_+", "_", name)
        # Remove leading/trailing underscores
        name = name.strip("_")
        # Lowercase
        return name.lower()

    def generate_yaml(
        self,
        filter_tags: list[str] | None = None,
        filter_methods: list[str] | None = None,
    ) -> str:
        """Generate tools.yaml content from spec.

        Args:
            filter_tags: Only include endpoints with these tags
            filter_methods: Only include these HTTP methods

        Returns:
            YAML string for tools.yaml
        """
        tools_config = {"tools": []}

        for endpoint in self.spec.endpoints:
            if filter_tags and not any(tag in endpoint.tags for tag in filter_tags):
                continue

            if filter_methods and endpoint.method not in filter_methods:
                continue

            tool_config = {
                "name": self._sanitize_name(endpoint.operation_id),
                "description": endpoint.summary or endpoint.description or f"{endpoint.method} {endpoint.path}",
                "parameters": [],
                "openapi_endpoint": {
                    "path": endpoint.path,
                    "method": endpoint.method,
                },
            }

            # Add parameters
            for param in endpoint.parameters:
                param_config = {
                    "name": param["name"],
                    "type": param.get("schema", {}).get("type", "string"),
                    "required": param.get("required", False),
                    "description": param.get("description", ""),
                }
                tool_config["parameters"].append(param_config)

            tools_config["tools"].append(tool_config)

        return yaml.dump(tools_config, default_flow_style=False, sort_keys=False)


def load_tools_from_openapi(
    spec_path: Path | str,
    base_url: str | None = None,
    filter_tags: list[str] | None = None,
    filter_methods: list[str] | None = None,
) -> list[Tool]:
    """Load tools directly from an OpenAPI spec file.

    Args:
        spec_path: Path to OpenAPI spec file (YAML or JSON)
        base_url: Override base URL
        filter_tags: Only include endpoints with these tags
        filter_methods: Only include these HTTP methods

    Returns:
        List of Tool instances
    """
    spec = OpenAPISpec.from_file(spec_path)
    generator = OpenAPIToolGenerator(spec, base_url=base_url)
    return generator.generate_tools(
        filter_tags=filter_tags,
        filter_methods=filter_methods,
    )
```

## Step 3: Add CLI Commands

Add to `app/cli/skill_commands.py` or create `app/cli/openapi_commands.py`:

```python
"""OpenAPI CLI commands."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax

openapi_app = typer.Typer(help="OpenAPI tool generation commands")
console = Console()


@openapi_app.command("preview")
def preview_spec(
    spec_path: Path = typer.Argument(..., help="Path to OpenAPI spec file"),
    tags: Optional[str] = typer.Option(None, "--tags", "-t", help="Filter by tags (comma-separated)"),
    methods: Optional[str] = typer.Option(None, "--methods", "-m", help="Filter by methods (comma-separated)"),
):
    """Preview tools that would be generated from an OpenAPI spec."""
    from app.core.openapi_loader import OpenAPISpec, OpenAPIToolGenerator

    if not spec_path.exists():
        console.print(f"[red]File not found: {spec_path}[/red]")
        raise typer.Exit(1)

    spec = OpenAPISpec.from_file(spec_path)

    console.print(f"[bold]API: {spec.title}[/bold] v{spec.version}")
    console.print(f"Description: {spec.description[:100]}..." if len(spec.description) > 100 else spec.description)
    console.print(f"Endpoints: {len(spec.endpoints)}")
    console.print()

    # Filter options
    filter_tags = tags.split(",") if tags else None
    filter_methods = [m.upper() for m in methods.split(",")] if methods else None

    generator = OpenAPIToolGenerator(spec)
    tools = generator.generate_tools(
        filter_tags=filter_tags,
        filter_methods=filter_methods,
    )

    table = Table(title=f"Generated Tools ({len(tools)})")
    table.add_column("Tool Name", style="cyan")
    table.add_column("Method", style="yellow")
    table.add_column("Path", style="white")
    table.add_column("Parameters", style="green")

    for endpoint in spec.endpoints:
        if filter_tags and not any(t in endpoint.tags for t in filter_tags):
            continue
        if filter_methods and endpoint.method not in filter_methods:
            continue

        param_count = len(endpoint.parameters)
        if endpoint.request_body:
            param_count += 1

        table.add_row(
            generator._sanitize_name(endpoint.operation_id),
            endpoint.method,
            endpoint.path[:40] + "..." if len(endpoint.path) > 40 else endpoint.path,
            str(param_count),
        )

    console.print(table)


@openapi_app.command("generate")
def generate_tools(
    spec_path: Path = typer.Argument(..., help="Path to OpenAPI spec file"),
    skill: str = typer.Option(..., "--skill", "-s", help="Skill to add tools to"),
    tags: Optional[str] = typer.Option(None, "--tags", "-t", help="Filter by tags"),
    methods: Optional[str] = typer.Option(None, "--methods", "-m", help="Filter by methods"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing"),
):
    """Generate tools.yaml from an OpenAPI spec."""
    from app.core.openapi_loader import OpenAPISpec, OpenAPIToolGenerator

    if not spec_path.exists():
        console.print(f"[red]File not found: {spec_path}[/red]")
        raise typer.Exit(1)

    skill_dir = Path("app/skills") / skill
    if not skill_dir.exists():
        console.print(f"[red]Skill '{skill}' not found[/red]")
        raise typer.Exit(1)

    spec = OpenAPISpec.from_file(spec_path)
    generator = OpenAPIToolGenerator(spec)

    filter_tags = tags.split(",") if tags else None
    filter_methods = [m.upper() for m in methods.split(",")] if methods else None

    yaml_content = generator.generate_yaml(
        filter_tags=filter_tags,
        filter_methods=filter_methods,
    )

    if dry_run:
        console.print("[bold]Generated tools.yaml:[/bold]")
        syntax = Syntax(yaml_content, "yaml", theme="monokai", line_numbers=True)
        console.print(syntax)
        return

    # Write to skill directory
    tools_yaml = skill_dir / "tools.yaml"

    if tools_yaml.exists():
        if not typer.confirm(f"Overwrite existing {tools_yaml}?"):
            raise typer.Exit(0)

    tools_yaml.write_text(yaml_content)
    console.print(f"[green]Generated {tools_yaml}[/green]")

    # Create stub tools.py
    tools_py = skill_dir / "tools.py"
    if not tools_py.exists():
        stub = '''"""Auto-generated tool stubs from OpenAPI spec."""

# TODO: Implement tool functions if custom logic is needed
# The OpenAPI generator will call endpoints directly if no implementation is specified
'''
        tools_py.write_text(stub)
        console.print(f"[green]Created {tools_py}[/green]")


@openapi_app.command("info")
def spec_info(
    spec_path: Path = typer.Argument(..., help="Path to OpenAPI spec file"),
):
    """Show information about an OpenAPI spec."""
    from app.core.openapi_loader import OpenAPISpec

    spec = OpenAPISpec.from_file(spec_path)

    console.print(f"[bold]Title:[/bold] {spec.title}")
    console.print(f"[bold]Version:[/bold] {spec.version}")
    console.print(f"[bold]Description:[/bold] {spec.description}")

    if spec.servers:
        console.print("\n[bold]Servers:[/bold]")
        for server in spec.servers:
            console.print(f"  - {server.get('url')}")

    # Collect tags
    all_tags = set()
    method_counts: dict[str, int] = {}
    for endpoint in spec.endpoints:
        all_tags.update(endpoint.tags)
        method_counts[endpoint.method] = method_counts.get(endpoint.method, 0) + 1

    console.print(f"\n[bold]Endpoints:[/bold] {len(spec.endpoints)}")
    for method, count in sorted(method_counts.items()):
        console.print(f"  {method}: {count}")

    if all_tags:
        console.print(f"\n[bold]Tags:[/bold] {', '.join(sorted(all_tags))}")

    console.print(f"\n[bold]Schemas:[/bold] {len(spec.schemas)}")
```

Register in main CLI:

```python
# app/cli/__init__.py
from app.cli.openapi_commands import openapi_app

app.add_typer(openapi_app, name="openapi", help="OpenAPI tool generation")
```

## Step 4: Example OpenAPI Spec

Create `specs/datasphere_api.yaml`:

```yaml
openapi: "3.0.3"
info:
  title: SAP Datasphere API
  description: API for querying SAP Datasphere views and tables
  version: "1.0.0"

servers:
  - url: https://{tenant}.datasphere.cloud.sap/api/v1
    variables:
      tenant:
        default: your-tenant

paths:
  /spaces/{spaceId}/entities:
    get:
      operationId: listEntities
      summary: List all entities in a space
      tags: [entities]
      parameters:
        - name: spaceId
          in: path
          required: true
          schema:
            type: string
          description: Space ID
      responses:
        "200":
          description: List of entities

  /spaces/{spaceId}/entities/{entityName}:
    get:
      operationId: getEntity
      summary: Get entity details
      tags: [entities]
      parameters:
        - name: spaceId
          in: path
          required: true
          schema:
            type: string
        - name: entityName
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Entity details

  /spaces/{spaceId}/entities/{entityName}/data:
    get:
      operationId: queryEntityData
      summary: Query entity data
      tags: [data]
      parameters:
        - name: spaceId
          in: path
          required: true
          schema:
            type: string
        - name: entityName
          in: path
          required: true
          schema:
            type: string
        - name: $select
          in: query
          required: false
          schema:
            type: string
          description: Fields to select (comma-separated)
        - name: $filter
          in: query
          required: false
          schema:
            type: string
          description: OData filter expression
        - name: $top
          in: query
          required: false
          schema:
            type: integer
          description: Maximum number of records
        - name: $skip
          in: query
          required: false
          schema:
            type: integer
          description: Number of records to skip
      responses:
        "200":
          description: Query results

  /spaces/{spaceId}/sql:
    post:
      operationId: executeSQL
      summary: Execute SQL query
      tags: [sql]
      parameters:
        - name: spaceId
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - query
              properties:
                query:
                  type: string
                  description: SQL query to execute
                parameters:
                  type: object
                  description: Query parameters
      responses:
        "200":
          description: Query results
```

## Usage Examples

```bash
# Preview what would be generated
uv run skillian openapi preview specs/datasphere_api.yaml

# Filter by tags
uv run skillian openapi preview specs/datasphere_api.yaml --tags data,sql

# Filter by methods
uv run skillian openapi preview specs/datasphere_api.yaml --methods GET,POST

# Generate tools for a skill
uv run skillian openapi generate specs/datasphere_api.yaml --skill datasphere

# Dry run (preview YAML output)
uv run skillian openapi generate specs/datasphere_api.yaml --skill datasphere --dry-run

# Show spec info
uv run skillian openapi info specs/datasphere_api.yaml
```

## Testing

Create `tests/test_openapi_loader.py`:

```python
"""Tests for OpenAPI loader."""

import pytest
from pathlib import Path

from app.core.openapi_loader import (
    OpenAPISpec,
    OpenAPIToolGenerator,
    load_tools_from_openapi,
)


@pytest.fixture
def sample_spec_content():
    return """
openapi: "3.0.3"
info:
  title: Test API
  version: "1.0.0"
paths:
  /items:
    get:
      operationId: listItems
      summary: List all items
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
      responses:
        "200":
          description: Success
  /items/{id}:
    get:
      operationId: getItem
      summary: Get item by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Success
"""


@pytest.fixture
def sample_spec(tmp_path, sample_spec_content):
    spec_file = tmp_path / "api.yaml"
    spec_file.write_text(sample_spec_content)
    return spec_file


class TestOpenAPISpec:
    def test_load_from_file(self, sample_spec):
        spec = OpenAPISpec.from_file(sample_spec)

        assert spec.title == "Test API"
        assert spec.version == "1.0.0"
        assert len(spec.endpoints) == 2

    def test_endpoint_parsing(self, sample_spec):
        spec = OpenAPISpec.from_file(sample_spec)

        list_endpoint = next(e for e in spec.endpoints if e.operation_id == "listItems")
        assert list_endpoint.method == "GET"
        assert list_endpoint.path == "/items"
        assert len(list_endpoint.parameters) == 1


class TestOpenAPIToolGenerator:
    def test_generate_tools(self, sample_spec):
        spec = OpenAPISpec.from_file(sample_spec)
        generator = OpenAPIToolGenerator(spec, base_url="https://api.example.com")

        tools = generator.generate_tools()

        assert len(tools) == 2
        assert any(t.name == "listitems" for t in tools)
        assert any(t.name == "getitem" for t in tools)

    def test_filter_by_method(self, sample_spec):
        spec = OpenAPISpec.from_file(sample_spec)
        generator = OpenAPIToolGenerator(spec)

        tools = generator.generate_tools(filter_methods=["GET"])
        assert len(tools) == 2

        tools = generator.generate_tools(filter_methods=["POST"])
        assert len(tools) == 0

    def test_generate_yaml(self, sample_spec):
        spec = OpenAPISpec.from_file(sample_spec)
        generator = OpenAPIToolGenerator(spec)

        yaml_content = generator.generate_yaml()

        assert "listitems" in yaml_content
        assert "getitem" in yaml_content
        assert "parameters:" in yaml_content
```

## Summary

You've implemented:

1. **OpenAPISpec** - Parser for OpenAPI specification files
2. **OpenAPIToolGenerator** - Converts endpoints to Tool instances
3. **Dynamic schema generation** - Creates Pydantic models from OpenAPI schemas
4. **YAML generation** - Creates tools.yaml from specs
5. **CLI commands** - preview, generate, info

## Next Steps

- Implement [Query Templates](06_QUERY_TEMPLATES.md) for zero-code tools
- Create [Skill Migration](07_SKILL_MIGRATION.md) guide
