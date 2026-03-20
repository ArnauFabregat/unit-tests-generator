import os
import subprocess
from unittest.mock import patch

from utgen.validation import save_and_clean_tests, validate_individual_test


def test_validate_individual_test_with_valid_test():
    """
    Test validate_individual_test with a valid test case that should pass.
    """
    # Arrange
    import_code = "import pytest"
    test_code = """

def test_example():
    assert 1 + 1 == 2
    """

    # Act
    with patch("subprocess.run") as mock_run:
        # Simulate a successful pytest run (returncode 0)
        mock_run.return_value = subprocess.CompletedProcess(
            args=["pytest", "temp_validation.py", "-q", "--tb=no"], returncode=0, stdout=b".\n", stderr=b""
        )

        result = validate_individual_test(import_code, test_code)

    # Assert
    assert result is True
    mock_run.assert_called_once()


def test_validate_individual_test_with_invalid_test():
    """
    Test validate_individual_test with a failing test case.
    """
    # Arrange
    import_code = "import pytest"
    test_code = """

def test_example():
    assert 1 + 1 == 3
    """

    # Act
    with patch("subprocess.run") as mock_run:
        # Simulate a failing pytest run (returncode 1)
        mock_run.return_value = subprocess.CompletedProcess(
            args=["pytest", "temp_validation.py", "-q", "--tb=no"], returncode=1, stdout=b"", stderr=b""
        )

        result = validate_individual_test(import_code, test_code)

    # Assert
    assert result is False
    mock_run.assert_called_once()


def test_validate_individual_test_with_syntax_error():
    """
    Test validate_individual_test with invalid Python syntax.
    """
    # Arrange
    import_code = "import pytest"
    test_code = """

def test_example():
    assert 1 + 1 == 2
    # Missing closing quote
    print('Hello World
    """

    # Act
    with patch("subprocess.run") as mock_run:
        # Simulate a syntax error (returncode 2)
        mock_run.return_value = subprocess.CompletedProcess(
            args=["pytest", "temp_validation.py", "-q", "--tb=no"], returncode=2, stdout=b"", stderr=b""
        )

        result = validate_individual_test(import_code, test_code)

    # Assert
    assert result is False
    mock_run.assert_called_once()


def test_validate_individual_test_with_empty_code():
    """
    Test validate_individual_test with empty import and test code.
    """
    # Arrange
    import_code = ""
    test_code = ""

    # Act
    with patch("subprocess.run") as mock_run:
        # Simulate a successful pytest run (returncode 0)
        mock_run.return_value = subprocess.CompletedProcess(
            args=["pytest", "temp_validation.py", "-q", "--tb=no"], returncode=0, stdout=b".\n", stderr=b""
        )

        result = validate_individual_test(import_code, test_code)

    # Assert
    assert result is True
    mock_run.assert_called_once()


def test_save_and_clean_tests_with_valid_tests(tmp_path):
    """
    Test save_and_clean_tests with valid test data.
    """
    # Arrange
    valid_tests = [
        ("import pytest", "def test_example():", "    assert 1 + 1 == 2"),
        ("import pytest", "def test_another():", "    assert 2 + 2 == 4"),
    ]

    # Convert to list of tuples (import_string, test_body_string)
    valid_tests_formatted = [(imp, body) for imp, body, _ in valid_tests]

    destination = str(tmp_path / "tests" / "llm_generated_tests.py")

    # Mock subprocess calls for Ruff
    with patch("subprocess.run") as mock_run:
        # Mock successful Ruff operations
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "check", "--select", "I", "--fix", destination], returncode=0, stdout=b"", stderr=b""
        )

        # Act
        save_and_clean_tests(valid_tests_formatted, destination)

    # Assert
    # Verify the file was created
    assert os.path.exists(destination)

    # Verify the content structure
    with open(destination, encoding="utf-8") as f:
        content = f.read()

    # Check that imports and tests are separated by a blank line
    assert "import pytest\n\ndef test_example():" in content
    assert "def test_another():" in content

    # Verify Ruff was called three times
    assert mock_run.call_count == 3


def test_save_and_clean_tests_with_no_valid_tests():
    """
    Test save_and_clean_tests with an empty list of valid tests.
    """
    # Arrange
    valid_tests = []
    destination = "../tests/llm_generated_tests.py"

    # Mock logger.debug
    with patch("utgen.validation.logger.debug") as mock_debug:
        # Mock subprocess (should not be called)
        with patch("subprocess.run") as mock_run:
            # Act
            save_and_clean_tests(valid_tests, destination)

    # Assert
    # Verify logger.debug was called with the expected message
    mock_debug.assert_called_once_with("No valid tests available to save.")

    # Verify subprocess.run was never called
    mock_run.assert_not_called()
