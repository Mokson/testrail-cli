"""Statuses command module."""

import typer
from typing import Optional
from ..client import TestRailClient
from ..io import output_result, handle_api_error

app = typer.Typer(help="Manage test statuses")


@app.command("list")
def list_statuses(
    ctx: typer.Context,
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: Optional[str] = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """List all available test statuses."""
    client: TestRailClient = ctx.obj["client"]

    try:
        statuses = client.call("get_statuses", "GET")
        output_result(statuses, output, fields)
    except Exception as e:
        handle_api_error(e)
