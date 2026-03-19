import ast

import networkx as nx

from utgen.raggraph.utils import canonical_id, get_node_context, get_source_segment, normalize_signature


def test_get_node_context_with_basic_graph():
    """
    Test get_node_context with a basic graph containing one node.
    """
    # Arrange
    g = nx.DiGraph()
    node_id = "utgen/validation.py::function::validate_individual_test"

    g.add_node(node_id, source="def validate_individual_test():", type="function")

    # Act
    context = get_node_context(g, node_id)

    # Assert
    assert "### NODE INFO ###" in context
    assert node_id in context
    assert "source:" in context
    assert "def validate_individual_test():" in context
    assert "### OUTGOING EDGES ###" not in context
    assert "### INCOMING EDGES ###" not in context
    assert "### NEIGHBOR NODE DETAILS ###" not in context


def test_get_node_context_with_edges():
    """
    Test get_node_context with a graph containing edges.
    """
    # Arrange
    g = nx.DiGraph()
    node_id = "utgen/validation.py::function::validate_individual_test"
    neighbor_id = "utgen/pipeline.py::function::pipeline"

    g.add_node(node_id, source="def validate_individual_test():", type="function")
    g.add_node(neighbor_id, source="def pipeline():", type="function", signature="def pipeline() -> None")

    # Add edges
    g.add_edge(neighbor_id, node_id, rel="calls")
    g.add_edge(node_id, neighbor_id, rel="uses")

    # Act
    context = get_node_context(g, node_id)

    # Assert
    assert "### OUTGOING EDGES ###" in context
    assert (
        "utgen/validation.py::function::validate_individual_test -[uses]-> utgen/pipeline.py::function::pipeline"
        in context
    )
    assert "### INCOMING EDGES ###" in context
    assert (
        "utgen/pipeline.py::function::pipeline -[calls]-> utgen/validation.py::function::validate_individual_test"
        in context
    )
    assert "### NEIGHBOR NODE DETAILS ###" in context
    assert "def pipeline() -> None" in context


def test_get_node_context_with_nested_function():
    """
    Test get_node_context with a nested function that should be excluded.
    """
    # Arrange
    g = nx.DiGraph()
    node_id = "utgen/validation.py::function::validate_individual_test"
    nested_id = "utgen/validation.py::function::validate_individual_test::nested_function::helper"

    g.add_node(node_id, source="def validate_individual_test():", type="function")
    g.add_node(nested_id, source="def helper():", type="nested_function")

    # Add edges
    g.add_edge(node_id, nested_id, rel="defines")
    g.add_edge(nested_id, node_id, rel="used_by")

    # Act
    context = get_node_context(g, node_id)

    # Assert
    assert "### OUTGOING EDGES ###" not in context
    assert "### INCOMING EDGES ###" not in context
    assert "### NEIGHBOR NODE DETAILS ###" not in context


def test_get_node_context_with_multiple_neighbors():
    """
    Test get_node_context with multiple neighbor nodes.
    """
    # Arrange
    g = nx.DiGraph()
    node_id = "utgen/validation.py::function::validate_individual_test"
    neighbor1_id = "utgen/pipeline.py::function::pipeline"
    neighbor2_id = "utgen/raggraph/utils.py::function::get_node_context"

    g.add_node(node_id, source="def validate_individual_test():", type="function")
    g.add_node(
        neighbor1_id,
        source="def pipeline():",
        type="function",
        signature="def pipeline() -> None",
        docstring="Main pipeline function",
    )
    g.add_node(
        neighbor2_id,
        source="def get_node_context():",
        type="function",
        signature="def get_node_context() -> str",
        docstring="Get node context",
    )

    # Add edges
    g.add_edge(neighbor1_id, node_id, rel="calls")
    g.add_edge(node_id, neighbor2_id, rel="uses")

    # Act
    context = get_node_context(g, node_id)

    # Assert
    assert "### NEIGHBOR NODE DETAILS ###" in context
    assert "def pipeline() -> None" in context
    assert "Main pipeline function" in context
    assert "def get_node_context() -> str" in context
    assert "Get node context" in context


def test_get_source_segment_with_invalid_file():
    """
    Test get_source_segment with a non-existent file.
    """
    # Arrange
    file_path = "/this/file/does/not/exist.py"

    # Create a simple AST node
    node = ast.FunctionDef(
        name="test_func",
        args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
        body=[],
        decorator_list=[],
        returns=None,
        type_comment=None,
    )

    # Act
    result = get_source_segment(file_path, node)

    # Assert
    assert result == ""


def test_canonical_id_with_basic_parts():
    """
    Test canonical_id with basic string parts.
    """
    # Arrange
    parts = ["file.py", "function", "my_function"]

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == "file.py::function::my_function"


def test_canonical_id_with_empty_parts():
    """
    Test canonical_id with empty parts.
    """
    # Arrange
    parts = []

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == ""


def test_canonical_id_with_single_part():
    """
    Test canonical_id with a single part.
    """
    # Arrange
    parts = ["file.py"]

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == "file.py"


def test_canonical_id_with_special_characters():
    """
    Test canonical_id with parts containing special characters.
    """
    # Arrange
    parts = ["file.py", "class", "MyClass@123"]

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == "file.py::class::MyClass@123"


def test_normalize_signature_with_basic_function():
    """
    Test normalize_signature with a basic function.
    """
    # Arrange
    node = ast.FunctionDef(
        name="example",
        args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
        body=[],
        decorator_list=[],
        returns=None,
        type_comment=None,
    )

    # Act
    result = normalize_signature(node)

    # Assert
    assert result == "def example()"


def test_normalize_signature_with_arguments():
    """
    Test normalize_signature with a function that has arguments.
    """
    # Arrange
    node = ast.FunctionDef(
        name="example",
        args=ast.arguments(
            args=[
                ast.arg(arg="a", annotation=ast.Name(id="int", ctx=ast.Load())),
                ast.arg(arg="b", annotation=ast.Name(id="str", ctx=ast.Load())),
            ],
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[],
        ),
        body=[],
        decorator_list=[],
        returns=None,
        type_comment=None,
    )

    # Act
    result = normalize_signature(node)

    # Assert
    assert result == "def example(a: int, b: str)"


def test_normalize_signature_with_return_type():
    """
    Test normalize_signature with a function that has a return type.
    """
    # Arrange
    node = ast.FunctionDef(
        name="example",
        args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
        body=[],
        decorator_list=[],
        returns=ast.Name(id="bool", ctx=ast.Load()),
        type_comment=None,
    )

    # Act
    result = normalize_signature(node)

    # Assert
    assert result == "def example() -> bool"


def test_normalize_signature_with_async_function():
    """
    Test normalize_signature with an async function.
    """
    # Arrange
    node = ast.AsyncFunctionDef(
        name="example",
        args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
        body=[],
        decorator_list=[],
        returns=None,
        type_comment=None,
    )

    # Act
    result = normalize_signature(node)

    # Assert
    assert result == "async def example()"
