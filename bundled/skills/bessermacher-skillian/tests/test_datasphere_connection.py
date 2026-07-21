"""Dedicated tests for Datasphere connection lifecycle.

Tests connect, close, health check, reconnection, error handling,
and context manager behaviour using mocked hdbcli.
"""

from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock, patch

import pytest

from app.connectors.datasphere import (
    DatasphereConnectionError,
    DatasphereConnector,
    DatasphereError,
)


@pytest.fixture
def connector():
    """Create a test connector with dummy credentials."""
    return DatasphereConnector(
        host="test.hana.prod-eu10.hanacloud.ondemand.com",
        user="DBUSER#TEST_SPACE",
        password="test-password",
        port=443,
    )


@pytest.fixture
def mock_dbapi():
    """Patch hdbcli.dbapi and return the mock."""
    with patch("app.connectors.datasphere.dbapi") as mock:
        mock_conn = MagicMock()
        mock.connect.return_value = mock_conn
        # Provide a usable Error class for exception matching
        mock.Error = Exception
        yield mock


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------


class TestConnectorInit:
    def test_default_parameters(self):
        c = DatasphereConnector(
            host="host",
            user="user",
            password="pw",
        )
        assert c.port == 443
        assert c.encrypt is True
        assert c.ssl_validate_certificate is True
        assert c.timeout == 60
        assert c.pool_size == 4

    def test_custom_parameters(self):
        c = DatasphereConnector(
            host="host",
            user="user",
            password="pw",
            port=30015,
            encrypt=False,
            ssl_validate_certificate=False,
            timeout=120,
            pool_size=8,
        )
        assert c.port == 30015
        assert c.encrypt is False
        assert c.ssl_validate_certificate is False
        assert c.timeout == 120
        assert c.pool_size == 8

    def test_not_connected_initially(self, connector):
        assert connector._connection is None
        assert connector._executor is None


# ---------------------------------------------------------------------------
# connect()
# ---------------------------------------------------------------------------


class TestConnect:
    @pytest.mark.asyncio
    async def test_connect_creates_connection(self, connector, mock_dbapi):
        await connector.connect()

        mock_dbapi.connect.assert_called_once_with(
            address=connector.host,
            port=connector.port,
            user=connector.user,
            password=connector.password,
            encrypt=connector.encrypt,
            sslValidateCertificate=connector.ssl_validate_certificate,
            connectTimeout=connector.timeout * 1000,
        )
        assert connector._connection is not None
        assert connector._executor is not None

    @pytest.mark.asyncio
    async def test_connect_is_idempotent(self, connector, mock_dbapi):
        """Calling connect() twice should not create a second connection."""
        await connector.connect()
        await connector.connect()

        mock_dbapi.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_failure_raises_connection_error(self, connector):
        with patch("app.connectors.datasphere.dbapi") as mock:
            mock.Error = Exception
            mock.connect.side_effect = mock.Error("auth failed")

            with pytest.raises(DatasphereConnectionError, match="Connection failed"):
                await connector.connect()

    @pytest.mark.asyncio
    async def test_connect_sets_up_thread_pool(self, connector, mock_dbapi):
        await connector.connect()
        assert isinstance(connector._executor, ThreadPoolExecutor)


# ---------------------------------------------------------------------------
# close()
# ---------------------------------------------------------------------------


class TestClose:
    @pytest.mark.asyncio
    async def test_close_cleans_up(self, connector, mock_dbapi):
        await connector.connect()
        mock_conn = connector._connection

        await connector.close()

        mock_conn.close.assert_called_once()
        assert connector._connection is None
        assert connector._executor is None

    @pytest.mark.asyncio
    async def test_close_when_not_connected(self, connector):
        """close() on an unconnected connector should be a no-op."""
        await connector.close()  # Should not raise
        assert connector._connection is None

    @pytest.mark.asyncio
    async def test_close_then_reconnect(self, connector, mock_dbapi):
        """After closing, a fresh connect() should work."""
        await connector.connect()
        await connector.close()

        # Reset mock so we can verify a second connect call
        mock_dbapi.connect.reset_mock()

        await connector.connect()
        mock_dbapi.connect.assert_called_once()
        assert connector._connection is not None


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------


class TestContextManager:
    @pytest.mark.asyncio
    async def test_context_manager_connects_and_closes(self, mock_dbapi):
        connector = DatasphereConnector(
            host="host",
            user="user",
            password="pw",
        )

        async with connector as ctx:
            assert ctx is connector
            assert ctx._connection is not None

        # After exiting context, connection should be cleaned up
        assert connector._connection is None
        assert connector._executor is None

    @pytest.mark.asyncio
    async def test_context_manager_closes_on_exception(self, mock_dbapi):
        connector = DatasphereConnector(
            host="host",
            user="user",
            password="pw",
        )

        with pytest.raises(RuntimeError):
            async with connector:
                raise RuntimeError("boom")

        assert connector._connection is None


# ---------------------------------------------------------------------------
# health_check()
# ---------------------------------------------------------------------------


class TestHealthCheck:
    @pytest.mark.asyncio
    async def test_health_check_success(self, connector, mock_dbapi):
        await connector.connect()

        # Simulate "SELECT 1 FROM DUMMY" returning one row
        mock_cursor = MagicMock()
        mock_cursor.description = [("1",)]
        mock_cursor.fetchall.return_value = [(1,)]
        connector._connection.cursor.return_value = mock_cursor

        result = await connector.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_not_connected(self, connector):
        result = await connector.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_health_check_query_failure(self, connector, mock_dbapi):
        await connector.connect()

        # Simulate cursor.execute raising an error
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("connection lost")
        connector._connection.cursor.return_value = mock_cursor

        result = await connector.health_check()
        assert result is False


# ---------------------------------------------------------------------------
# Operations without connection
# ---------------------------------------------------------------------------


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
