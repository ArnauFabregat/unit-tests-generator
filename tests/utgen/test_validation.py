import os
import subprocess
from unittest.mock import patch

from utgen.validation import save_and_clean_tests, validate_individual_test


def test_validate_individual_test_with_passing_test():
    """
    Test validate_individual_test with a test that passes.
    """
    # Arrange
    import_code = "import pytest"
    test_code = "def test_example():\n    assert 1 + 1 == 2"

    with (
        patch("subprocess.run") as mock_run,
        patch("os.path.exists", return_value=True) as mock_exists,
        patch("os.remove") as mock_remove,
    ):
        # Mock subprocess.run to return a successful result
        mock_run.return_value = subprocess.CompletedProcess(
            args=["pytest", "temp_validation.py", "-q", "--tb=no"], returncode=0, stdout=b".\n", stderr=b""
        )

        # Act
        result = validate_individual_test(import_code, test_code)

        # Assert
        assert result is True
        mock_run.assert_called_once_with(["pytest", "temp_validation.py", "-q", "--tb=no"], capture_output=True)
        mock_remove.assert_called_once_with("temp_validation.py")


def test_validate_individual_test_with_failing_test():
    """
    Test validate_individual_test with a test that fails.
    """
    # Arrange
    import_code = "import pytest"
    test_code = "def test_example():\n    assert 1 + 1 == 3"

    with (
        patch("subprocess.run") as mock_run,
        patch("os.path.exists", return_value=True) as mock_exists,
        patch("os.remove") as mock_remove,
    ):
        # Mock subprocess.run to return a failing result
        mock_run.return_value = subprocess.CompletedProcess(
            args=["pytest", "temp_validation.py", "-q", "--tb=no"], returncode=1, stdout=b"", stderr=b""
        )

        # Act
        result = validate_individual_test(import_code, test_code)

        # Assert
        assert result is False
        mock_run.assert_called_once_with(["pytest", "temp_validation.py", "-q", "--tb=no"], capture_output=True)
        mock_remove.assert_called_once_with("temp_validation.py")


def test_validate_individual_test_with_syntax_error():
    """
    Test validate_individual_test with invalid Python syntax.
    """
    # Arrange
    import_code = "import pytest"
    test_code = "def test_example():\n    assert 1 + 1 == 2  # Missing colon"

    with (
        patch("subprocess.run") as mock_run,
        patch("os.path.exists", return_value=True) as mock_exists,
        patch("os.remove") as mock_remove,
    ):
        # Mock subprocess.run to return a syntax error
        mock_run.return_value = subprocess.CompletedProcess(
            args=["pytest", "temp_validation.py", "-q", "--tb=no"],
            returncode=2,  # pytest returns 2 for collection errors
            stdout=b"",
            stderr=b"",
        )

        # Act
        result = validate_individual_test(import_code, test_code)

        # Assert
        assert result is False
        mock_run.assert_called_once_with(["pytest", "temp_validation.py", "-q", "--tb=no"], capture_output=True)
        mock_remove.assert_called_once_with("temp_validation.py")


def test_validate_individual_test_with_no_test_function():
    """
    Test validate_individual_test with no test function defined.
    """
    # Arrange
    import_code = "import pytest"
    test_code = "# No test function here"

    with (
        patch("subprocess.run") as mock_run,
        patch("os.path.exists", return_value=True) as mock_exists,
        patch("os.remove") as mock_remove,
    ):
        # Mock subprocess.run to return a collection error
        mock_run.return_value = subprocess.CompletedProcess(
            args=["pytest", "temp_validation.py", "-q", "--tb=no"],
            returncode=2,  # pytest returns 2 for collection errors
            stdout=b"",
            stderr=b"",
        )

        # Act
        result = validate_individual_test(import_code, test_code)

        # Assert
        assert result is False
        mock_run.assert_called_once_with(["pytest", "temp_validation.py", "-q", "--tb=no"], capture_output=True)
        mock_remove.assert_called_once_with("temp_validation.py")


def test_save_and_clean_tests_with_valid_tests(tmp_path):
    """
    Test save_and_clean_tests with valid test tuples.
    """
    # Arrange
    valid_tests = [
        ("import pytest", "def test_example():\n    assert 1 + 1 == 2"),
        ("import math", "def test_another():\n    assert math.sqrt(4) == 2"),
    ]
    destination = str(tmp_path / "tests" / "llm_generated_tests.py")

    with patch("subprocess.run") as mock_run:
        # Mock subprocess.run to avoid actually running ruff
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "check", "--select", "I", "--fix", destination], returncode=0, stdout=b"", stderr=b""
        )

        # Act
        save_and_clean_tests(valid_tests, destination)

        # Assert
        # Verify the file was created
        assert os.path.exists(destination)

        # Verify subprocess.run was called 3 times for ruff commands
        assert mock_run.call_count == 3

        # Verify the content was written correctly
        with open(destination, encoding="utf-8") as f:
            content = f.read()
            assert "import pytest" in content
            assert "import math" in content
            assert "def test_example()" in content
            assert "def test_another()" in content


def test_save_and_clean_tests_with_empty_list():
    """
    Test save_and_clean_tests with an empty list.
    """
    # Arrange
    valid_tests = []
    destination = "../tests/llm_generated_tests.py"

    with patch("subprocess.run") as mock_run:
        # Mock subprocess.run to avoid actually running ruff
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "check", "--select", "I", "--fix", destination], returncode=0, stdout=b"", stderr=b""
        )

        # Act
        save_and_clean_tests(valid_tests, destination)

        # Assert
        # Verify no file was created
        assert not os.path.exists(destination)

        # Verify subprocess.run was not called
        mock_run.assert_not_called()


def test_save_and_clean_tests_with_single_test(tmp_path):
    """
    Test save_and_clean_tests with a single test tuple.
    """
    # Arrange
    valid_tests = [("import pytest", "def test_single():\n    assert True")]
    destination = str(tmp_path / "tests" / "llm_generated_tests.py")

    with patch("subprocess.run") as mock_run:
        # Mock subprocess.run to avoid actually running ruff
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "check", "--select", "I", "--fix", destination], returncode=0, stdout=b"", stderr=b""
        )

        # Act
        save_and_clean_tests(valid_tests, destination)

        # Assert
        # Verify the file was created
        assert os.path.exists(destination)

        # Verify subprocess.run was called 3 times
        assert mock_run.call_count == 3

        # Verify the content was written correctly
        with open(destination, encoding="utf-8") as f:
            content = f.read()
            assert "import pytest" in content
            assert "def test_single()" in content


def test_save_and_clean_tests_with_duplicate_imports(tmp_path):
    """
    Test save_and_clean_tests with duplicate imports in the input.
    """
    # Arrange
    valid_tests = [
        ("import pytest", "def test_one():\n    assert 1 == 1"),
        ("import pytest", "def test_two():\n    assert 2 == 2"),
    ]
    destination = str(tmp_path / "tests" / "llm_generated_tests.py")

    with patch("subprocess.run") as mock_run:
        # Mock subprocess.run to avoid actually running ruff
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "check", "--select", "I", "--fix", destination], returncode=0, stdout=b"", stderr=b""
        )

        # Act
        save_and_clean_tests(valid_tests, destination)

        # Assert
        # Verify the file was created
        assert os.path.exists(destination)

        # Verify subprocess.run was called 3 times
        assert mock_run.call_count == 3

        # Verify the content was written correctly (duplicates should remain in this function)
        with open(destination, encoding="utf-8") as f:
            content = f.read()
            assert content.count("import pytest") == 2
