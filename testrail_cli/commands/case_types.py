"""Case types command module."""

import typer

from ..client import TestRailClient
from ..io import handle_api_error, output_result

app = typer.Typer(help="Manage case types")


@app.command("list")
def list_case_types(
    ctx: typer.Context,
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: str | None = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """List all available case types."""
    client: TestRailClient = ctx.obj["client"]

    try:
        case_types = client.call("get_case_types", "GET")
        output_result(case_types, output, fields)
    except Exception as e:
        handle_api_error(e)
