"""Tests for data_availability skill."""

import logging
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.skill_loader import SkillLoader
from app.skills import common as skills_common
from app.skills.data_availability import tools as availability_tools
from app.skills.data_availability.source_config import (
    InvestigationSourceConfig,
    load_investigation_config,
)

logger = logging.getLogger(__name__)

# --- Fixtures ---


@pytest.fixture
def mock_connector():
    """Mock Datasphere connector."""
    connector = MagicMock()
    connector.space = "TEST_SPACE"
    connector.execute_sql = AsyncMock(return_value=[])
    return connector


@pytest.fixture
def skill_loader(mock_connector):
    """Create skill loader with mock connector."""
    return SkillLoader(
        skills_dir=Path("app/skills"),
        connector_factory={"datasphere": mock_connector},
    )


@pytest.fixture
def skill(skill_loader):
    """Load the data_availability skill."""
    return skill_loader.load_skill("data_availability")


@pytest.fixture(autouse=True)
def reset_module_state(mock_connector):
    """Reset module-level state between tests."""
    skills_common._connector = mock_connector
    availability_tools._source_config = None
    yield
    skills_common._connector = None
    availability_tools._source_config = None


# --- Skill Loading Tests ---


class TestDataAvailabilitySkill:
    def test_skill_name(self, skill):
        assert skill.name == "data-availability"

    def test_skill_description(self, skill):
        assert "availability" in skill.description.lower()

    def test_skill_has_tools(self, skill):
        assert len(skill.tools) == 1

    def test_tool_names(self, skill):
        tool_names = [t.name for t in skill.tools]
        assert "check_data_availability" in tool_names

    def test_system_prompt_not_empty(self, skill):
        assert len(skill.system_prompt) > 100

    def test_connector_type(self, skill):
        assert skill.connector_type == "datasphere"


# --- Source Config Tests ---


class TestSourceConfig:
    def test_load_config(self):
        config = load_investigation_config(Path("config/investigation_sources.yaml"))
        assert isinstance(config, InvestigationSourceConfig)
        assert config.schema_name == "BW2AI"

    def test_reports_loaded(self):
        config = load_investigation_config(Path("config/investigation_sources.yaml"))
        assert "consolidation_management" in config.reports
        report = config.reports["consolidation_management"]
        assert len(report.versions) == 5

    def test_tables_loaded(self):
        config = load_investigation_config(Path("config/investigation_sources.yaml"))
        assert "bpc_mart" in config.tables
        assert config.tables["bpc_mart"].table == "CV_ZFI_AA01"

    def test_scope_values_loaded(self):
        config = load_investigation_config(Path("config/investigation_sources.yaml"))
        assert "S_NONE" in config.scope_values
        assert "S_LEGAL" in config.scope_values

    def test_get_table_info_from_report(self):
        config = load_investigation_config(Path("config/investigation_sources.yaml"))
        info = config.get_table_info("CV_ZBC_AA61")
        assert info is not None
        assert info["source_name"] == "consolidation_management"
        assert info["source_type"] == "report"
        assert len(info["default_group_by"]) > 0

    def test_get_table_info_from_tables(self):
        config = load_investigation_config(Path("config/investigation_sources.yaml"))
        info = config.get_table_info("CV_ZFI_AA01")
        assert info is not None
        assert info["source_name"] == "bpc_mart"
        assert info["source_type"] == "table"

    def test_get_table_info_not_found(self):
        config = load_investigation_config(Path("config/investigation_sources.yaml"))
        info = config.get_table_info("NONEXISTENT_TABLE")
        assert info is None

    def test_get_all_table_names(self):
        config = load_investigation_config(Path("config/investigation_sources.yaml"))
        tables = config.get_all_table_names()
        assert "CV_ZBC_AA61" in tables
        assert "CV_ZBC_AA62" in tables
        assert "CV_ZFI_AA01" in tables
        assert "CV_ZBC_AA08Z" in tables

    def test_missing_config_file(self):
        with pytest.raises(FileNotFoundError):
            load_investigation_config(Path("nonexistent.yaml"))

    def test_dimension_aliases(self):
        config = load_investigation_config(Path("config/investigation_sources.yaml"))
        report = config.reports["consolidation_management"]
        company_dim = next(d for d in report.check_dimensions if d.column == "ZCOMPCODE")
        assert "cocd" in company_dim.aliases
        assert "company_code" in company_dim.aliases

    def test_report_measures_loaded(self):
        config = load_investigation_config(Path("config/investigation_sources.yaml"))
        report = config.reports["consolidation_management"]
        assert len(report.measures) == 2
        measure_cols = [m.column for m in report.measures]
        assert "CS_TRN_LC" in measure_cols
        assert "CS_TRN_GC" in measure_cols

    def test_table_measures_loaded(self):
        config = load_investigation_config(Path("config/investigation_sources.yaml"))
        table = config.tables["bpc_mart"]
        assert len(table.measures) == 1
        assert table.measures[0].column == "CS_TRN_LC"

    def test_get_table_info_includes_measures(self):
        config = load_investigation_config(Path("config/investigation_sources.yaml"))
        info = config.get_table_info("CV_ZBC_AA61")
        assert "measures" in info
        measure_cols = [m.column for m in info["measures"]]
        assert "CS_TRN_LC" in measure_cols
        assert "CS_TRN_GC" in measure_cols

    def test_table_without_measures(self):
        config = load_investigation_config(Path("config/investigation_sources.yaml"))
        table = config.tables["ownership"]
        assert table.measures == []


# --- Tool Function Tests ---


class TestListInvestigationSources:
    def test_returns_reports(self, mock_connector):
        result = availability_tools.list_investigation_sources(connector=mock_connector)
        assert "reports" in result
        assert len(result["reports"]) > 0
        report = result["reports"][0]
        assert "name" in report
        assert "versions" in report
        assert "check_dimensions" in report
        assert "measures" in report

    def test_returns_tables(self, mock_connector):
        result = availability_tools.list_investigation_sources(connector=mock_connector)
        assert "tables" in result
        assert len(result["tables"]) > 0

    def test_returns_scope_values(self, mock_connector):
        result = availability_tools.list_investigation_sources(connector=mock_connector)
        assert "scope_values" in result
        assert "S_NONE" in result["scope_values"]

    def test_returns_all_table_names(self, mock_connector):
        result = availability_tools.list_investigation_sources(connector=mock_connector)
        assert "all_table_names" in result
        assert "CV_ZBC_AA61" in result["all_table_names"]


class TestCheckDataAvailability:
    @pytest.mark.asyncio
    async def test_data_found(self, mock_connector, caplog):
        mock_connector.execute_sql = AsyncMock(
            return_value=[
                {
                    "ZCOMPCODE": "1110",
                    "ZVERSION": "001",
                    "FISCPER": "2024012",
                    "ZSCOPE": "S_LEGAL",
                    "CS_TRN_LC": 42000,
                    "CS_TRN_GC": 5000,
                },
            ]
        )

        with caplog.at_level(logging.DEBUG):
            result = await availability_tools.check_data_availability(
                table="CV_ZBC_AA61",
                filters={"ZCOMPCODE": "1110", "FISCPER": "2024012"},
                connector=mock_connector,
            )

        logger.info("test_data_found result: %s", result)

        assert result["data_found"] is True
        assert result["totals"] == {"CS_TRN_LC": 42000, "CS_TRN_GC": 5000}
        assert result["group_count"] == 1
        assert len(result["groups"]) == 1
        assert result["groups"][0]["ZCOMPCODE"] == "1110"
        assert result["groups"][0]["CS_TRN_LC"] == 42000
        assert result["sample_rows"] == result["groups"]
        assert "data_found=True" in caplog.text

    @pytest.mark.asyncio
    async def test_no_data_found(self, mock_connector):
        mock_connector.execute_sql = AsyncMock(return_value=[])

        result = await availability_tools.check_data_availability(
            table="CV_ZBC_AA61",
            filters={"ZCOMPCODE": "9999"},
            connector=mock_connector,
        )

        assert result["data_found"] is False
        assert result["totals"] == {"CS_TRN_LC": 0, "CS_TRN_GC": 0}
        assert result["groups"] == []

    @pytest.mark.asyncio
    async def test_with_filters(self, mock_connector):
        mock_connector.execute_sql = AsyncMock(return_value=[])

        await availability_tools.check_data_availability(
            table="CV_ZBC_AA61",
            filters={"ZCOMPCODE": "1110", "FISCPER": "2024012"},
            connector=mock_connector,
        )

        call_args = mock_connector.execute_sql.call_args[0][0]
        assert "\"ZCOMPCODE\" = '1110'" in call_args
        assert "\"FISCPER\" = '2024012'" in call_args

    @pytest.mark.asyncio
    async def test_default_group_by(self, mock_connector):
        mock_connector.execute_sql = AsyncMock(return_value=[])

        result = await availability_tools.check_data_availability(
            table="CV_ZBC_AA61",
            connector=mock_connector,
        )

        # Should use default group_by from config
        assert "ZCOMPCODE" in result["group_by"]
        assert "ZVERSION" in result["group_by"]

    @pytest.mark.asyncio
    async def test_custom_group_by(self, mock_connector):
        mock_connector.execute_sql = AsyncMock(return_value=[])

        result = await availability_tools.check_data_availability(
            table="CV_ZBC_AA61",
            group_by=["ZCOMPCODE"],
            connector=mock_connector,
        )

        assert result["group_by"] == ["ZCOMPCODE"]
        call_args = mock_connector.execute_sql.call_args[0][0]
        assert "GROUP BY" in call_args

    @pytest.mark.asyncio
    async def test_sql_error_handling(self, mock_connector):
        from app.connectors.datasphere import DatasphereQueryError

        mock_connector.execute_sql = AsyncMock(side_effect=DatasphereQueryError("Connection lost"))

        result = await availability_tools.check_data_availability(
            table="CV_ZBC_AA61",
            connector=mock_connector,
        )

        assert "error" in result
        assert result["data_found"] is False

    @pytest.mark.asyncio
    async def test_invalid_table_name(self, mock_connector):
        result = await availability_tools.check_data_availability(
            table="DROP TABLE; --",
            connector=mock_connector,
        )

        assert "error" in result
        assert result["data_found"] is False
        mock_connector.execute_sql.assert_not_called()

    @pytest.mark.asyncio
    async def test_invalid_filter_column(self, mock_connector):
        result = await availability_tools.check_data_availability(
            table="CV_ZBC_AA61",
            filters={"'; DROP TABLE --": "bad"},
            connector=mock_connector,
        )

        assert "error" in result
        assert result["data_found"] is False
        mock_connector.execute_sql.assert_not_called()

    @pytest.mark.asyncio
    async def test_query_includes_schema(self, mock_connector):
        mock_connector.execute_sql = AsyncMock(return_value=[])

        await availability_tools.check_data_availability(
            table="CV_ZBC_AA61",
            connector=mock_connector,
        )

        call_args = mock_connector.execute_sql.call_args[0][0]
        assert '"BW2AI"' in call_args
        assert '"CV_ZBC_AA61"' in call_args

    @pytest.mark.asyncio
    async def test_filters_applied_in_result(self, mock_connector):
        mock_connector.execute_sql = AsyncMock(return_value=[])
        filters = {"ZCOMPCODE": "1110"}

        result = await availability_tools.check_data_availability(
            table="CV_ZBC_AA61",
            filters=filters,
            connector=mock_connector,
        )

        # User-provided filters are merged with default_filters from config
        assert result["filters_applied"]["ZCOMPCODE"] == "1110"
        assert "ZVERSION" in result["filters_applied"]
        assert "ZGRPACCT" in result["filters_applied"]

    @pytest.mark.asyncio
    async def test_invalid_group_by_column(self, mock_connector):
        result = await availability_tools.check_data_availability(
            table="CV_ZBC_AA61",
            group_by=["'; DROP TABLE --"],
            connector=mock_connector,
        )

        assert "error" in result
        assert result["data_found"] is False
        mock_connector.execute_sql.assert_not_called()

    @pytest.mark.asyncio
    async def test_multiple_groups_returned(self, mock_connector):
        mock_connector.execute_sql = AsyncMock(
            return_value=[
                {"ZCOMPCODE": "1110", "ZVERSION": "001", "CS_TRN_LC": 10000, "CS_TRN_GC": 1000},
                {"ZCOMPCODE": "1110", "ZVERSION": "021", "CS_TRN_LC": 5000, "CS_TRN_GC": 500},
                {"ZCOMPCODE": "2200", "ZVERSION": "001", "CS_TRN_LC": 8000, "CS_TRN_GC": 800},
            ]
        )

        result = await availability_tools.check_data_availability(
            table="CV_ZBC_AA61",
            group_by=["ZCOMPCODE", "ZVERSION"],
            connector=mock_connector,
        )

        assert result["data_found"] is True
        assert result["totals"] == {"CS_TRN_LC": 23000, "CS_TRN_GC": 2300}
        assert result["group_count"] == 3
        assert result["groups"][0]["ZCOMPCODE"] == "1110"
        assert result["groups"][0]["CS_TRN_LC"] == 10000
        assert result["groups"][1]["ZCOMPCODE"] == "1110"
        assert result["groups"][1]["CS_TRN_LC"] == 5000
        assert result["groups"][2]["ZCOMPCODE"] == "2200"
        assert result["groups"][2]["CS_TRN_LC"] == 8000

    @pytest.mark.asyncio
    async def test_sample_rows_capped_at_three(self, mock_connector):
        mock_connector.execute_sql = AsyncMock(
            return_value=[
                {"ZCOMPCODE": "1110", "CS_TRN_LC": 10000, "CS_TRN_GC": 1000},
                {"ZCOMPCODE": "2200", "CS_TRN_LC": 5000, "CS_TRN_GC": 500},
                {"ZCOMPCODE": "3300", "CS_TRN_LC": 8000, "CS_TRN_GC": 800},
                {"ZCOMPCODE": "4400", "CS_TRN_LC": 3000, "CS_TRN_GC": 300},
                {"ZCOMPCODE": "5500", "CS_TRN_LC": 7000, "CS_TRN_GC": 700},
            ]
        )

        result = await availability_tools.check_data_availability(
            table="CV_ZBC_AA61",
            group_by=["ZCOMPCODE"],
            connector=mock_connector,
        )

        assert len(result["sample_rows"]) == 3
        assert len(result["groups"]) == 5
        assert result["sample_rows"][0]["ZCOMPCODE"] == "1110"
        assert result["sample_rows"][2]["ZCOMPCODE"] == "3300"

    @pytest.mark.asyncio
    async def test_sample_rows_empty_when_no_data(self, mock_connector):
        mock_connector.execute_sql = AsyncMock(return_value=[])

        result = await availability_tools.check_data_availability(
            table="CV_ZBC_AA61",
            connector=mock_connector,
        )

        assert result["sample_rows"] == []

    @pytest.mark.asyncio
    async def test_no_filters_omits_where_clause(self, mock_connector):
        """Tables without default_filters and no user filters produce no WHERE clause."""
        mock_connector.execute_sql = AsyncMock(return_value=[])

        await availability_tools.check_data_availability(
            table="CV_ZFI_AA01",
            group_by=["ZCOMPCODE"],
            connector=mock_connector,
        )

        call_args = mock_connector.execute_sql.call_args[0][0]
        assert "WHERE" not in call_args

    @pytest.mark.asyncio
    async def test_default_filters_applied_when_no_user_filters(self, mock_connector):
        """Tables with default_filters include them even when user passes no filters."""
        mock_connector.execute_sql = AsyncMock(return_value=[])

        await availability_tools.check_data_availability(
            table="CV_ZBC_AA61",
            group_by=["ZCOMPCODE"],
            connector=mock_connector,
        )

        call_args = mock_connector.execute_sql.call_args[0][0]
        assert "WHERE" in call_args
        assert '"ZVERSION"' in call_args
        assert '"ZGRPACCT"' in call_args

    @pytest.mark.asyncio
    async def test_filter_value_with_single_quote_escaped(self, mock_connector):
        mock_connector.execute_sql = AsyncMock(return_value=[])

        await availability_tools.check_data_availability(
            table="CV_ZBC_AA61",
            filters={"ZCOMPCODE": "O'Brien"},
            connector=mock_connector,
        )

        call_args = mock_connector.execute_sql.call_args[0][0]
        assert "O''Brien" in call_args

    @pytest.mark.asyncio
    async def test_unknown_table_uses_empty_group_by(self, mock_connector):
        mock_connector.execute_sql = AsyncMock(return_value=[{"ROW_COUNT": 100}])

        result = await availability_tools.check_data_availability(
            table="UNKNOWN_TABLE_XYZ",
            connector=mock_connector,
        )

        assert result["group_by"] == []
        assert result["totals"] == {"ROW_COUNT": 100}
        call_args = mock_connector.execute_sql.call_args[0][0]
        assert "GROUP BY" not in call_args

    @pytest.mark.asyncio
    async def test_no_group_by_query_uses_measures(self, mock_connector):
        """Table with configured measures uses SUM aggregation even without group_by."""
        mock_connector.execute_sql = AsyncMock(
            return_value=[{"CS_TRN_LC": 50000, "CS_TRN_GC": 6000}]
        )

        result = await availability_tools.check_data_availability(
            table="CV_ZBC_AA61",
            group_by=[],
            connector=mock_connector,
        )

        call_args = mock_connector.execute_sql.call_args[0][0]
        assert 'SUM("CS_TRN_LC")' in call_args
        assert 'SUM("CS_TRN_GC")' in call_args
        assert "GROUP BY" not in call_args
        assert result["totals"] == {"CS_TRN_LC": 50000, "CS_TRN_GC": 6000}

    @pytest.mark.asyncio
    async def test_no_measures_falls_back_to_count(self, mock_connector):
        """Table without configured measures uses COUNT(*)."""
        mock_connector.execute_sql = AsyncMock(return_value=[{"ROW_COUNT": 50}])

        result = await availability_tools.check_data_availability(
            table="UNKNOWN_TABLE_XYZ",
            group_by=[],
            connector=mock_connector,
        )

        call_args = mock_connector.execute_sql.call_args[0][0]
        assert 'COUNT(*) as "ROW_COUNT"' in call_args
        assert result["totals"] == {"ROW_COUNT": 50}

    @pytest.mark.asyncio
    async def test_query_key_in_success_result(self, mock_connector):
        mock_connector.execute_sql = AsyncMock(return_value=[])

        result = await availability_tools.check_data_availability(
            table="CV_ZBC_AA61",
            connector=mock_connector,
        )

        assert "query" in result
        assert "SELECT" in result["query"]

    @pytest.mark.asyncio
    async def test_error_result_structure(self, mock_connector):
        from app.connectors.datasphere import DatasphereQueryError

        mock_connector.execute_sql = AsyncMock(side_effect=DatasphereQueryError("timeout"))

        result = await availability_tools.check_data_availability(
            table="CV_ZBC_AA61",
            filters={"ZCOMPCODE": "1110"},
            connector=mock_connector,
        )

        assert result["error"] == "timeout"
        assert result["table"] == "CV_ZBC_AA61"
        assert result["data_found"] is False
        assert result["groups"] == []
        assert result["filters_applied"]["ZCOMPCODE"] == "1110"

    @pytest.mark.asyncio
    async def test_rejects_array_filters(self, mock_connector):
        """When LLM passes filters as an array instead of a dict, return error."""
        result = await availability_tools.check_data_availability(
            table="CV_ZBC_AA61",
            filters=[{"field": "ZCOMPCODE", "operator": "=", "value": "1110"}],
            connector=mock_connector,
        )

        assert "error" in result
        assert result["data_found"] is False
        assert "flat object" in result["error"]
        # Connector should NOT have been queried
        mock_connector.execute_sql.assert_not_called()
