"""Sections command module."""

import typer
from typing import Optional
from ..client import TestRailClient
from ..io import output_result, handle_api_error

app = typer.Typer(help="Manage test sections")


@app.command("list")
def list_sections(
    ctx: typer.Context,
    project_id: int = typer.Option(..., help="Project ID"),
    suite_id: Optional[int] = typer.Option(None, help="Suite ID filter"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: Optional[str] = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """List all sections in a project."""
    client: TestRailClient = ctx.obj["client"]

    try:
        sections = client.get_sections(project_id, suite_id=suite_id)
        output_result(sections, output, fields)
    except Exception as e:
        handle_api_error(e)


@app.command("get")
def get_section(
    ctx: typer.Context,
    section_id: int = typer.Argument(..., help="Section ID"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: Optional[str] = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """Get a specific section by ID."""
    client: TestRailClient = ctx.obj["client"]

    try:
        section = client.get_section(section_id)
        output_result(section, output, fields)
    except Exception as e:
        handle_api_error(e)


@app.command("add")
def add_section(
    ctx: typer.Context,
    project_id: int = typer.Option(..., help="Project ID"),
    name: str = typer.Option(..., help="Section name"),
    suite_id: Optional[int] = typer.Option(None, help="Suite ID"),
    parent_id: Optional[int] = typer.Option(None, help="Parent section ID"),
    description: Optional[str] = typer.Option(None, help="Section description"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Create a new section."""
    client: TestRailClient = ctx.obj["client"]

    try:
        kwargs = {}
        if suite_id:
            kwargs["suite_id"] = suite_id
        if parent_id:
            kwargs["parent_id"] = parent_id
        if description:
            kwargs["description"] = description

        section = client.add_section(project_id, name, **kwargs)
        output_result(section, output, None)
    except Exception as e:
        handle_api_error(e)


@app.command("update")
def update_section(
    ctx: typer.Context,
    section_id: int = typer.Argument(..., help="Section ID"),
    name: Optional[str] = typer.Option(None, help="Section name"),
    description: Optional[str] = typer.Option(None, help="Section description"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Update a section."""
    client: TestRailClient = ctx.obj["client"]

    try:
        kwargs = {}
        if name:
            kwargs["name"] = name
        if description:
            kwargs["description"] = description

        section = client.update_section(section_id, **kwargs)
        output_result(section, output, None)
    except Exception as e:
        handle_api_error(e)


@app.command("delete")
def delete_section(
    ctx: typer.Context,
    section_id: int = typer.Argument(..., help="Section ID"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
) -> None:
    """Delete a section."""
    client: TestRailClient = ctx.obj["client"]

    if not yes:
        confirm = typer.confirm(
            f"Are you sure you want to delete section {section_id}?"
        )
        if not confirm:
            raise typer.Abort()

    try:
        client.delete_section(section_id)
        typer.echo(f"Section {section_id} deleted successfully")
    except Exception as e:
        handle_api_error(e)
