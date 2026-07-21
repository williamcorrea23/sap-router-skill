# Implementation Plan: Data Comparison Framework

**Version**: 2.0 (Revised)
**Status**: Ready for implementation
**Based on**: Anthropic best practices, LangGraph patterns, industry standards

---

## Design Principles (from Research)

### From Anthropic
1. **Selective tool implementation** - Focus on tools matching agent workflows, not every API
2. **Tool consolidation** - Combine related operations into single tools
3. **Meaningful responses** - Return semantic data, not technical identifiers
4. **Token-efficient** - Pagination, filtering, truncation with sensible defaults
5. **Clear descriptions** - Tool descriptions like onboarding documentation

### From LangGraph
1. **State management** - Checkpointing for conversation persistence
2. **Human-in-the-loop** - Interrupt and resume capabilities
3. **Observability** - Clear visibility into agent loops
4. **PostgresSaver** - For production state persistence (not MemorySaver)

### Keep Existing Infrastructure
- `app/llm/` - LLM factory (Ollama, Claude, OpenAI)
- `app/rag/` - Vector store with pgvector
- `app/api/` - REST API with FastAPI
- `app/db/` - SQLAlchemy async
- `app/core/tool.py` - Tool abstraction with Pydantic
- `app/core/base_skill.py` - Skill base class
- `app/core/registry.py` - Skill/tool registry

---

## New Architecture

```
skillian/
├── app/
│   ├── config.py                    # Settings ✓ (keep)
│   ├── dependencies.py              # FastAPI DI (update)
│   │
│   ├── core/                        # Framework
│   │   ├── __init__.py
│   │   ├── tool.py                  # ✓ (keep)
│   │   ├── base_skill.py            # ✓ (keep)
│   │   ├── skill.py                 # ✓ (keep)
│   │   ├── registry.py              # ✓ (keep)
│   │   ├── messages.py              # Minimal, will be replaced by LangGraph
│   │   ├── agent.py                 # Phase 2: Rebuild with LangGraph
│   │   ├── source_registry.py       # NEW: Load sources from YAML
│   │   ├── query_engine.py          # NEW: Build SQL from metadata
│   │   ├── comparison_engine.py     # NEW: Compare any two sources
│   │   └── cache.py                 # NEW: Result caching (Redis/memory)
│   │
│   ├── connectors/                  # Database connections
│   │   ├── __init__.py
│   │   └── postgres.py              # NEW: Generic async PostgreSQL
│   │
│   ├── skills/
│   │   └── data_analyst/            # NEW: Data analyst skill
│   │       ├── __init__.py
│   │       ├── skill.py
│   │       ├── tools.py             # Consolidated tools
│   │       └── knowledge/           # RAG documents
│   │           ├── sources/         # Source descriptions
│   │           └── rules/           # Comparison rules
│   │
│   ├── llm/                         # ✓ (keep)
│   ├── rag/                         # ✓ (keep)
│   ├── api/                         # ✓ (keep)
│   └── db/                          # ✓ (keep)
│
├── config/
│   └── sources.yaml                 # NEW: Source definitions
│
└── tests/
    ├── test_source_registry.py      # NEW
    ├── test_query_engine.py         # NEW
    ├── test_comparison_engine.py    # NEW
    └── test_data_analyst_skill.py   # NEW
```

---

## Phase 1: Source Infrastructure

### 1.1 Source Configuration (`config/sources.yaml`)

```yaml
sources:
  fi_reporting:
    description: "Financial transactions - source of truth for actuals"
    table: fi_reporting

    dimensions:
      company: { column: compcode, type: string }
      period: { column: fiscper, type: string, format: "YYYYPPP" }
      account: { column: gl_acct, type: string }
      segment: { column: segment, type: string }
      profit_center: { column: prof_ctr, type: string }

    measures:
      amount: { column: cs_trn_lc, aggregation: sum }
      quantity: { column: quantity, aggregation: sum }

    defaults:
      dimensions: [company, period]
      filters: { account: "4%|5%|6%" }  # P&L accounts

  consolidation_mart:
    description: "Consolidated data for group reporting"
    table: consolidation_mart

    dimensions:
      company: { column: compcode, type: string }
      period: { column: fiscper, type: string }
      version: { column: version, type: string, values: [ACTUAL, BUDGET, FORECAST] }
      account: { column: grpacct, type: string }
      segment: { column: segment, type: string }

    measures:
      amount: { column: cs_trn_lc, aggregation: sum }
      ytd_amount: { column: cs_ytd_lc, aggregation: sum }

    defaults:
      dimensions: [company, period, version]

  bpc_reporting:
    description: "Business Planning and Consolidation data"
    table: bpc_reporting

    dimensions:
      company: { column: compcode, type: string }
      period: { column: fiscper, type: string }
      version: { column: version, type: string }
      scope: { column: scope, type: string }
      account: { column: grpacct, type: string }

    measures:
      amount: { column: cs_trn_lc, aggregation: sum }
      amount_gc: { column: cs_trn_gc, aggregation: sum }

    defaults:
      dimensions: [company, period, version]

comparison:
  thresholds:
    match: { absolute: 1000, percentage: 1.0 }
    minor_diff: { absolute: 5000, percentage: 5.0 }
  cache_ttl_seconds: 3600
```

### 1.2 Source Registry (`app/core/source_registry.py`)

```python
"""Source registry - loads and validates source definitions."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


class DimensionDef(BaseModel):
    """Dimension definition."""
    column: str
    type: str = "string"
    format: str | None = None
    values: list[str] | None = None


class MeasureDef(BaseModel):
    """Measure definition."""
    column: str
    aggregation: str = "sum"


class SourceDef(BaseModel):
    """Source definition loaded from YAML."""
    name: str
    description: str
    table: str
    dimensions: dict[str, DimensionDef]
    measures: dict[str, MeasureDef]
    defaults: dict[str, Any] = {}


class SourceRegistry:
    """Registry of available data sources."""

    def __init__(self, config_path: Path | str = "config/sources.yaml"):
        self._sources: dict[str, SourceDef] = {}
        self._load_config(Path(config_path))

    def get(self, name: str) -> SourceDef | None:
        """Get source by name."""
        return self._sources.get(name)

    def list_sources(self) -> list[str]:
        """List all source names."""
        return list(self._sources.keys())

    def get_source_info(self) -> list[dict]:
        """Get info about all sources for LLM context."""
        return [
            {
                "name": s.name,
                "description": s.description,
                "dimensions": list(s.dimensions.keys()),
                "measures": list(s.measures.keys()),
            }
            for s in self._sources.values()
        ]
```

### 1.3 PostgreSQL Connector (`app/connectors/postgres.py`)

```python
"""Generic async PostgreSQL connector."""

import asyncpg
from typing import Any


class PostgresConnector:
    """Async PostgreSQL connection pool."""

    def __init__(self, database_url: str):
        self._url = database_url
        self._pool: asyncpg.Pool | None = None

    async def get_pool(self) -> asyncpg.Pool:
        """Get or create connection pool."""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(self._url)
        return self._pool

    async def execute(self, query: str, params: list[Any]) -> list[dict]:
        """Execute query and return results as dicts."""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]

    async def close(self) -> None:
        """Close connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None
```

---

## Phase 2: Query & Comparison Engines

### 2.1 Query Engine (`app/core/query_engine.py`)

Builds parameterized SQL from source metadata.

Key features:
- Translates semantic names (company, amount) to columns (compcode, cs_trn_lc)
- Builds GROUP BY with aggregations
- Generates parameterized WHERE clauses
- Returns standardized QueryResult

### 2.2 Comparison Engine (`app/core/comparison_engine.py`)

Compares data from any two sources.

Key features:
- Validates sources have common dimensions
- Aligns data by specified dimensions
- Calculates differences with thresholds
- Suggests drill-down dimensions
- Caches results for iterative analysis

---

## Phase 3: Tools (Following Anthropic Best Practices)

### Consolidated Tool Design

Instead of many small tools, we have **3 consolidated tools**:

```python
# app/skills/data_analyst/tools.py

class ListSourcesInput(BaseModel):
    """No parameters needed."""
    pass


class QuerySourceInput(BaseModel):
    """Input for query_source tool."""
    source: str = Field(description="Source name (see list_sources)")
    dimensions: list[str] = Field(
        default_factory=list,
        description="Dimensions to group by (e.g., ['company', 'period'])"
    )
    filters: dict[str, str] | None = Field(
        default=None,
        description="Filters (e.g., {'company': '1000', 'period': '2024012'})"
    )


class CompareSourcesInput(BaseModel):
    """Input for compare_sources tool."""
    source1: str = Field(description="First source to compare")
    source2: str = Field(description="Second source to compare")
    align_on: list[str] = Field(
        default_factory=lambda: ["company", "period"],
        description="Dimensions to align on"
    )
    filters: dict[str, str] | None = Field(
        default=None,
        description="Common filters for both sources"
    )
    measure: str = Field(
        default="amount",
        description="Measure to compare"
    )
```

### Tool Descriptions (Clear Like Documentation)

```python
LIST_SOURCES_DESCRIPTION = """
List all available data sources with their schemas.

Returns:
- Source names and descriptions
- Available dimensions (e.g., company, period, account)
- Available measures (e.g., amount, quantity)

Use this first to understand what data is available.
"""

QUERY_SOURCE_DESCRIPTION = """
Query aggregated data from a specific source.

Use this to:
- Get totals by company and period
- Drill down by adding dimensions (account, segment)
- Apply filters to focus on specific data

Dimensions are semantic names (not column names).
The system translates them automatically.
"""

COMPARE_SOURCES_DESCRIPTION = """
Compare data between two sources to find discrepancies.

Workflow:
1. Start with company + period alignment
2. If MISMATCH found, add account dimension
3. Continue drilling down: segment → profit_center

Returns:
- Row-by-row comparison with match status
- Summary: total matched, minor diff, mismatched
- Suggested next drill-down dimension
"""
```

---

## Phase 4: Data Analyst Skill

### Skill Definition

```python
# app/skills/data_analyst/skill.py

class DataAnalystSkill(BaseSkill):
    """Generic data analyst for comparing data sources."""

    def __init__(
        self,
        source_registry: SourceRegistry,
        query_engine: QueryEngine,
        comparison_engine: ComparisonEngine,
    ):
        self._registry = source_registry
        self._query = query_engine
        self._compare = comparison_engine

    @property
    def name(self) -> str:
        return "data_analyst"

    @property
    def description(self) -> str:
        return (
            "Analyze and compare data from multiple sources. "
            "Identify discrepancies, drill down to root causes."
        )

    @property
    def tools(self) -> list[Tool]:
        return [
            Tool(
                name="list_sources",
                description=LIST_SOURCES_DESCRIPTION,
                function=self._list_sources,
                input_schema=ListSourcesInput,
            ),
            Tool(
                name="query_source",
                description=QUERY_SOURCE_DESCRIPTION,
                function=self._query_source,
                input_schema=QuerySourceInput,
            ),
            Tool(
                name="compare_sources",
                description=COMPARE_SOURCES_DESCRIPTION,
                function=self._compare_sources,
                input_schema=CompareSourcesInput,
            ),
        ]

    @property
    def system_prompt(self) -> str:
        sources_info = self._registry.get_source_info()
        return f"""You are a data analyst expert.

AVAILABLE SOURCES:
{json.dumps(sources_info, indent=2)}

WORKFLOW:
1. Use list_sources to understand available data
2. Use query_source to retrieve specific data
3. Use compare_sources to identify discrepancies
4. Drill down by adding dimensions when mismatches found

MATCH STATUS:
- MATCH: Values align (diff ≤1% and ≤1000)
- MINOR_DIFF: Small difference (diff ≤5% and ≤5000)
- MISMATCH: Significant difference - investigate!

DRILL-DOWN STRATEGY:
company+period → add account → add segment → add profit_center
"""

    @property
    def knowledge_paths(self) -> list[str]:
        return ["app/skills/data_analyst/knowledge/"]
```

---

## Phase 5: Agent Upgrade (LangGraph)

Replace current agent loop with LangGraph for:
- **State management** with checkpointing
- **PostgresSaver** for production persistence
- **Human-in-the-loop** interrupt capability
- **Observability** with state snapshots

```python
# Future: app/core/langgraph_agent.py
from langgraph.graph import StateGraph
from langgraph.checkpoint.postgres import PostgresSaver
```

---

## Implementation Order

| Step | Task | Effort |
|------|------|--------|
| 1 | Create `config/sources.yaml` | Small |
| 2 | Implement `source_registry.py` + tests | Medium |
| 3 | Implement `postgres.py` connector | Small |
| 4 | Implement `query_engine.py` + tests | Medium |
| 5 | Implement `comparison_engine.py` + tests | Medium |
| 6 | Create data analyst skill | Medium |
| 7 | Create knowledge documents | Small |
| 8 | Register skill in dependencies | Small |
| 9 | End-to-end testing | Medium |
| 10 | (Future) LangGraph agent upgrade | Large |

---

## Success Criteria

1. **No hardcoded sources** - All from YAML config
2. **Generic SQL** - Works with any PostgreSQL tables
3. **Semantic names** - Agent uses `company`, not `compcode`
4. **3 consolidated tools** - Following Anthropic's guidance
5. **Clear descriptions** - LLM can use tools effectively
6. **All tests pass** - 100% coverage on new code

---

## Sources

- [Anthropic: Writing Effective Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Anthropic: Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [LangGraph Multi-Agent Orchestration Guide 2025](https://latenode.com/blog/ai-frameworks-technical-infrastructure/langgraph-multi-agent-orchestration)
- [Best AI Agent Frameworks 2025](https://langwatch.ai/blog/best-ai-agent-frameworks-in-2025)
