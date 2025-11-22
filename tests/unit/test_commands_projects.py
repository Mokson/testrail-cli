"""Unit tests for projects commands."""

from unittest.mock import MagicMock

from typer.testing import CliRunner

from testrail_cli.client import TestRailClient
from testrail_cli.commands.projects import app

runner = CliRunner()


def test_list_projects():
    """Test listing projects."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.get_projects.return_value = [{"id": 1, "name": "Project 1"}]

    result = runner.invoke(
        app,
        ["list", "--is-completed", "0"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.get_projects.assert_called_once_with(is_completed=0)
    assert "Project 1" in result.stdout


def test_get_project():
    """Test getting a project."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.get_project.return_value = {"id": 1, "name": "Project 1"}

    result = runner.invoke(
        app,
        ["get", "1"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.get_project.assert_called_once_with(1)
    assert "Project 1" in result.stdout


def test_add_project():
    """Test adding a project."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.add_project.return_value = {"id": 1, "name": "New Project"}

    result = runner.invoke(
        app,
        ["add", "--name", "New Project", "--announcement", "Announce"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.add_project.assert_called_once()
    call_args = mock_client.add_project.call_args
    assert call_args[0] == ("New Project",)
    assert call_args[1]["announcement"] == "Announce"
    assert "New Project" in result.stdout


def test_update_project():
    """Test updating a project."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.update_project.return_value = {"id": 1, "name": "Updated Project"}

    result = runner.invoke(
        app,
        ["update", "1", "--name", "Updated Project"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.update_project.assert_called_once()
    call_args = mock_client.update_project.call_args
    assert call_args[0] == (1,)
    assert call_args[1]["name"] == "Updated Project"
    assert "Updated Project" in result.stdout


def test_delete_project():
    """Test deleting a project."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.delete_project.return_value = None

    # Test with confirmation
    result = runner.invoke(
        app,
        ["delete", "1"],
        input="y\n",
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.delete_project.assert_called_once_with(1)
    assert "deleted successfully" in result.stdout

    # Test with --yes flag
    mock_client.reset_mock()
    result = runner.invoke(
        app,
        ["delete", "1", "--yes"],
        obj={"client": mock_client},
    )
    assert result.exit_code == 0
    mock_client.delete_project.assert_called_once_with(1)
