from utgen.test_generation_crew.guardrails import validate_tests_schema


def test_validate_tests_schema_valid_input():
    """Test validate_tests_schema with valid input."""
    # Arrange
    valid_data = {"tests": {"test_valid": {"imports": ["import pytest"], "code": "def test_valid():\n    assert True"}}}
    import json

    raw_content = json.dumps(valid_data, indent=2)

    # Mock TaskOutput
    class MockTaskOutput:
        def __init__(self, raw):
            self.raw = raw

    # Act
    result = validate_tests_schema(MockTaskOutput(raw_content))

    # Assert
    success, output = result
    assert success is True
    assert isinstance(output, str)
    # Verify it's valid JSON and contains the original data
    parsed = json.loads(output)
    assert "tests" in parsed
    assert "test_valid" in parsed["tests"]


def test_validate_tests_schema_invalid_json():
    """Test validate_tests_schema with invalid JSON."""
    # Arrange
    raw_content = "{ invalid json"

    # Mock TaskOutput
    class MockTaskOutput:
        def __init__(self, raw):
            self.raw = raw

    # Act
    result = validate_tests_schema(MockTaskOutput(raw_content))

    # Assert
    success, feedback = result
    assert success is False
    assert "Invalid JSON format" in feedback


def test_validate_tests_schema_missing_tests_key():
    """Test validate_tests_schema with missing 'tests' key."""
    # Arrange
    raw_content = '{"foo": "bar"}'

    # Mock TaskOutput
    class MockTaskOutput:
        def __init__(self, raw):
            self.raw = raw

    # Act
    result = validate_tests_schema(MockTaskOutput(raw_content))

    # Assert
    success, feedback = result
    assert success is False
    assert "Missing or invalid 'tests' key" in feedback


def test_validate_tests_schema_test_case_errors():
    """Test validate_tests_schema with test cases containing schema and syntax errors."""
    # Arrange
    # Test case with schema error: missing 'imports'
    # Test case with syntax error: invalid Python in imports
    invalid_data = {
        "tests": {
            "test_schema_error": {
                "code": "def test_foo(): pass"  # Missing 'imports'
            },
            "test_syntax_error": {
                "imports": ["import"],  # Incomplete import statement
                "code": "def test_foo(): pass",
            },
        }
    }
    import json

    raw_content = json.dumps(invalid_data, indent=2)

    # Mock TaskOutput
    class MockTaskOutput:
        def __init__(self, raw):
            self.raw = raw

    # Act
    result = validate_tests_schema(MockTaskOutput(raw_content))

    # Assert
    success, feedback = result
    assert success is False
    assert "Test 'test_schema_error' schema error" in feedback
    assert "Test 'test_syntax_error' syntax error" in feedback
