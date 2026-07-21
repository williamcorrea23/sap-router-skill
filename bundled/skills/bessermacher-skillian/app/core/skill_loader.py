"""Dynamic skill loader for config-based skills."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.core.configured_skill import ConfiguredSkill
from app.core.exception import SkillLoadError, ToolLoadError
from app.core.skill_parser import parse_skill_md
from app.core.tool import Tool
from app.core.yaml_tools import load_tools_from_yaml

logger = logging.getLogger(__name__)


class SkillLoader:
    """Load skills dynamically from directory structure.

    Skills are defined using configuration files:
        - SKILL.md: Skill metadata and system prompt
        - tools.yaml: Tool definitions
        - tools.py: Tool implementations

    Directory structure:
        app/skills/
        ├── financial/
        │   ├── SKILL.md
        │   ├── tools.yaml
        │   ├── tools.py
        │   └── knowledge/
        └── sales/
            ├── SKILL.md
            ├── tools.yaml
            ├── tools.py
            └── knowledge/
    """

    def __init__(
        self,
        skills_dir: Path,
        connector_factory: dict[str, Any] | None = None,
    ):
        self.skills_dir = Path(skills_dir)
        self.connector_factory = connector_factory or {}
        self._loaded_skills: dict[str, ConfiguredSkill] = {}
        self._skill_mtimes: dict[str, float] = {}

    def discover_skills(self) -> list[str]:
        """Discover all valid skill directories (those containing SKILL.md)."""
        if not self.skills_dir.exists():
            return []
        return sorted(
            p.name
            for p in self.skills_dir.iterdir()
            if p.is_dir() and not p.name.startswith("_") and (p / "SKILL.md").exists()
        )

    def load_skill(self, skill_name: str) -> ConfiguredSkill:
        """Load a skill by name.

        Raises:
            SkillLoadError: If skill cannot be loaded.
        """
        skill_path = self._validate_skill_path(skill_name)
        config, tools, knowledge_paths, _ = self._parse_and_load_tools(skill_name, skill_path)

        skill = self._build_skill(config, skill_name, tools, knowledge_paths)
        self._loaded_skills[skill_name] = skill
        self._skill_mtimes[skill_name] = self._get_skill_mtime(skill_path)
        return skill

    def load_all_skills(self) -> list[ConfiguredSkill]:
        """Load all discovered skills."""
        skills = []
        for skill_name in self.discover_skills():
            try:
                skills.append(self.load_skill(skill_name))
            except SkillLoadError as e:
                logger.warning("Failed to load skill '%s': %s", skill_name, e)
        return skills

    def load_skill_metadata(
        self, skill_name: str, *, include_tools: bool = False
    ) -> ConfiguredSkill:
        """Load skill metadata without requiring tools/connector.

        Useful for CLI operations that need to display skill info
        without actually loading functional tools.
        """
        skill_path = self._validate_skill_path(skill_name)
        config, tools, knowledge_paths, tool_error = self._parse_and_load_tools(
            skill_name, skill_path, graceful_tool_errors=not include_tools
        )

        # Count tools from YAML even if we couldn't load them
        tool_count = len(tools)
        if not tools:
            tools_yaml = skill_path / "tools.yaml"
            if tools_yaml.exists():
                try:
                    import yaml

                    content = yaml.safe_load(tools_yaml.read_text())
                    tool_count = len(content.get("tools", []))
                except Exception:
                    pass

        return self._build_skill(
            config,
            skill_name,
            tools,
            knowledge_paths,
            metadata_extra={
                "tool_count": tool_count if not tools else len(tools),
                "tool_error": tool_error,
            },
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_skill_path(self, skill_name: str) -> Path:
        """Validate and return the skill directory path."""
        skill_path = self.skills_dir / skill_name
        if not skill_path.exists():
            raise SkillLoadError(f"Skill directory not found: {skill_path}")
        if not (skill_path / "SKILL.md").exists():
            raise SkillLoadError(f"Missing SKILL.md in {skill_path}")
        return skill_path

    def _parse_and_load_tools(
        self,
        skill_name: str,
        skill_path: Path,
        *,
        graceful_tool_errors: bool = False,
    ) -> tuple[dict, list[Tool], list[str], str | None]:
        """Parse SKILL.md, load tools, resolve knowledge paths.

        Returns:
            (config, tools, knowledge_paths, tool_error_or_none)
        """
        try:
            config = parse_skill_md(skill_path / "SKILL.md")
        except Exception as e:
            raise SkillLoadError(f"Failed to parse SKILL.md: {e}") from e

        tools: list[Tool] = []
        tool_error: str | None = None
        tools_yaml = skill_path / "tools.yaml"

        if tools_yaml.exists():
            try:
                tools = load_tools_from_yaml(
                    tools_yaml,
                    skill_name=skill_name,
                    connector=self._get_connector(config.get("connector")),
                )
            except ToolLoadError as e:
                if graceful_tool_errors:
                    tool_error = str(e)
                else:
                    raise SkillLoadError(f"Failed to load tools: {e}") from e

        knowledge_dir = skill_path / "knowledge"
        knowledge_paths = [str(knowledge_dir)] if knowledge_dir.exists() else []

        return config, tools, knowledge_paths, tool_error

    @staticmethod
    def _build_skill(
        config: dict,
        skill_name: str,
        tools: list[Tool],
        knowledge_paths: list[str],
        metadata_extra: dict[str, Any] | None = None,
    ) -> ConfiguredSkill:
        """Build a ConfiguredSkill from parsed config."""
        metadata = config.get("metadata", {})
        if metadata_extra:
            metadata = {**metadata, **metadata_extra}

        return ConfiguredSkill(
            name=config.get("name", skill_name),
            description=config.get("description", ""),
            system_prompt=config.get("instructions", ""),
            tools=tools,
            knowledge_paths=knowledge_paths,
            metadata=metadata,
            version=config.get("version", "1.0.0"),
            author=config.get("author", ""),
            domain=config.get("domain", ""),
            tags=config.get("tags", []),
            connector_type=config.get("connector"),
        )

    def _get_connector(self, connector_type: str | None) -> Any | None:
        """Get a connector instance by type."""
        if not connector_type:
            return None
        return self.connector_factory.get(connector_type)

    def _get_skill_mtime(self, skill_path: Path) -> float:
        """Get the latest modification time for skill files."""
        mtimes = [
            (skill_path / f).stat().st_mtime
            for f in ("SKILL.md", "tools.yaml", "tools.py")
            if (skill_path / f).exists()
        ]
        return max(mtimes) if mtimes else 0

    def needs_reload(self, skill_name: str) -> bool:
        """Check if a skill has been modified and needs reloading."""
        skill_path = self.skills_dir / skill_name
        return self._get_skill_mtime(skill_path) > self._skill_mtimes.get(skill_name, 0)

    def reload_skill(self, skill_name: str) -> ConfiguredSkill:
        """Reload a skill (hot-reload)."""
        self._loaded_skills.pop(skill_name, None)
        return self.load_skill(skill_name)

    def get_loaded_skill(self, skill_name: str) -> ConfiguredSkill | None:
        """Get a previously loaded skill from cache."""
        return self._loaded_skills.get(skill_name)

    def is_loaded(self, skill_name: str) -> bool:
        """Check if a skill is currently loaded."""
        return skill_name in self._loaded_skills
