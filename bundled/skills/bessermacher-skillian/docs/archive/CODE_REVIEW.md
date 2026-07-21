# Skillian Code Review & Refactoring Guide

**Date:** 2026-02-01
**Reviewer:** Claude Code
**Project Version:** 0.1.0 (MVP)

This document provides a comprehensive analysis of the Skillian codebase and serves as the starting point for refactoring and optimization efforts.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Project Overview](#project-overview)
3. [Critical Issues](#critical-issues)
4. [Architecture Analysis](#architecture-analysis)
5. [Code Quality Issues](#code-quality-issues)
6. [Performance Optimizations](#performance-optimizations)
7. [Testing Gaps](#testing-gaps)
8. [Best Practices Alignment](#best-practices-alignment)
9. [Refactoring Roadmap](#refactoring-roadmap)
10. [Appendix: File Reference](#appendix-file-reference)

---

## Executive Summary

### Overall Assessment

| Category | Score | Notes |
|----------|-------|-------|
| Architecture | 8/10 | Clean, well-structured, minor DI issues |
| Security | 6/10 | CORS, rate limiting, error exposure |
| Performance | 7/10 | Missing pagination, pool limits |
| Code Quality | 8/10 | Good patterns, needs logging |
| Testing | 7/10 | Good coverage, mock quality issues |
| Best Practices | 8/10 | Modern Python, minor gaps |

**Verdict:** Well-architected MVP with production-readiness gaps that should be addressed before deployment.

### Key Strengths

- Protocol-based design for extensibility
- Modern Python 3.13+ syntax throughout
- Clean separation of concerns
- Comprehensive async implementation
- Good test structure with fixtures

### Key Weaknesses

- Security configuration not production-ready (CORS)
- No proper logging infrastructure
- Resource cleanup gaps on shutdown
- Architectural decisions needed (stateless vs sessions)

### Important Context

> **This is an internal MVP tool.** Many "best practice" suggestions would be over-engineering at this stage. The roadmap below distinguishes between actual bugs vs. nice-to-haves.

---

## Project Overview

### Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.13 |
| Framework | FastAPI + LangChain |
| Database | PostgreSQL + pgvector |
| LLM | Ollama (dev) / Claude (prod) |
| Package Manager | uv |

### Architecture

```
User Request
    ↓
FastAPI Route (/chat)
    ↓
Agent.process()
    ├── Converts conversation to LangChain messages
    ├── Calls LLM with bound tools
    ├── Executes tool calls (query_source, compare_sources)
    └── Returns response
```

### Codebase Statistics

- **Source files:** ~25 Python modules
- **Test files:** 14 test modules (~2000 lines)
- **Total lines:** ~5,755 lines
- **Skills implemented:** 1 (data_analyst)

---

## Critical Issues

### 1. Security Vulnerabilities

#### 1.1 CORS Configuration (HIGH)

**Location:** `main.py:59-65`

```python
# CURRENT - INSECURE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows any origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Problem:** Open CORS allows any website to make authenticated requests to the API.

**Fix:**
```python
# RECOMMENDED
from app.config import get_settings

settings = get_settings()
allowed_origins = (
    ["*"] if settings.is_development
    else ["https://your-production-domain.com"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
```

#### 1.2 No Rate Limiting (MEDIUM)

**Location:** `app/api/routes.py`

**Problem:** API endpoints have no throttling, allowing abuse.

**Fix:** Add `slowapi` or custom middleware:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request, ...):
    ...
```

#### 1.3 Error Message Exposure (MEDIUM)

**Location:** `app/api/routes.py:126`

```python
# CURRENT - EXPOSES INTERNALS
except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))
```

**Problem:** Exception details may leak sensitive information.

**Fix:**
```python
# RECOMMENDED
import logging
logger = logging.getLogger(__name__)

except Exception as e:
    logger.exception("Chat processing failed")
    raise HTTPException(
        status_code=500,
        detail="An internal error occurred. Please try again."
    )
```

### 2. Python Version Mismatch

| File | States |
|------|--------|
| `CLAUDE.md` | Python 3.14+ |
| `pyproject.toml:5` | `>=3.13,<3.14` |
| `pyproject.toml:43` | `target-version = "py313"` |

**Fix:** Update `CLAUDE.md` to reflect actual version:
```markdown
- Python 3.13+
```

### 3. Stateless Chat Architecture (DESIGN DECISION NEEDED)

**Location:** `app/api/routes.py:102-126`, `ui/chat.py:76-77`

**Current behavior:**
- `/chat` endpoint creates a **new Agent per request**
- Streamlit UI calls `/chat`, not `/sessions`
- Result: No conversation memory between messages on server side

```python
# routes.py - new agent every request
@router.post("/chat")
async def chat(
    request: ChatRequest,
    agent: Agent = Depends(get_agent),  # Creates new agent!
):
```

**Questions to answer:**
1. Is stateless `/chat` intentional for simplicity?
2. Should Streamlit use the sessions API instead?
3. Is the sessions feature needed at all for MVP?

### 4. Duplicate Router Mounting (BUG OR INTENTIONAL?)

**Location:** `main.py:68-71`

```python
# Routes available at BOTH /api/v1/health AND /health
app.include_router(router, prefix="/api/v1")
app.include_router(router)  # Also at root - why?
```

**Recommendation:** Remove duplicate if unintentional, or document if intentional.

### 5. Incomplete Health Check

**Location:** `app/api/routes.py:43-66`

**Problem:** Health endpoint checks vector store but not business database.

**Fix:** Add business database health check to the endpoint.

### 6. No Fail-Fast Configuration (HIGH)

**Location:** `app/config.py`

**Problem:** App starts successfully even with missing required API keys. Fails later at runtime when LLM is called.

**Fix:**
```python
from pydantic import model_validator

class Settings(BaseSettings):
    # ...existing fields...

    @model_validator(mode='after')
    def validate_provider_config(self) -> 'Settings':
        if self.llm_provider == 'anthropic' and not self.anthropic_api_key:
            raise ValueError('ANTHROPIC_API_KEY required when LLM_PROVIDER=anthropic')
        if self.llm_provider == 'openai' and not self.openai_api_key:
            raise ValueError('OPENAI_API_KEY required when LLM_PROVIDER=openai')
        return self
```

---

## Architecture Analysis

### What's Good

1. **Protocol-based Design**
   - `Skill` protocol in `app/core/skill.py` enables duck typing
   - `LLMProvider` protocol allows easy provider switching
   - Clean interface contracts

2. **Factory Pattern**
   - `create_llm_provider()` cleanly abstracts provider creation
   - `match` statement for provider selection

3. **Separation of Concerns**
   - Clear module boundaries (core, api, llm, rag, skills)
   - Single responsibility per module

4. **Async Throughout**
   - Consistent use of async/await
   - asyncpg for database operations

### Issues to Address

#### 3.1 Dependency Injection Limitations

**Location:** `app/dependencies.py`

**Problem:** Heavy `@lru_cache` usage creates global singletons that are difficult to reset in tests.

```python
# CURRENT
@lru_cache
def get_skill_registry() -> SkillRegistry:
    registry = SkillRegistry()
    skill = get_data_analyst_skill()
    registry.register(skill)
    return registry
```

**Impact:**
- Tests may share state unintentionally
- Cannot easily swap implementations
- Memory not released until process ends

**Assessment:** This is **not a problem worth fixing** for an MVP.
- The `lru_cache` approach is simple and works
- Tests can clear cache with `get_skill_registry.cache_clear()`
- A full DI container would add complexity without clear benefit

**If it becomes a problem later:** Add cache clearing in test fixtures.

#### 3.2 Resource Cleanup Missing

**Location:** `main.py` lifespan handler

**Problem:** Database connections are not closed on shutdown.

```python
# CURRENT
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... startup ...
    yield
    print("Shutting down...")  # No cleanup!
```

**Fix:**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    # ... rest of startup ...

    yield

    # Cleanup
    from app.dependencies import get_business_connector
    from app.db.connection import close_db

    connector = get_business_connector()
    await connector.close()
    await close_db()
    print("Shutdown complete")
```

#### 3.3 In-Memory Cache Scalability

**Location:** `app/core/comparison_engine.py:59-93`

**Observation:** `ComparisonCache` uses in-memory dict, won't work with multiple instances.

```python
class ComparisonCache:
    def __init__(self, ttl_seconds: int = 3600):
        self._cache: dict[str, ComparisonResult] = {}  # In-memory only
```

**Assessment:** This is **fine for MVP**.
- Internal tool likely runs single instance
- Adding Redis adds operational complexity
- Only abstract when you actually need multiple backends (YAGNI)

**When to revisit:** If/when deploying multiple API instances behind load balancer.

#### 3.4 Inefficient Session Listing

**Location:** `app/api/sessions.py:179-197`

**Problem:** `list_all()` creates a full Agent for every session, even for metadata-only listing.

```python
async def list_all(self) -> list[Session]:
    # ...
    for db_session in db_sessions:
        agent = self._agent_factory()  # Unnecessary!
        sessions.append(Session(..., agent=agent, ...))
```

**Fix:** Create lightweight metadata-only response:
```python
@dataclass
class SessionMetadata:
    session_id: str
    created_at: datetime
    last_accessed: datetime
    message_count: int

async def list_all(self) -> list[SessionMetadata]:
    result = await self._db.execute(select(SessionModel))
    return [
        SessionMetadata(
            session_id=str(s.id),
            created_at=s.created_at,
            last_accessed=s.last_accessed,
            message_count=s.message_count,
        )
        for s in result.scalars().all()
    ]
```

---

## Code Quality Issues

### 4.1 Logging Infrastructure

**Problem:** Uses `print()` instead of proper logging.

**Locations:**
- `main.py:25-42`
- `app/rag/store.py:118`

**Current:**
```python
print(f"Starting {settings.app_name} v{settings.app_version}")
print(f"Warning: RAG initialization failed: {e}")
```

**Fix:** Use stdlib `logging` (simpler than structlog for MVP):

```python
# app/logging.py
import logging
import sys

def setup_logging(debug: bool = False):
    level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
    )

# main.py
from app.logging import setup_logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.debug)

    logger = logging.getLogger(__name__)
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    # ...
```

**Note:** Don't use `structlog` - it adds a dependency and learning curve without significant benefit for an MVP.

### 4.2 Type Hint Issues

| Issue | Location | Fix |
|-------|----------|-----|
| `callable` should be `Callable` | `app/api/sessions.py:68` | `from collections.abc import Callable` |
| Empty class uses `pass` | `app/skills/data_analyst/tools.py:20` | Use `...` instead |

**Before:**
```python
class ListSourcesInput(BaseModel):
    pass
```

**After:**
```python
class ListSourcesInput(BaseModel):
    """Input for list_sources tool - no parameters needed."""
    ...
```

### 4.3 Exception Handling

**Problem:** Generic exception handling swallows errors silently.

**Locations:**
- `app/api/routes.py:52` - health check
- `app/connectors/postgres.py:69` - health check
- `main.py:41` - RAG initialization

**Current:**
```python
except Exception:
    doc_count = 0  # Silently fails
```

**Fix:** Log errors, use specific exceptions:
```python
except (DatabaseError, ConnectionError) as e:
    logger.warning("health_check_failed", error=str(e))
    doc_count = 0
```

### 4.4 Missing Docstrings

Several public methods lack docstrings:
- `ComparisonCache.size()`
- `QueryEngine._build_query()` (has minimal docstring)
- Various `__init__` methods

---

## Performance Optimizations

### 5.1 Database Connection Pool

**Location:** `app/connectors/postgres.py:23`

**Problem:** No pool size limits or timeouts.

**Current:**
```python
self._pool = await asyncpg.create_pool(self._url)
```

**Fix:**
```python
self._pool = await asyncpg.create_pool(
    self._url,
    min_size=2,
    max_size=10,
    max_inactive_connection_lifetime=300,
    command_timeout=60,
)
```

### 5.2 VectorStore Engine Creation

**Location:** `app/rag/store.py:192-210`

**Problem:** Creates new SQLAlchemy engine on every `count()` call.

**Current:**
```python
@property
def count(self) -> int:
    # Creates engine every time!
    engine = create_engine(connection)
    with engine.connect() as conn:
        ...
```

**Fix:** Reuse engine from initialization or cache it:
```python
def __post_init__(self):
    # ... existing code ...
    self._sync_engine = create_engine(connection)

@property
def count(self) -> int:
    with self._sync_engine.connect() as conn:
        ...
```

### 5.3 Missing Pagination

**Location:** `app/api/routes.py:195-209`

**Problem:** `list_sessions()` returns all sessions without pagination.

**Fix:**
```python
@router.get("/sessions")
async def list_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session_store: SessionStore = Depends(get_session_store),
) -> SessionListResponse:
    sessions = await session_store.list_paginated(skip=skip, limit=limit)
    total = await session_store.count()
    return SessionListResponse(
        sessions=[...],
        total=total,
        skip=skip,
        limit=limit,
    )
```

### 5.4 Query Result Limits

**Location:** `app/skills/data_analyst/tools.py:227`

**Current:** Hard-coded 100 row limit.

**Improvement:** Make configurable and add proper pagination:
```python
class QuerySourceInput(BaseModel):
    # ... existing fields ...
    limit: int = Field(default=100, le=1000, description="Max rows to return")
    offset: int = Field(default=0, ge=0, description="Rows to skip")
```

---

## Testing Gaps

### 6.1 Mock Embeddings Quality

**Location:** `tests/conftest.py:181-193`

**Problem:** Mock embeddings return identical vectors for all inputs.

```python
def embed_documents(self, texts: list[str]) -> list[list[float]]:
    return [[0.1] * self.dimension for _ in texts]  # All same!
```

**Impact:** All documents have identical similarity scores in tests.

**Fix:**
```python
import hashlib

def embed_documents(self, texts: list[str]) -> list[list[float]]:
    embeddings = []
    for text in texts:
        # Generate deterministic but unique embedding per text
        hash_val = hashlib.md5(text.encode()).digest()
        embedding = [b / 255.0 for b in hash_val[:self.dimension]]
        # Pad or truncate to dimension
        embedding = (embedding * (self.dimension // len(embedding) + 1))[:self.dimension]
        embeddings.append(embedding)
    return embeddings
```

### 6.2 Missing Test Categories

| Category | Status | Notes |
|----------|--------|-------|
| Unit tests | ✓ Good | Core modules well covered |
| Integration tests | Partial | Marked, skipped by default |
| Error path tests | Missing | Need negative test cases |
| Security tests | Missing | SQL injection, XSS, auth |
| Performance tests | Missing | Load testing, benchmarks |

### 6.3 Test Configuration

**Location:** `pyproject.toml:52`

Integration tests skipped by default:
```toml
addopts = "-v --tb=short -m 'not integration'"
```

**Recommendation:** Add CI job that runs integration tests separately.

---

## Best Practices Alignment

### What's Already Good

| Practice | Implementation |
|----------|----------------|
| Modern type hints | `list[str]`, `str \| None` |
| Match statements | LLM factory, message conversion |
| Protocols over ABC | Skill, LLMProvider |
| Frozen dataclasses | Tool definition |
| Pydantic validation | Input schemas, Settings |
| Async/await | Throughout codebase |

### What Needs Improvement (MVP Scope)

| Area | Current | Recommended | Status |
|------|---------|-------------|--------|
| Logging | `print()` | stdlib `logging` | ✅ Done |
| Config validation | Basic | Add `@model_validator` for provider keys | ✅ Done |
| Health checks | Partial | Include business DB | ✅ Done |
| Error responses | Generic | Log + sanitize | ✅ Done |
| API versioning | Dual mount | Remove duplicate | ✅ Done |

### What to Defer (Not Needed for MVP)

| Area | Why Defer |
|------|-----------|
| Database migrations (Alembic) | Schema is simple, only one table |
| Structured error schema | Basic error handling is sufficient |
| Redis caching | Single instance is fine |
| OpenTelemetry | Logging is enough for now |

---

## Refactoring Roadmap

> **Philosophy:** This is an internal MVP tool. Avoid over-engineering. Add complexity only when actually needed.

### Critical Re-evaluation Notes

#### What Was Over-Engineered in Initial Review

| Suggestion | Why It's Over-Engineering | Better Approach |
|------------|---------------------------|-----------------|
| Redis cache | Adds ops complexity; internal tool has few users | Keep in-memory; add Redis only when scaling horizontally |
| Rate limiting | Internal tool behind corp network doesn't need it | Defer; use nginx/traefik if ever needed |
| Kubernetes | Docker Compose works fine | Don't do yet |
| OpenTelemetry | Too complex for MVP | Simple logging is enough |
| structlog | Extra dependency, learning curve | Use stdlib `logging` |
| Full DI refactor | `lru_cache` works; tests can clear cache | Keep current approach |
| Pagination | Few sessions in MVP | Defer until needed |
| Alembic | Schema is simple (one table) | Defer until schema evolves |

#### What Was Missed in Initial Review

| Issue | Location | Status |
|-------|----------|--------|
| `/chat` is stateless | `routes.py:102` | ⏳ Design decision needed |
| Duplicate router mounting | `main.py:68-71` | ✅ Fixed (removed root mount) |
| Business DB not health-checked | `routes.py:43-66` | ✅ Fixed |
| Session GET recreates Agent | `sessions.py:126` | ⏳ Design decision needed |
| No fail-fast on bad config | `config.py` | ✅ Fixed |
| Streamlit ignores sessions | `ui/chat.py:76` | ⏳ Design decision needed |

---

### Revised Roadmap

### Tier 1: Must Fix (Actual Bugs) ✅ COMPLETED

| Task | File | Status |
|------|------|--------|
| Fix VectorStore.count() engine leak | `app/rag/store.py` | ✅ Done |
| Add resource cleanup on shutdown | `main.py` lifespan | ✅ Done |
| Add config validation (fail-fast) | `app/config.py` | ✅ Done |
| Add business DB health check | `app/api/routes.py` | ✅ Done |
| Connection pool limits | `app/connectors/postgres.py` | ✅ Done |

### Tier 2: Should Fix (Good Hygiene) ✅ COMPLETED

| Task | File | Status |
|------|------|--------|
| Replace print() with logging | `main.py` | ✅ Done |
| Fix CORS for production | `main.py` | ✅ Done |
| Remove duplicate router mount | `main.py` | ✅ Done (kept `/api/v1` only) |
| Fix type hint `callable` → `Callable` | `app/api/sessions.py` | ✅ Done |
| Improve error handling | `app/api/routes.py` | ✅ Done |
| Update Python version in docs | `CLAUDE.md` | ✅ Done |

### Tier 3: Design Decisions Needed

These require product decisions, not just code fixes.

---

## Tier 3 Deep Dive: Architecture Decisions

### Decision 1: Stateless `/chat` vs Session-Based Conversations

#### Current State
```
User → POST /chat → New Agent created → Response → Agent discarded
```

Each `/chat` request:
1. Creates a new `Agent` instance
2. Sets up system prompt from scratch
3. Has no memory of previous messages
4. Discards all context after responding

#### The Problem

The Streamlit UI stores conversation history client-side, but:
- Server has no memory between requests
- Each message is processed independently
- Multi-turn tool usage doesn't work properly
- LLM loses context for follow-up questions

**Example failure:**
```
User: "Compare FI and BPC for company 1000"
Assistant: [uses compare_sources tool, returns results]
User: "Show me the top differences"
Assistant: [has no idea what was compared - starts fresh]
```

#### Options

**Option A: Keep Stateless (Current)**

| Pros | Cons |
|------|------|
| Simple, no state management | No multi-turn conversations |
| Scales horizontally easily | Each request is isolated |
| No session cleanup needed | Can't do follow-up queries |
| Lower memory usage | Poor UX for complex analysis |

**Best for:** Simple single-question queries, stateless API consumers

**Option B: Auto-Create Session for `/chat`**

Change `/chat` to automatically create/use sessions:

```python
@router.post("/chat")
async def chat(request: ChatRequest):
    session_id = request.session_id or create_new_session()
    session = get_or_create_session(session_id)
    result = await session.agent.process(request.message)
    return ChatResponse(..., session_id=session_id)
```

| Pros | Cons |
|------|------|
| Transparent to clients | More complex server logic |
| Multi-turn works | Need session cleanup strategy |
| Better UX | Higher memory usage |
| Compatible with existing clients | Session management overhead |

**Best for:** Interactive conversations, data analysis workflows

**Option C: Require Sessions (Remove stateless `/chat`)**

Only allow session-based conversations:

| Pros | Cons |
|------|------|
| Consistent behavior | Breaking change for clients |
| Clear API contract | Forced complexity for simple queries |
| Proper conversation model | Extra round-trip to create session |

#### Recommendation

**For an SAP data diagnostic tool: Option B (auto-session)** is likely best because:
- Users often ask follow-up questions ("now show me company 2000")
- Tool results need context ("explain that difference")
- Analysis is iterative, not single-shot

---

### Decision 2: Streamlit Session Integration

#### Current State

```
[Streamlit UI]
    ↓
st.session_state.messages (client-side)
    ↓
POST /api/v1/chat (no session_id)
    ↓
[Server: New Agent, no history]
```

The UI maintains its own message history but doesn't use server sessions.

#### Options

**Option A: Keep Client-Side Only**

| Pros | Cons |
|------|------|
| Simple, works now | History lost on refresh |
| No server dependency | Can't resume on another device |
| Fast (no DB calls) | Inconsistent with sessions API |

**Option B: Integrate with Sessions API**

```python
# ui/chat.py changes
if "session_id" not in st.session_state:
    response = requests.post(f"{backend_url}/api/v1/sessions", ...)
    st.session_state.session_id = response.json()["session_id"]
else:
    response = requests.post(
        f"{backend_url}/api/v1/sessions/{st.session_state.session_id}/chat",
        ...
    )
```

| Pros | Cons |
|------|------|
| Persistent history | More complex UI code |
| Resume on refresh | DB dependency |
| Server-side context | Latency for session lookups |
| Multi-device support | Session cleanup needed |

#### Recommendation

**Depends on Decision 1:**
- If you choose Option B (auto-session) for `/chat`, Streamlit integration becomes simpler
- If stateless, client-side only makes sense

---

### Decision 3: Is the Sessions Feature Needed?

#### Current Usage
- Sessions API exists (`/sessions`, `/sessions/{id}/chat`)
- Streamlit UI doesn't use it
- `/chat` endpoint is stateless

#### Options

**Option A: Remove Sessions (Simplify)**

Delete:
- `app/api/sessions.py`
- Session routes in `routes.py`
- `SessionModel` in database

| Pros | Cons |
|------|------|
| Less code to maintain | Lose multi-turn capability |
| Simpler architecture | Can't add it back easily |
| Smaller attack surface | Limits future UX |

**Option B: Keep and Use Sessions**

Integrate sessions into the main flow.

| Pros | Cons |
|------|------|
| Multi-turn works | More complexity |
| Feature already built | Need to finish integration |
| Better UX potential | Session management overhead |

**Option C: Keep but Defer**

Leave sessions code, don't integrate yet.

| Pros | Cons |
|------|------|
| Option preserved | Dead code in codebase |
| No immediate work | Confusing architecture |
| Defer decision | Technical debt |

#### Recommendation

**For MVP: Option A or C**
- If you need multi-turn now: Option B
- If single-query works: Option A (remove)
- If unsure: Option C (defer, but add TODO)

---

### Decision Summary Table

| Decision | Recommended | Effort | Status |
|----------|-------------|--------|--------|
| 1. Stateless vs Sessions | **B: Auto-session** | Medium | ✅ Done |
| 2. Streamlit integration | Follows from #1 | Low | ✅ Done |
| 3. Keep sessions feature? | **B: Keep and use** | Already built | ✅ Done (in use) |

### ✅ Implemented: "Make it Conversational"

Implementation completed:
1. ✅ Modified `/chat` to auto-create sessions (accepts optional `session_id`)
2. ✅ Updated Streamlit UI to store and use `session_id` from responses
3. ⏸️ Session TTL/cleanup - deferred (manual cleanup if needed)
4. ⏸️ Optimize Agent recreation - deferred until performance issues arise

### If You Choose: "Keep it Simple"

Implementation steps:
1. Remove sessions code entirely
2. Update docs to clarify single-turn nature
3. Ensure Streamlit client-side history works well
4. Accept limitation for MVP

---

| Question | Current State | Options |
|----------|---------------|---------|
| Should `/chat` have memory? | Stateless, new Agent per request | A) Keep stateless (simpler) B) Auto-create session |
| Should Streamlit use sessions? | Doesn't use server sessions | A) Keep client-side only B) Integrate with sessions API |
| Is session feature needed for MVP? | Built but unused by UI | A) Remove sessions feature B) Use it in UI |
| Optimize session Agent creation? | Creates new Agent on every GET | Only optimize if sessions are kept |

### Tier 4: Defer Until Needed (YAGNI)

| Task | When to Revisit |
|------|-----------------|
| Pagination | When you have >100 sessions |
| Redis cache | When running multiple instances |
| Rate limiting | When exposed to internet |
| Alembic migrations | When schema needs changes |
| Abstract cache backend | When actually need Redis |
| Advanced testing (security, perf) | Before production launch |

### Tier 5: Don't Do

| Task | Reason |
|------|--------|
| Kubernetes manifests | Docker Compose is sufficient |
| OpenTelemetry | Over-engineering for MVP |
| Full DI container | Current approach works |
| structlog | stdlib logging is sufficient |

---

## Appendix: File Reference

### Core Files

| File | Purpose | Lines |
|------|---------|-------|
| `main.py` | FastAPI entry point | 82 |
| `app/config.py` | Pydantic settings | 65 |
| `app/dependencies.py` | DI container | 127 |
| `app/core/agent.py` | Agent orchestration | 212 |
| `app/core/skill.py` | Skill protocol | 75 |
| `app/core/tool.py` | Tool dataclass | 60 |
| `app/core/registry.py` | Skill registry | ~150 |
| `app/core/query_engine.py` | SQL builder | 141 |
| `app/core/comparison_engine.py` | Data comparison | 339 |

### API Files

| File | Purpose | Lines |
|------|---------|-------|
| `app/api/routes.py` | REST endpoints | 275 |
| `app/api/schemas.py` | Pydantic models | ~200 |
| `app/api/sessions.py` | Session management | 203 |

### LLM Files

| File | Purpose | Lines |
|------|---------|-------|
| `app/llm/factory.py` | Provider factory | 58 |
| `app/llm/protocol.py` | LLMProvider protocol | ~50 |
| `app/llm/ollama.py` | Ollama implementation | ~50 |
| `app/llm/anthropic.py` | Claude implementation | ~50 |
| `app/llm/openai.py` | OpenAI implementation | ~50 |

### RAG Files

| File | Purpose | Lines |
|------|---------|-------|
| `app/rag/store.py` | Vector store wrapper | 211 |
| `app/rag/manager.py` | Knowledge ingestion | ~100 |
| `app/rag/embeddings.py` | Embeddings factory | ~50 |

### Skill Files

| File | Purpose | Lines |
|------|---------|-------|
| `app/skills/data_analyst/skill.py` | Skill implementation | ~100 |
| `app/skills/data_analyst/tools.py` | Tool implementations | 265 |

---

## Document History

| Date | Author | Changes |
|------|--------|---------|
| 2026-02-01 | Claude Code | Initial review |

---

*This document should be updated as refactoring progresses. Mark completed items and add new findings as they emerge.*
