import pytest

from utgen.raggraph.utils import canonical_id


def test_canonical_id_with_multiple_parts():
    """
    Test canonical_id with multiple string parts.
    """
    # Arrange
    parts = ["test.py", "function", "test_function"]

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == "test.py::function::test_function"
    assert isinstance(result, str)


def test_canonical_id_with_two_parts():
    """
    Test canonical_id with two string parts.
    """
    # Arrange
    parts = ["test.py", "function"]

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == "test.py::function"
    assert isinstance(result, str)


def test_canonical_id_with_single_part():
    """
    Test canonical_id with a single string part.
    """
    # Arrange
    parts = ["test.py"]

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == "test.py"
    assert isinstance(result, str)


def test_canonical_id_with_empty_parts():
    """
    Test canonical_id with no parts provided.
    """
    # Arrange
    parts = []

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == ""
    assert isinstance(result, str)


def test_canonical_id_with_various_data_types():
    """
    Test canonical_id with various data types to verify type safety.
    """
    # Arrange
    parts = [123, None, True, 3.14]

    # Act & Assert
    with pytest.raises(TypeError):
        canonical_id(*parts)

    # Verify that only strings are accepted


def test_canonical_id_with_special_characters():
    """
    Test canonical_id with parts containing special characters.
    """
    # Arrange
    parts = ["test-file.py", "class", "MyClass@123"]

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == "test-file.py::class::MyClass@123"
    assert isinstance(result, str)


def test_canonical_id_with_unicode_characters():
    """
    Test canonical_id with parts containing unicode characters.
    """
    # Arrange
    parts = ["test.py", "function", "тестовая_функция"]

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == "test.py::function::тестовая_функция"
    assert isinstance(result, str)


def test_canonical_id_with_long_parts():
    """
    Test canonical_id with very long parts to check performance.
    """
    # Arrange
    long_str = "a" * 10000
    parts = [long_str, long_str, long_str]

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == f"{long_str}::{long_str}::{long_str}"
    assert isinstance(result, str)


def test_canonical_id_with_empty_strings():
    """
    Test canonical_id with empty string parts.
    """
    # Arrange
    parts = ["", "function", ""]

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == "::function::"
    assert isinstance(result, str)
