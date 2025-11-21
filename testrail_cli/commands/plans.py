"""Plans command module."""

import typer
from typing import Optional
from ..client import TestRailClient
from ..io import output_result, handle_api_error, parse_datetime

app = typer.Typer(help="Manage test plans")


@app.command("list")
def list_plans(
    ctx: typer.Context,
    project_id: int = typer.Option(..., help="Project ID"),
    created_after: Optional[str] = typer.Option(
        None, help="Created after (ISO8601 or epoch)"
    ),
    created_before: Optional[str] = typer.Option(
        None, help="Created before (ISO8601 or epoch)"
    ),
    is_completed: Optional[int] = typer.Option(
        None, help="Filter by completion (0=active, 1=completed)"
    ),
    limit: Optional[int] = typer.Option(None, help="Limit results"),
    offset: Optional[int] = typer.Option(None, help="Offset for pagination"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: Optional[str] = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """List test plans."""
    client: TestRailClient = ctx.obj["client"]

    try:
        kwargs = {}
        if created_after:
            kwargs["created_after"] = parse_datetime(created_after)
        if created_before:
            kwargs["created_before"] = parse_datetime(created_before)
        if is_completed is not None:
            kwargs["is_completed"] = is_completed
        if limit:
            kwargs["limit"] = limit
        if offset:
            kwargs["offset"] = offset

        plans = client.get_plans(project_id, **kwargs)
        output_result(plans, output, fields)
    except Exception as e:
        handle_api_error(e)


@app.command("get")
def get_plan(
    ctx: typer.Context,
    plan_id: int = typer.Argument(..., help="Plan ID"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: Optional[str] = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """Get a specific test plan by ID."""
    client: TestRailClient = ctx.obj["client"]

    try:
        plan = client.get_plan(plan_id)
        output_result(plan, output, fields)
    except Exception as e:
        handle_api_error(e)


@app.command("add")
def add_plan(
    ctx: typer.Context,
    project_id: int = typer.Option(..., help="Project ID"),
    name: str = typer.Option(..., help="Plan name"),
    description: Optional[str] = typer.Option(None, help="Plan description"),
    milestone_id: Optional[int] = typer.Option(None, help="Milestone ID"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Create a new test plan."""
    client: TestRailClient = ctx.obj["client"]

    try:
        kwargs = {}
        if description:
            kwargs["description"] = description
        if milestone_id:
            kwargs["milestone_id"] = milestone_id

        plan = client.add_plan(project_id, name, **kwargs)
        output_result(plan, output, None)
    except Exception as e:
        handle_api_error(e)


@app.command("update")
def update_plan(
    ctx: typer.Context,
    plan_id: int = typer.Argument(..., help="Plan ID"),
    name: Optional[str] = typer.Option(None, help="Plan name"),
    description: Optional[str] = typer.Option(None, help="Plan description"),
    milestone_id: Optional[int] = typer.Option(None, help="Milestone ID"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Update a test plan."""
    client: TestRailClient = ctx.obj["client"]

    try:
        kwargs = {}
        if name:
            kwargs["name"] = name
        if description:
            kwargs["description"] = description
        if milestone_id:
            kwargs["milestone_id"] = milestone_id

        plan = client.update_plan(plan_id, **kwargs)
        output_result(plan, output, None)
    except Exception as e:
        handle_api_error(e)


@app.command("close")
def close_plan(
    ctx: typer.Context,
    plan_id: int = typer.Argument(..., help="Plan ID"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Close a test plan."""
    client: TestRailClient = ctx.obj["client"]

    try:
        plan = client.close_plan(plan_id)
        output_result(plan, output, None)
    except Exception as e:
        handle_api_error(e)


@app.command("delete")
def delete_plan(
    ctx: typer.Context,
    plan_id: int = typer.Argument(..., help="Plan ID"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
) -> None:
    """Delete a test plan."""
    client: TestRailClient = ctx.obj["client"]

    if not yes:
        confirm = typer.confirm(f"Are you sure you want to delete plan {plan_id}?")
        if not confirm:
            raise typer.Abort()

    try:
        client.delete_plan(plan_id)
        typer.echo(f"Plan {plan_id} deleted successfully")
    except Exception as e:
        handle_api_error(e)
