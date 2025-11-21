"""Tests for CSV import normalization."""

from pathlib import Path

from testrail_cli.csv_import import import_cases_from_csv


class StubTestRailClient:
    """Lightweight stub client for CSV import tests."""

    def __init__(self):
        self.created_cases: list[dict] = []
        self.updated_cases: list[dict] = []

    def get_suites(self, project_id: int):
        return [{"id": 1, "name": "Default"}]

    def get_sections(self, project_id: int, suite_id: int | None = None):
        return [{"id": 10, "name": "Auth"}]

    def add_section(self, project_id: int, name: str, **kwargs):
        # Mirrors TestRail structure
        return {"id": 99, "name": name, **kwargs}

    def add_case(self, section_id: int, title: str, **kwargs):
        payload = {"section_id": section_id, "title": title, **kwargs}
        self.created_cases.append(payload)
        return {"id": len(self.created_cases), **payload}

    def update_case(self, case_id: int, **kwargs):
        payload = {"case_id": case_id, **kwargs}
        self.updated_cases.append(payload)
        return payload


def _write_csv(tmp_path: Path, content: str) -> str:
    csv_path = tmp_path / "cases.csv"
    csv_path.write_text(content)
    return str(csv_path)


def test_import_cases_handles_teststeps_and_numbered_steps(tmp_path):
    """Structured steps in CSV get normalized into custom_steps_separated."""
    csv_content = """case_id,title,section,teststeps,step_1,expected_1,step_2,expected_2
,Create with teststeps,Auth,"Open login | Form shows\\nSubmit form | Success banner",,,,
123,Update with columns,Auth,,Add item,Item added,Remove item,Cart cleared
"""
    csv_path = _write_csv(tmp_path, csv_content)
    client = StubTestRailClient()

    result = import_cases_from_csv(client, project_id=1, csv_path=csv_path)

    assert result["errors"] == 0
    assert result["created"] == 1
    assert result["updated"] == 1

    # Creation payload captures parsed teststeps
    created_steps = client.created_cases[0]["custom_steps_separated"]
    assert created_steps == [
        {"content": "Open login", "expected": "Form shows"},
        {"content": "Submit form", "expected": "Success banner"},
    ]

    # Update payload captures numbered step columns
    updated_steps = client.updated_cases[0]["custom_steps_separated"]
    assert updated_steps == [
        {"content": "Add item", "expected": "Item added"},
        {"content": "Remove item", "expected": "Cart cleared"},
    ]


def test_steps_field_respects_template_and_additional_info(tmp_path):
    """Step destination changes with steps_field/template and carries additional info."""
    csv_content = """title,section,template,steps_field,teststeps
Text template uses blob,Auth,Text,custom_steps,"Do thing | Expect thing | Info A"
Steps template uses list,Auth,Steps,,"Click login | Form shows | Browser Chrome"
"""
    csv_path = _write_csv(tmp_path, csv_content)
    client = StubTestRailClient()

    result = import_cases_from_csv(client, project_id=1, csv_path=csv_path)

    assert result["errors"] == 0
    assert result["created"] == 2

    # First row goes to custom_steps text field
    text_case = client.created_cases[0]
    assert "custom_steps" in text_case
    assert "Expected: Expect thing" in text_case["custom_steps"]
    assert "Info: Info A" in text_case["custom_steps"]

    # Second row defaults to structured steps and keeps additional_info
    steps_case = client.created_cases[1]
    step_entries = steps_case["custom_steps_separated"]
    assert step_entries[0]["additional_info"] == "Browser Chrome"
