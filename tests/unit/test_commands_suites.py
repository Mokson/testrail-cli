"""Unit tests for suites commands."""

from unittest.mock import MagicMock

from typer.testing import CliRunner

from testrail_cli.client import TestRailClient
from testrail_cli.commands.suites import app

runner = CliRunner()


def test_list_suites():
    """Test listing suites."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.get_suites.return_value = [{"id": 1, "name": "Suite 1"}]

    result = runner.invoke(
        app,
        ["list", "--project-id", "1"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.get_suites.assert_called_once_with(1)
    assert "Suite 1" in result.stdout


def test_get_suite():
    """Test getting a specific suite."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.get_suite.return_value = {"id": 1, "name": "Suite 1"}

    result = runner.invoke(
        app,
        ["get", "1"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.get_suite.assert_called_once_with(1)
    assert "Suite 1" in result.stdout


def test_add_suite():
    """Test adding a suite."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.add_suite.return_value = {"id": 1, "name": "New Suite"}

    result = runner.invoke(
        app,
        ["add", "--project-id", "1", "--name", "New Suite"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.add_suite.assert_called_once_with(1, "New Suite")
    assert "New Suite" in result.stdout


def test_add_suite_with_description():
    """Test adding a suite with description."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.add_suite.return_value = {"id": 1, "name": "New Suite"}

    result = runner.invoke(
        app,
        [
            "add",
            "--project-id",
            "1",
            "--name",
            "New Suite",
            "--description",
            "Desc",
        ],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.add_suite.assert_called_once_with(1, "New Suite", description="Desc")


def test_update_suite():
    """Test updating a suite."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.update_suite.return_value = {"id": 1, "name": "Updated Suite"}

    result = runner.invoke(
        app,
        ["update", "1", "--name", "Updated Suite"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.update_suite.assert_called_once_with(1, name="Updated Suite")
    assert "Updated Suite" in result.stdout


def test_delete_suite():
    """Test deleting a suite."""
    mock_client = MagicMock(spec=TestRailClient)

    result = runner.invoke(
        app,
        ["delete", "1", "--yes"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.delete_suite.assert_called_once_with(1)
    assert "deleted successfully" in result.stdout
