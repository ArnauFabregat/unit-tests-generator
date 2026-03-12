import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import os

# Assuming the function is in walker.py
from src.raggraph.walker import iter_python_files


class TestIterPythonFiles:
    """
    Test suite for iter_python_files function.
    """

    @pytest.fixture
    def mock_os_walk(self):
        """Fixture to mock os.walk for testing."""
        with patch('raggraph.walker.os.walk') as mock_walk:
            yield mock_walk

    @pytest.fixture
    def mock_path(self):
        """Fixture to mock Path for testing."""
        with patch('raggraph.walker.Path') as mock_path:
            yield mock_path

    def test_iter_python_files_basic(self, mock_os_walk, mock_path):
        """
        Test basic functionality of iter_python_files.
        Based on incoming edge from build_graph_from_directory,
        we expect path to be a string and skip_init to be a boolean.
        """
        # Mock os.walk to return a single directory with two files
        mock_os_walk.return_value = [
            ('/test/path', [], ['file1.py', '__init__.py', 'file2.txt'])
        ]

        # Mock Path to return a mock object with as_posix method
        mock_path_obj = MagicMock()
        mock_path_obj.as_posix.return_value = '/test/path/file1.py'
        mock_path.return_value = mock_path_obj

        # Call the function
        result = list(iter_python_files('/test/path'))

        # Verify the result
        assert result == ['/test/path/file1.py']
        mock_os_walk.assert_called_once_with('/test/path')
        mock_path.assert_called_once_with('/test/path', 'file1.py')

    def test_iter_python_files_skip_init(self, mock_os_walk, mock_path):
        """
        Test iter_python_files with skip_init=True (default).
        Should skip __init__.py files.
        """
        # Mock os.walk to return a single directory with two files
        mock_os_walk.return_value = [
            ('/test/path', [], ['__init__.py', 'file1.py'])
        ]

        # Mock Path to return a mock object with as_posix method
        mock_path_obj = MagicMock()
        mock_path_obj.as_posix.return_value = '/test/path/file1.py'
        mock_path.return_value = mock_path_obj

        # Call the function
        result = list(iter_python_files('/test/path'))

        # Verify the result
        assert result == ['/test/path/file1.py']
        mock_os_walk.assert_called_once_with('/test/path')
        mock_path.assert_called_once_with('/test/path', 'file1.py')

    def test_iter_python_files_no_skip_init(self, mock_os_walk, mock_path):
        """
        Test iter_python_files with skip_init=False.
        Should include __init__.py files.
        """
        # Mock os.walk to return a single directory with two files
        mock_os_walk.return_value = [
            ('/test/path', [], ['__init__.py', 'file1.py'])
        ]

        # Mock Path to return a mock object with as_posix method
        mock_path_obj1 = MagicMock()
        mock_path_obj1.as_posix.return_value = '/test/path/__init__.py'
        mock_path_obj2 = MagicMock()
        mock_path_obj2.as_posix.return_value = '/test/path/file1.py'
        mock_path.side_effect = [mock_path_obj1, mock_path_obj2]

        # Call the function
        result = list(iter_python_files('/test/path', skip_init=False))

        # Verify the result
        assert result == ['/test/path/__init__.py', '/test/path/file1.py']
        mock_os_walk.assert_called_once_with('/test/path')
        assert mock_path.call_count == 2

    def test_iter_python_files_no_python_files(self, mock_os_walk):
        """
        Test iter_python_files when there are no .py files.
        Should return an empty list.
        """
        # Mock os.walk to return a single directory with no .py files
        mock_os_walk.return_value = [
            ('/test/path', [], ['file1.txt', 'file2.md'])
        ]

        # Call the function
        result = list(iter_python_files('/test/path'))

        # Verify the result
        assert result == []
        mock_os_walk.assert_called_once_with('/test/path')

    def test_iter_python_files_multiple_directories(self, mock_os_walk, mock_path):
        """
        Test iter_python_files with multiple directories.
        """
        # Mock os.walk to return multiple directories with .py files
        mock_os_walk.return_value = [
            ('/test/path1', [], ['file1.py']),
            ('/test/path2', [], ['file2.py', '__init__.py']),
            ('/test/path3', [], ['file3.py'])
        ]

        # Mock Path to return a mock object with as_posix method
        mock_path_obj1 = MagicMock()
        mock_path_obj1.as_posix.return_value = '/test/path1/file1.py'
        mock_path_obj2 = MagicMock()
        mock_path_obj2.as_posix.return_value = '/test/path2/file2.py'
        mock_path_obj3 = MagicMock()
        mock_path_obj3.as_posix.return_value = '/test/path3/file3.py'
        mock_path.side_effect = [mock_path_obj1, mock_path_obj2, mock_path_obj3]

        # Call the function
        result = list(iter_python_files('/test/path'))

        # Verify the result
        assert result == ['/test/path1/file1.py', '/test/path2/file2.py', '/test/path3/file3.py']
        mock_os_walk.assert_called_once_with('/test/path')
        assert mock_path.call_count == 3