"""Projects command module."""

import typer
from typing import Optional
from ..client import TestRailClient
from ..io import output_result, handle_api_error

app = typer.Typer(help="Manage TestRail projects")


@app.command("list")
def list_projects(
    ctx: typer.Context,
    is_completed: Optional[int] = typer.Option(
        None, help="Filter by completion status (0=active, 1=completed)"
    ),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: Optional[str] = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """List all projects."""
    client: TestRailClient = ctx.obj["client"]

    try:
        projects = client.get_projects(is_completed=is_completed)
        output_result(projects, output, fields)
    except Exception as e:
        handle_api_error(e)


@app.command("get")
def get_project(
    ctx: typer.Context,
    project_id: int = typer.Argument(..., help="Project ID"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: Optional[str] = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """Get a specific project by ID."""
    client: TestRailClient = ctx.obj["client"]

    try:
        project = client.get_project(project_id)
        output_result(project, output, fields)
    except Exception as e:
        handle_api_error(e)


@app.command("add")
def add_project(
    ctx: typer.Context,
    name: str = typer.Option(..., help="Project name"),
    announcement: Optional[str] = typer.Option(None, help="Project announcement"),
    show_announcement: Optional[bool] = typer.Option(None, help="Show announcement"),
    suite_mode: Optional[int] = typer.Option(
        None, help="Suite mode (1=single, 2=single+baselines, 3=multiple)"
    ),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Create a new project."""
    client: TestRailClient = ctx.obj["client"]

    try:
        kwargs = {}
        if announcement:
            kwargs["announcement"] = announcement
        if show_announcement is not None:
            kwargs["show_announcement"] = show_announcement
        if suite_mode:
            kwargs["suite_mode"] = suite_mode

        project = client.add_project(name, **kwargs)
        output_result(project, output, None)
    except Exception as e:
        handle_api_error(e)


@app.command("update")
def update_project(
    ctx: typer.Context,
    project_id: int = typer.Argument(..., help="Project ID"),
    name: Optional[str] = typer.Option(None, help="Project name"),
    announcement: Optional[str] = typer.Option(None, help="Project announcement"),
    show_announcement: Optional[bool] = typer.Option(None, help="Show announcement"),
    is_completed: Optional[bool] = typer.Option(None, help="Mark as completed"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Update a project."""
    client: TestRailClient = ctx.obj["client"]

    try:
        kwargs = {}
        if name:
            kwargs["name"] = name
        if announcement:
            kwargs["announcement"] = announcement
        if show_announcement is not None:
            kwargs["show_announcement"] = show_announcement
        if is_completed is not None:
            kwargs["is_completed"] = is_completed

        project = client.update_project(project_id, **kwargs)
        output_result(project, output, None)
    except Exception as e:
        handle_api_error(e)


@app.command("delete")
def delete_project(
    ctx: typer.Context,
    project_id: int = typer.Argument(..., help="Project ID"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
) -> None:
    """Delete a project."""
    client: TestRailClient = ctx.obj["client"]

    if not yes:
        confirm = typer.confirm(
            f"Are you sure you want to delete project {project_id}?"
        )
        if not confirm:
            raise typer.Abort()

    try:
        client.delete_project(project_id)
        typer.echo(f"Project {project_id} deleted successfully")
    except Exception as e:
        handle_api_error(e)
