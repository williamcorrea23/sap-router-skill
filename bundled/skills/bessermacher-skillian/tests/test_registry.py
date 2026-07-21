"""Tests for SkillRegistry."""

import pytest
from pydantic import BaseModel

from app.core import (
    DuplicateSkillError,
    DuplicateToolError,
    SkillNotFoundError,
    SkillRegistry,
    Tool,
    ToolNotFoundError,
)


class DummyInput(BaseModel):
    value: str


def dummy_func(value: str) -> str:
    return value


def create_tool(name: str) -> Tool:
    return Tool(
        name=name,
        description=f"Tool {name}",
        function=dummy_func,
        input_schema=DummyInput,
    )


class SkillA:
    @property
    def name(self) -> str:
        return "skill_a"

    @property
    def description(self) -> str:
        return "Skill A"

    @property
    def tools(self) -> list[Tool]:
        return [create_tool("tool_a1"), create_tool("tool_a2")]

    @property
    def system_prompt(self) -> str:
        return "You are skill A."

    @property
    def knowledge_paths(self) -> list[str]:
        return []

    def get_tool(self, name: str) -> Tool | None:
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None


class SkillB:
    @property
    def name(self) -> str:
        return "skill_b"

    @property
    def description(self) -> str:
        return "Skill B"

    @property
    def tools(self) -> list[Tool]:
        return [create_tool("tool_b1")]

    @property
    def system_prompt(self) -> str:
        return "You are skill B."

    @property
    def knowledge_paths(self) -> list[str]:
        return []

    def get_tool(self, name: str) -> Tool | None:
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None


class SkillWithConflict:
    """Skill with tool name that conflicts with SkillA."""

    @property
    def name(self) -> str:
        return "conflict"

    @property
    def description(self) -> str:
        return "Conflicting skill"

    @property
    def tools(self) -> list[Tool]:
        return [create_tool("tool_a1")]  # Conflicts with SkillA

    @property
    def system_prompt(self) -> str:
        return "Conflict."

    @property
    def knowledge_paths(self) -> list[str]:
        return []

    def get_tool(self, name: str) -> Tool | None:
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None


class TestSkillRegistry:
    def test_register_skill(self):
        registry = SkillRegistry()
        registry.register(SkillA())

        assert registry.skill_count == 1
        assert registry.tool_count == 2

    def test_register_multiple_skills(self):
        registry = SkillRegistry()
        registry.register(SkillA())
        registry.register(SkillB())

        assert registry.skill_count == 2
        assert registry.tool_count == 3

    def test_register_duplicate_skill_raises(self):
        registry = SkillRegistry()
        registry.register(SkillA())

        with pytest.raises(DuplicateSkillError):
            registry.register(SkillA())

    def test_register_conflicting_tool_raises(self):
        registry = SkillRegistry()
        registry.register(SkillA())

        with pytest.raises(DuplicateToolError):
            registry.register(SkillWithConflict())

    def test_get_skill(self):
        registry = SkillRegistry()
        registry.register(SkillA())

        skill = registry.get_skill("skill_a")
        assert skill.name == "skill_a"

    def test_get_skill_not_found(self):
        registry = SkillRegistry()

        with pytest.raises(SkillNotFoundError):
            registry.get_skill("nonexistent")

    def test_get_tool(self):
        registry = SkillRegistry()
        registry.register(SkillA())

        tool = registry.get_tool("tool_a1")
        assert tool.name == "tool_a1"

    def test_get_tool_not_found(self):
        registry = SkillRegistry()

        with pytest.raises(ToolNotFoundError):
            registry.get_tool("nonexistent")

    def test_get_skill_for_tool(self):
        registry = SkillRegistry()
        registry.register(SkillA())
        registry.register(SkillB())

        skill = registry.get_skill_for_tool("tool_b1")
        assert skill.name == "skill_b"

    def test_get_all_tools(self):
        registry = SkillRegistry()
        registry.register(SkillA())
        registry.register(SkillB())

        tools = registry.get_all_tools()
        tool_names = [t.name for t in tools]

        assert len(tools) == 3
        assert "tool_a1" in tool_names
        assert "tool_a2" in tool_names
        assert "tool_b1" in tool_names

    def test_get_all_skills(self):
        registry = SkillRegistry()
        registry.register(SkillA())
        registry.register(SkillB())

        skills = registry.get_all_skills()
        skill_names = [s.name for s in skills]

        assert len(skills) == 2
        assert "skill_a" in skill_names
        assert "skill_b" in skill_names

    def test_unregister_skill(self):
        registry = SkillRegistry()
        registry.register(SkillA())
        registry.register(SkillB())

        registry.unregister("skill_a")

        assert registry.skill_count == 1
        assert registry.tool_count == 1

        with pytest.raises(SkillNotFoundError):
            registry.get_skill("skill_a")

        with pytest.raises(ToolNotFoundError):
            registry.get_tool("tool_a1")

    def test_unregister_nonexistent_raises(self):
        registry = SkillRegistry()

        with pytest.raises(SkillNotFoundError):
            registry.unregister("nonexistent")

    def test_get_combined_system_prompt(self):
        registry = SkillRegistry()
        registry.register(SkillA())
        registry.register(SkillB())

        prompt = registry.get_combined_system_prompt()

        assert "Skill_A Domain" in prompt
        assert "You are skill A." in prompt
        assert "Skill_B Domain" in prompt
        assert "You are skill B." in prompt

    def test_get_tool_descriptions(self):
        registry = SkillRegistry()
        registry.register(SkillA())

        descriptions = registry.get_tool_descriptions()

        assert "Skill_A Tools" in descriptions
        assert "tool_a1" in descriptions
        assert "tool_a2" in descriptions

    def test_repr(self):
        registry = SkillRegistry()
        registry.register(SkillA())

        repr_str = repr(registry)
        assert "SkillRegistry" in repr_str
        assert "skill_a" in repr_str
