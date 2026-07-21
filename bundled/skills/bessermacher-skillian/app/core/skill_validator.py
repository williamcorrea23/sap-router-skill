"""Skill definition validation."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator

from app.core.exception import SkillValidationError


class SkillMetadataSchema(BaseModel):
    """Pydantic schema for validating SKILL.md frontmatter."""

    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=10, max_length=500)
    version: str = Field(default="1.0.0", pattern=r"^\d+\.\d+\.\d+$")
    author: str = Field(default="")
    domain: str = Field(default="")
    tags: list[str] = Field(default_factory=list)
    connector: str | None = Field(default=None)
    license: str = Field(default="")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate skill name format."""
        if " " in v:
            raise ValueError("Name cannot contain spaces, use hyphens")
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Name can only contain alphanumeric, hyphens, underscores")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate tags are lowercase."""
        return [tag.lower() for tag in v]


def validate_skill_directory(skill_path: Path) -> dict[str, Any]:
    """Validate a complete skill directory structure.

    Args:
        skill_path: Path to skill directory

    Returns:
        Validation result with 'valid', 'errors', 'warnings' keys
    """
    errors = []
    warnings = []

    # Check directory exists
    if not skill_path.exists():
        return {
            "valid": False,
            "errors": [f"Directory not found: {skill_path}"],
            "warnings": [],
        }

    if not skill_path.is_dir():
        return {
            "valid": False,
            "errors": [f"Not a directory: {skill_path}"],
            "warnings": [],
        }

    # Check for skill definition file
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        errors.append("No skill definition found (SKILL.md)")

    # Validate SKILL.md if present
    if skill_md.exists():
        md_errors, md_warnings = _validate_skill_md(skill_md)
        errors.extend(md_errors)
        warnings.extend(md_warnings)

    # Validate tools.yaml if present
    tools_yaml = skill_path / "tools.yaml"
    if tools_yaml.exists():
        yaml_errors, yaml_warnings = _validate_tools_yaml(tools_yaml)
        errors.extend(yaml_errors)
        warnings.extend(yaml_warnings)

    # Check knowledge directory
    knowledge_dir = skill_path / "knowledge"
    if knowledge_dir.exists():
        if not any(knowledge_dir.iterdir()):
            warnings.append("Knowledge directory is empty")
    else:
        warnings.append("No knowledge directory found (optional but recommended)")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def _validate_skill_md(path: Path) -> tuple[list[str], list[str]]:
    """Validate SKILL.md file.

    Returns:
        Tuple of (errors, warnings)
    """
    from app.core.skill_parser import parse_skill_md, validate_skill_md

    errors = []
    warnings = []

    try:
        config = parse_skill_md(path)

        # Validate with Pydantic schema
        try:
            SkillMetadataSchema(**config)
        except Exception as e:
            errors.append(f"Invalid metadata: {e}")

        # Get additional warnings
        warnings = validate_skill_md(path)

    except SkillValidationError as e:
        errors.append(str(e))

    return errors, warnings


def _validate_tools_yaml(path: Path) -> tuple[list[str], list[str]]:
    """Validate tools.yaml file.

    Returns:
        Tuple of (errors, warnings)
    """
    errors = []
    warnings = []

    try:
        content = yaml.safe_load(path.read_text())

        if not isinstance(content, dict):
            errors.append("tools.yaml must be a dictionary")
            return errors, warnings

        if "tools" not in content:
            errors.append("tools.yaml missing 'tools' key")
            return errors, warnings

        tools = content["tools"]
        if not isinstance(tools, list):
            errors.append("'tools' must be a list")
            return errors, warnings

        tool_names = set()
        for i, tool in enumerate(tools):
            # Check required fields
            if "name" not in tool:
                errors.append(f"Tool {i} missing 'name'")
            else:
                name = tool["name"]
                if name in tool_names:
                    errors.append(f"Duplicate tool name: {name}")
                tool_names.add(name)

            if "description" not in tool:
                warnings.append(f"Tool '{tool.get('name', i)}' missing description")

            # Check implementation or query_template
            has_impl = "implementation" in tool
            has_query = "query_template" in tool

            if not has_impl and not has_query:
                errors.append(
                    f"Tool '{tool.get('name', i)}' needs 'implementation' or 'query_template'"
                )

    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML: {e}")
    except Exception as e:
        errors.append(f"Failed to validate: {e}")

    return errors, warnings
