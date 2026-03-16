from unittest.mock import patch

from utgen.validation import save_and_clean_tests


def test_save_and_clean_tests_with_valid_tests(tmp_path):
    """
    Test save_and_clean_tests with valid test tuples.
    """
    # Arrange
    valid_tests = [
        ("from math import sqrt", "def test_sqrt(): assert sqrt(4) == 2"),
        ("import os", "def test_os(): assert os.path.exists('/')"),
    ]
    destination = str(tmp_path / "tests" / "llm_generated_tests.py")

    # Act
    with patch("subprocess.run") as mock_subprocess:
        save_and_clean_tests(valid_tests, destination)

        # Assert
        mock_subprocess.assert_called()  # Verify subprocess was called

        # Verify file was created and contains expected content
        with open(destination) as f:
            content = f.read()
            assert "from math import sqrt" in content
            assert "def test_sqrt(): assert sqrt(4) == 2" in content
            assert "import os" in content
            assert "def test_os(): assert os.path.exists('/')" in content


def test_save_and_clean_tests_with_empty_list():
    """
    Test save_and_clean_tests with an empty list of tests.
    """
    # Arrange
    valid_tests = []
    destination = "../tests/llm_generated_tests.py"

    # Act
    with patch("subprocess.run") as mock_subprocess:
        save_and_clean_tests(valid_tests, destination)

        # Assert
        mock_subprocess.assert_not_called()  # No subprocess calls should be made
        # No assertions needed for print output


def test_save_and_clean_tests_with_single_test(tmp_path):
    """
    Test save_and_clean_tests with a single test tuple.
    """
    # Arrange
    valid_tests = [("from math import sqrt", "def test_sqrt(): assert sqrt(4) == 2")]
    destination = str(tmp_path / "tests" / "llm_generated_tests.py")

    # Act
    with patch("subprocess.run") as mock_subprocess:
        save_and_clean_tests(valid_tests, destination)

        # Assert
        mock_subprocess.assert_called()  # Verify subprocess was called

        # Verify file was created and contains expected content
        with open(destination) as f:
            content = f.read()
            assert "from math import sqrt" in content
            assert "def test_sqrt(): assert sqrt(4) == 2" in content


def test_save_and_clean_tests_with_duplicate_imports(tmp_path):
    """
    Test save_and_clean_tests with duplicate imports to verify Ruff handles them.
    """
    # Arrange
    valid_tests = [
        ("from math import sqrt", "def test_sqrt(): assert sqrt(4) == 2"),
        ("from math import sqrt", "def test_sqrt_again(): assert sqrt(9) == 3"),
    ]
    destination = str(tmp_path / "tests" / "llm_generated_tests.py")

    # Act
    with patch("subprocess.run") as mock_subprocess:
        save_and_clean_tests(valid_tests, destination)

        # Assert
        mock_subprocess.assert_called()  # Verify subprocess was called

        # Verify file was created and contains expected content
        with open(destination) as f:
            content = f.read()
            assert "from math import sqrt" in content
            assert "def test_sqrt(): assert sqrt(4) == 2" in content
            assert "def test_sqrt_again(): assert sqrt(9) == 3" in content
