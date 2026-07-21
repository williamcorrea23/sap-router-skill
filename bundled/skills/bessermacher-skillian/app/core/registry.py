"""Skill registry for managing and routing skills."""

from dataclasses import dataclass, field

from app.core.skill import Skill
from app.core.tool import Tool


class SkillNotFoundError(Exception):
    """Raised when a skill is not found in the registry."""


class ToolNotFoundError(Exception):
    """Raised when a tool is not found in any skill."""


class DuplicateSkillError(Exception):
    """Raised when attempting to register a skill with a duplicate name."""


class DuplicateToolError(Exception):
    """Raised when multiple skills have tools with the same name."""


@dataclass
class SkillRegistry:
    """Registry for managing domain skills.

    The registry maintains a collection of skills and provides:
    - Skill registration with duplicate detection
    - Tool lookup across all skills
    - Aggregated tool lists for LLM binding

    Example:
        registry = SkillRegistry()
        registry.register(DataAnalystSkill(connector))
        registry.register(AnotherSkill(connector))

        # Get all tools for LLM
        tools = registry.get_all_tools()

        # Route tool call to correct skill
        tool = registry.get_tool("analyze_cost_center")
        result = tool.execute(cost_center_id="CC-1001")
    """

    _skills: dict[str, Skill] = field(default_factory=dict)
    _tool_index: dict[str, str] = field(default_factory=dict)  # tool_name -> skill_name

    def register(self, skill: Skill) -> None:
        """Add a skill to the registry.

        Args:
            skill: The skill to register.

        Raises:
            DuplicateSkillError: If a skill with the same name exists.
            DuplicateToolError: If a tool name conflicts with existing tools.
        """
        if skill.name in self._skills:
            raise DuplicateSkillError(f"Skill '{skill.name}' is already registered")

        # Check for tool name conflicts
        for tool in skill.tools:
            if tool.name in self._tool_index:
                existing_skill = self._tool_index[tool.name]
                raise DuplicateToolError(
                    f"Tool '{tool.name}' already exists in skill '{existing_skill}'"
                )

        # Register skill and index tools
        self._skills[skill.name] = skill
        for tool in skill.tools:
            self._tool_index[tool.name] = skill.name

    def unregister(self, skill_name: str) -> None:
        """Remove a skill from the registry.

        Args:
            skill_name: Name of the skill to remove.

        Raises:
            SkillNotFoundError: If the skill is not registered.
        """
        if skill_name not in self._skills:
            raise SkillNotFoundError(f"Skill '{skill_name}' is not registered")

        skill = self._skills[skill_name]

        # Remove tool index entries
        for tool in skill.tools:
            del self._tool_index[tool.name]

        del self._skills[skill_name]

    def get_skill(self, name: str) -> Skill:
        """Get a skill by name.

        Args:
            name: The skill name.

        Returns:
            The requested skill.

        Raises:
            SkillNotFoundError: If the skill is not found.
        """
        if name not in self._skills:
            raise SkillNotFoundError(f"Skill '{name}' is not registered")
        return self._skills[name]

    def get_tool(self, name: str) -> Tool:
        """Get a tool by name from any skill.

        Args:
            name: The tool name.

        Returns:
            The requested tool.

        Raises:
            ToolNotFoundError: If the tool is not found.
        """
        if name not in self._tool_index:
            raise ToolNotFoundError(f"Tool '{name}' not found in any skill")

        skill_name = self._tool_index[name]
        skill = self._skills[skill_name]
        tool = skill.get_tool(name)

        if tool is None:
            raise ToolNotFoundError(f"Tool '{name}' not found in skill '{skill_name}'")

        return tool

    def get_skill_for_tool(self, tool_name: str) -> Skill:
        """Get the skill that owns a tool.

        Args:
            tool_name: The tool name.

        Returns:
            The skill containing the tool.

        Raises:
            ToolNotFoundError: If the tool is not found.
        """
        if tool_name not in self._tool_index:
            raise ToolNotFoundError(f"Tool '{tool_name}' not found in any skill")

        skill_name = self._tool_index[tool_name]
        return self._skills[skill_name]

    def get_all_tools(self) -> list[Tool]:
        """Get all tools from all registered skills.

        Returns:
            List of all available tools.
        """
        tools: list[Tool] = []
        for skill in self._skills.values():
            tools.extend(skill.tools)
        return tools

    def get_all_skills(self) -> list[Skill]:
        """Get all registered skills.

        Returns:
            List of all skills.
        """
        return list(self._skills.values())

    def get_combined_system_prompt(self) -> str:
        """Combine system prompts from all skills.

        Returns:
            Combined system prompt with domain context from all skills.
        """
        prompts = []
        for skill in self._skills.values():
            prompts.append(f"## {skill.name.title()} Domain\n{skill.system_prompt}")
        return "\n\n".join(prompts)

    def get_tool_descriptions(self) -> str:
        """Get formatted descriptions of all available tools.

        Returns:
            Formatted string describing all tools.
        """
        lines = []
        for skill in self._skills.values():
            lines.append(f"\n### {skill.name.title()} Tools")
            for tool in skill.tools:
                lines.append(f"- **{tool.name}**: {tool.description}")
        return "\n".join(lines)

    @property
    def skill_count(self) -> int:
        """Number of registered skills."""
        return len(self._skills)

    @property
    def tool_count(self) -> int:
        """Total number of tools across all skills."""
        return len(self._tool_index)

    def __repr__(self) -> str:
        skill_names = list(self._skills.keys())
        return f"SkillRegistry(skills={skill_names}, tool_count={self.tool_count})"
