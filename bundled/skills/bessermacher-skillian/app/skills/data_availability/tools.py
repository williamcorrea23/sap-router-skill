"""Tool implementations for data_availability skill."""

import logging
import re
from pathlib import Path
from typing import Any

from app.connectors.datasphere import DatasphereQueryError
from app.skills.common import get_connector

logger = logging.getLogger(__name__)

# Module-level config cache
_source_config: Any | None = None

# Pattern for valid SQL identifiers (column/table names)
_VALID_IDENTIFIER = re.compile(r'^[a-zA-Z0-9_/."]+$')


def _get_source_config():
    """Get or load the investigation source configuration."""
    global _source_config
    if _source_config is None:
        from app.skills.data_availability.source_config import load_investigation_config

        _source_config = load_investigation_config(Path("config/investigation_sources.yaml"))
    return _source_config


def _validate_identifier(name: str) -> bool:
    """Validate a SQL identifier to prevent injection."""
    return bool(_VALID_IDENTIFIER.match(name))


def list_investigation_sources(connector: Any = None) -> dict[str, Any]:
    """List all configured investigation sources."""
    if connector is not None:
        get_connector(connector)

    config = _get_source_config()

    reports = []
    for name, report in config.reports.items():
        reports.append(
            {
                "name": name,
                "description": report.description,
                "versions": [
                    {"code": v.code, "name": v.name, "table": v.table} for v in report.versions
                ],
                "check_dimensions": [
                    {"column": d.column, "aliases": d.aliases} for d in report.check_dimensions
                ],
                "default_group_by": report.default_group_by,
                "measures": [
                    {"column": m.column, "aggregation": m.aggregation} for m in report.measures
                ],
            }
        )

    tables = []
    for name, table_cfg in config.tables.items():
        tables.append(
            {
                "name": name,
                "description": table_cfg.description,
                "table": table_cfg.table,
                "check_dimensions": [
                    {"column": d.column, "aliases": d.aliases} for d in table_cfg.check_dimensions
                ],
                "default_group_by": table_cfg.default_group_by,
                "measures": [
                    {"column": m.column, "aggregation": m.aggregation} for m in table_cfg.measures
                ],
            }
        )

    return {
        "reports": reports,
        "tables": tables,
        "scope_values": config.scope_values,
        "all_table_names": config.get_all_table_names(),
    }


async def check_data_availability(
    table: str,
    filters: dict[str, str] | None = None,
    group_by: list[str] | None = None,
    connector: Any = None,
) -> dict[str, Any]:
    """Check if data exists in a Datasphere table for given filter criteria."""
    conn = get_connector(connector)
    config = _get_source_config()

    # Validate filters format — must be a flat dict of {column: value} pairs.
    # Reject array/nested formats that some LLMs produce.
    if filters is not None and not isinstance(filters, dict):
        return {
            "error": (
                "Invalid filters format. Filters must be a flat object with "
                'column:value pairs, e.g. {"ZCOMPCODE": "1110", "FISCPER": "2026001"}. '
                "Do NOT use arrays or nested objects."
            ),
            "data_found": False,
        }

    # Validate table name
    if not _validate_identifier(table):
        return {"error": f"Invalid table name: {table}", "data_found": False}

    # Look up defaults from config
    table_info = config.get_table_info(table)
    if group_by is None:
        if table_info:
            group_by = table_info["default_group_by"]
        else:
            group_by = []

    measures = table_info["measures"] if table_info else []

    # Merge default filters from config with user-provided filters
    # (user-provided values override defaults)
    if table_info and table_info.get("default_filters"):
        merged_filters = dict(table_info["default_filters"])
        if filters:
            merged_filters.update(filters)
        filters = merged_filters

    # Validate group_by columns
    for col in group_by:
        if not _validate_identifier(col):
            return {"error": f"Invalid column name: {col}", "data_found": False}

    # Build SQL query
    schema = config.schema_name
    group_cols = ", ".join(f'"{col}"' for col in group_by)

    # Build aggregation: use configured measures if available, else COUNT(*)
    if measures:
        agg_parts = [f'{m.aggregation.upper()}("{m.column}") as "{m.column}"' for m in measures]
        agg_clause = ", ".join(agg_parts)
    else:
        agg_clause = 'COUNT(*) as "ROW_COUNT"'

    if group_cols:
        select_clause = f"{group_cols}, {agg_clause}"
        group_clause = f"GROUP BY {group_cols}"
    else:
        select_clause = agg_clause
        group_clause = ""

    # Build WHERE clause from filters
    where_parts: list[str] = []
    if filters:
        for col, value in filters.items():
            if not _validate_identifier(col):
                return {"error": f"Invalid filter column: {col}", "data_found": False}
            # Escape single quotes in values
            safe_value = str(value).replace("'", "''")
            where_parts.append(f"\"{col}\" = '{safe_value}'")

    where_clause = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""

    query = f"""
SELECT {select_clause}
FROM "{schema}"."{table}"
{where_clause}
{group_clause}
""".strip()

    logger.info(
        "check_data_availability: table=%s filters=%s group_by=%s",
        table,
        filters,
        group_by,
    )
    logger.debug("check_data_availability: query=\n%s", query)

    try:
        results = await conn.execute_sql(query)

        # Build totals from measures or fallback to ROW_COUNT
        if measures:
            measure_cols = [m.column for m in measures]
            totals = {col: sum(r.get(col, 0) or 0 for r in results) for col in measure_cols}
            data_found = any(v != 0 for v in totals.values())
        else:
            totals = {"ROW_COUNT": sum(r.get("ROW_COUNT", 0) for r in results)}
            data_found = len(results) > 0

        logger.info(
            "check_data_availability: data_found=%s totals=%s group_count=%d",
            data_found,
            totals,
            len(results),
        )
        for row in results[:3]:
            logger.debug("check_data_availability: sample_row=%s", row)

        return {
            "table": table,
            "data_found": data_found,
            "totals": totals,
            "group_count": len(results),
            "sample_rows": results[:3],
            "groups": results,
            "filters_applied": filters or {},
            "group_by": group_by,
            "query": query,
        }
    except DatasphereQueryError as e:
        logger.error("check_data_availability: query failed — %s", e)
        return {
            "error": str(e),
            "table": table,
            "data_found": False,
            "groups": [],
            "filters_applied": filters or {},
        }
