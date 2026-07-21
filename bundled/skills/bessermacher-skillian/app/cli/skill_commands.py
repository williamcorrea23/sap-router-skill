"""CLI commands for skill management."""

import json
import shutil
import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

skill_app = typer.Typer(help="Skill management commands")
console = Console()


@skill_app.command("list")
def list_skills(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed info"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, json"),
):
    """List all available skills."""
    from app.core.skill_loader import SkillLoader

    loader = SkillLoader(Path("app/skills"))

    skills = loader.discover_skills()

    if format == "json":
        skill_data = []
        for name in skills:
            try:
                skill = loader.load_skill_metadata(name)
                tool_count = skill.metadata.get("tool_count", len(skill.tools))
                skill_data.append(
                    {
                        "name": skill.name,
                        "description": skill.description,
                        "tools": tool_count,
                        "version": getattr(skill, "version", "n/a"),
                    }
                )
            except Exception as e:
                skill_data.append({"name": name, "error": str(e)})
        console.print_json(json.dumps(skill_data, indent=2))
        return

    # Table format
    table = Table(title="Available Skills")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Tools", justify="right", style="green")

    if verbose:
        table.add_column("Version", style="blue")
        table.add_column("Domain", style="magenta")
        table.add_column("Connector", style="yellow")

    for name in skills:
        try:
            skill = loader.load_skill_metadata(name)
            tool_count = skill.metadata.get("tool_count", len(skill.tools))

            desc = skill.description
            if len(desc) > 50:
                desc = desc[:50] + "..."

            row = [
                skill.name,
                desc,
                str(tool_count),
            ]

            if verbose:
                row.append(getattr(skill, "version", "n/a"))
                row.append(getattr(skill, "domain", "n/a"))
                row.append(getattr(skill, "connector_type", None) or "-")

            table.add_row(*row)
        except Exception as e:
            table.add_row(name, f"[red]Error: {e}[/red]", "-")

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
        skill = loader.load_skill_metadata(skill_name)
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

    tool_count = skill.metadata.get("tool_count", len(skill.tools))
    info_lines.append(f"[bold]Tools:[/bold] {tool_count}")

    console.print(Panel("\n".join(info_lines), title=f"Skill: {skill_name}"))

    # Show tool error if any
    tool_error = skill.metadata.get("tool_error")
    if tool_error:
        console.print("\n[yellow]Note: Tools cannot be loaded without connector.[/yellow]")
        console.print(f"[dim]Requires '{skill.connector_type}' connector to be configured.[/dim]")

    # Tools table (from YAML if we can't load them)
    if skill.tools:
        tools_table = Table(title="Tools")
        tools_table.add_column("Name", style="cyan")
        tools_table.add_column("Description", style="white")

        for tool in skill.tools:
            desc = tool.description
            if len(desc) > 60:
                desc = desc[:60] + "..."
            tools_table.add_row(tool.name, desc)

        console.print(tools_table)
    elif tool_count > 0:
        # Show tools from YAML file directly
        tools_yaml = Path("app/skills") / skill_name / "tools.yaml"
        if tools_yaml.exists():
            import yaml

            try:
                content = yaml.safe_load(tools_yaml.read_text())
                tools_list = content.get("tools", [])

                tools_table = Table(title="Tools (from YAML)")
                tools_table.add_column("Name", style="cyan")
                tools_table.add_column("Description", style="white")

                for tool_def in tools_list:
                    name = tool_def.get("name", "unknown")
                    desc = tool_def.get("description", "")
                    if len(desc) > 60:
                        desc = desc[:60] + "..."
                    tools_table.add_row(name, desc)

                console.print(tools_table)
            except Exception:
                pass

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
        # If no templates, create a basic one inline
        console.print(f"[yellow]Template '{template}' not found, creating basic skill[/yellow]")
        new_skill_dir.mkdir(parents=True)
        _create_basic_skill(new_skill_dir, skill_name, domain)
    else:
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
    console.print(f"  1. Edit {new_skill_dir / 'SKILL.md'}")
    console.print(f"  2. Define tools in {new_skill_dir / 'tools.yaml'}")
    console.print(f"  3. Implement tools in {new_skill_dir / 'tools.py'}")
    console.print(f"  4. Add knowledge documents to {knowledge_dir}")
    console.print(f"  5. Run: skillian skill validate {skill_name}")


def _create_basic_skill(skill_dir: Path, skill_name: str, domain: str):
    """Create a basic skill from scratch."""
    # SKILL.md
    skill_md_content = f"""---
name: {skill_name}
description: |
  Description of {skill_name} skill.
  Update this with your skill's purpose.
version: "1.0.0"
author: ""
domain: {domain or skill_name}
tags: [{skill_name}]
connector: null
---

# {skill_name.replace("-", " ").title()} Skill

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
"""
    (skill_dir / "SKILL.md").write_text(skill_md_content)

    # tools.yaml
    tools_yaml_content = f"""tools:
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
    implementation: app.skills.{skill_name}.tools:example_tool
"""
    (skill_dir / "tools.yaml").write_text(tools_yaml_content)

    # tools.py
    tools_py_content = f'''"""Tool implementations for {skill_name} skill."""

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
    return {{
        "status": "success",
        "param1": param1,
        "param2": param2,
    }}
'''
    (skill_dir / "tools.py").write_text(tools_py_content)


@skill_app.command("validate")
def validate_skill(
    skill_name: str = typer.Argument(..., help="Name of the skill to validate"),
):
    """Validate a skill definition."""
    from app.core.skill_validator import validate_skill_directory

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
    tool: str | None = typer.Option(None, "--tool", "-t", help="Specific tool to test"),
):
    """Run tests for a skill."""
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
    skill_name: str | None = typer.Argument(None, help="Skill name (all if not specified)"),
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
