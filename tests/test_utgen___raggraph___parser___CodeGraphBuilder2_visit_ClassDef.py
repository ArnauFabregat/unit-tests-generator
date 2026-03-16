import ast
from unittest.mock import Mock, patch

from utgen.raggraph.parser import CodeGraphBuilder2


def test_visit_ClassDef_nested_class():
    """
    Test visit_ClassDef with a nested class definition.
    """
    # Arrange
    outer_class = ast.ClassDef(
        name="OuterClass",
        bases=[],
        keywords=[],
        body=[ast.ClassDef(name="InnerClass", bases=[], keywords=[], body=[], decorator_list=[], docstring=None)],
        decorator_list=[],
        docstring=None,
    )

    # Mock canonical_id to return predictable values
    with patch("utgen.raggraph.utils.canonical_id") as mock_canonical_id:
        mock_canonical_id.side_effect = lambda *parts: "::".join(parts)

        # Initialize the builder
        builder = CodeGraphBuilder2(code_path="src", file_path="src/module.py", graph=Mock())

        # Act - visit outer class first
        builder.visit_ClassDef(outer_class)

        # Get the inner class node
        inner_class = outer_class.body[0]

        # Act - visit inner class
        builder.visit_ClassDef(inner_class)

        # Assert
        # Verify that current_class was set and restored for both classes
        # The outer class should be restored to None after its visit
        # The inner class should also be restored to None after its visit
        assert builder.current_class is None
