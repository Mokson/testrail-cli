"""CSV import functionality for test cases."""

import csv
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml

from .client import TestRailClient


def load_mapping(mapping_path: str) -> Dict[str, Any]:
    """Load field mapping from YAML or JSON file.

    Args:
        mapping_path: Path to mapping file

    Returns:
        Mapping dictionary
    """
    path = Path(mapping_path)
    with open(path, "r") as f:
        if path.suffix in [".yaml", ".yml"]:
            return yaml.safe_load(f) or {}
        else:
            return json.load(f)


def apply_mapping(
    row: Dict[str, str], mapping: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """Apply field mapping to a CSV row.

    Args:
        row: CSV row as dict
        mapping: Optional mapping configuration

    Returns:
        Mapped row
    """
    if not mapping:
        return row

    mapped = {}
    field_mappings = mapping.get("fields", {})

    for csv_field, value in row.items():
        # Check if there's a mapping for this field
        if csv_field in field_mappings:
            target_field = field_mappings[csv_field]
            if isinstance(target_field, dict):
                # Complex mapping with transformations
                mapped_field = target_field.get("field", csv_field)
                mapped[mapped_field] = value
            else:
                # Simple field rename
                mapped[target_field] = value
        else:
            # No mapping, use as-is
            mapped[csv_field] = value

    return mapped


def validate_row(row: Dict[str, Any], row_num: int) -> List[str]:
    """Validate a CSV row.

    Args:
        row: Row data
        row_num: Row number for error messages

    Returns:
        List of validation errors
    """
    errors = []

    # Check for required fields
    if "case_id" not in row or not row.get("case_id"):
        # New case - title is required
        if "title" not in row or not row.get("title") or not row.get("title").strip():
            errors.append(f"Row {row_num}: Missing or empty 'title' field for new cases")

    return errors


def resolve_suite(
    client: TestRailClient,
    project_id: int,
    suite_id: Optional[int],
    suite_name: Optional[str],
) -> int:
    """Resolve suite ID from ID or name.

    Args:
        client: TestRail client
        project_id: Project ID
        suite_id: Optional suite ID
        suite_name: Optional suite name

    Returns:
        Suite ID
    """
    if suite_id:
        return suite_id

    if suite_name:
        suites = client.get_suites(project_id)
        for suite in suites:
            if suite["name"] == suite_name:
                return suite["id"]
        raise ValueError(f"Suite not found: {suite_name}")

    # Try to get default suite (for single-suite projects)
    suites = client.get_suites(project_id)
    if len(suites) == 1:
        return suites[0]["id"]

    raise ValueError("suite_id or suite_name is required for multi-suite projects")


def resolve_section(
    client: TestRailClient,
    project_id: int,
    suite_id: int,
    section_path: Optional[str],
    create_missing: bool = False,
) -> Optional[int]:
    """Resolve section ID from path.

    Args:
        client: TestRail client
        project_id: Project ID
        suite_id: Suite ID
        section_path: Section path (e.g., "Parent/Child")
        create_missing: Whether to create missing sections

    Returns:
        Section ID or None
    """
    if not section_path:
        return None

    sections = client.get_sections(project_id, suite_id=suite_id)

    # Build section hierarchy
    section_map = {s["name"]: s for s in sections}

    # Parse path
    parts = section_path.split("/")
    current_section = None

    for part in parts:
        if part in section_map:
            current_section = section_map[part]
        elif create_missing:
            # Create missing section
            parent_id = current_section["id"] if current_section else None
            new_section = client.add_section(
                project_id,
                part,
                suite_id=suite_id,
                parent_id=parent_id,
            )
            section_map[part] = new_section
            current_section = new_section
        else:
            raise ValueError(f"Section not found: {part} in path {section_path}")

    return current_section["id"] if current_section else None


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks.

    Args:
        items: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]


def import_cases_from_csv(
    client: TestRailClient,
    project_id: int,
    csv_path: str,
    suite_id: Optional[int] = None,
    suite_name: Optional[str] = None,
    section_path: Optional[str] = None,
    mapping_path: Optional[str] = None,
    create_missing_sections: bool = False,
    chunk_size: int = 50,
) -> Dict[str, int]:
    """Import test cases from CSV file.

    Args:
        client: TestRail client
        project_id: Project ID
        csv_path: Path to CSV file
        suite_id: Optional suite ID
        suite_name: Optional suite name
        section_path: Default section path
        mapping_path: Optional path to mapping file
        create_missing_sections: Whether to create missing sections
        chunk_size: Batch size for API calls

    Returns:
        Dictionary with counts: created, updated, errors
    """
    # Load mapping if provided
    mapping = None
    if mapping_path:
        mapping = load_mapping(mapping_path)

    # Resolve suite
    suite_id = resolve_suite(client, project_id, suite_id, suite_name)

    # Resolve default section
    default_section_id = None
    if section_path:
        default_section_id = resolve_section(
            client, project_id, suite_id, section_path, create_missing_sections
        )

    # Read CSV
    rows = []
    errors = []
    error_details = []

    try:
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader, start=2):  # Start at 2 (row 1 is header)
                # Apply mapping
                mapped_row = apply_mapping(row, mapping)

                # Validate
                row_errors = validate_row(mapped_row, idx)
                if row_errors:
                    errors.extend(row_errors)
                    error_details.extend(row_errors)
                    continue

                rows.append(mapped_row)
    except FileNotFoundError:
        return {
            "created": 0,
            "updated": 0,
            "errors": 1,
            "error_details": [f"CSV file not found: {csv_path}"]
        }

    # Split into creates and updates
    creates = []
    updates = []

    for row in rows:
        if "case_id" in row and row["case_id"]:
            updates.append(row)
        else:
            creates.append(row)

    # Process creates
    created_count = 0
    for chunk in chunk_list(creates, chunk_size):
        for case_data in chunk:
            try:
                # Determine section
                section_id = default_section_id
                if "section" in case_data and case_data["section"]:
                    section_id = resolve_section(
                        client,
                        project_id,
                        suite_id,
                        case_data["section"],
                        create_missing_sections,
                    )

                if not section_id:
                    raise ValueError("Section is required for creating cases")

                # Prepare case data
                title = case_data.get("title")
                if not title:
                    raise ValueError("Title is required for creating cases")

                # Create a copy and remove non-API fields
                api_data = dict(case_data)
                api_data.pop("title", None)
                api_data.pop("section", None)
                api_data.pop("case_id", None)

                # Create case
                client.add_case(section_id, title, **api_data)
                created_count += 1

            except Exception as e:
                errors.append(str(e))
                error_details.append(f"Create error: {e}")

    # Process updates
    updated_count = 0
    for case_data in updates:
        try:
            case_id_str = case_data.get("case_id")
            if not case_id_str:
                raise ValueError("case_id is required for updates")
            case_id = int(case_id_str)

            # Create a copy and remove non-API fields
            api_data = dict(case_data)
            api_data.pop("case_id", None)
            api_data.pop("section", None)

            # Update case
            client.update_case(case_id, **api_data)
            updated_count += 1

        except Exception as e:
            errors.append(str(e))
            error_details.append(f"Update error for case {case_id}: {e}")

    return {
        "created": created_count,
        "updated": updated_count,
        "errors": len(errors),
        "error_details": error_details if error_details else None,
    }
