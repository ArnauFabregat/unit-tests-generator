import ast

import networkx as nx

from utgen.raggraph.utils import canonical_id, get_node_context, get_source_segment, normalize_signature


def test_get_node_context_with_basic_node():
    """
    Test get_node_context with a node that has no edges or neighbors.
    """
    # Arrange
    g = nx.DiGraph()
    node_id = "utgen/logger.py::function::disable_dependency_loggers"
    g.add_node(node_id, source="def func(): pass", type="function")

    # Act
    context = get_node_context(g, node_id)

    # Assert
    assert "### NODE INFO ###" in context
    assert f"file::type::name -> {node_id}" in context
    assert "source:" in context
    assert "def func(): pass" in context
    assert "### OUTGOING EDGES ###" not in context
    assert "### INCOMING EDGES ###" not in context
    assert "### NEIGHBOR NODE DETAILS ###" not in context


def test_get_node_context_with_outgoing_edges():
    """
    Test get_node_context with outgoing edges.
    """
    # Arrange
    g = nx.DiGraph()
    node_id = "utgen/logger.py::function::disable_dependency_loggers"
    neighbor_id = "utgen/logger.py::function::setup_logger"
    g.add_node(node_id, source="def func(): pass", type="function")
    g.add_node(neighbor_id, source="def setup(): pass", type="function")
    g.add_edge(node_id, neighbor_id, rel="calls")

    # Act
    context = get_node_context(g, node_id)

    # Assert
    assert "### OUTGOING EDGES ###" in context
    assert f"{node_id} -[calls]-> {neighbor_id}" in context
    assert "### INCOMING EDGES ###" not in context
    assert "### NEIGHBOR NODE DETAILS ###" in context
    assert f"file::type::name -> {neighbor_id}" in context


def test_get_node_context_with_incoming_edges():
    """
    Test get_node_context with incoming edges.
    """
    # Arrange
    g = nx.DiGraph()
    node_id = "utgen/logger.py::function::disable_dependency_loggers"
    neighbor_id = "utgen/logger.py::function::setup_logger"
    g.add_node(node_id, source="def func(): pass", type="function")
    g.add_node(neighbor_id, source="def setup(): pass", type="function")
    g.add_edge(neighbor_id, node_id, rel="calls")

    # Act
    context = get_node_context(g, node_id)

    # Assert
    assert "### INCOMING EDGES ###" in context
    assert f"{neighbor_id} -[calls]-> {node_id}" in context
    assert "### OUTGOING EDGES ###" not in context
    assert "### NEIGHBOR NODE DETAILS ###" in context
    assert f"file::type::name -> {neighbor_id}" in context


def test_get_node_context_with_multiple_neighbors():
    """
    Test get_node_context with multiple neighbors.
    """
    # Arrange
    g = nx.DiGraph()
    node_id = "utgen/logger.py::function::disable_dependency_loggers"
    neighbor1_id = "utgen/logger.py::function::setup_logger"
    neighbor2_id = "utgen/validation.py::function::validate_individual_test"
    g.add_node(node_id, source="def func(): pass", type="function")
    g.add_node(neighbor1_id, source="def setup(): pass", type="function")
    g.add_node(neighbor2_id, source="def validate(): pass", type="function")
    g.add_edge(node_id, neighbor1_id, rel="calls")
    g.add_edge(neighbor2_id, node_id, rel="uses")

    # Act
    context = get_node_context(g, node_id)

    # Assert
    assert "### OUTGOING EDGES ###" in context
    assert f"{node_id} -[calls]-> {neighbor1_id}" in context
    assert "### INCOMING EDGES ###" in context
    assert f"{neighbor2_id} -[uses]-> {node_id}" in context
    assert "### NEIGHBOR NODE DETAILS ###" in context
    assert f"file::type::name -> {neighbor1_id}" in context
    assert f"file::type::name -> {neighbor2_id}" in context


def test_get_node_context_with_nested_functions():
    """
    Test get_node_context with nested functions (should be ignored).
    """
    # Arrange
    g = nx.DiGraph()
    node_id = "utgen/logger.py::function::disable_dependency_loggers"
    nested_id = "utgen/logger.py::function::disable_dependency_loggers::nested_helper"
    g.add_node(node_id, source="def func(): pass", type="function")
    g.add_node(nested_id, source="def helper(): pass", type="nested_function")
    g.add_edge(node_id, nested_id, rel="contains")

    # Act
    context = get_node_context(g, node_id)

    # Assert
    assert "### OUTGOING EDGES ###" not in context
    assert "### INCOMING EDGES ###" not in context
    assert "### NEIGHBOR NODE DETAILS ###" not in context


def test_get_source_segment_with_nonexistent_file():
    """
    Test get_source_segment with a file that doesn't exist.
    """
    # Arrange
    non_existent_file = "nonexistent.py"

    # Create a dummy node (doesn't matter for this test)
    node = ast.parse("def dummy(): pass").body[0]

    # Act
    result = get_source_segment(non_existent_file, node)

    # Assert
    assert result == ""


def test_get_source_segment_with_node_without_lineno(tmp_path):
    """
    Test get_source_segment with a node that lacks line number attributes.
    """
    # Arrange
    test_file = tmp_path / "test.py"
    content = """
    def my_function():
        print('Hello')
        return True
    """
    test_file.write_text(content, encoding="utf-8")

    # Create a node without lineno/end_lineno
    class DummyNode(ast.AST):
        pass

    node = DummyNode()

    # Act
    result = get_source_segment(str(test_file), node)

    # Assert
    assert result == ""


def test_canonical_id_with_multiple_parts():
    """
    Test canonical_id with multiple string parts.
    """
    # Arrange
    parts = ["utgen", "function", "my_function"]

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == "utgen::function::my_function"


def test_canonical_id_with_single_part():
    """
    Test canonical_id with a single string part.
    """
    # Arrange
    part = "utgen"

    # Act
    result = canonical_id(part)

    # Assert
    assert result == "utgen"


def test_canonical_id_with_no_parts():
    """
    Test canonical_id with no string parts.
    """
    # Arrange

    # Act
    result = canonical_id()

    # Assert
    assert result == ""


def test_canonical_id_with_special_characters():
    """
    Test canonical_id with special characters in parts.
    """
    # Arrange
    parts = ["utgen", "function", "my_function_123", "!@#$%"]

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == "utgen::function::my_function_123::!@#$%"


def test_normalize_signature_with_basic_function():
    """
    Test normalize_signature with a basic function.
    """
    # Arrange
    source = "def my_function():\n    pass"
    tree = ast.parse(source)
    node = tree.body[0]

    # Act
    result = normalize_signature(node)

    # Assert
    assert result == "def my_function()"


def test_normalize_signature_with_arguments():
    """
    Test normalize_signature with a function that has arguments.
    """
    # Arrange
    source = "def my_function(a, b, c):\n    pass"
    tree = ast.parse(source)
    node = tree.body[0]

    # Act
    result = normalize_signature(node)

    # Assert
    assert result == "def my_function(a, b, c)"


def test_normalize_signature_with_type_annotations():
    """
    Test normalize_signature with type annotations.
    """
    # Arrange
    source = "def my_function(a: int, b: str) -> bool:\n    pass"
    tree = ast.parse(source)
    node = tree.body[0]

    # Act
    result = normalize_signature(node)

    # Assert
    assert result == "def my_function(a: int, b: str) -> bool"


def test_normalize_signature_with_positional_only_args():
    """
    Test normalize_signature with positional-only arguments.
    """
    # Arrange
    source = "def my_function(a, b, /, c):\n    pass"
    tree = ast.parse(source)
    node = tree.body[0]

    # Act
    result = normalize_signature(node)

    # Assert
    assert result == "def my_function(a, b, /, c)"


def test_normalize_signature_with_varargs():
    """
    Test normalize_signature with *args.
    """
    # Arrange
    source = "def my_function(*args):\n    pass"
    tree = ast.parse(source)
    node = tree.body[0]

    # Act
    result = normalize_signature(node)

    # Assert
    assert result == "def my_function(*args)"


def test_normalize_signature_with_kwargs():
    """
    Test normalize_signature with **kwargs.
    """
    # Arrange
    source = "def my_function(**kwargs):\n    pass"
    tree = ast.parse(source)
    node = tree.body[0]

    # Act
    result = normalize_signature(node)

    # Assert
    assert result == "def my_function(**kwargs)"


def test_normalize_signature_with_async_function():
    """
    Test normalize_signature with an async function.
    """
    # Arrange
    source = "async def my_function():\n    pass"
    tree = ast.parse(source)
    node = tree.body[0]

    # Act
    result = normalize_signature(node)

    # Assert
    assert result == "async def my_function()"


def test_normalize_signature_with_invalid_node_type():
    """
    Test normalize_signature with an invalid node type.
    """
    # Arrange
    node = ast.parse("1 + 1").body[0].value  # An expression, not a function

    # Act
    result = normalize_signature(node)

    # Assert
    assert result == ""
