"""Tests for Tool class."""

import pytest
from pydantic import BaseModel, Field

from app.core.tool import Tool


class SimpleInput(BaseModel):
    value: str = Field(description="A simple value")


class MultiInput(BaseModel):
    required_field: str
    optional_field: int | None = None


def simple_func(value: str) -> str:
    return f"Result: {value}"


def multi_func(required_field: str, optional_field: int | None = None) -> dict:
    return {"required": required_field, "optional": optional_field}


async def async_func(value: str) -> str:
    return f"Async: {value}"


class TestTool:
    def test_create_tool(self):
        tool = Tool(
            name="test_tool",
            description="A test tool",
            function=simple_func,
            input_schema=SimpleInput,
        )
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"

    def test_execute_validates_input(self):
        tool = Tool(
            name="simple",
            description="Simple tool",
            function=simple_func,
            input_schema=SimpleInput,
        )
        result = tool.execute(value="hello")
        assert result == "Result: hello"

    def test_execute_with_optional_params(self):
        tool = Tool(
            name="multi",
            description="Multi param tool",
            function=multi_func,
            input_schema=MultiInput,
        )

        # With optional
        result = tool.execute(required_field="test", optional_field=42)
        assert result == {"required": "test", "optional": 42}

        # Without optional
        result = tool.execute(required_field="test")
        assert result == {"required": "test", "optional": None}

    def test_execute_raises_on_invalid_input(self):
        tool = Tool(
            name="simple",
            description="Simple tool",
            function=simple_func,
            input_schema=SimpleInput,
        )
        with pytest.raises(Exception):  # Pydantic ValidationError
            tool.execute()  # Missing required field

    @pytest.mark.asyncio
    async def test_async_execute(self):
        tool = Tool(
            name="async_tool",
            description="Async tool",
            function=async_func,
            input_schema=SimpleInput,
        )
        result = await tool.aexecute(value="world")
        assert result == "Async: world"

    def test_to_langchain_tool(self):
        tool = Tool(
            name="test",
            description="Test description",
            function=simple_func,
            input_schema=SimpleInput,
        )
        lc_tool = tool.to_langchain_tool()

        assert lc_tool["name"] == "test"
        assert lc_tool["description"] == "Test description"
        assert "properties" in lc_tool["parameters"]
        assert "value" in lc_tool["parameters"]["properties"]
