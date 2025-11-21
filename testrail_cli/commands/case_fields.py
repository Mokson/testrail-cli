"""Case fields command module."""

import typer
from typing import Optional
from ..client import TestRailClient
from ..io import output_result, handle_api_error

app = typer.Typer(help="Manage case fields")


@app.command("list")
def list_case_fields(
    ctx: typer.Context,
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: Optional[str] = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """List all case fields."""
    client: TestRailClient = ctx.obj["client"]

    try:
        case_fields = client.call("get_case_fields", "GET")
        output_result(case_fields, output, fields)
    except Exception as e:
        handle_api_error(e)


@app.command("add")
def add_case_field(
    ctx: typer.Context,
    type: str = typer.Option(..., help="Field type"),
    name: str = typer.Option(..., help="Field name"),
    label: str = typer.Option(..., help="Field label"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Add a custom case field."""
    client: TestRailClient = ctx.obj["client"]

    try:
        data = {"type": type, "name": name, "label": label}
        result = client.call("add_case_field", "POST", data=data)
        output_result(result, output, None)
    except Exception as e:
        handle_api_error(e)
