"""Tests for CSV import normalization."""

from pathlib import Path

from testrail_cli.csv_import import import_cases_from_csv


class StubTestRailClient:
    """Lightweight stub client for CSV import tests."""

    def __init__(self):
        self.created_cases: list[dict] = []
        self.updated_cases: list[dict] = []
        self.sections = {10: {"id": 10, "name": "Auth", "parent_id": None}}
        self.cases_for_export: list[dict] = []

    def get_suites(self, _project_id: int):
        return [{"id": 1, "name": "Default"}]

    def get_sections(self, _project_id: int, suite_id: int | None = None):
        _ = suite_id
        return list(self.sections.values())

    def get_section(self, section_id: int):
        return self.sections[section_id]

    def add_section(self, _project_id: int, name: str, **kwargs):
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

    def get_cases(self, _project_id: int, **kwargs):
        _ = kwargs
        return self.cases_for_export

    def get_case(self, case_id: int):
        for case in self.cases_for_export:
            if case["id"] == case_id:
                return case
        raise KeyError(case_id)


def _write_csv(tmp_path: Path, content: str) -> str:
    csv_path = tmp_path / "cases.csv"
    csv_path.write_text(content)
    return str(csv_path)


def test_import_cases_handles_teststeps_and_numbered_steps(tmp_path):
    """Multiple rows per case aggregate into custom_steps_separated."""
    csv_content = """case_id,title,section,step,expected
,Create with rows,Auth,Open login,Form shows
,Create with rows,Auth,Submit form,Success banner
123,Update with rows,Auth,Add item,Item added
"""
    csv_path = _write_csv(tmp_path, csv_content)
    client = StubTestRailClient()

    result = import_cases_from_csv(client, project_id=1, csv_path=csv_path)

    assert result["errors"] == 0
    assert result["created"] == 1
    assert result["updated"] == 1

    created_steps = client.created_cases[0]["custom_steps_separated"]
    assert created_steps == [
        {"content": "Open login", "expected": "Form shows"},
        {"content": "Submit form", "expected": "Success banner"},
    ]

    updated_steps = client.updated_cases[0]["custom_steps_separated"]
    assert updated_steps == [
        {"content": "Add item", "expected": "Item added"},
    ]


def test_steps_field_respects_template_and_additional_info(tmp_path):
    """steps_field override flattens steps to text and carries additional info."""
    csv_content = """case_id,title,section,step,expected,additional_info
,Text template uses blob,Auth,Do thing,Expect thing,Info A
,Text template uses blob,Auth,Second step,Second expected,Second info
"""
    csv_path = _write_csv(tmp_path, csv_content)
    client = StubTestRailClient()

    result = import_cases_from_csv(
        client,
        project_id=1,
        csv_path=csv_path,
        template_id=7,
        steps_field="custom_steps",
    )

    assert result["errors"] == 0
    assert result["created"] == 1

    case = client.created_cases[0]
    assert case.get("template_id") == 7
    assert "custom_steps" in case
    assert "Do thing" in case["custom_steps"]
    assert "Expected: Expect thing" in case["custom_steps"]
    assert "Info: Info A" in case["custom_steps"]


def test_export_cases_to_csv(tmp_path):
    """Export produces the same structure (one row per step)."""
    from testrail_cli.csv_import import export_cases_to_csv

    client = StubTestRailClient()
    client.sections[20] = {"id": 20, "name": "Login", "parent_id": 10}
    client.sections[10] = {"id": 10, "name": "Auth", "parent_id": None}
    client.cases_for_export = [
        {
            "id": 5,
            "title": "Export me",
            "section_id": 20,
            "priority_id": 2,
            "type_id": 1,
            "template_id": 3,
            "estimate": "2m",
            "refs": "REQ-9",
            "custom_steps_separated": [
                {"content": "Step one", "expected": "Exp one", "additional_info": "Info"},
                {"content": "Step two", "expected": "Exp two"},
            ],
        }
    ]

    csv_path = tmp_path / "out.csv"
    result = export_cases_to_csv(client, project_id=1, csv_path=str(csv_path))
    assert result["exported"] == 2

    content = csv_path.read_text()
    assert "Export me" in content
    assert "Auth/Login" in content


def test_import_exploratory_template(tmp_path):
    """Import verifies standard fields are mapped to custom fields."""
    csv_content = """case_id,title,section,mission,goals
,Exploratory Session,Auth,Test mission,Test goals
"""
    csv_path = _write_csv(tmp_path, csv_content)
    client = StubTestRailClient()

    result = import_cases_from_csv(client, project_id=1, csv_path=csv_path)

    assert result["errors"] == 0
    assert result["created"] == 1

    case = client.created_cases[0]
    assert case["custom_mission"] == "Test mission"
    assert case["custom_goals"] == "Test goals"
    assert "mission" not in case
    assert "goals" not in case


def test_export_includes_template_fields(tmp_path):
    """Export includes mission, goals, and preconds."""
    from testrail_cli.csv_import import export_cases_to_csv

    client = StubTestRailClient()
    client.sections[10] = {"id": 10, "name": "Auth", "parent_id": None}
    client.cases_for_export = [
        {
            "id": 5,
            "title": "Export me",
            "section_id": 10,
            "template_id": 1,
            "custom_mission": "My Mission",
            "custom_goals": "My Goals",
            "custom_preconds": "My Preconditions",
        }
    ]

    csv_path = tmp_path / "out.csv"
    result = export_cases_to_csv(client, project_id=1, csv_path=str(csv_path))
    assert result["exported"] == 1

    content = csv_path.read_text()
    assert "My Mission" in content
    assert "My Goals" in content
    assert "My Preconditions" in content

    # Verify header
    lines = content.splitlines()
    header = lines[0]
    assert "mission" in header
    assert "goals" in header
    assert "preconds" in header
