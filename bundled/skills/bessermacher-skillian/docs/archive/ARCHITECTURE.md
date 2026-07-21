# Skillian Architecture

Complete guide to understanding how Skillian works, from high-level concepts to implementation details.

## Table of Contents

1. [Overview](#overview)
2. [Core Concept: Skill = Tools + Knowledge + Prompt](#core-concept)
3. [System Components](#system-components)
4. [Request Flow](#request-flow)
5. [Dependency Injection](#dependency-injection)
6. [Key Design Patterns](#key-design-patterns)
7. [Configuration](#configuration)
8. [Adding New Components](#adding-new-components)

---

## Overview

Skillian is an AI-powered assistant for diagnosing SAP BW data issues. It uses a **skill-based architecture** where domain knowledge is encapsulated into modular, reusable components.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              SKILLIAN                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────────────────┐   │
│  │   Client    │────▶│  FastAPI    │────▶│        Agent            │   │
│  │  (Request)  │     │  Endpoint   │     │   (Orchestration)       │   │
│  └─────────────┘     └─────────────┘     └───────────┬─────────────┘   │
│                                                       │                  │
│                            ┌──────────────────────────┴───────────┐     │
│                            │                                      │     │
│                            ▼                                      ▼     │
│                   ┌─────────────────┐                  ┌──────────────┐ │
│                   │  Skill Registry │                  │ LLM Provider │ │
│                   │  ┌───────────┐  │                  │ (Ollama/     │ │
│                   │  │   Data    │  │                  │  Claude/     │ │
│                   │  │  Analyst  │  │                  │  OpenAI)     │ │
│                   │  │   Skill   │  │                  └──────────────┘ │
│                   │  └───────────┘  │                                   │
│                   └────────┬────────┘                                   │
│                            │                                            │
│                            ▼                                            │
│          ┌─────────────────────────────────────────┐                   │
│          │           Core Engines                   │                   │
│          │  ┌───────────────┐  ┌────────────────┐  │                   │
│          │  │ Comparison    │  │  Query         │  │                   │
│          │  │ Engine        │  │  Engine        │  │                   │
│          │  └───────────────┘  └────────────────┘  │                   │
│          └──────────────┬──────────────────────────┘                   │
│                         │                                               │
│                         ▼                                               │
│                ┌─────────────────┐     ┌──────────────────────┐        │
│                │ PostgresConnect │     │   Source Registry    │        │
│                │ (asyncpg pool)  │     │   (YAML config)      │        │
│                └─────────────────┘     └──────────────────────┘        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Core Concept

The fundamental building block is the **Skill**:

```
┌─────────────────────────────────────────────────────────────────────┐
│                           SKILL                                      │
│                                                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │     TOOLS       │  │    KNOWLEDGE    │  │   SYSTEM PROMPT     │  │
│  │                 │  │     (RAG)       │  │                     │  │
│  │ • list_sources  │  │                 │  │ "You are a data     │  │
│  │ • query_source  │  │ • Markdown      │  │  analyst expert     │  │
│  │ • compare_      │  │   documents     │  │  specializing in    │  │
│  │   sources       │  │ • Domain        │  │  SAP BW data        │  │
│  │                 │  │   knowledge     │  │  reconciliation..." │  │
│  │                 │  │ • Best          │  │                     │  │
│  │                 │  │   practices     │  │                     │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘  │
│                                                                      │
│         Skill = Tools + Knowledge + System Prompt                    │
└─────────────────────────────────────────────────────────────────────┘
```

### Tool Structure

Each tool follows a strict pattern with Pydantic validation:

```
┌─────────────────────────────────────────────────┐
│                    TOOL                          │
├─────────────────────────────────────────────────┤
│  name: "compare_sources"                        │
│  description: "Compare measure between sources" │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │         INPUT SCHEMA (Pydantic)          │   │
│  │  source_a: str (required)                │   │
│  │  source_b: str (required)                │   │
│  │  measure: str (required)                 │   │
│  │  filters: dict | None (optional)         │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │         FUNCTION                         │   │
│  │  async def compare_sources(             │   │
│  │      engine, source_a, source_b, ...    │   │
│  │  ) -> dict                               │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## System Components

### 1. API Layer (`app/api/`)

| File | Purpose |
|------|---------|
| `routes.py` | FastAPI route handlers for `/chat`, `/sessions`, `/health` |
| `schemas.py` | Request/response Pydantic models |

### 2. Core (`app/core/`)

| File | Purpose |
|------|---------|
| `agent.py` | Main orchestration loop - LLM + Tool execution |
| `skill.py` | Skill protocol definition |
| `tool.py` | Tool dataclass with Pydantic validation |
| `registry.py` | Skill registration and tool routing |
| `messages.py` | Conversation state management |
| `comparison_engine.py` | Row alignment and diff classification |
| `query_engine.py` | SQL generation from source definitions |
| `source_registry.py` | YAML config loader for data sources |

### 3. Skills (`app/skills/`)

| Directory | Purpose |
|-----------|---------|
| `data_analyst/` | Data comparison and querying tools |

### 4. LLM (`app/llm/`)

| File | Purpose |
|------|---------|
| `protocol.py` | LLMProvider protocol definition |
| `factory.py` | Provider factory (Ollama/Anthropic/OpenAI) |
| `ollama.py` | Ollama local LLM implementation |
| `anthropic.py` | Claude API implementation |
| `openai.py` | OpenAI API implementation |

### 5. Connectors (`app/connectors/`)

| File | Purpose |
|------|---------|
| `postgres.py` | PostgreSQL async connector for business data |

### 6. RAG (`app/rag/`)

| File | Purpose |
|------|---------|
| `store.py` | pgvector-based knowledge retrieval |

---

## Request Flow

When a user sends a message, it flows through the system:

```
                    User: "Compare amounts between fi_reporting and bpc"
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 1: API RECEIVES REQUEST                                             │
│                                                                          │
│   POST /chat                                                             │
│   Body: { "message": "Compare amounts between fi_reporting and bpc" }   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 2: DEPENDENCY INJECTION                                             │
│                                                                          │
│   ┌───────────────┐     ┌───────────────┐     ┌───────────────┐        │
│   │  get_settings │────▶│ get_llm_      │────▶│  get_skill_   │        │
│   │   (cached)    │     │   provider    │     │   registry    │        │
│   └───────────────┘     │   (cached)    │     │   (cached)    │        │
│                         └───────────────┘     └───────┬───────┘        │
│                                                       │                 │
│                                                       ▼                 │
│                                               ┌───────────────┐        │
│                                               │   get_agent   │        │
│                                               │ (fresh/request)│        │
│                                               └───────────────┘        │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 3: AGENT PROCESSING                                                 │
│                                                                          │
│   agent.process("Compare amounts between fi_reporting and bpc")         │
│   (See AGENT_LOOP.md for detailed algorithm)                            │
│                                                                          │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 4: RETURN RESPONSE                                                  │
│                                                                          │
│   {                                                                      │
│     "response": "The comparison shows 96.7% alignment...",              │
│     "tool_calls": [                                                      │
│       { "tool": "compare_sources", "args": {...}, "result": {...} }     │
│     ],                                                                   │
│     "finished": true                                                     │
│   }                                                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Dependency Injection

Skillian uses FastAPI's `Depends` with `@lru_cache` for singleton management:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     DEPENDENCY GRAPH                                     │
└─────────────────────────────────────────────────────────────────────────┘

                         get_settings()
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
    get_llm_provider()  get_source_registry()  get_postgres_connector()
              │               │                        │
              │               │               ┌────────┴────────┐
              ▼               ▼               ▼                 ▼
    get_chat_model()    get_query_engine()  get_comparison_engine()
              │               │                        │
              │               └────────────┬───────────┘
              │                            │
              │                            ▼
              │                   get_data_analyst_skill()
              │                            │
              │                            ▼
              │                   get_skill_registry()
              │                            │
              └────────────────────────────┤
                                           ▼
                                     get_agent()
                                           │
                                           ▼
                                   Route Handler
```

### Key Dependencies

```python
# app/dependencies.py

@lru_cache
def get_settings() -> Settings:
    return Settings()

@lru_cache
def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    return create_llm_provider(settings)

@lru_cache
def get_skill_registry() -> SkillRegistry:
    registry = SkillRegistry()
    registry.register(get_data_analyst_skill())
    return registry

def get_agent() -> Agent:  # Not cached - fresh per request
    return Agent(
        chat_model=get_chat_model(),
        registry=get_skill_registry()
    )
```

---

## Key Design Patterns

### 1. Protocol-Based Duck Typing

Skills and LLM providers use `Protocol` (not ABC) for flexibility:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Skill(Protocol):
    @property
    def name(self) -> str: ...
    @property
    def tools(self) -> list[Tool]: ...
    @property
    def system_prompt(self) -> str: ...
```

### 2. Factory Pattern

LLM provider selection based on configuration:

```python
def create_llm_provider(settings: Settings) -> LLMProvider:
    match settings.llm_provider:
        case "anthropic":
            return AnthropicProvider(settings.anthropic_api_key)
        case "ollama":
            return OllamaProvider(settings.ollama_base_url)
        case "openai":
            return OpenAIProvider(settings.openai_api_key)
```

### 3. Tool Binding

Tools are converted to LangChain format and bound to the chat model:

```python
# In Agent.__init__
langchain_tools = [
    tool.to_langchain_tool()
    for tool in registry.get_all_tools()
]
self.model = chat_model.bind_tools(langchain_tools)
```

### 4. Conversation State

Messages are tracked with proper role separation:

```python
class Conversation:
    messages: list[Message]

    def add_user(self, content: str)
    def add_assistant(self, content: str, tool_calls: list | None)
    def add_tool_result(self, content: str, tool_call_id: str)
```

---

## Configuration

### Environment Variables

```bash
# .env
ENV=development
DEBUG=true

# LLM Provider
LLM_PROVIDER=ollama              # ollama | anthropic | openai
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
ANTHROPIC_API_KEY=sk-...         # for production

# Databases
DATABASE_URL=postgresql+asyncpg://skillian:skillian@localhost:5432/skillian
BUSINESS_DATABASE_URL=postgresql://skillian:skillian@localhost:5432/skillian
```

### Source Configuration (`config/sources.yaml`)

```yaml
sources:
  fi_reporting:
    description: "Financial transactions - source of truth"
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

---

## Adding New Components

### Adding a New Skill

1. Create directory structure:
   ```
   app/skills/{domain}/
   ├── __init__.py
   ├── skill.py          # Skill class
   ├── tools.py          # Tool functions + schemas
   └── knowledge/        # RAG documents
       └── guide.md
   ```

2. Define tool input schemas:
   ```python
   class MyToolInput(BaseModel):
       param: str = Field(description="Parameter description")
       optional: int | None = Field(default=None)
   ```

3. Implement skill class:
   ```python
   class DomainSkill:
       @property
       def name(self) -> str:
           return "domain"

       @property
       def tools(self) -> list[Tool]:
           return [...]

       @property
       def system_prompt(self) -> str:
           return "You are an expert in..."
   ```

4. Register in `app/dependencies.py`:
   ```python
   registry.register(DomainSkill(...))
   ```

### Adding a New LLM Provider

1. Implement the protocol in `app/llm/{provider}.py`:
   ```python
   class NewProvider:
       def get_chat_model(self) -> BaseChatModel:
           return ChatNewProvider(...)

       @property
       def model_name(self) -> str:
           return "model-name"

       @property
       def provider_name(self) -> str:
           return "new_provider"
   ```

2. Add to factory in `app/llm/factory.py`:
   ```python
   case "new_provider":
       return NewProvider(settings.new_api_key)
   ```

### Adding a New Data Source

Add to `config/sources.yaml`:
```yaml
sources:
  new_source:
    description: "Description for LLM"
    table: actual_table_name
    dimensions:
      logical_name: { column: actual_column }
    measures:
      metric: { column: value_column, aggregation: sum }
```

---

## Related Documentation

- [AGENT_LOOP.md](./AGENT_LOOP.md) - How the AI reasoning loop works
- [COMPARISON_ENGINE.md](./COMPARISON_ENGINE.md) - Data comparison algorithm details
- [DATA_COMPARISON_FRAMEWORK.md](./DATA_COMPARISON_FRAMEWORK.md) - Comparison framework overview
