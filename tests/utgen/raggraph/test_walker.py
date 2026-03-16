import os
import tempfile
from unittest.mock import patch

import networkx as nx
import pytest

from utgen.raggraph.walker import build_graph_from_directory, iter_python_files


def test_iter_python_files_with_no_python_files():
    """
    Test iter_python_files with a directory containing no Python files.
    """
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create some non-Python files
        with open(os.path.join(tmpdir, "test1.txt"), "w") as f:
            f.write("Hello")
        with open(os.path.join(tmpdir, "test2.md"), "w") as f:
            f.write("World")

        # Act
        files = list(iter_python_files(tmpdir))

        # Assert
        assert len(files) == 0


def test_iter_python_files_with_empty_directory():
    """
    Test iter_python_files with an empty directory.
    """
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        # Act
        files = list(iter_python_files(tmpdir))

        # Assert
        assert len(files) == 0


def test_build_graph_from_directory_with_empty_directory():
    """
    Test build_graph_from_directory with an empty directory.
    """
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        # Mock the CodeGraphBuilder classes
        with patch("utgen.raggraph.walker.CodeGraphBuilder1"), patch("utgen.raggraph.walker.CodeGraphBuilder2"):
            # Act
            graph = build_graph_from_directory(tmpdir)

            # Assert
            assert isinstance(graph, nx.DiGraph)
            assert len(graph.nodes) == 0


def test_build_graph_from_directory_with_save_graph_true(tmp_path):
    """
    Test build_graph_from_directory with save_graph=True.
    """
    # Arrange
    test_file = tmp_path / "test.py"
    test_file.write_text("def my_function():\n    pass", encoding="utf-8")

    # Mock the CodeGraphBuilder classes and nx.write_graphml
    with (
        patch("utgen.raggraph.walker.CodeGraphBuilder1"),
        patch("utgen.raggraph.walker.CodeGraphBuilder2"),
        patch("networkx.write_graphml") as mock_write_graphml,
    ):
        # Act
        build_graph_from_directory(str(tmp_path), save_graph=True, save_path=str(tmp_path / "graph.graphml"))

        # Assert
        mock_write_graphml.assert_called_once()


def test_build_graph_from_directory_with_nonexistent_directory():
    """
    Test build_graph_from_directory with a non-existent directory.
    """
    # Arrange
    nonexistent_dir = "/this/directory/does/not/exist"

    # Mock os.walk to raise an exception
    with (
        patch("os.walk", side_effect=OSError()),
        patch("utgen.raggraph.walker.CodeGraphBuilder1"),
        patch("utgen.raggraph.walker.CodeGraphBuilder2"),
    ):
        # Act and Assert
        with pytest.raises(OSError):
            build_graph_from_directory(nonexistent_dir)
