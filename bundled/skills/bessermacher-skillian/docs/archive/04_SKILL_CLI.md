# Guide 4: Skill CLI

This guide explains how to implement a command-line interface for managing skills without code changes.

## Overview

The Skill CLI provides commands for:
- Listing available skills
- Creating new skills from templates
- Validating skill definitions
- Enabling/disabling skills
- Hot-reloading skills during development

```bash
uv run skillian skill list
uv run skillian skill create inventory
uv run skillian skill validate financial
uv run skillian skill reload financial
```

## Step 1: Install CLI Dependencies

Add Typer for CLI building:

```bash
uv add typer[all]
```

Or in `pyproject.toml`:
```toml
[project]
dependencies = [
    # ... existing deps ...
    "typer[all]>=0.9.0",
]
```

## Step 2: Create CLI Entry Point

Update `pyproject.toml` to add CLI script:

```toml
[project.scripts]
skillian = "app.cli:app"
```

## Step 3: Create Main CLI Module

Create `app/cli/__init__.py`:

```python
"""Skillian CLI application."""

import typer

from app.cli.skill_commands import skill_app

app = typer.Typer(
    name="skillian",
    help="Skillian - SAP BW AI Assistant CLI",
    no_args_is_help=True,
)

# Register sub-commands
app.add_typer(skill_app, name="skill", help="Manage skills")


@app.command()
def version():
    """Show version information."""
    from app.config import get_settings

    settings = get_settings()
    typer.echo(f"{settings.app_name} v{settings.app_version}")


@app.command()
def info():
    """Show application information."""
    from app.config import get_settings
    from app.dependencies import get_skill_registry, get_llm_provider

    settings = get_settings()
    registry = get_skill_registry()
    provider = get_llm_provider()

    typer.echo(f"Application: {settings.app_name} v{settings.app_version}")
    typer.echo(f"Environment: {settings.env}")
    typer.echo(f"LLM Provider: {provider.provider_name} ({provider.model_name})")
    typer.echo(f"Skills loaded: {registry.skill_count}")
    typer.echo(f"Tools available: {registry.tool_count}")


if __name__ == "__main__":
    app()
```

## Step 4: Create Skill Commands

Create `app/cli/skill_commands.py`:

```python
"""CLI commands for skill management."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

skill_app = typer.Typer(help="Skill management commands")
console = Console()


@skill_app.command("list")
def list_skills(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed info"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, json"),
):
    """List all available skills."""
    from app.core.skill_loader import SkillLoader
    from app.config import get_settings

    settings = get_settings()
    loader = SkillLoader(Path("app/skills"))

    skills = loader.discover_skills()

    if format == "json":
        import json
        skill_data = []
        for name in skills:
            try:
                skill = loader.load_skill(name)
                skill_data.append({
                    "name": skill.name,
                    "description": skill.description,
                    "tools": len(skill.tools),
                    "type": "config" if hasattr(skill, "version") else "python",
                })
            except Exception as e:
                skill_data.append({"name": name, "error": str(e)})
        console.print_json(json.dumps(skill_data, indent=2))
        return

    # Table format
    table = Table(title="Available Skills")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Tools", justify="right", style="green")
    table.add_column("Type", style="yellow")

    if verbose:
        table.add_column("Version", style="blue")
        table.add_column("Domain", style="magenta")

    for name in skills:
        try:
            skill = loader.load_skill(name)
            skill_type = "config" if hasattr(skill, "version") else "python"

            row = [
                skill.name,
                skill.description[:50] + "..." if len(skill.description) > 50 else skill.description,
                str(len(skill.tools)),
                skill_type,
            ]

            if verbose:
                row.append(getattr(skill, "version", "n/a"))
                row.append(getattr(skill, "domain", "n/a"))

            table.add_row(*row)
        except Exception as e:
            table.add_row(name, f"[red]Error: {e}[/red]", "-", "-")

    console.print(table)


@skill_app.command("info")
def skill_info(
    skill_name: str = typer.Argument(..., help="Name of the skill"),
):
    """Show detailed information about a skill."""
    from app.core.skill_loader import SkillLoader

    loader = SkillLoader(Path("app/skills"))

    if skill_name not in loader.discover_skills():
        console.print(f"[red]Skill '{skill_name}' not found[/red]")
        raise typer.Exit(1)

    try:
        skill = loader.load_skill(skill_name)
    except Exception as e:
        console.print(f"[red]Failed to load skill: {e}[/red]")
        raise typer.Exit(1)

    # Build info panel
    info_lines = [
        f"[bold]Name:[/bold] {skill.name}",
        f"[bold]Description:[/bold] {skill.description}",
    ]

    if hasattr(skill, "version"):
        info_lines.append(f"[bold]Version:[/bold] {skill.version}")
    if hasattr(skill, "author") and skill.author:
        info_lines.append(f"[bold]Author:[/bold] {skill.author}")
    if hasattr(skill, "domain") and skill.domain:
        info_lines.append(f"[bold]Domain:[/bold] {skill.domain}")
    if hasattr(skill, "tags") and skill.tags:
        info_lines.append(f"[bold]Tags:[/bold] {', '.join(skill.tags)}")
    if hasattr(skill, "connector_type") and skill.connector_type:
        info_lines.append(f"[bold]Connector:[/bold] {skill.connector_type}")

    console.print(Panel("\n".join(info_lines), title=f"Skill: {skill_name}"))

    # Tools table
    if skill.tools:
        tools_table = Table(title="Tools")
        tools_table.add_column("Name", style="cyan")
        tools_table.add_column("Description", style="white")

        for tool in skill.tools:
            desc = tool.description[:60] + "..." if len(tool.description) > 60 else tool.description
            tools_table.add_row(tool.name, desc)

        console.print(tools_table)

    # Knowledge paths
    if skill.knowledge_paths:
        console.print("\n[bold]Knowledge Paths:[/bold]")
        for path in skill.knowledge_paths:
            console.print(f"  - {path}")

    # System prompt preview
    if skill.system_prompt:
        console.print("\n[bold]System Prompt (preview):[/bold]")
        preview = skill.system_prompt[:500]
        if len(skill.system_prompt) > 500:
            preview += "..."
        console.print(Panel(preview, border_style="dim"))


@skill_app.command("create")
def create_skill(
    skill_name: str = typer.Argument(..., help="Name for the new skill"),
    template: str = typer.Option("basic", "--template", "-t", help="Template to use"),
    domain: str = typer.Option("", "--domain", "-d", help="Domain name"),
):
    """Create a new skill from a template."""
    import shutil

    skills_dir = Path("app/skills")
    templates_dir = skills_dir / "_templates"
    new_skill_dir = skills_dir / skill_name

    # Check if skill already exists
    if new_skill_dir.exists():
        console.print(f"[red]Skill '{skill_name}' already exists[/red]")
        raise typer.Exit(1)

    # Check template exists
    template_dir = templates_dir / template
    if not template_dir.exists():
        console.print(f"[red]Template '{template}' not found[/red]")
        available = [d.name for d in templates_dir.iterdir() if d.is_dir()]
        console.print(f"Available templates: {', '.join(available)}")
        raise typer.Exit(1)

    # Copy template
    shutil.copytree(template_dir, new_skill_dir)

    # Customize SKILL.md
    skill_md = new_skill_dir / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text()
        content = content.replace("skill-name", skill_name)
        content = content.replace("domain-name", domain or skill_name)
        skill_md.write_text(content)

    # Create knowledge directory
    knowledge_dir = new_skill_dir / "knowledge"
    knowledge_dir.mkdir(exist_ok=True)
    (knowledge_dir / ".gitkeep").touch()

    console.print(f"[green]Created skill '{skill_name}' at {new_skill_dir}[/green]")
    console.print("\nNext steps:")
    console.print(f"  1. Edit {skill_md}")
    console.print(f"  2. Define tools in {new_skill_dir / 'tools.yaml'}")
    console.print(f"  3. Implement tools in {new_skill_dir / 'tools.py'}")
    console.print(f"  4. Add knowledge documents to {knowledge_dir}")
    console.print(f"  5. Run: skillian skill validate {skill_name}")


@skill_app.command("validate")
def validate_skill(
    skill_name: str = typer.Argument(..., help="Name of the skill to validate"),
    fix: bool = typer.Option(False, "--fix", help="Attempt to fix issues"),
):
    """Validate a skill definition."""
    from app.core.skill_validator import validate_skill_directory
    from app.core.skill_parser import validate_skill_md

    skill_dir = Path("app/skills") / skill_name

    if not skill_dir.exists():
        console.print(f"[red]Skill directory not found: {skill_dir}[/red]")
        raise typer.Exit(1)

    result = validate_skill_directory(skill_dir)

    if result["valid"]:
        console.print(f"[green]✓ Skill '{skill_name}' is valid[/green]")
    else:
        console.print(f"[red]✗ Skill '{skill_name}' has errors[/red]")

    if result["errors"]:
        console.print("\n[red]Errors:[/red]")
        for error in result["errors"]:
            console.print(f"  [red]✗[/red] {error}")

    if result["warnings"]:
        console.print("\n[yellow]Warnings:[/yellow]")
        for warning in result["warnings"]:
            console.print(f"  [yellow]![/yellow] {warning}")

    # Return exit code based on validity
    if not result["valid"]:
        raise typer.Exit(1)


@skill_app.command("reload")
def reload_skill(
    skill_name: str = typer.Argument(..., help="Name of the skill to reload"),
):
    """Hot-reload a skill (development only)."""
    from app.config import get_settings
    from app.core.skill_loader import SkillLoader
    from app.dependencies import get_skill_registry

    settings = get_settings()
    if not settings.debug:
        console.print("[red]Hot-reload is only available in debug mode[/red]")
        raise typer.Exit(1)

    loader = SkillLoader(Path("app/skills"))

    if skill_name not in loader.discover_skills():
        console.print(f"[red]Skill '{skill_name}' not found[/red]")
        raise typer.Exit(1)

    try:
        with console.status(f"Reloading {skill_name}..."):
            skill = loader.reload_skill(skill_name)

            # Update registry
            registry = get_skill_registry()
            registry.update(skill)

        console.print(f"[green]✓ Reloaded skill '{skill_name}'[/green]")
        console.print(f"  Tools: {', '.join(t.name for t in skill.tools)}")

    except Exception as e:
        console.print(f"[red]Failed to reload: {e}[/red]")
        raise typer.Exit(1)


@skill_app.command("enable")
def enable_skill(
    skill_name: str = typer.Argument(..., help="Name of the skill to enable"),
):
    """Enable a disabled skill."""
    skill_dir = Path("app/skills") / skill_name

    if not skill_dir.exists():
        console.print(f"[red]Skill '{skill_name}' not found[/red]")
        raise typer.Exit(1)

    disabled_marker = skill_dir / ".disabled"
    if disabled_marker.exists():
        disabled_marker.unlink()
        console.print(f"[green]Enabled skill '{skill_name}'[/green]")
    else:
        console.print(f"Skill '{skill_name}' is already enabled")


@skill_app.command("disable")
def disable_skill(
    skill_name: str = typer.Argument(..., help="Name of the skill to disable"),
):
    """Disable a skill (won't be loaded on startup)."""
    skill_dir = Path("app/skills") / skill_name

    if not skill_dir.exists():
        console.print(f"[red]Skill '{skill_name}' not found[/red]")
        raise typer.Exit(1)

    disabled_marker = skill_dir / ".disabled"
    disabled_marker.touch()
    console.print(f"[yellow]Disabled skill '{skill_name}'[/yellow]")


@skill_app.command("test")
def test_skill(
    skill_name: str = typer.Argument(..., help="Name of the skill to test"),
    tool: Optional[str] = typer.Option(None, "--tool", "-t", help="Specific tool to test"),
):
    """Run tests for a skill."""
    import subprocess
    import sys

    # Find test file
    test_file = Path(f"tests/test_{skill_name}.py")

    if not test_file.exists():
        # Try skills test directory
        test_file = Path(f"tests/skills/test_{skill_name}.py")

    if not test_file.exists():
        console.print(f"[yellow]No test file found for '{skill_name}'[/yellow]")
        console.print(f"Expected: tests/test_{skill_name}.py")
        raise typer.Exit(1)

    cmd = ["uv", "run", "pytest", str(test_file), "-v"]

    if tool:
        cmd.extend(["-k", tool])

    console.print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    raise typer.Exit(result.returncode)


@skill_app.command("show")
def show_skill_file(
    skill_name: str = typer.Argument(..., help="Name of the skill"),
    file: str = typer.Option("SKILL.md", "--file", "-f", help="File to show"),
):
    """Show contents of a skill file with syntax highlighting."""
    skill_dir = Path("app/skills") / skill_name
    file_path = skill_dir / file

    if not file_path.exists():
        console.print(f"[red]File not found: {file_path}[/red]")
        raise typer.Exit(1)

    content = file_path.read_text()

    # Determine syntax type
    suffix = file_path.suffix.lower()
    syntax_map = {
        ".md": "markdown",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".py": "python",
        ".json": "json",
    }
    syntax_type = syntax_map.get(suffix, "text")

    syntax = Syntax(content, syntax_type, theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=str(file_path)))


@skill_app.command("tools")
def list_tools(
    skill_name: Optional[str] = typer.Argument(None, help="Skill name (all if not specified)"),
):
    """List all tools or tools for a specific skill."""
    from app.core.skill_loader import SkillLoader

    loader = SkillLoader(Path("app/skills"))

    table = Table(title="Available Tools")
    table.add_column("Tool", style="cyan")
    table.add_column("Skill", style="yellow")
    table.add_column("Description", style="white")

    if skill_name:
        skills = [skill_name]
    else:
        skills = loader.discover_skills()

    for name in skills:
        try:
            skill = loader.load_skill(name)
            for tool in skill.tools:
                desc = tool.description.split("\n")[0][:60]
                table.add_row(tool.name, skill.name, desc)
        except Exception as e:
            if skill_name:  # Only show error if specific skill requested
                console.print(f"[red]Error loading {name}: {e}[/red]")

    console.print(table)
```

## Step 5: Add Disabled Skill Support to Loader

Update `app/core/skill_loader.py` to respect `.disabled` marker:

```python
def discover_skills(self) -> list[str]:
    """Discover all valid skill directories."""
    if not self.skills_dir.exists():
        return []

    skills = []
    for path in self.skills_dir.iterdir():
        if not path.is_dir():
            continue
        if path.name.startswith("_"):
            continue

        # Check for disabled marker
        if (path / ".disabled").exists():
            continue

        # Check for valid skill markers
        has_skill_md = (path / "SKILL.md").exists()
        has_skill_py = (path / "skill.py").exists()

        if has_skill_md or has_skill_py:
            skills.append(path.name)

    return sorted(skills)
```

## Step 6: Create Basic Template

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
tags: [tag1, tag2]
connector: datasphere
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

## Instructions

1. Understand the user's request
2. Use appropriate tools
3. Present findings clearly

## Examples

### Example 1: Basic Query

User: "Sample user query"
Assistant: Describes what tools to use
```

Create `app/skills/_templates/basic/tools.yaml`:

```yaml
tools:
  - name: example_tool
    description: |
      Example tool description.
      Explain what this tool does.
    parameters:
      - name: param1
        type: string
        required: true
        description: First parameter
      - name: param2
        type: integer
        required: false
        description: Optional second parameter
    implementation: app.skills.skill-name.tools:example_tool
```

Create `app/skills/_templates/basic/tools.py`:

```python
"""Tool implementations for skill-name skill."""

from typing import Any


async def example_tool(
    param1: str,
    param2: int | None = None,
    connector: Any | None = None,
) -> dict[str, Any]:
    """Example tool implementation.

    Args:
        param1: First parameter
        param2: Optional second parameter
        connector: Database connector

    Returns:
        Result dictionary
    """
    # TODO: Implement tool logic
    return {
        "status": "success",
        "param1": param1,
        "param2": param2,
    }
```

## Usage Examples

```bash
# List all skills
uv run skillian skill list

# List with details
uv run skillian skill list --verbose

# Show specific skill info
uv run skillian skill info financial

# Create new skill
uv run skillian skill create inventory --domain logistics

# Validate skill
uv run skillian skill validate inventory

# Show SKILL.md contents
uv run skillian skill show inventory

# Show tools.yaml
uv run skillian skill show inventory --file tools.yaml

# List all tools
uv run skillian skill tools

# List tools for specific skill
uv run skillian skill tools financial

# Disable a skill
uv run skillian skill disable old-skill

# Enable a skill
uv run skillian skill enable old-skill

# Hot-reload during development
uv run skillian skill reload financial

# Run skill tests
uv run skillian skill test financial
uv run skillian skill test financial --tool check_gl_balance
```

## Testing

Create `tests/test_cli.py`:

```python
"""Tests for CLI commands."""

import pytest
from typer.testing import CliRunner

from app.cli import app

runner = CliRunner()


class TestSkillCommands:
    def test_list_skills(self):
        result = runner.invoke(app, ["skill", "list"])
        assert result.exit_code == 0

    def test_list_skills_json(self):
        result = runner.invoke(app, ["skill", "list", "--format", "json"])
        assert result.exit_code == 0
        assert "[" in result.stdout  # JSON array

    def test_info_nonexistent(self):
        result = runner.invoke(app, ["skill", "info", "nonexistent"])
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()

    def test_validate_nonexistent(self):
        result = runner.invoke(app, ["skill", "validate", "nonexistent"])
        assert result.exit_code == 1

    def test_create_already_exists(self, tmp_path, monkeypatch):
        # Would need to mock the skills directory
        pass

    def test_version(self):
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "Skillian" in result.stdout
```

## Summary

You've implemented:

1. **Main CLI app** with Typer
2. **skill list** - List all skills with optional verbosity
3. **skill info** - Detailed skill information
4. **skill create** - Create from template
5. **skill validate** - Validate skill definition
6. **skill reload** - Hot-reload for development
7. **skill enable/disable** - Control skill loading
8. **skill test** - Run skill tests
9. **skill show** - View skill files
10. **skill tools** - List available tools

## Next Steps

- Implement the [OpenAPI Tool Generator](05_OPENAPI_TOOL_GENERATOR.md)
- Implement the [Query Templates](06_QUERY_TEMPLATES.md)
