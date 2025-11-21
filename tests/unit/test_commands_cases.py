"""Unit tests for cases commands."""

import json
from unittest.mock import MagicMock

from typer.testing import CliRunner

from testrail_cli.client import TestRailClient
from testrail_cli.commands.cases import app

runner = CliRunner()


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

    if result.exit_code != 0:
        print(result.stdout)
        print(result.exception)

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

    if result.exit_code != 0:
        print(result.stdout)
        print(result.exception)

    assert result.exit_code == 0
    mock_client.update_case.assert_called_once()
    call_args = mock_client.update_case.call_args
    assert call_args[1]["title"] == "Updated via Stdin"
    assert call_args[1]["custom_steps"] == "Steps"


def test_update_case_arg_priority():
    """Test that CLI args override JSON values."""
    # Create a dummy JSON file
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
