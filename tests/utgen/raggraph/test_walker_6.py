from unittest.mock import patch

import networkx as nx

from utgen.raggraph.walker import build_graph_from_directory


def test_build_graph_from_directory_with_save_graph(tmp_path):
    """
    Test build_graph_from_directory with save_graph=True.
    """
    # Arrange - Create a temporary directory structure
    dir1 = tmp_path / "project"
    dir1.mkdir()

    file1 = dir1 / "module1.py"
    file1.write_text("""
def func1():
    pass
""")

    save_path = tmp_path / "graph.graphml"

    # Mock the CodeGraphBuilder1 and CodeGraphBuilder2 classes
    with (
        patch("utgen.raggraph.parser.CodeGraphBuilder1") as mock_builder1,
        patch("utgen.raggraph.parser.CodeGraphBuilder2") as mock_builder2,
        patch("networkx.write_graphml") as mock_write_graphml,
    ):
        # Act
        graph = build_graph_from_directory(str(tmp_path), save_graph=True, save_path=str(save_path))

        # Assert
        assert isinstance(graph, nx.DiGraph)
        mock_write_graphml.assert_called_once_with(graph, str(save_path))


def test_build_graph_from_directory_with_skip_init(tmp_path):
    """
    Test build_graph_from_directory with skip_init=True (default).
    """
    # Arrange - Create a temporary directory structure
    dir1 = tmp_path / "project"
    dir1.mkdir()

    init_file = dir1 / "__init__.py"
    init_file.write_text("print('init')")

    file1 = dir1 / "module1.py"
    file1.write_text("""
def func1():
    pass
""")

    # Mock the iter_python_files function to verify it's called with skip_init=True
    with patch("utgen.raggraph.walker.iter_python_files") as mock_iter_files:
        mock_iter_files.return_value = [str(file1)]

        # Act
        graph = build_graph_from_directory(str(tmp_path))

        # Assert
        mock_iter_files.assert_called_with(str(tmp_path), skip_init=True)


def test_build_graph_from_directory_with_no_skip_init(tmp_path):
    """
    Test build_graph_from_directory with skip_init=False.
    """
    # Arrange - Create a temporary directory structure
    dir1 = tmp_path / "project"
    dir1.mkdir()

    init_file = dir1 / "__init__.py"
    init_file.write_text("print('init')")

    file1 = dir1 / "module1.py"
    file1.write_text("""
def func1():
    pass
""")

    # Mock the iter_python_files function to verify it's called with skip_init=False
    with patch("utgen.raggraph.walker.iter_python_files") as mock_iter_files:
        mock_iter_files.return_value = [str(init_file), str(file1)]

        # Act
        graph = build_graph_from_directory(str(tmp_path), skip_init=False)

        # Assert
        mock_iter_files.assert_called_with(str(tmp_path), skip_init=False)


def test_build_graph_from_directory_with_empty_directory(tmp_path):
    """
    Test build_graph_from_directory with an empty directory.
    """
    # Arrange
    dir1 = tmp_path / "project"
    dir1.mkdir()

    # Mock the iter_python_files to return an empty list
    with patch("utgen.raggraph.walker.iter_python_files") as mock_iter_files:
        mock_iter_files.return_value = []

        # Act
        graph = build_graph_from_directory(str(tmp_path))

        # Assert
        assert isinstance(graph, nx.DiGraph)
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0


def test_build_graph_from_directory_with_invalid_code_path():
    """
    Test build_graph_from_directory with an invalid code path.
    """
    # Arrange
    invalid_path = "/this/path/does/not/exist"

    # Mock the iter_python_files to handle invalid paths
    with patch("utgen.raggraph.walker.iter_python_files") as mock_iter_files:
        mock_iter_files.return_value = []

        # Act
        graph = build_graph_from_directory(invalid_path)

        # Assert
        assert isinstance(graph, nx.DiGraph)
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
