"""Result fields command module."""

import typer
from typing import Optional
from ..client import TestRailClient
from ..io import output_result, handle_api_error

app = typer.Typer(help="Manage result fields")


@app.command("list")
def list_result_fields(
    ctx: typer.Context,
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: Optional[str] = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """List all result fields."""
    client: TestRailClient = ctx.obj["client"]

    try:
        result_fields = client.call("get_result_fields", "GET")
        output_result(result_fields, output, fields)
    except Exception as e:
        handle_api_error(e)
