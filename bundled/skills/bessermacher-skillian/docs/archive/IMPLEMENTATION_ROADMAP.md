# Skillian - Implementation Roadmap (MVP)

Focused roadmap for minimum viable product with modern Python practices.

## Guiding Principles

- **Type Safety**: Full type hints, Pydantic models for validation
- **Async-First**: Async/await for I/O operations
- **Dependency Injection**: Clean testability, no global state
- **Single Responsibility**: Small, focused modules
- **Configuration**: Environment-based, 12-factor app principles
- **Testing**: Unit tests for core logic, integration tests for API

## Tech Stack (MVP)

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Python | 3.14+ | t-strings, deferred annotations, free-threading |
| Package Manager | uv | Fast, modern dependency management |
| LLM Framework | LangChain | Ecosystem, abstractions |
| API | FastAPI | Async, auto-docs, Pydantic integration |
| Vector Store | ChromaDB | Embedded, no infra for MVP |
| SAP Connector | Mock | MVP development without SAP |
| LLM (Dev) | Ollama | Free local development |
| LLM (Prod) | Claude | Best reasoning for complex tasks |

## Project Structure (MVP)

```
skillian/
├── pyproject.toml
├── .env.example
├── main.py                     # FastAPI app entry
│
├── app/
│   ├── __init__.py
│   ├── config.py               # Settings with pydantic-settings
│   ├── dependencies.py         # FastAPI dependency injection
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── base.py             # Protocol for LLM interface
│   │   └── factory.py          # LLM provider factory
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── skill.py            # Base Skill protocol + dataclasses
│   │   ├── registry.py         # Skill registry and routing
│   │   └── agent.py            # Agent orchestration
│   │
│   ├── skills/
│   │   ├── __init__.py
│   │   └── financial/          # First skill for MVP
│   │       ├── __init__.py
│   │       ├── skill.py        # FinancialSkill implementation
│   │       ├── tools.py        # FI diagnostic tools
│   │       └── knowledge/      # RAG documents
│   │           └── common_errors.md
│   │
│   ├── connectors/
│   │   ├── __init__.py
│   │   ├── base.py             # Connector protocol
│   │   └── mock.py             # Mock connector for MVP
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   └── store.py            # ChromaDB wrapper
│   │
│   └── api/
│       ├── __init__.py
│       ├── routes.py           # API endpoints
│       └── schemas.py          # Request/Response models
│
├── tests/
│   ├── conftest.py             # Fixtures
│   ├── test_agent.py
│   ├── test_skills.py
│   └── test_api.py
│
└── docs/
    ├── PROJECT_SUMMARY.md
    └── IMPLEMENTATION_ROADMAP.md
```

---

## Phase 1: Foundation

### 1.1 Project Setup

**pyproject.toml**
```toml
[project]
name = "skillian"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.6.0",
    "langchain>=0.3.0",
    "langchain-anthropic>=0.3.0",
    "langchain-ollama>=0.2.0",
    "chromadb>=0.5.0",
    "httpx>=0.28.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-asyncio>=0.24", "ruff>=0.8.0"]
```

### 1.2 Configuration

**app/config.py**
```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Environment
    env: str = "development"
    debug: bool = True

    # LLM
    llm_provider: str = "ollama"  # ollama | anthropic | openai
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Vector Store
    chroma_persist_dir: str = "./data/chroma"

    @property
    def is_production(self) -> bool:
        return self.env == "production"

    model_config = {"env_file": ".env", "extra": "ignore"}

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

---

## Phase 2: LLM Layer

### 2.1 LLM Protocol & Factory

**app/llm/base.py**
```python
from typing import Protocol, Any
from langchain_core.language_models import BaseChatModel

class LLMProvider(Protocol):
    def get_model(self) -> BaseChatModel: ...
```

**app/llm/factory.py**
```python
from langchain_core.language_models import BaseChatModel
from app.config import Settings

def create_llm(settings: Settings) -> BaseChatModel:
    match settings.llm_provider:
        case "anthropic":
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model="claude-sonnet-4-20250514",
                api_key=settings.anthropic_api_key,
            )
        case "openai":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model="gpt-4o",
                api_key=settings.openai_api_key,
            )
        case "ollama" | _:
            from langchain_ollama import ChatOllama
            return ChatOllama(
                model=settings.ollama_model,
                base_url=settings.ollama_base_url,
            )
```

---

## Phase 3: Core Framework

### 3.1 Skill Protocol

**app/core/skill.py**
```python
from typing import Protocol, Callable, Any
from dataclasses import dataclass
from pydantic import BaseModel

@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    func: Callable[..., Any]
    args_schema: type[BaseModel] | None = None

class Skill(Protocol):
    name: str
    description: str

    def get_tools(self) -> list[Tool]: ...
    def get_system_prompt(self, context: str = "") -> str: ...
    def get_context(self, query: str) -> str: ...
```

### 3.2 Skill Registry

**app/core/registry.py**
```python
from langchain_core.language_models import BaseChatModel
from app.core.skill import Skill

class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        self._skills[skill.name] = skill

    def get(self, name: str) -> Skill | None:
        return self._skills.get(name)

    def list_skills(self) -> list[str]:
        return list(self._skills.keys())

    def route(self, query: str, llm: BaseChatModel) -> Skill:
        """Route query to appropriate skill using LLM."""
        if len(self._skills) == 1:
            return next(iter(self._skills.values()))

        # For MVP: simple keyword matching
        # Production: LLM-based routing
        query_lower = query.lower()
        for skill in self._skills.values():
            if skill.name in query_lower:
                return skill

        # Default to first skill
        return next(iter(self._skills.values()))
```

### 3.3 Agent

**app/core/agent.py**
```python
from dataclasses import dataclass, field
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import StructuredTool
from app.core.skill import Skill
from app.core.registry import SkillRegistry

@dataclass
class AgentResult:
    answer: str
    skill_used: str
    tool_calls: list[dict] = field(default_factory=list)
    error: str | None = None

class SkillAgent:
    def __init__(
        self,
        llm: BaseChatModel,
        registry: SkillRegistry,
        max_iterations: int = 5,
    ) -> None:
        self.llm = llm
        self.registry = registry
        self.max_iterations = max_iterations

    def run(self, query: str) -> AgentResult:
        skill = self.registry.route(query, self.llm)
        context = skill.get_context(query)

        tools = [
            StructuredTool(
                name=t.name,
                description=t.description,
                func=t.func,
                args_schema=t.args_schema,
            )
            for t in skill.get_tools()
        ]

        llm_with_tools = self.llm.bind_tools(tools)

        messages = [
            SystemMessage(content=skill.get_system_prompt(context)),
            HumanMessage(content=query),
        ]

        tool_calls_log = []

        for _ in range(self.max_iterations):
            response = llm_with_tools.invoke(messages)

            if not response.tool_calls:
                return AgentResult(
                    answer=response.content,
                    skill_used=skill.name,
                    tool_calls=tool_calls_log,
                )

            messages.append(response)

            for tool_call in response.tool_calls:
                tool = next(t for t in tools if t.name == tool_call["name"])
                result = tool.invoke(tool_call["args"])
                tool_calls_log.append({
                    "name": tool_call["name"],
                    "args": tool_call["args"],
                    "result": result,
                })
                messages.append(AIMessage(
                    content=str(result),
                    name=tool_call["name"],
                ))

        return AgentResult(
            answer="Max iterations reached",
            skill_used=skill.name,
            tool_calls=tool_calls_log,
            error="Max iterations exceeded",
        )
```

---

## Phase 4: SAP Connector

### 4.1 Connector Protocol

**app/connectors/base.py**
```python
from typing import Protocol, Any

class BWConnector(Protocol):
    def execute(self, query: str) -> list[dict[str, Any]]: ...
    def close(self) -> None: ...
```

### 4.2 Mock Connector

**app/connectors/mock.py**
```python
from typing import Any

class MockBWConnector:
    """Mock connector for development without SAP."""

    def __init__(self) -> None:
        self._data = self._load_mock_data()

    def _load_mock_data(self) -> dict[str, list[dict]]:
        return {
            "documents": [
                {"DOCNR": "100500", "GJAHR": "2024", "PRCTR": "", "STATUS": "PSA"},
                {"DOCNR": "100501", "GJAHR": "2024", "PRCTR": "PC001", "STATUS": "CUBE"},
            ],
            "requests": [
                {"REQUEST": "REQU_001", "STATUS": "G", "RECORDS": 1000},
                {"REQUEST": "REQU_002", "STATUS": "R", "ERROR": "PRCTR initial not allowed"},
            ],
        }

    def execute(self, query: str) -> list[dict[str, Any]]:
        query_lower = query.lower()
        if "docnr" in query_lower:
            return self._data["documents"]
        if "request" in query_lower:
            return self._data["requests"]
        return []

    def close(self) -> None:
        pass
```

---

## Phase 5: Financial Skill (MVP)

### 5.1 Tools

**app/skills/financial/tools.py**
```python
from typing import Any
from pydantic import BaseModel, Field
from app.connectors.base import BWConnector

class DataPathInput(BaseModel):
    doc_number: str = Field(description="Document number to trace")
    fiscal_year: str | None = Field(default=None, description="Fiscal year")

class LoadStatusInput(BaseModel):
    request_id: str = Field(description="BW request ID")

class FinancialTools:
    def __init__(self, connector: BWConnector) -> None:
        self.conn = connector

    def find_data_path(self, doc_number: str, fiscal_year: str | None = None) -> dict[str, Any]:
        """Trace document through BW layers."""
        filters = f"DOCNR = '{doc_number}'"
        if fiscal_year:
            filters += f" AND GJAHR = '{fiscal_year}'"

        results = self.conn.execute(f"SELECT * WHERE {filters}")

        if not results:
            return {"found": False, "doc_number": doc_number}

        doc = results[0]
        return {
            "found": True,
            "doc_number": doc_number,
            "current_layer": doc.get("STATUS", "UNKNOWN"),
            "profit_center": doc.get("PRCTR", ""),
            "diagnosis": "Missing profit center" if not doc.get("PRCTR") else "OK",
        }

    def check_load_status(self, request_id: str) -> dict[str, Any]:
        """Check BW request status."""
        results = self.conn.execute(f"SELECT * WHERE REQUEST = '{request_id}'")

        if not results:
            return {"found": False, "request_id": request_id}

        req = results[0]
        return {
            "found": True,
            "request_id": request_id,
            "status": req.get("STATUS"),
            "error": req.get("ERROR"),
        }
```

### 5.2 Skill Implementation

**app/skills/financial/skill.py**
```python
from pathlib import Path
from app.core.skill import Skill, Tool
from app.connectors.base import BWConnector
from app.skills.financial.tools import FinancialTools, DataPathInput, LoadStatusInput

SYSTEM_PROMPT = """You are an SAP BW Financial expert. You help diagnose data issues in financial reporting.

When a user reports missing data:
1. Use find_data_path to trace the document through BW layers
2. Check for common issues: missing profit center, cost center, or GL account
3. If data is stuck, use check_load_status to find errors

Always explain the root cause and suggest concrete solutions.

Context from knowledge base:
{context}
"""

class FinancialSkill:
    name = "financial"
    description = "SAP BW Financial diagnostics for GL, cost centers, profit centers"

    def __init__(self, connector: BWConnector, knowledge_path: Path | None = None) -> None:
        self.tools = FinancialTools(connector)
        self.knowledge_path = knowledge_path or Path(__file__).parent / "knowledge"
        self._knowledge_cache: str | None = None

    def get_tools(self) -> list[Tool]:
        return [
            Tool(
                name="find_data_path",
                description="Trace a financial document through BW data layers (PSA→DSO→Cube)",
                func=self.tools.find_data_path,
                args_schema=DataPathInput,
            ),
            Tool(
                name="check_load_status",
                description="Check the status of a BW load request",
                func=self.tools.check_load_status,
                args_schema=LoadStatusInput,
            ),
        ]

    def get_system_prompt(self, context: str = "") -> str:
        return SYSTEM_PROMPT.format(context=context or "No additional context.")

    def get_context(self, query: str) -> str:
        # MVP: Return static knowledge
        # Production: RAG similarity search
        if self._knowledge_cache is None:
            self._knowledge_cache = self._load_knowledge()
        return self._knowledge_cache

    def _load_knowledge(self) -> str:
        knowledge_file = self.knowledge_path / "common_errors.md"
        if knowledge_file.exists():
            return knowledge_file.read_text()
        return ""
```

### 5.3 Knowledge Base

**app/skills/financial/knowledge/common_errors.md**
```markdown
# Common Financial Data Issues in SAP BW

## Missing Profit Center (PRCTR)
- **Symptom**: Document in PSA/DSO but not in reporting cube
- **Cause**: Profit center field is initial (empty) in source document
- **Solution**: Fill profit center in ERP (FB02), re-run delta load

## Cost Center Derivation Failed
- **Symptom**: Cost center shows as "#" or initial
- **Cause**: Derivation rule in transformation couldn't find mapping
- **Solution**: Check derivation rules, update mapping table

## GL Account Not in Hierarchy
- **Symptom**: Data loads but doesn't appear in reports
- **Cause**: GL account not assigned to reporting hierarchy
- **Solution**: Add account to hierarchy in BW, rebuild aggregates
```

---

## Phase 6: API Layer

### 6.1 Schemas

**app/api/schemas.py**
```python
from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str
    skill: str | None = None  # Optional skill override

class QueryResponse(BaseModel):
    answer: str
    skill_used: str
    tool_calls: list[dict]
    error: str | None = None

class HealthResponse(BaseModel):
    status: str
    skills: list[str]
```

### 6.2 Routes

**app/api/routes.py**
```python
from fastapi import APIRouter, Depends
from app.api.schemas import QueryRequest, QueryResponse, HealthResponse
from app.core.agent import SkillAgent
from app.dependencies import get_agent

router = APIRouter(prefix="/api/v1")

@router.get("/health", response_model=HealthResponse)
def health(agent: SkillAgent = Depends(get_agent)) -> HealthResponse:
    return HealthResponse(
        status="healthy",
        skills=agent.registry.list_skills(),
    )

@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest, agent: SkillAgent = Depends(get_agent)) -> QueryResponse:
    result = agent.run(request.query)
    return QueryResponse(
        answer=result.answer,
        skill_used=result.skill_used,
        tool_calls=result.tool_calls,
        error=result.error,
    )
```

### 6.3 Dependencies

**app/dependencies.py**
```python
from functools import lru_cache
from app.config import get_settings
from app.llm.factory import create_llm
from app.core.registry import SkillRegistry
from app.core.agent import SkillAgent
from app.connectors.mock import MockBWConnector
from app.skills.financial.skill import FinancialSkill

@lru_cache
def get_agent() -> SkillAgent:
    settings = get_settings()
    llm = create_llm(settings)

    connector = MockBWConnector()
    registry = SkillRegistry()
    registry.register(FinancialSkill(connector))

    return SkillAgent(llm, registry)
```

### 6.4 Main Entry Point

**main.py**
```python
from fastapi import FastAPI
from app.api.routes import router
from app.config import get_settings

def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Skillian",
        description="SAP BW AI Assistant",
        version="0.1.0",
        debug=settings.debug,
    )
    app.include_router(router)
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

---

## Phase 7: Testing

### 7.1 Fixtures

**tests/conftest.py**
```python
import pytest
from app.connectors.mock import MockBWConnector
from app.skills.financial.skill import FinancialSkill
from app.core.registry import SkillRegistry

@pytest.fixture
def connector() -> MockBWConnector:
    return MockBWConnector()

@pytest.fixture
def financial_skill(connector: MockBWConnector) -> FinancialSkill:
    return FinancialSkill(connector)

@pytest.fixture
def registry(financial_skill: FinancialSkill) -> SkillRegistry:
    reg = SkillRegistry()
    reg.register(financial_skill)
    return reg
```

### 7.2 Skill Tests

**tests/test_skills.py**
```python
from app.skills.financial.skill import FinancialSkill

def test_financial_skill_tools(financial_skill: FinancialSkill) -> None:
    tools = financial_skill.get_tools()
    assert len(tools) == 2
    assert tools[0].name == "find_data_path"

def test_find_data_path(financial_skill: FinancialSkill) -> None:
    result = financial_skill.tools.find_data_path("100500")
    assert result["found"] is True
    assert result["diagnosis"] == "Missing profit center"
```

---

## MVP Milestones

| Milestone | Deliverable | Acceptance Criteria |
|-----------|-------------|---------------------|
| **M1** | Project setup | uv init, dependencies, config loading |
| **M2** | LLM factory | Ollama working locally |
| **M3** | Core framework | Skill protocol, registry, basic agent |
| **M4** | Financial skill | Tools working with mock connector |
| **M5** | API | /health and /query endpoints |
| **M6** | Integration | End-to-end query flow working |
| **M7** | Tests | >80% coverage on core modules |

## Post-MVP Enhancements

1. **RAG with ChromaDB** - Vector similarity search for knowledge
2. **Additional Skills** - Sales, Inventory, Controlling
3. **Real SAP Connector** - HANA/RFC integration
4. **Streaming Responses** - Server-sent events for real-time output
5. **Authentication** - API key or OAuth
6. **Observability** - Structured logging, metrics, tracing
