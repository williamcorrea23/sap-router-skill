# Skillian - SAP BW AI Assistant

## Overview
Skillian is an AI-powered assistant for SAP BW data diagnostics. It uses a skill-based architecture where each skill (data_availability, data_investigation, ownership_check) provides domain-specific tools for querying and comparing SAP financial data.

## Tech Stack
- **Language**: Python 3.13
- **Framework**: FastAPI (backend API) + Streamlit (chat UI)
- **LLM**: LangChain with multiple providers (Ollama, Anthropic, OpenAI, custom OpenAI-compatible)
- **Database**: PostgreSQL with pgvector (vector store), async via SQLAlchemy + asyncpg
- **Business DB**: PostgreSQL (SAP BW data), optional SAP Datasphere via hdbcli
- **Package manager**: uv
- **Linter**: ruff
- **Testing**: pytest with pytest-asyncio

## Project Structure
```
main.py              # FastAPI app entrypoint
app/
  api/               # REST routes and schemas
    routes.py        # API endpoints (chat, sessions, knowledge, health)
    schemas.py       # Pydantic request/response models
    sessions.py      # PostgreSQL-backed session store (SessionStore, Session, SessionInfo)
  cli/               # Typer CLI (skillian command)
  config.py          # pydantic-settings configuration
  connectors/        # Database connectors (postgres, datasphere)
  core/
    agent.py         # Agent loop — unified _run_loop() async generator
    playbook.py      # InvestigationPlaybook — extracted auto-chain business logic
    registry.py      # SkillRegistry — skill/tool discovery and lookup
    skill_loader.py  # Loads skills from app/skills/<name>/ directories
    messages.py      # Conversation and Message types
    tool.py          # Tool abstraction (sync/async execution)
    yaml_tools.py    # YAML-based tool definition parser
  db/                # DB connection and models
  dependencies.py    # Dependency injection (wires config → Agent, SessionStore, etc.)
  llm/               # LLM provider factory (ollama, anthropic, openai, custom_openai)
  rag/               # RAG pipeline (embeddings, vector store, manager)
    embeddings.py    # Embeddings factory (ollama, openai, custom_openai; anthropic falls back to ollama)
  skills/            # Domain skills (data_availability, data_investigation, ownership_check)
    common.py        # Shared connector management for all skills
config/sources.yaml  # Data source definitions (tables, dimensions, measures)
database/            # SQL init and seed scripts
ui/chat.py           # Streamlit chat frontend
tests/               # pytest test suite
```

## Common Commands
```bash
# Run the API server
uv run uvicorn main:app --reload

# Run the Streamlit UI
uv run streamlit run ui/chat.py

# Run tests (unit only, skips integration)
uv run pytest

# Run tests with coverage
uv run pytest --cov=app --cov-report=term-missing

# Run integration tests (requires running databases)
uv run pytest -m integration

# Lint
uv run ruff check .
uv run ruff format .

# Docker (full stack)
docker compose up --build

# CLI
uv run skillian --help
```

## Configuration
All settings are in `app/config.py` via pydantic-settings, loaded from environment variables or `.env` file. Key settings:
- `LLM_PROVIDER`: ollama | anthropic | openai | custom_openai
- `LLM_TIMEOUT`: Seconds before LLM call times out (default 120)
- `TOOL_TIMEOUT`: Seconds before individual tool execution times out (default 60)
- `MAX_ITERATIONS`: Maximum agent loop iterations (default 15)
- `EMBEDDING_MODEL`: Override default embedding model per provider (optional)
- `DATABASE_URL`: PostgreSQL connection for vector store
- `BUSINESS_DATABASE_URL`: PostgreSQL connection for SAP BW data
- `DATASPHERE_*`: Optional SAP Datasphere connection settings

## Agent Architecture

The agent (`app/core/agent.py`) uses a unified `_run_loop()` async generator that yields SSE events. Both `process()` (non-streaming) and `process_stream()` (streaming) are thin wrappers over this single loop, eliminating duplication.

Key patterns:
- **Timeouts**: LLM calls and tool executions are wrapped with `asyncio.wait_for()` using configurable timeouts from settings
- **Cached tool names**: Tool names are stored as a `frozenset` at init for O(1) lookup
- **Playbook callback**: Business logic for auto-chaining investigation steps lives in `InvestigationPlaybook` (`app/core/playbook.py`), decoupled from the agent via a `ToolExecutor` callable
- **RAG context injection**: The agent accepts an optional `RAGManager` and injects relevant knowledge as a system message before each user query

### System Prompt Structure

The base system prompt (`agent.py:_setup_system_prompt`) uses structured markdown sections following prompt engineering best practices (see `docs/prompt-engineering-audit.md`):

1. **# Role** — identity and domain expertise
2. **# Instructions** — what the agent can do and when to use tools
3. **# Tool Usage Rules** — autonomous execution, persistence, investigation completion
4. **# Reasoning** — think before tool calls, reflect on results
5. **# Guardrails** — what NOT to do (never fabricate values, never call tools without required params)
6. **# Output Format** — structured format for investigation results (Problem, Findings, Root Cause, Recommended Actions)
7. **# Skill Domains** — auto-generated from all registered skills via `registry.get_combined_system_prompt()`

Each skill domain section includes its instructions, capabilities, when-to-use guidance, and few-shot examples with concrete tool call sequences.

## Skills Architecture
Skills live in `app/skills/<name>/` and contain:
- `SKILL.md` — skill description, instructions, and few-shot examples (injected into system prompt)
- `tools.yaml` — tool definitions (name, description, parameters)
- `tools.py` — tool implementations
- `knowledge/` — additional markdown docs for RAG ingestion

Skills are discovered and registered automatically by `app/core/registry.py` and `app/core/skill_loader.py`.

### SKILL.md Prompt Conventions
- **Instructions section**: Role definition, workflow steps, field aliases, domain reference data
- **Examples section**: Use `<examples>` / `<example>` tags with concrete tool call sequences showing exact arguments, expected results, and responses. These are injected into the system prompt as few-shot demonstrations via `skill_parser.py:_build_instructions()`
- Tool descriptions in `tools.yaml` should explain what the tool does, what it returns, and when to use it

### Request-scoped state
Skill tools that maintain state (e.g. `data_investigation`) use `contextvars.ContextVar` for request-scoped isolation, preventing cross-request leakage in concurrent scenarios.

## Sessions
Sessions are PostgreSQL-backed via `app/api/sessions.py`. `SessionStore` persists conversation history as JSONB. Listing sessions uses a lightweight `SessionInfo` dataclass (metadata only, no Agent created).

## Time Tracking

Every request is instrumented with timing data (`app/core/agent.py`). `AgentResponse.timing` contains:

- `total_seconds` — end-to-end request duration
- `llm_calls` — list of `{iteration, duration_seconds}` per LLM invocation
- `tool_calls` — list of `{tool, duration_seconds}` per tool execution

Streaming emits `llm_response` and augmented `tool_result` events with `duration_seconds`. The `done` event includes the full `timing` summary. The non-streaming `ChatResponse` also includes `timing` and per-tool `duration_seconds` in `ToolCall`.

## Testing Conventions
- Unit tests run by default (`pytest`), integration tests are marked with `@pytest.mark.integration`
- Async tests use `pytest-asyncio` with `asyncio_mode = "auto"`
- Test files follow `test_<module>.py` naming
