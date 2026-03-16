import ast

from utgen.raggraph.utils import normalize_signature


def test_normalize_signature_with_basic_function():
    """
    Test normalize_signature with a basic function.
    """
    # Arrange
    source = """def example():
    pass"""
    tree = ast.parse(source)
    func_node = tree.body[0]

    # Act
    result = normalize_signature(func_node)

    # Assert
    assert result == "def example()"


def test_normalize_signature_with_arguments():
    """
    Test normalize_signature with a function that has arguments.
    """
    # Arrange
    source = """def example(a, b, c):
    pass"""
    tree = ast.parse(source)
    func_node = tree.body[0]

    # Act
    result = normalize_signature(func_node)

    # Assert
    assert result == "def example(a, b, c)"


def test_normalize_signature_with_type_hints():
    """
    Test normalize_signature with a function that has type hints.
    """
    # Arrange
    source = """def example(a: int, b: str) -> bool:
    pass"""
    tree = ast.parse(source)
    func_node = tree.body[0]

    # Act
    result = normalize_signature(func_node)

    # Assert
    assert result == "def example(a: int, b: str) -> bool"


def test_normalize_signature_with_async_function():
    """
    Test normalize_signature with an async function.
    """
    # Arrange
    source = """async def example():
    pass"""
    tree = ast.parse(source)
    func_node = tree.body[0]

    # Act
    result = normalize_signature(func_node)

    # Assert
    assert result == "async def example()"


def test_normalize_signature_with_positional_only_args():
    """
    Test normalize_signature with positional-only arguments.
    """
    # Arrange
    source = """def example(a, b, /, c):
    pass"""
    tree = ast.parse(source)
    func_node = tree.body[0]

    # Act
    result = normalize_signature(func_node)

    # Assert
    assert result == "def example(a, b, /, c)"


def test_normalize_signature_with_keyword_only_args():
    """
    Test normalize_signature with keyword-only arguments.
    """
    # Arrange
    source = """def example(*, a, b):
    pass"""
    tree = ast.parse(source)
    func_node = tree.body[0]

    # Act
    result = normalize_signature(func_node)

    # Assert
    assert result == "def example(*, a, b)"


def test_normalize_signature_with_invalid_node_type():
    """
    Test normalize_signature with an invalid node type.
    """
    # Arrange
    node = ast.parse("x = 10").body[0]  # This is an Assign node, not a function

    # Act
    result = normalize_signature(node)

    # Assert
    assert result == ""
