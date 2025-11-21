"""Attachments command module."""

import os

import typer

from ..client import TestRailClient
from ..io import handle_api_error, output_result

app = typer.Typer(help="Manage attachments")


@app.command("add-to-result")
def add_attachment_to_result(
    ctx: typer.Context,
    result_id: int = typer.Option(..., help="Result ID"),
    file_path: str = typer.Option(..., help="Path to file to attach"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Add an attachment to a result."""
    client: TestRailClient = ctx.obj["client"]

    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "rb") as f:
            files = {"attachment": (os.path.basename(file_path), f)}
            result = client.call(f"add_attachment_to_result/{result_id}", "POST", files=files)
        output_result(result, output, None)
    except Exception as e:
        handle_api_error(e)


@app.command("add-to-case")
def add_attachment_to_case(
    ctx: typer.Context,
    case_id: int = typer.Option(..., help="Case ID"),
    file_path: str = typer.Option(..., help="Path to file to attach"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Add an attachment to a case."""
    client: TestRailClient = ctx.obj["client"]

    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "rb") as f:
            files = {"attachment": (os.path.basename(file_path), f)}
            result = client.call(f"add_attachment_to_case/{case_id}", "POST", files=files)
        output_result(result, output, None)
    except Exception as e:
        handle_api_error(e)


@app.command("add-to-run")
def add_attachment_to_run(
    ctx: typer.Context,
    run_id: int = typer.Option(..., help="Run ID"),
    file_path: str = typer.Option(..., help="Path to file to attach"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Add an attachment to a run."""
    client: TestRailClient = ctx.obj["client"]

    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "rb") as f:
            files = {"attachment": (os.path.basename(file_path), f)}
            result = client.call(f"add_attachment_to_run/{run_id}", "POST", files=files)
        output_result(result, output, None)
    except Exception as e:
        handle_api_error(e)


@app.command("add-to-plan")
def add_attachment_to_plan(
    ctx: typer.Context,
    plan_id: int = typer.Option(..., help="Plan ID"),
    file_path: str = typer.Option(..., help="Path to file to attach"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Add an attachment to a plan."""
    client: TestRailClient = ctx.obj["client"]

    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "rb") as f:
            files = {"attachment": (os.path.basename(file_path), f)}
            result = client.call(f"add_attachment_to_plan/{plan_id}", "POST", files=files)
        output_result(result, output, None)
    except Exception as e:
        handle_api_error(e)


@app.command("list-for-case")
def list_attachments_for_case(
    ctx: typer.Context,
    case_id: int = typer.Option(..., help="Case ID"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: str | None = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """List attachments for a case."""
    client: TestRailClient = ctx.obj["client"]

    try:
        attachments = client.call(f"get_attachments_for_case/{case_id}", "GET")
        output_result(attachments, output, fields)
    except Exception as e:
        handle_api_error(e)


@app.command("list-for-run")
def list_attachments_for_run(
    ctx: typer.Context,
    run_id: int = typer.Option(..., help="Run ID"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: str | None = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """List attachments for a run."""
    client: TestRailClient = ctx.obj["client"]

    try:
        attachments = client.call(f"get_attachments_for_run/{run_id}", "GET")
        output_result(attachments, output, fields)
    except Exception as e:
        handle_api_error(e)
