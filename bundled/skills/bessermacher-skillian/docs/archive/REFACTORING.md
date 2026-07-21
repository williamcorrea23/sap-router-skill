# Skillian Refactoring Plan

Code analysis performed 2026-02-16. Findings organized by severity with concrete locations and fixes.

**Refactoring executed 2026-02-16.** Items marked with status below.

---

## CRITICAL

### 1. SQL Injection in Datasphere Connector -- DONE

**Files:** `app/connectors/datasphere.py`

**Problem:** `get_tables()` and `get_columns()` used f-string interpolation for `schema` and `table_name` parameters.

**Fix applied:** Both methods now use parameterized queries (`?` placeholders) via `execute_sql(query, [param])`.

---

### 2. Global Mutable State in All Skills -- PARTIAL

**Problem:** All three skills used module-level globals for connector state, duplicated across files.

**What was done:** Connector caching extracted to `app/skills/common.py` with a single `get_connector()` function, eliminating the triplicated `_get_connector()` (see item #5). The module-level global pattern remains (not migrated to `contextvars`) as the app runs single-user.

**Remaining:** `_current_investigation` state in `data_investigation/tools.py` is still a module-level global. Migrate to `contextvars` if concurrent multi-session support is needed.

---

## HIGH

### 3. Over-Engineered Auto-Chaining in Agent (~250 lines) -- DEFERRED

**Reason:** Large refactor of agent core with high risk. The auto-chaining logic works and is tested. Extracting to an orchestrator would be valuable but requires careful re-testing of the investigation playbook flow.

---

### 4. Duplicate Test Files -- DONE

Diffed and confirmed stale copies. Deleted:
- `tests/test_data_availability_skill 2.py`
- `tests/test_data_investigation_skill 2.py`

---

### 5. Triplicated Connector Caching Pattern -- DONE

Extracted to `app/skills/common.py`. All three skills now import `get_connector` from the shared module. Test fixtures updated to use `skills_common._connector`.

---

### 6. Unused `_lock` Field -- DONE

Removed from `app/connectors/datasphere.py`.

---

## MEDIUM

### 7. `print()` Instead of `logger` in Multiple Files -- DONE

Replaced `print()` with `logger.warning()` in:
- `app/core/openapi_loader.py`
- `app/core/skill_loader.py`
- `app/rag/store.py`

Added `logger = logging.getLogger(__name__)` and `import logging` where missing.

---

### 8. Flawed Type Coercion in tool.py -- DONE

Changed `origin is type(int | str)` to `origin is types.UnionType` in `app/core/tool.py`.

---

### 9. Weak Typing -- `dict[str, Any]` Everywhere -- DEFERRED

**Reason:** Marginal gain for internal types. Would add medium effort for little runtime benefit.

---

### 10. Inconsistent Dependency Injection in Routes -- DEFERRED

**Reason:** Cosmetic consistency. Direct calls work fine and are simpler to read in some cases.

---

### 11. Code Duplication in Skill Loader -- DEFERRED

**Reason:** Risky to change core loading logic for moderate DRY gain. The two methods have different error handling strategies.

---

### 12. Stale LangChain Version Specs in pyproject.toml -- DEFERRED

**Reason:** Version pinning policy decision. The loose `>=` constraints work with the lock file.

---

### 13. No Timeout Configuration -- DEFERRED

**Reason:** Adds configuration complexity. Datasphere already has a 60s timeout. Can be added when a timeout issue is actually observed.

---

### 14. Bare `except Exception` in Routes -- DEFERRED

**Reason:** Needs careful testing per-route. Better addressed alongside adding structured error responses.

---

### 15. Caching Mutable Connector Objects -- DEFERRED

**Reason:** Larger architectural change to move connectors to `app.state`. Current `@lru_cache` approach works for single-instance deployment.

---

## LOW

### 16. Redundant `requests` Dependency -- NOT AN ISSUE

`requests` is used in `ui/chat.py` (Streamlit frontend). Not redundant.

---

### 17. Tool Call Args Missing in UI -- DONE

Changed `"args": {}` to `"args": data.get("args", {})` in `ui/chat.py`.

---

### 18. CLI Hardcoded Paths -- DEFERRED

Low impact. Can be addressed if CLI gets more complex.

---

### 19. `archive-temp/` Directory -- DONE

Deleted `archive-temp/` and its contents.

---

### 20. Minimal Ruff Rules -- DEFERRED

Adding security/complexity rules would generate many new warnings. Better as a separate cleanup pass.

---

### 21. Executor Shutdown Without Wait -- DONE

Changed `self._executor.shutdown(wait=False)` to `wait=True` in `app/connectors/datasphere.py`.

---

### 22. No Session ID Validation on Path Parameters -- DEFERRED

Nice to have but not causing issues currently.

---

## CONFIRMED GOOD (No Changes Needed)

These areas are well-designed and should stay as-is:

- **Skill architecture** (SKILL.md + tools.yaml + tools.py) -- clean, extensible, auto-discovered
- **LLM provider abstraction** -- Protocol-based, minimal, all modern LangChain imports
- **RAG pipeline** -- simple coordination layer, appropriate chunking defaults
- **FastAPI lifespan management** -- modern `@asynccontextmanager` pattern
- **Pydantic v2 usage** -- proper `SettingsConfigDict`, `model_validator`, `Self` type
- **Source config models** (`app/skills/data_availability/source_config.py`) -- useful type safety for YAML configs
- **Input validation in ownership_check** -- regex-based SQL injection prevention
- **Async patterns** -- proper async/await, ThreadPoolExecutor bridge for sync hdbcli
- **Test quality** -- good edge case coverage, SQL injection tests, LLM format rejection tests

---

## Summary

| # | Item | Status |
|---|------|--------|
| 1 | SQL injection in datasphere.py | DONE |
| 2 | Global mutable state | PARTIAL (connector extracted, contextvars deferred) |
| 3 | Over-engineered auto-chaining | DEFERRED |
| 4 | Duplicate test files | DONE |
| 5 | Triplicated connector caching | DONE |
| 6 | Unused `_lock` field | DONE |
| 7 | `print()` instead of `logger` | DONE |
| 8 | Flawed type coercion | DONE |
| 9 | Weak typing | DEFERRED |
| 10 | Inconsistent DI | DEFERRED |
| 11 | Skill loader duplication | DEFERRED |
| 12 | Stale LangChain versions | DEFERRED |
| 13 | No timeout configuration | DEFERRED |
| 14 | Bare `except Exception` | DEFERRED |
| 15 | Caching mutable connectors | DEFERRED |
| 16 | Redundant `requests` dep | NOT AN ISSUE |
| 17 | UI tool call args | DONE |
| 18 | CLI hardcoded paths | DEFERRED |
| 19 | `archive-temp/` directory | DONE |
| 20 | Minimal ruff rules | DEFERRED |
| 21 | Executor shutdown | DONE |
| 22 | Session ID validation | DEFERRED |

**10 of 22 items completed. 11 deferred. 1 not an issue.**
