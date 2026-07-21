# Data Comparison Framework

Domain-agnostic data comparison framework for Skillian, built following Anthropic best practices.

## Overview

The framework enables comparing data between multiple sources to identify discrepancies. It uses a YAML-based source registry, SQL query generation, and threshold-based diff classification.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     DataAnalystSkill                            │
│  ┌─────────────┐ ┌──────────────┐ ┌───────────────────────┐    │
│  │list_sources │ │ query_source │ │   compare_sources     │    │
│  └─────────────┘ └──────────────┘ └───────────────────────┘    │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                    ComparisonEngine                             │
│  ┌────────────────────┐  ┌────────────────────┐                │
│  │   QueryEngine      │  │  ComparisonCache   │                │
│  └─────────┬──────────┘  └────────────────────┘                │
└────────────┼────────────────────────────────────────────────────┘
             │
┌────────────┴────────────┐  ┌────────────────────────────────────┐
│   PostgresConnector     │  │       SourceRegistry               │
│   (asyncpg pool)        │  │   (YAML config loader)             │
└─────────────────────────┘  └────────────────────────────────────┘
```

## Components

### Source Registry (`app/core/source_registry.py`)

Loads data source definitions from `config/sources.yaml`:

- **Sources**: Named data sources with table, dimensions, and measures
- **Dimensions**: Fields for grouping (company, period, account, etc.)
- **Measures**: Aggregatable values (amount, quantity)
- **Comparison Config**: Thresholds for match/minor_diff/major_diff classification

### Query Engine (`app/core/query_engine.py`)

Builds and executes SQL queries:

- Generates SELECT with dimension aliases and measure aggregations
- Handles parameterized filters
- Returns structured `QueryResult` with rows and metadata

### Comparison Engine (`app/core/comparison_engine.py`)

Compares data between sources:

- Aligns rows by common dimensions
- Calculates absolute and percentage differences
- Classifies differences based on thresholds
- Caches results with configurable TTL for drill-down queries

### Data Analyst Skill (`app/skills/data_analyst/`)

Provides 3 consolidated tools following Anthropic best practices:

| Tool | Purpose |
|------|---------|
| `list_sources` | List available sources with dimensions, measures, and valid comparison pairs |
| `query_source` | Query single source with optional grouping and filtering |
| `compare_sources` | Compare measure between two sources with threshold classification |

## Configuration

### Source Definition (`config/sources.yaml`)

```yaml
sources:
  fi_reporting:
    description: "Financial transactions - source of truth for actuals"
    table: fi_reporting
    dimensions:
      company: { column: compcode }
      period: { column: fiscper }
      account: { column: gl_acct }
    measures:
      amount: { column: cs_trn_lc, aggregation: sum }
    defaults:
      dimensions: [company, period]

comparison:
  default_align_on: [company, period]
  thresholds:
    match: { absolute: 1000, percentage: 1.0 }
    minor_diff: { absolute: 5000, percentage: 5.0 }
  cache_ttl_seconds: 3600
```

### Environment Variables

```bash
BUSINESS_DATABASE_URL=postgresql://user:pass@host:port/db
```

## Diff Classification

| Status | Condition |
|--------|-----------|
| `match` | Both absolute AND percentage within match thresholds |
| `minor_diff` | Within minor thresholds but exceeds match |
| `major_diff` | Exceeds both threshold levels |

## Comparison Result Structure

```python
{
    "summary": {
        "source_a": "fi_reporting",
        "source_b": "bpc_reporting",
        "measure": "amount",
        "total_rows": 150,
        "matches": 120,
        "minor_differences": 20,
        "major_differences": 10,
        "total_diff": 50000.0
    },
    "top_differences": [...],  # Top 5 by absolute diff
    "cache_key": "abc123...",  # For follow-up queries
    "interpretation": "Good alignment (80% match)..."
}
```

## Knowledge Documents

RAG documents in `app/skills/data_analyst/knowledge/`:

- `comparison_guide.md` - How to use comparison tools effectively
- `troubleshooting.md` - Common patterns and resolution strategies

## Testing

```bash
# Run all unit tests
uv run pytest -m "not integration"

# Run with coverage
uv run pytest --cov=app -m "not integration"
```

## Dependencies

- `asyncpg` - Async PostgreSQL driver
- `pyyaml` - YAML config loading
- `pydantic` - Schema validation

## Design Principles

1. **Consolidated Tools**: 3 powerful tools instead of many small ones
2. **Clear Descriptions**: Documentation-style tool descriptions
3. **Meaningful Responses**: Structured output with interpretation
4. **Caching**: TTL-based cache for drill-down workflows
5. **Prompt-Based Reasoning**: Upgradeable to LangGraph later
