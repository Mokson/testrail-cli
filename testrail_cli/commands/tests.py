"""Tests command module."""

import typer

from ..client import TestRailClient
from ..io import handle_api_error, output_result, parse_list

app = typer.Typer(help="Manage tests")


@app.command("list")
def list_tests(
    ctx: typer.Context,
    run_id: int = typer.Option(..., help="Run ID"),
    status_id: str | None = typer.Option(None, help="Status ID(s), comma-separated"),
    limit: int | None = typer.Option(None, help="Limit results"),
    offset: int | None = typer.Option(None, help="Offset for pagination"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: str | None = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """List tests in a run."""
    client: TestRailClient = ctx.obj["client"]

    try:
        kwargs = {}
        if status_id:
            kwargs["status_id"] = parse_list(status_id)
        if limit:
            kwargs["limit"] = limit
        if offset:
            kwargs["offset"] = offset

        tests = client.get_tests(run_id, **kwargs)
        output_result(tests, output, fields)
    except Exception as e:
        handle_api_error(e)


@app.command("get")
def get_test(
    ctx: typer.Context,
    test_id: int = typer.Argument(..., help="Test ID"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: str | None = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """Get a specific test by ID."""
    client: TestRailClient = ctx.obj["client"]

    try:
        test = client.get_test(test_id)
        output_result(test, output, fields)
    except Exception as e:
        handle_api_error(e)
