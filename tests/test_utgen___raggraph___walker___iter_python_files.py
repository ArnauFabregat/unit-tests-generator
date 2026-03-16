from utgen.raggraph.walker import iter_python_files


def test_iter_python_files_with_empty_directory(tmp_path):
    """
    Test iter_python_files with an empty directory.
    """
    # Arrange
    test_dir = tmp_path / "empty_project"
    test_dir.mkdir()

    # Act
    result = list(iter_python_files(str(test_dir)))

    # Assert
    assert result == []


def test_iter_python_files_with_no_python_files(tmp_path):
    """
    Test iter_python_files with a directory containing no Python files.
    """
    # Arrange
    test_dir = tmp_path / "test_project"
    test_dir.mkdir()

    # Create non-Python files
    (test_dir / "README.md").write_text("Project documentation")
    (test_dir / "config.json").write_text('{"key": "value"}')

    # Act
    result = list(iter_python_files(str(test_dir)))

    # Assert
    assert result == []
