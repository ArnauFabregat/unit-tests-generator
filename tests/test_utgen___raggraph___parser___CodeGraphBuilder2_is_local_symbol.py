import networkx as nx

from utgen.raggraph.parser import CodeGraphBuilder2


def test_is_local_symbol_with_existing_symbol():
    """
    Test is_local_symbol with a symbol that exists in the graph.
    """
    # Arrange
    graph = nx.DiGraph()
    graph.add_node("file::module.py::function::existing_func", name="existing_func")

    builder = CodeGraphBuilder2(code_path="src", file_path="src/module.py", graph=graph)

    # Act
    result = builder.is_local_symbol("existing_func")

    # Assert
    assert result is True
    assert builder.dst_canonical_id == "file::module.py::function::existing_func"


def test_is_local_symbol_with_nonexistent_symbol():
    """
    Test is_local_symbol with a symbol that does not exist in the graph.
    """
    # Arrange
    graph = nx.DiGraph()
    graph.add_node("file::module.py::function::other_func", name="other_func")

    builder = CodeGraphBuilder2(code_path="src", file_path="src/module.py", graph=graph)

    # Act
    result = builder.is_local_symbol("nonexistent")

    # Assert
    assert result is False
    assert builder.dst_canonical_id is None


def test_is_local_symbol_with_multiple_nodes():
    """
    Test is_local_symbol with multiple nodes in the graph.
    """
    # Arrange
    graph = nx.DiGraph()
    graph.add_node("file::module.py::function::func1", name="func1")
    graph.add_node("file::module.py::class::Class1", name="Class1")
    graph.add_node("file::module.py::function::func2", name="func2")

    builder = CodeGraphBuilder2(code_path="src", file_path="src/module.py", graph=graph)

    # Act - test with existing symbol
    result1 = builder.is_local_symbol("func1")

    # Reset for next test
    builder.dst_canonical_id = None

    # Act - test with another existing symbol
    result2 = builder.is_local_symbol("Class1")

    # Assert
    assert result1 is True
    assert result2 is True
    assert builder.dst_canonical_id == "file::module.py::class::Class1"  # Should be the last found


def test_is_local_symbol_with_empty_graph():
    """
    Test is_local_symbol with an empty graph.
    """
    # Arrange
    graph = nx.DiGraph()

    builder = CodeGraphBuilder2(code_path="src", file_path="src/module.py", graph=graph)

    # Act
    result = builder.is_local_symbol("any_symbol")

    # Assert
    assert result is False
    assert builder.dst_canonical_id is None


def test_is_local_symbol_with_case_sensitivity():
    """
    Test is_local_symbol with case-sensitive symbol matching.
    """
    # Arrange
    graph = nx.DiGraph()
    graph.add_node("file::module.py::function::MyFunction", name="MyFunction")

    builder = CodeGraphBuilder2(code_path="src", file_path="src/module.py", graph=graph)

    # Act
    result1 = builder.is_local_symbol("MyFunction")  # Exact case
    result2 = builder.is_local_symbol("myfunction")  # Different case

    # Assert
    assert result1 is True
    assert result2 is False
    assert builder.dst_canonical_id == "file::module.py::function::MyFunction"


def test_is_local_symbol_with_unicode_symbols():
    """
    Test is_local_symbol with unicode symbol names.
    """
    # Arrange
    graph = nx.DiGraph()
    graph.add_node("file::module.py::function::函数", name="函数")

    builder = CodeGraphBuilder2(code_path="src", file_path="src/module.py", graph=graph)

    # Act
    result = builder.is_local_symbol("函数")

    # Assert
    assert result is True
    assert builder.dst_canonical_id == "file::module.py::function::函数"


def test_is_local_symbol_with_special_characters():
    """
    Test is_local_symbol with symbol names containing special characters.
    """
    # Arrange
    graph = nx.DiGraph()
    graph.add_node("file::module.py::function::test_func_v2", name="test_func_v2")

    builder = CodeGraphBuilder2(code_path="src", file_path="src/module.py", graph=graph)

    # Act
    result = builder.is_local_symbol("test_func_v2")

    # Assert
    assert result is True
    assert builder.dst_canonical_id == "file::module.py::function::test_func_v2"
