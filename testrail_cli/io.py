"""I/O utilities for output formatting, pagination, and data parsing."""

import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from rich.console import Console
from rich.table import Table
from rich import box


console = Console()


def output_json(data: Any, fields: Optional[List[str]] = None) -> None:
    """Output data as JSON.

    Args:
        data: Data to output (dict, list, or primitive)
        fields: Optional field filter (for dicts/lists of dicts)
    """
    if fields and isinstance(data, (list, dict)):
        data = filter_fields(data, fields)

    console.print_json(json.dumps(data, indent=2, default=str))


def output_table(
    data: List[Dict[str, Any]], fields: Optional[List[str]] = None
) -> None:
    """Output data as a formatted table.

    Args:
        data: List of dicts to display
        fields: Optional field filter
    """
    if not data:
        console.print("[dim]No results[/dim]")
        return

    # Filter fields if specified
    if fields:
        data = [filter_fields(row, fields) for row in data]
    else:
        # Default: use all keys from first row
        fields = list(data[0].keys())

    # Create table
    table = Table(box=box.SIMPLE, show_header=True)

    for field in fields:
        table.add_column(field, overflow="fold")

    for row in data:
        table.add_row(*[str(row.get(field, "")) for field in fields])

    console.print(table)


def output_raw(data: Any) -> None:
    """Output data as raw string (no formatting)."""
    print(data)


def extract_paginated_data(data: Any) -> Any:
    """Extract data from paginated API responses.

    TestRail API returns paginated responses in this format:
    {
        "offset": 0,
        "limit": 250,
        "size": 6,
        "_links": {...},
        "<resource_name>": [...]
    }

    This function extracts the array from such responses.

    Args:
        data: API response data

    Returns:
        Extracted array or original data if not paginated
    """
    if not isinstance(data, dict):
        return data

    # Check if response has pagination metadata
    has_pagination_metadata = all(k in data for k in ['offset', 'limit', 'size'])

    if has_pagination_metadata:
        # Find the array key (should be the one that's not metadata)
        metadata_keys = {'offset', 'limit', 'size', '_links'}
        for key, value in data.items():
            if key not in metadata_keys and isinstance(value, list):
                return value

    # Fallback: check known paginated response keys
    paginated_keys = [
        'projects', 'cases', 'runs', 'plans', 'tests', 'results',
        'milestones', 'sections', 'suites', 'users', 'statuses',
        'priorities', 'case_types', 'case_fields', 'result_fields',
        'attachments'
    ]

    for key in paginated_keys:
        if key in data:
            return data[key]

    return data


def output_result(
    data: Any, format: str = "json", fields: Optional[str] = None
) -> None:
    """Output result in specified format.

    Args:
        data: Data to output
        format: Output format (json, table, raw)
        fields: Comma-separated field list
    """
    field_list = fields.split(",") if fields else None

    # Extract paginated data if needed (for table/fields filtering)
    if format == "table" or field_list:
        data = extract_paginated_data(data)

    if format == "json":
        output_json(data, field_list)
    elif format == "table":
        if isinstance(data, list):
            output_table(data, field_list)
        else:
            output_table([data], field_list)
    elif format == "raw":
        output_raw(data)
    else:
        raise ValueError(f"Unknown output format: {format}")


def filter_fields(data: Any, fields: List[str]) -> Any:
    """Filter data to include only specified fields.

    Args:
        data: Dict or list of dicts
        fields: List of field names to include

    Returns:
        Filtered data
    """
    if isinstance(data, dict):
        return {k: v for k, v in data.items() if k in fields}
    elif isinstance(data, list):
        return [
            filter_fields(item, fields) if isinstance(item, dict) else item
            for item in data
        ]
    else:
        return data


def paginate_all(
    fetch_func: Callable, limit: int = 250, offset: int = 0, **kwargs
) -> List[Dict[str, Any]]:
    """Paginate through all results using limit/offset.

    Args:
        fetch_func: Function that accepts offset, limit, and kwargs
        limit: Page size
        offset: Starting offset
        **kwargs: Additional parameters to pass to fetch_func

    Returns:
        List of all results
    """
    all_results = []
    current_offset = offset

    while True:
        results = fetch_func(offset=current_offset, limit=limit, **kwargs)

        if not results:
            break

        all_results.extend(results)

        if len(results) < limit:
            break

        current_offset += limit

    return all_results


def parse_datetime(value: str) -> int:
    """Parse datetime string to epoch seconds.

    Accepts ISO8601 format or epoch seconds.

    Args:
        value: DateTime string or epoch seconds

    Returns:
        Unix timestamp (seconds since epoch)
    """
    # Try as epoch seconds first
    try:
        timestamp = int(value)
        # Validate reasonable range (1970-2100)
        if timestamp < 0 or timestamp > 4102444800:
            raise ValueError(
                f"Invalid timestamp: {value}. Must be between 0 and 4102444800 (year 2100)."
            )
        return timestamp
    except ValueError as e:
        if "Invalid timestamp" in str(e):
            raise
        # Not an integer, try ISO8601

    # Try ISO8601 parsing
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        timestamp = int(dt.timestamp())
        # Validate reasonable range
        if timestamp < 0 or timestamp > 4102444800:
            raise ValueError(
                f"Invalid date: {value}. Must be between 1970 and 2100."
            )
        return timestamp
    except ValueError as e:
        if "Invalid date" in str(e):
            raise
        raise ValueError(
            f"Invalid datetime format: {value}. Use ISO8601 (e.g., '2024-01-01T00:00:00Z') or epoch seconds."
        )


def parse_list(value: str) -> List[str]:
    """Parse comma-separated string to list.

    Args:
        value: Comma-separated values

    Returns:
        List of strings
    """
    return [v.strip() for v in value.split(",") if v.strip()]


def error_exit(message: str, exit_code: int = 1) -> None:
    """Print error message and exit.

    Args:
        message: Error message
        exit_code: Exit code (default 1)
    """
    error_console = Console(stderr=True)
    error_console.print(f"[bold red]Error:[/bold red] {message}")
    sys.exit(exit_code)


def handle_api_error(e: Exception) -> None:
    """Handle API exception and exit with appropriate message.

    Args:
        e: Exception from API call
    """
    # Handle StatusCodeError from testrail-api
    if hasattr(e, "args") and len(e.args) >= 4:
        status_code, reason, url, body = e.args[:4]
        error_msg = f"HTTP {status_code}: {reason}"

        # Try to parse error body
        if body:
            try:
                body_str = (
                    body.decode("utf-8") if isinstance(body, bytes) else str(body)
                )
                error_data = json.loads(body_str)
                if "error" in error_data:
                    error_msg = f"HTTP {status_code}: {error_data['error']}"
            except (ValueError, AttributeError):
                pass
    else:
        error_msg = str(e)

    error_exit(error_msg)
