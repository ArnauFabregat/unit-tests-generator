from unittest.mock import patch

import pytest

from utgen.raggraph.walker import iter_python_files


def test_iter_python_files_empty_directory(tmp_path):
    """
    Test edge case: empty directory should yield no files. PASS
    """
    result = list(iter_python_files(tmp_path))
    assert len(result) == 0


def test_iter_python_files_no_python_files(tmp_path):
    """
    Test edge case: directory with no .py files. PASS
    """
    (tmp_path / "module1").mkdir()
    (tmp_path / "module1" / "file1.txt").touch()
    (tmp_path / "module1" / "file2.md").touch()

    result = list(iter_python_files(tmp_path))
    assert len(result) == 0


@patch("utgen.raggraph.walker.os.walk")
def test_iter_python_files_os_walk_error(mock_walk):
    """
    Test error handling when os.walk raises an exception. PASS
    """
    mock_walk.side_effect = OSError("Permission denied")

    with pytest.raises(OSError):
        list(iter_python_files("/some/path"))
