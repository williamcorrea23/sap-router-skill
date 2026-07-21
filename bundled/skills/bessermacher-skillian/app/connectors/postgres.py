"""Generic async PostgreSQL connector."""

from typing import Any

import asyncpg


class PostgresConnector:
    """Async PostgreSQL connection pool for data queries."""

    def __init__(self, database_url: str):
        """Initialize connector with database URL.

        Args:
            database_url: PostgreSQL connection string.
        """
        self._url = database_url
        self._pool: asyncpg.Pool | None = None

    async def get_pool(self) -> asyncpg.Pool:
        """Get or create connection pool."""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                self._url,
                min_size=2,
                max_size=10,
                max_inactive_connection_lifetime=300,
                command_timeout=60,
            )
        return self._pool

    async def execute(self, query: str, params: list[Any] | None = None) -> list[dict]:
        """Execute query and return results as list of dicts.

        Args:
            query: SQL query with $1, $2, etc. placeholders.
            params: Query parameters.

        Returns:
            List of row dictionaries.
        """
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            if params:
                rows = await conn.fetch(query, *params)
            else:
                rows = await conn.fetch(query)
            return [dict(row) for row in rows]

    async def execute_one(self, query: str, params: list[Any] | None = None) -> dict | None:
        """Execute query and return single result.

        Args:
            query: SQL query.
            params: Query parameters.

        Returns:
            Single row dict or None.
        """
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            if params:
                row = await conn.fetchrow(query, *params)
            else:
                row = await conn.fetchrow(query)
            return dict(row) if row else None

    async def health_check(self) -> bool:
        """Check database connectivity."""
        try:
            pool = await self.get_pool()
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception:
            return False

    async def close(self) -> None:
        """Close connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None
