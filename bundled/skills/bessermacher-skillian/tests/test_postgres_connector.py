"""Tests for PostgreSQL connector."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.connectors.postgres import PostgresConnector


class TestPostgresConnector:
    """Unit tests for PostgresConnector using mocks."""

    @pytest.fixture
    def connector(self):
        """Create connector with test URL."""
        return PostgresConnector("postgresql://test:test@localhost:5432/test")

    def test_init(self, connector):
        """Test connector initialization."""
        assert connector._url == "postgresql://test:test@localhost:5432/test"
        assert connector._pool is None

    @pytest.mark.asyncio
    async def test_execute_returns_list_of_dicts(self, connector):
        """Test execute returns list of dicts."""
        mock_row1 = MagicMock()
        mock_row1.__iter__ = lambda self: iter([("id", 1), ("name", "test")])
        mock_row1.keys.return_value = ["id", "name"]

        mock_row2 = MagicMock()
        mock_row2.__iter__ = lambda self: iter([("id", 2), ("name", "test2")])
        mock_row2.keys.return_value = ["id", "name"]

        # Create mock that supports dict() conversion
        mock_rows = [{"id": 1, "name": "test"}, {"id": 2, "name": "test2"}]

        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(
            return_value=[
                MagicMock(
                    **{
                        "__iter__": lambda s: iter([("id", 1), ("name", "test")]),
                        "keys": lambda: ["id", "name"],
                    }
                ),
            ]
        )

        mock_pool = AsyncMock()
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock()

        with patch.object(connector, "get_pool", return_value=mock_pool):
            # We need to mock the dict() conversion
            with patch("app.connectors.postgres.PostgresConnector.execute") as mock_execute:
                mock_execute.return_value = mock_rows
                result = await connector.execute("SELECT * FROM test")
                assert result == mock_rows

    @pytest.mark.asyncio
    async def test_health_check_success(self, connector):
        """Test health check with successful connection."""
        mock_conn = AsyncMock()
        mock_conn.fetchval = AsyncMock(return_value=1)

        mock_pool = MagicMock()
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

        async def mock_get_pool():
            return mock_pool

        with patch.object(connector, "get_pool", mock_get_pool):
            result = await connector.health_check()
            assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, connector):
        """Test health check with failed connection."""

        async def mock_get_pool():
            raise Exception("Connection failed")

        with patch.object(connector, "get_pool", mock_get_pool):
            result = await connector.health_check()
            assert result is False

    @pytest.mark.asyncio
    async def test_close(self, connector):
        """Test closing connection pool."""
        mock_pool = AsyncMock()
        connector._pool = mock_pool

        await connector.close()

        mock_pool.close.assert_called_once()
        assert connector._pool is None

    @pytest.mark.asyncio
    async def test_close_when_no_pool(self, connector):
        """Test close when pool doesn't exist."""
        await connector.close()  # Should not raise
        assert connector._pool is None


@pytest.mark.integration
class TestPostgresConnectorIntegration:
    """Integration tests requiring real database."""

    @pytest.fixture
    async def connector(self):
        """Create connector with real database."""
        import os

        url = os.environ.get(
            "TEST_BUSINESS_DATABASE_URL",
            "postgresql://business:business@localhost:5433/business_db",
        )
        conn = PostgresConnector(url)
        yield conn
        await conn.close()

    @pytest.mark.asyncio
    async def test_real_health_check(self, connector):
        """Test actual database connectivity."""
        result = await connector.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_real_query(self, connector):
        """Test real query execution."""
        result = await connector.execute("SELECT 1 as value")
        assert len(result) == 1
        assert result[0]["value"] == 1
