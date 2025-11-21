"""Results command module."""

import json

import typer

from ..client import TestRailClient
from ..io import handle_api_error, output_result, parse_datetime, parse_list

app = typer.Typer(help="Manage test results")


@app.command("list")
def list_results(
    ctx: typer.Context,
    test_id: int = typer.Option(..., help="Test ID"),
    status_id: str | None = typer.Option(None, help="Status ID(s), comma-separated"),
    limit: int | None = typer.Option(None, help="Limit results"),
    offset: int | None = typer.Option(None, help="Offset for pagination"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: str | None = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """List results for a test."""
    client: TestRailClient = ctx.obj["client"]

    try:
        kwargs = {}
        if status_id:
            kwargs["status_id"] = parse_list(status_id)
        if limit:
            kwargs["limit"] = limit
        if offset:
            kwargs["offset"] = offset

        results = client.get_results(test_id, **kwargs)
        output_result(results, output, fields)
    except Exception as e:
        handle_api_error(e)


@app.command("list-for-case")
def list_results_for_case(
    ctx: typer.Context,
    run_id: int = typer.Option(..., help="Run ID"),
    case_id: int = typer.Option(..., help="Case ID"),
    status_id: str | None = typer.Option(None, help="Status ID(s), comma-separated"),
    limit: int | None = typer.Option(None, help="Limit results"),
    offset: int | None = typer.Option(None, help="Offset for pagination"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: str | None = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """List results for a test case in a run."""
    client: TestRailClient = ctx.obj["client"]

    try:
        kwargs = {}
        if status_id:
            kwargs["status_id"] = parse_list(status_id)
        if limit:
            kwargs["limit"] = limit
        if offset:
            kwargs["offset"] = offset

        results = client.get_results_for_case(run_id, case_id, **kwargs)
        output_result(results, output, fields)
    except Exception as e:
        handle_api_error(e)


@app.command("list-for-run")
def list_results_for_run(
    ctx: typer.Context,
    run_id: int = typer.Option(..., help="Run ID"),
    status_id: str | None = typer.Option(None, help="Status ID(s), comma-separated"),
    created_after: str | None = typer.Option(None, help="Created after (ISO8601 or epoch)"),
    created_before: str | None = typer.Option(None, help="Created before (ISO8601 or epoch)"),
    limit: int | None = typer.Option(None, help="Limit results"),
    offset: int | None = typer.Option(None, help="Offset for pagination"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: str | None = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """List results for a run."""
    client: TestRailClient = ctx.obj["client"]

    try:
        kwargs = {}
        if status_id:
            kwargs["status_id"] = parse_list(status_id)
        if created_after:
            kwargs["created_after"] = parse_datetime(created_after)
        if created_before:
            kwargs["created_before"] = parse_datetime(created_before)
        if limit:
            kwargs["limit"] = limit
        if offset:
            kwargs["offset"] = offset

        results = client.get_results_for_run(run_id, **kwargs)
        output_result(results, output, fields)
    except Exception as e:
        handle_api_error(e)


@app.command("add")
def add_result(
    ctx: typer.Context,
    test_id: int = typer.Option(..., help="Test ID"),
    status_id: int = typer.Option(..., help="Status ID"),
    comment: str | None = typer.Option(None, help="Result comment"),
    version: str | None = typer.Option(None, help="Version tested"),
    elapsed: str | None = typer.Option(None, help="Elapsed time (e.g., '30s', '1m')"),
    defects: str | None = typer.Option(None, help="Defects (comma-separated)"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Add a result for a test."""
    client: TestRailClient = ctx.obj["client"]

    try:
        kwargs = {"status_id": status_id}
        if comment:
            kwargs["comment"] = comment
        if version:
            kwargs["version"] = version
        if elapsed:
            kwargs["elapsed"] = elapsed
        if defects:
            kwargs["defects"] = defects

        result = client.add_result(test_id, **kwargs)
        output_result(result, output, None)
    except Exception as e:
        handle_api_error(e)


@app.command("add-for-case")
def add_result_for_case(
    ctx: typer.Context,
    run_id: int = typer.Option(..., help="Run ID"),
    case_id: int = typer.Option(..., help="Case ID"),
    status_id: int = typer.Option(..., help="Status ID"),
    comment: str | None = typer.Option(None, help="Result comment"),
    version: str | None = typer.Option(None, help="Version tested"),
    elapsed: str | None = typer.Option(None, help="Elapsed time"),
    defects: str | None = typer.Option(None, help="Defects (comma-separated)"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Add a result for a case in a run."""
    client: TestRailClient = ctx.obj["client"]

    try:
        kwargs = {"status_id": status_id}
        if comment:
            kwargs["comment"] = comment
        if version:
            kwargs["version"] = version
        if elapsed:
            kwargs["elapsed"] = elapsed
        if defects:
            kwargs["defects"] = defects

        result = client.add_result_for_case(run_id, case_id, **kwargs)
        output_result(result, output, None)
    except Exception as e:
        handle_api_error(e)


@app.command("add-bulk")
def add_results_bulk(
    ctx: typer.Context,
    run_id: int = typer.Option(..., help="Run ID"),
    results_file: str = typer.Option(..., help="Path to JSON file with results array"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Add multiple results for a run (bulk operation)."""
    client: TestRailClient = ctx.obj["client"]

    try:
        try:
            with open(results_file) as f:
                results = json.load(f)
        except FileNotFoundError:
            typer.echo(f"Error: Results file not found: {results_file}", err=True)
            raise typer.Exit(1) from None

        if not isinstance(results, list):
            raise ValueError("Results file must contain a JSON array")

        result = client.add_results(run_id, results)
        output_result(result, output, None)
    except Exception as e:
        handle_api_error(e)


@app.command("add-bulk-for-cases")
def add_results_bulk_for_cases(
    ctx: typer.Context,
    run_id: int = typer.Option(..., help="Run ID"),
    results_file: str = typer.Option(..., help="Path to JSON file with results array"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Add multiple results for cases in a run (bulk operation)."""
    client: TestRailClient = ctx.obj["client"]

    try:
        try:
            with open(results_file) as f:
                results = json.load(f)
        except FileNotFoundError:
            typer.echo(f"Error: Results file not found: {results_file}", err=True)
            raise typer.Exit(1) from None

        if not isinstance(results, list):
            raise ValueError("Results file must contain a JSON array")

        result = client.add_results_for_cases(run_id, results)
        output_result(result, output, None)
    except Exception as e:
        handle_api_error(e)
