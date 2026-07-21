"""Tests for data_investigation skill."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.core.skill_loader import SkillLoader
from app.skills import common as skills_common
from app.skills.data_investigation import tools as investigation_tools

# --- Fixtures ---


@pytest.fixture
def mock_connector():
    """Mock Datasphere connector."""
    connector = MagicMock()
    connector.space = "TEST_SPACE"
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
    """Load the data_investigation skill."""
    return skill_loader.load_skill("data_investigation")


@pytest.fixture(autouse=True)
def reset_investigation_state():
    """Reset investigation state between tests.

    _current_investigation is now a ContextVar; use .set() to reset it.
    """
    investigation_tools._current_investigation.set(None)
    skills_common._connector = None
    yield
    investigation_tools._current_investigation.set(None)
    skills_common._connector = None


# --- Skill Loading Tests ---


class TestDataInvestigationSkill:
    def test_skill_name(self, skill):
        assert skill.name == "data-investigation"

    def test_skill_description(self, skill):
        assert "investigation" in skill.description.lower()

    def test_skill_has_tools(self, skill):
        assert len(skill.tools) == 3

    def test_tool_names(self, skill):
        tool_names = [t.name for t in skill.tools]
        assert "start_investigation" in tool_names
        assert "record_finding" in tool_names
        assert "get_investigation_summary" in tool_names

    def test_system_prompt_contains_playbook(self, skill):
        assert "playbook" in skill.system_prompt.lower()

    def test_system_prompt_contains_versions(self, skill):
        assert "001" in skill.system_prompt
        assert "021" in skill.system_prompt

    def test_connector_type(self, skill):
        assert skill.connector_type == "datasphere"

    def test_knowledge_paths(self, skill):
        assert len(skill.knowledge_paths) > 0


# --- Tool Function Tests ---


class TestStartInvestigation:
    def test_start_creates_investigation(self):
        result = investigation_tools.start_investigation(
            problem_description="No actual data for CoCd 1110 in Dec 2024",
        )

        assert result["status"] == "started"
        assert "investigation_id" in result
        assert result["investigation_id"].startswith("inv_")

    def test_start_returns_next_step(self):
        result = investigation_tools.start_investigation(
            problem_description="Missing data",
            company_code="1110",
            fiscal_period="2024012",
            version="001",
        )

        assert result["next_step"]["table"] == "CV_ZBC_AA61"
        assert result["next_step"]["filters"]["ZCOMPCODE"] == "1110"
        assert result["next_step"]["filters"]["FISCPER"] == "2024012"

    def test_start_forecast_version_uses_aa62(self):
        result = investigation_tools.start_investigation(
            problem_description="Missing forecast data",
            company_code="2200",
            fiscal_period="2025006",
            version="021",
        )

        assert result["next_step"]["table"] == "CV_ZBC_AA62"

    def test_start_defaults_to_version_001(self):
        result = investigation_tools.start_investigation(
            problem_description="Missing data",
            company_code="1110",
            fiscal_period="2024012",
        )

        assert result["next_step"]["table"] == "CV_ZBC_AA61"

    def test_start_blocks_when_investigation_in_progress(self):
        result1 = investigation_tools.start_investigation(
            problem_description="First investigation",
            company_code="1110",
            fiscal_period="2024012",
        )
        assert result1["status"] == "started"

        # Second call should be blocked
        result2 = investigation_tools.start_investigation(
            problem_description="Second investigation",
        )
        assert "error" in result2
        assert result2["investigation_id"] == result1["investigation_id"]
        assert "check_data_availability" in result2["instruction"]
        assert result2["next_step"]["table"] == "CV_ZBC_AA61"
        assert result2["next_step"]["filters"]["ZCOMPCODE"] == "1110"

        # Current investigation should still be the first one
        summary = investigation_tools.get_investigation_summary()
        assert summary["problem_description"] == "First investigation"

    def test_start_with_connector(self, mock_connector):
        result = investigation_tools.start_investigation(
            problem_description="Test",
            connector=mock_connector,
        )
        assert result["status"] == "started"


class TestRecordFinding:
    def test_record_requires_active_investigation(self):
        result = investigation_tools.record_finding(
            step_name="Step 1",
            result_summary="Some result",
            conclusion="Some conclusion",
        )

        assert "error" in result

    def test_record_finding_success(self):
        investigation_tools.start_investigation(
            problem_description="Test investigation",
        )

        result = investigation_tools.record_finding(
            step_name="Check reporting table",
            result_summary="No data found in CV_ZBC_AA61",
            conclusion="Data is missing from reporting. Need to check BPC engine.",
            tool_used="check_data_availability",
            status="needs_further_check",
        )

        assert result["recorded"] is True
        assert result["step_number"] == 1
        assert result["step_name"] == "Check reporting table"
        assert result["total_findings"] == 1

    def test_record_multiple_findings(self):
        investigation_tools.start_investigation(
            problem_description="Test investigation",
        )

        investigation_tools.record_finding(
            step_name="Step 1",
            result_summary="Result 1",
            conclusion="Conclusion 1",
        )
        investigation_tools.record_finding(
            step_name="Step 2",
            result_summary="Result 2",
            conclusion="Conclusion 2",
        )
        result = investigation_tools.record_finding(
            step_name="Step 3",
            result_summary="Result 3",
            conclusion="Conclusion 3",
        )

        assert result["step_number"] == 3
        assert result["total_findings"] == 3

    def test_record_finding_default_status(self):
        investigation_tools.start_investigation(
            problem_description="Test investigation",
        )

        investigation_tools.record_finding(
            step_name="Step 1",
            result_summary="Result",
            conclusion="Conclusion",
        )

        summary = investigation_tools.get_investigation_summary()
        assert summary["findings"][0]["status"] == "needs_further_check"

    def test_record_finding_custom_status(self):
        investigation_tools.start_investigation(
            problem_description="Test investigation",
        )

        investigation_tools.record_finding(
            step_name="Step 1",
            result_summary="Found the problem",
            conclusion="Data is missing",
            status="issue_found",
        )

        summary = investigation_tools.get_investigation_summary()
        assert summary["findings"][0]["status"] == "issue_found"


class TestGetInvestigationSummary:
    def test_no_active_investigation(self):
        result = investigation_tools.get_investigation_summary()
        assert "error" in result

    def test_empty_investigation(self):
        investigation_tools.start_investigation(
            problem_description="Test investigation",
        )

        result = investigation_tools.get_investigation_summary()
        assert result["status"] == "investigation_in_progress"
        assert result["total_findings"] == 0
        assert result["findings"] == []

    def test_investigation_with_issues(self):
        investigation_tools.start_investigation(
            problem_description="Test investigation",
        )
        investigation_tools.record_finding(
            step_name="Step 1",
            result_summary="Problem found",
            conclusion="Data missing",
            status="issue_found",
        )

        result = investigation_tools.get_investigation_summary()
        assert result["status"] == "issues_identified"

    def test_investigation_all_normal(self):
        investigation_tools.start_investigation(
            problem_description="Test investigation",
        )
        investigation_tools.record_finding(
            step_name="Step 1",
            result_summary="Data present",
            conclusion="All good",
            status="normal",
        )
        investigation_tools.record_finding(
            step_name="Step 2",
            result_summary="Data matches",
            conclusion="All good",
            status="normal",
        )

        result = investigation_tools.get_investigation_summary()
        assert result["status"] == "no_issues_found"

    def test_investigation_mixed_status(self):
        investigation_tools.start_investigation(
            problem_description="Test investigation",
        )
        investigation_tools.record_finding(
            step_name="Step 1",
            result_summary="Data present",
            conclusion="OK",
            status="normal",
        )
        investigation_tools.record_finding(
            step_name="Step 2",
            result_summary="Checking next",
            conclusion="Need more info",
            status="needs_further_check",
        )

        result = investigation_tools.get_investigation_summary()
        assert result["status"] == "investigation_in_progress"

    def test_full_investigation_flow(self):
        """Test a complete investigation matching the CM playbook."""
        # Start
        start_result = investigation_tools.start_investigation(
            problem_description="No actual data for CoCd 1110 in Dec 2024",
            report_name="Consolidated Management PnL",
            company_code="1110",
            fiscal_period="2024012",
        )
        assert start_result["status"] == "started"

        # Step 1: Check reporting table
        investigation_tools.record_finding(
            step_name="Check reporting table",
            tool_used="check_data_availability",
            result_summary="No data found in CV_ZBC_AA61 for CoCd 1110, period 2024012",
            conclusion="Data is missing from reporting table. Checking BPC engine next.",
            status="needs_further_check",
        )

        # Step 2B: Check BPC mart
        investigation_tools.record_finding(
            step_name="Check BPC mart",
            tool_used="check_data_availability",
            result_summary="Data found in CV_ZFI_AA01 with 15 rows",
            conclusion="Data exists in BPC mart but not in reporting. "
            "Reporting data load likely not triggered.",
            status="issue_found",
        )

        # Get summary
        summary = investigation_tools.get_investigation_summary()

        assert summary["status"] == "issues_identified"
        assert summary["total_findings"] == 2
        assert summary["context"]["company_code"] == "1110"
        assert summary["context"]["fiscal_period"] == "2024012"
        assert summary["findings"][0]["step_name"] == "Check reporting table"
        assert summary["findings"][1]["step_name"] == "Check BPC mart"
        assert summary["findings"][0]["step_number"] == 1
        assert summary["findings"][1]["step_number"] == 2
