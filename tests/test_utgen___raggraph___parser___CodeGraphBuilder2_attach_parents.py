import ast

from utgen.raggraph.parser import CodeGraphBuilder2


def test_attach_parents_with_simple_ast():
    """
    Test attach_parents with a simple AST containing a FunctionDef.
    """
    # Arrange
    fn_node = ast.FunctionDef(
        name="my_function",
        args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
        body=[],
        decorator_list=[],
        returns=None,
        type_comment=None,
    )

    # Act
    CodeGraphBuilder2.attach_parents(fn_node)

    # Assert
    # Verify that the FunctionDef node has no parent (it's the root)
    assert not hasattr(fn_node, "parent")

    # Verify that child nodes have the parent attribute set
    # In this case, FunctionDef has no child nodes, so nothing to check
    assert True


def test_attach_parents_with_nested_ast():
    """
    Test attach_parents with a nested AST structure.
    """
    # Arrange
    fn_node = ast.FunctionDef(
        name="outer",
        args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
        body=[
            ast.FunctionDef(
                name="inner",
                args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
                body=[],
                decorator_list=[],
                returns=None,
                type_comment=None,
            )
        ],
        decorator_list=[],
        returns=None,
        type_comment=None,
    )

    # Act
    CodeGraphBuilder2.attach_parents(fn_node)

    # Assert
    # Verify that the outer FunctionDef has no parent (it's the root)
    assert not hasattr(fn_node, "parent")

    # Verify that the inner FunctionDef has the outer FunctionDef as parent
    inner_node = fn_node.body[0]
    assert hasattr(inner_node, "parent")
    assert inner_node.parent is fn_node

    # Verify that child nodes of inner FunctionDef have the inner FunctionDef as parent
    # In this case, inner FunctionDef has no child nodes, so nothing to check
    assert True


def test_attach_parents_with_complex_ast():
    """
    Test attach_parents with a complex AST structure containing multiple node types.
    """
    # Arrange
    fn_node = ast.FunctionDef(
        name="complex",
        args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
        body=[
            ast.Assign(targets=[ast.Name(id="x", ctx=ast.Store())], value=ast.Constant(value=42)),
            ast.If(
                test=ast.Compare(
                    left=ast.Name(id="x", ctx=ast.Load()), ops=[ast.Gt()], comparators=[ast.Constant(value=10)]
                ),
                body=[
                    ast.Expr(
                        value=ast.Call(
                            func=ast.Name(id="print", ctx=ast.Load()),
                            args=[ast.Constant(value="Greater than 10")],
                            keywords=[],
                        )
                    )
                ],
                orelse=[],
            ),
        ],
        decorator_list=[],
        returns=None,
        type_comment=None,
    )

    # Act
    CodeGraphBuilder2.attach_parents(fn_node)

    # Assert
    # Verify that the complex FunctionDef has no parent (it's the root)
    assert not hasattr(fn_node, "parent")

    # Verify that child nodes have the correct parent
    assign_node = fn_node.body[0]
    assert hasattr(assign_node, "parent")
    assert assign_node.parent is fn_node

    if_node = fn_node.body[1]
    assert hasattr(if_node, "parent")
    assert if_node.parent is fn_node

    # Verify that nested child nodes have the correct parent
    compare_node = if_node.test
    assert hasattr(compare_node, "parent")
    assert compare_node.parent is if_node

    name_x_node = compare_node.left
    assert hasattr(name_x_node, "parent")
    assert name_x_node.parent is compare_node

    constant_10_node = compare_node.comparators[0]
    assert hasattr(constant_10_node, "parent")
    assert constant_10_node.parent is compare_node

    expr_node = if_node.body[0]
    assert hasattr(expr_node, "parent")
    assert expr_node.parent is if_node

    call_node = expr_node.value
    assert hasattr(call_node, "parent")
    assert call_node.parent is expr_node

    name_print_node = call_node.func
    assert hasattr(name_print_node, "parent")
    assert name_print_node.parent is call_node

    constant_str_node = call_node.args[0]
    assert hasattr(constant_str_node, "parent")
    assert constant_str_node.parent is call_node
