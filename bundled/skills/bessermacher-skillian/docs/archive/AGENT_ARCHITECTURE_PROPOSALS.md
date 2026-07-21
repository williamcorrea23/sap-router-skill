# Skillian Agent Architecture: Research & Proposals

> Research summary and implementation proposals for an extensible AI agent with no-code skill management, based on analysis of FinRobot, OpenBB, and industry best practices.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current Architecture Analysis](#current-architecture-analysis)
3. [Industry Research Findings](#industry-research-findings)
4. [Gap Analysis](#gap-analysis)
5. [Proposed Improvements](#proposed-improvements)
6. [No-Code Skill Definition System](#no-code-skill-definition-system)
7. [Implementation Roadmap](#implementation-roadmap)

---

## Executive Summary

### Key Findings

| Aspect | Current Skillian | Industry Standard | Gap |
|--------|------------------|-------------------|-----|
| **Skill Architecture** | Python classes implementing Protocol | YAML/Markdown config + Python | Medium |
| **Tool Definition** | Pydantic schemas in code | JSON Schema / OpenAPI spec | Low |
| **Dynamic Loading** | Manual registration in `dependencies.py` | Entry points / Auto-discovery | High |
| **Multi-Agent** | Single agent | Multi-agent orchestration | High |
| **Extensibility** | Requires Python coding | Config-based with plugin system | High |

### Top Recommendations

1. **Adopt SKILL.md Standard** - Use the Agent Skills specification for skill definitions
2. **Implement Dynamic Skill Loading** - Auto-discover skills from directory structure
3. **Add OpenAPI-to-Tool Generation** - Generate tools from SAP API specifications
4. **Consider Multi-Agent Architecture** - For complex diagnostic scenarios
5. **Create Skill CLI** - For managing skills without code changes

---

## Current Architecture Analysis

### Strengths

Your current architecture follows several best practices:

```
✅ Protocol-based design (Skill protocol with duck typing)
✅ Pydantic validation for tool inputs
✅ Clean separation: Tool, Skill, Registry
✅ LangChain integration via to_langchain_tool()
✅ Knowledge paths for RAG integration
✅ Dependency injection via FastAPI
```

### Current Skill Structure

```python
# app/core/skill.py - Current Protocol
class Skill(Protocol):
    @property
    def name(self) -> str: ...
    @property
    def description(self) -> str: ...
    @property
    def tools(self) -> list[Tool]: ...
    @property
    def system_prompt(self) -> str: ...
    @property
    def knowledge_paths(self) -> list[str]: ...
    def get_tool(self, name: str) -> Tool | None: ...
```

### Current Registration Flow

```python
# app/dependencies.py - Manual registration
registry = SkillRegistry()
registry.register(DataAnalystSkill(connector))  # Requires code change
```

### Pain Points

1. **Adding skills requires Python code** - Must create class, tools, register manually
2. **No hot-reloading** - Server restart required for new skills
3. **Tightly coupled** - Tools are defined inside skill modules
4. **No versioning** - No skill version tracking or compatibility checks
5. **Limited observability** - No telemetry on skill/tool usage

---

## Industry Research Findings

### FinRobot Architecture

FinRobot (AI4Finance Foundation) uses a **four-layer hierarchical architecture**:

```
┌─────────────────────────────────────────────────────────┐
│ Layer 1: Financial AI Agents (Perception-Brain-Action)  │
├─────────────────────────────────────────────────────────┤
│ Layer 2: Financial LLMs (FinGPT, FinRL, FinML)         │
├─────────────────────────────────────────────────────────┤
│ Layer 3: LLMOps & DataOps (Smart Scheduler, RAG)       │
├─────────────────────────────────────────────────────────┤
│ Layer 4: Foundation Models (Llama, ChatGLM, Falcon)    │
└─────────────────────────────────────────────────────────┘
```

**Key Patterns from FinRobot:**

| Pattern | Description | Skillian Applicability |
|---------|-------------|------------------------|
| **Agent Library** | Predefined agent configs in `agent_library.py` | ✅ Create skill library with configs |
| **Financial CoT** | Chain-of-Thought for structured reasoning | ✅ Add SAP-specific reasoning chains |
| **Multi-Agent Workflows** | Single/Multi/Leader patterns | ⚠️ Future consideration |
| **Data Source Abstraction** | Unified data connector interface | ✅ Already have connector protocol |
| **Toolkit Registration** | Tools registered during instantiation | ✅ Similar to current approach |

**FinRobot Skill Organization:**

```
finrobot/
├── agents/
│   └── agent_library.py      # Predefined configurations
├── data_source/              # Data connectors
│   ├── finnhub_utils.py
│   ├── sec_utils.py
│   └── yfinance_utils.py
├── functional/               # Tool implementations
│   ├── analyzer.py
│   ├── charting.py
│   └── quantitative.py
└── toolkits.py               # Tool registration
```

### OpenBB Architecture

OpenBB uses a **TET (Transform-Extract-Transform) pipeline** with plugin-based extensibility:

```
┌────────────────┐    ┌────────────────┐    ┌────────────────┐
│   Transform    │───▶│    Extract     │───▶│   Transform    │
│ (Query Params) │    │ (API/Data)     │    │  (Output)      │
└────────────────┘    └────────────────┘    └────────────────┘
```

**Key Patterns from OpenBB:**

| Pattern | Description | Skillian Applicability |
|---------|-------------|------------------------|
| **Fetcher Protocol** | Standardized data retrieval interface | ✅ Align connectors to this pattern |
| **Entry Point Discovery** | `pyproject.toml` plugin registration | ✅ Enable dynamic skill loading |
| **Pydantic QueryParams** | Input validation models | ✅ Already using |
| **OBBject Wrapper** | Unified response format | ⚠️ Consider for tool responses |
| **OpenAPI Generation** | Auto-generate from specs | ✅ Generate SAP BW tools |

**OpenBB Extension Pattern:**

```toml
# pyproject.toml
[tool.poetry.plugins."openbb_provider_extension"]
my_provider = "openbb_my_provider:my_provider"

[tool.poetry.plugins."openbb_core_extension"]
my_router = "my_router.my_router:router"
```

### Agent Skills Standard (SKILL.md)

The emerging **Agent Skills specification** (Linux Foundation / AAIF) provides a universal format:

```yaml
# SKILL.md frontmatter
---
name: financial-diagnostics
description: Diagnose SAP BW financial data issues...
license: Apache-2.0
compatibility: Requires SAP Datasphere connection
allowed-tools: Bash(query:*) Read Write
metadata:
  author: skillian
  version: "1.0"
  domain: financial
---

# Financial Diagnostics Skill

## Instructions
[Markdown instructions for the LLM]

## Examples
[Concrete usage examples]
```

**Benefits of SKILL.md:**
- Adopted by 25+ platforms (Claude Code, Cursor, Goose, etc.)
- Self-contained documentation
- Portable across agent frameworks
- Human-readable and version-controllable

### Model Context Protocol (MCP)

MCP is becoming the standard for tool integration:

```json
{
  "name": "query_infocube",
  "description": "Query SAP BW InfoCube data",
  "inputSchema": {
    "type": "object",
    "properties": {
      "infocube_id": {"type": "string"},
      "dimensions": {"type": "array", "items": {"type": "string"}},
      "measures": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["infocube_id"]
  }
}
```

**MCP Benefits:**
- Universal protocol for AI tool access
- JSON Schema for validation
- Hot-reloading support
- Transport agnostic (stdio, HTTP, SSE)

---

## Gap Analysis

### Architecture Gaps

| Area | Current State | Target State | Priority |
|------|---------------|--------------|----------|
| **Skill Discovery** | Manual registration | Auto-discovery from directory | High |
| **Skill Definition** | Python only | YAML/Markdown + Python | High |
| **Tool Generation** | Manual coding | OpenAPI spec generation | Medium |
| **Hot Reload** | Server restart | Runtime reload | Medium |
| **Versioning** | None | SemVer with compatibility | Low |
| **Telemetry** | None | Tool execution metrics | Low |
| **Multi-Agent** | Single agent | Orchestrated multi-agent | Future |

### Missing Components

1. **Skill Loader** - Dynamic loading from config files
2. **Skill CLI** - Command-line management tool
3. **Skill Validator** - Schema validation before loading
4. **Tool Generator** - Generate tools from OpenAPI specs
5. **Skill Marketplace** - Repository of reusable skills (future)

---

## Proposed Improvements

### 1. Hybrid Skill Definition System

Support both Python-based and config-based skills:

```
app/skills/
├── financial/                    # Config-based skill
│   ├── SKILL.md                  # Skill definition (Agent Skills format)
│   ├── tools.yaml                # Tool definitions
│   ├── tools.py                  # Tool implementations
│   └── knowledge/                # RAG documents
│       └── gl_accounts.md
├── data_analyst/                 # Python-based skill (existing)
│   ├── skill.py
│   ├── tools.py
│   └── knowledge/
└── _templates/                   # Skill templates
    ├── basic/
    └── advanced/
```

### 2. SKILL.md Format for Skillian

```yaml
# app/skills/financial/SKILL.md
---
name: financial-diagnostics
description: |
  Diagnose SAP BW financial data issues including GL discrepancies,
  cost center allocations, and posting period validations.
  Use when users ask about financial reports or data quality.
version: "1.0.0"
author: skillian
domain: financial
tags: [sap, bw, finance, gl, cost-center]
connector: datasphere  # Required connector type
---

# Financial Diagnostics Skill

## Capabilities

This skill helps diagnose financial data issues in SAP BW:

- Validate GL account balances across periods
- Check posting period consistency
- Detect missing cost allocations
- Compare actuals vs. budget
- Identify currency conversion issues

## When to Use

Activate this skill when the user asks about:
- GL account discrepancies
- Cost center data issues
- Financial report validation
- Period-end reconciliation

## Instructions

1. Always start by understanding the scope (company code, fiscal year, period)
2. Use `check_gl_balance` for single account validation
3. Use `compare_sources` for cross-system reconciliation
4. Present differences with both absolute and percentage values
5. Suggest root causes based on common patterns

## Examples

### Example 1: GL Balance Check
User: "Check GL account 400000 for company 1000 in 2024"
Assistant: Uses check_gl_balance with account=400000, company=1000, year=2024

### Example 2: Cross-System Comparison
User: "Compare FI and BPC revenue for Q1"
Assistant: Uses compare_sources with source_a=fi_reporting, source_b=bpc_reporting
```

### 3. YAML Tool Definitions

```yaml
# app/skills/financial/tools.yaml
tools:
  - name: check_gl_balance
    description: |
      Verify GL account balance for a specific period.
      Returns balance details and any anomalies detected.
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
        description: Specific period (e.g., "001" for January)
    implementation: app.skills.financial.tools:check_gl_balance

  - name: validate_cost_allocations
    description: |
      Check for missing or incorrect cost center allocations.
      Identifies postings without required cost objects.
    parameters:
      - name: cost_center
        type: string
        required: false
        description: Specific cost center to check (checks all if not specified)
      - name: date_range
        type: object
        required: true
        properties:
          start: {type: string, format: date}
          end: {type: string, format: date}
    implementation: app.skills.financial.tools:validate_cost_allocations
```

### 4. Dynamic Skill Loader

```python
# app/core/skill_loader.py
"""Dynamic skill loader with hot-reload support."""

from pathlib import Path
import yaml
import importlib
import importlib.util
from typing import Any

from app.core.skill import Skill
from app.core.tool import Tool


class SkillLoader:
    """Load skills from directory structure."""

    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self._loaded_skills: dict[str, Skill] = {}

    def discover_skills(self) -> list[str]:
        """Find all skill directories."""
        skills = []
        for path in self.skills_dir.iterdir():
            if path.is_dir() and not path.name.startswith("_"):
                if (path / "SKILL.md").exists() or (path / "skill.py").exists():
                    skills.append(path.name)
        return skills

    def load_skill(self, skill_name: str) -> Skill:
        """Load a skill by name."""
        skill_path = self.skills_dir / skill_name

        # Check for config-based skill first
        skill_md = skill_path / "SKILL.md"
        if skill_md.exists():
            return self._load_config_skill(skill_path, skill_md)

        # Fall back to Python-based skill
        skill_py = skill_path / "skill.py"
        if skill_py.exists():
            return self._load_python_skill(skill_path, skill_py)

        raise SkillLoadError(f"No skill definition found in {skill_path}")

    def _load_config_skill(self, skill_path: Path, skill_md: Path) -> Skill:
        """Load skill from SKILL.md and tools.yaml."""
        # Parse SKILL.md frontmatter
        config = self._parse_skill_md(skill_md)

        # Load tools
        tools_yaml = skill_path / "tools.yaml"
        tools = self._load_tools(tools_yaml) if tools_yaml.exists() else []

        return ConfiguredSkill(
            name=config["name"],
            description=config["description"],
            system_prompt=config.get("instructions", ""),
            tools=tools,
            knowledge_paths=[str(skill_path / "knowledge")],
            metadata=config.get("metadata", {}),
        )

    def _load_tools(self, tools_yaml: Path) -> list[Tool]:
        """Load tools from YAML definition."""
        config = yaml.safe_load(tools_yaml.read_text())
        tools = []

        for tool_def in config.get("tools", []):
            # Import implementation function
            module_path, func_name = tool_def["implementation"].rsplit(":", 1)
            module = importlib.import_module(module_path)
            func = getattr(module, func_name)

            # Build Pydantic schema from YAML
            schema = self._build_schema(tool_def["parameters"])

            tools.append(Tool(
                name=tool_def["name"],
                description=tool_def["description"],
                function=func,
                input_schema=schema,
            ))

        return tools

    def reload_skill(self, skill_name: str) -> Skill:
        """Hot-reload a skill."""
        if skill_name in self._loaded_skills:
            # Invalidate caches
            module_name = f"app.skills.{skill_name}"
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])

        return self.load_skill(skill_name)
```

### 5. Skill CLI Tool

```bash
# Skill management commands
uv run skillian skill list                    # List all skills
uv run skillian skill info financial          # Show skill details
uv run skillian skill create inventory        # Create from template
uv run skillian skill validate financial      # Validate skill definition
uv run skillian skill enable financial        # Enable skill
uv run skillian skill disable financial       # Disable skill
uv run skillian skill reload financial        # Hot-reload skill
uv run skillian skill test financial          # Run skill tests
```

### 6. OpenAPI-to-Tool Generator

For SAP Datasphere APIs, generate tools automatically:

```python
# app/core/openapi_loader.py
"""Generate tools from OpenAPI specifications."""

from openapi_core import Spec

def load_tools_from_openapi(spec_path: Path) -> list[Tool]:
    """Generate Tool objects from OpenAPI spec."""
    spec = Spec.from_file(spec_path)
    tools = []

    for path, path_item in spec.paths.items():
        for method, operation in path_item.items():
            if method in ["get", "post"]:
                tool = Tool(
                    name=operation.operation_id,
                    description=operation.summary or operation.description,
                    function=create_api_caller(spec, path, method),
                    input_schema=build_schema_from_openapi(operation),
                )
                tools.append(tool)

    return tools
```

### 7. Updated Project Structure

```
skillian/
├── main.py
├── pyproject.toml
├── app/
│   ├── config.py
│   ├── dependencies.py
│   ├── cli/                      # NEW: CLI commands
│   │   ├── __init__.py
│   │   └── skill_commands.py
│   ├── core/
│   │   ├── skill.py
│   │   ├── skill_loader.py       # NEW: Dynamic loader
│   │   ├── skill_validator.py    # NEW: Schema validation
│   │   ├── tool.py
│   │   ├── tool_generator.py     # NEW: OpenAPI generator
│   │   ├── registry.py
│   │   └── agent.py
│   ├── skills/
│   │   ├── _templates/           # NEW: Skill templates
│   │   │   └── basic/
│   │   │       ├── SKILL.md
│   │   │       ├── tools.yaml
│   │   │       └── tools.py
│   │   ├── financial/            # Migrated to config-based
│   │   │   ├── SKILL.md
│   │   │   ├── tools.yaml
│   │   │   ├── tools.py
│   │   │   └── knowledge/
│   │   ├── inventory/            # NEW: Example domain
│   │   │   ├── SKILL.md
│   │   │   ├── tools.yaml
│   │   │   ├── tools.py
│   │   │   └── knowledge/
│   │   └── data_analyst/         # Keep Python-based
│   │       ├── skill.py
│   │       ├── tools.py
│   │       └── knowledge/
│   ├── connectors/
│   │   ├── protocol.py           # NEW: Connector protocol
│   │   ├── datasphere.py
│   │   └── mock.py
│   └── api/
│       ├── routes.py
│       └── schemas.py
├── specs/                        # NEW: OpenAPI specs
│   └── datasphere_api.yaml
├── tests/
└── docs/
```

---

## No-Code Skill Definition System

### Complete No-Code Skill Example

To add a new skill without writing Python code:

#### Step 1: Create Skill Directory

```bash
mkdir -p app/skills/inventory
```

#### Step 2: Create SKILL.md

```yaml
# app/skills/inventory/SKILL.md
---
name: inventory-diagnostics
description: |
  Diagnose SAP BW inventory data issues including stock discrepancies,
  material movements, and warehouse transfers.
version: "1.0.0"
author: skillian
domain: inventory
tags: [sap, bw, inventory, mm, wm]
connector: datasphere
---

# Inventory Diagnostics Skill

## Capabilities

- Check stock levels across storage locations
- Validate material movements
- Detect inventory discrepancies
- Analyze transfer postings

## Instructions

1. Identify the material and plant scope
2. Use appropriate diagnostic tool
3. Present findings with quantity and value differences
```

#### Step 3: Define Tools (YAML)

```yaml
# app/skills/inventory/tools.yaml
tools:
  - name: check_stock_level
    description: Check current stock level for a material
    parameters:
      - name: material_number
        type: string
        required: true
        description: SAP material number
      - name: plant
        type: string
        required: true
        description: Plant code
      - name: storage_location
        type: string
        required: false
        description: Storage location (optional)
    # Uses generic query - no Python implementation needed
    query_template: |
      SELECT material, plant, storage_location, SUM(quantity) as stock
      FROM ZINV_STOCK
      WHERE material = '{material_number}'
        AND plant = '{plant}'
        {% if storage_location %}AND storage_location = '{storage_location}'{% endif %}
      GROUP BY material, plant, storage_location
```

#### Step 4: (Optional) Add Knowledge Documents

```markdown
# app/skills/inventory/knowledge/stock_types.md

# SAP Inventory Stock Types

## Unrestricted Stock
Available for consumption or sales...

## Quality Inspection Stock
Stock pending quality approval...

## Blocked Stock
Stock not available for use...
```

#### Step 5: Enable Skill

```bash
uv run skillian skill enable inventory
```

### Query-Template Based Tools (Zero Python)

For simple query tools, use templates instead of Python:

```yaml
# tools.yaml with query templates
tools:
  - name: get_material_documents
    description: Retrieve material documents for analysis
    parameters:
      - name: material
        type: string
        required: true
      - name: date_from
        type: string
        format: date
        required: true
      - name: date_to
        type: string
        format: date
        required: true
    query_template: |
      SELECT doc_number, material, movement_type, quantity, posting_date
      FROM ZMAT_DOC
      WHERE material = '{material}'
        AND posting_date BETWEEN '{date_from}' AND '{date_to}'
      ORDER BY posting_date DESC
    connector: datasphere
```

The loader executes these templates through the configured connector.

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

| Task | Description | Files |
|------|-------------|-------|
| Create SkillLoader | Dynamic loading from directories | `app/core/skill_loader.py` |
| SKILL.md Parser | Parse frontmatter + markdown | `app/core/skill_parser.py` |
| YAML Tool Loader | Load tools from YAML definitions | `app/core/yaml_tools.py` |
| Update Registry | Support dynamic registration | `app/core/registry.py` |

### Phase 2: Migration (Week 3)

| Task | Description | Files |
|------|-------------|-------|
| Migrate Financial Skill | Convert to SKILL.md format | `app/skills/financial/` |
| Create Skill Template | Basic template for new skills | `app/skills/_templates/` |
| Update Dependencies | Auto-discover and load skills | `app/dependencies.py` |

### Phase 3: CLI & Tooling (Week 4)

| Task | Description | Files |
|------|-------------|-------|
| Skill CLI | Management commands | `app/cli/skill_commands.py` |
| Skill Validator | Schema validation | `app/core/skill_validator.py` |
| Hot Reload | Runtime skill reloading | `app/core/skill_loader.py` |

### Phase 4: Advanced Features (Future)

| Task | Description | Priority |
|------|-------------|----------|
| OpenAPI Generator | Generate tools from API specs | Medium |
| Query Templates | Zero-code query tools | Medium |
| Multi-Agent | Orchestrated workflows | Low |
| Skill Marketplace | Shared skill repository | Low |

---

## Summary

### Key Architectural Decisions

1. **Adopt SKILL.md Standard** - For portability and ecosystem compatibility
2. **Hybrid Python/YAML** - Support both approaches for flexibility
3. **Auto-Discovery** - Load skills from directory structure automatically
4. **Query Templates** - Enable zero-code tools for simple queries
5. **CLI Management** - Non-technical skill management interface

### Benefits

| Benefit | Impact |
|---------|--------|
| **Faster skill development** | No Python required for simple skills |
| **Lower barrier to entry** | Domain experts can contribute |
| **Better maintainability** | Skills are self-documenting |
| **Ecosystem compatibility** | Works with other Agent Skills platforms |
| **Hot reloading** | No server restart for changes |

### Industry Alignment

Your enhanced architecture will align with:

- ✅ **FinRobot** - Agent library pattern, tool registration
- ✅ **OpenBB** - TET pipeline, entry point discovery
- ✅ **Agent Skills** - SKILL.md standard
- ✅ **MCP** - JSON Schema tool definitions
- ✅ **LangChain** - Pydantic-based tools

---

## References

- [FinRobot GitHub](https://github.com/AI4Finance-Foundation/FinRobot)
- [OpenBB Platform](https://github.com/OpenBB-finance/OpenBB)
- [Agent Skills Specification](https://agentskills.io/specification)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FinGPT](https://github.com/AI4Finance-Foundation/FinGPT)
- [CrewAI](https://docs.crewai.com/)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
