# SAP Datasphere Integration Guide

This guide explains how to add a connector for SAP Datasphere and create a skill that uses it for data analysis.

## Overview

Integration involves three components:

```
┌─────────────────────────────────────────────────────────┐
│                     Skill Layer                          │
│  DatasphereSkill (tools + knowledge + system prompt)    │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                   Connector Layer                        │
│  DatasphereConnector (async queries, connection pool)   │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                SAP Datasphere API                        │
│  OData / SQL / REST endpoints                           │
└─────────────────────────────────────────────────────────┘
```

## Part 1: Create the Datasphere Connector

### Step 1.1: Add Configuration

Edit `app/config.py` to add Datasphere settings:

```python
class Settings(BaseSettings):
    # ... existing settings ...

    # SAP Datasphere
    datasphere_host: str | None = None
    datasphere_port: int = 443
    datasphere_space: str | None = None  # Datasphere space ID
    datasphere_client_id: str | None = None
    datasphere_client_secret: str | None = None
    datasphere_token_url: str | None = None  # OAuth token endpoint
    datasphere_timeout: int = 60
    datasphere_max_connections: int = 10

    @model_validator(mode="after")
    def validate_datasphere_config(self) -> Self:
        """Validate Datasphere config when connector is needed."""
        # Only validate if we have partial config (user intends to use it)
        if self.datasphere_host and not all([
            self.datasphere_client_id,
            self.datasphere_client_secret,
            self.datasphere_token_url,
        ]):
            raise ValueError(
                "DATASPHERE_CLIENT_ID, DATASPHERE_CLIENT_SECRET, and "
                "DATASPHERE_TOKEN_URL are required when DATASPHERE_HOST is set"
            )
        return self
```

### Step 1.2: Create the Connector

Create `app/connectors/datasphere.py`:

```python
"""SAP Datasphere connector with OAuth2 authentication."""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

import httpx
from pydantic import BaseModel


class DatasphereError(Exception):
    """Base exception for Datasphere operations."""
    pass


class DatasphereAuthError(DatasphereError):
    """Authentication failed."""
    pass


class DatasphereQueryError(DatasphereError):
    """Query execution failed."""
    pass


@dataclass
class OAuthToken:
    """OAuth2 token with expiry tracking."""

    access_token: str
    expires_at: datetime
    token_type: str = "Bearer"

    @property
    def is_expired(self) -> bool:
        """Check if token is expired (with 60s buffer)."""
        return datetime.now() >= self.expires_at - timedelta(seconds=60)


@dataclass
class DatasphereConnector:
    """Async connector for SAP Datasphere.

    Handles OAuth2 authentication and query execution via OData/SQL endpoints.
    Uses connection pooling for efficient resource usage.

    Example:
        connector = DatasphereConnector(
            host="your-tenant.datasphere.cloud.sap",
            space="YOUR_SPACE",
            client_id="...",
            client_secret="...",
            token_url="https://your-tenant.authentication.sap.hana.ondemand.com/oauth/token",
        )
        await connector.connect()
        results = await connector.execute_sql("SELECT * FROM view_name LIMIT 10")
        await connector.close()
    """

    host: str
    space: str
    client_id: str
    client_secret: str
    token_url: str
    port: int = 443
    timeout: int = 60
    max_connections: int = 10

    _client: httpx.AsyncClient | None = field(default=None, init=False, repr=False)
    _token: OAuthToken | None = field(default=None, init=False, repr=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)

    @property
    def base_url(self) -> str:
        """Base URL for Datasphere API."""
        return f"https://{self.host}:{self.port}"

    @property
    def odata_url(self) -> str:
        """OData service URL."""
        return f"{self.base_url}/api/v1/dwc/consumption/relational/{self.space}"

    @property
    def sql_url(self) -> str:
        """SQL execution endpoint."""
        return f"{self.base_url}/api/v1/dwc/sql/{self.space}"

    async def connect(self) -> None:
        """Initialize the HTTP client and authenticate."""
        if self._client is not None:
            return

        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            limits=httpx.Limits(
                max_connections=self.max_connections,
                max_keepalive_connections=self.max_connections // 2,
            ),
        )

        await self._refresh_token()

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
            self._token = None

    async def _refresh_token(self) -> None:
        """Obtain or refresh OAuth2 token."""
        if self._client is None:
            raise DatasphereError("Connector not connected. Call connect() first.")

        async with self._lock:
            # Double-check after acquiring lock
            if self._token and not self._token.is_expired:
                return

            try:
                response = await self._client.post(
                    self.token_url,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()

                data = response.json()
                expires_in = data.get("expires_in", 3600)

                self._token = OAuthToken(
                    access_token=data["access_token"],
                    expires_at=datetime.now() + timedelta(seconds=expires_in),
                    token_type=data.get("token_type", "Bearer"),
                )

            except httpx.HTTPStatusError as e:
                raise DatasphereAuthError(
                    f"Authentication failed: {e.response.status_code} - {e.response.text}"
                ) from e
            except Exception as e:
                raise DatasphereAuthError(f"Authentication failed: {e}") from e

    async def _get_headers(self) -> dict[str, str]:
        """Get request headers with valid auth token."""
        if self._token is None or self._token.is_expired:
            await self._refresh_token()

        return {
            "Authorization": f"{self._token.token_type} {self._token.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def execute_sql(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a SQL query against Datasphere.

        Args:
            query: SQL query string
            parameters: Optional query parameters for prepared statements

        Returns:
            List of result rows as dictionaries

        Raises:
            DatasphereQueryError: If query execution fails
        """
        if self._client is None:
            raise DatasphereError("Connector not connected. Call connect() first.")

        headers = await self._get_headers()

        payload = {"query": query}
        if parameters:
            payload["parameters"] = parameters

        try:
            response = await self._client.post(
                self.sql_url,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()

            data = response.json()
            return data.get("results", [])

        except httpx.HTTPStatusError as e:
            raise DatasphereQueryError(
                f"Query failed: {e.response.status_code} - {e.response.text}"
            ) from e
        except Exception as e:
            raise DatasphereQueryError(f"Query failed: {e}") from e

    async def execute_odata(
        self,
        entity: str,
        select: list[str] | None = None,
        filter_expr: str | None = None,
        top: int | None = None,
        skip: int | None = None,
        orderby: str | None = None,
    ) -> list[dict[str, Any]]:
        """Execute an OData query against a Datasphere view/table.

        Args:
            entity: Entity set name (view or table name)
            select: Fields to select
            filter_expr: OData filter expression
            top: Maximum number of results
            skip: Number of results to skip
            orderby: Order by expression

        Returns:
            List of result entities as dictionaries
        """
        if self._client is None:
            raise DatasphereError("Connector not connected. Call connect() first.")

        headers = await self._get_headers()

        # Build OData query parameters
        params: dict[str, str] = {}
        if select:
            params["$select"] = ",".join(select)
        if filter_expr:
            params["$filter"] = filter_expr
        if top:
            params["$top"] = str(top)
        if skip:
            params["$skip"] = str(skip)
        if orderby:
            params["$orderby"] = orderby

        url = f"{self.odata_url}/{entity}"

        try:
            response = await self._client.get(url, params=params, headers=headers)
            response.raise_for_status()

            data = response.json()
            return data.get("value", [])

        except httpx.HTTPStatusError as e:
            raise DatasphereQueryError(
                f"OData query failed: {e.response.status_code} - {e.response.text}"
            ) from e
        except Exception as e:
            raise DatasphereQueryError(f"OData query failed: {e}") from e

    async def get_metadata(self, entity: str | None = None) -> dict[str, Any]:
        """Retrieve metadata for entities in the space.

        Args:
            entity: Specific entity name, or None for all metadata

        Returns:
            Metadata dictionary
        """
        if self._client is None:
            raise DatasphereError("Connector not connected. Call connect() first.")

        headers = await self._get_headers()

        url = f"{self.odata_url}/$metadata"
        if entity:
            url = f"{self.odata_url}/{entity}/$metadata"

        try:
            response = await self._client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise DatasphereQueryError(
                f"Metadata query failed: {e.response.status_code}"
            ) from e

    async def list_entities(self) -> list[str]:
        """List available entities (views/tables) in the space."""
        metadata = await self.get_metadata()
        # Parse entity names from metadata
        # Structure depends on Datasphere's metadata format
        entities = []
        for schema in metadata.get("schemas", []):
            for entity in schema.get("entityTypes", []):
                entities.append(entity.get("name"))
        return entities

    async def health_check(self) -> bool:
        """Check if Datasphere connection is healthy."""
        try:
            if self._client is None:
                return False
            await self._refresh_token()
            return True
        except Exception:
            return False


# Factory function for dependency injection
def create_datasphere_connector(
    host: str,
    space: str,
    client_id: str,
    client_secret: str,
    token_url: str,
    **kwargs: Any,
) -> DatasphereConnector:
    """Create a Datasphere connector with the given configuration."""
    return DatasphereConnector(
        host=host,
        space=space,
        client_id=client_id,
        client_secret=client_secret,
        token_url=token_url,
        **kwargs,
    )
```

### Step 1.3: Add Connector to Dependencies

Edit `app/dependencies.py`:

```python
from app.connectors.datasphere import DatasphereConnector


@lru_cache
def get_datasphere_connector() -> DatasphereConnector | None:
    """Get cached Datasphere connector if configured."""
    settings = get_settings()

    if not settings.datasphere_host:
        return None

    return DatasphereConnector(
        host=settings.datasphere_host,
        space=settings.datasphere_space,
        client_id=settings.datasphere_client_id,
        client_secret=settings.datasphere_client_secret,
        token_url=settings.datasphere_token_url,
        port=settings.datasphere_port,
        timeout=settings.datasphere_timeout,
        max_connections=settings.datasphere_max_connections,
    )
```

### Step 1.4: Initialize Connector on Startup

Update `main.py` lifespan:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... existing startup code ...

    # Initialize Datasphere connector if configured
    datasphere = get_datasphere_connector()
    if datasphere:
        try:
            await datasphere.connect()
            logger.info("Datasphere connector initialized for space: %s", datasphere.space)
        except Exception as e:
            logger.warning("Datasphere initialization failed: %s", e)

    yield

    # ... existing shutdown code ...

    # Close Datasphere connector
    if datasphere:
        await datasphere.close()
        logger.debug("Datasphere connector closed")
```

---

## Part 2: Create the Datasphere Skill

### Step 2.1: Create Skill Directory Structure

```
app/skills/datasphere/
├── __init__.py
├── skill.py          # Main skill class
├── tools.py          # Tool implementations
└── knowledge/
    ├── datasphere_overview.md
    └── query_patterns.md
```

### Step 2.2: Define Tool Input Schemas and Implementations

Create `app/skills/datasphere/tools.py`:

```python
"""Tool implementations for Datasphere skill."""

from typing import Any

from pydantic import BaseModel, Field

from app.connectors.datasphere import DatasphereConnector, DatasphereQueryError


# ============================================================================
# Tool Input Schemas
# ============================================================================

class ListEntitiesInput(BaseModel):
    """Input for listing available entities."""
    pass


class QueryEntityInput(BaseModel):
    """Input for querying a Datasphere entity via OData."""

    entity: str = Field(
        description="Name of the entity (view/table) to query"
    )
    select: list[str] | None = Field(
        default=None,
        description="Fields to return. If not specified, all fields are returned."
    )
    filter_expr: str | None = Field(
        default=None,
        description="OData filter expression, e.g., \"CALMONTH eq '202401' and MATERIAL eq 'MAT001'\""
    )
    top: int | None = Field(
        default=100,
        description="Maximum number of rows to return (default: 100)"
    )
    orderby: str | None = Field(
        default=None,
        description="Order by field, e.g., 'AMOUNT desc'"
    )


class ExecuteSQLInput(BaseModel):
    """Input for executing raw SQL against Datasphere."""

    query: str = Field(
        description="SQL query to execute. Use SELECT statements only."
    )


class GetEntityMetadataInput(BaseModel):
    """Input for retrieving entity metadata."""

    entity: str = Field(
        description="Name of the entity to get metadata for"
    )


class CompareEntitiesInput(BaseModel):
    """Input for comparing data between two entities."""

    entity_a: str = Field(
        description="First entity name (reference)"
    )
    entity_b: str = Field(
        description="Second entity name (to compare)"
    )
    measure: str = Field(
        description="Measure/numeric field to compare"
    )
    group_by: list[str] | None = Field(
        default=None,
        description="Dimensions to group and align comparison on"
    )
    filter_expr: str | None = Field(
        default=None,
        description="OData filter to apply to both entities"
    )


# ============================================================================
# Tool Implementation Class
# ============================================================================

class DatasphereTools:
    """Tool implementations for Datasphere skill."""

    def __init__(self, connector: DatasphereConnector):
        self._connector = connector

    async def list_entities(self) -> dict[str, Any]:
        """List all available entities in the Datasphere space."""
        try:
            entities = await self._connector.list_entities()
            return {
                "entities": entities,
                "count": len(entities),
                "space": self._connector.space,
            }
        except DatasphereQueryError as e:
            return {"error": str(e), "entities": []}

    async def query_entity(
        self,
        entity: str,
        select: list[str] | None = None,
        filter_expr: str | None = None,
        top: int | None = 100,
        orderby: str | None = None,
    ) -> dict[str, Any]:
        """Query a Datasphere entity using OData."""
        try:
            results = await self._connector.execute_odata(
                entity=entity,
                select=select,
                filter_expr=filter_expr,
                top=top,
                orderby=orderby,
            )

            return {
                "entity": entity,
                "row_count": len(results),
                "rows": results,
                "truncated": len(results) == top,
                "filter_applied": filter_expr,
            }
        except DatasphereQueryError as e:
            return {
                "error": str(e),
                "entity": entity,
                "row_count": 0,
                "rows": [],
            }

    async def execute_sql(self, query: str) -> dict[str, Any]:
        """Execute a SQL query against Datasphere."""
        # Basic safety check - only allow SELECT
        query_upper = query.strip().upper()
        if not query_upper.startswith("SELECT"):
            return {
                "error": "Only SELECT queries are allowed for safety",
                "query": query,
                "rows": [],
            }

        try:
            results = await self._connector.execute_sql(query)
            return {
                "query": query,
                "row_count": len(results),
                "rows": results[:500],  # Limit response size
                "truncated": len(results) > 500,
            }
        except DatasphereQueryError as e:
            return {
                "error": str(e),
                "query": query,
                "rows": [],
            }

    async def get_entity_metadata(self, entity: str) -> dict[str, Any]:
        """Get metadata for a specific entity."""
        try:
            metadata = await self._connector.get_metadata(entity)
            return {
                "entity": entity,
                "metadata": metadata,
            }
        except DatasphereQueryError as e:
            return {
                "error": str(e),
                "entity": entity,
                "metadata": {},
            }

    async def compare_entities(
        self,
        entity_a: str,
        entity_b: str,
        measure: str,
        group_by: list[str] | None = None,
        filter_expr: str | None = None,
    ) -> dict[str, Any]:
        """Compare a measure between two entities."""
        try:
            # Query both entities
            select_fields = [measure]
            if group_by:
                select_fields = group_by + [measure]

            results_a = await self._connector.execute_odata(
                entity=entity_a,
                select=select_fields,
                filter_expr=filter_expr,
                top=1000,
            )

            results_b = await self._connector.execute_odata(
                entity=entity_b,
                select=select_fields,
                filter_expr=filter_expr,
                top=1000,
            )

            # Build comparison
            comparison = self._build_comparison(
                results_a, results_b, measure, group_by or []
            )

            return {
                "entity_a": entity_a,
                "entity_b": entity_b,
                "measure": measure,
                "group_by": group_by,
                "comparison": comparison,
                "summary": self._summarize_comparison(comparison, measure),
            }
        except DatasphereQueryError as e:
            return {
                "error": str(e),
                "entity_a": entity_a,
                "entity_b": entity_b,
            }

    def _build_comparison(
        self,
        results_a: list[dict],
        results_b: list[dict],
        measure: str,
        group_by: list[str],
    ) -> list[dict]:
        """Build comparison records between two result sets."""
        if not group_by:
            # Simple total comparison
            total_a = sum(r.get(measure, 0) or 0 for r in results_a)
            total_b = sum(r.get(measure, 0) or 0 for r in results_b)
            diff = total_b - total_a
            pct = (diff / total_a * 100) if total_a else 0

            return [{
                "value_a": total_a,
                "value_b": total_b,
                "difference": diff,
                "difference_pct": round(pct, 2),
            }]

        # Group-by comparison
        def make_key(row: dict) -> tuple:
            return tuple(row.get(dim) for dim in group_by)

        index_a = {make_key(r): r.get(measure, 0) for r in results_a}
        index_b = {make_key(r): r.get(measure, 0) for r in results_b}

        all_keys = set(index_a.keys()) | set(index_b.keys())
        comparison = []

        for key in sorted(all_keys):
            val_a = index_a.get(key, 0) or 0
            val_b = index_b.get(key, 0) or 0
            diff = val_b - val_a
            pct = (diff / val_a * 100) if val_a else 0

            record = {
                **dict(zip(group_by, key)),
                "value_a": val_a,
                "value_b": val_b,
                "difference": diff,
                "difference_pct": round(pct, 2),
            }
            comparison.append(record)

        return comparison

    def _summarize_comparison(
        self,
        comparison: list[dict],
        measure: str,
    ) -> dict[str, Any]:
        """Generate summary statistics for a comparison."""
        total_a = sum(c["value_a"] for c in comparison)
        total_b = sum(c["value_b"] for c in comparison)
        total_diff = total_b - total_a
        total_pct = (total_diff / total_a * 100) if total_a else 0

        mismatches = [c for c in comparison if abs(c["difference_pct"]) > 1]

        return {
            "total_a": total_a,
            "total_b": total_b,
            "total_difference": total_diff,
            "total_difference_pct": round(total_pct, 2),
            "records_compared": len(comparison),
            "mismatches_over_1pct": len(mismatches),
            "largest_differences": sorted(
                comparison, key=lambda x: abs(x["difference"]), reverse=True
            )[:5],
        }
```

### Step 2.3: Create the Skill Class

Create `app/skills/datasphere/skill.py`:

```python
"""SAP Datasphere skill for data analysis and comparison."""

from pathlib import Path

from app.core.tool import Tool
from app.connectors.datasphere import DatasphereConnector
from app.skills.datasphere.tools import (
    DatasphereTools,
    ListEntitiesInput,
    QueryEntityInput,
    ExecuteSQLInput,
    GetEntityMetadataInput,
    CompareEntitiesInput,
)


class DatasphereSkill:
    """Skill for querying and analyzing SAP Datasphere data.

    Provides tools for:
    - Listing available entities (views/tables)
    - Querying entities via OData
    - Executing SQL queries
    - Comparing data between entities
    - Retrieving metadata
    """

    def __init__(self, connector: DatasphereConnector):
        self._connector = connector
        self._tool_impl = DatasphereTools(connector)
        self._tools = self._build_tools()

    def _build_tools(self) -> list[Tool]:
        """Build the list of available tools."""
        return [
            Tool(
                name="ds_list_entities",
                description=(
                    "List all available entities (views and tables) in the "
                    "SAP Datasphere space. Use this first to discover what data "
                    "is available for querying."
                ),
                function=self._tool_impl.list_entities,
                input_schema=ListEntitiesInput,
            ),
            Tool(
                name="ds_query_entity",
                description=(
                    "Query a SAP Datasphere entity (view or table) using OData. "
                    "Supports field selection, filtering, ordering, and pagination. "
                    "Use this for exploring data and retrieving specific records."
                ),
                function=self._tool_impl.query_entity,
                input_schema=QueryEntityInput,
            ),
            Tool(
                name="ds_execute_sql",
                description=(
                    "Execute a SQL SELECT query against SAP Datasphere. "
                    "Use this for complex queries that require joins, "
                    "aggregations, or features not available via OData. "
                    "Only SELECT statements are allowed."
                ),
                function=self._tool_impl.execute_sql,
                input_schema=ExecuteSQLInput,
            ),
            Tool(
                name="ds_get_metadata",
                description=(
                    "Get metadata for a specific entity including field names, "
                    "data types, and descriptions. Use this to understand the "
                    "structure of an entity before querying."
                ),
                function=self._tool_impl.get_entity_metadata,
                input_schema=GetEntityMetadataInput,
            ),
            Tool(
                name="ds_compare_entities",
                description=(
                    "Compare a numeric measure between two entities. "
                    "Useful for data reconciliation, finding discrepancies, "
                    "and validating data across different sources or time periods. "
                    "Returns differences and percentage variances."
                ),
                function=self._tool_impl.compare_entities,
                input_schema=CompareEntitiesInput,
            ),
        ]

    @property
    def name(self) -> str:
        return "datasphere"

    @property
    def description(self) -> str:
        return (
            "SAP Datasphere skill for querying, analyzing, and comparing "
            "enterprise data stored in Datasphere views and tables."
        )

    @property
    def tools(self) -> list[Tool]:
        return self._tools

    @property
    def system_prompt(self) -> str:
        return """You are an expert in SAP Datasphere data analysis. When helping users:

1. **Discovery First**: Always start by listing available entities if the user
   doesn't specify which data to query. Use ds_list_entities to discover the schema.

2. **Understand Structure**: Before querying, use ds_get_metadata to understand
   field names, data types, and relationships.

3. **Query Efficiently**:
   - Use OData (ds_query_entity) for simple queries with filters
   - Use SQL (ds_execute_sql) for complex joins and aggregations
   - Always apply filters to avoid retrieving too much data

4. **Data Comparison**: When users want to reconcile or validate data:
   - Identify the reference entity and comparison entity
   - Determine the measure to compare and dimensions to align on
   - Use ds_compare_entities to find discrepancies
   - Explain differences clearly, focusing on significant variances

5. **SAP Terminology**: Users may use SAP terms like:
   - InfoObject → Dimension or Characteristic
   - Key Figure → Measure
   - InfoProvider → Entity/View
   - Request → Data load batch

6. **Common Analysis Patterns**:
   - Period-over-period comparison (filter by CALMONTH/FISCPER)
   - Source-to-target reconciliation
   - Aggregation verification (detail vs. summary)
   - Data quality checks (nulls, outliers)

Always explain your findings clearly and suggest next steps for investigation."""

    @property
    def knowledge_paths(self) -> list[str]:
        return [str(Path(__file__).parent / "knowledge")]

    def get_tool(self, name: str) -> Tool | None:
        for tool in self._tools:
            if tool.name == name:
                return tool
        return None
```

### Step 2.4: Create Knowledge Documents

Create `app/skills/datasphere/knowledge/datasphere_overview.md`:

```markdown
# SAP Datasphere Overview

SAP Datasphere is a cloud-based data management solution that provides:

## Key Concepts

### Spaces
- Isolated environments for organizing data assets
- Each space has its own set of views, tables, and connections
- Users query within their assigned space

### Data Entities
- **Views**: Virtualized data models combining multiple sources
- **Tables**: Physical storage of data within Datasphere
- **Remote Tables**: References to external data sources

### Common Field Patterns
- CALMONTH: Calendar month (YYYYMM)
- FISCPER: Fiscal period
- MATERIAL: Material number
- PLANT: Plant code
- CUSTOMER: Customer number
- AMOUNT: Monetary value
- QUANTITY: Numeric quantity

## Query Best Practices

1. Always filter by time dimensions to limit data volume
2. Use appropriate aggregation in SQL queries
3. Check for null values in key fields
4. Consider currency/unit conversions when comparing amounts
```

Create `app/skills/datasphere/knowledge/query_patterns.md`:

```markdown
# Common Query Patterns

## Period Filtering
```sql
SELECT * FROM view_name
WHERE CALMONTH BETWEEN '202401' AND '202412'
```

## Aggregation
```sql
SELECT MATERIAL, PLANT, SUM(AMOUNT) as TOTAL_AMOUNT
FROM sales_view
GROUP BY MATERIAL, PLANT
```

## OData Filters
- Equals: `MATERIAL eq 'MAT001'`
- Multiple: `MATERIAL eq 'MAT001' and PLANT eq '1000'`
- Contains: `contains(MATERIAL, 'MAT')`
- Greater than: `AMOUNT gt 1000`
- In list: `MATERIAL in ('MAT001', 'MAT002')`

## Reconciliation Pattern
Compare totals between source and target:
1. Query source with aggregation
2. Query target with same aggregation
3. Compare using ds_compare_entities
4. Investigate records with >1% variance
```

Create `app/skills/datasphere/__init__.py`:

```python
"""SAP Datasphere skill package."""

from app.skills.datasphere.skill import DatasphereSkill

__all__ = ["DatasphereSkill"]
```

### Step 2.5: Register the Skill

Update `app/dependencies.py`:

```python
from app.skills.datasphere import DatasphereSkill


@lru_cache
def get_datasphere_skill() -> DatasphereSkill | None:
    """Get cached Datasphere skill if connector is configured."""
    connector = get_datasphere_connector()
    if connector is None:
        return None
    return DatasphereSkill(connector)


@lru_cache
def get_skill_registry() -> SkillRegistry:
    """Get cached skill registry with all skills registered."""
    registry = SkillRegistry()

    # Register data analyst skill (always available)
    data_analyst = get_data_analyst_skill()
    registry.register(data_analyst)

    # Register Datasphere skill if configured
    datasphere = get_datasphere_skill()
    if datasphere:
        registry.register(datasphere)

    return registry
```

---

## Part 3: Environment Configuration

Create or update `.env`:

```bash
# .env
ENV=production
DEBUG=false

# LLM Configuration
LLM_PROVIDER=custom_openai  # or anthropic
CUSTOM_OPENAI_API_KEY=your-llm-api-key
CUSTOM_OPENAI_BASE_URL=https://your-llm-endpoint.com/v1
CUSTOM_OPENAI_CHAT_MODEL=your-model

# Database Configuration
DATABASE_URL=postgresql+asyncpg://skillian:password@dbhost:5432/skillian
VECTOR_COLLECTION_NAME=skillian_knowledge

# SAP Datasphere Configuration
DATASPHERE_HOST=your-tenant.datasphere.cloud.sap
DATASPHERE_PORT=443
DATASPHERE_SPACE=YOUR_SPACE_ID
DATASPHERE_CLIENT_ID=your-client-id
DATASPHERE_CLIENT_SECRET=your-client-secret
DATASPHERE_TOKEN_URL=https://your-tenant.authentication.sap.hana.ondemand.com/oauth/token
DATASPHERE_TIMEOUT=60
DATASPHERE_MAX_CONNECTIONS=10
```

---

## Part 4: Testing

### Unit Tests

Create `tests/test_datasphere_connector.py`:

```python
"""Tests for Datasphere connector."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from app.connectors.datasphere import (
    DatasphereConnector,
    DatasphereAuthError,
    DatasphereQueryError,
    OAuthToken,
)


@pytest.fixture
def connector():
    """Create test connector."""
    return DatasphereConnector(
        host="test.datasphere.cloud.sap",
        space="TEST_SPACE",
        client_id="test-client",
        client_secret="test-secret",
        token_url="https://test.auth.com/oauth/token",
    )


class TestOAuthToken:
    def test_is_expired_false(self):
        token = OAuthToken(
            access_token="test",
            expires_at=datetime.now() + timedelta(hours=1),
        )
        assert not token.is_expired

    def test_is_expired_true(self):
        token = OAuthToken(
            access_token="test",
            expires_at=datetime.now() - timedelta(seconds=1),
        )
        assert token.is_expired


class TestDatasphereConnector:
    def test_base_url(self, connector):
        assert connector.base_url == "https://test.datasphere.cloud.sap:443"

    def test_odata_url(self, connector):
        assert "TEST_SPACE" in connector.odata_url

    @pytest.mark.asyncio
    async def test_connect_creates_client(self, connector):
        with patch("app.connectors.datasphere.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance

            # Mock token response
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "access_token": "test-token",
                "expires_in": 3600,
            }
            mock_response.raise_for_status = MagicMock()
            mock_instance.post.return_value = mock_response

            await connector.connect()

            assert connector._client is not None
            assert connector._token is not None

    @pytest.mark.asyncio
    async def test_execute_sql_requires_select(self, connector):
        connector._client = AsyncMock()
        connector._token = OAuthToken(
            access_token="test",
            expires_at=datetime.now() + timedelta(hours=1),
        )

        result = await connector.execute_sql("DELETE FROM table")
        assert "error" in result
        assert "SELECT" in result["error"]
```

Create `tests/test_datasphere_skill.py`:

```python
"""Tests for Datasphere skill."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.skills.datasphere.skill import DatasphereSkill
from app.skills.datasphere.tools import DatasphereTools


@pytest.fixture
def mock_connector():
    connector = MagicMock()
    connector.space = "TEST_SPACE"
    connector.list_entities = AsyncMock(return_value=["view1", "view2"])
    connector.execute_odata = AsyncMock(return_value=[{"id": 1, "value": 100}])
    connector.execute_sql = AsyncMock(return_value=[{"id": 1, "value": 100}])
    return connector


@pytest.fixture
def skill(mock_connector):
    return DatasphereSkill(mock_connector)


class TestDatasphereSkill:
    def test_skill_name(self, skill):
        assert skill.name == "datasphere"

    def test_skill_has_tools(self, skill):
        assert len(skill.tools) == 5

    def test_tool_names(self, skill):
        tool_names = [t.name for t in skill.tools]
        assert "ds_list_entities" in tool_names
        assert "ds_query_entity" in tool_names
        assert "ds_execute_sql" in tool_names

    def test_get_tool(self, skill):
        tool = skill.get_tool("ds_list_entities")
        assert tool is not None
        assert tool.name == "ds_list_entities"

    def test_system_prompt_not_empty(self, skill):
        assert len(skill.system_prompt) > 100


class TestDatasphereTools:
    @pytest.mark.asyncio
    async def test_list_entities(self, mock_connector):
        tools = DatasphereTools(mock_connector)
        result = await tools.list_entities()

        assert result["count"] == 2
        assert "view1" in result["entities"]

    @pytest.mark.asyncio
    async def test_query_entity(self, mock_connector):
        tools = DatasphereTools(mock_connector)
        result = await tools.query_entity(
            entity="test_view",
            top=10,
        )

        assert result["entity"] == "test_view"
        assert result["row_count"] == 1
```

### Integration Test

Create `tests/test_datasphere_integration.py`:

```python
"""Integration tests for Datasphere (requires real connection)."""

import pytest
from app.connectors.datasphere import DatasphereConnector
from app.config import get_settings


@pytest.fixture
def real_connector():
    """Create real connector from settings. Skip if not configured."""
    settings = get_settings()
    if not settings.datasphere_host:
        pytest.skip("Datasphere not configured")

    return DatasphereConnector(
        host=settings.datasphere_host,
        space=settings.datasphere_space,
        client_id=settings.datasphere_client_id,
        client_secret=settings.datasphere_client_secret,
        token_url=settings.datasphere_token_url,
    )


@pytest.mark.integration
class TestDatasphereIntegration:
    @pytest.mark.asyncio
    async def test_connect_and_list(self, real_connector):
        await real_connector.connect()
        try:
            entities = await real_connector.list_entities()
            assert isinstance(entities, list)
        finally:
            await real_connector.close()

    @pytest.mark.asyncio
    async def test_health_check(self, real_connector):
        await real_connector.connect()
        try:
            healthy = await real_connector.health_check()
            assert healthy is True
        finally:
            await real_connector.close()
```

---

## Part 5: Verification Checklist

After integration, verify:

- [ ] Environment variables are set correctly
- [ ] Application starts: `uv run python main.py`
- [ ] Datasphere connector initializes (check logs)
- [ ] `ds_list_entities` tool works via chat
- [ ] `ds_query_entity` returns data
- [ ] `ds_compare_entities` produces comparison results
- [ ] Knowledge documents are ingested (check RAG logs)
- [ ] Unit tests pass: `uv run pytest tests/test_datasphere*.py`
- [ ] Integration tests pass (if running against real Datasphere)

---

## Troubleshooting

### Authentication Failures

```python
# Debug OAuth flow
import httpx

async def test_auth():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://your-tenant.authentication.sap.hana.ondemand.com/oauth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": "your-client-id",
                "client_secret": "your-client-secret",
            },
        )
        print(response.status_code)
        print(response.json())
```

### Connection Timeouts

Increase timeout in settings:

```bash
DATASPHERE_TIMEOUT=120
```

### Entity Not Found

Verify the space and entity names:

```python
# List all entities first
entities = await connector.list_entities()
print(entities)
```

### OData Filter Syntax Errors

Common mistakes:
- Use single quotes for strings: `'value'` not `"value"`
- Use `eq` not `=`
- Escape special characters in entity names

---

## Summary

You've now integrated:

1. **DatasphereConnector** - Handles OAuth2 authentication, connection pooling, and query execution
2. **DatasphereSkill** - Provides LLM-callable tools for data exploration and comparison
3. **Knowledge documents** - RAG context for SAP Datasphere patterns

The skill will automatically register when `DATASPHERE_HOST` is configured, enabling the agent to query and analyze Datasphere data through natural language.
