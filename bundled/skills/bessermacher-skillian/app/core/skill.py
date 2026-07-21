"""Skill protocol definition."""

from typing import Protocol, runtime_checkable

from app.core.tool import Tool


@runtime_checkable
class Skill(Protocol):
    """Protocol defining the interface for domain skills.

    A skill represents a domain-specific capability composed of:
    - Tools: Callable functions the LLM can invoke
    - Knowledge: RAG documents for context (optional)
    - System Prompt: Domain-specific instructions

    Example:
        class DataAnalystSkill:
            @property
            def name(self) -> str:
                return "data_analyst"

            @property
            def description(self) -> str:
                return "Compare and analyze data from multiple sources"

            @property
            def tools(self) -> list[Tool]:
                return [self.query_source, self.compare_datasets, ...]

            @property
            def system_prompt(self) -> str:
                return "You are a data analyst..."

            @property
            def knowledge_paths(self) -> list[str]:
                return ["app/skills/data_analyst/knowledge/"]
    """

    @property
    def name(self) -> str:
        """Unique identifier for the skill (e.g., 'financial', 'sales')."""
        ...

    @property
    def description(self) -> str:
        """Human-readable description of what the skill does."""
        ...

    @property
    def tools(self) -> list[Tool]:
        """List of tools available in this skill."""
        ...

    @property
    def system_prompt(self) -> str:
        """System prompt providing domain context to the LLM."""
        ...

    @property
    def knowledge_paths(self) -> list[str]:
        """Paths to knowledge documents for RAG (can be empty)."""
        ...

    def get_tool(self, name: str) -> Tool | None:
        """Get a specific tool by name.

        Args:
            name: The tool name to look up.

        Returns:
            The tool if found, None otherwise.
        """
        ...
