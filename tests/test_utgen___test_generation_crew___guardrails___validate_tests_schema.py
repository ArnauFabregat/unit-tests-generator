from utgen.test_generation_crew.guardrails import validate_tests_schema


def test_validate_tests_schema_with_invalid_json_format():
    """
    Test validate_tests_schema with invalid JSON format.
    """
    # Arrange
    invalid_json = '{\n    "tests": {\n        "test_example": {\n            "imports": ["import pytest"],\n            "code": "def test_example():\nassert True"\n        }\n    }\n}'  # Missing closing brace

    class MockTaskOutput:
        def __init__(self, raw):
            self.raw = raw

    result = MockTaskOutput(invalid_json)

    # Act
    success, feedback = validate_tests_schema(result)

    # Assert
    assert success is False
    assert "Invalid JSON format" in feedback


def test_validate_tests_schema_with_invalid_test_case_schema():
    """
    Test validate_tests_schema with invalid test case schema.
    """
    # Arrange
    invalid_json = """
    {
        "tests": {
            "test_example": {
                "invalid_key": "some value"
            }
        }
    }
    """

    class MockTaskOutput:
        def __init__(self, raw):
            self.raw = raw

    result = MockTaskOutput(invalid_json)

    # Act
    success, feedback = validate_tests_schema(result)

    # Assert
    assert success is False
    assert "schema error" in feedback
