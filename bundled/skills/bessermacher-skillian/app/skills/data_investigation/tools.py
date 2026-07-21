"""Tool implementations for data_investigation skill."""

from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

from app.skills.common import get_connector

# Request-scoped investigation state via contextvars.
# Each asyncio task (i.e. each FastAPI request) gets its own value,
# preventing cross-request leakage in concurrent scenarios.
_current_investigation: ContextVar[dict[str, Any] | None] = ContextVar(
    "_current_investigation", default=None
)


_VERSION_TABLE_MAP = {
    "001": "CV_ZBC_AA61",
    "002": "CV_ZBC_AA61",
    "003": "CV_ZBC_AA61",
    "004": "CV_ZBC_AA61",
    "021": "CV_ZBC_AA62",
}

_VERSION_NAMES = {
    "001": "Actual",
    "002": "Actuals at last year budget rate",
    "003": "Actuals at budget rate",
    "004": "Actuals at next year budget rate",
    "021": "Forecast",
}


def _build_next_step(inv: dict[str, Any]) -> dict[str, Any]:
    """Build the next_step directive from an investigation's state."""
    version = inv.get("version", "001")
    table = _VERSION_TABLE_MAP.get(version, "CV_ZBC_AA61")
    filters: dict[str, str] = {}
    if inv.get("company_code"):
        filters["ZCOMPCODE"] = inv["company_code"]
    if inv.get("fiscal_period"):
        filters["FISCPER"] = inv["fiscal_period"]
    return {
        "action": "call check_data_availability now",
        "table": table,
        "filters": filters,
        "version": version,
        "version_name": _VERSION_NAMES.get(version, f"Version {version}"),
    }


def start_investigation(
    problem_description: str,
    report_name: str | None = None,
    company_code: str | None = None,
    fiscal_period: str | None = None,
    version: str | None = None,
    connector: Any = None,
) -> dict[str, Any]:
    """Start a new data investigation."""
    if connector is not None:
        get_connector(connector)

    current = _current_investigation.get()

    # Guard: refuse to restart if an investigation is already in progress.
    if current is not None and current["status"] == "in_progress":
        return {
            "error": "Investigation already in progress. Do NOT call start_investigation again.",
            "investigation_id": current["id"],
            "instruction": (
                "Continue the current investigation. "
                "Call check_data_availability NOW with the table and filters below."
            ),
            "next_step": _build_next_step(current),
        }

    version = version or "001"

    new_inv = {
        "id": f"inv_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S_%f')}",
        "started_at": datetime.now(UTC).isoformat(),
        "problem_description": problem_description,
        "report_name": report_name,
        "company_code": company_code,
        "fiscal_period": fiscal_period,
        "version": version,
        "findings": [],
        "status": "in_progress",
    }
    _current_investigation.set(new_inv)

    return {
        "investigation_id": new_inv["id"],
        "status": "started",
        "next_step": _build_next_step(new_inv),
    }


def record_finding(
    step_name: str,
    result_summary: str,
    conclusion: str,
    tool_used: str | None = None,
    status: str | None = None,
    connector: Any = None,
) -> dict[str, Any]:
    """Record a finding from an investigation step."""
    if connector is not None:
        get_connector(connector)

    current = _current_investigation.get()

    if current is None:
        return {
            "error": "No active investigation. Call start_investigation first.",
        }

    finding = {
        "step_number": len(current["findings"]) + 1,
        "step_name": step_name,
        "tool_used": tool_used,
        "result_summary": result_summary,
        "conclusion": conclusion,
        "status": status or "needs_further_check",
        "recorded_at": datetime.now(UTC).isoformat(),
    }

    current["findings"].append(finding)

    return {
        "recorded": True,
        "step_number": finding["step_number"],
        "step_name": step_name,
        "total_findings": len(current["findings"]),
    }


def get_investigation_summary(
    connector: Any = None,
) -> dict[str, Any]:
    """Get complete investigation summary."""
    if connector is not None:
        get_connector(connector)

    current = _current_investigation.get()

    if current is None:
        return {
            "error": "No active investigation.",
            "findings": [],
        }

    finding_statuses = [f["status"] for f in current["findings"]]

    if "issue_found" in finding_statuses:
        overall_status = "issues_identified"
    elif finding_statuses and all(s == "normal" for s in finding_statuses):
        overall_status = "no_issues_found"
    else:
        overall_status = "investigation_in_progress"

    return {
        "investigation_id": current["id"],
        "problem_description": current["problem_description"],
        "context": {
            "report_name": current["report_name"],
            "company_code": current["company_code"],
            "fiscal_period": current["fiscal_period"],
            "version": current.get("version", "001"),
            "version_name": _VERSION_NAMES.get(current.get("version", "001"), "Unknown"),
        },
        "started_at": current["started_at"],
        "status": overall_status,
        "total_findings": len(current["findings"]),
        "findings": current["findings"],
    }
