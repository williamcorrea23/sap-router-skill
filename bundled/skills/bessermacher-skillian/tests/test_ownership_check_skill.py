"""Tests for ownership_check skill."""

import logging
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.connectors.datasphere import DatasphereQueryError
from app.core.skill_loader import SkillLoader
from app.skills import common as skills_common
from app.skills.ownership_check import tools as ownership_tools

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
    """Load the ownership_check skill."""
    return skill_loader.load_skill("ownership_check")


@pytest.fixture(autouse=True)
def reset_module_state(mock_connector):
    """Reset module-level state between tests."""
    skills_common._connector = mock_connector
    yield
    skills_common._connector = None


# --- Skill Loading Tests ---


class TestOwnershipCheckSkill:
    def test_skill_name(self, skill):
        assert skill.name == "ownership-check"

    def test_skill_description(self, skill):
        assert "company code" in skill.description.lower()

    def test_skill_has_tools(self, skill):
        assert len(skill.tools) == 1

    def test_tool_names(self, skill):
        tool_names = [t.name for t in skill.tools]
        assert "check_ownership" in tool_names

    def test_system_prompt_not_empty(self, skill):
        assert len(skill.system_prompt) > 50

    def test_connector_type(self, skill):
        assert skill.connector_type == "datasphere"


# --- Tool Function Tests ---


class TestCheckOwnership:
    @pytest.mark.asyncio
    async def test_ownership_found(self, mock_connector, caplog):
        mock_connector.execute_sql = AsyncMock(
            return_value=[
                {
                    "FISCPER": "2024012",
                    "ZCOMPCODE": "1110",
                    "ZSCOPE": "S_LEGAL",
                    "ZVERSION": "001",
                },
            ]
        )

        with caplog.at_level(logging.DEBUG):
            result = await ownership_tools.check_ownership(
                param_fiscper="2024012",
                param_cocd="1110",
                connector=mock_connector,
            )

        logger.info("test_ownership_found result: %s", result)

        assert result["result"] is True
        assert result["rows_found"] == 1
        assert result["param_fiscper"] == "2024012"
        assert result["param_cocd"] == "1110"
        assert "found=True" in caplog.text

    @pytest.mark.asyncio
    async def test_ownership_not_found(self, mock_connector):
        mock_connector.execute_sql = AsyncMock(return_value=[])

        result = await ownership_tools.check_ownership(
            param_fiscper="2024012",
            param_cocd="9999",
            connector=mock_connector,
        )

        assert result["result"] is False
        assert result["rows_found"] == 0

    @pytest.mark.asyncio
    async def test_multiple_rows_found(self, mock_connector):
        mock_connector.execute_sql = AsyncMock(
            return_value=[
                {"FISCPER": "2024012", "ZCOMPCODE": "1110", "ZSCOPE": "S_LEGAL", "ZVERSION": "001"},
                {
                    "FISCPER": "2024012",
                    "ZCOMPCODE": "1110",
                    "ZSCOPE": "S_LEGAL_DKK",
                    "ZVERSION": "001",
                },
                {"FISCPER": "2024012", "ZCOMPCODE": "1110", "ZSCOPE": "S_LEGAL", "ZVERSION": "021"},
            ]
        )

        result = await ownership_tools.check_ownership(
            param_fiscper="2024012",
            param_cocd="1110",
            connector=mock_connector,
        )

        assert result["result"] is True
        assert result["rows_found"] == 3

    @pytest.mark.asyncio
    async def test_query_includes_correct_table(self, mock_connector):
        mock_connector.execute_sql = AsyncMock(return_value=[])

        await ownership_tools.check_ownership(
            param_fiscper="2024012",
            param_cocd="1110",
            connector=mock_connector,
        )

        call_args = mock_connector.execute_sql.call_args[0][0]
        assert '"BW2AI"' in call_args
        assert '"CV_ZBC_AA08Z"' in call_args

    @pytest.mark.asyncio
    async def test_query_includes_fiscper_filter(self, mock_connector):
        mock_connector.execute_sql = AsyncMock(return_value=[])

        await ownership_tools.check_ownership(
            param_fiscper="2024006",
            param_cocd="1110",
            connector=mock_connector,
        )

        call_args = mock_connector.execute_sql.call_args[0][0]
        assert "'2024006'" in call_args

    @pytest.mark.asyncio
    async def test_query_includes_company_code_filter(self, mock_connector):
        mock_connector.execute_sql = AsyncMock(return_value=[])

        await ownership_tools.check_ownership(
            param_fiscper="2024012",
            param_cocd="2200",
            connector=mock_connector,
        )

        call_args = mock_connector.execute_sql.call_args[0][0]
        assert "'2200'" in call_args

    @pytest.mark.asyncio
    async def test_query_includes_scope_conditions(self, mock_connector):
        mock_connector.execute_sql = AsyncMock(return_value=[])

        await ownership_tools.check_ownership(
            param_fiscper="2024012",
            param_cocd="1110",
            connector=mock_connector,
        )

        call_args = mock_connector.execute_sql.call_args[0][0]
        assert "S_LEGAL" in call_args
        assert "S_LEGAL_DKK" in call_args
        assert "S_LEGAL_SPECIAL" in call_args

    @pytest.mark.asyncio
    async def test_query_includes_version_conditions(self, mock_connector):
        mock_connector.execute_sql = AsyncMock(return_value=[])

        await ownership_tools.check_ownership(
            param_fiscper="2024012",
            param_cocd="1110",
            connector=mock_connector,
        )

        call_args = mock_connector.execute_sql.call_args[0][0]
        assert "'001'" in call_args
        assert "'021'" in call_args

    @pytest.mark.asyncio
    async def test_sql_error_handling(self, mock_connector):
        mock_connector.execute_sql = AsyncMock(side_effect=DatasphereQueryError("Connection lost"))

        result = await ownership_tools.check_ownership(
            param_fiscper="2024012",
            param_cocd="1110",
            connector=mock_connector,
        )

        assert "error" in result
        assert result["result"] is None
        assert result["param_fiscper"] == "2024012"
        assert result["param_cocd"] == "1110"

    @pytest.mark.asyncio
    async def test_parameters_echoed_in_result(self, mock_connector):
        mock_connector.execute_sql = AsyncMock(return_value=[])

        result = await ownership_tools.check_ownership(
            param_fiscper="2025003",
            param_cocd="3300",
            connector=mock_connector,
        )

        assert result["param_fiscper"] == "2025003"
        assert result["param_cocd"] == "3300"

    @pytest.mark.asyncio
    async def test_columns_returned_when_data_found(self, mock_connector):
        mock_connector.execute_sql = AsyncMock(
            return_value=[
                {
                    "FISCPER": "2024012",
                    "ZCOMPCODE": "1110",
                    "ZSCOPE": "S_LEGAL",
                    "ZVERSION": "001",
                },
            ]
        )

        result = await ownership_tools.check_ownership(
            param_fiscper="2024012",
            param_cocd="1110",
            connector=mock_connector,
        )

        assert result["columns"] == ["FISCPER", "ZCOMPCODE", "ZSCOPE", "ZVERSION"]

    @pytest.mark.asyncio
    async def test_columns_empty_when_no_data(self, mock_connector):
        mock_connector.execute_sql = AsyncMock(return_value=[])

        result = await ownership_tools.check_ownership(
            param_fiscper="2024012",
            param_cocd="9999",
            connector=mock_connector,
        )

        assert result["columns"] == []


class TestInputValidation:
    @pytest.mark.asyncio
    async def test_invalid_fiscper_sql_injection(self, mock_connector):
        result = await ownership_tools.check_ownership(
            param_fiscper="'; DROP TABLE --",
            param_cocd="1110",
            connector=mock_connector,
        )

        assert "error" in result
        assert result["result"] is None
        mock_connector.execute_sql.assert_not_called()

    @pytest.mark.asyncio
    async def test_invalid_cocd_sql_injection(self, mock_connector):
        result = await ownership_tools.check_ownership(
            param_fiscper="2024012",
            param_cocd="1110' OR '1'='1",
            connector=mock_connector,
        )

        assert "error" in result
        assert result["result"] is None
        mock_connector.execute_sql.assert_not_called()

    @pytest.mark.asyncio
    async def test_valid_fiscper_accepted(self, mock_connector):
        mock_connector.execute_sql = AsyncMock(return_value=[])

        result = await ownership_tools.check_ownership(
            param_fiscper="2024012",
            param_cocd="1110",
            connector=mock_connector,
        )

        assert "error" not in result
        mock_connector.execute_sql.assert_called_once()

    @pytest.mark.asyncio
    async def test_invalid_fiscper_with_spaces(self, mock_connector):
        result = await ownership_tools.check_ownership(
            param_fiscper="2024 012",
            param_cocd="1110",
            connector=mock_connector,
        )

        assert "error" in result
        mock_connector.execute_sql.assert_not_called()

    @pytest.mark.asyncio
    async def test_invalid_cocd_with_special_chars(self, mock_connector):
        result = await ownership_tools.check_ownership(
            param_fiscper="2024012",
            param_cocd="11;10",
            connector=mock_connector,
        )

        assert "error" in result
        mock_connector.execute_sql.assert_not_called()


class TestGetConnector:
    def test_connector_not_configured(self):
        skills_common._connector = None

        with pytest.raises(ValueError, match="Datasphere connector not configured"):
            skills_common.get_connector(None)

    def test_connector_passed_directly(self):
        new_connector = MagicMock()
        result = skills_common.get_connector(new_connector)
        assert result is new_connector

    def test_connector_cached(self, mock_connector):
        result = skills_common.get_connector(None)
        assert result is mock_connector
