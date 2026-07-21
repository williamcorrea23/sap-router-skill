# Metadata-Driven Data Comparison Framework

Design document for a flexible, no-code data comparison system.

**Status**: Proposal
**Date**: January 2025

---

## Overview

A framework that enables an AI agent to compare data from any registered sources by reading source metadata from the knowledge base. New sources can be added without code changes.

### Core Principles

1. **No-code source registration** - Sources defined in markdown knowledge documents
2. **Agent-driven comparison** - LLM decides which sources to compare based on user query
3. **Flexible alignment** - Data automatically aligned by common dimensions
4. **Caching with drill-down** - Results cached for iterative investigation
5. **Exception-focused output** - Return only mismatches needing attention

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AI Agent                                        │
│  - Reads source descriptions from RAG                                       │
│  - Decides which sources to compare                                         │
│  - Builds comparison strategy                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
┌───────────────────────────────┐   ┌─────────────────────────────────────────┐
│     Knowledge Base (RAG)      │   │            Generic Tools                 │
│                               │   │                                         │
│  sources/                     │   │  query_source(source, dims, filters)    │
│    fi_reporting.md            │   │  compare_datasets(src1, src2, align_on) │
│    consolidation_mart.md      │   │  get_comparison_cache(key)              │
│    bpc_reporting.md           │   │  store_comparison_cache(key, data)      │
│  rules/                       │   │                                         │
│    comparison_defaults.md     │   └─────────────────────────────────────────┘
│    dimension_mappings.md      │                       │
└───────────────────────────────┘                       ▼
                                    ┌─────────────────────────────────────────┐
                                    │         Source Router                    │
                                    │  (routes query_source to connector)     │
                                    │                                         │
                                    │  Reads config/sources.yaml              │
                                    │  Maps source_name → table + connector   │
                                    └─────────────────────────────────────────┘
                                                        │
                                                        ▼
                                    ┌─────────────────────────────────────────┐
                                    │           Data Sources                   │
                                    │  (PostgreSQL tables via connector)      │
                                    └─────────────────────────────────────────┘
```

---

## Knowledge Base Structure

```
app/skills/business/knowledge/
├── sources/
│   ├── fi_reporting.md           # FI source description
│   ├── consolidation_mart.md     # Consolidation source description
│   └── bpc_reporting.md          # BPC source description
├── rules/
│   ├── comparison_defaults.md    # Default comparison settings
│   └── dimension_mappings.md     # How dimensions map across sources
└── common_issues.md              # Troubleshooting guide
```

---

## Source Description Format

Each source is documented in a markdown file that the agent reads via RAG.

### Example: `sources/fi_reporting.md`

```markdown
# FI Reporting Source

## Overview
Raw financial transactions from SAP FI module. This is the **source of truth**
for actual posted transactions.

## Query Name
`fi_reporting`

## Dimensions
| Dimension | Column | Description |
|-----------|--------|-------------|
| company | compcode | SAP company code |
| period | fiscper | Fiscal period (YYYYPPP format) |
| fiscal_year | fiscyear | Fiscal year |
| account | gl_acct | GL account number |
| profit_center | prof_ctr | Profit center |
| segment | segment | Business segment |
| cost_center | costctr | Cost center |

## Measures
| Measure | Column | Description |
|---------|--------|-------------|
| amount_lc | cs_trn_lc | Transaction amount in local currency |
| quantity | quantity | Transaction quantity |

## Default Filters
- For P&L comparison: `gl_acct LIKE '4%' OR '5%' OR '6%'`
- Debit-side only: `fidbcrin = 'S'`

## Version Support
No version dimension. FI contains only actual posted data.

## Comparison Notes
- Compare with `consolidation_mart` to verify data transfer to BPC
- Compare with `bpc_reporting` to verify planning vs actual
- FI is typically more granular than consolidated sources
```

### Example: `rules/dimension_mappings.md`

```markdown
# Dimension Mappings Between Sources

## Company
| Source | Column |
|--------|--------|
| fi_reporting | compcode |
| consolidation_mart | compcode |
| bpc_reporting | compcode |

## Period
| Source | Column | Format |
|--------|--------|--------|
| fi_reporting | fiscper | YYYYPPP |
| consolidation_mart | fiscper | YYYYPPP |
| bpc_reporting | fiscper | YYYYPPP |

## Account
| Source | Column | Notes |
|--------|--------|-------|
| fi_reporting | gl_acct | Detailed GL account |
| consolidation_mart | grpacct | Group account (aggregated) |
| bpc_reporting | grpacct | Group account |

**Note**: When comparing FI to Consolidation/BPC, aggregate FI by group account
or filter to accounts that map 1:1.
```

### Example: `rules/comparison_defaults.md`

```markdown
# Default Comparison Rules

## Standard Comparison Dimensions
When user doesn't specify, compare by:
1. company (compcode)
2. period (fiscper)

## Match Thresholds
| Status | Criteria |
|--------|----------|
| MATCH | Difference = 0 OR (diff ≤ 1000 AND diff% ≤ 1%) |
| MINOR_DIFF | diff ≤ 5000 AND diff% ≤ 5% |
| MISMATCH | Everything else |

## Drill-Down Strategy
When mismatch found:
1. First drill down by: account/grpacct
2. Then by: segment
3. Then by: profit_center

## Source Priority for Actuals
1. fi_reporting (source of truth)
2. consolidation_mart (should match FI)
3. bpc_reporting (may have adjustments)
```

---

## Source Routing Configuration

Minimal configuration to map source names to database tables.

### `config/sources.yaml`

```yaml
sources:
  fi_reporting:
    table: fi_reporting
    connector: business

  consolidation_mart:
    table: consolidation_mart
    connector: business

  bpc_reporting:
    table: bpc_reporting
    connector: business

# Example: Adding a new external source (no code change needed)
  external_sales:
    table: ext_sales_data
    connector: business
    dimensions:
      company: company_id      # Column mapping if different
      period: fiscal_period
    measures:
      amount: sales_amount
```

---

## Tools

### 1. `query_source` - Generic Data Fetcher

```python
class QuerySourceInput(BaseModel):
    """Input schema for query_source tool."""

    source: str = Field(
        description="Source name from knowledge base (e.g., 'fi_reporting')"
    )
    dimensions: list[str] = Field(
        default=["company", "period"],
        description="Dimensions to group by (use semantic names from knowledge base)"
    )
    filters: dict | None = Field(
        default=None,
        description="Filter conditions, e.g., {'company': '1000', 'period': '2024012'}"
    )
    measures: list[str] | None = Field(
        default=None,
        description="Measures to aggregate (default: all available)"
    )


async def query_source(
    source: str,
    dimensions: list[str],
    filters: dict | None = None,
    measures: list[str] | None = None,
) -> dict:
    """Query any registered source with specified dimensions and filters.

    The source must be registered in config/sources.yaml and documented
    in the knowledge base. Dimension and measure names are mapped to
    actual column names based on configuration.

    Returns:
        Aggregated data grouped by specified dimensions.
    """
    pass
```

### 2. `compare_datasets` - Comparison Engine

```python
class CompareInput(BaseModel):
    """Input schema for compare_datasets tool."""

    source1: str = Field(
        description="First source name"
    )
    source2: str = Field(
        description="Second source name"
    )
    align_on: list[str] = Field(
        default=["company", "period"],
        description="Dimensions to align/join on"
    )
    filters: dict | None = Field(
        default=None,
        description="Common filters to apply to both sources"
    )
    cache_key: str | None = Field(
        default=None,
        description="Key to cache result for later drill-down"
    )


async def compare_datasets(
    source1: str,
    source2: str,
    align_on: list[str],
    filters: dict | None = None,
    cache_key: str | None = None,
) -> dict:
    """Compare two sources, aligning by specified dimensions.

    1. Query both sources with same filters
    2. Align data by common dimensions
    3. Calculate differences
    4. Apply match thresholds
    5. Cache result if key provided

    Returns:
        Comparison result with match status and differences.
    """
    pass
```

### 3. `get_cached_comparison` - Retrieve Cached Result

```python
async def get_cached_comparison(cache_key: str) -> dict | None:
    """Retrieve a previously cached comparison result.

    Returns None if cache key doesn't exist or has expired.
    """
    pass
```

### 4. `add_source_to_comparison` - Extend Comparison

```python
async def add_source_to_comparison(
    cache_key: str,
    new_source: str,
) -> dict:
    """Add another source to an existing cached comparison.

    Useful when initial comparison doesn't reveal the issue
    and agent wants to check additional sources.
    """
    pass
```

---

## Data Structures

### Comparison Result

```python
@dataclass
class ComparisonResult:
    """Result of comparing two data sources."""

    source1: str
    source2: str
    aligned_on: list[str]
    filters: dict | None

    # Row-level comparison
    rows: list[ComparisonRow]

    # Summary statistics
    summary: ComparisonSummary

    # For agent decision-making
    has_mismatches: bool
    suggested_drill_down: str | None
    cache_key: str | None


@dataclass
class ComparisonRow:
    """Single row in comparison result."""

    dimensions: dict[str, Any]      # e.g., {"company": "1000", "period": "2024012"}
    source1_amount: float | None
    source2_amount: float | None
    difference: float
    difference_pct: float
    match_status: str               # MATCH, MINOR_DIFF, MISMATCH


@dataclass
class ComparisonSummary:
    """Summary of comparison result."""

    total_rows: int
    matched_rows: int
    minor_diff_rows: int
    mismatched_rows: int

    source1_total: float
    source2_total: float
    total_difference: float

    overall_status: str             # MATCH, MINOR_DIFF, MISMATCH
```

---

## Agent Workflow

### Example: User asks "Why don't FI and BPC match for company 1000?"

```
1. Agent reads knowledge base:
   - fi_reporting.md → understands FI schema
   - bpc_reporting.md → understands BPC schema
   - dimension_mappings.md → knows how to align
   - comparison_defaults.md → knows default settings

2. Agent plans comparison:
   "I'll compare fi_reporting and bpc_reporting for company 1000,
   aligned by company and period."

3. Agent executes:
   compare_datasets(
       source1="fi_reporting",
       source2="bpc_reporting",
       align_on=["company", "period"],
       filters={"company": "1000"},
       cache_key="fi_bpc_1000"
   )

4. Result shows MISMATCH in period 2024012, diff = 50,000

5. Agent decides to drill down:
   compare_datasets(
       source1="fi_reporting",
       source2="bpc_reporting",
       align_on=["company", "period", "account"],
       filters={"company": "1000", "period": "2024012"},
       cache_key="fi_bpc_1000_detail"
   )

6. Result shows account G4500000 has 50,000 in FI, 0 in BPC

7. Agent responds:
   "FI and BPC don't match for company 1000 in December 2024.
   The difference of 50,000 EUR comes from account G4500000
   (External Sales) which exists in FI but is missing in BPC.
   This may indicate a posting that hasn't been transferred yet."
```

---

## Adding a New Source (No Code Change)

### Step 1: Create Knowledge Document

Create `sources/external_sales.md`:

```markdown
# External Sales System

## Overview
Sales data from external CRM system. Used for reconciliation with FI.

## Query Name
`external_sales`

## Dimensions
| Dimension | Column | Description |
|-----------|--------|-------------|
| company | company_id | Company identifier |
| period | fiscal_period | Fiscal period (YYYYPPP) |
| customer | customer_id | Customer identifier |

## Measures
| Measure | Column | Description |
|---------|--------|-------------|
| amount | sales_amount | Sales amount |

## Comparison Notes
- Compare with `fi_reporting` to verify sales postings
- External system may have timing differences
```

### Step 2: Update Dimension Mappings

Add to `rules/dimension_mappings.md`:

```markdown
## Company
| Source | Column |
|--------|--------|
| external_sales | company_id |
...
```

### Step 3: Add Source Config

Add to `config/sources.yaml`:

```yaml
external_sales:
  table: ext_sales_data
  connector: business
```

**Done!** Agent can now compare external_sales with other sources.

---

## Implementation Phases

### Phase 1: Foundation
- [ ] Source routing from YAML config
- [ ] Generic `query_source` tool
- [ ] Basic dimension mapping

### Phase 2: Comparison Engine
- [ ] `compare_datasets` tool
- [ ] Alignment logic
- [ ] Match threshold evaluation

### Phase 3: Caching & Drill-Down
- [ ] Result caching
- [ ] `add_source_to_comparison` tool
- [ ] Drill-down suggestions

### Phase 4: Agent Integration
- [ ] Update system prompt for comparison workflow
- [ ] Knowledge base documents for existing sources
- [ ] Test with real user scenarios

---

## Open Questions

1. **Cache TTL**: How long should comparison results be cached?
   - Proposal: 1 hour default, configurable per comparison

2. **Large result sets**: How to handle comparisons with thousands of rows?
   - Proposal: Return top N mismatches, offer pagination

3. **Concurrent comparisons**: Support multiple cached comparisons?
   - Proposal: Yes, use unique cache keys

4. **Audit trail**: Log comparison requests for compliance?
   - Proposal: Optional logging to separate table

---

## References

- [AI Agent Research](./ai_agent_research.md) - Background research
- [LangGraph Documentation](https://www.langchain.com/langgraph) - Recommended framework
- [LangChain Dynamic Tool Calling](https://changelog.langchain.com/announcements/dynamic-tool-calling-in-langgraph-agents)
