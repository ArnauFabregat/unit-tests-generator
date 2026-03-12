"""
Test suite for iter_python_files function.
This test suite focuses on the real-world usage patterns found in the graph relationships.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import patch

# Import the function to be tested
from utgen.raggraph.walker import iter_python_files

# Test cases based on Incoming Edges analysis
def test_iter_python_files_basic_usage(tmp_path):
    """
    Test basic usage pattern found in build_graph_from_directory call.
    Verifies that the function yields .py files correctly.
    """
    # Create test directory structure
    (tmp_path / "module1").mkdir()
    (tmp_path / "module1" / "__init__.py").touch()
    (tmp_path / "module1" / "file1.py").touch()
    (tmp_path / "module2").mkdir()
    (tmp_path / "module2" / "file2.py").touch()

    # Test default behavior (skip_init=True)
    result = list(iter_python_files(tmp_path))
    assert len(result) == 2
    assert "module1/file1.py" in result
    assert "module2/file2.py" in result

    # Test skip_init=False
    result = list(iter_python_files(tmp_path, skip_init=False))
    assert len(result) == 3
    assert "module1/__init__.py" in result

def test_iter_python_files_empty_directory(tmp_path):
    """
    Test edge case: empty directory should yield no files.
    """
    result = list(iter_python_files(tmp_path))
    assert len(result) == 0

def test_iter_python_files_no_python_files(tmp_path):
    """
    Test edge case: directory with no .py files.
    """
    (tmp_path / "module1").mkdir()
    (tmp_path / "module1" / "file1.txt").touch()
    (tmp_path / "module1" / "file2.md").touch()

    result = list(iter_python_files(tmp_path))
    assert len(result) == 0

def test_iter_python_files_nested_directories(tmp_path):
    """
    Test nested directory structure handling.
    """
    (tmp_path / "level1").mkdir()
    (tmp_path / "level1" / "level2").mkdir()
    (tmp_path / "level1" / "level2" / "file.py").touch()
    (tmp_path / "level1" / "file.py").touch()

    result = list(iter_python_files(tmp_path))
    assert len(result) == 2
    assert "level1/file.py" in result
    assert "level1/level2/file.py" in result

def test_iter_python_files_with_non_standard_names(tmp_path):
    """
    Test handling of non-standard .py file names.
    """
    (tmp_path / "module1").mkdir()
    (tmp_path / "module1" / "test_file.py").touch()
    (tmp_path / "module1" / "test-file.py").touch()
    (tmp_path / "module1" / "test_file.PY").touch()

    result = list(iter_python_files(tmp_path))
    assert len(result) == 2
    assert "module1/test_file.py" in result
    assert "module1/test-file.py" in result
    assert "module1/test_file.PY" not in result  # Case-sensitive check

def test_iter_python_files_with_symlinks(tmp_path):
    """
    Test handling of symbolic links.
    """
    (tmp_path / "module1").mkdir()
    (tmp_path / "module1" / "file.py").touch()
    (tmp_path / "module2").mkdir()
    (tmp_path / "module2" / "link_to_file.py").symlink_to(tmp_path / "module1" / "file.py")

    result = list(iter_python_files(tmp_path))
    assert len(result) == 2
    assert "module1/file.py" in result
    assert "module2/link_to_file.py" in result

@patch('utgen.raggraph.walker.os.walk')
def test_iter_python_files_os_walk_error(mock_walk):
    """
    Test error handling when os.walk raises an exception.
    """
    mock_walk.side_effect = OSError("Permission denied")

    with pytest.raises(OSError):
        list(iter_python_files("/some/path"))

def test_iter_python_files_with_hidden_files(tmp_path):
    """
    Test handling of hidden files (starting with .).
    """
    (tmp_path / "module1").mkdir()
    (tmp_path / "module1" / ".hidden.py").touch()
    (tmp_path / "module1" / "visible.py").touch()

    result = list(iter_python_files(tmp_path))
    assert len(result) == 2
    assert "module1/.hidden.py" in result
    assert "module1/visible.py" in result