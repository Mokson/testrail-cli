"""Shared test fixtures and configuration."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_testrail_client():
    """Create a mock TestRail API client."""
    client = MagicMock()
    client.base_url = "https://example.testrail.io"
    client.user = "test@example.com"
    return client


@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file."""
    config_file = tmp_path / ".testrail-cli.yaml"
    config_content = """
default:
  url: https://example.testrail.io
  username: test@example.com
  api_key: test_api_key
"""
    config_file.write_text(config_content)
    return config_file


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        "id": 1,
        "name": "Test Project",
        "announcement": "This is a test project",
        "show_announcement": True,
        "is_completed": False,
        "completed_on": None,
        "suite_mode": 1,
        "url": "https://example.testrail.io/index.php?/projects/overview/1",
    }


@pytest.fixture
def sample_suite_data():
    """Sample suite data for testing."""
    return {
        "id": 1,
        "name": "Test Suite",
        "description": "This is a test suite",
        "project_id": 1,
        "is_master": True,
        "is_baseline": False,
        "is_completed": False,
        "completed_on": None,
        "url": "https://example.testrail.io/index.php?/suites/view/1",
    }


@pytest.fixture
def sample_case_data():
    """Sample test case data for testing."""
    return {
        "id": 1,
        "title": "Test Case 1",
        "section_id": 1,
        "template_id": 1,
        "type_id": 1,
        "priority_id": 2,
        "estimate": "1m",
        "refs": "REF-123",
        "custom_steps": "Step 1\nStep 2",
        "custom_expected": "Expected result",
    }


@pytest.fixture
def sample_run_data():
    """Sample test run data for testing."""
    return {
        "id": 1,
        "suite_id": 1,
        "name": "Test Run",
        "description": "This is a test run",
        "milestone_id": None,
        "assignedto_id": None,
        "include_all": True,
        "is_completed": False,
        "completed_on": None,
        "passed_count": 0,
        "blocked_count": 0,
        "untested_count": 10,
        "retest_count": 0,
        "failed_count": 0,
        "custom_status1_count": 0,
        "project_id": 1,
        "plan_id": None,
        "url": "https://example.testrail.io/index.php?/runs/view/1",
    }
