"""Unit tests for runs commands."""

from unittest.mock import MagicMock

from typer.testing import CliRunner

from testrail_cli.client import TestRailClient
from testrail_cli.commands.runs import app

runner = CliRunner()


def test_list_runs():
    """Test listing runs."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.get_runs.return_value = [{"id": 1, "name": "Test Run"}]

    result = runner.invoke(
        app,
        ["list", "--project-id", "1", "--limit", "10"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.get_runs.assert_called_once()
    call_args = mock_client.get_runs.call_args
    assert call_args[0] == (1,)
    assert call_args[1]["limit"] == "10"
    assert "Test Run" in result.stdout


def test_get_run():
    """Test getting a run."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.get_run.return_value = {"id": 1, "name": "Test Run"}

    result = runner.invoke(
        app,
        ["get", "1"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.get_run.assert_called_once_with(1)
    assert "Test Run" in result.stdout


def test_add_run():
    """Test adding a run."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.add_run.return_value = {"id": 1, "name": "New Run"}

    result = runner.invoke(
        app,
        ["add", "--project-id", "1", "--name", "New Run", "--description", "Desc"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.add_run.assert_called_once()
    call_args = mock_client.add_run.call_args
    assert call_args[0] == (1,)
    assert call_args[1]["name"] == "New Run"
    assert call_args[1]["description"] == "Desc"
    assert "New Run" in result.stdout


def test_update_run():
    """Test updating a run."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.update_run.return_value = {"id": 1, "name": "Updated Run"}

    result = runner.invoke(
        app,
        ["update", "1", "--name", "Updated Run"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.update_run.assert_called_once()
    call_args = mock_client.update_run.call_args
    assert call_args[0] == (1,)
    assert call_args[1]["name"] == "Updated Run"
    assert "Updated Run" in result.stdout


def test_close_run():
    """Test closing a run."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.close_run.return_value = {"id": 1, "is_completed": True}

    result = runner.invoke(
        app,
        ["close", "1"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.close_run.assert_called_once_with(1)


def test_delete_run():
    """Test deleting a run."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.delete_run.return_value = None

    # Test with confirmation
    result = runner.invoke(
        app,
        ["delete", "1"],
        input="y\n",
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.delete_run.assert_called_once_with(1)
    assert "deleted successfully" in result.stdout

    # Test with --yes flag
    mock_client.reset_mock()
    result = runner.invoke(
        app,
        ["delete", "1", "--yes"],
        obj={"client": mock_client},
    )
    assert result.exit_code == 0
    mock_client.delete_run.assert_called_once_with(1)
