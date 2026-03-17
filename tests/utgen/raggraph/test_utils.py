import ast

import pytest
from networkx import DiGraph

from utgen.raggraph.utils import canonical_id, get_node_context, get_source_segment, normalize_signature


def test_get_node_context_basic():
    """
    Test get_node_context with a simple graph containing one node.
    """
    # Arrange
    g = DiGraph()
    node_id = "file.py::class::MyClass"
    g.add_node(node_id, source="class MyClass:\n    pass", signature="MyClass", docstring="A simple class")

    # Act
    result = get_node_context(g, node_id)

    # Assert
    assert "### NODE INFO ###" in result
    assert "file::type::name -> file.py::class::MyClass" in result
    assert "source:" in result
    assert "class MyClass:" in result
    assert "### OUTGOING EDGES ###" not in result
    assert "### INCOMING EDGES ###" not in result
    assert "### NEIGHBOR NODE DETAILS ###" not in result


def test_get_node_context_with_edges():
    """
    Test get_node_context with a graph containing edges.
    """
    # Arrange
    g = DiGraph()
    node1 = "file1.py::function::func1"
    node2 = "file2.py::function::func2"
    g.add_node(node1, source="def func1():\n    pass", signature="func1", docstring="Function 1")
    g.add_node(node2, source="def func2():\n    pass", signature="func2", docstring="Function 2")
    g.add_edge(node1, node2, rel="calls")

    # Act
    result = get_node_context(g, node1)

    # Assert
    assert "### OUTGOING EDGES ###" in result
    assert "file1.py::function::func1 -[calls]-> file2.py::function::func2" in result
    assert "### INCOMING EDGES ###" not in result
    assert "### NEIGHBOR NODE DETAILS ###" in result
    assert "file2.py::function::func2" in result


def test_get_node_context_with_incoming_edges():
    """
    Test get_node_context with incoming edges.
    """
    # Arrange
    g = DiGraph()
    node1 = "file1.py::function::func1"
    node2 = "file2.py::function::func2"
    g.add_node(node1, source="def func1():\n    pass", signature="func1", docstring="Function 1")
    g.add_node(node2, source="def func2():\n    pass", signature="func2", docstring="Function 2")
    g.add_edge(node1, node2, rel="calls")

    # Act
    result = get_node_context(g, node2)

    # Assert
    assert "### INCOMING EDGES ###" in result
    assert "file1.py::function::func1 -[calls]-> file2.py::function::func2" in result
    assert "### NEIGHBOR NODE DETAILS ###" in result
    assert "file1.py::function::func1" in result


def test_get_node_context_missing_node():
    """
    Test get_node_context with a non-existent node (should handle gracefully).
    """
    # Arrange
    g = DiGraph()

    # Act & Assert
    with pytest.raises(KeyError):
        get_node_context(g, "nonexistent::node")


def test_get_source_segment_single_line(tmp_path):
    """
    Test get_source_segment with a single-line node.
    """
    # Arrange
    file_path = tmp_path / "test.py"
    source_code = """x = 42"""
    file_path.write_text(source_code, encoding="utf-8")

    tree = ast.parse(source_code)
    assign_node = next(n for n in ast.walk(tree) if isinstance(n, ast.Assign))

    # Act
    result = get_source_segment(str(file_path), assign_node)

    # Assert
    assert result == "x = 42"


def test_canonical_id_basic():
    """
    Test canonical_id with basic string components.
    """
    # Arrange
    parts = ("file.py", "class", "MyClass")

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == "file.py::class::MyClass"


def test_canonical_id_empty():
    """
    Test canonical_id with no arguments (edge case).
    """
    # Arrange

    # Act
    result = canonical_id()

    # Assert
    assert result == ""


def test_canonical_id_single_part():
    """
    Test canonical_id with a single string component.
    """
    # Arrange
    part = "file.py"

    # Act
    result = canonical_id(part)

    # Assert
    assert result == "file.py"


def test_canonical_id_multiple_parts():
    """
    Test canonical_id with multiple string components.
    """
    # Arrange
    parts = ("module", "function", "my_func", "nested")

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == "module::function::my_func::nested"


def test_normalize_signature_basic():
    """
    Test normalize_signature with a basic function.
    """
    # Arrange
    source = "def my_function():\n    pass"
    tree = ast.parse(source)
    func_node = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))

    # Act
    result = normalize_signature(func_node)

    # Assert
    assert result == "def my_function()"


def test_normalize_signature_with_args():
    """
    Test normalize_signature with positional arguments.
    """
    # Arrange
    source = "def add(a, b):\n    return a + b"
    tree = ast.parse(source)
    func_node = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))

    # Act
    result = normalize_signature(func_node)

    # Assert
    assert result == "def add(a, b)"


def test_normalize_signature_with_annotations():
    """
    Test normalize_signature with type annotations.
    """
    # Arrange
    source = 'def greet(name: str) -> str:\n    return f"Hello {name}"'
    tree = ast.parse(source)
    func_node = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))

    # Act
    result = normalize_signature(func_node)

    # Assert
    assert result == "def greet(name: str) -> str"


def test_normalize_signature_with_varargs():
    """
    Test normalize_signature with *args.
    """
    # Arrange
    source = "def sum_all(*args):\n    return sum(args)"
    tree = ast.parse(source)
    func_node = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))

    # Act
    result = normalize_signature(func_node)

    # Assert
    assert result == "def sum_all(*args)"


def test_normalize_signature_with_kwargs():
    """
    Test normalize_signature with **kwargs.
    """
    # Arrange
    source = "def create(**kwargs):\n    return kwargs"
    tree = ast.parse(source)
    func_node = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))

    # Act
    result = normalize_signature(func_node)

    # Assert
    assert result == "def create(**kwargs)"


def test_normalize_signature_with_posonly():
    """
    Test normalize_signature with positional-only arguments.
    """
    # Arrange
    source = "def divide(a, b, /):\n    return a / b"
    tree = ast.parse(source)
    func_node = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))

    # Act
    result = normalize_signature(func_node)

    # Assert
    assert result == "def divide(a, b, /)"


def test_normalize_signature_with_kwonly():
    """
    Test normalize_signature with keyword-only arguments.
    """
    # Arrange
    source = "def func(a, *, b):\n    return a + b"
    tree = ast.parse(source)
    func_node = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))

    # Act
    result = normalize_signature(func_node)

    # Assert
    assert result == "def func(a, *, b)"


def test_normalize_signature_with_mixed():
    """
    Test normalize_signature with mixed argument types.
    """
    # Arrange
    source = "def complex_func(a: int, b: str, /, *, c: float, **kwargs) -> bool:\n    return True"
    tree = ast.parse(source)
    func_node = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))

    # Act
    result = normalize_signature(func_node)

    # Assert
    assert result == "def complex_func(a: int, b: str, /, *, c: float, **kwargs) -> bool"


def test_normalize_signature_async():
    """
    Test normalize_signature with async functions.
    """
    # Arrange
    source = "async def fetch_data(url: str) -> dict:\n    return {}"
    tree = ast.parse(source)
    func_node = next(n for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef))

    # Act
    result = normalize_signature(func_node)

    # Assert
    assert result == "async def fetch_data(url: str) -> dict"


def test_normalize_signature_non_function():
    """
    Test normalize_signature with non-function AST node.
    """
    # Arrange
    class_node = ast.ClassDef(name="MyClass", bases=[], body=[], decorator_list=[])

    # Act
    result = normalize_signature(class_node)

    # Assert
    assert result == ""
