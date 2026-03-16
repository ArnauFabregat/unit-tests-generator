from unittest.mock import Mock

from utgen.test_generation_crew.guardrails import validate_tests_schema


def test_validate_tests_schema_with_invalid_json():
    """
    Test validate_tests_schema with invalid JSON input.
    """
    # Arrange
    invalid_json = '{\n    "tests": {\n        "test_example": {\n            "imports": ["import pytest"],\n            "code": "def test_example():\n    assert 1 + 1 == 2"\n        }\n    }\n}'

    mock_result = Mock()
    mock_result.raw = invalid_json

    # Act
    success, feedback = validate_tests_schema(mock_result)

    # Assert
    assert success is False
    assert "Invalid JSON format" in feedback


def test_validate_tests_schema_with_invalid_tests_type():
    """
    Test validate_tests_schema with 'tests' key having invalid type.
    """
    # Arrange
    json_invalid_tests = """
    {
        "tests": "not a dictionary"
    }
    """

    mock_result = Mock()
    mock_result.raw = json_invalid_tests

    # Act
    success, feedback = validate_tests_schema(mock_result)

    # Assert
    assert success is False
    assert "Missing or invalid 'tests' key" in feedback
