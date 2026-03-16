import networkx as nx

from utgen.raggraph.walker import build_graph_from_directory


def test_build_graph_from_directory_with_empty_directory(tmp_path):
    """
    Test build_graph_from_directory with an empty directory.
    """
    # Arrange
    project_dir = tmp_path / "empty_project"
    project_dir.mkdir()

    # Act
    graph = build_graph_from_directory(str(project_dir))

    # Assert
    assert isinstance(graph, nx.DiGraph)
    assert len(graph.nodes) == 0
    assert len(graph.edges) == 0
