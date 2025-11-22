"""Unit tests for plans commands."""

from unittest.mock import MagicMock

from typer.testing import CliRunner

from testrail_cli.client import TestRailClient
from testrail_cli.commands.plans import app

runner = CliRunner()


def test_list_plans():
    """Test listing plans."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.get_plans.return_value = [{"id": 1, "name": "Plan 1"}]

    result = runner.invoke(
        app,
        ["list", "--project-id", "1"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.get_plans.assert_called_once_with(1)
    assert "Plan 1" in result.stdout


def test_list_plans_filters():
    """Test listing plans with filters."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.get_plans.return_value = []

    result = runner.invoke(
        app,
        [
            "list",
            "--project-id",
            "1",
            "--created-after",
            "1600000000",
            "--is-completed",
            "1",
            "--limit",
            "5",
        ],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.get_plans.assert_called_once()
    args, kwargs = mock_client.get_plans.call_args
    assert args == (1,)
    assert kwargs["created_after"] == 1600000000
    assert kwargs["is_completed"] == 1
    assert kwargs["limit"] == 5


def test_get_plan():
    """Test getting a specific plan."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.get_plan.return_value = {"id": 1, "name": "Plan 1"}

    result = runner.invoke(
        app,
        ["get", "1"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.get_plan.assert_called_once_with(1)
    assert "Plan 1" in result.stdout


def test_add_plan():
    """Test adding a plan."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.add_plan.return_value = {"id": 1, "name": "New Plan"}

    result = runner.invoke(
        app,
        ["add", "--project-id", "1", "--name", "New Plan"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.add_plan.assert_called_once_with(1, "New Plan")
    assert "New Plan" in result.stdout


def test_add_plan_optional_args():
    """Test adding a plan with optional arguments."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.add_plan.return_value = {"id": 1, "name": "New Plan"}

    result = runner.invoke(
        app,
        [
            "add",
            "--project-id",
            "1",
            "--name",
            "New Plan",
            "--description",
            "Desc",
            "--milestone-id",
            "2",
        ],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.add_plan.assert_called_once()
    args, kwargs = mock_client.add_plan.call_args
    assert args == (1, "New Plan")
    assert kwargs["description"] == "Desc"
    assert kwargs["milestone_id"] == "2"


def test_update_plan():
    """Test updating a plan."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.update_plan.return_value = {"id": 1, "name": "Updated Plan"}

    result = runner.invoke(
        app,
        ["update", "1", "--name", "Updated Plan"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.update_plan.assert_called_once_with(1, name="Updated Plan")
    assert "Updated Plan" in result.stdout


def test_close_plan():
    """Test closing a plan."""
    mock_client = MagicMock(spec=TestRailClient)
    mock_client.close_plan.return_value = {"id": 1, "is_completed": True}

    result = runner.invoke(
        app,
        ["close", "1"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.close_plan.assert_called_once_with(1)


def test_delete_plan():
    """Test deleting a plan."""
    mock_client = MagicMock(spec=TestRailClient)

    result = runner.invoke(
        app,
        ["delete", "1", "--yes"],
        obj={"client": mock_client},
    )

    assert result.exit_code == 0
    mock_client.delete_plan.assert_called_once_with(1)
    assert "deleted successfully" in result.stdout
