# Comparison Engine: How Data Comparison Works

This document explains the data comparison algorithm in detail - how Skillian aligns rows between data sources, calculates differences, and classifies discrepancies.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [The Compare Algorithm](#the-compare-algorithm)
4. [Row Alignment](#row-alignment)
5. [Difference Classification](#difference-classification)
6. [Caching](#caching)
7. [Query Engine Integration](#query-engine-integration)
8. [Data Structures](#data-structures)
9. [Configuration](#configuration)
10. [Example Walkthrough](#example-walkthrough)

---

## Overview

The `ComparisonEngine` (`app/core/comparison_engine.py`) is responsible for:

1. **Querying** two data sources with the same filters
2. **Aligning** rows by common dimensions (e.g., company, period)
3. **Comparing** measure values between aligned rows
4. **Classifying** differences as `match`, `minor_diff`, or `major_diff`
5. **Caching** results for drill-down workflows

---

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

### Components

| Component | File | Purpose |
|-----------|------|---------|
| `ComparisonEngine` | `app/core/comparison_engine.py` | Main comparison logic |
| `QueryEngine` | `app/core/query_engine.py` | SQL generation and execution |
| `SourceRegistry` | `app/core/source_registry.py` | Source definitions and config |
| `ComparisonCache` | `app/core/comparison_engine.py` | TTL-based result caching |

---

## The Compare Algorithm

The main `compare()` method follows this algorithm:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    COMPARE ALGORITHM                                      │
└──────────────────────────────────────────────────────────────────────────┘

  compare(source_a, source_b, measure, align_on, filters)
                           │
                           ▼
         ┌─────────────────────────────────┐
         │ 1. GENERATE CACHE KEY           │
         │    MD5 hash of parameters       │
         └─────────────────┬───────────────┘
                           │
                           ▼
         ┌─────────────────────────────────┐
         │ 2. CHECK CACHE                  │
         │    If cached & not expired:     │
         │    return cached result         │
         └─────────────────┬───────────────┘
                           │ cache miss
                           ▼
         ┌─────────────────────────────────┐
         │ 3. GET SOURCE DEFINITIONS       │
         │    registry.get(source_a)       │
         │    registry.get(source_b)       │
         └─────────────────┬───────────────┘
                           │
                           ▼
         ┌─────────────────────────────────┐
         │ 4. DETERMINE ALIGNMENT DIMS     │
         │    Use provided align_on        │
         │    or defaults from config      │
         └─────────────────┬───────────────┘
                           │
                           ▼
         ┌─────────────────────────────────┐
         │ 5. VALIDATE MEASURE             │
         │    Ensure measure exists        │
         │    in both sources              │
         └─────────────────┬───────────────┘
                           │
                           ▼
         ┌─────────────────────────────────┐
         │ 6. QUERY BOTH SOURCES           │
         │    (in parallel)                │
         │    QueryEngine.query(a, ...)    │
         │    QueryEngine.query(b, ...)    │
         └─────────────────┬───────────────┘
                           │
                           ▼
         ┌─────────────────────────────────┐
         │ 7. ALIGN AND COMPARE            │
         │    _align_and_compare()         │
         │    (see detail below)           │
         └─────────────────┬───────────────┘
                           │
                           ▼
         ┌─────────────────────────────────┐
         │ 8. CALCULATE SUMMARY            │
         │    Totals, counts, percentages  │
         └─────────────────┬───────────────┘
                           │
                           ▼
         ┌─────────────────────────────────┐
         │ 9. CACHE RESULT                 │
         │    Store with timestamp         │
         └─────────────────┬───────────────┘
                           │
                           ▼
         ┌─────────────────────────────────┐
         │ 10. RETURN ComparisonResult     │
         └─────────────────────────────────┘
```

### Code Reference

```python
# app/core/comparison_engine.py:120-198

async def compare(
    self,
    source_a_name: str,
    source_b_name: str,
    measure: str,
    align_on: list[str] | None = None,
    filters: dict[str, Any] | None = None,
    use_cache: bool = True,
) -> ComparisonResult:
```

---

## Row Alignment

The `_align_and_compare()` method aligns rows from both sources by dimension keys:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    ROW ALIGNMENT ALGORITHM                                │
└──────────────────────────────────────────────────────────────────────────┘

  Source A Rows:                    Source B Rows:
  ┌──────────────────────────┐     ┌──────────────────────────┐
  │ company │ period │ amount│     │ company │ period │ amount│
  ├─────────┼────────┼───────┤     ├─────────┼────────┼───────┤
  │  1001   │ 202401 │ 5000  │     │  1001   │ 202401 │ 4800  │
  │  1001   │ 202402 │ 6000  │     │  1001   │ 202402 │ 6000  │
  │  1002   │ 202401 │ 3000  │     │  1002   │ 202401 │ 3200  │
  │  1003   │ 202401 │ 2000  │     │         │        │       │
  └──────────────────────────┘     └──────────────────────────┘

                    │
                    ▼

  Step 1: Build lookup dictionaries keyed by (company, period)

  lookup_a:                          lookup_b:
  ┌────────────────────────────┐    ┌────────────────────────────┐
  │ (1001, 202401) → 5000      │    │ (1001, 202401) → 4800      │
  │ (1001, 202402) → 6000      │    │ (1001, 202402) → 6000      │
  │ (1002, 202401) → 3000      │    │ (1002, 202401) → 3200      │
  │ (1003, 202401) → 2000      │    └────────────────────────────┘
  └────────────────────────────┘

                    │
                    ▼

  Step 2: Get union of all keys

  all_keys = {(1001, 202401), (1001, 202402), (1002, 202401), (1003, 202401)}

                    │
                    ▼

  Step 3: Compare each key

  ┌───────────────────────────────────────────────────────────────────────┐
  │  Key            │ Value A │ Value B │ Abs Diff │ Pct Diff │ Status   │
  ├─────────────────┼─────────┼─────────┼──────────┼──────────┼──────────┤
  │ (1001, 202401)  │   5000  │   4800  │    200   │   4.0%   │ minor    │
  │ (1001, 202402)  │   6000  │   6000  │      0   │   0.0%   │ match    │
  │ (1002, 202401)  │   3000  │   3200  │    200   │   6.7%   │ major    │
  │ (1003, 202401)  │   2000  │   None  │   2000   │  100%    │ major    │
  └───────────────────────────────────────────────────────────────────────┘
```

### Handling Missing Rows

When a row exists in one source but not the other:
- Missing value is treated as `None`
- For diff calculation, `None` is treated as `0`
- This typically results in a `major_diff` status

---

## Difference Classification

The `_classify_diff()` method determines the status based on configurable thresholds:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    DIFF CLASSIFICATION ALGORITHM                          │
└──────────────────────────────────────────────────────────────────────────┘

  Input: abs_diff, pct_diff, thresholds

                    │
                    ▼
         ┌─────────────────────────────────┐
         │ Check MATCH threshold:          │
         │   abs_diff <= 1000              │
         │   AND                           │
         │   pct_diff <= 1.0%              │
         └─────────────────┬───────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
           BOTH OK                   EXCEEDS
              │                         │
              ▼                         ▼
         ┌─────────┐         ┌─────────────────────────────────┐
         │ MATCH   │         │ Check MINOR threshold:          │
         └─────────┘         │   abs_diff <= 5000              │
                             │   AND                           │
                             │   pct_diff <= 5.0%              │
                             └─────────────────┬───────────────┘
                                               │
                                  ┌────────────┴────────────┐
                                  │                         │
                               BOTH OK                   EXCEEDS
                                  │                         │
                                  ▼                         ▼
                             ┌──────────┐              ┌──────────┐
                             │ MINOR    │              │ MAJOR    │
                             │ DIFF     │              │ DIFF     │
                             └──────────┘              └──────────┘
```

### Threshold Configuration

From `config/sources.yaml`:

```yaml
comparison:
  thresholds:
    match:
      absolute: 1000      # Up to $1,000 difference
      percentage: 1.0     # Up to 1%
    minor_diff:
      absolute: 5000      # Up to $5,000 difference
      percentage: 5.0     # Up to 5%
    # Anything exceeding minor_diff → major_diff
```

### Classification Logic

| Condition | Status |
|-----------|--------|
| abs_diff ≤ 1000 AND pct_diff ≤ 1% | `match` |
| abs_diff ≤ 5000 AND pct_diff ≤ 5% | `minor_diff` |
| Otherwise | `major_diff` |

**Note**: Both absolute AND percentage must be within threshold for classification.

---

## Caching

The `ComparisonCache` class provides TTL-based caching:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    CACHING MECHANISM                                      │
└──────────────────────────────────────────────────────────────────────────┘

  Cache Key Generation:
  ┌─────────────────────────────────────────────────────────────────────┐
  │  cache_key = MD5(                                                    │
  │    source_a + "|" +                                                  │
  │    source_b + "|" +                                                  │
  │    measure + "|" +                                                   │
  │    sorted(align_on) + "|" +                                          │
  │    sorted(filters.items())                                           │
  │  )[:16]                                                              │
  └─────────────────────────────────────────────────────────────────────┘

  Cache Lookup:
  ┌─────────────────────────────────────────────────────────────────────┐
  │  1. Check if key exists in cache                                     │
  │  2. If exists, check if expired (time.time() - timestamp > ttl)      │
  │  3. If expired, delete and return None                               │
  │  4. If valid, return cached result                                   │
  └─────────────────────────────────────────────────────────────────────┘
```

### Cache Usage

```python
# In compare():

# Check cache first
if use_cache:
    cached = self._cache.get(cache_key)
    if cached:
        return cached  # Return immediately

# ... do expensive comparison ...

# Cache result before returning
self._cache.set(result)
return result
```

### Cache Configuration

```yaml
# config/sources.yaml
comparison:
  cache_ttl_seconds: 3600  # 1 hour
```

---

## Query Engine Integration

The `QueryEngine` generates and executes SQL for each source:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    QUERY GENERATION                                       │
└──────────────────────────────────────────────────────────────────────────┘

  Input:
    source: fi_reporting
    dimensions: [company, period]
    measures: [amount]
    filters: {company: "1001"}

                    │
                    ▼

  SQL Generated:
  ┌─────────────────────────────────────────────────────────────────────┐
  │  SELECT                                                              │
  │    compcode AS company,                                              │
  │    fiscper AS period,                                                │
  │    SUM(cs_trn_lc) AS amount                                          │
  │  FROM fi_reporting                                                   │
  │  WHERE compcode = $1                                                 │
  │  GROUP BY compcode, fiscper                                          │
  └─────────────────────────────────────────────────────────────────────┘

  Parameters: ["1001"]
```

### Column Mapping

The QueryEngine uses source definitions to map logical names to actual columns:

| Logical Name | Source Definition | Actual Column |
|--------------|-------------------|---------------|
| `company` | `dimensions.company.column` | `compcode` |
| `period` | `dimensions.period.column` | `fiscper` |
| `amount` | `measures.amount.column` | `cs_trn_lc` |

---

## Data Structures

### RowComparison

Represents a single row comparison:

```python
@dataclass
class RowComparison:
    key: dict[str, Any]           # {"company": "1001", "period": "202401"}
    source_a_value: float | None  # 5000
    source_b_value: float | None  # 4800
    absolute_diff: float          # 200
    percentage_diff: float | None # 4.0
    status: DiffStatus            # DiffStatus.MINOR_DIFF
```

### ComparisonResult

Complete comparison result:

```python
@dataclass
class ComparisonResult:
    source_a: str                 # "fi_reporting"
    source_b: str                 # "bpc_reporting"
    measure: str                  # "amount"
    align_on: list[str]           # ["company", "period"]
    rows: list[RowComparison]     # Individual row comparisons
    summary: dict[str, Any]       # Aggregate statistics
    cache_key: str                # For drill-down queries
    timestamp: float              # For TTL calculation
```

### Summary Structure

```python
summary = {
    "measure": "amount",
    "total_rows": 150,
    "total_source_a": 1_500_000,
    "total_source_b": 1_492_000,
    "total_absolute_diff": 8_000,
    "total_percentage_diff": 0.53,
    "match_count": 120,
    "minor_diff_count": 20,
    "major_diff_count": 10,
}
```

---

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

  bpc_reporting:
    description: "BPC consolidated planning data"
    table: bpc_reporting
    dimensions:
      company: { column: company_code }
      period: { column: fiscal_period }
      account: { column: account }
    measures:
      amount: { column: amount_lc, aggregation: sum }
    defaults:
      dimensions: [company, period]

comparison:
  default_align_on: [company, period]
  thresholds:
    match:
      absolute: 1000
      percentage: 1.0
    minor_diff:
      absolute: 5000
      percentage: 5.0
  cache_ttl_seconds: 3600
```

---

## Example Walkthrough

### Request

```
"Compare amounts between fi_reporting and bpc_reporting for company 1001"
```

### Step 1: Generate Cache Key

```python
key_parts = [
    "fi_reporting",
    "bpc_reporting",
    "amount",
    "['company', 'period']",
    "[('company', '1001')]"
]
cache_key = md5("fi_reporting|bpc_reporting|amount|...").hexdigest()[:16]
# Result: "abc123def456ghij"
```

### Step 2: Check Cache (Miss)

```python
cached = self._cache.get("abc123def456ghij")
# Returns None (cache miss)
```

### Step 3: Query Both Sources

**Query A (fi_reporting):**
```sql
SELECT compcode AS company, fiscper AS period, SUM(cs_trn_lc) AS amount
FROM fi_reporting
WHERE compcode = '1001'
GROUP BY compcode, fiscper
```

**Result A:**
| company | period | amount |
|---------|--------|--------|
| 1001 | 202401 | 500,000 |
| 1001 | 202402 | 600,000 |
| 1001 | 202403 | 400,000 |

**Query B (bpc_reporting):**
```sql
SELECT company_code AS company, fiscal_period AS period, SUM(amount_lc) AS amount
FROM bpc_reporting
WHERE company_code = '1001'
GROUP BY company_code, fiscal_period
```

**Result B:**
| company | period | amount |
|---------|--------|--------|
| 1001 | 202401 | 498,000 |
| 1001 | 202402 | 600,000 |
| 1001 | 202403 | 394,000 |

### Step 4: Build Lookup Dictionaries

```python
lookup_a = {
    ("1001", "202401"): 500000,
    ("1001", "202402"): 600000,
    ("1001", "202403"): 400000,
}

lookup_b = {
    ("1001", "202401"): 498000,
    ("1001", "202402"): 600000,
    ("1001", "202403"): 394000,
}
```

### Step 5: Compare Each Row

| Key | Value A | Value B | Abs Diff | Pct Diff | Status |
|-----|---------|---------|----------|----------|--------|
| (1001, 202401) | 500,000 | 498,000 | 2,000 | 0.4% | match |
| (1001, 202402) | 600,000 | 600,000 | 0 | 0.0% | match |
| (1001, 202403) | 400,000 | 394,000 | 6,000 | 1.5% | minor_diff |

**Classification Logic for (1001, 202403):**
- abs_diff = 6,000 > match threshold (1,000) → not match
- abs_diff = 6,000 > minor threshold (5,000) → not minor
- BUT pct_diff = 1.5% < minor threshold (5.0%) → minor_diff

Wait, both must pass. Let me recalculate:
- Match: 6,000 > 1,000 → FAIL
- Minor: 6,000 > 5,000 → FAIL
- Result: `major_diff`

### Step 6: Calculate Summary

```python
summary = {
    "measure": "amount",
    "total_rows": 3,
    "total_source_a": 1_500_000,
    "total_source_b": 1_492_000,
    "total_absolute_diff": 8_000,
    "total_percentage_diff": 0.53,
    "match_count": 2,
    "minor_diff_count": 0,
    "major_diff_count": 1,
}
```

### Step 7: Create and Cache Result

```python
result = ComparisonResult(
    source_a="fi_reporting",
    source_b="bpc_reporting",
    measure="amount",
    align_on=["company", "period"],
    rows=[...],
    summary=summary,
    cache_key="abc123def456ghij",
    timestamp=1706547600.0
)

self._cache.set(result)
```

### Step 8: Format Response for Tool

The tool formats the result for the LLM:

```json
{
  "summary": {
    "source_a": "fi_reporting",
    "source_b": "bpc_reporting",
    "measure": "amount",
    "total_rows": 3,
    "matches": 2,
    "minor_differences": 0,
    "major_differences": 1,
    "total_diff": 8000
  },
  "top_differences": [
    {
      "key": {"company": "1001", "period": "202403"},
      "source_a_value": 400000,
      "source_b_value": 394000,
      "absolute_diff": 6000,
      "percentage_diff": 1.5,
      "status": "major_diff"
    }
  ],
  "cache_key": "abc123def456ghij",
  "interpretation": "Good alignment (66.7% match). 1 row with major differences."
}
```

---

## Key Files

| File | Purpose |
|------|---------|
| `app/core/comparison_engine.py` | ComparisonEngine and cache classes |
| `app/core/query_engine.py` | SQL generation and execution |
| `app/core/source_registry.py` | YAML config loading |
| `app/skills/data_analyst/tools.py` | Tool wrapper for compare_sources |
| `config/sources.yaml` | Source definitions and thresholds |

---

## Related Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Overall system architecture
- [AGENT_LOOP.md](./AGENT_LOOP.md) - How the AI orchestration works
- [DATA_COMPARISON_FRAMEWORK.md](./DATA_COMPARISON_FRAMEWORK.md) - Framework overview
