import ast

from utgen.raggraph.parser import CodeGraphBuilder2


def test_attach_parents_with_no_children():
    # Create a leaf node
    leaf = ast.Constant(value=None)

    # Attach parents (should handle gracefully)
    CodeGraphBuilder2.attach_parents(leaf)

    # Verify no parent was set (leaf has no children)
    assert not hasattr(leaf, "parent")
