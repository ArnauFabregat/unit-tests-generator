import os
from unittest.mock import MagicMock, patch


def test_validate_individual_test_with_valid_code():
    """Test validate_individual_test with valid import and test code."""
    import_code = "import pytest"
    test_code = "def test_example():\n    assert True"

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)

        from utgen.validation import validate_individual_test

        result = validate_individual_test(import_code, test_code)

        assert result is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "pytest"
        assert "temp_validation.py" in args[1]
        assert "-q" in args
        assert "--tb=no" in args

        # File should be removed after execution
        assert not os.path.exists("temp_validation.py")


def test_validate_individual_test_with_failing_test():
    """Test validate_individual_test when test fails."""
    import_code = "import pytest"
    test_code = "def test_example():\n    assert False"

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1)

        from utgen.validation import validate_individual_test

        result = validate_individual_test(import_code, test_code)

        assert result is False
        mock_run.assert_called_once()

        # File should be removed even after failure
        assert not os.path.exists("temp_validation.py")


def test_validate_individual_test_with_syntax_error():
    """Test validate_individual_test when code has syntax error."""
    import_code = "import pytest"
    test_code = "def test_example():\n    assert True\n  invalid_indentation"

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1)

        from utgen.validation import validate_individual_test

        result = validate_individual_test(import_code, test_code)

        assert result is False
        mock_run.assert_called_once()

        # File should be removed even after syntax error
        assert not os.path.exists("temp_validation.py")


def test_validate_individual_test_with_empty_code():
    """Test validate_individual_test with empty test code."""
    import_code = ""
    test_code = ""

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1)  # pytest fails with empty test

        from utgen.validation import validate_individual_test

        result = validate_individual_test(import_code, test_code)

        assert result is False
        mock_run.assert_called_once()

        # File should be removed
        assert not os.path.exists("temp_validation.py")


def test_save_and_clean_tests_with_valid_tests(tmp_path):
    """Test save_and_clean_tests with valid test data."""
    valid_tests = [
        ("import pytest", "def test_example():\n    assert True"),
        ("import sys", "def test_sys():\n    assert sys.version_info"),
    ]
    destination = tmp_path / "test_output.py"

    with patch("utgen.validation.subprocess.run") as mock_subprocess:
        from utgen.validation import save_and_clean_tests

        save_and_clean_tests(valid_tests, str(destination))

        # Check file was created
        assert destination.exists()

        # Check file content
        content = destination.read_text()
        assert "import pytest" in content
        assert "import sys" in content
        assert "def test_example()" in content
        assert "def test_sys()" in content

        # Check Ruff was called three times
        assert mock_subprocess.call_count == 3
        # First call: isort
        assert mock_subprocess.call_args_list[0][0][0] == ["ruff", "check", "--select", "I", "--fix", str(destination)]
        # Second call: linting
        assert mock_subprocess.call_args_list[1][0][0] == ["ruff", "check", "--fix", str(destination)]
        # Third call: formatting
        assert mock_subprocess.call_args_list[2][0][0] == ["ruff", "format", str(destination)]


def test_save_and_clean_tests_with_empty_list():
    """Test save_and_clean_tests with empty list returns early."""
    with (
        patch("utgen.validation.os.makedirs") as mock_makedirs,
        patch("utgen.validation.open") as mock_open,
        patch("utgen.validation.subprocess.run") as mock_subprocess,
    ):
        from utgen.validation import save_and_clean_tests

        save_and_clean_tests([], "/nonexistent/path.py")

        # Should not create directories
        mock_makedirs.assert_not_called()
        # Should not open file
        mock_open.assert_not_called()
        # Should not run Ruff
        mock_subprocess.assert_not_called()


def test_save_and_clean_tests_creates_nested_directories(tmp_path):
    """Test save_and_clean_tests creates nested directories."""
    destination = tmp_path / "deep" / "nested" / "folder" / "test.py"
    valid_tests = [("import pytest", "def test_pass(): pass")]

    with patch("utgen.validation.subprocess.run"):
        from utgen.validation import save_and_clean_tests

        save_and_clean_tests(valid_tests, str(destination))

        # Check directories were created
        assert destination.parent.exists()
        # Check file was created
        assert destination.exists()


def test_save_and_clean_tests_with_duplicate_imports(tmp_path):
    """Test save_and_clean_tests with duplicate imports."""
    valid_tests = [
        ("import pytest", "def test_1(): pass"),
        ("import pytest", "def test_2(): pass"),
        ("import sys", "def test_3(): pass"),
    ]
    destination = tmp_path / "duplicates.py"

    with patch("utgen.validation.subprocess.run"):
        from utgen.validation import save_and_clean_tests

        save_and_clean_tests(valid_tests, str(destination))

        content = destination.read_text()
        # Before Ruff formatting, duplicate imports are preserved in raw content
        import_lines = [line.strip() for line in content.split("\n") if line.strip().startswith("import")]
        assert len(import_lines) == 3
        assert import_lines.count("import pytest") == 2
        assert import_lines.count("import sys") == 1
