"""Parser for SKILL.md skill definition files."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import frontmatter

from app.core.exception import SkillValidationError


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
    Examples are included at the end to serve as few-shot demonstrations.
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

    # Add examples as few-shot demonstrations
    if "examples" in sections:
        parts.append(f"## Examples\n{sections['examples']}")

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
