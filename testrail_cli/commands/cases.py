"""Cases command module."""

import json
import sys

import typer

from ..client import TestRailClient
from ..io import handle_api_error, output_result, parse_datetime, parse_list

app = typer.Typer(help="Manage test cases")


@app.command("list")
def list_cases(
    ctx: typer.Context,
    project_id: int | None = typer.Option(None, help="Project ID"),
    suite_id: int | None = typer.Option(None, help="Suite ID filter"),
    section_id: int | None = typer.Option(None, help="Section ID filter"),
    created_after: str | None = typer.Option(None, help="Created after (ISO8601 or epoch)"),
    created_before: str | None = typer.Option(None, help="Created before (ISO8601 or epoch)"),
    updated_after: str | None = typer.Option(None, help="Updated after (ISO8601 or epoch)"),
    updated_before: str | None = typer.Option(None, help="Updated before (ISO8601 or epoch)"),
    priority_id: str | None = typer.Option(None, help="Priority ID(s), comma-separated"),
    type_id: str | None = typer.Option(None, help="Type ID(s), comma-separated"),
    case_ids: str | None = typer.Option(None, help="Case ID(s), comma-separated"),
    limit: int | None = typer.Option(None, help="Limit results"),
    offset: int | None = typer.Option(None, help="Offset for pagination"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: str | None = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """List test cases."""
    client: TestRailClient = ctx.obj["client"]

    try:
        if case_ids:
            case_ids_list = [int(x) for x in parse_list(case_ids)]
            cases = []
            for case_id in case_ids_list:
                cases.append(client.get_case(case_id))
        else:
            if not project_id:
                typer.echo("Error: Missing option '--project-id'.", err=True)
                raise typer.Exit(code=1)

            kwargs = {}
            if suite_id:
                kwargs["suite_id"] = suite_id
            if section_id:
                kwargs["section_id"] = section_id
            if created_after:
                kwargs["created_after"] = parse_datetime(created_after)
            if created_before:
                kwargs["created_before"] = parse_datetime(created_before)
            if updated_after:
                kwargs["updated_after"] = parse_datetime(updated_after)
            if updated_before:
                kwargs["updated_before"] = parse_datetime(updated_before)
            if priority_id:
                kwargs["priority_id"] = parse_list(priority_id)  # type: ignore[assignment]
            if type_id:
                kwargs["type_id"] = parse_list(type_id)  # type: ignore[assignment]
            if limit:
                kwargs["limit"] = str(limit)  # type: ignore[assignment]
            if offset:
                kwargs["offset"] = str(offset)  # type: ignore[assignment]

            cases = client.get_cases(project_id, **kwargs)

        output_result(cases, output, fields)
    except Exception as e:
        handle_api_error(e)


@app.command("get")
def get_case(
    ctx: typer.Context,
    case_id: int = typer.Argument(..., help="Case ID"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
    fields: str | None = typer.Option(None, help="Comma-separated field list"),
) -> None:
    """Get a specific test case by ID."""
    client: TestRailClient = ctx.obj["client"]

    try:
        case = client.get_case(case_id)
        output_result(case, output, fields)
    except Exception as e:
        handle_api_error(e)


@app.command("add")
def add_case(
    ctx: typer.Context,
    section_id: int = typer.Option(..., help="Section ID"),
    title: str = typer.Option(..., help="Case title"),
    template_id: int | None = typer.Option(None, help="Template ID"),
    type_id: int | None = typer.Option(None, help="Type ID"),
    priority_id: int | None = typer.Option(None, help="Priority ID"),
    estimate: str | None = typer.Option(None, help="Estimate (e.g., '30s', '1m', '2h')"),
    refs: str | None = typer.Option(None, help="References (comma-separated)"),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Create a new test case."""
    client: TestRailClient = ctx.obj["client"]

    try:
        kwargs = {}
        if template_id:
            kwargs["template_id"] = str(template_id)
        if type_id:
            kwargs["type_id"] = str(type_id)
        if priority_id:
            kwargs["priority_id"] = str(priority_id)
        if estimate:
            kwargs["estimate"] = estimate
        if refs:
            kwargs["refs"] = str(refs)

        case = client.add_case(section_id, title, **kwargs)
        output_result(case, output, None)
    except Exception as e:
        handle_api_error(e)


@app.command("update")
def update_case(
    ctx: typer.Context,
    case_id: int = typer.Argument(..., help="Case ID"),
    title: str | None = typer.Option(None, help="Case title"),
    template_id: int | None = typer.Option(None, help="Template ID"),
    type_id: int | None = typer.Option(None, help="Type ID"),
    priority_id: int | None = typer.Option(None, help="Priority ID"),
    estimate: str | None = typer.Option(None, help="Estimate"),
    refs: str | None = typer.Option(None, help="References"),
    json_file: str | None = typer.Option(
        None, "--json", "--file", help="JSON file path or '-' for stdin"
    ),
    output: str = typer.Option("json", help="Output format (json, table, raw)"),
) -> None:
    """Update a test case."""
    client: TestRailClient = ctx.obj["client"]

    try:
        kwargs = {}

        if json_file:
            if json_file == "-":
                data = json.load(sys.stdin)
            else:
                with open(json_file, encoding="utf-8") as f:
                    data = json.load(f)
            kwargs.update(data)

        if title:
            kwargs["title"] = title
        if template_id:
            kwargs["template_id"] = str(template_id)
        if type_id:
            kwargs["type_id"] = str(type_id)
        if priority_id:
            kwargs["priority_id"] = str(priority_id)
        if estimate:
            kwargs["estimate"] = estimate
        if refs:
            kwargs["refs"] = str(refs)

        case = client.update_case(case_id, **kwargs)
        output_result(case, output, None)
    except Exception as e:
        handle_api_error(e)


@app.command("delete")
def delete_case(
    ctx: typer.Context,
    case_id: int = typer.Argument(..., help="Case ID"),
    soft: int | None = typer.Option(None, help="Soft delete (1) or hard delete (0)"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
) -> None:
    """Delete a test case."""
    client: TestRailClient = ctx.obj["client"]

    if not yes:
        delete_type = "soft delete" if soft == 1 else "hard delete" if soft == 0 else "delete"
        confirm = typer.confirm(f"Are you sure you want to {delete_type} case {case_id}?")
        if not confirm:
            raise typer.Abort()

    try:
        client.delete_case(case_id, soft=soft)
        typer.echo(f"Case {case_id} deleted successfully")
    except Exception as e:
        handle_api_error(e)


@app.command("import")
def import_cases(
    ctx: typer.Context,
    project_id: int = typer.Option(..., help="Project ID"),
    csv: str = typer.Option(..., help="Path to CSV file"),
    suite_id: int | None = typer.Option(None, help="Suite ID"),
    suite_name: str | None = typer.Option(None, help="Suite name (alternative to suite_id)"),
    section_path: str | None = typer.Option(None, help="Default section path (e.g., 'Parent/Sub')"),
    mapping: str | None = typer.Option(None, help="Path to mapping YAML/JSON file"),
    template_id: int | None = typer.Option(
        None, help="Template ID to apply to all imported cases (overrides CSV)"
    ),
    steps_field: str | None = typer.Option(
        None,
        help="Target field for steps (e.g., custom_steps_separated, custom_steps, custom_gherkin). Overrides CSV.",
    ),
    create_missing_sections: bool = typer.Option(False, help="Create sections if missing"),
    chunk_size: int = typer.Option(50, help="Batch size for API calls"),
) -> None:
    """Import test cases from CSV."""
    from ..csv_import import import_cases_from_csv

    client: TestRailClient = ctx.obj["client"]

    try:
        result = import_cases_from_csv(
            client=client,
            project_id=project_id,
            csv_path=csv,
            suite_id=suite_id,
            suite_name=suite_name,
            section_path=section_path,
            mapping_path=mapping,
            template_id=template_id,
            steps_field=steps_field,
            create_missing_sections=create_missing_sections,
            chunk_size=chunk_size,
        )

        typer.echo(f"Created: {result['created']}")
        typer.echo(f"Updated: {result['updated']}")
        typer.echo(f"Errors: {result['errors']}")

        if result.get("error_details"):
            typer.echo("\nError details:")
            for error in result["error_details"]:
                typer.echo(f"  - {error}")

    except Exception as e:
        handle_api_error(e)


@app.command("export")
def export_cases(
    ctx: typer.Context,
    project_id: int = typer.Option(..., help="Project ID"),
    csv: str = typer.Option(..., help="Path to CSV output file"),
    suite_id: int | None = typer.Option(None, help="Suite ID filter"),
    section_id: int | None = typer.Option(None, help="Section ID filter"),
    priority_id: str | None = typer.Option(None, help="Priority ID(s), comma-separated"),
    type_id: str | None = typer.Option(None, help="Type ID(s), comma-separated"),
    case_ids: str | None = typer.Option(None, help="Case ID(s) to export, comma-separated"),
) -> None:
    """Export test cases to CSV (one row per step) compatible with import."""
    from ..csv_import import export_cases_to_csv

    client: TestRailClient = ctx.obj["client"]

    try:
        priority_ids = [int(x) for x in parse_list(priority_id)] if priority_id else None
        type_ids = [int(x) for x in parse_list(type_id)] if type_id else None
        case_ids_list = [int(x) for x in parse_list(case_ids)] if case_ids else None

        result = export_cases_to_csv(
            client=client,
            project_id=project_id,
            csv_path=csv,
            suite_id=suite_id,
            case_ids=case_ids_list,
            section_id=section_id,
            priority_ids=priority_ids,
            type_ids=type_ids,
        )
        typer.echo(f"Exported rows: {result['exported']}")
        typer.echo(f"CSV written to: {csv}")
    except Exception as e:
        handle_api_error(e)
