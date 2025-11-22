"""Unit tests for milestones commands."""

from unittest.mock import MagicMock

from typer.testing import CliRunner

from testrail_cli.client import TestRailClient
from testrail_cli.commands.milestones import app

runner = CliRunner()


def test_list_milestones():
    """Test listing milestones."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.get_milestones.return_value = [{"id": 1, "name": "Milestone 1"}]

    result = runner.invoke(
        app,
        ["list", "--project-id", "1"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.get_milestones.assert_called_once_with(1)
    assert "Milestone 1" in result.stdout


def test_list_milestones_completed_filter():
    """Test listing milestones with completed filter."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.get_milestones.return_value = []

    result = runner.invoke(
        app,
        ["list", "--project-id", "1", "--is-completed", "1"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.get_milestones.assert_called_once_with(1, is_completed=1)


def test_get_milestone():
    """Test getting a specific milestone."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.get_milestone.return_value = {"id": 1, "name": "Milestone 1"}

    result = runner.invoke(
        app,
        ["get", "1"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.get_milestone.assert_called_once_with(1)
    assert "Milestone 1" in result.stdout


def test_add_milestone():
    """Test adding a milestone."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.add_milestone.return_value = {"id": 1, "name": "New Milestone"}

    result = runner.invoke(
        app,
        ["add", "--project-id", "1", "--name", "New Milestone"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.add_milestone.assert_called_once_with(1, "New Milestone")
    assert "New Milestone" in result.stdout


def test_add_milestone_optional_args():
    """Test adding a milestone with optional arguments."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.add_milestone.return_value = {"id": 1, "name": "New Milestone"}

    result = runner.invoke(
        app,
        [
            "add",
            "--project-id",
            "1",
            "--name",
            "New Milestone",
            "--description",
            "Desc",
            "--due-on",
            "1600000000",
            "--parent-id",
            "2",
            "--start-on",
            "1500000000",
        ],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.add_milestone.assert_called_once()
    args, kwargs = mock_client.add_milestone.call_args
    assert args == (1, "New Milestone")
    assert kwargs["description"] == "Desc"
    assert kwargs["due_on"] == "1600000000"
    assert kwargs["parent_id"] == "2"
    assert kwargs["start_on"] == "1500000000"


def test_update_milestone():
    """Test updating a milestone."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.update_milestone.return_value = {"id": 1, "name": "Updated Milestone"}

    result = runner.invoke(
        app,
        ["update", "1", "--name", "Updated Milestone"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.update_milestone.assert_called_once_with(1, name="Updated Milestone")
    assert "Updated Milestone" in result.stdout


def test_delete_milestone():
    """Test deleting a milestone."""
    mock_client = MagicMock(spec=TestRailClient)

    result = runner.invoke(
        app,
        ["delete", "1", "--yes"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.delete_milestone.assert_called_once_with(1)
    assert "deleted successfully" in result.stdout


def test_delete_milestone_no_confirm():
    """Test deleting a milestone without confirmation (abort)."""
    mock_client = MagicMock(spec=TestRailClient)

    result = runner.invoke(
        app,
        ["delete", "1"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 1
    mock_client.delete_milestone.assert_not_called()
