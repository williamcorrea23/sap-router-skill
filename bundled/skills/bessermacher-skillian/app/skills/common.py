"""Shared utilities for skill tool implementations."""

from typing import Any

from app.connectors.datasphere import DatasphereConnector

# Module-level connector cache shared across skills
_connector: DatasphereConnector | None = None


def get_connector(connector: Any = None) -> DatasphereConnector:
    """Get or cache the Datasphere connector.

    Args:
        connector: Optional connector instance to cache.

    Returns:
        The cached DatasphereConnector instance.

    Raises:
        ValueError: If no connector has been configured.
    """
    global _connector
    if connector is not None:
        _connector = connector
    if _connector is None:
        raise ValueError("Datasphere connector not configured")
    return _connector
