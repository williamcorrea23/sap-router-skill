"""Pydantic models and loader for investigation_sources.yaml."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class MeasureConfig(BaseModel):
    """A key figure measure with column name and aggregation function."""

    column: str
    aggregation: str = "sum"


class DimensionConfig(BaseModel):
    """A check dimension with its column name and aliases."""

    column: str
    aliases: list[str] = []


class VersionConfig(BaseModel):
    """A report version with code, name, and backing table."""

    code: str
    name: str
    table: str


class ReportConfig(BaseModel):
    """A report definition with versions and dimensions."""

    description: str
    versions: list[VersionConfig]
    check_dimensions: list[DimensionConfig]
    default_group_by: list[str]
    measures: list[MeasureConfig] = []
    default_filters: dict[str, str] = {}


class TableConfig(BaseModel):
    """A standalone table definition."""

    description: str
    table: str
    check_dimensions: list[DimensionConfig]
    default_group_by: list[str]
    measures: list[MeasureConfig] = []
    default_filters: dict[str, str] = {}


class InvestigationSourceConfig(BaseModel):
    """Top-level investigation source configuration."""

    schema_name: str = Field(alias="schema")
    reports: dict[str, ReportConfig] = {}
    tables: dict[str, TableConfig] = {}
    scope_values: dict[str, str] = {}

    model_config = {"populate_by_name": True}

    def get_table_info(self, table_name: str) -> dict[str, Any] | None:
        """Get config for a table by its Datasphere table name.

        Searches through both reports (all version tables) and standalone tables.

        Returns:
            Dict with 'default_group_by', 'check_dimensions', 'source_name',
            and 'source_type', or None if not found.
        """
        for name, report in self.reports.items():
            for version in report.versions:
                if version.table == table_name:
                    return {
                        "source_name": name,
                        "source_type": "report",
                        "default_group_by": report.default_group_by,
                        "check_dimensions": report.check_dimensions,
                        "measures": report.measures,
                        "default_filters": report.default_filters,
                    }

        for name, table_cfg in self.tables.items():
            if table_cfg.table == table_name:
                return {
                    "source_name": name,
                    "source_type": "table",
                    "default_group_by": table_cfg.default_group_by,
                    "check_dimensions": table_cfg.check_dimensions,
                    "measures": table_cfg.measures,
                    "default_filters": table_cfg.default_filters,
                }

        return None

    def get_all_table_names(self) -> list[str]:
        """Get all unique Datasphere table names from config."""
        tables: set[str] = set()
        for report in self.reports.values():
            for version in report.versions:
                tables.add(version.table)
        for table_cfg in self.tables.values():
            tables.add(table_cfg.table)
        return sorted(tables)


def load_investigation_config(path: Path) -> InvestigationSourceConfig:
    """Load and parse investigation_sources.yaml.

    Args:
        path: Path to the YAML configuration file.

    Returns:
        Parsed InvestigationSourceConfig.

    Raises:
        FileNotFoundError: If config file does not exist.
        ValueError: If config file is invalid.
    """
    if not path.exists():
        raise FileNotFoundError(f"Investigation config not found: {path}")

    content = yaml.safe_load(path.read_text())
    if not isinstance(content, dict):
        raise ValueError(f"Invalid investigation config: expected dict, got {type(content)}")

    return InvestigationSourceConfig(**content)
