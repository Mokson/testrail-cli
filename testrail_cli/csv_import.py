"""CSV import functionality for test cases."""

import csv
import json
import re
from pathlib import Path
from typing import Any

import yaml

from .client import TestRailClient


def load_mapping(mapping_path: str) -> dict[str, Any]:
    """Load field mapping from YAML or JSON file.

    Args:
        mapping_path: Path to mapping file

    Returns:
        Mapping dictionary
    """
    path = Path(mapping_path)
    with open(path) as f:
        if path.suffix in [".yaml", ".yml"]:
            return yaml.safe_load(f) or {}
        else:
            return json.load(f)  # type: ignore[no-any-return]


def apply_mapping(row: dict[str, str], mapping: dict[str, Any] | None) -> dict[str, Any]:
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


STANDARD_FIELDS = {
    "mission": "custom_mission",
    "goals": "custom_goals",
    "preconds": "custom_preconds",
    "preconditions": "custom_preconds",
}


def _apply_standard_mapping(row: dict[str, Any]) -> dict[str, Any]:
    """Apply standard field mapping for common templates."""
    mapped = dict(row)
    for standard, custom in STANDARD_FIELDS.items():
        if standard in mapped and custom not in mapped:
            mapped[custom] = mapped.pop(standard)
    return mapped


def validate_row(row: dict[str, Any], row_num: int) -> list[str]:
    """Validate a CSV row.

    Args:
        row: Row data
        row_num: Row number for error messages

    Returns:
        List of validation errors
    """
    errors = []

    # Check for required fields
    if ("case_id" not in row or not row.get("case_id")) and (
        "title" not in row or not row.get("title") or not row.get("title", "").strip()
    ):
        errors.append(f"Row {row_num}: Missing or empty 'title' field for new cases")

    return errors


def _normalize_step_items(data: Any) -> list[dict[str, str]]:
    """Convert various step formats into TestRail step dictionaries."""
    normalized_steps: list[dict[str, str]] = []

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                content = str(item.get("content", "")).strip()
                expected = str(item.get("expected", "")).strip()
                additional_info = str(item.get("additional_info", "")).strip()
                if content or expected or additional_info:
                    step_dict = {"content": content, "expected": expected}
                    if additional_info:
                        step_dict["additional_info"] = additional_info
                    normalized_steps.append(step_dict)
            elif item is not None:
                content = str(item).strip()
                if content:
                    normalized_steps.append({"content": content, "expected": ""})
    elif isinstance(data, dict):
        content = str(data.get("content", "")).strip()
        expected = str(data.get("expected", "")).strip()
        additional_info = str(data.get("additional_info", "")).strip()
        if content or expected or additional_info:
            step_dict = {"content": content, "expected": expected}
            if additional_info:
                step_dict["additional_info"] = additional_info
            normalized_steps.append(step_dict)

    return normalized_steps


def parse_steps_value(
    value: Any, row_num: int, field_name: str
) -> tuple[list[dict[str, str]], list[str]]:
    """Parse a CSV value into TestRail step dictionaries.

    Supports JSON lists/dicts, newline-separated strings, and pipe-delimited
    action/expected pairs (e.g., "Do thing | Expect result").
    """
    errors: list[str] = []

    if value is None:
        return [], errors

    # Preserve already-normalized lists/dicts
    if isinstance(value, list | dict):
        return _normalize_step_items(value), errors

    text = str(value).strip()
    if not text:
        return [], errors

    # Try JSON first
    try:
        parsed = json.loads(text)
        return _normalize_step_items(parsed), errors
    except json.JSONDecodeError:
        pass

    # Handle escaped newlines for single-cell multi-steps
    lines = text.replace("\\n", "\n").splitlines()
    steps: list[dict[str, str]] = []
    for line in lines:
        if not line.strip():
            continue

        # Split content/expected using common separators
        if "||" in line:
            parts = line.split("||", 2)
        elif "|" in line:
            parts = line.split("|", 2)
        elif "->" in line:
            parts = line.split("->", 2)
        else:
            parts = [line]

        content = parts[0].strip() if len(parts) > 0 else ""
        expected = parts[1].strip() if len(parts) > 1 else ""
        additional_info = parts[2].strip() if len(parts) > 2 else ""
        if content or expected or additional_info:
            step = {"content": content, "expected": expected}
            if additional_info:
                step["additional_info"] = additional_info
            steps.append(step)

    if not steps:
        errors.append(f"Row {row_num}: Unable to parse steps from '{field_name}'")

    return steps, errors


def infer_step_target_field(row: dict[str, Any]) -> tuple[str, set[str]]:
    """Infer which TestRail field should receive structured steps."""
    cleanup_keys: set[str] = set()

    explicit = row.get("steps_field") or row.get("step_field") or row.get("steps_target")
    if explicit:
        cleanup_keys.update({"steps_field", "step_field", "steps_target"})
        return str(explicit), cleanup_keys

    template_hint = str(row.get("template") or row.get("template_name") or "").lower()
    if template_hint:
        cleanup_keys.update({"template", "template_name"})
        if "gherkin" in template_hint:
            return "custom_gherkin", cleanup_keys
        if "text" in template_hint or "exploratory" in template_hint:
            return "custom_steps", cleanup_keys
        if "step" in template_hint:
            return "custom_steps_separated", cleanup_keys

    if "custom_gherkin" in row:
        return "custom_gherkin", cleanup_keys
    if "custom_steps" in row:
        return "custom_steps", cleanup_keys

    return "custom_steps_separated", cleanup_keys


def format_steps_as_text(steps: list[dict[str, str]]) -> str:
    """Convert structured steps into a text blob for text templates."""
    lines = []
    for step in steps:
        parts = [step.get("content", "").strip()]
        expected = step.get("expected", "").strip()
        additional = step.get("additional_info", "").strip()
        if expected:
            parts.append(f"Expected: {expected}")
        if additional:
            parts.append(f"Info: {additional}")
        composed = " | ".join(p for p in parts if p)
        if composed:
            lines.append(composed)
    return "\n".join(lines)


def apply_steps_to_payload(
    api_data: dict[str, Any],
    steps: list[dict[str, str]],
    target_field: str | None,
) -> None:
    """Attach steps to the API payload according to the target field."""
    field = target_field or api_data.pop("steps_field", None)

    if field == "custom_steps":
        api_data["custom_steps"] = format_steps_as_text(steps)
    elif field == "custom_gherkin":
        api_data["custom_gherkin"] = format_steps_as_text(steps)
    else:
        api_data["custom_steps_separated"] = steps


def _get_section_path(client: TestRailClient, section_id: int, cache: dict[int, str]) -> str:
    """Resolve section_id to path and memoize."""
    if section_id in cache:
        return cache[section_id]

    section = client.get_section(section_id)
    parent_id = section.get("parent_id")
    if parent_id:
        parent_path = _get_section_path(client, parent_id, cache)
        path = f"{parent_path}/{section['name']}"
    else:
        path = section["name"]

    cache[section_id] = path
    return path


def case_to_rows(case: dict[str, Any], section_path: str) -> list[dict[str, Any]]:
    """Convert a TestRail case dict into CSV step rows."""
    base = {
        "case_id": case.get("id"),
        "title": case.get("title", ""),
        "section": section_path,
        "priority_id": case.get("priority_id"),
        "type_id": case.get("type_id"),
        "template_id": case.get("template_id"),
        "estimate": case.get("estimate"),
        "refs": case.get("refs"),
        "mission": case.get("custom_mission"),
        "goals": case.get("custom_goals"),
        "preconds": case.get("custom_preconds"),
    }

    steps = case.get("custom_steps_separated") or []
    if not steps and case.get("custom_steps"):
        # Flatten text steps into separate lines
        steps = [
            {"content": line.strip(), "expected": ""}
            for line in str(case["custom_steps"]).splitlines()
            if line
        ]
    if not steps and case.get("custom_gherkin"):
        steps = [
            {"content": line.strip(), "expected": ""}
            for line in str(case["custom_gherkin"]).splitlines()
            if line
        ]

    rows: list[dict[str, Any]] = []
    if not steps:
        rows.append({**base, "step": "", "expected": "", "additional_info": ""})
        return rows

    for step in steps:
        rows.append(
            {
                **base,
                "step": step.get("content", ""),
                "expected": step.get("expected", ""),
                "additional_info": step.get("additional_info", ""),
            }
        )

    return rows


def export_cases_to_csv(
    client: TestRailClient,
    project_id: int,
    csv_path: str,
    suite_id: int | None = None,
    case_ids: list[int] | None = None,
    section_id: int | None = None,
    priority_ids: list[int] | None = None,
    type_ids: list[int] | None = None,
) -> dict[str, Any]:
    """Export test cases to CSV in the same structure as import."""
    section_cache: dict[int, str] = {}
    cases: list[dict[str, Any]] = []

    if case_ids:
        for case_id in case_ids:
            cases.append(client.get_case(case_id))
    else:
        kwargs: dict[str, Any] = {}
        if suite_id:
            kwargs["suite_id"] = suite_id
        if section_id:
            kwargs["section_id"] = section_id
        if priority_ids:
            kwargs["priority_id"] = priority_ids
        if type_ids:
            kwargs["type_id"] = type_ids
        cases = client.get_cases(project_id, **kwargs)

    rows: list[dict[str, Any]] = []
    for case in cases:
        section_path = ""
        if case.get("section_id"):
            section_path = _get_section_path(client, int(case["section_id"]), section_cache)
        rows.extend(case_to_rows(case, section_path))

    fieldnames = [
        "case_id",
        "title",
        "section",
        "priority_id",
        "type_id",
        "template_id",
        "estimate",
        "refs",
        "mission",
        "goals",
        "preconds",
        "step",
        "expected",
        "additional_info",
    ]
    Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    return {"exported": len(rows)}


def normalize_row(row: dict[str, Any], row_num: int) -> tuple[dict[str, Any], list[str]]:
    """Normalize row data (e.g., convert step representations).

    Args:
        row: Raw or mapped row data
        row_num: Current CSV row number (for error reporting)

    Returns:
        Tuple of (normalized row, list of errors)
    """
    normalized = dict(row)
    errors: list[str] = []
    step_fields: dict[int, dict[str, str]] = {}
    keys_to_remove: set[str] = set()

    # Collect numbered step/expected/extra columns (e.g., step_1, expected_1, info_1)
    for key, value in list(normalized.items()):
        if value is None:
            continue

        lower_key = key.lower()
        step_match = re.match(r"step[\s_]*(\d+)$", lower_key)
        expected_match = re.match(r"(expected|exp)[\s_]*(\d+)$", lower_key)
        info_match = re.match(
            r"(additional(_info)?|info|notes?|note|data|test[_\s]?data)[\s_]*(\d+)$", lower_key
        )

        if step_match:
            idx = int(step_match.group(1))
            step_fields.setdefault(idx, {})["content"] = str(value).strip()
            keys_to_remove.add(key)
        elif expected_match:
            idx = int(expected_match.group(2))
            step_fields.setdefault(idx, {})["expected"] = str(value).strip()
            keys_to_remove.add(key)
        elif info_match:
            idx = int(info_match.group(3))
            step_fields.setdefault(idx, {})["additional_info"] = str(value).strip()
            keys_to_remove.add(key)

    steps: list[dict[str, str]] = []
    if step_fields:
        for idx in sorted(step_fields):
            entry = step_fields[idx]
            content = entry.get("content", "").strip()
            expected = entry.get("expected", "").strip()
            additional = entry.get("additional_info", "").strip()
            if content or expected or additional:
                step_dict = {"content": content, "expected": expected}
                if additional:
                    step_dict["additional_info"] = additional
                steps.append(step_dict)

    # Parse combined test step fields
    structured_step_fields = {
        "teststeps",
        "test_steps",
        "steps_separated",
        "custom_steps_separated",
    }
    for key in list(normalized.keys()):
        if key in keys_to_remove:
            continue

        lower_key = key.lower()
        if lower_key in structured_step_fields:
            parsed_steps, parse_errors = parse_steps_value(normalized[key], row_num, key)
            steps.extend(parsed_steps)
            errors.extend(parse_errors)
            keys_to_remove.add(key)

    if steps:
        target_field, inferred_keys = infer_step_target_field(normalized)
        keys_to_remove.update(inferred_keys)

        if target_field in {"custom_steps", "custom_gherkin"}:
            normalized[target_field] = format_steps_as_text(steps)
        else:
            normalized["custom_steps_separated"] = steps

    meta_keys = {"steps_field", "step_field", "steps_target", "template", "template_name"}
    for key in keys_to_remove.union(meta_keys):
        normalized.pop(key, None)

    return normalized, errors


def extract_steps_and_clean(
    row: dict[str, Any], row_num: int
) -> tuple[dict[str, Any], list[dict[str, str]], list[str]]:
    """Extract a single step (one row per step) and clean base fields."""
    errors: list[str] = []
    steps: list[dict[str, str]] = []
    cleaned = dict(row)
    keys_to_remove: set[str] = set()

    # Structured step columns (one step per row)
    content = ""
    expected = ""
    additional_info = ""
    for key, value in list(cleaned.items()):
        lower_key = key.lower()
        if lower_key in {"step", "step_content", "action"}:
            content = str(value or "").strip()
            keys_to_remove.add(key)
        elif lower_key in {"expected", "expected_result"}:
            expected = str(value or "").strip()
            keys_to_remove.add(key)
        elif lower_key in {"additional_info", "info", "notes", "note", "data", "test_data"}:
            additional_info = str(value or "").strip()
            keys_to_remove.add(key)

    if content or expected or additional_info:
        step_dict: dict[str, str] = {"content": content, "expected": expected}
        if additional_info:
            step_dict["additional_info"] = additional_info
        steps.append(step_dict)

    # Fallback: allow teststeps for compatibility (parsed into steps)
    if "teststeps" in cleaned and not steps:
        parsed_steps, parse_errors = parse_steps_value(
            cleaned.get("teststeps"), row_num, "teststeps"
        )
        steps.extend(parsed_steps)
        errors.extend(parse_errors)
        keys_to_remove.add("teststeps")

    # Remove step/meta columns from base data
    for key in keys_to_remove:
        cleaned.pop(key, None)

    return cleaned, steps, errors


def build_case_key(
    row: dict[str, Any], default_section: str | None
) -> tuple[str, str, str] | tuple[str, int] | None:
    """Build a grouping key for multi-row cases."""
    case_id = row.get("case_id")
    if case_id:
        try:
            return ("id", int(case_id))
        except ValueError:
            return None

    title = str(row.get("title", "")).strip()
    section = str(row.get("section", default_section or "")).strip()
    if title and section:
        return ("new", title.lower(), section.lower())
    return None


def merge_base_data(existing: dict[str, Any], incoming: dict[str, Any], row_num: int) -> list[str]:
    """Ensure repeated rows of the same case keep consistent values."""
    errors: list[str] = []
    for key, value in incoming.items():
        if value is None or str(value).strip() == "":
            continue
        if key not in existing or not existing.get(key):
            existing[key] = value
        elif str(existing[key]).strip() != str(value).strip():
            errors.append(
                f"Row {row_num}: Conflicting value for '{key}' "
                f"(previous '{existing[key]}', got '{value}')"
            )
    return errors


def resolve_suite(
    client: TestRailClient,
    project_id: int,
    suite_id: int | None,
    suite_name: str | None,
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
                return suite["id"]  # type: ignore[no-any-return]
        raise ValueError(f"Suite not found: {suite_name}")

    # Try to get default suite (for single-suite projects)
    suites = client.get_suites(project_id)
    if len(suites) == 1:
        return suites[0]["id"]  # type: ignore[no-any-return]

    raise ValueError("suite_id or suite_name is required for multi-suite projects")


def resolve_section(
    client: TestRailClient,
    project_id: int,
    suite_id: int,
    section_path: str | None,
    create_missing: bool = False,
) -> int | None:
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


def chunk_list(items: list[Any], chunk_size: int) -> list[list[Any]]:
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
    suite_id: int | None = None,
    suite_name: str | None = None,
    section_path: str | None = None,
    mapping_path: str | None = None,
    template_id: int | None = None,
    steps_field: str | None = None,
    create_missing_sections: bool = False,
    chunk_size: int = 50,
) -> dict[str, Any]:
    """Import test cases from CSV file.

    Args:
        client: TestRail client
        project_id: Project ID
        csv_path: Path to CSV file
        suite_id: Optional suite ID
        suite_name: Optional suite name
        section_path: Default section path
        mapping_path: Optional path to mapping file
        template_id: Optional template ID to apply to all cases
        steps_field: Optional target steps field override
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

    # Read CSV and group rows per case (one row per step)
    grouped: dict[tuple[Any, ...], dict[str, Any]] = {}
    errors: list[str] = []
    error_details: list[str] = []

    try:
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            if "case_id" not in (reader.fieldnames or []):
                return {
                    "created": 0,
                    "updated": 0,
                    "errors": 1,
                    "error_details": [
                        "CSV must include 'case_id' column (may be empty for new cases)"
                    ],
                }
            for idx, row in enumerate(reader, start=2):  # Start at 2 (row 1 is header)
                # Apply mapping
                mapped_row = apply_mapping(row, mapping)
                mapped_row = _apply_standard_mapping(mapped_row)
                cleaned_row, step_entries, normalization_errors = extract_steps_and_clean(
                    mapped_row, idx
                )
                if normalization_errors:
                    errors.extend(normalization_errors)
                    error_details.extend(normalization_errors)
                    continue

                key = build_case_key(cleaned_row, section_path)
                if not key:
                    err = f"Row {idx}: Missing identifiers (case_id or title+section)"
                    errors.append(err)
                    error_details.append(err)
                    continue

                grouped.setdefault(key, {"base": {}, "steps": []})
                merge_errors = merge_base_data(grouped[key]["base"], cleaned_row, idx)
                if merge_errors:
                    errors.extend(merge_errors)
                    error_details.extend(merge_errors)
                    continue

                if step_entries:
                    grouped[key]["steps"].extend(step_entries)
    except FileNotFoundError:
        return {
            "created": 0,
            "updated": 0,
            "errors": 1,
            "error_details": [f"CSV file not found: {csv_path}"],
        }

    # Split into creates and updates
    creates: list[dict[str, Any]] = []
    updates: list[dict[str, Any]] = []

    for key, data in grouped.items():
        base_row = data["base"]
        step_entries = data["steps"]

        # Validate base fields
        row_errors = validate_row(base_row, 0)
        if row_errors:
            errors.extend(row_errors)
            error_details.extend(row_errors)
            continue

        # Attach aggregated steps for later processing
        if step_entries:
            base_row["__steps"] = step_entries

        if key[0] == "id":
            updates.append(base_row)
        else:
            creates.append(base_row)

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
                steps = api_data.pop("__steps", [])
                api_data.pop("title", None)
                api_data.pop("section", None)
                api_data.pop("case_id", None)
                if template_id and "template_id" not in api_data:
                    api_data["template_id"] = template_id
                if steps:
                    apply_steps_to_payload(api_data, steps, steps_field)

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
            steps = api_data.pop("__steps", [])
            api_data.pop("case_id", None)
            api_data.pop("section", None)
            if template_id and "template_id" not in api_data:
                api_data["template_id"] = template_id
            if steps:
                apply_steps_to_payload(api_data, steps, steps_field)

            # Update case
            client.update_case(case_id, **api_data)
            updated_count += 1

        except Exception as e:
            errors.append(str(e))
            error_details.append(f"Update error for case {case_id_str}: {e}")

    return {
        "created": created_count,
        "updated": updated_count,
        "errors": len(errors),
        "error_details": error_details if error_details else None,
    }
