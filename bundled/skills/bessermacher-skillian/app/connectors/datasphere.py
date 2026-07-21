"""SAP Datasphere connector using hdbcli for direct database access."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any

from hdbcli import dbapi


class DatasphereError(Exception):
    """Base exception for Datasphere operations."""


class DatasphereConnectionError(DatasphereError):
    """Connection failed."""


class DatasphereQueryError(DatasphereError):
    """Query execution failed."""


@dataclass
class DatasphereConnector:
    """Connector for SAP Datasphere using hdbcli.

    Uses the SAP HANA Python client (hdbcli) to connect directly to the
    Datasphere HANA database. Requires a database user created in
    Datasphere Space Management.

    Note: Your IP address may need to be added to Datasphere's IP allow-list.

    Example:
        connector = DatasphereConnector(
            host="your-tenant.hana.prod-eu10.hanacloud.ondemand.com",
            user="DBUSER#YOUR_SPACE",
            password="your-password",
        )
        await connector.connect()
        results = await connector.execute_sql("SELECT * FROM view_name LIMIT 10")
        await connector.close()
    """

    host: str
    user: str
    password: str
    port: int = 443
    encrypt: bool = True
    ssl_validate_certificate: bool = True
    timeout: int = 60
    pool_size: int = 4

    _connection: dbapi.Connection | None = field(default=None, init=False, repr=False)
    _executor: ThreadPoolExecutor | None = field(default=None, init=False, repr=False)

    async def connect(self) -> None:
        """Initialize the database connection."""
        if self._connection is not None:
            return

        self._executor = ThreadPoolExecutor(max_workers=self.pool_size)

        loop = asyncio.get_event_loop()
        try:
            self._connection = await loop.run_in_executor(
                self._executor,
                self._create_connection,
            )
        except dbapi.Error as e:
            raise DatasphereConnectionError(f"Connection failed: {e}") from e

    def _create_connection(self) -> dbapi.Connection:
        """Create a synchronous hdbcli connection."""
        return dbapi.connect(
            address=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            encrypt=self.encrypt,
            sslValidateCertificate=self.ssl_validate_certificate,
            connectTimeout=self.timeout * 1000,  # milliseconds
        )

    async def close(self) -> None:
        """Close the database connection."""
        if self._connection:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor,
                self._connection.close,
            )
            self._connection = None

        if self._executor:
            self._executor.shutdown(wait=True)
            self._executor = None

    async def execute_sql(
        self,
        query: str,
        parameters: tuple[Any, ...] | list[Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a SQL query against Datasphere.

        Args:
            query: SQL query string
            parameters: Optional query parameters for prepared statements

        Returns:
            List of result rows as dictionaries

        Raises:
            DatasphereQueryError: If query execution fails
        """
        if self._connection is None:
            await self.connect()

        loop = asyncio.get_event_loop()
        try:
            return await loop.run_in_executor(
                self._executor,
                self._execute_sql_sync,
                query,
                parameters,
            )
        except dbapi.Error as e:
            raise DatasphereQueryError(f"Query failed: {e}") from e

    def _execute_sql_sync(
        self,
        query: str,
        parameters: tuple[Any, ...] | list[Any] | None,
    ) -> list[dict[str, Any]]:
        """Execute SQL synchronously (runs in executor)."""
        cursor = self._connection.cursor()
        try:
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)

            if cursor.description is None:
                return []

            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row, strict=False)) for row in rows]
        finally:
            cursor.close()

    async def execute_many(
        self,
        query: str,
        parameters_list: list[tuple[Any, ...] | list[Any]],
    ) -> int:
        """Execute a SQL statement with multiple parameter sets.

        Args:
            query: SQL statement (INSERT, UPDATE, etc.)
            parameters_list: List of parameter tuples

        Returns:
            Number of affected rows
        """
        if self._connection is None:
            await self.connect()

        loop = asyncio.get_event_loop()
        try:
            return await loop.run_in_executor(
                self._executor,
                self._execute_many_sync,
                query,
                parameters_list,
            )
        except dbapi.Error as e:
            raise DatasphereQueryError(f"Batch execution failed: {e}") from e

    def _execute_many_sync(
        self,
        query: str,
        parameters_list: list[tuple[Any, ...] | list[Any]],
    ) -> int:
        """Execute batch SQL synchronously (runs in executor)."""
        cursor = self._connection.cursor()
        try:
            cursor.executemany(query, parameters_list)
            self._connection.commit()
            return cursor.rowcount
        finally:
            cursor.close()

    async def get_tables(self, schema: str | None = None) -> list[dict[str, Any]]:
        """List available tables in the schema.

        Args:
            schema: Schema name (defaults to user's default schema)

        Returns:
            List of table metadata dictionaries
        """
        if schema:
            query = """
                SELECT TABLE_NAME, TABLE_TYPE, RECORD_COUNT
                FROM TABLES
                WHERE SCHEMA_NAME = ?
            """
            return await self.execute_sql(query, [schema])
        query = """
            SELECT TABLE_NAME, TABLE_TYPE, RECORD_COUNT
            FROM TABLES
            WHERE SCHEMA_NAME = CURRENT_SCHEMA
        """
        return await self.execute_sql(query)

    async def get_columns(self, table_name: str, schema: str | None = None) -> list[dict[str, Any]]:
        """Get column metadata for a table.

        Args:
            table_name: Name of the table
            schema: Schema name (defaults to user's default schema)

        Returns:
            List of column metadata dictionaries
        """
        if schema:
            query = """
                SELECT COLUMN_NAME, DATA_TYPE_NAME, LENGTH, IS_NULLABLE, DEFAULT_VALUE
                FROM TABLE_COLUMNS
                WHERE SCHEMA_NAME = ? AND TABLE_NAME = ?
                ORDER BY POSITION
            """
            return await self.execute_sql(query, [schema, table_name])
        query = """
            SELECT COLUMN_NAME, DATA_TYPE_NAME, LENGTH, IS_NULLABLE, DEFAULT_VALUE
            FROM TABLE_COLUMNS
            WHERE SCHEMA_NAME = CURRENT_SCHEMA AND TABLE_NAME = ?
            ORDER BY POSITION
        """
        return await self.execute_sql(query, [table_name])

    async def health_check(self) -> bool:
        """Check if Datasphere connection is healthy."""
        try:
            if self._connection is None:
                return False
            result = await self.execute_sql("SELECT 1 FROM DUMMY")
            return len(result) == 1
        except Exception:
            return False

    async def __aenter__(self) -> "DatasphereConnector":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, _exc_type, _exc_val, _exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
