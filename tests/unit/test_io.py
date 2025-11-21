"""Unit tests for I/O utilities."""

import json

from testrail_cli.io import (
    filter_fields,
    output_json,
)


class TestOutputFunctions:
    """Tests for output formatting functions."""

    def test_output_json_single_item(self, capsys):
        """Test JSON output for a single item."""
        data = {"id": 1, "name": "Test"}
        output_json(data)

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result == data

    def test_output_json_list_items(self, capsys):
        """Test JSON output for a list of items."""
        data = [{"id": 1, "name": "Test1"}, {"id": 2, "name": "Test2"}]
        output_json(data)

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result == data


class TestFilterFields:
    """Tests for filter_fields function."""

    def test_filter_fields_single_item(self):
        """Test filtering fields from a single item."""
        data = {"id": 1, "name": "Test", "description": "A test"}
        fields = ["id", "name"]

        result = filter_fields(data, fields)

        assert result == {"id": 1, "name": "Test"}
        assert "description" not in result

    def test_filter_fields_list_items(self):
        """Test filtering fields from a list of items."""
        data = [
            {"id": 1, "name": "Test1", "description": "A test"},
            {"id": 2, "name": "Test2", "description": "Another test"},
        ]
        fields = ["id", "name"]

        result = filter_fields(data, fields)

        assert len(result) == 2
        assert all("description" not in item for item in result)

    def test_filter_fields_nonexistent_field(self):
        """Test filtering with non-existent field doesn't raise error."""
        data = {"id": 1, "name": "Test"}
        fields = ["id", "nonexistent"]

        result = filter_fields(data, fields)

        assert result == {"id": 1}

    def test_filter_fields_empty_list(self):
        """Test filtering with empty field list returns original data."""
        data = {"id": 1, "name": "Test"}
        fields = []

        result = filter_fields(data, fields)

        assert result == data
