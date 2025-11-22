"""Unit tests for results commands."""

from unittest.mock import MagicMock

from typer.testing import CliRunner

from testrail_cli.client import TestRailClient
from testrail_cli.commands.results import app

runner = CliRunner()


def test_list_results():
    """Test listing results for a test."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.get_results.return_value = [{"id": 1, "status_id": 1}]

    result = runner.invoke(
        app,
        ["list", "--test-id", "1", "--limit", "10"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.get_results.assert_called_once()
    call_args = mock_client.get_results.call_args
    assert call_args[0] == (1,)
    assert call_args[1]["limit"] == "10"


def test_list_results_for_case():
    """Test listing results for a case."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.get_results_for_case.return_value = [{"id": 1, "status_id": 1}]

    result = runner.invoke(
        app,
        ["list-for-case", "--run-id", "1", "--case-id", "2", "--limit", "10"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.get_results_for_case.assert_called_once()
    call_args = mock_client.get_results_for_case.call_args
    assert call_args[0] == (1, 2)
    assert call_args[1]["limit"] == "10"


def test_add_result():
    """Test adding a result."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.add_result.return_value = {"id": 1, "status_id": 1}

    result = runner.invoke(
        app,
        ["add", "--test-id", "1", "--status-id", "1", "--comment", "Test comment"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.add_result.assert_called_once()
    call_args = mock_client.add_result.call_args
    assert call_args[0] == (1,)
    assert call_args[1]["status_id"] == "1"
    assert call_args[1]["comment"] == "Test comment"


def test_add_result_for_case():
    """Test adding a result for a case."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.add_result_for_case.return_value = {"id": 1, "status_id": 1}

    result = runner.invoke(
        app,
        [
            "add-for-case",
            "--run-id",
            "1",
            "--case-id",
            "2",
            "--status-id",
            "1",
            "--comment",
            "Test comment",
        ],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.add_result_for_case.assert_called_once()
    call_args = mock_client.add_result_for_case.call_args
    assert call_args[0] == (1, 2)
    assert call_args[1]["status_id"] == "1"
    assert call_args[1]["comment"] == "Test comment"
