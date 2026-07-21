# Guide 1: Dynamic Skill Loader

This guide walks you through implementing the dynamic skill loader that auto-discovers and loads skills from the directory structure.

## Overview

The skill loader replaces manual skill registration with automatic discovery. Instead of editing `dependencies.py` for each new skill, skills are automatically loaded from `app/skills/`.

**Before (manual):**
```python
registry.register(DataAnalystSkill(connector))
registry.register(FinancialSkill(connector))  # Must add each manually
```

**After (automatic):**
```python
loader = SkillLoader(Path("app/skills"))
for skill in loader.load_all_skills():
    registry.register(skill)
```

## Skill Format

All skills use a config-based format:

```
app/skills/
├── financial/
│   ├── SKILL.md         # Skill metadata and system prompt
│   ├── tools.yaml       # Tool definitions
│   ├── tools.py         # Tool implementations
│   └── knowledge/       # RAG documents
└── sales/
    ├── SKILL.md
    ├── tools.yaml
    ├── tools.py
    └── knowledge/
```

## Step 1: Create the Exception Classes

Create `app/core/exception.py`:

```python
"""Skill system exceptions."""


class SkillError(Exception):
    """Base exception for skill-related errors."""
    pass


class SkillLoadError(SkillError):
    """Failed to load a skill."""
    pass


class SkillValidationError(SkillError):
    """Skill definition is invalid."""
    pass


class ToolLoadError(SkillError):
    """Failed to load a tool."""
    pass
```

## Step 2: Create the ConfiguredSkill Class

This dataclass represents skills loaded from configuration files.

Create `app/core/configured_skill.py`:

```python
"""Skill implementation loaded from configuration files."""

from dataclasses import dataclass, field
from typing import Any

from app.core.tool import Tool


@dataclass
class ConfiguredSkill:
    """A skill loaded from SKILL.md and tools.yaml configuration.

    This class provides the same interface as the Skill protocol
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
    connector_type: str | None = None

    def get_tool(self, name: str) -> Tool | None:
        """Get a tool by name."""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None

    def get_tool_names(self) -> list[str]:
        """Get list of all tool names."""
        return [tool.name for tool in self.tools]

    @property
    def is_enabled(self) -> bool:
        """Check if skill is enabled."""
        return self.metadata.get("enabled", True)

    def __repr__(self) -> str:
        return (
            f"ConfiguredSkill(name={self.name!r}, "
            f"tools={len(self.tools)}, version={self.version!r})"
        )
```

## Step 3: Create the Skill Loader

Create `app/core/skill_loader.py`:

```python
"""Dynamic skill loader for config-based skills."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.core.configured_skill import ConfiguredSkill
from app.core.exception import SkillLoadError, ToolLoadError
from app.core.skill_parser import parse_skill_md
from app.core.yaml_tools import load_tools_from_yaml


class SkillLoader:
    """Load skills dynamically from directory structure.

    Skills are defined using configuration files:
        - SKILL.md: Skill metadata and system prompt
        - tools.yaml: Tool definitions
        - tools.py: Tool implementations
    """

    def __init__(
        self,
        skills_dir: Path,
        connector_factory: dict[str, Any] | None = None,
    ):
        """Initialize the skill loader.

        Args:
            skills_dir: Path to the skills directory
            connector_factory: Dict mapping connector names to instances
        """
        self.skills_dir = Path(skills_dir)
        self.connector_factory = connector_factory or {}
        self._loaded_skills: dict[str, ConfiguredSkill] = {}
        self._skill_mtimes: dict[str, float] = {}

    def discover_skills(self) -> list[str]:
        """Discover all valid skill directories.

        A valid skill directory contains a SKILL.md file.

        Returns:
            List of skill names (directory names)
        """
        if not self.skills_dir.exists():
            return []

        skills = []
        for path in self.skills_dir.iterdir():
            if not path.is_dir():
                continue
            if path.name.startswith("_"):
                continue

            if (path / "SKILL.md").exists():
                skills.append(path.name)

        return sorted(skills)

    def load_skill(self, skill_name: str) -> ConfiguredSkill:
        """Load a skill by name.

        Args:
            skill_name: Name of the skill (directory name)

        Returns:
            ConfiguredSkill instance

        Raises:
            SkillLoadError: If skill cannot be loaded
        """
        skill_path = self.skills_dir / skill_name

        if not skill_path.exists():
            raise SkillLoadError(f"Skill directory not found: {skill_path}")

        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            raise SkillLoadError(f"Missing SKILL.md in {skill_path}")

        skill = self._load_skill(skill_name, skill_path)
        self._loaded_skills[skill_name] = skill
        self._skill_mtimes[skill_name] = self._get_skill_mtime(skill_path)

        return skill

    def load_all_skills(self) -> list[ConfiguredSkill]:
        """Load all discovered skills.

        Returns:
            List of loaded ConfiguredSkill instances
        """
        skills = []
        for skill_name in self.discover_skills():
            try:
                skill = self.load_skill(skill_name)
                skills.append(skill)
            except SkillLoadError as e:
                print(f"Warning: Failed to load skill '{skill_name}': {e}")
        return skills

    def _load_skill(self, skill_name: str, skill_path: Path) -> ConfiguredSkill:
        """Load a skill from SKILL.md and tools.yaml."""
        skill_md = skill_path / "SKILL.md"

        try:
            config = parse_skill_md(skill_md)
        except Exception as e:
            raise SkillLoadError(f"Failed to parse SKILL.md: {e}") from e

        tools = []
        tools_yaml = skill_path / "tools.yaml"
        if tools_yaml.exists():
            try:
                tools = load_tools_from_yaml(
                    tools_yaml,
                    skill_name=skill_name,
                    connector=self._get_connector(config.get("connector")),
                )
            except ToolLoadError as e:
                raise SkillLoadError(f"Failed to load tools: {e}") from e

        knowledge_dir = skill_path / "knowledge"
        knowledge_paths = [str(knowledge_dir)] if knowledge_dir.exists() else []

        return ConfiguredSkill(
            name=config.get("name", skill_name),
            description=config.get("description", ""),
            system_prompt=config.get("instructions", ""),
            tools=tools,
            knowledge_paths=knowledge_paths,
            metadata=config.get("metadata", {}),
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
        mtimes = []
        for pattern in ["SKILL.md", "tools.yaml", "tools.py"]:
            path = skill_path / pattern
            if path.exists():
                mtimes.append(path.stat().st_mtime)
        return max(mtimes) if mtimes else 0

    def needs_reload(self, skill_name: str) -> bool:
        """Check if a skill has been modified and needs reloading."""
        skill_path = self.skills_dir / skill_name
        current_mtime = self._get_skill_mtime(skill_path)
        cached_mtime = self._skill_mtimes.get(skill_name, 0)
        return current_mtime > cached_mtime

    def reload_skill(self, skill_name: str) -> ConfiguredSkill:
        """Reload a skill (hot-reload)."""
        if skill_name in self._loaded_skills:
            del self._loaded_skills[skill_name]
        return self.load_skill(skill_name)

    def get_loaded_skill(self, skill_name: str) -> ConfiguredSkill | None:
        """Get a previously loaded skill from cache."""
        return self._loaded_skills.get(skill_name)

    def is_loaded(self, skill_name: str) -> bool:
        """Check if a skill is currently loaded."""
        return skill_name in self._loaded_skills
```

## Step 4: Update Dependencies

Update `app/dependencies.py` to use the skill loader:

```python
"""Dependency injection for FastAPI."""

from functools import lru_cache
from pathlib import Path

from app.config import get_settings
from app.core.skill_loader import SkillLoader
from app.core.registry import SkillRegistry


@lru_cache
def get_skill_loader() -> SkillLoader:
    """Get cached skill loader with connector factory."""
    connector_factory = {}

    connector_factory["postgres"] = get_business_connector()
    connector_factory["business"] = get_business_connector()

    datasphere = get_datasphere_connector()
    if datasphere:
        connector_factory["datasphere"] = datasphere

    return SkillLoader(
        skills_dir=Path("app/skills"),
        connector_factory=connector_factory,
    )


@lru_cache
def get_skill_registry() -> SkillRegistry:
    """Get cached skill registry with auto-discovered skills."""
    registry = SkillRegistry()
    loader = get_skill_loader()

    for skill in loader.load_all_skills():
        registry.register(skill)

    return registry
```

## Step 5: Add Hot-Reload Endpoint (Optional)

For development, add an endpoint to reload skills without restarting:

```python
# app/api/routes.py

from fastapi import APIRouter, HTTPException
from app.dependencies import get_skill_loader, get_skill_registry

router = APIRouter()


@router.post("/admin/skills/{skill_name}/reload")
async def reload_skill(skill_name: str):
    """Hot-reload a skill (development only)."""
    settings = get_settings()
    if not settings.debug:
        raise HTTPException(403, "Hot-reload only available in debug mode")

    loader = get_skill_loader()
    registry = get_skill_registry()

    if skill_name not in loader.discover_skills():
        raise HTTPException(404, f"Skill '{skill_name}' not found")

    skill = loader.reload_skill(skill_name)
    registry.update(skill)

    return {
        "status": "reloaded",
        "skill": skill_name,
        "tools": skill.get_tool_names(),
    }
```

## Step 6: Add Registry Update Methods

Update `app/core/registry.py` to support unregistration:

```python
# Add to SkillRegistry class

def unregister(self, skill_name: str) -> bool:
    """Remove a skill from the registry."""
    if skill_name not in self._skills:
        return False

    skill = self._skills[skill_name]

    for tool in skill.tools:
        if tool.name in self._tool_index:
            del self._tool_index[tool.name]

    del self._skills[skill_name]
    return True

def update(self, skill) -> None:
    """Update or add a skill in the registry."""
    self.unregister(skill.name)
    self.register(skill)
```

## Testing

Create `tests/test_skill_loader.py`:

```python
"""Tests for the skill loader."""

import pytest
from pathlib import Path

from app.core.skill_loader import SkillLoader
from app.core.exception import SkillLoadError


@pytest.fixture
def temp_skills_dir(tmp_path):
    """Create a temporary skills directory with test skills."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    # Create a test skill
    test_skill = skills_dir / "test_skill"
    test_skill.mkdir()
    (test_skill / "SKILL.md").write_text("""---
name: test-skill
description: A test skill
version: "1.0.0"
---

# Test Skill

## Instructions

This is a test skill.
""")

    return skills_dir


class TestSkillLoader:
    def test_discover_skills(self, temp_skills_dir):
        loader = SkillLoader(temp_skills_dir)
        skills = loader.discover_skills()

        assert "test_skill" in skills

    def test_discover_ignores_underscore_dirs(self, temp_skills_dir):
        (temp_skills_dir / "_templates").mkdir()
        (temp_skills_dir / "_templates" / "SKILL.md").write_text("test")

        loader = SkillLoader(temp_skills_dir)
        skills = loader.discover_skills()

        assert "_templates" not in skills

    def test_discover_ignores_dirs_without_skill_md(self, temp_skills_dir):
        (temp_skills_dir / "invalid").mkdir()

        loader = SkillLoader(temp_skills_dir)
        skills = loader.discover_skills()

        assert "invalid" not in skills

    def test_load_nonexistent_skill(self, temp_skills_dir):
        loader = SkillLoader(temp_skills_dir)

        with pytest.raises(SkillLoadError):
            loader.load_skill("nonexistent")

    def test_needs_reload(self, temp_skills_dir):
        loader = SkillLoader(temp_skills_dir)
        loader.load_skill("test_skill")

        assert not loader.needs_reload("test_skill")

        # Modify the file
        import time
        time.sleep(0.1)
        skill_md = temp_skills_dir / "test_skill" / "SKILL.md"
        skill_md.write_text(skill_md.read_text() + "\n# Updated")

        assert loader.needs_reload("test_skill")
```

## Summary

You've implemented:

1. **SkillLoader** - Core class for discovering and loading config-based skills
2. **ConfiguredSkill** - Dataclass representing loaded skills
3. **Hot-reload support** - Detect changes and reload without restart
4. **Connector injection** - Pass connectors to skills that need them

## Next Steps

- Implement the [SKILL.md Parser](02_SKILL_MD_PARSER.md) for parsing skill definitions
- Implement the [YAML Tool Loader](03_YAML_TOOL_DEFINITIONS.md) for loading tools from YAML
