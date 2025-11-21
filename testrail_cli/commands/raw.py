"""Raw API passthrough command."""

import typer
import json
from typing import Optional, List
from pathlib import Path
from ..client import TestRailClient
from ..io import output_result, handle_api_error

app = typer.Typer(help="Raw API endpoint passthrough")


@app.command()
def raw(
    ctx: typer.Context,
    endpoint: str = typer.Option(
        ..., help="API endpoint (e.g., 'get_projects', 'add_case/123')"
    ),
    method: str = typer.Option("GET", help="HTTP method (GET, POST, DELETE)"),
    params: Optional[List[str]] = typer.Option(
        None, help="Query params as key=value (repeatable)"
    ),
    data: Optional[List[str]] = typer.Option(
        None, help="Request body data as key=value (repeatable)"
    ),
    payload_file: Optional[str] = typer.Option(
        None, help="Path to JSON/YAML file for request body"
    ),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: Optional[str] = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """Make a raw API call to any TestRail endpoint.

    This command allows calling any TestRail API endpoint, including new endpoints
    not yet modeled in the CLI. Useful for testing and accessing newly released API features.

    Examples:
        testrail raw --endpoint get_projects --method GET
        testrail raw --endpoint add_case/123 --method POST --data title="Test case" --data priority_id=2
        testrail raw --endpoint get_tests/456 --method GET --params status_id=1,2
    """
    client: TestRailClient = ctx.obj["client"]

    try:
        # Parse params
        params_dict = {}
        if params:
            for param in params:
                if "=" not in param:
                    raise ValueError(f"Invalid param format: {param}. Use key=value")
                key, value = param.split("=", 1)
                params_dict[key] = value

        # Parse data
        data_dict = {}
        if payload_file:
            # Load from file
            file_path = Path(payload_file)
            if not file_path.exists():
                typer.echo(f"Error: Payload file not found: {payload_file}", err=True)
                raise typer.Exit(1)
            with open(file_path, "r") as f:
                if file_path.suffix in [".yaml", ".yml"]:
                    import yaml

                    data_dict = yaml.safe_load(f)
                else:
                    data_dict = json.load(f)
        elif data:
            # Parse from command line
            for item in data:
                if "=" not in item:
                    raise ValueError(f"Invalid data format: {item}. Use key=value")
                key, value = item.split("=", 1)
                # Try to parse as JSON value
                try:
                    data_dict[key] = json.loads(value)
                except json.JSONDecodeError:
                    # Use as string if not valid JSON
                    data_dict[key] = value

        # Make the call
        result = client.call(
            endpoint=endpoint,
            method=method.upper(),
            params=params_dict if params_dict else None,
            data=data_dict if data_dict else None,
        )

        output_result(result, output, fields)

    except Exception as e:
        handle_api_error(e)
