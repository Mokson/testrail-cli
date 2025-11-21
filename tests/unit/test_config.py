"""Unit tests for configuration management."""

from pathlib import Path

import pytest

from testrail_cli.config import init_config, load_config, resolve_config


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_config_with_explicit_path(self, tmp_path):
        """Test loading config from explicit path."""
        config_file = tmp_path / "test-config.yaml"
        config_file.write_text("profiles:\n  default:\n    url: https://test.testrail.io\n")

        config = load_config(str(config_file))

        assert "profiles" in config
        assert config["profiles"]["default"]["url"] == "https://test.testrail.io"

    def test_load_config_file_not_found(self):
        """Test loading config with non-existent path raises error."""
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/path.yaml")

    def test_load_config_empty_when_no_file(self, tmp_path, monkeypatch):
        """Test loading config returns empty dict when no config file exists."""
        monkeypatch.chdir(tmp_path)
        config = load_config()
        assert config == {}


class TestResolveConfig:
    """Tests for resolve_config function."""

    def test_resolve_config_with_cli_args(self):
        """Test config resolution with CLI arguments (highest priority)."""
        config = resolve_config(
            url="https://cli.testrail.io",
            email="cli@example.com",
            password="cli_password",
        )

        assert config["url"] == "https://cli.testrail.io"
        assert config["email"] == "cli@example.com"
        assert config["password"] == "cli_password"

    def test_resolve_config_with_env_vars(self, monkeypatch, tmp_path):
        """Test config resolution with environment variables."""
        monkeypatch.setenv("TESTRAIL_URL", "https://env.testrail.io")
        monkeypatch.setenv("TESTRAIL_EMAIL", "env@example.com")
        monkeypatch.setenv("TESTRAIL_PASSWORD", "env_password")
        monkeypatch.chdir(tmp_path)

        config = resolve_config()

        assert config["url"] == "https://env.testrail.io"
        assert config["email"] == "env@example.com"
        assert config["password"] == "env_password"

    def test_resolve_config_missing_url_raises_error(self, tmp_path, monkeypatch):
        """Test that missing URL raises ValueError."""
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ValueError, match="TestRail URL is required"):
            resolve_config()

    def test_resolve_config_missing_email_raises_error(self, tmp_path, monkeypatch):
        """Test that missing email raises ValueError."""
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ValueError, match="TestRail email is required"):
            resolve_config(url="https://test.testrail.io")

    def test_resolve_config_missing_password_raises_error(self, tmp_path, monkeypatch):
        """Test that missing password raises ValueError."""
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ValueError, match="TestRail password/API key is required"):
            resolve_config(url="https://test.testrail.io", email="test@example.com")

    def test_resolve_config_defaults(self, tmp_path, monkeypatch):
        """Test that defaults are applied correctly."""
        monkeypatch.chdir(tmp_path)
        config = resolve_config(
            url="https://test.testrail.io",
            email="test@example.com",
            password="test_password",
        )

        assert config["timeout"] == 30
        assert config["verify"] is True
        assert config["proxy"] is None

    def test_resolve_config_insecure_flag(self, tmp_path, monkeypatch):
        """Test that insecure flag disables SSL verification."""
        monkeypatch.chdir(tmp_path)
        config = resolve_config(
            url="https://test.testrail.io",
            email="test@example.com",
            password="test_password",
            insecure=True,
        )

        assert config["verify"] is False


class TestInitConfig:
    """Tests for init_config function."""

    def test_init_config_creates_new_file(self, tmp_path, monkeypatch):
        """Test that init_config creates a new config file."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        config_path = init_config(
            profile="default",
            url="https://test.testrail.io",
            email="test@example.com",
            password="test_password",
        )

        assert config_path.exists()
        assert config_path.name == ".testrail-cli.yaml"

    def test_init_config_updates_existing_profile(self, tmp_path, monkeypatch):
        """Test that init_config updates an existing profile."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        # Create initial config
        init_config(
            profile="default",
            url="https://test1.testrail.io",
            email="test1@example.com",
            password="password1",
        )

        # Update the profile
        init_config(
            profile="default",
            url="https://test2.testrail.io",
            email="test2@example.com",
            password="password2",
        )

        # Load and verify
        config_path = tmp_path / ".testrail-cli.yaml"
        config = load_config(str(config_path))

        assert config["profiles"]["default"]["url"] == "https://test2.testrail.io"
        assert config["profiles"]["default"]["email"] == "test2@example.com"

    def test_init_config_adds_new_profile(self, tmp_path, monkeypatch):
        """Test that init_config can add a new profile."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        # Create default profile
        init_config(
            profile="default",
            url="https://default.testrail.io",
            email="default@example.com",
            password="default_password",
        )

        # Add staging profile
        init_config(
            profile="staging",
            url="https://staging.testrail.io",
            email="staging@example.com",
            password="staging_password",
        )

        # Load and verify both profiles exist
        config_path = tmp_path / ".testrail-cli.yaml"
        config = load_config(str(config_path))

        assert "default" in config["profiles"]
        assert "staging" in config["profiles"]
        assert config["profiles"]["staging"]["url"] == "https://staging.testrail.io"
