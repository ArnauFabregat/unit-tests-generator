from unittest.mock import patch

import networkx as nx

from utgen.raggraph.utils import get_node_context


def test_get_node_context_with_basic_node():
    """
    Test get_node_context with a basic node containing source code.
    """
    # Arrange
    graph = nx.DiGraph()
    node_id = "test_file.py::function::test_func"

    # Add node with source code
    graph.add_node(node_id, source="def test_func():\n    pass")

    with patch("utgen.raggraph.utils.canonical_id", return_value="test_file.py::function::test_func"):
        # Act
        context = get_node_context(graph, node_id)

        # Assert
        assert context.startswith("### NODE INFO ###")
        assert f"file::type::name -> {node_id}" in context
        assert "source:\n" in context
        assert "def test_func():\n    pass" in context
        assert "### OUTGOING EDGES ###" not in context
        assert "### INCOMING EDGES ###" not in context
        assert "### NEIGHBOR NODE DETAILS ###" not in context


def test_get_node_context_with_outgoing_edges():
    """
    Test get_node_context with a node that has outgoing edges.
    """
    # Arrange
    graph = nx.DiGraph()
    node_id = "test_file.py::function::test_func"

    # Add node with source code
    graph.add_node(node_id, source="def test_func():\n    pass")

    # Add neighbor node
    neighbor_id = "test_file.py::function::helper"
    graph.add_node(
        neighbor_id, type="function", name="helper", signature="def helper():", docstring="A helper function"
    )

    # Add outgoing edge
    graph.add_edge(node_id, neighbor_id, rel="calls")

    with patch("utgen.raggraph.utils.canonical_id", return_value="test_file.py::function::test_func"):
        # Act
        context = get_node_context(graph, node_id)

        # Assert
        assert "### OUTGOING EDGES ###" in context
        assert f"{node_id} -[calls]-> {neighbor_id}" in context
        assert "### NEIGHBOR NODE DETAILS ###" in context
        assert "--- Neighbor Node ---" in context
        assert f"file::type::name -> {neighbor_id}" in context
        assert "signature: def helper():" in context
        assert "docstring:\nA helper function" in context


def test_get_node_context_with_incoming_edges():
    """
    Test get_node_context with a node that has incoming edges.
    """
    # Arrange
    graph = nx.DiGraph()
    node_id = "test_file.py::function::test_func"

    # Add node with source code
    graph.add_node(node_id, source="def test_func():\n    pass")

    # Add neighbor node
    neighbor_id = "test_file.py::function::main"
    graph.add_node(neighbor_id, type="function", name="main", signature="def main():", docstring="Main function")

    # Add incoming edge
    graph.add_edge(neighbor_id, node_id, rel="calls")

    with patch("utgen.raggraph.utils.canonical_id", return_value="test_file.py::function::test_func"):
        # Act
        context = get_node_context(graph, node_id)

        # Assert
        assert "### INCOMING EDGES ###" in context
        assert f"{neighbor_id} -[calls]-> {node_id}" in context
        assert "### NEIGHBOR NODE DETAILS ###" in context
        assert "--- Neighbor Node ---" in context
        assert f"file::type::name -> {neighbor_id}" in context
        assert "signature: def main():" in context
        assert "docstring:\nMain function" in context


def test_get_node_context_with_both_edges():
    """
    Test get_node_context with a node that has both incoming and outgoing edges.
    """
    # Arrange
    graph = nx.DiGraph()
    node_id = "test_file.py::function::test_func"

    # Add node with source code
    graph.add_node(node_id, source="def test_func():\n    pass")

    # Add neighbor nodes
    neighbor1_id = "test_file.py::function::main"
    graph.add_node(neighbor1_id, type="function", name="main", signature="def main():", docstring="Main function")

    neighbor2_id = "test_file.py::function::helper"
    graph.add_node(
        neighbor2_id, type="function", name="helper", signature="def helper():", docstring="A helper function"
    )

    # Add edges
    graph.add_edge(neighbor1_id, node_id, rel="calls")  # incoming
    graph.add_edge(node_id, neighbor2_id, rel="calls")  # outgoing

    with patch("utgen.raggraph.utils.canonical_id", return_value="test_file.py::function::test_func"):
        # Act
        context = get_node_context(graph, node_id)

        # Assert
        assert "### INCOMING EDGES ###" in context
        assert f"{neighbor1_id} -[calls]-> {node_id}" in context

        assert "### OUTGOING EDGES ###" in context
        assert f"{node_id} -[calls]-> {neighbor2_id}" in context

        assert "### NEIGHBOR NODE DETAILS ###" in context
        assert context.count("--- Neighbor Node ---") == 2


def test_get_node_context_with_special_characters():
    """
    Test get_node_context with special characters in source code.
    """
    # Arrange
    graph = nx.DiGraph()
    node_id = "test_file.py::function::test_func"

    # Add node with source code containing special characters
    graph.add_node(node_id, source='def test_func():\n    print("Hello, World!")\n    return 1 + 2')

    with patch("utgen.raggraph.utils.canonical_id", return_value="test_file.py::function::test_func"):
        # Act
        context = get_node_context(graph, node_id)

        # Assert
        assert 'print("Hello, World!")' in context
        assert "return 1 + 2" in context
