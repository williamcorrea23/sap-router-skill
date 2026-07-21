# Fix: DatasphereConnector Lazy Auto-Connect

**Date:** 2026-02-19
**Issue:** All tool calls (`check_data_availability`, `check_ownership`) fail immediately with `"Tool 'X' failed unexpectedly"`

## Root Cause

The `DatasphereConnector` is instantiated in `app/dependencies.py` but `connect()` is never called. Since the factory uses `@lru_cache` (sync), it cannot `await` the async `connect()`. Every tool call hits `execute_sql()` which raises `DatasphereError("Connector not connected")`, caught and masked as `"failed unexpectedly"` by the agent.

## Fix

Make `DatasphereConnector` lazy-connect on first use (matching the `PostgresConnector` pattern where `get_pool()` lazily creates the connection pool). This is safe because `connect()` is already idempotent.

---

## Changes

### File 1: `app/connectors/datasphere.py`

#### Change A: `execute_sql()` method (~line 115)

**Before:**
```python
        if self._connection is None:
            raise DatasphereError("Connector not connected. Call connect() first.")
```

**After:**
```python
        if self._connection is None:
            await self.connect()
```

#### Change B: `execute_many()` method (~line 165)

**Before:**
```python
        if self._connection is None:
            raise DatasphereError("Connector not connected. Call connect() first.")
```

**After:**
```python
        if self._connection is None:
            await self.connect()
```

---

### File 2: `tests/test_datasphere_connection.py`

#### Replace the `TestNotConnectedErrors` class (~line 242)

**Before:**
```python
class TestNotConnectedErrors:
    @pytest.mark.asyncio
    async def test_execute_sql_requires_connection(self, connector):
        with pytest.raises(DatasphereError, match="not connected"):
            await connector.execute_sql("SELECT 1")

    @pytest.mark.asyncio
    async def test_execute_many_requires_connection(self, connector):
        with pytest.raises(DatasphereError, match="not connected"):
            await connector.execute_many("INSERT INTO t VALUES (?)", [(1,)])

    @pytest.mark.asyncio
    async def test_get_tables_requires_connection(self, connector):
        with pytest.raises(DatasphereError, match="not connected"):
            await connector.get_tables()

    @pytest.mark.asyncio
    async def test_get_columns_requires_connection(self, connector):
        with pytest.raises(DatasphereError, match="not connected"):
            await connector.get_columns("some_table")
```

**After:**
```python
class TestNotConnectedErrors:
    """Auto-connect: methods attempt to connect lazily, so they raise
    DatasphereConnectionError (not "not connected") when credentials are invalid."""

    @pytest.mark.asyncio
    async def test_execute_sql_auto_connects(self, connector):
        with pytest.raises(DatasphereConnectionError, match="Connection failed"):
            await connector.execute_sql("SELECT 1")

    @pytest.mark.asyncio
    async def test_execute_many_auto_connects(self, connector):
        with pytest.raises(DatasphereConnectionError, match="Connection failed"):
            await connector.execute_many("INSERT INTO t VALUES (?)", [(1,)])

    @pytest.mark.asyncio
    async def test_get_tables_auto_connects(self, connector):
        with pytest.raises(DatasphereConnectionError, match="Connection failed"):
            await connector.get_tables()

    @pytest.mark.asyncio
    async def test_get_columns_auto_connects(self, connector):
        with pytest.raises(DatasphereConnectionError, match="Connection failed"):
            await connector.get_columns("some_table")
```

Note: `DatasphereConnectionError` is already imported in the test file, no import changes needed.

---

## Verification

Run `uv run pytest -x -q` — all 197 tests should pass.
