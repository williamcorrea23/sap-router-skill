"""Integration tests for Datasphere (requires real connection)."""

import pytest

from app.config import get_settings
from app.connectors.datasphere import DatasphereConnector


@pytest.fixture
def real_connector():
    """Create real connector from settings. Skip if not configured."""
    settings = get_settings()
    if not settings.datasphere_host:
        pytest.skip("Datasphere not configured")

    return DatasphereConnector(
        host=settings.datasphere_host,
        space=settings.datasphere_space,
        client_id=settings.datasphere_client_id,
        client_secret=settings.datasphere_client_secret,
        token_url=settings.datasphere_token_url,
        port=settings.datasphere_port,
        timeout=settings.datasphere_timeout,
        max_connections=settings.datasphere_max_connections,
    )


@pytest.mark.integration
class TestDatasphereIntegration:
    @pytest.mark.asyncio
    async def test_connect_and_list(self, real_connector):
        await real_connector.connect()
        try:
            entities = await real_connector.list_entities()
            assert isinstance(entities, list)
        finally:
            await real_connector.close()

    @pytest.mark.asyncio
    async def test_health_check(self, real_connector):
        await real_connector.connect()
        try:
            healthy = await real_connector.health_check()
            assert healthy is True
        finally:
            await real_connector.close()

    @pytest.mark.asyncio
    async def test_execute_simple_query(self, real_connector):
        """Test a simple SQL query against Datasphere."""
        await real_connector.connect()
        try:
            # This query depends on the actual schema in Datasphere
            # In real tests, you'd use a known table/view
            results = await real_connector.execute_sql("SELECT 1 as test_column")
            assert isinstance(results, list)
        finally:
            await real_connector.close()
