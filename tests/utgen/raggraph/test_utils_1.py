import networkx as nx
import pytest

from utgen.raggraph.utils import get_node_context


def test_get_node_context_with_basic_graph():
    """
    Test get_node_context with a basic graph containing a single node.
    """
    # Arrange
    g = nx.DiGraph()

    # Create a mock node with basic attributes
    node_id = "test.py::function::test_function"
    g.add_node(
        node_id,
        source="def test_function():",
        type="function",
        signature="def test_function()",
        docstring="Test function docstring",
    )

    # Act
    result = get_node_context(g, node_id)

    # Assert
    assert "### NODE INFO ###" in result
    assert f"file::type::name -> {node_id}" in result
    assert "source:" in result
    assert "def test_function():" in result
    assert "### OUTGOING EDGES ###" not in result
    assert "### INCOMING EDGES ###" not in result
    assert "### NEIGHBOR NODE DETAILS ###" not in result


def test_get_node_context_with_outgoing_edges():
    """
    Test get_node_context with a graph containing outgoing edges.
    """
    # Arrange
    g = nx.DiGraph()

    # Create nodes
    node_id = "test.py::function::test_function"
    neighbor_id = "test.py::function::helper_function"

    g.add_node(
        node_id,
        source="def test_function():",
        type="function",
        signature="def test_function()",
        docstring="Test function docstring",
    )

    g.add_node(
        neighbor_id,
        source="def helper_function():",
        type="function",
        signature="def helper_function()",
        docstring="Helper function docstring",
    )

    # Add outgoing edge
    g.add_edge(node_id, neighbor_id, rel="calls")

    # Act
    result = get_node_context(g, node_id)

    # Assert
    assert "### OUTGOING EDGES ###" in result
    assert f"{node_id} -[calls]-> {neighbor_id}" in result
    assert "### NEIGHBOR NODE DETAILS ###" in result
    assert f"file::type::name -> {neighbor_id}" in result


def test_get_node_context_with_incoming_edges():
    """
    Test get_node_context with a graph containing incoming edges.
    """
    # Arrange
    g = nx.DiGraph()

    # Create nodes
    node_id = "test.py::function::test_function"
    caller_id = "test.py::function::caller_function"

    g.add_node(
        node_id,
        source="def test_function():",
        type="function",
        signature="def test_function()",
        docstring="Test function docstring",
    )

    g.add_node(
        caller_id,
        source="def caller_function():",
        type="function",
        signature="def caller_function()",
        docstring="Caller function docstring",
    )

    # Add incoming edge
    g.add_edge(caller_id, node_id, rel="calls")

    # Act
    result = get_node_context(g, node_id)

    # Assert
    assert "### INCOMING EDGES ###" in result
    assert f"{caller_id} -[calls]-> {node_id}" in result
    assert "### NEIGHBOR NODE DETAILS ###" in result
    assert f"file::type::name -> {caller_id}" in result


def test_get_node_context_with_nested_functions():
    """
    Test get_node_context with nested functions to verify they are skipped.
    """
    # Arrange
    g = nx.DiGraph()

    # Create nodes
    node_id = "test.py::function::test_function"
    nested_id = "test.py::function::test_function::nested_helper"

    g.add_node(
        node_id,
        source="def test_function():",
        type="function",
        signature="def test_function()",
        docstring="Test function docstring",
    )

    g.add_node(
        nested_id,
        source="def nested_helper():",
        type="nested_function",
        signature="def nested_helper()",
        docstring="Nested helper docstring",
    )

    # Add edges (both directions)
    g.add_edge(node_id, nested_id, rel="contains")
    g.add_edge(nested_id, node_id, rel="contained_by")

    # Act
    result = get_node_context(g, node_id)

    # Assert
    # Verify nested function is not included in outgoing edges
    assert "### OUTGOING EDGES ###" not in result
    # Verify nested function is not included in incoming edges
    assert "### INCOMING EDGES ###" not in result
    # Verify neighbor details doesn't include nested function
    assert "### NEIGHBOR NODE DETAILS ###" not in result


def test_get_node_context_with_multiple_neighbors():
    """
    Test get_node_context with multiple neighbors in different directions.
    """
    # Arrange
    g = nx.DiGraph()

    # Create nodes
    node_id = "test.py::function::test_function"
    neighbor1_id = "test.py::function::helper1"
    neighbor2_id = "test.py::function::helper2"

    g.add_node(
        node_id,
        source="def test_function():",
        type="function",
        signature="def test_function()",
        docstring="Test function docstring",
    )

    g.add_node(
        neighbor1_id,
        source="def helper1():",
        type="function",
        signature="def helper1()",
        docstring="Helper 1 docstring",
    )

    g.add_node(
        neighbor2_id,
        source="def helper2():",
        type="function",
        signature="def helper2()",
        docstring="Helper 2 docstring",
    )

    # Add edges
    g.add_edge(node_id, neighbor1_id, rel="calls")
    g.add_edge(neighbor2_id, node_id, rel="calls")

    # Act
    result = get_node_context(g, node_id)

    # Assert
    assert "### OUTGOING EDGES ###" in result
    assert f"{node_id} -[calls]-> {neighbor1_id}" in result
    assert "### INCOMING EDGES ###" in result
    assert f"{neighbor2_id} -[calls]-> {node_id}" in result
    assert "### NEIGHBOR NODE DETAILS ###" in result
    assert f"file::type::name -> {neighbor1_id}" in result
    assert f"file::type::name -> {neighbor2_id}" in result


def test_get_node_context_with_empty_graph():
    """
    Test get_node_context with a node that doesn't exist in the graph.
    """
    # Arrange
    g = nx.DiGraph()
    node_id = "nonexistent.py::function::test_function"

    # Act & Assert
    with pytest.raises(KeyError):
        get_node_context(g, node_id)
