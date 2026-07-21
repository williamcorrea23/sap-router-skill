"""Tool implementations for ownership_check skill."""

import logging
import re
from typing import Any

from app.connectors.datasphere import DatasphereQueryError
from app.skills.common import get_connector

logger = logging.getLogger(__name__)

# Pattern for valid parameter values (alphanumeric only — fiscal periods and company codes)
_VALID_PARAM = re.compile(r"^[a-zA-Z0-9_]+$")


async def check_ownership(
    param_fiscper: str,
    param_cocd: str,
    connector: Any = None,
) -> dict[str, Any]:
    """Check if a company code is present in the defined scope and fiscal period."""
    conn = get_connector(connector)

    # Validate inputs to prevent SQL injection
    if not _VALID_PARAM.match(param_fiscper):
        return {
            "error": f"Invalid fiscal period: {param_fiscper}",
            "result": None,
            "param_fiscper": param_fiscper,
            "param_cocd": param_cocd,
        }
    if not _VALID_PARAM.match(param_cocd):
        return {
            "error": f"Invalid company code: {param_cocd}",
            "result": None,
            "param_fiscper": param_fiscper,
            "param_cocd": param_cocd,
        }

    query = f"""
SELECT * FROM "BW2AI"."CV_ZBC_AA08Z"
WHERE "FISCPER" = '{param_fiscper}'
 AND "ZCOMPCODE" = '{param_cocd}'
 AND (("ZSCOPE" IN ('S_LEGAL', 'S_LEGAL_DKK', 'S_LEGAL_SPECIAL') AND "ZVERSION" = '001')
 OR ("ZSCOPE" = 'S_LEGAL' AND "ZVERSION" = '021'))
""".strip()

    logger.info("check_ownership: fiscper=%s cocd=%s", param_fiscper, param_cocd)
    logger.debug("check_ownership: query=\n%s", query)

    try:
        results = await conn.execute_sql(query)
        found = len(results) > 0

        logger.info("check_ownership: found=%s rows=%d", found, len(results))
        for row in results[:3]:
            logger.debug("check_ownership: sample_row=%s", row)

        return {
            "result": found,
            "rows_found": len(results),
            "param_fiscper": param_fiscper,
            "param_cocd": param_cocd,
            "columns": list(results[0].keys()) if results else [],
        }
    except DatasphereQueryError as e:
        logger.error("check_ownership: query failed — %s", e)
        return {
            "error": str(e),
            "result": None,
            "param_fiscper": param_fiscper,
            "param_cocd": param_cocd,
        }
