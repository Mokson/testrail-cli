"""Unit tests for cases commands."""

import json
from unittest.mock import MagicMock

from typer.testing import CliRunner

from testrail_cli.client import TestRailClient
from testrail_cli.commands.cases import app

runner = CliRunner()


def test_list_cases():
    """Test listing cases."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.get_cases.return_value = [{"id": 1, "title": "Case 1"}]

    result = runner.invoke(
        app,
        ["list", "--project-id", "1"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.get_cases.assert_called_once()
    args, kwargs = mock_client.get_cases.call_args
    assert args == (1,)
    assert "Case 1" in result.stdout


def test_list_cases_by_ids():
    """Test listing cases by IDs."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.get_case.return_value = {"id": 1, "title": "Case 1"}

    result = runner.invoke(
        app,
        ["list", "--case-ids", "1,2"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    assert mock_client.get_case.call_count == 2
    mock_client.get_case.assert_any_call(1)
    mock_client.get_case.assert_any_call(2)


def test_list_cases_filters():
    """Test listing cases with filters."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.get_cases.return_value = []

    result = runner.invoke(
        app,
        [
            "list",
            "--project-id",
            "1",
            "--suite-id",
            "2",
            "--section-id",
            "3",
            "--created-after",
            "1600000000",
            "--priority-id",
            "1,2",
        ],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.get_cases.assert_called_once()
    args, kwargs = mock_client.get_cases.call_args
    assert args == (1,)
    assert kwargs["suite_id"] == 2
    assert kwargs["section_id"] == 3
    assert kwargs["created_after"] == 1600000000
    assert kwargs["priority_id"] == ["1", "2"]


def test_get_case():
    """Test getting a specific case."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.get_case.return_value = {"id": 1, "title": "Case 1"}

    result = runner.invoke(
        app,
        ["get", "1"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.get_case.assert_called_once_with(1)
    assert "Case 1" in result.stdout


def test_add_case():
    """Test adding a case."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.add_case.return_value = {"id": 1, "title": "New Case"}

    result = runner.invoke(
        app,
        ["add", "--section-id", "1", "--title", "New Case"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.add_case.assert_called_once_with(1, "New Case")
    assert "New Case" in result.stdout


def test_add_case_optional_args():
    """Test adding a case with optional arguments."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.add_case.return_value = {"id": 1, "title": "New Case"}

    result = runner.invoke(
        app,
        [
            "add",
            "--section-id",
            "1",
            "--title",
            "New Case",
            "--template-id",
            "2",
            "--type-id",
            "3",
            "--priority-id",
            "4",
            "--estimate",
            "1h",
            "--refs",
            "REF-1",
        ],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.add_case.assert_called_once()
    args, kwargs = mock_client.add_case.call_args
    assert args == (1, "New Case")
    assert kwargs["template_id"] == "2"
    assert kwargs["type_id"] == "3"
    assert kwargs["priority_id"] == "4"
    assert kwargs["estimate"] == "1h"
    assert kwargs["refs"] == "REF-1"


def test_update_case():
    """Test updating a case."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.update_case.return_value = {"id": 1, "title": "Updated Case"}

    result = runner.invoke(
        app,
        ["update", "1", "--title", "Updated Case"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.update_case.assert_called_once_with(1, title="Updated Case")
    assert "Updated Case" in result.stdout


def test_update_case_json_file(tmp_path):
    """Test updating a case using a JSON file."""
    # Create a dummy JSON file
    json_file = tmp_path / "update.json"
    update_data = {
        "title": "Updated via JSON",
        "custom_preconds": "Preconditions from JSON",
        "priority_id": 2,
    }
    json_file.write_text(json.dumps(update_data), encoding="utf-8")

    # Mock the client
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.update_case.return_value = {"id": 1, "title": "Updated via JSON"}

    result = runner.invoke(
        app,
        ["update", "1", "--json", str(json_file)],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.update_case.assert_called_once()
    call_args = mock_client.update_case.call_args
    assert call_args[0] == (1,)  # case_id
    assert call_args[1]["title"] == "Updated via JSON"
    assert call_args[1]["custom_preconds"] == "Preconditions from JSON"
    assert call_args[1]["priority_id"] == 2


def test_update_case_json_stdin():
    """Test updating a case using stdin."""
    update_data = {"title": "Updated via Stdin", "custom_steps": "Steps"}
    input_str = json.dumps(update_data)

    mock_client = MagicMock(spec=TestRailClient)
    mock_client.update_case.return_value = {"id": 1, "title": "Updated via Stdin"}

    result = runner.invoke(
        app,
        ["update", "1", "--file", "-"],
        input=input_str,
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.update_case.assert_called_once()
    call_args = mock_client.update_case.call_args
    assert call_args[1]["title"] == "Updated via Stdin"
    assert call_args[1]["custom_steps"] == "Steps"


def test_update_case_arg_priority():
    """Test that CLI args override JSON values."""
    import os
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tmp:
        json.dump({"title": "From JSON", "priority_id": "1"}, tmp)
        tmp_path = tmp.name

    try:
        mock_client = MagicMock(spec=TestRailClient)
        mock_client.update_case.return_value = {"id": 1, "title": "From CLI"}

        result = runner.invoke(
            app,
            ["update", "1", "--json", tmp_path, "--title", "From CLI"],
            obj={"client": mock_client},
        )

        assert result.exit_code == 0
        mock_client.update_case.assert_called_once()
        kwargs = mock_client.update_case.call_args[1]
        assert kwargs["title"] == "From CLI"  # Should override JSON
        assert kwargs["priority_id"] == "1"  # Should come from JSON

    finally:
        os.remove(tmp_path)


def test_delete_case():
    """Test deleting a case."""
    mock_client = MagicMock(spec=TestRailClient)

    result = runner.invoke(
        app,
        ["delete", "1", "--yes"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.delete_case.assert_called_once_with(1, soft=None)
    assert "deleted successfully" in result.stdout


def test_delete_case_soft():
    """Test soft deleting a case."""
    mock_client = MagicMock(spec=TestRailClient)

    result = runner.invoke(
        app,
        ["delete", "1", "--soft", "1", "--yes"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.delete_case.assert_called_once_with(1, soft=1)
