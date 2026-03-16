from utgen.raggraph.walker import iter_python_files


def test_iter_python_files_with_no_python_files(tmp_path):
    """
    Test iter_python_files with a directory containing no .py files.
    """
    # Arrange
    dir1 = tmp_path / "dir1"
    dir1.mkdir()

    file1 = dir1 / "file1.txt"
    file1.write_text("print('hello')")

    # Act
    result = list(iter_python_files(str(tmp_path)))

    # Assert
    assert result == []


def test_iter_python_files_with_empty_directory(tmp_path):
    """
    Test iter_python_files with an empty directory.
    """
    # Arrange
    dir1 = tmp_path / "dir1"
    dir1.mkdir()

    # Act
    result = list(iter_python_files(str(tmp_path)))

    # Assert
    assert result == []


def test_iter_python_files_with_invalid_path():
    """
    Test iter_python_files with an invalid path.
    """
    # Arrange
    invalid_path = "/this/path/does/not/exist"

    # Act
    result = list(iter_python_files(invalid_path))

    # Assert
    assert result == []
