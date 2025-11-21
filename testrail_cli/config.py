"""Configuration management for TestRail CLI."""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any

import yaml


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from file.

    Searches for config in:
    1. Provided path (if given)
    2. ./.testrail-cli.yaml (repo-local)
    3. ~/.testrail-cli.yaml (user home)

    Returns empty dict if no config found.
    """
    if config_path:
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        return _read_yaml(path)

    # Try repo-local first
    local_config = Path(".testrail-cli.yaml")
    if local_config.exists():
        return _read_yaml(local_config)

    # Try user home
    home_config = Path.home() / ".testrail-cli.yaml"
    if home_config.exists():
        return _read_yaml(home_config)

    return {}


def _read_yaml(path: Path) -> Dict[str, Any]:
    """Read and parse YAML config file."""
    try:
        with open(path, "r") as f:
            config = yaml.safe_load(f) or {}

        # Check file permissions on POSIX systems
        # Note: Windows users should ensure config file is not shared or accessible to other users
        # through NTFS permissions or folder sharing settings
        if sys.platform != "win32":
            mode = path.stat().st_mode & 0o777
            if mode != 0o600:
                print(
                    f"Warning: Config file {path} has permissions {oct(mode)}, should be 600",
                    file=sys.stderr,
                )
        else:
            # Windows: Config file security relies on NTFS permissions
            print(
                f"Info: On Windows, ensure {path} is only accessible to your user account",
                file=sys.stderr,
            )

        return config
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in config file {path}: {e}")


def resolve_config(
    profile: Optional[str] = None,
    url: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
    timeout: Optional[int] = None,
    proxy: Optional[str] = None,
    insecure: bool = False,
    config_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Resolve final configuration from precedence: CLI flags > env vars > config file.

    Returns dict with keys: url, email, password, timeout, proxy, verify
    """
    config = load_config(config_path)

    # Extract profile if specified
    profile_name = profile or "default"
    profile_config = config.get("profiles", {}).get(profile_name, {})

    # Precedence: CLI > env > profile/config > defaults
    resolved = {
        "url": url or os.getenv("TESTRAIL_URL") or profile_config.get("url"),
        "email": email or os.getenv("TESTRAIL_EMAIL") or profile_config.get("email"),
        "password": password
        or os.getenv("TESTRAIL_PASSWORD")
        or profile_config.get("password"),
        "timeout": timeout or profile_config.get("timeout") or 30,
        "proxy": proxy or profile_config.get("proxy"),
        "verify": not insecure and profile_config.get("verify", True),
    }

    # Validate required fields
    if not resolved["url"]:
        raise ValueError(
            "TestRail URL is required (via --url, TESTRAIL_URL env, or config file)"
        )
    if not resolved["email"]:
        raise ValueError(
            "TestRail email is required (via --email, TESTRAIL_EMAIL env, or config file)"
        )
    if not resolved["password"]:
        raise ValueError(
            "TestRail password/API key is required (via --password, TESTRAIL_PASSWORD env, or config file)"
        )

    return resolved


def init_config(
    profile: str = "default", url: str = "", email: str = "", password: str = ""
) -> Path:
    """Initialize or update config file with provided credentials.

    Creates ~/.testrail-cli.yaml with mode 600 and stores the profile.
    """
    config_path = Path.home() / ".testrail-cli.yaml"

    # Load existing config if present
    existing_config = {}
    if config_path.exists():
        with open(config_path, "r") as f:
            existing_config = yaml.safe_load(f) or {}

    # Ensure profiles key exists
    if "profiles" not in existing_config:
        existing_config["profiles"] = {}

    # Update profile
    existing_config["profiles"][profile] = {
        "url": url,
        "email": email,
        "password": password,
        "verify": True,
        "timeout": 30,
    }

    # Write config atomically using temp file
    config_dir = config_path.parent
    with tempfile.NamedTemporaryFile(mode='w', dir=config_dir, delete=False, suffix='.tmp') as f:
        temp_path = Path(f.name)
        yaml.safe_dump(existing_config, f, default_flow_style=False, sort_keys=False)

    # Set permissions on temp file before moving (POSIX only)
    if sys.platform != "win32":
        temp_path.chmod(0o600)

    # Atomic replace
    shutil.move(str(temp_path), str(config_path))

    return config_path
