"""Priorities command module."""

import typer

from ..client import TestRailClient
from ..io import handle_api_error, output_result

app = typer.Typer(help="Manage case priorities")


@app.command("list")
def list_priorities(
    ctx: typer.Context,
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: str | None = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """List all available case priorities."""
    client: TestRailClient = ctx.obj["client"]

    try:
        priorities = client.call("get_priorities", "GET")
        output_result(priorities, output, fields)
    except Exception as e:
        handle_api_error(e)
