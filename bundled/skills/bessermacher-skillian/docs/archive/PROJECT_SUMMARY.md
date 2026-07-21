# Skillian - SAP BW AI Assistant

AI-powered diagnostic and analysis platform for SAP BW data issues, organized by functional domain skills.

## Overview

Skillian is an intelligent assistant that helps SAP BW users diagnose and resolve data issues across different functional areas. The system uses domain-specific **Skills** to provide expert-level analysis for each business area.

## Core Concept

```
Skill = Tools + Knowledge (RAG) + System Prompt
```

Each skill encapsulates:
- **Tools**: Functions the AI can call to query SAP BW data
- **Knowledge**: Domain-specific documentation for RAG retrieval
- **System Prompt**: Expert instructions for the functional area

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                          │
│                  (API / Chat Interface)                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Skillian Agent                            │
│  ┌──────────────┐  ┌───────────────┐  ┌─────────────────┐   │
│  │ LLM Factory  │  │ Skill Router  │  │ RAG Module      │   │
│  │ (Claude/     │  │ (auto-select  │  │ (pgvector)      │   │
│  │  OpenAI/     │  │  skill by     │  │                 │   │
│  │  Ollama)     │  │  query)       │  │                 │   │
│  └──────────────┘  └───────────────┘  └─────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      Skills Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ Financial   │  │ Sales       │  │ Inventory   │   ...    │
│  │ Skill       │  │ Skill       │  │ Skill       │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   SAP BW Connector                           │
│              (HANA Direct / RFC / Mock)                      │
└─────────────────────────────────────────────────────────────┘
```

## Planned Skills

| Skill | Domain | Use Cases |
|-------|--------|-----------|
| **Financial (FI)** | Financial Reporting | GL postings missing in reports, cost center issues, profit center reconciliation |
| **Sales (SD)** | Sales Analytics | Sales orders not in reports, billing document issues, revenue recognition |
| **Inventory (MM)** | Material Management | Stock discrepancies, goods movement issues, valuation problems |
| **Controlling (CO)** | Cost Accounting | Cost allocation issues, internal order reporting, profitability analysis |
| **BPC** | Planning & Consolidation | BPC data load issues, consolidation errors, planning data problems |

## Common Tools (Shared Across Skills)

| Tool | Purpose |
|------|---------|
| `find_data_path` | Trace document through PSA → DSO → Cube |
| `check_load_status` | Get DTP/request status |
| `query_dso` | Query DSO data with filters |
| `query_psa` | Query raw extracted data |
| `check_delta_queue` | Check extraction queue status |
| `get_transformation_rules` | Get mapping/transformation rules |
| `get_recent_errors` | Get recent load errors |

## Technology Stack

- **Python 3.12+**
- **LangChain** - LLM integration framework
- **FastAPI** - REST API
- **PostgreSQL + pgvector** - Vector store for RAG
- **LLM Providers**: Claude (Anthropic), OpenAI, Ollama (local dev)
- **SAP Connectivity**: hdbcli (HANA), pyrfc (RFC)

## Project Structure

```
skillian/
├── main.py                 # Application entry point
├── pyproject.toml          # Dependencies
├── docs/
│   └── PROJECT_SUMMARY.md  # This file
│
├── app/
│   ├── config.py           # Environment configuration
│   ├── constants.py        # Application constants
│   │
│   ├── llm/                # LLM integration
│   │   ├── factory.py      # LLM provider factory
│   │   └── chat_model.py   # Custom chat model wrapper
│   │
│   ├── core/               # Core framework
│   │   ├── base_skill.py   # Abstract Skill class
│   │   ├── skill_registry.py # Skill routing
│   │   └── agent.py        # Main orchestration
│   │
│   ├── skills/             # Domain skills
│   │   ├── financial/      # FI skill
│   │   │   ├── skill.py
│   │   │   ├── tools.py
│   │   │   ├── prompts.py
│   │   │   └── knowledge/
│   │   ├── sales/          # SD skill
│   │   ├── inventory/      # MM skill
│   │   └── controlling/    # CO skill
│   │
│   ├── connectors/         # SAP connectivity
│   │   ├── base.py
│   │   ├── hana.py
│   │   ├── rfc.py
│   │   └── mock.py
│   │
│   └── api/                # REST endpoints
│       └── routes.py
│
└── tests/
```

## Key Features

1. **Automatic Skill Routing** - Agent automatically selects the appropriate skill based on user query
2. **RAG-Enhanced Responses** - Domain knowledge retrieved from vector store for context
3. **Tool-Augmented Analysis** - LLM can execute diagnostic tools against SAP BW
4. **Multi-Provider LLM** - Support for Claude, OpenAI, and local models
5. **Streaming Support** - Real-time response streaming for better UX

## Example Usage

```bash
# Query example
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Document 100500 is not showing in the P&L report"}'

# Response
{
  "answer": "Document 100500 was found in PSA but failed to load into the reporting DSO due to missing profit center...",
  "skill_used": "financial",
  "tool_calls": [...],
  "diagnosis": "..."
}
```

## Next Steps

1. Set up project structure and dependencies
2. Implement LLM factory (Claude/OpenAI/Ollama)
3. Create base Skill class and registry
4. Implement Financial skill as first domain
5. Add SAP BW connector (mock for development)
6. Build REST API endpoints
7. Add additional skills (Sales, Inventory, etc.)
