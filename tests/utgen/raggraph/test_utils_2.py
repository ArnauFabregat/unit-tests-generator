import ast

from utgen.raggraph.utils import get_source_segment


def test_get_source_segment_with_invalid_file_path():
    """
    Test get_source_segment with an invalid file path.
    """
    # Arrange
    # Create a dummy AST node
    node = ast.FunctionDef(
        name="test_function",
        args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
        body=[],
        decorator_list=[],
        returns=None,
        type_comment=None,
    )

    # Act
    result = get_source_segment("nonexistent_file.py", node)

    # Assert
    assert result == ""
    # Verify that the function handles OSError gracefully
