"""Suites command module."""

import typer

from ..client import TestRailClient
from ..io import handle_api_error, output_result

app = typer.Typer(help="Manage test suites")


@app.command("list")
def list_suites(
    ctx: typer.Context,
    project_id: int = typer.Option(..., help="Project ID"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: str | None = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """List all suites in a project."""
    client: TestRailClient = ctx.obj["client"]

    try:
        suites = client.get_suites(project_id)
        output_result(suites, output, fields)
    except Exception as e:
        handle_api_error(e)


@app.command("get")
def get_suite(
    ctx: typer.Context,
    suite_id: int = typer.Argument(..., help="Suite ID"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: str | None = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """Get a specific suite by ID."""
    client: TestRailClient = ctx.obj["client"]

    try:
        suite = client.get_suite(suite_id)
        output_result(suite, output, fields)
    except Exception as e:
        handle_api_error(e)


@app.command("add")
def add_suite(
    ctx: typer.Context,
    project_id: int = typer.Option(..., help="Project ID"),
    name: str = typer.Option(..., help="Suite name"),
    description: str | None = typer.Option(None, help="Suite description"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Create a new suite."""
    client: TestRailClient = ctx.obj["client"]

    try:
        kwargs = {}
        if description:
            kwargs["description"] = description

        suite = client.add_suite(project_id, name, **kwargs)
        output_result(suite, output, None)
    except Exception as e:
        handle_api_error(e)


@app.command("update")
def update_suite(
    ctx: typer.Context,
    suite_id: int = typer.Argument(..., help="Suite ID"),
    name: str | None = typer.Option(None, help="Suite name"),
    description: str | None = typer.Option(None, help="Suite description"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Update a suite."""
    client: TestRailClient = ctx.obj["client"]

    try:
        kwargs = {}
        if name:
            kwargs["name"] = name
        if description:
            kwargs["description"] = description

        suite = client.update_suite(suite_id, **kwargs)
        output_result(suite, output, None)
    except Exception as e:
        handle_api_error(e)


@app.command("delete")
def delete_suite(
    ctx: typer.Context,
    suite_id: int = typer.Argument(..., help="Suite ID"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
) -> None:
    """Delete a suite."""
    client: TestRailClient = ctx.obj["client"]

    if not yes:
        confirm = typer.confirm(f"Are you sure you want to delete suite {suite_id}?")
        if not confirm:
            raise typer.Abort()

    try:
        client.delete_suite(suite_id)
        typer.echo(f"Suite {suite_id} deleted successfully")
    except Exception as e:
        handle_api_error(e)
