from utgen.raggraph.utils import canonical_id


def test_canonical_id_with_multiple_parts():
    """
    Test canonical_id with multiple string parts.
    """
    # Arrange
    parts = ["test.py", "function", "my_function"]

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == "test.py::function::my_function"


def test_canonical_id_with_two_parts():
    """
    Test canonical_id with two string parts.
    """
    # Arrange
    parts = ["test.py", "my_function"]

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == "test.py::my_function"


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


def test_canonical_id_with_special_characters():
    """
    Test canonical_id with parts containing special characters.
    """
    # Arrange
    parts = ["test.py", "function", "my_function!"]

    # Act
    result = canonical_id(*parts)

    # Assert
    assert result == "test.py::function::my_function!"
