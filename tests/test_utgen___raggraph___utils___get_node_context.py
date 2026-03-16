import networkx as nx

from utgen.raggraph.utils import get_node_context


def test_get_node_context_with_basic_graph():
    """
    Test get_node_context with a simple graph containing one node.
    """
    # Arrange
    g = nx.DiGraph()
    node_id = "test.py::function::test_func"
    g.add_node(node_id, source="def test_func(): pass", signature="test_func()", docstring="Test function")

    # Act
    context = get_node_context(g, node_id)

    # Assert
    assert "### NODE INFO ###" in context
    assert "test.py::function::test_func" in context
    assert "source:" in context
    assert "def test_func(): pass" in context
    assert "### OUTGOING EDGES ###" not in context  # No outgoing edges
    assert "### INCOMING EDGES ###" not in context  # No incoming edges
    assert "### NEIGHBOR NODE DETAILS ###" not in context  # No neighbors


def test_get_node_context_with_outgoing_edges():
    """
    Test get_node_context with a node that has outgoing edges.
    """
    # Arrange
    g = nx.DiGraph()
    parent_id = "test.py::function::parent_func"
    child_id = "test.py::function::child_func"

    g.add_node(parent_id, source="def parent_func(): pass", signature="parent_func()", docstring="Parent function")
    g.add_node(child_id, source="def child_func(): pass", signature="child_func()", docstring="Child function")

    g.add_edge(parent_id, child_id, rel="calls")

    # Act
    context = get_node_context(g, parent_id)

    # Assert
    assert "### OUTGOING EDGES ###" in context
    assert f"{parent_id} -[calls]-> {child_id}" in context
    assert "### INCOMING EDGES ###" not in context  # No incoming edges
    assert "### NEIGHBOR NODE DETAILS ###" in context  # Should include child node details


def test_get_node_context_with_incoming_edges():
    """
    Test get_node_context with a node that has incoming edges.
    """
    # Arrange
    g = nx.DiGraph()
    caller_id = "test.py::function::caller_func"
    callee_id = "test.py::function::callee_func"

    g.add_node(caller_id, source="def caller_func(): pass", signature="caller_func()", docstring="Caller function")
    g.add_node(callee_id, source="def callee_func(): pass", signature="callee_func()", docstring="Callee function")

    g.add_edge(caller_id, callee_id, rel="calls")

    # Act
    context = get_node_context(g, callee_id)

    # Assert
    assert "### INCOMING EDGES ###" in context
    assert f"{caller_id} -[calls]-> {callee_id}" in context
    assert "### OUTGOING EDGES ###" not in context  # No outgoing edges
    assert "### NEIGHBOR NODE DETAILS ###" in context  # Should include caller node details


def test_get_node_context_with_nested_functions():
    """
    Test get_node_context with nested functions (should be excluded).
    """
    # Arrange
    g = nx.DiGraph()
    outer_id = "test.py::function::outer_func"
    nested_id = "test.py::function::nested_func"

    g.add_node(
        outer_id, source="def outer_func(): pass", signature="outer_func()", docstring="Outer function", type="function"
    )
    g.add_node(
        nested_id,
        source="def nested_func(): pass",
        signature="nested_func()",
        docstring="Nested function",
        type="nested_function",
    )

    g.add_edge(outer_id, nested_id, rel="contains")

    # Act
    context = get_node_context(g, outer_id)

    # Assert
    assert "### OUTGOING EDGES ###" not in context  # Nested function should be excluded
    assert "### NEIGHBOR NODE DETAILS ###" not in context  # Nested function should not appear in neighbors


def test_get_node_context_with_multiple_neighbors():
    """
    Test get_node_context with multiple neighbors (both incoming and outgoing).
    """
    # Arrange
    g = nx.DiGraph()

    # Create nodes
    node_a = "test.py::function::node_a"
    node_b = "test.py::function::node_b"
    node_c = "test.py::function::node_c"

    g.add_node(node_a, source="def node_a(): pass", signature="node_a()", docstring="Node A")
    g.add_node(node_b, source="def node_b(): pass", signature="node_b()", docstring="Node B")
    g.add_node(node_c, source="def node_c(): pass", signature="node_c()", docstring="Node C")

    # Create edges
    g.add_edge(node_a, node_b, rel="calls")  # A calls B
    g.add_edge(node_c, node_b, rel="uses")  # C uses B

    # Act
    context = get_node_context(g, node_b)

    # Assert
    assert "### INCOMING EDGES ###" in context
    assert f"{node_a} -[calls]-> {node_b}" in context
    assert f"{node_c} -[uses]-> {node_b}" in context
    assert "### OUTGOING EDGES ###" not in context  # Node B has no outgoing edges
    assert "### NEIGHBOR NODE DETAILS ###" in context  # Should include both A and C
