from unittest.mock import Mock, patch

from utgen.validation import validate_individual_test


def test_validate_individual_test_with_passing_test():
    """
    Test validate_individual_test with a test that passes.
    """
    # Arrange
    import_code = "from math import sqrt"
    test_code = """def test_sqrt():
    assert sqrt(4) == 2"""

    # Mock subprocess.run to return success
    with patch("utgen.validation.subprocess") as mock_subprocess, patch("utgen.validation.os") as mock_os:
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.run.return_value = mock_result

        # Act
        result = validate_individual_test(import_code, test_code)

        # Assert
        assert result is True

        # Verify subprocess.run was called with correct arguments
        mock_subprocess.run.assert_called_once_with(
            ["pytest", "temp_validation.py", "-q", "--tb=no"], capture_output=True
        )

        # Verify temp file was removed
        mock_os.remove.assert_called_once_with("temp_validation.py")


def test_validate_individual_test_with_failing_test():
    """
    Test validate_individual_test with a test that fails.
    """
    # Arrange
    import_code = "from math import sqrt"
    test_code = """def test_sqrt():
    assert sqrt(4) == 3"""

    # Mock subprocess.run to return failure
    with patch("utgen.validation.subprocess") as mock_subprocess, patch("utgen.validation.os") as mock_os:
        mock_result = Mock()
        mock_result.returncode = 1
        mock_subprocess.run.return_value = mock_result

        # Act
        result = validate_individual_test(import_code, test_code)

        # Assert
        assert result is False

        # Verify subprocess.run was called with correct arguments
        mock_subprocess.run.assert_called_once_with(
            ["pytest", "temp_validation.py", "-q", "--tb=no"], capture_output=True
        )

        # Verify temp file was removed
        mock_os.remove.assert_called_once_with("temp_validation.py")


def test_validate_individual_test_with_invalid_import():
    """
    Test validate_individual_test with invalid import statements.
    """
    # Arrange
    import_code = "from non_existent_module import something"
    test_code = """def test_something():
    assert True"""

    # Mock subprocess.run to return failure
    with patch("utgen.validation.subprocess") as mock_subprocess, patch("utgen.validation.os") as mock_os:
        mock_result = Mock()
        mock_result.returncode = 1
        mock_subprocess.run.return_value = mock_result

        # Act
        result = validate_individual_test(import_code, test_code)

        # Assert
        assert result is False

        # Verify subprocess.run was called with correct arguments
        mock_subprocess.run.assert_called_once_with(
            ["pytest", "temp_validation.py", "-q", "--tb=no"], capture_output=True
        )

        # Verify temp file was removed
        mock_os.remove.assert_called_once_with("temp_validation.py")


def test_validate_individual_test_with_syntax_error():
    """
    Test validate_individual_test with code containing syntax errors.
    """
    # Arrange
    import_code = ""
    test_code = """def test_syntax_error():
    assert 1 = 1"""

    # Mock subprocess.run to return failure
    with patch("utgen.validation.subprocess") as mock_subprocess, patch("utgen.validation.os") as mock_os:
        mock_result = Mock()
        mock_result.returncode = 1
        mock_subprocess.run.return_value = mock_result

        # Act
        result = validate_individual_test(import_code, test_code)

        # Assert
        assert result is False

        # Verify subprocess.run was called with correct arguments
        mock_subprocess.run.assert_called_once_with(
            ["pytest", "temp_validation.py", "-q", "--tb=no"], capture_output=True
        )

        # Verify temp file was removed
        mock_os.remove.assert_called_once_with("temp_validation.py")
