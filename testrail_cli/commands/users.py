"""Users command module."""

import typer
from typing import Optional
from ..client import TestRailClient
from ..io import output_result, handle_api_error

app = typer.Typer(help="Manage users")


@app.command("list")
def list_users(
    ctx: typer.Context,
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: Optional[str] = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """List all users."""
    client: TestRailClient = ctx.obj["client"]

    try:
        users = client.get_users()
        output_result(users, output, fields)
    except Exception as e:
        handle_api_error(e)


@app.command("get")
def get_user(
    ctx: typer.Context,
    user_id: int = typer.Argument(..., help="User ID"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: Optional[str] = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """Get a specific user by ID."""
    client: TestRailClient = ctx.obj["client"]

    try:
        user = client.get_user(user_id)
        output_result(user, output, fields)
    except Exception as e:
        handle_api_error(e)


@app.command("get-by-email")
def get_user_by_email(
    ctx: typer.Context,
    email: str = typer.Argument(..., help="User email"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: Optional[str] = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """Get a user by email address."""
    client: TestRailClient = ctx.obj["client"]

    try:
        user = client.get_user_by_email(email)
        output_result(user, output, fields)
    except Exception as e:
        handle_api_error(e)
