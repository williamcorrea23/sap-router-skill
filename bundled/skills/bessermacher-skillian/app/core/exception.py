"""Skill system exceptions."""


class SkillError(Exception):
    """Base exception for skill-related errors."""


class SkillLoadError(SkillError):
    """Failed to load a skill."""


class SkillValidationError(SkillError):
    """Skill definition is invalid."""


class ToolLoadError(SkillError):
    """Failed to load a tool."""
