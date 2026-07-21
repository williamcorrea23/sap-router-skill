"""OpenAPI CLI commands."""

from pathlib import Path

import typer
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

openapi_app = typer.Typer(help="OpenAPI tool generation commands")
console = Console()


@openapi_app.command("preview")
def preview_spec(
    spec_path: Path = typer.Argument(..., help="Path to OpenAPI spec file"),
    tags: str | None = typer.Option(None, "--tags", "-t", help="Filter by tags (comma-separated)"),
    methods: str | None = typer.Option(
        None, "--methods", "-m", help="Filter by methods (comma-separated)"
    ),
):
    """Preview tools that would be generated from an OpenAPI spec."""
    from app.core.openapi_loader import OpenAPISpec, OpenAPIToolGenerator

    if not spec_path.exists():
        console.print(f"[red]File not found: {spec_path}[/red]")
        raise typer.Exit(1)

    spec = OpenAPISpec.from_file(spec_path)

    console.print(f"[bold]API: {spec.title}[/bold] v{spec.version}")
    desc = spec.description[:100] + "..." if len(spec.description) > 100 else spec.description
    console.print(f"Description: {desc}")
    console.print(f"Endpoints: {len(spec.endpoints)}")
    console.print()

    # Filter options
    filter_tags = tags.split(",") if tags else None
    filter_methods = [m.upper() for m in methods.split(",")] if methods else None

    generator = OpenAPIToolGenerator(spec)
    tools = generator.generate_tools(
        filter_tags=filter_tags,
        filter_methods=filter_methods,
    )

    table = Table(title=f"Generated Tools ({len(tools)})")
    table.add_column("Tool Name", style="cyan")
    table.add_column("Method", style="yellow")
    table.add_column("Path", style="white")
    table.add_column("Parameters", style="green")

    for endpoint in spec.endpoints:
        if filter_tags and not any(t in endpoint.tags for t in filter_tags):
            continue
        if filter_methods and endpoint.method not in filter_methods:
            continue

        param_count = len(endpoint.parameters)
        if endpoint.request_body:
            param_count += 1

        path_display = endpoint.path[:40] + "..." if len(endpoint.path) > 40 else endpoint.path

        table.add_row(
            generator._sanitize_name(endpoint.operation_id),
            endpoint.method,
            path_display,
            str(param_count),
        )

    console.print(table)


@openapi_app.command("generate")
def generate_tools(
    spec_path: Path = typer.Argument(..., help="Path to OpenAPI spec file"),
    skill: str = typer.Option(..., "--skill", "-s", help="Skill to add tools to"),
    tags: str | None = typer.Option(None, "--tags", "-t", help="Filter by tags"),
    methods: str | None = typer.Option(None, "--methods", "-m", help="Filter by methods"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing"),
):
    """Generate tools.yaml from an OpenAPI spec."""
    from app.core.openapi_loader import OpenAPISpec, OpenAPIToolGenerator

    if not spec_path.exists():
        console.print(f"[red]File not found: {spec_path}[/red]")
        raise typer.Exit(1)

    skill_dir = Path("app/skills") / skill
    if not skill_dir.exists():
        console.print(f"[red]Skill '{skill}' not found[/red]")
        raise typer.Exit(1)

    spec = OpenAPISpec.from_file(spec_path)
    generator = OpenAPIToolGenerator(spec)

    filter_tags = tags.split(",") if tags else None
    filter_methods = [m.upper() for m in methods.split(",")] if methods else None

    yaml_content = generator.generate_yaml(
        filter_tags=filter_tags,
        filter_methods=filter_methods,
    )

    if dry_run:
        console.print("[bold]Generated tools.yaml:[/bold]")
        syntax = Syntax(yaml_content, "yaml", theme="monokai", line_numbers=True)
        console.print(syntax)
        return

    # Write to skill directory
    tools_yaml = skill_dir / "tools.yaml"

    if tools_yaml.exists():
        if not typer.confirm(f"Overwrite existing {tools_yaml}?"):
            raise typer.Exit(0)

    tools_yaml.write_text(yaml_content)
    console.print(f"[green]Generated {tools_yaml}[/green]")

    # Create stub tools.py
    tools_py = skill_dir / "tools.py"
    if not tools_py.exists():
        stub = '''"""Auto-generated tool stubs from OpenAPI spec."""

# TODO: Implement tool functions if custom logic is needed
# The OpenAPI generator will call endpoints directly if no implementation is specified
'''
        tools_py.write_text(stub)
        console.print(f"[green]Created {tools_py}[/green]")


@openapi_app.command("info")
def spec_info(
    spec_path: Path = typer.Argument(..., help="Path to OpenAPI spec file"),
):
    """Show information about an OpenAPI spec."""
    from app.core.openapi_loader import OpenAPISpec

    if not spec_path.exists():
        console.print(f"[red]File not found: {spec_path}[/red]")
        raise typer.Exit(1)

    spec = OpenAPISpec.from_file(spec_path)

    console.print(f"[bold]Title:[/bold] {spec.title}")
    console.print(f"[bold]Version:[/bold] {spec.version}")
    console.print(f"[bold]Description:[/bold] {spec.description}")

    if spec.servers:
        console.print("\n[bold]Servers:[/bold]")
        for server in spec.servers:
            console.print(f"  - {server.get('url')}")

    # Collect tags
    all_tags = set()
    method_counts: dict[str, int] = {}
    for endpoint in spec.endpoints:
        all_tags.update(endpoint.tags)
        method_counts[endpoint.method] = method_counts.get(endpoint.method, 0) + 1

    console.print(f"\n[bold]Endpoints:[/bold] {len(spec.endpoints)}")
    for method, count in sorted(method_counts.items()):
        console.print(f"  {method}: {count}")

    if all_tags:
        console.print(f"\n[bold]Tags:[/bold] {', '.join(sorted(all_tags))}")

    console.print(f"\n[bold]Schemas:[/bold] {len(spec.schemas)}")
