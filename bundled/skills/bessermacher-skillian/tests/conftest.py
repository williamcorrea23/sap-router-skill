"""Shared test fixtures."""

import tempfile
from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.config import Settings
from app.core import SkillRegistry, Tool


@pytest.fixture(autouse=True)
def reset_db_connection():
    """Reset database connection between tests to avoid event loop issues."""
    import app.db.connection as db_conn

    # Reset the global state before each test
    db_conn._engine = None
    db_conn._async_session_factory = None
    yield
    # Reset again after test
    db_conn._engine = None
    db_conn._async_session_factory = None


# Settings Fixtures


@pytest.fixture
def test_settings() -> Settings:
    """Test settings with defaults."""
    return Settings(
        env="development",
        debug=True,
        llm_provider="ollama",
        ollama_base_url="http://localhost:11434",
        ollama_model="llama3.2",
    )


# Tool/Skill Fixtures


class SimpleInput(BaseModel):
    """Simple input for test tools."""

    value: str


def simple_function(value: str) -> dict:
    """Simple test function."""
    return {"result": value}


async def async_function(value: str) -> dict:
    """Async test function."""
    return {"result": value}


@pytest.fixture
def simple_tool() -> Tool:
    """Simple tool for testing."""
    return Tool(
        name="simple_tool",
        description="A simple test tool",
        function=simple_function,
        input_schema=SimpleInput,
    )


@pytest.fixture
def async_tool() -> Tool:
    """Async tool for testing."""
    return Tool(
        name="async_tool",
        description="An async test tool",
        function=async_function,
        input_schema=SimpleInput,
    )


class TestSkill:
    """Test skill implementation."""

    def __init__(self, tools: list[Tool] | None = None):
        self._tools = tools or []

    @property
    def name(self) -> str:
        return "test_skill"

    @property
    def description(self) -> str:
        return "A test skill"

    @property
    def tools(self) -> list[Tool]:
        return self._tools

    @property
    def system_prompt(self) -> str:
        return "You are a test assistant."

    @property
    def knowledge_paths(self) -> list[str]:
        return []

    def get_tool(self, name: str) -> Tool | None:
        for tool in self._tools:
            if tool.name == name:
                return tool
        return None


@pytest.fixture
def test_skill(simple_tool: Tool) -> TestSkill:
    """Test skill with one tool."""
    return TestSkill(tools=[simple_tool])


@pytest.fixture
def skill_registry(test_skill: TestSkill) -> SkillRegistry:
    """Registry with test skill registered."""
    registry = SkillRegistry()
    registry.register(test_skill)
    return registry


# LLM Mocks


@pytest.fixture
def mock_chat_model() -> MagicMock:
    """Mock LangChain chat model."""
    model = MagicMock()

    # Mock response without tool calls
    mock_response = MagicMock()
    mock_response.content = "Mock response"
    mock_response.tool_calls = None

    model.ainvoke = AsyncMock(return_value=mock_response)
    model.bind_tools = MagicMock(return_value=model)

    return model


@pytest.fixture
def mock_chat_model_with_tool_call() -> MagicMock:
    """Mock chat model that makes tool calls."""
    model = MagicMock()

    # First response: tool call
    tool_response = MagicMock()
    tool_response.content = ""
    tool_response.tool_calls = [{"id": "call_1", "name": "simple_tool", "args": {"value": "test"}}]

    # Second response: final answer
    final_response = MagicMock()
    final_response.content = "Final answer after tool call"
    final_response.tool_calls = None

    model.ainvoke = AsyncMock(side_effect=[tool_response, final_response])
    model.bind_tools = MagicMock(return_value=model)

    return model


# API Fixtures


@pytest.fixture
def client() -> Generator[TestClient]:
    """FastAPI test client."""
    from main import app

    with TestClient(app) as client:
        yield client


# Temp Directory Fixtures


@pytest.fixture
def temp_dir() -> Generator[str]:
    """Temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


# Mock Embeddings


class MockEmbeddings:
    """Mock embeddings for testing without real models."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return mock embeddings."""
        return [[0.1] * self.dimension for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        """Return mock query embedding."""
        return [0.1] * self.dimension


@pytest.fixture
def mock_embeddings() -> MockEmbeddings:
    """Mock embeddings instance."""
    return MockEmbeddings()
