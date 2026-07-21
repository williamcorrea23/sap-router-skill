"""Tests for Skill protocol and ConfiguredSkill."""

from pydantic import BaseModel

from app.core import ConfiguredSkill, Skill, Tool


class DummyInput(BaseModel):
    param: str


def dummy_func(param: str) -> str:
    return param


class TestSkillProtocol:
    """Test that ConfiguredSkill implements the Skill protocol."""

    def test_implements_protocol(self):
        skill = ConfiguredSkill(
            name="test_skill",
            description="A test skill",
            system_prompt="You are a test assistant.",
            tools=[
                Tool(
                    name="dummy_tool",
                    description="A dummy tool",
                    function=dummy_func,
                    input_schema=DummyInput,
                )
            ],
        )
        assert isinstance(skill, Skill)

    def test_get_tool_found(self):
        skill = ConfiguredSkill(
            name="test_skill",
            description="A test skill",
            system_prompt="You are a test assistant.",
            tools=[
                Tool(
                    name="dummy_tool",
                    description="A dummy tool",
                    function=dummy_func,
                    input_schema=DummyInput,
                )
            ],
        )
        tool = skill.get_tool("dummy_tool")
        assert tool is not None
        assert tool.name == "dummy_tool"

    def test_get_tool_not_found(self):
        skill = ConfiguredSkill(
            name="test_skill",
            description="A test skill",
            system_prompt="You are a test assistant.",
        )
        tool = skill.get_tool("nonexistent")
        assert tool is None

    def test_get_tool_names(self):
        skill = ConfiguredSkill(
            name="test_skill",
            description="A test skill",
            system_prompt="You are a test assistant.",
            tools=[
                Tool(
                    name="dummy_tool",
                    description="A dummy tool",
                    function=dummy_func,
                    input_schema=DummyInput,
                )
            ],
        )
        names = skill.get_tool_names()
        assert names == ["dummy_tool"]

    def test_knowledge_paths_default_empty(self):
        skill = ConfiguredSkill(
            name="test_skill",
            description="A test skill",
            system_prompt="You are a test assistant.",
        )
        assert skill.knowledge_paths == []

    def test_repr(self):
        skill = ConfiguredSkill(
            name="test_skill",
            description="A test skill",
            system_prompt="You are a test assistant.",
        )
        repr_str = repr(skill)
        assert "ConfiguredSkill" in repr_str
        assert "test_skill" in repr_str
