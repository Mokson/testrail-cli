"""Milestones command module."""

import typer

from ..client import TestRailClient
from ..io import handle_api_error, output_result, parse_datetime

app = typer.Typer(help="Manage milestones")


@app.command("list")
def list_milestones(
    ctx: typer.Context,
    project_id: int = typer.Option(..., help="Project ID"),
    is_completed: int | None = typer.Option(
        None, help="Filter by completion (0=active, 1=completed)"
    ),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: str | None = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """List milestones in a project."""
    client: TestRailClient = ctx.obj["client"]

    try:
        kwargs = {}
        if is_completed is not None:
            kwargs["is_completed"] = is_completed

        milestones = client.get_milestones(project_id, **kwargs)
        output_result(milestones, output, fields)
    except Exception as e:
        handle_api_error(e)


@app.command("get")
def get_milestone(
    ctx: typer.Context,
    milestone_id: int = typer.Argument(..., help="Milestone ID"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: str | None = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """Get a specific milestone by ID."""
    client: TestRailClient = ctx.obj["client"]

    try:
        milestone = client.get_milestone(milestone_id)
        output_result(milestone, output, fields)
    except Exception as e:
        handle_api_error(e)


@app.command("add")
def add_milestone(
    ctx: typer.Context,
    project_id: int = typer.Option(..., help="Project ID"),
    name: str = typer.Option(..., help="Milestone name"),
    description: str | None = typer.Option(None, help="Milestone description"),
    due_on: str | None = typer.Option(None, help="Due date (ISO8601 or epoch)"),
    parent_id: int | None = typer.Option(None, help="Parent milestone ID"),
    start_on: str | None = typer.Option(None, help="Start date (ISO8601 or epoch)"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Create a new milestone."""
    client: TestRailClient = ctx.obj["client"]

    try:
        kwargs = {}
        if description:
            kwargs["description"] = description
        if due_on:
            kwargs["due_on"] = parse_datetime(due_on)
        if parent_id:
            kwargs["parent_id"] = parent_id
        if start_on:
            kwargs["start_on"] = parse_datetime(start_on)

        milestone = client.add_milestone(project_id, name, **kwargs)
        output_result(milestone, output, None)
    except Exception as e:
        handle_api_error(e)


@app.command("update")
def update_milestone(
    ctx: typer.Context,
    milestone_id: int = typer.Argument(..., help="Milestone ID"),
    name: str | None = typer.Option(None, help="Milestone name"),
    description: str | None = typer.Option(None, help="Milestone description"),
    due_on: str | None = typer.Option(None, help="Due date (ISO8601 or epoch)"),
    is_completed: bool | None = typer.Option(None, help="Mark as completed"),
    start_on: str | None = typer.Option(None, help="Start date (ISO8601 or epoch)"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Update a milestone."""
    client: TestRailClient = ctx.obj["client"]

    try:
        kwargs = {}
        if name:
            kwargs["name"] = name
        if description:
            kwargs["description"] = description
        if due_on:
            kwargs["due_on"] = parse_datetime(due_on)
        if is_completed is not None:
            kwargs["is_completed"] = is_completed
        if start_on:
            kwargs["start_on"] = parse_datetime(start_on)

        milestone = client.update_milestone(milestone_id, **kwargs)
        output_result(milestone, output, None)
    except Exception as e:
        handle_api_error(e)


@app.command("delete")
def delete_milestone(
    ctx: typer.Context,
    milestone_id: int = typer.Argument(..., help="Milestone ID"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
) -> None:
    """Delete a milestone."""
    client: TestRailClient = ctx.obj["client"]

    if not yes:
        confirm = typer.confirm(f"Are you sure you want to delete milestone {milestone_id}?")
        if not confirm:
            raise typer.Abort()

    try:
        client.delete_milestone(milestone_id)
        typer.echo(f"Milestone {milestone_id} deleted successfully")
    except Exception as e:
        handle_api_error(e)
