"""Generate tools from OpenAPI specifications."""

from __future__ import annotations

import logging
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, create_model

from app.core.exception import ToolLoadError
from app.core.tool import Tool

logger = logging.getLogger(__name__)


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
    def from_file(cls, path: Path | str) -> OpenAPISpec:
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
    def from_dict(cls, data: dict[str, Any]) -> OpenAPISpec:
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
                logger.warning("Failed to generate tool for %s: %s", endpoint.operation_id, e)

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
        description = (
            endpoint.summary or endpoint.description or f"{endpoint.method} {endpoint.path}"
        )

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
                    fields["body"] = (
                        body_type | None,
                        Field(default=None, description="Request body"),
                    )

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
                fields[prop_name] = (
                    prop_type | None,
                    Field(default=None, description=description),
                )

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
        tools_config: dict[str, list[dict[str, Any]]] = {"tools": []}

        for endpoint in self.spec.endpoints:
            if filter_tags and not any(tag in endpoint.tags for tag in filter_tags):
                continue

            if filter_methods and endpoint.method not in filter_methods:
                continue

            tool_config: dict[str, Any] = {
                "name": self._sanitize_name(endpoint.operation_id),
                "description": endpoint.summary
                or endpoint.description
                or f"{endpoint.method} {endpoint.path}",
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
