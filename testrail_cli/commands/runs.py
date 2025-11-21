"""Runs command module."""

import typer
from typing import Optional
from ..client import TestRailClient
from ..io import output_result, handle_api_error, parse_datetime, parse_list

app = typer.Typer(help="Manage test runs")


@app.command("list")
def list_runs(
    ctx: typer.Context,
    project_id: int = typer.Option(..., help="Project ID"),
    suite_id: Optional[int] = typer.Option(None, help="Suite ID filter"),
    milestone_id: Optional[int] = typer.Option(None, help="Milestone ID filter"),
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
    """List test runs."""
    client: TestRailClient = ctx.obj["client"]

    try:
        kwargs = {}
        if suite_id:
            kwargs["suite_id"] = suite_id
        if milestone_id:
            kwargs["milestone_id"] = milestone_id
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

        runs = client.get_runs(project_id, **kwargs)
        output_result(runs, output, fields)
    except Exception as e:
        handle_api_error(e)


@app.command("get")
def get_run(
    ctx: typer.Context,
    run_id: int = typer.Argument(..., help="Run ID"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: Optional[str] = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """Get a specific test run by ID."""
    client: TestRailClient = ctx.obj["client"]

    try:
        run = client.get_run(run_id)
        output_result(run, output, fields)
    except Exception as e:
        handle_api_error(e)


@app.command("add")
def add_run(
    ctx: typer.Context,
    project_id: int = typer.Option(..., help="Project ID"),
    suite_id: Optional[int] = typer.Option(None, help="Suite ID"),
    name: Optional[str] = typer.Option(None, help="Run name"),
    description: Optional[str] = typer.Option(None, help="Run description"),
    milestone_id: Optional[int] = typer.Option(None, help="Milestone ID"),
    assignedto_id: Optional[int] = typer.Option(None, help="Assigned to user ID"),
    include_all: Optional[bool] = typer.Option(None, help="Include all test cases"),
    case_ids: Optional[str] = typer.Option(
        None, help="Specific case IDs (comma-separated)"
    ),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Create a new test run."""
    client: TestRailClient = ctx.obj["client"]

    try:
        kwargs = {}
        if suite_id:
            kwargs["suite_id"] = suite_id
        if name:
            kwargs["name"] = name
        if description:
            kwargs["description"] = description
        if milestone_id:
            kwargs["milestone_id"] = milestone_id
        if assignedto_id:
            kwargs["assignedto_id"] = assignedto_id
        if include_all is not None:
            kwargs["include_all"] = include_all
        if case_ids:
            kwargs["case_ids"] = [int(x) for x in parse_list(case_ids)]

        run = client.add_run(project_id, **kwargs)
        output_result(run, output, None)
    except Exception as e:
        handle_api_error(e)


@app.command("update")
def update_run(
    ctx: typer.Context,
    run_id: int = typer.Argument(..., help="Run ID"),
    name: Optional[str] = typer.Option(None, help="Run name"),
    description: Optional[str] = typer.Option(None, help="Run description"),
    milestone_id: Optional[int] = typer.Option(None, help="Milestone ID"),
    include_all: Optional[bool] = typer.Option(None, help="Include all test cases"),
    case_ids: Optional[str] = typer.Option(
        None, help="Specific case IDs (comma-separated)"
    ),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Update a test run."""
    client: TestRailClient = ctx.obj["client"]

    try:
        kwargs = {}
        if name:
            kwargs["name"] = name
        if description:
            kwargs["description"] = description
        if milestone_id:
            kwargs["milestone_id"] = milestone_id
        if include_all is not None:
            kwargs["include_all"] = include_all
        if case_ids:
            kwargs["case_ids"] = [int(x) for x in parse_list(case_ids)]

        run = client.update_run(run_id, **kwargs)
        output_result(run, output, None)
    except Exception as e:
        handle_api_error(e)


@app.command("close")
def close_run(
    ctx: typer.Context,
    run_id: int = typer.Argument(..., help="Run ID"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Close a test run."""
    client: TestRailClient = ctx.obj["client"]

    try:
        run = client.close_run(run_id)
        output_result(run, output, None)
    except Exception as e:
        handle_api_error(e)


@app.command("delete")
def delete_run(
    ctx: typer.Context,
    run_id: int = typer.Argument(..., help="Run ID"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
) -> None:
    """Delete a test run."""
    client: TestRailClient = ctx.obj["client"]

    if not yes:
        confirm = typer.confirm(f"Are you sure you want to delete run {run_id}?")
        if not confirm:
            raise typer.Abort()

    try:
        client.delete_run(run_id)
        typer.echo(f"Run {run_id} deleted successfully")
    except Exception as e:
        handle_api_error(e)
