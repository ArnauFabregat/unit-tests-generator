from unittest.mock import patch
from ast import AST
from src.raggraph.utils import unparse

# Mock for ast.unparse since it's an outgoing dependency
# We need to mock it to control its behavior and test error handling
@patch('ast.unparse')
def test_unparse_normal_case(mock_unparse):
    """
    Test normal case where ast.unparse succeeds.
    Based on Incoming Edge: normalize_signature -> unparse
    """
    # Arrange: Create a mock AST node and define mock behavior
    mock_ast_node = AST()
    expected_result = "def example() -> None:\n    pass"
    
    # Mock ast.unparse to return expected string
    mock_unparse.return_value = expected_result
    
    # Act: Call the function under test
    result = unparse(mock_ast_node)
    
    # Assert: Verify the result matches expected output
    assert result == expected_result
    mock_unparse.assert_called_once_with(mock_ast_node)

@patch('ast.unparse')
def test_unparse_exception_case(mock_unparse):
    """
    Test exception case where ast.unparse raises an exception.
    Based on Incoming Edge: normalize_signature -> unparse
    """
    # Arrange: Create a mock AST node and force exception
    mock_ast_node = AST()
    
    # Mock ast.unparse to raise an exception
    mock_unparse.side_effect = Exception("Parse error")
    
    # Act: Call the function under test
    result = unparse(mock_ast_node)
    
    # Assert: Verify the function returns empty string on exception
    assert result == ""
    mock_unparse.assert_called_once_with(mock_ast_node)

def test_unparse_with_none_input():
    """
    Test edge case with None input.
    Based on function signature allowing any input type.
    """
    # Act: Call the function with None
    result = unparse(None)
    
    # Assert: Verify the function handles None gracefully
    assert result == ""

def test_unparse_with_non_ast_input():
    """
    Test edge case with non-AST input.
    Based on function signature allowing any input type.
    """
    # Act: Call the function with a string (non-AST)
    result = unparse("not an AST node")
    
    # Assert: Verify the function handles non-AST input gracefully
    assert result == ""
