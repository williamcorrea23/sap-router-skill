# Guide 2: SKILL.md Parser

This guide explains how to implement a parser for the SKILL.md format, which defines skills using YAML frontmatter and Markdown content.

## Overview

The SKILL.md format combines:
- **YAML frontmatter** - Structured metadata (name, version, tags)
- **Markdown content** - Human-readable instructions and examples

Example SKILL.md:
```yaml
---
name: financial-diagnostics
description: Diagnose SAP BW financial data issues
version: "1.0.0"
domain: financial
tags: [sap, finance, gl]
connector: datasphere
---

# Financial Diagnostics Skill

## Instructions
When helping users with financial data...

## Examples
User: "Check GL account 400000"
Assistant: Uses check_gl_balance tool...
```

## Step 1: Install Dependencies

Add `python-frontmatter` for YAML parsing:

```bash
uv add python-frontmatter
```

Or add to `pyproject.toml`:
```toml
[project]
dependencies = [
    # ... existing deps ...
    "python-frontmatter>=1.0.0",
]
```

## Step 2: Create the Parser Module

Create `app/core/skill_parser.py`:

```python
"""Parser for SKILL.md skill definition files."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import frontmatter

from app.core.exceptions import SkillValidationError


@dataclass
class SkillDefinition:
    """Parsed SKILL.md content."""

    # Required fields
    name: str
    description: str

    # Optional metadata
    version: str = "1.0.0"
    author: str = ""
    domain: str = ""
    tags: list[str] = field(default_factory=list)
    connector: str | None = None
    license: str = ""

    # Parsed markdown sections
    instructions: str = ""
    capabilities: list[str] = field(default_factory=list)
    examples: list[dict[str, str]] = field(default_factory=list)
    when_to_use: list[str] = field(default_factory=list)

    # Raw content
    raw_content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for skill loader."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "domain": self.domain,
            "tags": self.tags,
            "connector": self.connector,
            "instructions": self.instructions,
            "capabilities": self.capabilities,
            "examples": self.examples,
            "when_to_use": self.when_to_use,
            "metadata": self.metadata,
        }


def parse_skill_md(path: Path | str) -> dict[str, Any]:
    """Parse a SKILL.md file and return configuration dict.

    Args:
        path: Path to SKILL.md file

    Returns:
        Dictionary with skill configuration

    Raises:
        SkillValidationError: If file is invalid or missing required fields
    """
    path = Path(path)

    if not path.exists():
        raise SkillValidationError(f"SKILL.md not found: {path}")

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        raise SkillValidationError(f"Failed to read SKILL.md: {e}") from e

    return parse_skill_md_content(content)


def parse_skill_md_content(content: str) -> dict[str, Any]:
    """Parse SKILL.md content string.

    Args:
        content: Raw SKILL.md content

    Returns:
        Dictionary with skill configuration

    Raises:
        SkillValidationError: If content is invalid
    """
    try:
        post = frontmatter.loads(content)
    except Exception as e:
        raise SkillValidationError(f"Failed to parse YAML frontmatter: {e}") from e

    # Extract frontmatter
    metadata = dict(post.metadata)

    # Validate required fields
    if "name" not in metadata:
        raise SkillValidationError("SKILL.md missing required field: name")
    if "description" not in metadata:
        raise SkillValidationError("SKILL.md missing required field: description")

    # Parse markdown sections
    markdown_content = post.content
    sections = _parse_markdown_sections(markdown_content)

    # Build instructions from relevant sections
    instructions = _build_instructions(sections)

    # Parse examples section
    examples = _parse_examples(sections.get("examples", ""))

    # Parse capabilities section
    capabilities = _parse_list_section(sections.get("capabilities", ""))

    # Parse when to use section
    when_to_use = _parse_list_section(sections.get("when to use", ""))

    return {
        "name": metadata["name"],
        "description": metadata["description"],
        "version": metadata.get("version", "1.0.0"),
        "author": metadata.get("author", ""),
        "domain": metadata.get("domain", ""),
        "tags": metadata.get("tags", []),
        "connector": metadata.get("connector"),
        "license": metadata.get("license", ""),
        "instructions": instructions,
        "capabilities": capabilities,
        "examples": examples,
        "when_to_use": when_to_use,
        "metadata": metadata,
        "raw_content": markdown_content,
    }


def _parse_markdown_sections(content: str) -> dict[str, str]:
    """Parse markdown content into sections by headers.

    Args:
        content: Markdown content

    Returns:
        Dict mapping section names (lowercase) to content
    """
    sections: dict[str, str] = {}

    # Split by ## headers
    pattern = r"^##\s+(.+)$"
    parts = re.split(pattern, content, flags=re.MULTILINE)

    # First part is content before any ## header
    if parts[0].strip():
        sections["_intro"] = parts[0].strip()

    # Subsequent parts are header/content pairs
    for i in range(1, len(parts), 2):
        if i + 1 < len(parts):
            header = parts[i].strip().lower()
            section_content = parts[i + 1].strip()
            sections[header] = section_content

    return sections


def _build_instructions(sections: dict[str, str]) -> str:
    """Build system prompt instructions from parsed sections.

    Combines relevant sections into a coherent instruction block.
    """
    parts = []

    # Add intro if present
    if "_intro" in sections:
        parts.append(sections["_intro"])

    # Add instructions section
    if "instructions" in sections:
        parts.append(sections["instructions"])

    # Add capabilities as context
    if "capabilities" in sections:
        parts.append(f"## Capabilities\n{sections['capabilities']}")

    # Add when to use as context
    if "when to use" in sections:
        parts.append(f"## When to Use\n{sections['when to use']}")

    return "\n\n".join(parts)


def _parse_examples(content: str) -> list[dict[str, str]]:
    """Parse examples section into structured format.

    Looks for patterns like:
    ### Example 1: Title
    User: "query"
    Assistant: response

    Returns:
        List of dicts with 'title', 'user', 'assistant' keys
    """
    examples = []

    # Split by ### headers
    pattern = r"^###\s+(.+)$"
    parts = re.split(pattern, content, flags=re.MULTILINE)

    for i in range(1, len(parts), 2):
        if i + 1 >= len(parts):
            continue

        title = parts[i].strip()
        example_content = parts[i + 1].strip()

        # Parse user/assistant from content
        user_match = re.search(r"User:\s*[\"']?(.+?)[\"']?\s*$", example_content, re.MULTILINE)
        assistant_match = re.search(r"Assistant:\s*(.+?)(?:\n\n|\Z)", example_content, re.DOTALL)

        example = {
            "title": title,
            "user": user_match.group(1).strip() if user_match else "",
            "assistant": assistant_match.group(1).strip() if assistant_match else "",
        }
        examples.append(example)

    return examples


def _parse_list_section(content: str) -> list[str]:
    """Parse a bullet-point list section.

    Args:
        content: Section content with bullet points

    Returns:
        List of items (without bullet markers)
    """
    items = []

    for line in content.split("\n"):
        line = line.strip()
        # Match bullet points: -, *, or numbered (1.)
        match = re.match(r"^[-*]\s+(.+)$|^(\d+\.)\s+(.+)$", line)
        if match:
            item = match.group(1) or match.group(3)
            if item:
                items.append(item.strip())

    return items


def validate_skill_md(path: Path | str) -> list[str]:
    """Validate a SKILL.md file and return any warnings.

    Args:
        path: Path to SKILL.md file

    Returns:
        List of warning messages (empty if valid)

    Raises:
        SkillValidationError: For critical validation failures
    """
    warnings = []

    config = parse_skill_md(path)

    # Check for recommended fields
    if not config.get("version"):
        warnings.append("Missing recommended field: version")

    if not config.get("domain"):
        warnings.append("Missing recommended field: domain")

    if not config.get("instructions"):
        warnings.append("Missing Instructions section in markdown")

    if not config.get("examples"):
        warnings.append("Missing Examples section - examples help LLM understand usage")

    # Check name format
    name = config["name"]
    if " " in name:
        warnings.append(f"Skill name contains spaces: '{name}' - use hyphens instead")

    if not name.replace("-", "").replace("_", "").isalnum():
        warnings.append(f"Skill name contains special characters: '{name}'")

    # Check version format
    version = config.get("version", "")
    if version and not re.match(r"^\d+\.\d+\.\d+$", version):
        warnings.append(f"Version '{version}' doesn't follow semver (x.y.z)")

    return warnings


# Convenience function for use in skill_loader
def parse_skill_config(skill_path: Path) -> dict[str, Any]:
    """Parse skill configuration from a skill directory.

    Looks for SKILL.md in the directory and parses it.

    Args:
        skill_path: Path to skill directory

    Returns:
        Skill configuration dictionary
    """
    skill_md = skill_path / "SKILL.md"
    return parse_skill_md(skill_md)
```

## Step 3: Create Validation Utilities

Add comprehensive validation in `app/core/skill_validator.py`:

```python
"""Skill definition validation."""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.core.exceptions import SkillValidationError


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
    skill_py = skill_path / "skill.py"

    if not skill_md.exists() and not skill_py.exists():
        errors.append("No skill definition found (SKILL.md or skill.py)")

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
    import yaml

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
```

## Step 4: Usage Examples

### Basic Parsing

```python
from pathlib import Path
from app.core.skill_parser import parse_skill_md

# Parse a SKILL.md file
config = parse_skill_md(Path("app/skills/financial/SKILL.md"))

print(f"Name: {config['name']}")
print(f"Description: {config['description']}")
print(f"Version: {config['version']}")
print(f"Tags: {config['tags']}")
print(f"Instructions length: {len(config['instructions'])}")
print(f"Examples: {len(config['examples'])}")
```

### Validation

```python
from pathlib import Path
from app.core.skill_validator import validate_skill_directory
from app.core.skill_parser import validate_skill_md

# Validate entire skill directory
result = validate_skill_directory(Path("app/skills/financial"))

if result["valid"]:
    print("Skill is valid!")
else:
    print("Errors:")
    for error in result["errors"]:
        print(f"  - {error}")

if result["warnings"]:
    print("Warnings:")
    for warning in result["warnings"]:
        print(f"  - {warning}")

# Quick validation of just SKILL.md
warnings = validate_skill_md(Path("app/skills/financial/SKILL.md"))
for w in warnings:
    print(f"Warning: {w}")
```

## Testing

Create `tests/test_skill_parser.py`:

```python
"""Tests for SKILL.md parser."""

import pytest
from pathlib import Path

from app.core.skill_parser import (
    parse_skill_md_content,
    parse_skill_md,
    validate_skill_md,
    _parse_markdown_sections,
    _parse_examples,
    _parse_list_section,
)
from app.core.exceptions import SkillValidationError


class TestParseSkillMdContent:
    def test_minimal_valid(self):
        content = """---
name: test-skill
description: A test skill
---

# Test Skill
"""
        config = parse_skill_md_content(content)

        assert config["name"] == "test-skill"
        assert config["description"] == "A test skill"
        assert config["version"] == "1.0.0"  # default

    def test_full_metadata(self):
        content = """---
name: financial-diagnostics
description: Diagnose financial data
version: "2.1.0"
author: skillian
domain: financial
tags: [sap, finance, gl]
connector: datasphere
---

# Financial Skill
"""
        config = parse_skill_md_content(content)

        assert config["name"] == "financial-diagnostics"
        assert config["version"] == "2.1.0"
        assert config["author"] == "skillian"
        assert config["domain"] == "financial"
        assert config["tags"] == ["sap", "finance", "gl"]
        assert config["connector"] == "datasphere"

    def test_missing_name_raises(self):
        content = """---
description: A skill without a name
---
"""
        with pytest.raises(SkillValidationError, match="missing required field: name"):
            parse_skill_md_content(content)

    def test_missing_description_raises(self):
        content = """---
name: no-description
---
"""
        with pytest.raises(SkillValidationError, match="missing required field: description"):
            parse_skill_md_content(content)

    def test_invalid_yaml_raises(self):
        content = """---
name: [invalid yaml
description: broken
---
"""
        with pytest.raises(SkillValidationError, match="Failed to parse YAML"):
            parse_skill_md_content(content)


class TestParseMarkdownSections:
    def test_parse_sections(self):
        content = """# Main Title

Introduction text.

## Instructions

Do these things.

## Examples

Some examples here.
"""
        sections = _parse_markdown_sections(content)

        assert "instructions" in sections
        assert "examples" in sections
        assert "Do these things" in sections["instructions"]

    def test_empty_content(self):
        sections = _parse_markdown_sections("")
        assert sections == {}


class TestParseExamples:
    def test_parse_example(self):
        content = """
### Example 1: Check Balance

User: "Check GL account 400000"
Assistant: Uses check_gl_balance tool with account=400000
"""
        examples = _parse_examples(content)

        assert len(examples) == 1
        assert examples[0]["title"] == "Example 1: Check Balance"
        assert "Check GL account" in examples[0]["user"]
        assert "check_gl_balance" in examples[0]["assistant"]


class TestParseListSection:
    def test_bullet_list(self):
        content = """
- First item
- Second item
- Third item
"""
        items = _parse_list_section(content)
        assert items == ["First item", "Second item", "Third item"]

    def test_numbered_list(self):
        content = """
1. Step one
2. Step two
"""
        items = _parse_list_section(content)
        assert items == ["Step one", "Step two"]


class TestValidateSkillMd:
    def test_warns_on_missing_fields(self, tmp_path):
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text("""---
name: minimal
description: A minimal skill
---
""")
        warnings = validate_skill_md(skill_md)

        assert any("version" in w for w in warnings)
        assert any("domain" in w for w in warnings)
        assert any("Instructions" in w for w in warnings)

    def test_warns_on_spaces_in_name(self, tmp_path):
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text("""---
name: bad name with spaces
description: A skill
version: "1.0.0"
---
""")
        warnings = validate_skill_md(skill_md)
        assert any("spaces" in w.lower() for w in warnings)
```

## SKILL.md Template

Create `app/skills/_templates/basic/SKILL.md`:

```yaml
---
name: skill-name
description: |
  Brief description of what this skill does.
  Include key capabilities and use cases.
version: "1.0.0"
author: your-name
domain: domain-name
tags: [tag1, tag2, tag3]
connector: datasphere  # or null if no connector needed
---

# Skill Name

Brief introduction to this skill.

## Capabilities

- Capability one
- Capability two
- Capability three

## When to Use

Activate this skill when the user asks about:

- Topic one
- Topic two
- Related questions

## Instructions

Provide detailed instructions for the LLM:

1. First, understand the user's request
2. Use appropriate tools to gather data
3. Present findings clearly
4. Suggest follow-up actions

## Examples

### Example 1: Basic Query

User: "Sample user query here"
Assistant: Describes what tools to use and expected response

### Example 2: Complex Analysis

User: "Another sample query"
Assistant: Multi-step response description
```

## Summary

You've implemented:

1. **parse_skill_md()** - Main parser function that extracts frontmatter and content
2. **Section parsing** - Extracts Instructions, Examples, Capabilities sections
3. **Validation** - Checks required fields and provides helpful warnings
4. **SkillMetadataSchema** - Pydantic model for strict validation

## Next Steps

- Implement the [YAML Tool Definitions](03_YAML_TOOL_DEFINITIONS.md) for loading tools
- Create the [Skill CLI](04_SKILL_CLI.md) for managing skills
