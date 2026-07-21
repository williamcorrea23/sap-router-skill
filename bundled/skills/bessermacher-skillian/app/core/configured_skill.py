"""Skill implementation loaded from configuration files."""

from dataclasses import dataclass, field
from typing import Any

from app.core.tool import Tool


@dataclass
class ConfiguredSkill:
    """A skill loaded from SKILL.md and tools.yaml configuration.

    This class provides the same interface as Python-based skills
    but is populated from configuration files instead of code.
    """

    name: str
    description: str
    system_prompt: str
    tools: list[Tool] = field(default_factory=list)
    knowledge_paths: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Optional fields from SKILL.md
    version: str = "1.0.0"
    author: str = ""
    domain: str = ""
    tags: list[str] = field(default_factory=list)
    connector_type: str | None = None  # Required connector

    def get_tool(self, name: str) -> Tool | None:
        """Get a tool by name."""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None

    def get_tool_names(self) -> list[str]:
        """Get list of all tool names."""
        return [tool.name for tool in self.tools]

    def __repr__(self) -> str:
        return (
            f"ConfiguredSkill(name={self.name!r}, "
            f"tools={len(self.tools)}, version={self.version!r})"
        )
