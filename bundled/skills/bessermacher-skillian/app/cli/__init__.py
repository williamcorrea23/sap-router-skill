"""Skillian CLI application."""

import typer

from app.cli.openapi_commands import openapi_app
from app.cli.skill_commands import skill_app

app = typer.Typer(
    name="skillian",
    help="Skillian - SAP BW AI Assistant CLI",
    no_args_is_help=True,
)

# Register sub-commands
app.add_typer(skill_app, name="skill", help="Manage skills")
app.add_typer(openapi_app, name="openapi", help="OpenAPI tool generation")


@app.command()
def version():
    """Show version information."""
    from app.config import get_settings

    settings = get_settings()
    typer.echo(f"Skillian v{settings.app_version}")


@app.command()
def info():
    """Show application information."""
    from app.config import get_settings

    settings = get_settings()

    typer.echo(f"Application: Skillian v{settings.app_version}")
    typer.echo(f"Environment: {settings.env}")
    typer.echo(f"LLM Provider: {settings.llm_provider}")


if __name__ == "__main__":
    app()
