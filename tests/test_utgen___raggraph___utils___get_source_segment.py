import ast

from utgen.raggraph.utils import get_source_segment


def test_get_source_segment_with_nonexistent_file():
    """
    Test get_source_segment with a file that doesn't exist.
    """
    # Arrange
    non_existent_file = "nonexistent.py"

    # Create a simple AST node
    node = ast.parse("x = 10").body[0]

    # Act
    result = get_source_segment(non_existent_file, node)

    # Assert
    assert result == ""
