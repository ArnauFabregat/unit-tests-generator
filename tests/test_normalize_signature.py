import ast
from unittest.mock import Mock

from utgen.raggraph.utils import normalize_signature


def test_normalize_signature_with_function_def():
    # Create a mock FunctionDef node with various argument types
    mock_node = Mock(spec=ast.FunctionDef)
    mock_node.name = "test_function"

    # Mock args with posonlyargs, args, vararg, kwonlyargs, and kwarg
    mock_args = Mock()
    mock_args.posonlyargs = [Mock(arg="a", annotation=ast.Name(id="int", ctx=ast.Load()))]
    mock_args.args = [Mock(arg="b", annotation=ast.Name(id="str", ctx=ast.Load()))]
    mock_args.vararg = Mock(arg="args", annotation=ast.Name(id="tuple", ctx=ast.Load()))
    mock_args.kwonlyargs = [Mock(arg="c", annotation=ast.Name(id="bool", ctx=ast.Load()))]
    mock_args.kwarg = Mock(arg="kwargs", annotation=ast.Name(id="dict", ctx=ast.Load()))
    mock_node.args = mock_args

    # Mock return type
    mock_node.returns = ast.Name(id="None", ctx=ast.Load())

    # Expected result
    expected_signature = "def test_function(a: int, /, b: str, *args: tuple, c: bool, **kwargs: dict) -> None"

    # Call the function
    result = normalize_signature(mock_node)

    # Assert the result
    assert result == expected_signature


def test_normalize_signature_with_async_function_def():
    # Create a mock AsyncFunctionDef node
    mock_node = Mock(spec=ast.AsyncFunctionDef)
    mock_node.name = "async_test_function"

    # Mock args with no arguments
    mock_args = Mock()
    mock_args.posonlyargs = []
    mock_args.args = []
    mock_args.vararg = None
    mock_args.kwonlyargs = []
    mock_args.kwarg = None
    mock_node.args = mock_args

    # Mock return type
    mock_node.returns = ast.Name(id="Awaitable[int]", ctx=ast.Load())

    # Expected result
    expected_signature = "def async_test_function() -> Awaitable[int]"

    # Call the function
    result = normalize_signature(mock_node)

    # Assert the result
    assert result == expected_signature


def test_normalize_signature_with_empty_args():
    # Create a mock FunctionDef node with no arguments
    mock_node = Mock(spec=ast.FunctionDef)
    mock_node.name = "empty_args_function"

    # Mock args with no arguments
    mock_args = Mock()
    mock_args.posonlyargs = []
    mock_args.args = []
    mock_args.vararg = None
    mock_args.kwonlyargs = []
    mock_args.kwarg = None
    mock_node.args = mock_args

    # Mock return type
    mock_node.returns = ast.Name(id="None", ctx=ast.Load())

    # Expected result
    expected_signature = "def empty_args_function() -> None"

    # Call the function
    result = normalize_signature(mock_node)

    # Assert the result
    assert result == expected_signature


def test_normalize_signature_with_only_positional_args():
    # Create a mock FunctionDef node with only positional arguments
    mock_node = Mock(spec=ast.FunctionDef)
    mock_node.name = "positional_args_function"

    # Mock args with only positional arguments
    mock_args = Mock()
    mock_args.posonlyargs = []
    mock_args.args = [
        Mock(arg="x", annotation=ast.Name(id="int", ctx=ast.Load())),
        Mock(arg="y", annotation=ast.Name(id="float", ctx=ast.Load())),
    ]
    mock_args.vararg = None
    mock_args.kwonlyargs = []
    mock_args.kwarg = None
    mock_node.args = mock_args

    # Mock return type
    mock_node.returns = ast.Name(id="int", ctx=ast.Load())

    # Expected result
    expected_signature = "def positional_args_function(x: int, y: float) -> int"

    # Call the function
    result = normalize_signature(mock_node)

    # Assert the result
    assert result == expected_signature


def test_normalize_signature_with_only_keyword_args():
    # Create a mock FunctionDef node with only keyword arguments
    mock_node = Mock(spec=ast.FunctionDef)
    mock_node.name = "keyword_args_function"

    # Mock args with only keyword arguments
    mock_args = Mock()
    mock_args.posonlyargs = []
    mock_args.args = []
    mock_args.vararg = None
    mock_args.kwonlyargs = [Mock(arg="z", annotation=ast.Name(id="str", ctx=ast.Load()))]
    mock_args.kwarg = None
    mock_node.args = mock_args

    # Mock return type
    mock_node.returns = ast.Name(id="str", ctx=ast.Load())

    # Expected result
    expected_signature = "def keyword_args_function(*, z: str) -> str"

    # Call the function
    result = normalize_signature(mock_node)

    # Assert the result
    assert result == expected_signature
