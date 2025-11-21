"""Integration tests for CLI commands."""

import pytest
from typer.testing import CliRunner
from testrail_cli.__main__ import cli


runner = CliRunner()


class TestCLIBasics:
    """Basic CLI integration tests."""

    def test_cli_help(self):
        """Test that CLI help command works."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "TestRail CLI" in result.stdout

    def test_cli_version(self):
        """Test that version command works."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0

    def test_projects_list_without_config(self):
        """Test projects list fails gracefully without config."""
        result = runner.invoke(cli, ["projects", "list"])
        assert result.exit_code != 0
        assert "required" in result.stdout.lower() or "error" in result.stdout.lower()


class TestConfigCommand:
    """Tests for config commands."""

    def test_config_init_help(self):
        """Test config init help command."""
        result = runner.invoke(cli, ["config", "init", "--help"])
        assert result.exit_code == 0
        assert "Initialize" in result.stdout or "init" in result.stdout
