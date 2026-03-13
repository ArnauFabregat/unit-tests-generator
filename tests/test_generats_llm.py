from unittest.mock import patch

from utgen.raggraph.walker import iter_python_files


@patch("os.walk")
def test_iter_python_files_basic(mock_walk):
    mock_walk.return_value = [("/test/path", [], ["file1.py", "file2.py", "__init__.py"])]

    result = list(iter_python_files("/test/path"))

    assert result == ["/test/path/file1.py", "/test/path/file2.py"]
    mock_walk.assert_called_once_with("/test/path")


@patch("os.walk")
def test_iter_python_files_skip_init_false(mock_walk):
    mock_walk.return_value = [("/test/path", [], ["file1.py", "__init__.py"])]

    result = list(iter_python_files("/test/path", skip_init=False))

    assert result == ["/test/path/file1.py", "/test/path/__init__.py"]
    mock_walk.assert_called_once_with("/test/path")


@patch("os.walk")
def test_iter_python_files_no_python_files(mock_walk):
    mock_walk.return_value = [("/test/path", [], ["file1.txt", "file2.md"])]

    result = list(iter_python_files("/test/path"))

    assert result == []
    mock_walk.assert_called_once_with("/test/path")


@patch("os.walk")
def test_iter_python_files_nested_directories(mock_walk):
    mock_walk.return_value = [
        ("/test/path", ["subdir"], ["file1.py"]),
        ("/test/path/subdir", [], ["file2.py", "__init__.py"]),
    ]

    result = list(iter_python_files("/test/path"))

    assert result == ["/test/path/file1.py", "/test/path/subdir/file2.py"]
    mock_walk.assert_called_once_with("/test/path")
