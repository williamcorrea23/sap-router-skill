"""Data connector module.

Connectors provide database access for data sources.
"""

from app.connectors.postgres import PostgresConnector

__all__ = ["PostgresConnector"]
