"""Tool definition for skills."""

import logging
import types
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, get_args, get_origin

from pydantic import BaseModel

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Tool:
    """Represents a callable tool within a skill.

    Attributes:
        name: Unique identifier for the tool.
        description: Human-readable description shown to LLM.
        function: The callable that executes the tool.
        input_schema: Pydantic model defining input parameters.
    """

    name: str
    description: str
    function: Callable[..., Any]
    input_schema: type[BaseModel]

    def _coerce_args(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Coerce LLM-provided arguments to match expected schema types.

        Small/local LLMs often send wrong types (e.g. {} instead of [] for
        lists, or a bare string instead of a single-element list). This
        method applies best-effort coercion so that Pydantic validation
        succeeds for these common mistakes.
        """
        hints = self.input_schema.model_fields
        coerced = dict(kwargs)

        for field_name, field_info in hints.items():
            if field_name not in coerced:
                continue

            value = coerced[field_name]
            expected = field_info.annotation

            # Unwrap Optional (Union[X, None]) to get the inner type
            origin = get_origin(expected)
            if origin is types.UnionType:  # e.g. int | str, Optional via X | None
                inner_types = [t for t in get_args(expected) if t is not type(None)]
                if len(inner_types) == 1:
                    expected = inner_types[0]
                    origin = get_origin(expected)

            # Coerce dict → list when a list is expected
            if expected is list or origin is list:
                if isinstance(value, dict):
                    if not value:
                        coerced[field_name] = []
                    else:
                        coerced[field_name] = list(value.keys())
                    logger.debug("Tool %s: coerced %s from dict to list", self.name, field_name)
                elif isinstance(value, str):
                    coerced[field_name] = [value]
                    logger.debug("Tool %s: coerced %s from str to list", self.name, field_name)

            # Coerce list/other → dict when a dict is expected
            elif expected is dict or origin is dict:
                if isinstance(value, list):
                    coerced[field_name] = {}
                    logger.debug("Tool %s: coerced %s from list to dict", self.name, field_name)

            # Coerce str → int/float when a number is expected
            elif expected in (int, float) and isinstance(value, str):
                try:
                    coerced[field_name] = expected(value)
                    logger.debug(
                        "Tool %s: coerced %s from str to %s",
                        self.name,
                        field_name,
                        expected.__name__,
                    )
                except (ValueError, TypeError):
                    pass  # let Pydantic report the error

        return coerced

    def execute(self, **kwargs: Any) -> Any:
        """Execute the tool with validated inputs.

        Args:
            **kwargs: Tool parameters matching input_schema.

        Returns:
            Tool execution result.
        """
        kwargs = self._coerce_args(kwargs)
        validated = self.input_schema(**kwargs)
        return self.function(**validated.model_dump())

    async def aexecute(self, **kwargs: Any) -> Any:
        """Execute the tool asynchronously with validated inputs.

        For async functions, awaits the result.
        For sync functions, calls directly.
        """
        import asyncio

        kwargs = self._coerce_args(kwargs)
        validated = self.input_schema(**kwargs)
        result = self.function(**validated.model_dump())

        if asyncio.iscoroutine(result):
            return await result
        return result

    def to_langchain_tool(self) -> dict:
        """Convert to LangChain tool format for binding to models."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.input_schema.model_json_schema(),
        }
