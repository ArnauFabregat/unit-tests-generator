import ast

import networkx as nx
import pytest

from utgen.raggraph.utils import canonical_id, get_node_context, get_source_segment


def test_get_node_context_with_basic_graph():
    """
    Test get_node_context with a basic graph containing one node.
    """
    # Arrange
    # Create a simple graph with one node
    g = nx.DiGraph()
    node_id = "test_file.py::function::test_func"

    # Add node with basic attributes
    g.add_node(
        node_id, source="def test_func():", type="function", signature="def test_func()", docstring="Test function"
    )

    # Act
    result = get_node_context(g, node_id)

    # Assert
    # Verify that the context contains the node info section
    assert "### NODE INFO ###" in result
    assert f"file::type::name -> {node_id}" in result
    assert "source:" in result
    assert "def test_func():" in result

    # Verify that no edges sections are present (since there are no edges)
    assert "### OUTGOING EDGES ###" not in result
    assert "### INCOMING EDGES ###" not in result
    assert "### NEIGHBOR NODE DETAILS ###" not in result


def test_get_node_context_with_outgoing_edges():
    """
    Test get_node_context with a graph that has outgoing edges.
    """
    # Arrange
    # Create a graph with one node and outgoing edges
    g = nx.DiGraph()
    node_id = "test_file.py::function::test_func"

    # Add node with basic attributes
    g.add_node(
        node_id, source="def test_func():", type="function", signature="def test_func()", docstring="Test function"
    )

    # Add neighbor node
    neighbor_id = "test_file.py::function::helper_func"
    g.add_node(
        neighbor_id,
        source="def helper_func():",
        type="function",
        signature="def helper_func()",
        docstring="Helper function",
    )

    # Add outgoing edge
    g.add_edge(node_id, neighbor_id, rel="calls")

    # Act
    result = get_node_context(g, node_id)

    # Assert
    # Verify that the context contains the node info section
    assert "### NODE INFO ###" in result
    assert f"file::type::name -> {node_id}" in result

    # Verify that the source code is included
    assert "source:" in result
    assert "def test_func():" in result

    # Verify that the outgoing edges section is present
    assert "### OUTGOING EDGES ###" in result
    assert f"{node_id} -[calls]-> {neighbor_id}" in result

    # Verify that the incoming edges section is not present
    assert "### INCOMING EDGES ###" not in result

    # Verify that the neighbor node details section is present
    assert "### NEIGHBOR NODE DETAILS ###" in result
    assert f"file::type::name -> {neighbor_id}" in result
    assert "signature: def helper_func()" in result
    assert "docstring:" in result
    assert "Helper function" in result


def test_get_node_context_with_incoming_edges():
    """
    Test get_node_context with a graph that has incoming edges.
    """
    # Arrange
    # Create a graph with one node and incoming edges
    g = nx.DiGraph()
    node_id = "test_file.py::function::test_func"

    # Add node with basic attributes
    g.add_node(
        node_id, source="def test_func():", type="function", signature="def test_func()", docstring="Test function"
    )

    # Add neighbor node
    neighbor_id = "test_file.py::function::main_func"
    g.add_node(
        neighbor_id, source="def main_func():", type="function", signature="def main_func()", docstring="Main function"
    )

    # Add incoming edge
    g.add_edge(neighbor_id, node_id, rel="calls")

    # Act
    result = get_node_context(g, node_id)

    # Assert
    # Verify that the context contains the node info section
    assert "### NODE INFO ###" in result
    assert f"file::type::name -> {node_id}" in result

    # Verify that the source code is included
    assert "source:" in result
    assert "def test_func():" in result

    # Verify that the outgoing edges section is not present
    assert "### OUTGOING EDGES ###" not in result

    # Verify that the incoming edges section is present
    assert "### INCOMING EDGES ###" in result
    assert f"{neighbor_id} -[calls]-> {node_id}" in result

    # Verify that the neighbor node details section is present
    assert "### NEIGHBOR NODE DETAILS ###" in result
    assert f"file::type::name -> {neighbor_id}" in result
    assert "signature: def main_func()" in result
    assert "docstring:" in result
    assert "Main function" in result


def test_get_node_context_with_no_source_code():
    """
    Test get_node_context when the node has no source code.
    """
    # Arrange
    # Create a graph with a node that has no source code
    g = nx.DiGraph()
    node_id = "test_file.py::function::test_func"

    # Add node with no source code
    g.add_node(node_id, type="function", signature="def test_func()", docstring="Test function")

    # Act
    result = get_node_context(g, node_id)

    # Assert
    # Verify that the context contains the node info section
    assert "### NODE INFO ###" in result
    assert f"file::type::name -> {node_id}" in result

    # Verify that the source section is present but empty
    assert "source:" in result
    assert "source:" in result and result.split("source:")[1].strip() == ""

    # Verify that no edges sections are present (since there are no edges)
    assert "### OUTGOING EDGES ###" not in result
    assert "### INCOMING EDGES ###" not in result
    assert "### NEIGHBOR NODE DETAILS ###" not in result


def test_get_node_context_with_no_attributes():
    """
    Test get_node_context when the node has no attributes.
    """
    # Arrange
    # Create a graph with a node that has no attributes
    g = nx.DiGraph()
    node_id = "test_file.py::function::test_func"

    # Add node with no attributes
    g.add_node(node_id)

    # Act
    result = get_node_context(g, node_id)

    # Assert
    # Verify that the context contains the node info section
    assert "### NODE INFO ###" in result
    assert f"file::type::name -> {node_id}" in result

    # Verify that the source section is present but empty
    assert "source:" in result
    assert "source:" in result and result.split("source:")[1].strip() == ""

    # Verify that no edges sections are present (since there are no edges)
    assert "### OUTGOING EDGES ###" not in result
    assert "### INCOMING EDGES ###" not in result
    assert "### NEIGHBOR NODE DETAILS ###" not in result


def test_get_node_context_with_multiple_neighbors():
    """
    Test get_node_context with a graph that has multiple neighbor nodes.
    """
    # Arrange
    # Create a graph with multiple neighbors
    g = nx.DiGraph()
    node_id = "test_file.py::function::test_func"

    # Add main node
    g.add_node(
        node_id, source="def test_func():", type="function", signature="def test_func()", docstring="Test function"
    )

    # Add neighbor nodes
    neighbor_ids = [
        "test_file.py::function::helper1",
        "test_file.py::function::helper2",
        "test_file.py::function::main",
    ]

    for nid in neighbor_ids:
        g.add_node(
            nid,
            source=f"def {nid.split('::')[-1]}():",
            type="function",
            signature=f"def {nid.split('::')[-1]}()",
            docstring=f"{nid.split('::')[-1]} function",
        )

    # Add edges
    g.add_edge(node_id, neighbor_ids[0], rel="calls")
    g.add_edge(node_id, neighbor_ids[1], rel="calls")
    g.add_edge(neighbor_ids[2], node_id, rel="calls")

    # Act
    result = get_node_context(g, node_id)

    # Assert
    # Verify that the context contains the node info section
    assert "### NODE INFO ###" in result
    assert f"file::type::name -> {node_id}" in result

    # Verify that the source code is included
    assert "source:" in result
    assert "def test_func():" in result

    # Verify that the outgoing edges section is present
    assert "### OUTGOING EDGES ###" in result
    assert f"{node_id} -[calls]-> {neighbor_ids[0]}" in result
    assert f"{node_id} -[calls]-> {neighbor_ids[1]}" in result

    # Verify that the incoming edges section is present
    assert "### INCOMING EDGES ###" in result
    assert f"{neighbor_ids[2]} -[calls]-> {node_id}" in result

    # Verify that the neighbor node details section is present
    assert "### NEIGHBOR NODE DETAILS ###" in result

    # Verify that all neighbor nodes are included
    for nid in neighbor_ids:
        assert f"file::type::name -> {nid}" in result
        assert f"signature: def {nid.split('::')[-1]}()" in result
        assert f"{nid.split('::')[-1]} function" in result


def test_get_node_context_with_no_node_in_graph():
    """
    Test get_node_context when the node_id is not in the graph.
    """
    # Arrange
    # Create an empty graph
    g = nx.DiGraph()
    node_id = "test_file.py::function::test_func"

    # Act and Assert
    # Verify that the function raises a KeyError when the node is not found
    with pytest.raises(KeyError):
        get_node_context(g, node_id)


def test_get_source_segment_with_non_existent_file():
    """
    Test get_source_segment when the file does not exist.
    """
    # Arrange
    # Create a simple AST node
    node = ast.parse("def my_function(): pass").body[0]

    # Act
    result = get_source_segment("non_existent_file.py", node)

    # Assert
    # Verify that an empty string is returned
    assert result == ""

    # Verify that no exception is raised
    assert True


def test_canonical_id_with_basic_parts():
    """
    Test canonical_id with basic string parts.
    """
    # Arrange
    parts = ("test_file.py", "function", "my_function")

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == "test_file.py::function::my_function"


def test_canonical_id_with_empty_parts():
    """
    Test canonical_id with no parts provided.
    """
    # Arrange
    parts = ()

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == ""


def test_canonical_id_with_single_part():
    """
    Test canonical_id with a single string part.
    """
    # Arrange
    parts = ("test_file.py",)

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == "test_file.py"


def test_canonical_id_with_multiple_parts():
    """
    Test canonical_id with multiple string parts.
    """
    # Arrange
    parts = ("test_file.py", "class", "TestClass", "method", "my_method")

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == "test_file.py::class::TestClass::method::my_method"


def test_canonical_id_with_special_characters():
    """
    Test canonical_id with parts containing special characters.
    """
    # Arrange
    parts = ("test_file.py", "class", "Test_Class_123", "method", "my-method")

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == "test_file.py::class::Test_Class_123::method::my-method"


def test_canonical_id_with_empty_strings():
    """
    Test canonical_id with parts containing empty strings.
    """
    # Arrange
    parts = ("test_file.py", "", "my_function")

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == "test_file.py::::my_function"


def test_canonical_id_with_non_string_parts():
    """
    Test canonical_id with non-string parts.
    """
    # Arrange
    parts = ("test_file.py", 123, "my_function")

    # Act and Assert
    # Verify that the function raises a TypeError when non-string parts are provided
    with pytest.raises(TypeError):
        canonical_id(*parts)
