"""Statuses command module."""

import typer

from ..client import TestRailClient
from ..io import handle_api_error, output_result

app = typer.Typer(help="Manage test statuses")


@app.command("list")
def list_statuses(
    ctx: typer.Context,
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: str | None = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """List all available test statuses."""
    client: TestRailClient = ctx.obj["client"]

    try:
        statuses = client.call("get_statuses", "GET")
        output_result(statuses, output, fields)
    except Exception as e:
        handle_api_error(e)
