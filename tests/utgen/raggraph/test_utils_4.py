import ast

from utgen.raggraph.utils import normalize_signature


def test_normalize_signature_with_simple_function():
    """
    Test normalize_signature with a simple function definition.
    """
    # Arrange
    src = "def simple_func():\n    pass"
    module = ast.parse(src)
    node = module.body[0]  # Get the FunctionDef node

    # Act
    result = normalize_signature(node)

    # Assert
    assert result == "def simple_func()"
    assert isinstance(result, str)


def test_normalize_signature_with_arguments():
    """
    Test normalize_signature with a function having multiple arguments.
    """
    # Arrange
    src = "def func_with_args(a, b, c):\n    pass"
    module = ast.parse(src)
    node = module.body[0]  # Get the FunctionDef node

    # Act
    result = normalize_signature(node)

    # Assert
    assert result == "def func_with_args(a, b, c)"
    assert isinstance(result, str)


def test_normalize_signature_with_type_annotations():
    """
    Test normalize_signature with type annotations on arguments and return type.
    """
    # Arrange
    src = "def typed_func(a: int, b: str) -> bool:\n    pass"
    module = ast.parse(src)
    node = module.body[0]  # Get the FunctionDef node

    # Act
    result = normalize_signature(node)

    # Assert
    assert result == "def typed_func(a: int, b: str) -> bool"
    assert isinstance(result, str)


def test_normalize_signature_with_varargs_and_kwargs():
    """
    Test normalize_signature with *args and **kwargs.
    """
    # Arrange
    src = "def func_with_varargs(*args, **kwargs):\n    pass"
    module = ast.parse(src)
    node = module.body[0]  # Get the FunctionDef node

    # Act
    result = normalize_signature(node)

    # Assert
    assert result == "def func_with_varargs(*args, **kwargs)"
    assert isinstance(result, str)


def test_normalize_signature_with_positional_only_arguments():
    """
    Test normalize_signature with positional-only arguments (Python 3.8+ syntax).
    """
    # Arrange
    src = "def posonly_func(a, b, /, c):\n    pass"
    module = ast.parse(src)
    node = module.body[0]  # Get the FunctionDef node

    # Act
    result = normalize_signature(node)

    # Assert
    assert result == "def posonly_func(a, b, /, c)"
    assert isinstance(result, str)


def test_normalize_signature_with_async_function():
    """
    Test normalize_signature with an async function.
    """
    # Arrange
    src = "async def async_func(a, b):\n    pass"
    module = ast.parse(src)
    node = module.body[0]  # Get the AsyncFunctionDef node

    # Act
    result = normalize_signature(node)

    # Assert
    assert result == "async def async_func(a, b)"
    assert isinstance(result, str)


def test_normalize_signature_with_non_function_node():
    """
    Test normalize_signature with a non-function AST node.
    """
    # Arrange
    src = "class TestClass:\n    pass"
    module = ast.parse(src)
    node = module.body[0]  # Get the ClassDef node

    # Act
    result = normalize_signature(node)

    # Assert
    assert result == ""
    assert isinstance(result, str)


def test_normalize_signature_with_complex_annotations():
    """
    Test normalize_signature with complex type annotations.
    """
    # Arrange
    src = "def complex_func(a: List[int], b: Dict[str, Any]) -> Tuple[int, str]:\n    pass"
    module = ast.parse(src)
    node = module.body[0]  # Get the FunctionDef node

    # Act
    result = normalize_signature(node)

    # Assert
    assert "def complex_func(a: List[int], b: Dict[str, Any]) -> Tuple[int, str]" in result
    assert isinstance(result, str)


def test_normalize_signature_with_no_arguments_and_return_type():
    """
    Test normalize_signature with no arguments but with return type annotation.
    """
    # Arrange
    src = "def no_args_func() -> None:\n    pass"
    module = ast.parse(src)
    node = module.body[0]  # Get the FunctionDef node

    # Act
    result = normalize_signature(node)

    # Assert
    assert result == "def no_args_func() -> None"
    assert isinstance(result, str)
