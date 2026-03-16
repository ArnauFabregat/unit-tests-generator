import ast
from unittest.mock import Mock, patch

from utgen.raggraph.parser import CodeGraphBuilder2


def test_visit_Name_with_no_current_scope():
    """
    Test visit_Name when there is no current scope (should return early).
    """
    # Arrange
    name_node = ast.Name(id="any_name", ctx=ast.Load())

    # Mock is_local_symbol to avoid unnecessary calls
    with patch.object(CodeGraphBuilder2, "is_local_symbol") as mock_is_local_symbol:
        # Initialize the builder without current scope
        builder = CodeGraphBuilder2(code_path="src", file_path="src/module.py", graph=Mock())

        # Act
        builder.visit_Name(name_node)

        # Assert
        # Verify that is_local_symbol was NOT called
        mock_is_local_symbol.assert_not_called()


def test_visit_Name_with_call_but_nonexistent_symbol():
    """
    Test visit_Name with a CALL relationship but the symbol doesn't exist locally.
    """
    # Arrange
    # Create a Call node where the function being called is a Name node
    call_node = ast.Call(func=ast.Name(id="nonexistent_func", ctx=ast.Load()), args=[], keywords=[])

    # Set up the parent relationship
    call_node.func.parent = call_node

    # Mock is_local_symbol to return False
    with patch.object(CodeGraphBuilder2, "is_local_symbol", return_value=False) as mock_is_local_symbol:
        # Initialize the builder with context
        builder = CodeGraphBuilder2(code_path="src", file_path="src/module.py", graph=Mock())
        builder.current_scope = "src::module.py::function::caller_func"

        # Act
        builder.visit_Name(call_node.func)

        # Assert
        # Verify that is_local_symbol was called
        mock_is_local_symbol.assert_called_once_with("nonexistent_func")

        # Verify that no edge was added to the graph
        mock_graph = builder.graph
        mock_graph.add_edge.assert_not_called()


def test_visit_Name_with_reference_but_nonexistent_symbol():
    """
    Test visit_Name with a REFERENCE relationship but the symbol doesn't exist locally.
    """
    # Arrange
    name_node = ast.Name(id="nonexistent_var", ctx=ast.Load())

    # Mock is_local_symbol to return False
    with patch.object(CodeGraphBuilder2, "is_local_symbol", return_value=False) as mock_is_local_symbol:
        # Initialize the builder with context
        builder = CodeGraphBuilder2(code_path="src", file_path="src/module.py", graph=Mock())
        builder.current_scope = "src::module.py::function::current_func"

        # Act
        builder.visit_Name(name_node)

        # Assert
        # Verify that is_local_symbol was called
        mock_is_local_symbol.assert_called_once_with("nonexistent_var")

        # Verify that no edge was added to the graph
        mock_graph = builder.graph
        mock_graph.add_edge.assert_not_called()
